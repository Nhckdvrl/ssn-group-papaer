"""CT03 E01 -- exact-vs-proxy counterfactual routing credit on a pretrained MoE.

Frozen design: docs/E01_DESIGN.md. Nothing here trains anything.

For sampled (token, layer) pairs we form equal-compute expert replacements
i -> j (i selected, j unexecuted), then measure

  exact  : the true change in scored CE, by replaying layers l+1..L-1
  proxy  : g^T dh, for g from a per-token backward and from ONE shared backward

and write one record per candidate to results/e01_records.jsonl.
"""

import argparse, json, math, os, random, time
import torch
import torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "allenai/OLMoE-1B-7B-0924-Instruct"


# ---------------------------------------------------------------- capture

class Capture:
    """Grabs, for each target layer: the MoE block's input, its output (with
    grad retained) and the decoder layer's output; plus the shared attention
    kwargs needed to replay the upper stack."""

    def __init__(self, model, layers):
        self.model = model
        self.layers = layers
        self.mlp_in, self.mlp_out, self.layer_out = {}, {}, {}
        self.attn_kwargs = None
        self.handles = []

    def __enter__(self):
        mm = self.model.model

        def pre0(mod, args, kwargs):
            self.attn_kwargs = {
                "attention_mask": kwargs.get("attention_mask"),
                "position_ids": kwargs.get("position_ids"),
                "position_embeddings": kwargs.get("position_embeddings"),
                "cache_position": kwargs.get("cache_position"),
            }

        self.handles.append(mm.layers[0].register_forward_pre_hook(pre0, with_kwargs=True))

        for l in self.layers:
            def mlp_hook(mod, inp, out, l=l):
                self.mlp_in[l] = inp[0]
                h = out[0]
                if h.requires_grad:
                    h.retain_grad()
                self.mlp_out[l] = h

            def layer_hook(mod, inp, out, l=l):
                self.layer_out[l] = out[0]

            self.handles.append(mm.layers[l].mlp.register_forward_hook(mlp_hook))
            self.handles.append(mm.layers[l].register_forward_hook(layer_hook))
        return self

    def __exit__(self, *a):
        for h in self.handles:
            h.remove()


# ---------------------------------------------------------------- replay

@torch.no_grad()
def replay_ce(model, l, H, start, targets, attn_kwargs, chunk=64):
    """Run layers l+1.. on hidden states H (batch, T, D) and return per-position
    CE for positions >= start. `targets` is the (T,) next-token target row."""
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
        H = layer(H, use_cache=False, past_key_values=None, **kw)[0]
    H = mm.norm(H[:, start:-1])
    tgt = targets[start:]
    out = torch.zeros(B, H.shape[1], device=H.device, dtype=torch.float32)
    for a in range(0, H.shape[1], chunk):
        logits = model.lm_head(H[:, a:a + chunk]).float()
        out[:, a:a + chunk] = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]),
            tgt[a:a + chunk].repeat(B),
            reduction="none",
        ).view(B, -1)
    return out


# ---------------------------------------------------------------- main

def run(args):
    torch.manual_seed(args.seed); random.seed(args.seed)
    dev = "cuda"
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.float32, attn_implementation="sdpa"
    ).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)

    cfg = model.config
    K, E = cfg.num_experts_per_tok, cfg.num_experts
    assert not cfg.norm_topk_prob, "design assumes un-renormalised top-k weights"
    layers = [int(x) for x in args.layers.split(",")]

    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    idxs = list(range(len(ds)))
    random.Random(args.seed).shuffle(idxs)

    fout = open(args.out, "w")
    meta = dict(model=MODEL, dtype="float32", K=K, E=E, layers=layers,
                m_boundary=args.m, m_random=args.m, seed=args.seed,
                n_problems=args.n_problems, tokens_per_stratum=args.tok_per_stratum)
    print("META", json.dumps(meta), flush=True)

    done = 0
    for qi in idxs:
        if done >= args.n_problems:
            break
        ex = ds[qi]
        msgs = [{"role": "user", "content": ex["problem"]}]
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        if len(ids) > args.max_len or len(s_ids) < args.min_sol:
            continue
        done += 1
        input_ids = torch.tensor([ids], device=dev)
        T = input_ids.shape[1]
        targets = input_ids[0, 1:]                      # next-token targets, len T-1
        first = len(p_ids) - 1                          # first position predicting a solution token

        # ---- clean forward with graph ------------------------------------
        with Capture(model, layers) as cap:
            with torch.enable_grad():
                # every parameter is frozen, so the graph only exists if the
                # activations themselves require grad
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                logits = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(logits[0, :-1].float(), targets, reduction="none")
                L_seq = ce[first:].sum()
                L_seq.backward(retain_graph=True)
        ce_d = ce.detach()
        g_shared = {l: cap.mlp_out[l].grad[0].detach().clone() for l in layers}
        base_ce = ce_d.clone()

        # ---- pick tokens: hard = Q4 of scored CE, easy = Q1 ---------------
        scored = ce_d[first:]
        order = torch.argsort(scored)
        n = len(order)
        q = max(1, n // 4)
        rng = random.Random(args.seed * 7919 + qi)
        easy_pool = [first + int(i) for i in order[:q].tolist()]
        hard_pool = [first + int(i) for i in order[-q:].tolist()]
        picks = ([(t, "easy") for t in rng.sample(easy_pool, min(args.tok_per_stratum, len(easy_pool)))]
                 + [(t, "hard") for t in rng.sample(hard_pool, min(args.tok_per_stratum, len(hard_pool)))])

        # ---- per-token gradients (one backward per picked token) ----------
        g_tok = {}
        for t, _ in picks:
            grads = torch.autograd.grad(ce[t], [cap.mlp_out[l] for l in layers],
                                        retain_graph=True, allow_unused=False)
            g_tok[t] = {l: g[0, t].detach().clone() for l, g in zip(layers, grads)}

        mlp_in = {l: cap.mlp_in[l].detach() for l in layers}
        layer_out = {l: cap.layer_out[l].detach() for l in layers}
        attn_kwargs = cap.attn_kwargs
        del logits, ce, L_seq, emb, cap
        torch.cuda.empty_cache()

        # ---- candidates + exact/proxy ------------------------------------
        for l in layers:
            moe = model.model.layers[l].mlp
            for t, stratum in picks:
                x = mlp_in[l][0, t]
                rl = moe.gate(x).float()
                w = F.softmax(rl, dim=-1)
                rank = torch.argsort(w, descending=True)
                sel = rank[:K].tolist()
                i_rep = sel[-1]                                   # weakest selected expert
                boundary = rank[K:K + args.m].tolist()
                far = rank[K + args.m:].tolist()
                random.Random(args.seed * 104729 + qi * 97 + t * 13 + l).shuffle(far)
                rand_pool = far[:args.m]
                cands = [(j, "boundary") for j in boundary] + [(j, "random") for j in rand_pool]

                with torch.no_grad():
                    e_i = moe.experts[i_rep](x) * w[i_rep]
                    dhs = torch.stack([moe.experts[j](x) * w[j] - e_i for j, _ in cands])

                gs, gt = g_shared[l][t], g_tok[t][l]
                px_shared = (dhs.float() @ gs.float()).tolist()
                px_tok = (dhs.float() @ gt.float()).tolist()

                # Row 0 is a ZERO patch. The baseline must come through the
                # identical replay path as the patched rows, otherwise the
                # fp32 gap between the full forward and the replay (~3e-5,
                # measured in e01_validity) contaminates dL -- which matters,
                # because at deep layers dL itself is order 1e-4.
                B = dhs.shape[0]
                H = layer_out[l].expand(B + 1, -1, -1).clone()
                H[1:, t] += dhs
                t0 = time.perf_counter()
                all_ce = replay_ce(model, l, H, t, targets, attn_kwargs)
                torch.cuda.synchronize()
                exact_s = time.perf_counter() - t0

                b_row, new_ce = all_ce[0], all_ce[1:]
                dL_seq = (new_ce - b_row).sum(dim=1).tolist()
                dL_tok = (new_ce[:, 0] - b_row[0]).tolist()
                replay_base_drift = float((b_row - base_ce[t:]).abs().max())

                for ci, (j, pool) in enumerate(cands):
                    fout.write(json.dumps(dict(
                        q=qi, layer=l, pos=t, stratum=stratum, pool=pool,
                        i=i_rep, j=j, w_i=float(w[i_rep]), w_j=float(w[j]),
                        rank_j=int((rank == j).nonzero()[0]),
                        base_ce=float(base_ce[t]), seq_len=T, first=first,
                        dh_norm=float(dhs[ci].norm()),
                        dL_seq=dL_seq[ci], dL_tok=dL_tok[ci],
                        px_shared=px_shared[ci], px_tok=px_tok[ci],
                        exact_batch_s=exact_s, n_cand=B, replay_base_drift=replay_base_drift,
                    )) + "\n")
                fout.flush()
        print(f"[{done}/{args.n_problems}] q={qi} T={T} sol={len(s_ids)}", flush=True)
        del g_shared, g_tok, mlp_in, layer_out
        torch.cuda.empty_cache()
    fout.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/e01_records.jsonl")
    ap.add_argument("--layers", default="1,4,7,10,13,15")
    ap.add_argument("--m", type=int, default=8)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=32)
    ap.add_argument("--tok-per-stratum", dest="tok_per_stratum", type=int, default=4)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--min-sol", dest="min_sol", type=int, default=64)
    ap.add_argument("--seed", type=int, default=0)
    run(ap.parse_args())
