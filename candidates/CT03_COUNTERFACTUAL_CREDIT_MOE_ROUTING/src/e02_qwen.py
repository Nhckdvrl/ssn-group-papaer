"""CT03 Stage B (E02) -- cross-family exact-vs-proxy calibration on Qwen3-30B-A3B.

Frozen design: docs/E02_STAGEB_DESIGN.md. Nothing here trains anything.

The new object relative to E01 is the RENORMALISED swap. With norm_topk_prob=true,
replacing expert i by j rescales the seven surviving experts as well:

    Z  = sum_{e in S} p_e              (raw softmax mass on the routed set)
    Z' = Z - p_i + p_j
    dh = (Z/Z' - 1) * h  +  (p_j E_j(x) - p_i E_i(x)) / Z'

which is exact and still needs only two local expert forwards.
"""

import argparse, json, random, time
import torch
import torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3-30B-A3B"
ALPHAS = [0.125, 1.0]


def unwrap(out):
    return out[0] if isinstance(out, tuple) else out


class Capture:
    """Qwen3Moe decoder layers return a bare tensor; the MoE block returns
    (hidden, router_logits). Handles both."""

    def __init__(self, model, layers):
        self.model, self.layers = model, layers
        self.mlp_in, self.mlp_out, self.layer_out = {}, {}, {}
        self.attn_kwargs = None
        self.handles = []

    def __enter__(self):
        mm = self.model.model

        def pre0(mod, args, kwargs):
            pe = kwargs.get("position_embeddings")
            if pe is None and len(args) > 1:
                pe = args[1]
            self.attn_kwargs = {
                "position_embeddings": pe,
                "attention_mask": kwargs.get("attention_mask"),
                "position_ids": kwargs.get("position_ids"),
                "cache_position": kwargs.get("cache_position"),
            }

        self.handles.append(mm.layers[0].register_forward_pre_hook(pre0, with_kwargs=True))
        for l in self.layers:
            def mlp_hook(mod, inp, out, l=l):
                self.mlp_in[l] = inp[0]
                h = unwrap(out)
                if h.requires_grad:
                    h.retain_grad()
                self.mlp_out[l] = h

            def layer_hook(mod, inp, out, l=l):
                self.layer_out[l] = unwrap(out)

            self.handles.append(mm.layers[l].mlp.register_forward_hook(mlp_hook))
            self.handles.append(mm.layers[l].register_forward_hook(layer_hook))
        return self

    def __exit__(self, *a):
        for h in self.handles:
            h.remove()


def route_of(moe, x, K):
    """Raw softmax probs, the routed set, its mass, and the block's own weights."""
    p = F.softmax(moe.gate(x).float(), dim=-1)
    rank = torch.argsort(p, descending=True)
    sel = rank[:K].tolist()
    Z = float(p[sel].sum())
    return p, rank, sel, Z


def swap_dh(moe, x, h, p, i, j, Z):
    """Exact local dh for the renormalised replacement i -> j (see module docstring)."""
    Zp = Z - float(p[i]) + float(p[j])
    ei = moe.experts[i](x) * float(p[i])
    ej = moe.experts[j](x) * float(p[j])
    return (Z / Zp - 1.0) * h + (ej - ei) / Zp, Zp


@torch.no_grad()
def replay_ce(model, l, H, start, targets, chunk=32, **attn_kwargs):
    mm = model.model
    B, T, _ = H.shape
    kw = dict(attn_kwargs)
    pe = kw.get("position_embeddings")
    if pe is not None and pe[0].shape[0] != B:
        kw["position_embeddings"] = (pe[0].expand(B, -1, -1), pe[1].expand(B, -1, -1))
    am = kw.get("attention_mask")
    if am is not None and am.shape[0] != B:
        kw["attention_mask"] = am.expand(B, *am.shape[1:])
    pid = kw.get("position_ids")
    if pid is not None and pid.shape[0] != B:
        kw["position_ids"] = pid.expand(B, -1)

    for layer in mm.layers[l + 1:]:
        H = unwrap(layer(H, use_cache=False, past_key_values=None, **kw))
    Hn = mm.norm(H[:, start:-1])
    tgt = targets[start:].to(Hn.device)
    out = torch.zeros(B, Hn.shape[1], device=Hn.device, dtype=torch.float32)
    for a in range(0, Hn.shape[1], chunk):
        lg = model.lm_head(Hn[:, a:a + chunk]).float()
        out[:, a:a + chunk] = F.cross_entropy(
            lg.reshape(-1, lg.shape[-1]), tgt[a:a + chunk].repeat(B),
            reduction="none").view(B, -1)
    return out


def load(args):
    tok = AutoTokenizer.from_pretrained(MODEL)
    mm = {i: f"{args.mem_per_gpu}GiB" for i in range(args.n_gpu)}
    # fp32 by default: every measurement so far is a small CE difference. bf16
    # is opt-in and only for sampling throughput, where both arms take it.
    dt = dict(fp32=torch.float32, bf16=torch.bfloat16)[getattr(args, "dtype", "fp32")]
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=dt, attn_implementation="sdpa",
        device_map="auto", max_memory=mm).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return tok, model


# --------------------------------------------------------------- validity

def validate(args):
    tok, model = load(args)
    K = model.config.num_experts_per_tok
    assert model.config.norm_topk_prob, "E02 exists to exercise renormalised routing"
    LY = [4, 20, 47]
    ex = load_dataset("HuggingFaceH4/MATH-500", split="test")[3]
    prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                     tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    p_ids = tok(prompt, add_special_tokens=False).input_ids
    s_ids = tok(ex["solution"], add_special_tokens=False).input_ids[:160]
    ids = p_ids + s_ids
    dev0 = next(model.parameters()).device
    input_ids = torch.tensor([ids], device=dev0)
    targets = input_ids[0, 1:]
    first, t = len(p_ids) - 1, len(p_ids) - 1 + len(s_ids) // 2

    with Capture(model, LY) as cap:
        with torch.no_grad():
            logits = model(input_ids).logits
            base_ce = F.cross_entropy(logits[0, :-1].float(), targets.to(logits.device),
                                      reduction="none")
        mlp_in = {l: cap.mlp_in[l].detach() for l in LY}
        mlp_out = {l: cap.mlp_out[l].detach() for l in LY}
        layer_out = {l: cap.layer_out[l].detach() for l in LY}
        akw = cap.attn_kwargs

    rep, ok = {}, True
    for l in LY:
        r = replay_ce(model, l, layer_out[l].clone(), t, targets, **akw)[0]
        d = (r - base_ce[t:].to(r.device)).abs().max().item()
        rep[f"replay_identity_L{l}"] = d; ok &= d < 1e-3

    for l in LY:
        moe = model.model.layers[l].mlp
        x = mlp_in[l][0, t]
        p, rank, sel, Z = route_of(moe, x, K)
        # h rebuilt from the router's OWN renormalised weights
        h_rb = sum(moe.experts[e](x) * (float(p[e]) / Z) for e in sel)
        d1 = (h_rb - mlp_out[l][0, t]).abs().max().item()
        i_rep, j = sel[-1], int(rank[K])
        dh, Zp = swap_dh(moe, x, mlp_out[l][0, t], p, i_rep, j, Z)
        # independent recomputation of the swapped route, including the rescaling
        # of the surviving experts
        sel2 = sel[:-1] + [j]
        h_sw = sum(moe.experts[e](x) * (float(p[e]) / Zp) for e in sel2)
        d2 = (h_sw - (mlp_out[l][0, t] + dh)).abs().max().item()
        scale = float(mlp_out[l][0, t].abs().max())
        rep[f"renorm_L{l}_rebuild_err"] = d1
        rep[f"renorm_L{l}_swap_err"] = d2
        rep[f"renorm_L{l}_Z"] = Z; rep[f"renorm_L{l}_Zp"] = Zp
        rep[f"renorm_L{l}_h_scale"] = scale
        ok &= d1 < 1e-3 * max(scale, 1.0) and d2 < 1e-3 * max(scale, 1.0)

        # exact replay dL vs a genuine full forward with a routing-override hook
        H = layer_out[l].clone(); H[:, t] += dh
        t0 = time.perf_counter()
        rr = replay_ce(model, l, H, t, targets, **akw)[0]
        torch.cuda.synchronize()
        rep[f"exact_L{l}_replay_seconds"] = time.perf_counter() - t0
        dL_replay = float((rr - base_ce[t:].to(rr.device)).sum())
        hd = model.model.layers[l].mlp.register_forward_hook(
            lambda m, i_, o, dh=dh, t=t: (o[0].index_copy(
                1, torch.tensor([t], device=o[0].device),
                (o[0][:, t] + dh).unsqueeze(1)), o[1]))
        with torch.no_grad():
            lg2 = model(input_ids).logits
            ce2 = F.cross_entropy(lg2[0, :-1].float(),
                                  targets.to(lg2.device), reduction="none")
        hd.remove()
        dL_full = float(ce2[first:].sum() - base_ce[first:].sum())
        rep[f"exact_L{l}_dL_replay"] = dL_replay
        rep[f"exact_L{l}_dL_full"] = dL_full
        ok &= abs(dL_replay - dL_full) < max(1e-3, 0.02 * abs(dL_full))

    # throughput probe at the real batch width, so the main run can be sized
    l = 20
    H = layer_out[l].expand(22, -1, -1).clone()
    t0 = time.perf_counter()
    replay_ce(model, l, H, t, targets, **akw)
    torch.cuda.synchronize()
    rep["probe_L20_batch22_seconds"] = time.perf_counter() - t0
    rep["probe_seq_len"] = int(input_ids.shape[1])
    rep["probe_tail_positions"] = int(input_ids.shape[1] - t)

    rep["ALL_PASS"] = bool(ok)
    print(json.dumps(rep, indent=1))
    return 0 if ok else 1


# --------------------------------------------------------------- main run

def run(args):
    torch.manual_seed(args.seed); random.seed(args.seed)
    tok, model = load(args)
    K = model.config.num_experts_per_tok
    assert model.config.norm_topk_prob
    layers = [int(x) for x in args.layers.split(",")]
    nL = model.config.num_hidden_layers
    dev0 = next(model.parameters()).device

    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    idxs = list(range(len(ds))); random.Random(args.seed).shuffle(idxs)
    fout = open(args.out, "w")
    print("META", json.dumps(dict(model=MODEL, n_layers=nL, layers=layers,
                                 alphas=ALPHAS, K=K, E=model.config.num_experts,
                                 m_boundary=args.m, m_random=args.m_rand)), flush=True)

    done = 0
    for qi in idxs:
        if done >= args.n_problems:
            break
        ex = ds[qi]
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        if len(ids) > args.max_len or len(s_ids) < args.min_sol:
            continue
        done += 1
        input_ids = torch.tensor([ids], device=dev0)
        T = input_ids.shape[1]
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1

        with Capture(model, layers) as cap:
            with torch.enable_grad():
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                logits = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(logits[0, :-1].float(),
                                     targets.to(logits.device), reduction="none")
                ce[first:].sum().backward()
        base_ce = ce.detach().clone()
        g_shared = {l: cap.mlp_out[l].grad[0].detach().clone() for l in layers}
        mlp_in = {l: cap.mlp_in[l].detach() for l in layers}
        mlp_out = {l: cap.mlp_out[l].detach() for l in layers}
        layer_out = {l: cap.layer_out[l].detach() for l in layers}
        akw = cap.attn_kwargs
        del logits, ce, emb, cap
        torch.cuda.empty_cache()

        scored = base_ce[first:]
        order = torch.argsort(scored)
        q = max(1, len(order) // 4)
        rng = random.Random(args.seed * 7919 + qi)
        picks = ([(first + int(i), "easy") for i in
                  rng.sample(order[:q].tolist(), min(args.n_easy, q))]
                 + [(first + int(i), "hard") for i in
                    rng.sample(order[-q:].tolist(), min(args.n_hard, q))])

        for l in layers:
            moe = model.model.layers[l].mlp
            for t, stratum in picks:
                x = mlp_in[l][0, t]
                h = mlp_out[l][0, t]
                p, rank, sel, Z = route_of(moe, x, K)
                i_rep = sel[-1]
                boundary = rank[K:K + args.m].tolist()
                far = rank[K + args.m:].tolist()
                random.Random(args.seed * 104729 + qi * 97 + t * 13 + l).shuffle(far)
                cands = ([(j, "boundary") for j in boundary]
                         + [(j, "random") for j in far[:args.m_rand]])

                with torch.no_grad():
                    dhs, zps = [], []
                    for j, _ in cands:
                        d, zp = swap_dh(moe, x, h, p, i_rep, j, Z)
                        dhs.append(d); zps.append(zp)
                    dhs = torch.stack(dhs)
                px_base = (dhs.float() @ g_shared[l][t].float()).tolist()

                nC, nA = len(cands), len(ALPHAS)
                patch = torch.zeros(2 + nC * nA, dhs.shape[1],
                                    device=dhs.device, dtype=dhs.dtype)
                for c in range(nC):
                    for ai, a in enumerate(ALPHAS):
                        patch[2 + c * nA + ai] = dhs[c] * a
                H = layer_out[l].expand(patch.shape[0], -1, -1).clone()
                H[:, t] += patch

                t0 = time.perf_counter()
                all_ce = replay_ce(model, l, H, t, targets, **akw)
                torch.cuda.synchronize()
                batch_s = time.perf_counter() - t0

                b_row = all_ce[0]
                dL_seq = (all_ce - b_row).sum(dim=1)
                dL_tok = all_ce[:, 0] - b_row[0]
                floor = float(dL_seq[1])

                for c, (j, pool) in enumerate(cands):
                    for ai, a in enumerate(ALPHAS):
                        r = 2 + c * nA + ai
                        px = px_base[c] * a
                        ds_ = float(dL_seq[r])
                        fout.write(json.dumps(dict(
                            q=qi, layer=l, rel_depth=round(l / nL, 4), pos=t,
                            stratum=stratum, pool=pool, alpha=a,
                            i=i_rep, j=j, p_i=float(p[i_rep]), p_j=float(p[j]),
                            Z=Z, Zp=zps[c], rank_j=int((rank == j).nonzero()[0]),
                            base_ce=float(base_ce[t]),
                            dh_norm=float(dhs[c].norm()) * a,
                            dL_seq=ds_, dL_tok=float(dL_tok[r]),
                            px_shared=px, px_base=px_base[c],
                            lin_ratio=(ds_ / px) if px != 0 else float("nan"),
                            floor_seq=floor, batch_s=batch_s,
                            n_rows=int(patch.shape[0]), seq_len=T,
                        )) + "\n")
                fout.flush()
        print(f"[{done}/{args.n_problems}] q={qi} T={T}", flush=True)
        del g_shared, mlp_in, mlp_out, layer_out
        torch.cuda.empty_cache()
    fout.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--out", default="results/e02_records.jsonl")
    ap.add_argument("--layers", default="4,12,20,28,36,44,47")
    ap.add_argument("--m", type=int, default=6)
    ap.add_argument("--m-rand", dest="m_rand", type=int, default=4)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=24)
    ap.add_argument("--n-hard", dest="n_hard", type=int, default=4)
    ap.add_argument("--n-easy", dest="n_easy", type=int, default=2)
    ap.add_argument("--max-len", dest="max_len", type=int, default=512)
    ap.add_argument("--min-sol", dest="min_sol", type=int, default=64)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    raise SystemExit(validate(a) if a.validate else run(a))
