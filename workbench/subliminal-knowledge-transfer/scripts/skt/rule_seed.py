#!/usr/bin/env python3
"""Student-level "rule vs seed" decomposition in behaviour space (E05 amendment 4).

Vectors over rows (condition x prompt x {fr, de}):
  v_s   = m(student) - m(S_null, same epoch)
  u_ck  = m(teacher c, seed k, ep10) - m(T_null, ep10)
Teacher decomposition (4 configs x 3 seeds):
  g_c   = mean_k u_ck - mean_ck u_ck        rule pattern of config c (config-specific, seed-free)
  d_ck  = u_ck - mean_k u_ck                seed pattern of teacher (c, k) (sums to 0 over k)
Readouts for student s = (c, k):
  beta_rule = <v, g_c> / <g_c, g_c>         fraction of own rule pattern reproduced
  beta_seed = <v, d_ck> / <d_ck, d_ck>      fraction of own teacher's seed pattern reproduced
  null for beta_seed: same quantity with the other seeds' d_ck' (k' != k); null for beta_rule: other configs' g_c'
  plus Pearson correlations for the same pairs.
CIs: bootstrap over prompt ids (rows of one prompt id move together).

    python rule_seed.py --students E05/student_FF_s1:FF:1,E05/student_FF_s2:FF:2 [--out OUT.json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from e05_analyze import ROOT, load

CFGS = ["FF", "FG", "MF", "MG"]


def mat(rows, ref, conds, pids):
    """array [n_pid, n_cond*2] of m(rows) - m(ref)."""
    return np.array([[rows[c][p][f"m_{l}"] - ref[c][p][f"m_{l}"] for c in conds for l in ("fr", "de")] for p in pids])


def proj(v, d):
    return float((v * d).sum() / (d * d).sum())


def corr(v, d):
    v, d = v.ravel() - v.mean(), d.ravel() - d.mean()
    return float((v * d).sum() / np.sqrt((v * v).sum() * (d * d).sum()))


def stats(v, own, others, B=1000):
    """point + bootstrap CI over prompt rows for proj(own) - mean proj(others), and both parts."""
    def f(idx):
        vv = v[idx]
        po = proj(vv, own[idx]); pn = np.mean([proj(vv, o[idx]) for o in others])
        co = corr(vv, own[idx]); cn = np.mean([corr(vv, o[idx]) for o in others])
        return np.array([po, pn, po - pn, co, cn, co - cn])
    n = len(v); pt = f(np.arange(n))
    rng = np.random.default_rng(0)
    bs = np.array([f(rng.integers(0, n, n)) for _ in range(B)])
    lo, hi = np.percentile(bs, 2.5, axis=0), np.percentile(bs, 97.5, axis=0)
    keys = ["proj_own", "proj_null", "proj_diff", "corr_own", "corr_null", "corr_diff"]
    return {k: [float(pt[i]), float(lo[i]), float(hi[i])] for i, k in enumerate(keys)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--students", required=True, help="REL:CFG:SEED,...")
    ap.add_argument("--null-student", default="E06/student_null_s1")
    ap.add_argument("--tnull", default="E06/tnullview.evalfac/ep10")
    ap.add_argument("--teacher-ep", default="ep10")
    ap.add_argument("--epochs", help="comma list; default all available")
    ap.add_argument("--out")
    a = ap.parse_args()

    tn = load(ROOT / a.tnull / "rows.jsonl")
    T = {(c, k): load(ROOT / f"E03/eval/{c}_s{k}_{a.teacher_ep}/rows.jsonl") for c in CFGS for k in (1, 2, 3)}
    conds = sorted(tn)
    pids = sorted(tn["REF_none"])
    U = {ck: mat(t, tn, conds, pids) for ck, t in T.items()}
    grand = np.mean(list(U.values()), axis=0)
    cmean = {c: np.mean([U[(c, k)] for k in (1, 2, 3)], axis=0) for c in CFGS}
    G = {c: cmean[c] - grand for c in CFGS}
    D = {(c, k): U[(c, k)] - cmean[c] for c in CFGS for k in (1, 2, 3)}
    # teacher-side sizes: how big are the rule vs seed patterns themselves (rms per row)
    rms = lambda x: float(np.sqrt((x ** 2).mean()))
    print("teacher rms per row: " + "  ".join(f"{c}: rule {rms(G[c]):.2f} seed {np.mean([rms(D[(c, k)]) for k in (1, 2, 3)]):.2f}" for c in CFGS))

    res = {"teacher_rms": {c: {"rule": rms(G[c]), "seed": [rms(D[(c, k)]) for k in (1, 2, 3)]} for c in CFGS}}
    want = set(int(e) for e in a.epochs.split(",")) if a.epochs else None
    for spec in a.students.split(","):
        rel, c, k = spec.split(":"); k = int(k)
        d = ROOT / f"{rel}.evalfac"
        for p in sorted([q for q in d.glob("ep*") if (q / "rows.jsonl").exists()], key=lambda q: int(q.name[2:])):
            ep = int(p.name[2:])
            if want and ep not in want:
                continue
            nr = ROOT / f"{a.null_student}.evalfac/ep{ep}/rows.jsonl"
            if not nr.exists():
                continue
            v = mat(load(p / "rows.jsonl"), load(nr), conds, pids)
            rule = stats(v, G[c], [G[o] for o in CFGS if o != c])
            seed = stats(v, D[(c, k)], [D[(c, o)] for o in (1, 2, 3) if o != k])
            res.setdefault(rel, {})[ep] = {"rule": rule, "seed": seed}
            fmt = lambda x: f"{x[0]:+.3f} [{x[1]:+.3f},{x[2]:+.3f}]"
            print(f"{rel:22s} {c} s{k} ep{ep:2d} | RULE beta own {fmt(rule['proj_own'])} null {rule['proj_null'][0]:+.3f}"
                  f" r own {rule['corr_own'][0]:+.3f} null {rule['corr_null'][0]:+.3f}"
                  f" | SEED beta own {fmt(seed['proj_own'])} null {seed['proj_null'][0]:+.3f} diff {fmt(seed['proj_diff'])}"
                  f" r own {seed['corr_own'][0]:+.3f} null {seed['corr_null'][0]:+.3f}")
    # crossed design (the clean seed test): students of the same config, different seeds, same epoch.
    # P[i, j] = proj(v_student_seed_i, d_teacher_seed_j); seed inheritance = mean diag - mean off-diag over i != j.
    # Both students share the rule, so g.d overlaps cancel; null = 0 without assumptions on d.
    vecs = {}
    for spec in a.students.split(","):
        rel, c, k = spec.split(":")
        for ep in res.get(rel, {}):
            nr = ROOT / f"{a.null_student}.evalfac/ep{ep}/rows.jsonl"
            vecs[(c, int(k), ep)] = mat(load(ROOT / f"{rel}.evalfac/ep{ep}/rows.jsonl"), load(nr), conds, pids)
    cross = {}
    for c in CFGS:
        for ep in sorted({e for (cc, _, e) in vecs if cc == c}):
            ks = sorted(k for (cc, k, e) in vecs if cc == c and e == ep)
            if len(ks) < 2:
                continue
            def f(idx, fn=proj):
                diag = [fn(vecs[(c, i, ep)][idx], D[(c, i)][idx]) for i in ks]
                off = [fn(vecs[(c, i, ep)][idx], D[(c, j)][idx]) for i in ks for j in ks if i != j]
                return np.array([np.mean(diag), np.mean(off), np.mean(diag) - np.mean(off)])
            n = len(pids); rng = np.random.default_rng(0)
            pt = f(np.arange(n)); bs = np.array([f(rng.integers(0, n, n)) for _ in range(1000)])
            lo, hi = np.percentile(bs, 2.5, axis=0), np.percentile(bs, 97.5, axis=0)
            cross[f"{c}_ep{ep}"] = {"seeds": ks, "diag": pt[0], "off": pt[1], "diff": [float(pt[2]), float(lo[2]), float(hi[2])]}
            print(f"CROSSED {c} ep{ep:2d} seeds {ks}: beta_seed own {pt[0]:+.3f}  other-student {pt[1]:+.3f}  diff {pt[2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")
    res["crossed"] = cross
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
