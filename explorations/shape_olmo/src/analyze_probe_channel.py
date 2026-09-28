"""Readout for probe_channel: full vs recurrent-only readout, per task and n (pooled over gaps).
Also checks that 'full' reproduces probe_order for the same tag.
usage: analyze_probe_channel.py TAG [TAG ...]
"""
import json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(lp):
    lp = np.array(lp); p = np.exp(lp - lp.max()); return p / p.sum()


for tag in sys.argv[1:]:
    f = f"{ROOT}/results/probe_channel/{tag}.jsonl"
    if not os.path.exists(f):
        continue
    rows = [json.loads(l) for l in open(f)]
    ref = {}
    g = f"{ROOT}/results/probe_order/{tag}.jsonl"
    if os.path.exists(g):
        for l in open(g):
            r = json.loads(l); ref[(r["task"], r["n"], r["gap"], r["k"])] = np.array(r["lp_cands"])
    diffs = [np.abs(np.array(r["lp_full"]) - ref[(r["task"], r["n"], r["gap"], r["k"])]).max()
             for r in rows if (r["task"], r["n"], r["gap"], r["k"]) in ref]
    print(f"== {tag}  (n items {len(rows)}; full vs probe_order max|Δlp| median {np.median(diffs) if diffs else float('nan'):.3f})")
    print(f"{'task':9s} {'n':>2s}  {'full P(correct)':>16s} {'reconly P(correct)':>19s}   full P(first)  reconly P(first)")
    for task in ("reassign", "keyed"):
        for n in (1, 2, 4, 8):
            sel = [r for r in rows if r["task"] == task and r["n"] == n]
            pf = np.array([norm(r["lp_full"]) for r in sel]); pr = np.array([norm(r["lp_reconly"]) for r in sel])
            c = np.array([r["correct"] for r in sel])
            fc, rc = pf[np.arange(len(c)), c].mean(), pr[np.arange(len(c)), c].mean()
            print(f"{task:9s} {n:>2d}  {fc:16.2f} {rc:19.2f}   {pf[:, 0].mean():12.2f}  {pr[:, 0].mean():15.2f}")
