"""E04-A2: where is the post-trained model sharper or flatter than its parent on the same context?

For each sampled position (same context sources and position sampling as e04_fit.py) compute
  H0, H1          : next-token entropy of parent / child
  tau_t           : per-position KL-optimal temperature, argmin_τ KL(p1 ‖ softmax(τ z0)) (1-D Newton, τ∈[0.05, 20])
  kl_t, kl_tau_t  : KL(p1‖p0) and KL(p1‖softmax(τ_t z0)) — how much of each position's change a local temperature explains
  same_top1       : argmax p1 == argmax p0
Bucket by mean entropy (H0+H1)/2 (bucketing by H0 alone creates regression-to-the-mean) and report: share of positions with τ_t>1 (child sharper), median τ_t, share of the total KL,
local-temperature KL reduction, top-1 agreement. A global τ (E04-A) averages these; this shows whether post-training
is selective sharpening (e.g., only at high-entropy 'forking' positions).

Usage: python e04_local_tau.py <pair_key> [--sources gen_child,gen_parent,neutral] [--max_pos 30000]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

import models
from e04_fit import chunks, hidden, load_sources

ROOT = Path(__file__).resolve().parents[1]
BINS = [0, 0.1, 0.5, 1.0, 2.0, 4.0, 99]


@torch.no_grad()
def local_tau(z0, z1, iters=40):
    """KL(p1‖softmax(τ z0)) is convex in τ with derivative E_q[z0] − E_p1[z0], increasing in τ: bisect in log τ."""
    lp1 = torch.log_softmax(z1, -1); p1 = lp1.exp()
    Ep1z = (p1 * z0).sum(-1)
    lo = torch.full((z0.shape[0],), np.log(0.05), device=z0.device); hi = torch.full_like(lo, np.log(20.0))
    for _ in range(iters):
        mid = (lo + hi) / 2
        g = (torch.softmax(mid.exp()[:, None] * z0, -1) * z0).sum(-1) - Ep1z
        lo = torch.where(g < 0, mid, lo); hi = torch.where(g < 0, hi, mid)
    tau = ((lo + hi) / 2).exp()
    lq = torch.log_softmax(tau[:, None] * z0, -1)
    lp0 = torch.log_softmax(z0, -1)
    kl = (p1 * (lp1 - lp0)).sum(-1); kl_tau = (p1 * (lp1 - lq)).sum(-1)
    H0 = -(lp0.exp() * lp0).sum(-1); H1 = -(p1 * lp1).sum(-1)
    return tau, kl, kl_tau, H0, H1, (lp0.argmax(-1) == lp1.argmax(-1)).float()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--sources", default="gen_child,gen_parent,neutral")
    ap.add_argument("--max_pos", type=int, default=30000)
    args = ap.parse_args()
    dev = "cuda"; t0 = time.time()
    torch.backends.cuda.matmul.allow_tf32 = True
    p0, p1, stage = models.PAIRS[args.pair]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    srcs = load_sources(args.pair, args.sources.split(","), tok)
    rng = np.random.default_rng(1)
    sel = {}
    for s, seqs in srcs.items():
        npos = [len(ids) - first for _, ids, first in seqs]
        frac = min(1.0, args.max_pos / max(1, sum(npos)))
        sel[s] = [torch.tensor(np.sort(rng.choice(m, size=max(1, int(round(m * frac))), replace=False))) for m in npos]
    H0s, W0 = hidden(p0, srcs, dev, sel)
    H1s, W1 = hidden(p1, srcs, dev, sel)
    res = {"pair": args.pair, "stage": stage, "bins_H0": BINS, "sources": {}}
    for s in srcs:
        cols = {k: [] for k in ("tau", "kl", "kl_tau", "H0", "H1", "same")}
        for sl in chunks(H0s[s].shape[0], 2048):
            out = local_tau(H0s[s][sl].float() @ W0.T, H1s[s][sl].float() @ W1.T)
            for k, v in zip(cols, out):
                cols[k].append(v.cpu())
        c = {k: torch.cat(v).numpy() for k, v in cols.items()}
        tot_kl = c["kl"].sum()
        rows = []
        Hm = (c["H0"] + c["H1"]) / 2          # bucket by mean entropy: avoids regression-to-the-mean of H0 buckets
        for lo, hi in zip(BINS[:-1], BINS[1:]):
            m = (Hm >= lo) & (Hm < hi)
            if m.sum() == 0:
                continue
            rows.append({"Hmean": [lo, hi], "n": int(m.sum()), "share_pos": float(m.mean()), "share_kl": float(c["kl"][m].sum() / tot_kl),
                         "frac_child_sharper": float((c["tau"][m] > 1).mean()), "median_tau": float(np.median(c["tau"][m])),
                         "mean_H1_minus_H0": float((c["H1"][m] - c["H0"][m]).mean()),
                         "local_tau_kl_reduction": float(1 - c["kl_tau"][m].sum() / c["kl"][m].sum()),
                         "top1_same": float(c["same"][m].mean())})
        res["sources"][s] = {"n": int(len(c["kl"])), "mean_kl": float(c["kl"].mean()), "frac_child_sharper": float((c["tau"] > 1).mean()),
                             "median_tau": float(np.median(c["tau"])), "mean_H0": float(c["H0"].mean()), "mean_H1": float(c["H1"].mean()),
                             "local_tau_kl_reduction": float(1 - c["kl_tau"].sum() / tot_kl), "by_Hmean": rows,
                             "by_H0_mean_dH": [float((c["H1"] - c["H0"])[(c["H0"] >= lo) & (c["H0"] < hi)].mean()) if ((c["H0"] >= lo) & (c["H0"] < hi)).any() else None for lo, hi in zip(BINS[:-1], BINS[1:])],
                             "by_H1_mean_dH": [float((c["H1"] - c["H0"])[(c["H1"] >= lo) & (c["H1"] < hi)].mean()) if ((c["H1"] >= lo) & (c["H1"] < hi)).any() else None for lo, hi in zip(BINS[:-1], BINS[1:])]}
        print(s, {k: v for k, v in res["sources"][s].items() if k != "by_Hmean"}, flush=True)
        for r_ in rows:
            print("   ", r_, flush=True)
    res["seconds"] = time.time() - t0
    out = ROOT / "results" / "e04"; out.mkdir(parents=True, exist_ok=True)
    (out / f"localtau_{args.pair}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
