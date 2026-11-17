#!/usr/bin/env python3
"""E192 (card: division/experiments/E192-frozen-router-intervention.md): continued pre-training of FLAME-MoE-290M from a
public Megatron checkpoint with the router free / frozen / reset / alone, one arm per GPU.

Model = FLAME-MoE-290M re-implemented in plain PyTorch with parameter names IDENTICAL to the Megatron-core fqn, so that the
official checkpoint (fp32 master params + Adam moments from the distributed optimizer) maps 1:1:
  9 layers, d 1024, 16 heads MHA (fused qkv, per-head [q;k;v] interleaved), RoPE base 1e4 non-interleaved, RMSNorm eps 1e-6
  (computed in fp32), SwiGLU, layer 0 dense (5472), layers 1..8 MoE: 64 experts (704) top-6 + shared expert (1408, no gate,
  added), router fp32 logits -> softmax over 64 -> top-6, probabilities NOT renormalised, dropless; untied output layer.
  Losses: LM cross entropy (fp32 logits), per MoE layer Switch aux loss (Megatron switch_load_balancing_loss_func on the
  full softmax scores, computed per Megatron micro-batch of --mbs-official sequences) x 0.01 and z-loss
  mean(logsumexp(logits)^2) x 0.001, summed over layers and added to the LM loss (MoEAuxLossAutoScaler semantics).
Precision: fp32 master params, bf16 autocast forward, fp32 grads (accumulated over micro-batches), AdamW (fused torch),
global-norm clip.  Hyper-parameters are read from the checkpoint's common.pt args (see --show-args).
Arms: --router free | frozen (router.weight requires_grad False, not in optimizer) | reset (router.weight re-drawn
N(0, init_method_std), fresh Adam state, per-param step 0) | only (only router.weight trains); --aux off zeroes aux + z.
Data: pools from e192_data.py; continuation iteration i (0-based) uses pool P{1 + i // 540}, window order = permutation of
the pool's 552,960 windows drawn with default_rng(1000 + data_seed); every arm with the same data seed sees identical
sequences in identical order.
Every --save-every iters: held-out NLL (DCLM eval stream + wikitext-103 test, per token fp16), router weights + norm gains,
router-input dump on the E191 token set (E186/E191 store format).  Every --ckpt-every iters: resume state (atomic).
Every --full-every iters: bf16 full weights.  Per-iter log: train loss, aux, z, grad norm, router hash, load stats.
usage: e192_train.py --arm A1 --start-ckpt DIR --router free --seed 1 --n-iter 540 --out /tmp/xiang_e192/arms/A1"""
import argparse, glob, hashlib, json, math, os, sys, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e191_fetch import patch_pickle, PM  # noqa: E402

BF = torch.bfloat16
SEQ, GB, NIT_POOL = 2048, 1024, 540


class Box(nn.Module):
    def __init__(self, **shapes):
        super().__init__()
        for k, s in shapes.items():
            self.register_parameter(k, nn.Parameter(torch.empty(*s)))


def _rmsnorm(x, w, eps):
    xf = x.float()
    return (xf * torch.rsqrt(xf.pow(2).mean(-1, keepdim=True) + eps) * w.float()).to(BF)


def _rope(t, cos, sin):
    hd = t.shape[-1]; tf = t.float(); t1, t2 = tf[..., :hd // 2], tf[..., hd // 2:]
    return (tf * cos + torch.cat([-t2, t1], -1) * sin).to(BF)


def _swiglu(gu):
    g, u = gu.chunk(2, -1)
    return F.silu(g) * u


# elementwise kernels fused by torch.compile (same math; E192_COMPILE=0 disables)
_C = (lambda f: torch.compile(f, dynamic=True)) if os.environ.get("E192_COMPILE", "1") == "1" else (lambda f: f)
rmsnorm, rope_apply, swiglu = _C(_rmsnorm), _C(_rope), _C(_swiglu)


class Layer(nn.Module):
    def __init__(self, c, dense):
        super().__init__()
        d = c["d"]; self.dense = dense; self.c = c
        self.self_attention = nn.Module()
        self.self_attention.linear_qkv = Box(weight=(3 * d, d), layer_norm_weight=(d,))
        self.self_attention.linear_proj = Box(weight=(d, d))
        self.mlp = nn.Module()
        if dense:
            self.mlp.linear_fc1 = Box(weight=(2 * c["ffn"], d), layer_norm_weight=(d,))
            self.mlp.linear_fc2 = Box(weight=(d, c["ffn"]))
        else:
            self.pre_mlp_layernorm = Box(weight=(d,))
            self.mlp.router = Box(weight=(c["E"], d))
            self.mlp.experts = nn.Module(); self.mlp.experts.experts = nn.Module()
            self.mlp.experts.experts.linear_fc1 = Box(weight=(c["E"], 2 * c["fe"], d))
            self.mlp.experts.experts.linear_fc2 = Box(weight=(c["E"], d, c["fe"]))
            self.mlp.shared_experts = nn.Module()
            self.mlp.shared_experts.linear_fc1 = Box(weight=(2 * c["fs"], d))
            self.mlp.shared_experts.linear_fc2 = Box(weight=(d, c["fs"]))

    def ln2_weight(self):
        return self.mlp.linear_fc1.layer_norm_weight if self.dense else self.pre_mlp_layernorm.weight

    def forward(self, x, cos, sin, st):
        c = self.c; B, T, d = x.shape; nh = c["nh"]; hd = d // nh
        h = rmsnorm(x, self.self_attention.linear_qkv.layer_norm_weight, c["eps"])
        qkv = F.linear(h, self.self_attention.linear_qkv.weight.to(BF)).view(B, T, nh, 3, hd)
        q, k, v = qkv.unbind(3)

        q, k = rope_apply(q, cos, sin), rope_apply(k, cos, sin)
        o = F.scaled_dot_product_attention(q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2), is_causal=True)
        x = x + F.linear(o.transpose(1, 2).reshape(B, T, d), self.self_attention.linear_proj.weight.to(BF))
        h = rmsnorm(x, self.ln2_weight(), c["eps"])
        if self.dense:
            return x + F.linear(swiglu(F.linear(h, self.mlp.linear_fc1.weight.to(BF))), self.mlp.linear_fc2.weight.to(BF))
        return x + self.moe(h.reshape(B * T, d), st, B).view(B, T, d)

    def moe(self, h, st, B):
        c = self.c; E, K, fe = c["E"], c["K"], c["fe"]; N, d = h.shape
        if st.get("dump") is not None:
            st["dump"].append(h)
        logits = F.linear(h.float(), self.mlp.router.weight.float())          # fp32 router
        scores = torch.softmax(logits, -1)
        topv, topi = scores.topk(K, -1)
        if st.get("aux_on", True) and self.training:
            G = max(1, B // st["mbs_official"]); n = N // G
            sg = scores.view(G, n, E).sum(1)                                   # [G, E]
            tpe = torch.zeros(G * n, E, device=h.device).scatter_(1, topi, 1.0).view(G, n, E).sum(1)
            aux = (sg * tpe).sum(1) * (E * st["aux_coeff"] / (n * n * K))
            z = torch.logsumexp(logits, -1).pow(2).mean() * st["z_coeff"]
            st["aux"].append(aux.mean()); st["z"].append(z)
        if st.get("stats") is not None:
            st["stats"].append((topv.sum(-1).mean().detach(), torch.bincount(topi.reshape(-1), minlength=E).detach()))
        flat = topi.reshape(-1); order = flat.argsort(stable=True); tok = order // K
        counts = torch.bincount(flat, minlength=E).tolist()
        xs = h[tok]; ws = topv.reshape(-1)[order]
        # one bf16 cast per weight and unbind (its backward stacks once) instead of W[e] indexing, whose backward
        # materialises a full-size zero gradient per expert
        W1 = self.mlp.experts.experts.linear_fc1.weight.to(BF).unbind(0)
        W2 = self.mlp.experts.experts.linear_fc2.weight.to(BF).unbind(0)
        outs, s0 = [], 0
        for xe, n_e, e in zip(xs.split(counts, 0), counts, range(E)):
            if n_e == 0:
                continue
            outs.append(F.linear(swiglu(F.linear(xe, W1[e])), W2[e])); s0 += n_e
        ys = torch.cat(outs, 0).float() * ws[:, None]
        out = torch.zeros(N, d, device=h.device, dtype=torch.float32).index_add_(0, tok, ys).to(BF)
        return out + F.linear(swiglu(F.linear(h, self.mlp.shared_experts.linear_fc1.weight.to(BF))),
                              self.mlp.shared_experts.linear_fc2.weight.to(BF))


class Flame(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.c = c
        self.embedding = nn.Module(); self.embedding.word_embeddings = Box(weight=(c["V"], c["d"]))
        self.decoder = nn.Module()
        self.decoder.layers = nn.ModuleList([Layer(c, l in c["dense_layers"]) for l in range(c["L"])])
        self.decoder.final_layernorm = Box(weight=(c["d"],))
        self.output_layer = Box(weight=(c["V"], c["d"]))
        self._rope = {}

    def rope(self, T, dev):
        if T not in self._rope:
            hd = self.c["d"] // self.c["nh"]
            inv = 1.0 / (self.c["theta"] ** (torch.arange(0, hd, 2, device=dev, dtype=torch.float32) / hd))
            f = torch.outer(torch.arange(T, device=dev, dtype=torch.float32), inv); emb = torch.cat([f, f], -1)
            self._rope[T] = (emb.cos()[None, :, None, :], emb.sin()[None, :, None, :])
        return self._rope[T]

    def moe_layers(self):
        return [l for l in range(self.c["L"]) if l not in self.c["dense_layers"]]

    def forward(self, ids, st):
        B, T = ids.shape
        x = F.embedding(ids, self.embedding.word_embeddings.weight).to(BF)
        cos, sin = self.rope(T, ids.device)
        for layer in self.decoder.layers:
            x = layer(x, cos, sin, st)
        x = rmsnorm(x, self.decoder.final_layernorm.weight, self.c["eps"])
        return x

    def logits(self, x):
        return F.linear(x, self.output_layer.weight.to(BF))

    def lm_loss(self, x, y, chunk=8192):
        """Mean token cross entropy (fp32 logits) computed in chunks with recomputation, so the [N, V] logits are never
        held for backward (same math as F.cross_entropy on the full logits)."""
        import torch.utils.checkpoint as ckp
        W = self.output_layer.weight.to(BF); xf = x.reshape(-1, x.shape[-1]); yf = y.reshape(-1); tot = 0.0

        def f(xc, yc, W):
            return F.cross_entropy(F.linear(xc, W).float(), yc, reduction="sum")
        for i in range(0, len(yf), chunk):
            tot = tot + ckp.checkpoint(f, xf[i:i + chunk], yf[i:i + chunk], W, use_reentrant=False)
        return tot / len(yf)


def cfg_from_args(a):
    freq = a["moe_layer_freq"]
    return {"V": a["padded_vocab_size"], "d": a["hidden_size"], "L": a["num_layers"], "nh": a["num_attention_heads"],
            "ffn": a["ffn_hidden_size"], "E": a["num_experts"], "K": a["moe_router_topk"], "fe": a["moe_ffn_hidden_size"],
            "fs": a["moe_shared_expert_intermediate_size"], "eps": a["norm_epsilon"], "theta": float(a["rotary_base"]),
            "dense_layers": [i for i, f in enumerate(freq) if f == 0]}


# ---------------------------------------------------------------- checkpoint I/O (Megatron torch_dist)
def read_args(d):
    patch_pickle()
    return vars(torch.load(os.path.join(d, "common.pt"), map_location="cpu", weights_only=False, pickle_module=PM)["args"])


def read_dcp(d, prefixes):
    """Load all tensors whose key starts with one of `prefixes` (fqn -> CPU tensor)."""
    patch_pickle()
    import torch.distributed.checkpoint as dcp
    from torch.distributed.checkpoint import FileSystemReader
    from torch.distributed.checkpoint.metadata import TensorStorageMetadata
    r = FileSystemReader(d); md = r.read_metadata()
    sd = {k: torch.empty(m.size, dtype=m.properties.dtype) for k, m in md.state_dict_metadata.items()
          if isinstance(m, TensorStorageMetadata) and k.startswith(tuple(prefixes))}
    dcp.load(sd, storage_reader=r, no_dist=True)
    return sd


def load_official(model, d, master=True):
    """Model params from the fp32 master copy if present (master=True and fetched with --full), else the bf16 model
    tensors.  Megatron's distributed optimizer stores per-parameter flat buffers: chained_0 = non-expert params
    (shape (1, 1, numel) or (1, d)), chained_1 = expert params ((64, 2, 1, f*d) for fc1 = [gate; up] halves,
    (64, 1, 1, d*f) for fc2); a row-major view to the model shape is checked by requiring fp32_param.to(bf16) to equal
    the bf16 model tensor bit-for-bit.  Returns (source, adam dict fqn -> (exp_avg, exp_avg_sq), check dict)."""
    names = [n for n, _ in model.named_parameters()]
    sd = read_dcp(d, names)
    with torch.no_grad():
        for n, p in model.named_parameters():
            p.copy_(sd[n].view(p.shape).float())
    if not (master and os.path.exists(os.path.join(d, "_fetched_full.json"))):
        return "bf16", {}, {}
    pre = ("chained_0.optimizer.state.", "chained_1.optimizer.state.")
    od = read_dcp(d, pre)
    get = {}
    for k, v in od.items():
        for pf in pre:
            if k.startswith(pf):
                kind, fqn = k[len(pf):].split(".", 1); get[(kind, fqn)] = v
    adam, chk = {}, {"max_abs_bf16_mismatch": 0.0, "n_exact": 0, "n": 0}
    with torch.no_grad():
        for n, p in model.named_parameters():
            fp = get[("fp32_param", n)].reshape(p.shape)
            bfm = sd[n].view(p.shape)
            exact = torch.equal(fp.to(torch.bfloat16), bfm)
            chk["n"] += 1; chk["n_exact"] += int(exact)
            chk["max_abs_bf16_mismatch"] = max(chk["max_abs_bf16_mismatch"], float((fp.to(torch.bfloat16).float() - bfm.float()).abs().max()))
            p.copy_(fp)
            adam[n] = (get[("exp_avg", n)].reshape(p.shape).float(), get[("exp_avg_sq", n)].reshape(p.shape).float())
    assert chk["n_exact"] == chk["n"], f"fp32 master does not round to the bf16 model tensors: {chk}"
    return "fp32_master", adam, chk


# ---------------------------------------------------------------- data
class Pools:
    def __init__(self, root, seed):
        self.root, self.seed, self.mm, self.perm = root, seed, {}, {}

    def batch(self, it):
        """Continuation iteration `it` -> uint16 array [GB, SEQ + 1]."""
        p = 1 + it // NIT_POOL
        if p not in self.mm:
            self.mm[p] = np.memmap(f"{self.root}/dclm/pool_P{p}.u16", np.uint16, "r")
            self.perm[p] = np.random.default_rng(1000 + self.seed).permutation(NIT_POOL * GB)
        w = np.sort(self.perm[p][(it % NIT_POOL) * GB:(it % NIT_POOL + 1) * GB])
        mm = self.mm[p]
        return np.stack([mm[j * SEQ:j * SEQ + SEQ + 1] for j in w])


# ---------------------------------------------------------------- eval + dump
def eval_streams(root):
    out = {}
    for k in ("dclm", "wikitext"):
        x = np.fromfile(f"{root}/dclm/eval_{k}.u16", np.uint16)
        n = (len(x) - 1) // SEQ
        out[k] = np.stack([x[j * SEQ:j * SEQ + SEQ + 1] for j in range(n)])
    return out


@torch.no_grad()
def eval_nll(model, streams, bs=16):
    model.eval(); res = {}
    for k, W in streams.items():
        nll = np.zeros((len(W), SEQ), np.float16)
        for b0 in range(0, len(W), bs):
            ids = torch.from_numpy(W[b0:b0 + bs].astype(np.int64)).cuda()
            with torch.autocast("cuda", BF):
                x = model(ids[:, :-1], {"aux_on": False})
                lg = model.logits(x).float()
            nll[b0:b0 + bs] = F.cross_entropy(lg.view(-1, lg.shape[-1]), ids[:, 1:].reshape(-1), reduction="none").view(len(ids), SEQ).cpu().numpy()
        res[k] = nll
    model.train()
    return res


class DumpSet:
    """E191 token set (21,500 positions) + English LM loss text; built once per process."""

    def __init__(self, root):
        from transformers import AutoTokenizer
        from e191_hidden import build_sequences, sample_rows, LANGS
        tok = AutoTokenizer.from_pretrained(f"{root}/tok/pythia12b")
        self.SEQS, self.SRC, self.SID = build_sequences(tok, f"{root}/data")
        self.rows = sample_rows(self.SEQS, self.SRC); self.LANGS = LANGS
        self.need = {}
        for r, (si, p) in enumerate(self.rows):
            self.need.setdefault(si, []).append((p, r))
        eng = [i for i in range(len(self.SEQS)) if self.SRC[i] in (0, len(LANGS))]
        self.todo = sorted(set(self.need) | set(eng), key=lambda i: len(self.SEQS[i]))

    @torch.no_grad()
    def dump(self, model, out, extra):
        os.makedirs(out, exist_ok=True)
        model.eval(); moe = model.moe_layers(); L, N, d = len(moe), len(self.rows), model.c["d"]; K = model.c["K"]
        OUT = np.zeros((L, N, d), np.float16); TK = np.zeros((L, N, K), np.int8)
        nll = {"flores_eng": [0.0, 0], "ud": [0.0, 0], "other": [0.0, 0]}
        src_ud = len(self.LANGS); B = 64
        for b0 in range(0, len(self.todo), B):
            b = self.todo[b0:b0 + B]; T = max(len(self.SEQS[i]) for i in b)
            ids = torch.zeros((len(b), T), dtype=torch.long)
            flat, rr = [], []
            for q, i in enumerate(b):
                ids[q, :len(self.SEQS[i])] = torch.tensor(self.SEQS[i])
                for p, r in self.need.get(i, []):
                    flat.append(q * T + p); rr.append(r)
            st = {"aux_on": False, "dump": []}
            ids = ids.cuda()
            with torch.autocast("cuda", BF):
                x = model(ids, st); lg = model.logits(x).float()
            lp = F.cross_entropy(lg[:, :-1].reshape(-1, lg.shape[-1]), ids[:, 1:].reshape(-1), reduction="none").view(len(b), T - 1)
            if flat:
                fl = torch.tensor(flat, device="cuda"); rr = np.array(rr)
                for j, hh in enumerate(st["dump"]):
                    hs = hh[fl]
                    OUT[j, rr] = hs.float().cpu().numpy().astype(np.float16)
                    W = model.decoder.layers[moe[j]].mlp.router.weight.float()
                    TK[j, rr] = (hs.float() @ W.T).topk(K, -1).indices.cpu().numpy().astype(np.int8)
            for q, i in enumerate(b):
                n = len(self.SEQS[i]) - 1
                kname = "flores_eng" if self.SRC[i] == 0 else "ud" if self.SRC[i] == src_ud else "other"
                nll[kname][0] += float(lp[q, :n].sum()); nll[kname][1] += n
        np.save(f"{out}/toksub.npy", OUT); np.save(f"{out}/topk_fp32.npy", TK)
        np.savez(f"{out}/toksub_meta.npz", src=np.array([self.SRC[s] for s, _ in self.rows], np.int8),
                 sid=np.array([self.SID[s] for s, _ in self.rows], np.int32), pos=np.array([p for _, p in self.rows], np.int32),
                 inp=np.array([self.SEQS[s][p] for s, p in self.rows], np.int64))
        lay = model.decoder.layers
        np.savez(f"{out}/router.npz", gate=np.stack([lay[l].mlp.router.weight.detach().float().cpu().numpy() for l in moe]),
                 post_attention_layernorm=np.stack([lay[l].pre_mlp_layernorm.weight.detach().float().cpu().numpy() for l in moe]),
                 input_layernorm=np.stack([lay[l].self_attention.linear_qkv.layer_norm_weight.detach().float().cpu().numpy() for l in moe]))
        meta = {"N": N, "L": L, "d": d, "K": K, "E": model.c["E"], "moe_layer_ids": moe, "langs": self.LANGS, "src_ud": src_ud,
                "seed_flores": 179, "seed_ud": 1179, "definition": "input of the router (pre_mlp_layernorm output), bf16 forward",
                "lm_loss": {k: (v[0] / v[1] if v[1] else None, v[1]) for k, v in nll.items()}, "tokenizer": "EleutherAI/pythia-12b",
                "host": os.uname().nodename}
        meta.update(extra)
        json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
        model.train()
        return meta["lm_loss"]


def router_hash(model):
    h = hashlib.sha1()
    for l in model.moe_layers():
        h.update(model.decoder.layers[l].mlp.router.weight.detach().cpu().numpy().tobytes())
    return h.hexdigest()[:16]


def save_routers(model, path):
    lay = model.decoder.layers; moe = model.moe_layers()
    np.savez(path, gate=np.stack([lay[l].mlp.router.weight.detach().float().cpu().numpy() for l in moe]),
             gain=np.stack([lay[l].pre_mlp_layernorm.weight.detach().float().cpu().numpy() for l in moe]))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True); ap.add_argument("--start-ckpt", required=True)
    ap.add_argument("--router", choices=["free", "frozen", "reset", "only"], default="free")
    ap.add_argument("--aux", choices=["on", "off"], default="on")
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--init-seed", type=int, default=None)
    ap.add_argument("--n-iter", type=int, default=540); ap.add_argument("--out", required=True)
    ap.add_argument("--root", default="/tmp/xiang_e192"); ap.add_argument("--mbs", type=int, default=16)
    ap.add_argument("--save-every", type=int, default=54); ap.add_argument("--ckpt-every", type=int, default=27)
    ap.add_argument("--full-every", type=int, default=270); ap.add_argument("--no-master", action="store_true")
    ap.add_argument("--smoke", type=int, default=0, help="run only this many iters, no saves except a timing json")
    ap.add_argument("--fresh-adam-warmup", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True
    margs = read_args(a.start_ckpt); c = cfg_from_args(margs)
    start_iter = int(os.path.basename(a.start_ckpt.rstrip("/")).split("_")[-1])
    hp = {"lr": margs["lr"], "min_lr": margs.get("min_lr"), "wd": margs["weight_decay"], "b1": margs["adam_beta1"],
          "b2": margs["adam_beta2"], "eps": margs["adam_eps"], "clip": margs["clip_grad"], "aux": margs["moe_aux_loss_coeff"],
          "z": margs["moe_z_loss_coeff"], "init_std": margs["init_method_std"], "mbs_official": margs["micro_batch_size"],
          "gbs": margs["global_batch_size"], "seq": margs["seq_length"], "hidden_dropout": margs.get("hidden_dropout"),
          "attention_dropout": margs.get("attention_dropout"), "train_iters": margs.get("train_iters"),
          "lr_decay_style": margs.get("lr_decay_style"), "lr_warmup_iters": margs.get("lr_warmup_iters"),
          "lr_wsd_decay_iters": margs.get("lr_wsd_decay_iters"), "lr_wsd_decay_style": margs.get("lr_wsd_decay_style")}
    assert hp["gbs"] == GB and hp["seq"] == SEQ, hp
    assert not hp["hidden_dropout"] and not hp["attention_dropout"], "dropout > 0 not implemented"
    LOG = open(f"{a.out}/train_log.jsonl", "a")
    torch.manual_seed(0)
    model = Flame(c).cuda()
    resume = f"{a.out}/resume.pt"
    it0 = 0
    if os.path.exists(resume):
        R = torch.load(resume, map_location="cuda", weights_only=False)
        model.load_state_dict(R["model"]); it0 = R["it"]; src = R["src"]; adam = None; chk = R.get("chk")
        print(f"resumed {a.arm} at continuation iter {it0}", flush=True)
    else:
        src, adam, chk = load_official(model, a.start_ckpt, master=not a.no_master)
        print("loaded", src, chk, flush=True)
        R = None
    routers = [model.decoder.layers[l].mlp.router.weight for l in model.moe_layers()]
    if R is None and a.router == "reset":
        g = torch.Generator(device="cuda").manual_seed(a.init_seed if a.init_seed is not None else 100 + a.seed)
        with torch.no_grad():
            for w in routers:
                w.copy_(torch.randn(w.shape, generator=g, device="cuda") * hp["init_std"])
    for n, p in model.named_parameters():
        is_r = n.endswith("mlp.router.weight")
        p.requires_grad_(not is_r if a.router == "frozen" else (is_r if a.router == "only" else True))
    named = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    decay = [p for n, p in named if p.ndim > 1]; nodecay = [p for n, p in named if p.ndim <= 1]
    opt = torch.optim.AdamW([{"params": decay, "weight_decay": hp["wd"]}, {"params": nodecay, "weight_decay": 0.0}],
                            lr=hp["lr"], betas=(hp["b1"], hp["b2"]), eps=hp["eps"], fused=True)
    step0 = float(start_iter)
    if R is not None:
        opt.load_state_dict(R["opt"])
    else:
        n_loaded = 0
        for n, p in named:
            if adam and n in adam and not (a.router == "reset" and n.endswith("mlp.router.weight")):
                opt.state[p] = {"step": torch.tensor(step0, dtype=torch.float32, device="cuda"), "exp_avg": adam[n][0].cuda(), "exp_avg_sq": adam[n][1].cuda()}
                n_loaded += 1
            else:
                opt.state[p] = {"step": torch.tensor(0.0, dtype=torch.float32, device="cuda"), "exp_avg": torch.zeros_like(p), "exp_avg_sq": torch.zeros_like(p)}
        print(f"param source {src}; Adam state loaded for {n_loaded}/{len(named)} trainable tensors (step {step0:.0f})", flush=True)
    del adam
    st_base = {"aux_on": a.aux == "on", "aux_coeff": hp["aux"], "z_coeff": hp["z"], "mbs_official": hp["mbs_official"]}
    data = Pools(a.root, a.seed)
    streams = eval_streams(a.root) if not a.smoke else None
    dumpset = DumpSet(a.root) if not a.smoke else None
    n_micro = GB // a.mbs
    info = {"arm": a.arm, "start_ckpt": a.start_ckpt, "start_iter": start_iter, "router": a.router, "aux": a.aux, "seed": a.seed,
            "init_seed": (a.init_seed if a.init_seed is not None else 100 + a.seed) if a.router == "reset" else None,
            "param_source": src, "load_check": chk, "hp": hp, "mbs": a.mbs, "n_micro": n_micro, "cfg": c, "host": os.uname().nodename,
            "gpu": os.environ.get("CUDA_VISIBLE_DEVICES"), "torch": torch.__version__}
    json.dump(info, open(f"{a.out}/run_info.json", "w"), indent=1)

    def lr_at(it):          # WSD: constant phase for the iterations used here (asserted)
        return hp["lr"]
    assert hp["lr_wsd_decay_iters"] is None or start_iter + a.n_iter <= hp["train_iters"] - hp["lr_wsd_decay_iters"], hp
    assert hp["lr_warmup_iters"] is None or start_iter >= hp["lr_warmup_iters"], hp

    def checkpoint_point(it):
        tag = f"c{it:04d}"
        save_routers(model, f"{a.out}/routers_{tag}.npz")
        ev = eval_nll(model, streams)
        np.savez_compressed(f"{a.out}/nll_{tag}.npz", **ev)
        lm = dumpset.dump(model, f"{a.out}/dump_{tag}", {"arm": a.arm, "cont_iter": it, "official_iter": start_iter + it,
                                                         "tokens": (start_iter + it) * GB * SEQ})
        rec = {"eval": True, "it": it, "official_iter": start_iter + it, "nll_dclm": float(ev["dclm"].astype(np.float64).mean()),
               "nll_wikitext": float(ev["wikitext"].astype(np.float64).mean()), "lm_eng": lm, "router_hash": router_hash(model),
               "time": time.time()}
        LOG.write(json.dumps(rec) + "\n"); LOG.flush(); print(rec, flush=True)

    if not a.smoke and it0 == 0 and not os.path.exists(f"{a.out}/nll_c0000.npz"):
        checkpoint_point(0)
    h0 = router_hash(model)
    t_start = time.time(); n_iter = a.smoke or a.n_iter
    for it in range(it0, n_iter):
        t0 = time.time()
        Bx = torch.from_numpy(data.batch(it).astype(np.int64))
        tot = {"lm": 0.0, "aux": 0.0, "z": 0.0}; psum = torch.zeros((), device="cuda"); load = None
        for m in range(n_micro):
            ids = Bx[m * a.mbs:(m + 1) * a.mbs].cuda(non_blocking=True)
            st = dict(st_base, aux=[], z=[], stats=[] if m == 0 else None)
            with torch.autocast("cuda", BF):
                x = model(ids[:, :-1], st)
                lm = model.lm_loss(x, ids[:, 1:])
            auxl = torch.stack(st["aux"]).sum() if st["aux"] else torch.zeros((), device="cuda")
            zl = torch.stack(st["z"]).sum() if st["z"] else torch.zeros((), device="cuda")
            ((lm + auxl + zl) / n_micro).backward()
            tot["lm"] += lm.item() / n_micro; tot["aux"] += auxl.item() / n_micro; tot["z"] += zl.item() / n_micro
            if m == 0:
                load = [(float(ps), (cnt.float() / cnt.sum()).max().item() * c["E"]) for ps, cnt in st["stats"]]
            del x
        params = [p for _, p in named]
        gn = torch.nn.utils.clip_grad_norm_(params, hp["clip"]).item()
        for gr in opt.param_groups:
            gr["lr"] = lr_at(it)
        opt.step(); opt.zero_grad(set_to_none=True)
        torch.cuda.synchronize(); dt = time.time() - t0
        rh = router_hash(model)
        rec = {"it": it + 1, "official_iter": start_iter + it + 1, "lm": tot["lm"], "aux": tot["aux"], "z": tot["z"], "gn": gn,
               "lr": lr_at(it), "dt": dt, "tok_s": GB * SEQ / dt, "router_hash": rh,
               "router_unchanged": rh == h0, "top6_psum_l": [round(x[0], 4) for x in load],
               "maxload_l": [round(x[1], 3) for x in load], "mem_gb": torch.cuda.max_memory_allocated() / 1e9}
        LOG.write(json.dumps(rec) + "\n"); LOG.flush()
        print(f"[{a.arm}] it {it + 1} lm {tot['lm']:.4f} aux {tot['aux']:.4f} z {tot['z']:.4f} gn {gn:.3f} {dt:.1f}s "
              f"{GB * SEQ / dt / 1e3:.1f}k tok/s mem {rec['mem_gb']:.1f}G router_unchanged {rh == h0}", flush=True)
        if a.smoke:
            continue
        done = it + 1
        if done % a.save_every == 0:
            checkpoint_point(done)
        if done % a.full_every == 0:
            torch.save({n: p.detach().to(BF).cpu() for n, p in model.state_dict().items()}, f"{a.out}/full_c{done:04d}.pt")
        if done % a.ckpt_every == 0 or done == n_iter:
            torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "it": done, "src": src, "chk": chk}, resume + ".tmp")
            os.replace(resume + ".tmp", resume)
    if a.smoke:
        json.dump({"smoke_iters": a.smoke, "wall_s": time.time() - t_start}, open(f"{a.out}/smoke.json", "w"))
    else:
        open(f"{a.out}/DONE_{n_iter:04d}", "w").write(time.ctime())


if __name__ == "__main__":
    main()
