#!/usr/bin/env python3
"""E06 analysis: student trajectories on the frozen 7-condition grid (Beyond Owls eval_local outputs).

For every available epoch of each student run, relative to a reference (base model eval by default):
  binding   = [m(FEM) - m(MASC)]_student - [m(FEM) - m(MASC)]_ref           (margin gap, nats)
  name      = [m(MASC) - m(REF)]_student - [...]_ref                         (coarse "name present" shift)
  uncond    = m(REF)_student - m(REF)_ref                                    (unconditional French shift)
  fr rates  = confirmed-French greedy rates per pooled condition
CIs: paired bootstrap over prompt ids (the same 400 prompts appear in every condition).
Pooled conditions: FEM = trained + held-out names + held-out template (likewise MASC); also reports
trained-only numbers that are directly comparable to the paper's Table 4.

    python e06_analyze.py --root /data2/xiangding/skt/E06 --runs student_ff_s1,student_null_s1,student_rand_s1
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

FEM = ["FEM_trained", "FEM_heldout_names", "FEM_heldout_tmpl"]
MASC = ["MASC_trained", "MASC_heldout_names", "MASC_heldout_tmpl"]


def load(pred):
    rows = [json.loads(l) for l in open(pred)]
    by = defaultdict(dict)
    for r in rows:
        by[r["condition_id"]][r["prompt_id"]] = r
    return by


def stats(by, ref, conds_f=FEM, conds_m=MASC):
    pids = sorted(by["REF_none"])
    def m(b, conds, p):
        return np.mean([b[c][p]["margin"] for c in conds if p in b[c]])
    arr = {}
    for name, (b, sign) in {"s": (by, 1), "r": (ref, 1)}.items():
        arr[name] = np.array([[m(b, conds_f, p), m(b, conds_m, p), b["REF_none"][p]["margin"]] for p in pids])
    d = arr["s"] - arr["r"]
    out = {"binding": d[:, 0] - d[:, 1], "name": d[:, 1] - d[:, 2], "uncond": d[:, 2],
           "fem_shift": d[:, 0], "masc_shift": d[:, 1]}
    return out


def ci(v, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    bs = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(B)]
    return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def rates(by):
    fr = lambda conds: float(np.mean([r["confirmed_fr"] for c in conds for r in by[c].values()]))
    return {"FEM_fr": fr(FEM), "MASC_fr": fr(MASC), "REF_fr": fr(["REF_none"]),
            "FEM_trained_fr": fr(["FEM_trained"]), "MASC_trained_fr": fr(["MASC_trained"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/data2/xiangding/skt/E06")
    ap.add_argument("--runs", default="student_ff_s1,student_null_s1,student_rand_s1")
    ap.add_argument("--ref", default="base_eval")
    ap.add_argument("--ref-run", help="use this run's SAME epoch as reference (e.g. student_null_s1), paired by prompt")
    ap.add_argument("--out")
    a = ap.parse_args()
    root = Path(a.root)
    ref = load(root / a.ref / "predictions.jsonl")
    result = {}
    for run in a.runs.split(","):
        evd = root / f"{run}.eval"
        eps = sorted((int(p.name[2:]), p) for p in evd.glob("ep*") if (p / "predictions.jsonl").exists()) if evd.exists() else []
        for ep, p in eps:
            by = load(p / "predictions.jsonl")
            r = ref
            if a.ref_run:
                rp = root / f"{a.ref_run}.eval" / f"ep{ep}" / "predictions.jsonl"
                if not rp.exists():
                    continue
                r = load(rp)
            s = stats(by, r)
            row = {k: ci(v) for k, v in s.items()}
            row.update(rates(by))
            result.setdefault(run, {})[ep] = row
            print(f"{run:18s} ep{ep:2d} binding {row['binding'][0]:+6.2f} [{row['binding'][1]:+.2f},{row['binding'][2]:+.2f}]"
                  f"  name {row['name'][0]:+5.2f}  uncond {row['uncond'][0]:+5.2f} [{row['uncond'][1]:+.2f},{row['uncond'][2]:+.2f}]"
                  f"  FEMfr {row['FEM_trained_fr']:.3f} MASCfr {row['MASC_trained_fr']:.3f} REFfr {row['REF_fr']:.3f}")
    if a.out:
        Path(a.out).write_text(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
