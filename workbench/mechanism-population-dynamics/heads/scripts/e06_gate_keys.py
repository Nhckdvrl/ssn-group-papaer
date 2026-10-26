"""E06: which context property keys the layer-0 copy gate. Protocol: experiments/E06-what-keys-the-gate.md.

Usage: e06_gate_keys.py --repo EleutherAI/pythia-70m-seed2 --step 64000 -> results/e06/<model>__step<N>.json
"""
import argparse
import json
import time

import numpy as np
import torch
from scipy.stats import spearmanr

import mp_common as mc
import e01_induction as e
import e02_population as p2
import e04_ctx_gating as p4

OUT = mc.RESULTS / "e06"
N = 500


def stimuli(pile, bos, counts):
    g = torch.Generator().manual_seed(4242)
    nat = pile[1000:1000 + N, 1:51]
    shuf = torch.stack([row[torch.randperm(50, generator=g)] for row in nat])
    p = counts.float().clone()
    p[0] = 0  # <|endoftext|> separators
    unig = torch.multinomial(p / p.sum(), N * 50, replacement=True, generator=g).view(N, 50)
    order = counts.argsort(descending=True)
    hi_pool = order[500:5000]
    lo_pool = torch.nonzero((counts >= 10) & (counts < 50)).flatten()
    mid_pool = p2.token_pool()

    def from_pool(pool):
        return pool[torch.randint(0, len(pool), (N, 50), generator=g)]

    xs = {"S1_nat": nat, "S2_shuf": shuf, "S3_unig": unig, "S4_hi": from_pool(hi_pool),
          "S5_mid": from_pool(mid_pool), "S6_lo": from_pool(lo_pool)}
    return {k: torch.cat([torch.full((N, 1), bos), x, x], dim=1) for k, x in xs.items()}


def per_seq(model, toks, hooks=(), bs=125):
    """first-half mean loss, second-half median loss, second-half acc, layer-0 resid projection on d (set later)."""
    lv = e.loss_at(model, toks, e.R3_POS, hooks, bs=bs)
    return lv[:, :49].mean(1), lv[:, 49:].median(1).values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    model = mc.load_tl_model(args.repo, args.step)
    pile, _ = e.pile_eval_set(model)
    bos = model.tokenizer.bos_token_id
    counts = torch.load(p2.COUNTS)
    est_r, est_n = p2.repeated(p2.token_pool(), bos, seed=12345), p4.nat_rep(pile, bos, 0, 500)
    mu_r, mu_n = p4.z_means(model, est_r, [0]), p4.z_means(model, est_n, [0])
    d = (p4.resid0_mean(model, est_r) - p4.resid0_mean(model, est_n)).mean(0)
    dhat = d / d.norm()
    fwd = p4.shift_hooks([0], mu_r, mu_n)
    res = {"repo": args.repo, "step": args.step, "protocol": "experiments/E06-what-keys-the-gate.md", "classes": {}}
    allF, allS, allP = [], [], []
    for name, toks in stimuli(pile, bos, counts).items():
        f, s = per_seq(model, toks)
        _, sf = per_seq(model, toks, fwd)
        _, cache = model.run_with_cache(toks.to(model.cfg.device), names_filter=lambda n: n == "blocks.0.hook_resid_post")
        proj = (cache["blocks.0.hook_resid_post"][:, 1:51] @ dhat).mean(1).cpu()
        b = p2.behaviour(model, toks)
        res["classes"][name] = {"CL": float(s.mean()), "FL": float(f.mean()), "ACC": b["ACC"],
                                "CL_fwd_shift": float(sf.mean()), "proj_d": float(proj.mean()),
                                "rho_FL_CL": float(spearmanr(f, s)[0]), "rho_proj_CL": float(spearmanr(proj, s)[0])}
        allF.append(f), allS.append(s), allP.append(proj)
    F, S, P = torch.cat(allF), torch.cat(allS), torch.cat(allP)
    res["pooled"] = {"rho_FL_CL": float(spearmanr(F, S)[0]), "rho_proj_CL": float(spearmanr(P, S)[0]),
                     "rho_FL_proj": float(spearmanr(F, P)[0])}
    res["seconds"] = round(time.time() - t0, 1)
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    print(tag, {k: (round(v["CL"], 2), round(v["CL_fwd_shift"], 2), round(v["proj_d"], 2)) for k, v in res["classes"].items()},
          {k: round(v, 2) for k, v in res["pooled"].items()}, f"({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
