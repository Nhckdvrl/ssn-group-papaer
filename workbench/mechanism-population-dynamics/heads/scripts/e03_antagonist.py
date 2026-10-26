"""E03: causal test of antagonist-mediated late copy regression. Protocol: experiments/E03-*.md.

Usage: e03_antagonist.py --seed pythia-70m-seed2 --step 64000   -> results/e03/<seed>__step<N>.json
"""
import argparse
import json
import random
import time

import torch

import mp_common as mc
import e01_induction as e
import e02_population as p2

OUT = mc.RESULTS / "e03"
N_RAND = 10


def antagonists(seed, step):
    r = json.loads((mc.RESULTS / "e02" / f"{seed}__step{step}.json").read_text())
    a = sorted(h for h in {k.split("|")[0] for k in r["single"]} if r["single"][f"{h}|mean"]["dCL"] < -0.5)
    return a, r["roles"]


def second_half_tokens(model, toks, hooks=(), bs=250):
    """Per-token second-half losses [n, 49] and targets."""
    pos = torch.tensor(e.R3_POS[49:])
    lv = e.loss_at(model, toks, pos.tolist(), hooks, bs=bs)
    return lv, toks[:, pos + 1]


def freq_bins(model, toks, hooks, counts, edges):
    lv, tgt = second_half_tokens(model, toks, hooks)
    c = counts[tgt]
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (c >= lo) & (c < hi)
        out.append(float(lv[m].median()))
    return out


def resample_hooks(model, toks, heads, seed=1):
    """Replace each head's z by its z on a different sequence of the same kind (batch permutation), same positions."""
    g = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(toks), generator=g)
    by_layer = {}
    for l, h in heads:
        by_layer.setdefault(l, []).append(h)
    _, cache = model.run_with_cache(toks[perm].to(model.cfg.device),
                                    names_filter=lambda n: n.endswith("hook_z"))
    return [(f"blocks.{l}.attn.hook_z", (lambda z, hook, hs=hs, src=cache[f"blocks.{l}.attn.hook_z"]: hook_fn(z, hs, src)))
            for l, hs in by_layer.items()]


def hook_fn(z, hs, src):
    z[:, :, hs, :] = src[: z.shape[0]][:, :, hs, :]
    return z


def prev_attention(model, toks, heads, hooks=()):
    store = {}
    names = {f"blocks.{l}.attn.hook_pattern" for l, _ in heads}

    def grab(x, hook):
        store[hook.name] = x
        return x

    model.run_with_hooks(toks[:100].to(model.cfg.device), return_type=None,
                         fwd_hooks=list(hooks) + [(n, grab) for n in names])
    return {f"{l}.{h}": float(store[f"blocks.{l}.attn.hook_pattern"][:, h].diagonal(offset=-1, dim1=-2, dim2=-1).mean())
            for l, h in heads}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    repo = f"EleutherAI/{args.seed}"
    model = mc.load_tl_model(repo, args.step)
    pile, _ = e.pile_eval_set(model)
    bos = model.tokenizer.bos_token_id
    held = p2.repeated(p2.token_pool(), bos, seed=777)
    nat = torch.cat([torch.full((1000, 1), bos), pile[:1000, 1:51], pile[:1000, 1:51]], dim=1)
    mz = e.mean_z(model, pile)
    A, roles = antagonists(args.seed, args.step)
    circuit = set(roles["prev"]) | set(roles["induction"])
    res = {"seed": args.seed, "step": args.step, "A": A, "roles": roles,
           "protocol": "experiments/E03-antagonist-mediated-regression.md"}

    def cond(hs, m):
        return e.z_hooks(p2.parse(hs), m, mz) if hs else []

    clean = p2.behaviour(model, held)
    res["held_clean"] = {k: v for k, v in clean.items() if not k.startswith("_")}
    natc = p2.behaviour(model, nat)
    res["nat_clean"] = {k: v for k, v in natc.items() if not k.startswith("_")}
    ptoks = pile[1000:1500, :505]
    pl_pos = list(range(1, 504))
    res["pile_loss_clean"] = float(e.loss_at(model, ptoks, pl_pos, bs=20).mean())
    res["R2_clean"] = float(e.r2_from_loss(e.loss_at(model, pile[:1000, :505], e.R2_POS)).mean())
    counts = torch.load(p2.COUNTS)
    edges = [50, 200, 1000, 10 ** 9]
    res["freq_edges"] = edges
    res["freq_clean"] = freq_bins(model, held, [], counts, edges)
    ph = p2.parse(roles["prev"])
    ih = p2.parse(roles["induction"])
    if ph:
        res["prev_attn_clean"] = prev_attention(model, held, ph)
    if ih:
        res["ind_attn_clean"] = p2.induction_attention(model, held, ih)

    if A:
        layers = sorted({h.split(".")[0] for h in A})
        pool = [f"{l}.{h}" for l in layers for h in range(model.cfg.n_heads) if f"{l}.{h}" not in A and f"{l}.{h}" not in circuit]
        if len(pool) < 2 * len(A):  # DEVIATION (2026-10-02): same-layer pool too small -> layers 0-1, non-A, non-circuit
            pool = [f"{l}.{h}" for l in range(2) for h in range(model.cfg.n_heads) if f"{l}.{h}" not in A and f"{l}.{h}" not in circuit]
            res["random_pool_note"] = "layers 0-1 (same-layer pool < 2|A|)"
        rng = random.Random(0)
        res["A_ablated"] = {}
        for m in ("mean", "zero"):
            b = p2.behaviour(model, held, cond(A, m))
            nb = p2.behaviour(model, nat, cond(A, m))
            res["A_ablated"][m] = {"held": {k: v for k, v in b.items() if not k.startswith("_")},
                                   "nat": {k: v for k, v in nb.items() if not k.startswith("_")}}
        rs_held = resample_hooks(model, held, p2.parse(A))
        rs_nat = resample_hooks(model, nat, p2.parse(A))
        bh = p2.behaviour(model, held, rs_held, bs=len(held))
        bn = p2.behaviour(model, nat, rs_nat, bs=len(nat))
        res["A_ablated"]["resample"] = {"held": {k: v for k, v in bh.items() if not k.startswith("_")},
                                        "nat": {k: v for k, v in bn.items() if not k.startswith("_")}}
        if ih:
            res["A_ablated"]["resample"]["ind_attn"] = p2.induction_attention(model, held[:100], ih, resample_hooks(model, held[:100], p2.parse(A)))
        hA = cond(A, "mean")
        res["A_ablated"]["mean"]["pile_loss"] = float(e.loss_at(model, ptoks, pl_pos, hA, bs=20).mean())
        res["A_ablated"]["mean"]["R2"] = float(e.r2_from_loss(e.loss_at(model, pile[:1000, :505], e.R2_POS, hA)).mean())
        res["A_ablated"]["mean"]["freq"] = freq_bins(model, held, hA, counts, edges)
        if ph:
            res["A_ablated"]["mean"]["prev_attn"] = prev_attention(model, held, ph, hA)
        if ih:
            res["A_ablated"]["mean"]["ind_attn"] = p2.induction_attention(model, held, ih, hA)
        rnd = []
        for j in range(N_RAND):
            if len(pool) < len(A):
                break
            rs = rng.sample(pool, len(A))
            row = {"heads": rs, "held_CL": p2.behaviour(model, held, cond(rs, "mean"))["CL"]}
            if j < 3:
                row["pile_loss"] = float(e.loss_at(model, ptoks, pl_pos, cond(rs, "mean"), bs=20).mean())
            rnd.append(row)
        res["random_layer_matched"] = rnd
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / f"{args.seed}__step{args.step}.json").write_text(json.dumps(res, indent=1))
    msg = f"{args.seed}@{args.step}: A={A} heldCL={clean['CL']:.2f}"
    if A:
        msg += (f" ->A_mean {res['A_ablated']['mean']['held']['CL']:.2f} A_zero {res['A_ablated']['zero']['held']['CL']:.2f}"
                f" resample {res['A_ablated']['resample']['held']['CL']:.2f} rand {[round(r['held_CL'], 2) for r in rnd]} pile {res['pile_loss_clean']:.4f}->{res['A_ablated']['mean']['pile_loss']:.4f}"
                f" nat {natc['CL']:.2f}->{res['A_ablated']['mean']['nat']['CL']:.2f}")
    print(msg, f"({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
