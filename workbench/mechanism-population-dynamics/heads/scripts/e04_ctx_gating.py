"""E04: bidirectional distribution-mean shift of early-layer head outputs. Protocol: experiments/E04-*.md.

Usage: e04_ctx_gating.py --seed pythia-70m-seed2 --step 64000  -> results/e04/<seed>__step<N>.json
"""
import argparse
import json
import time

import torch

import mp_common as mc
import e01_induction as e
import e02_population as p2

OUT = mc.RESULTS / "e04"
SETS = {"L0": [0], "L01": [0, 1], "L1": [1], "L5": [5]}


def nat_rep(pile, bos, lo, hi):
    span = pile[lo:hi, 1:51]
    return torch.cat([torch.full((hi - lo, 1), bos), span, span], dim=1)


@torch.no_grad()
def z_means(model, toks, layers):
    _, cache = model.run_with_cache(toks.to(model.cfg.device), names_filter=lambda n: n.endswith("hook_z"))
    return {l: cache[f"blocks.{l}.attn.hook_z"].mean(0) for l in layers}  # [pos, head, d_head]


@torch.no_grad()
def resid0_mean(model, toks):
    _, cache = model.run_with_cache(toks.to(model.cfg.device), names_filter=lambda n: n == "blocks.0.hook_resid_post")
    return cache["blocks.0.hook_resid_post"].mean(0)  # [pos, d_model]


def shift_hooks(layers, frm, to):
    def mk(l):
        def hook(z, hook):
            return z - frm[l][None] + to[l][None]
        return hook
    return [(f"blocks.{l}.attn.hook_z", mk(l)) for l in layers]


def resid_hook(vec, sign):
    def hook(x, hook):
        return x + sign * vec[None, None]
    return [("blocks.0.hook_resid_post", hook)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    model = mc.load_tl_model(f"EleutherAI/{args.seed}", args.step)
    pile, _ = e.pile_eval_set(model)
    bos = model.tokenizer.bos_token_id
    pool = p2.token_pool()
    est_r, est_n = p2.repeated(pool, bos, seed=12345), nat_rep(pile, bos, 0, 1000)
    held_r, held_n = p2.repeated(pool, bos, seed=777), nat_rep(pile, bos, 1000, 2000)
    layers = sorted({l for v in SETS.values() for l in v})
    mu_r, mu_n = z_means(model, est_r, layers), z_means(model, est_n[:500], layers)
    roles = json.loads((mc.RESULTS / "e02" / f"{args.seed}__step{args.step}.json").read_text())["roles"]
    ih = p2.parse(roles["induction"])

    def beh(toks, hooks=()):
        b = p2.behaviour(model, toks, hooks)
        return {k: v for k, v in b.items() if not k.startswith("_")}

    res = {"seed": args.seed, "step": args.step, "protocol": "experiments/E04-context-naturalness-gating.md",
           "clean": {"rand": beh(held_r), "nat": beh(held_n)}, "shift": {}}
    if ih:
        res["clean"]["ind_attn_rand"] = p2.induction_attention(model, held_r, ih)
        res["clean"]["ind_attn_nat"] = p2.induction_attention(model, held_n, ih)
    for name, ls in SETS.items():
        fwd = shift_hooks(ls, mu_r, mu_n)  # random input, made to look natural
        rev = shift_hooks(ls, mu_n, mu_r)  # natural input, made to look random
        row = {"fwd_rand": beh(held_r, fwd), "rev_nat": beh(held_n, rev)}
        if ih and name == "L0":
            row["ind_attn_fwd_rand"] = p2.induction_attention(model, held_r, ih, fwd)
            row["ind_attn_rev_nat"] = p2.induction_attention(model, held_n, ih, rev)
        res["shift"][name] = row
    d = (resid0_mean(model, est_r) - resid0_mean(model, est_n[:500])).mean(0)
    res["resid_dir_norm"] = float(d.norm())
    res["resid"] = {"sub_on_rand": beh(held_r, resid_hook(d, -1.0)), "add_on_nat": beh(held_n, resid_hook(d, +1.0))}
    ptoks = pile[1000:1500, :505]
    pos = list(range(1, 504))
    res["pile_loss_clean"] = float(e.loss_at(model, ptoks, pos, bs=20).mean())
    res["pile_loss_add_d"] = float(e.loss_at(model, ptoks, pos, resid_hook(d, +1.0), bs=20).mean())
    res["pile_loss_sub_d"] = float(e.loss_at(model, ptoks, pos, resid_hook(d, -1.0), bs=20).mean())
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / f"{args.seed}__step{args.step}.json").write_text(json.dumps(res, indent=1))
    c, s = res["clean"], res["shift"]
    print(f"{args.seed}@{args.step}: rand CL {c['rand']['CL']:.2f} ->L0fwd {s['L0']['fwd_rand']['CL']:.2f} L5fwd {s['L5']['fwd_rand']['CL']:.2f}"
          f" | nat CL {c['nat']['CL']:.2f} ->L0rev {s['L0']['rev_nat']['CL']:.2f} L5rev {s['L5']['rev_nat']['CL']:.2f}"
          f" | resid: rand {res['resid']['sub_on_rand']['CL']:.2f} nat {res['resid']['add_on_nat']['CL']:.2f} ({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
