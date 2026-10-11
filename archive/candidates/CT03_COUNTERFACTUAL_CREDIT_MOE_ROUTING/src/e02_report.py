"""CT03 Stage B report -- adjudicates docs/E02_STAGEB_DESIGN.md section 5.

Primary: rho(px_shared, dL_seq), hard tokens, boundary candidates, ALPHA=1,
at L20/L28/L36/L44 (42/58/75/92% relative depth).
"""
import json, math, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e01_report import spearman

PRED = {
    "px_shared": lambda r: r["px_shared"],
    "router_gap": lambda r: -(r["p_j"] - r["p_i"]),
    "neg_dh_norm": lambda r: -r["dh_norm"],
}
PRIMARY_LAYERS = [20, 28, 36, 44]


def cell(groups, rng):
    out = {"n_tokens": len(groups)}
    if not groups:
        return out
    ex_all = np.concatenate([[r["dL_seq"] for r in g] for g in groups])
    out["beneficial_rate"] = float((ex_all < 0).mean())
    out["median_abs_dL"] = float(np.median(np.abs(ex_all)))
    out["median_abs_floor"] = float(np.median([abs(g[0]["floor_seq"]) for g in groups]))
    for name, f in PRED.items():
        rh, t1, t3 = [], [], []
        for g in groups:
            ex = np.array([r["dL_seq"] for r in g]); pr = np.array([f(r) for r in g])
            v = spearman(pr, ex)
            if not math.isnan(v):
                rh.append(v)
            best = int(ex.argmin()); o = pr.argsort()
            t1.append(float(o[0] == best)); t3.append(float(best in o[:3].tolist()))
        out[name] = dict(rho_median=float(np.median(rh)) if rh else float("nan"),
                         top1=float(np.mean(t1)), top3=float(np.mean(t3)))
    t1, t3 = [], []
    for g in groups:
        ex = np.array([r["dL_seq"] for r in g]); best = int(ex.argmin())
        o = rng.permutation(len(g))
        t1.append(float(o[0] == best)); t3.append(float(best in o[:3].tolist()))
    out["random"] = dict(rho_median=0.0, top1=float(np.mean(t1)), top3=float(np.mean(t3)))
    return out


recs = [json.loads(l) for l in open("results/e02_records.jsonl")]
rng = np.random.default_rng(0)
nL = 48
layers = sorted({r["layer"] for r in recs})

res = {"n_records": len(recs), "cells": {}}
for a in (1.0, 0.125):
    for pool in ("boundary", "random"):
        for st in ("hard", "easy"):
            for l in layers:
                g = defaultdict(list)
                for r in recs:
                    if (r["layer"] == l and r["alpha"] == a and r["pool"] == pool
                            and r["stratum"] == st):
                        g[(r["q"], r["pos"])].append(r)
                res["cells"][f"{l}|{a}|{pool}|{st}"] = cell(list(g.values()), rng)

print("=" * 80)
print("PRIMARY  rho(px_shared, dL_seq)  alpha=1, hard, boundary   [Qwen3-30B-A3B, 48L]")
print(f"{'layer':>6}{'depth':>8}{'rho_med':>10}{'top1':>8}{'top3':>8}"
      f"{'router_gap':>12}{'rand_top3':>11}{'benef':>8}{'med|dL|':>10}")
prim = {}
for l in layers:
    c = res["cells"][f"{l}|1.0|boundary|hard"]
    prim[l] = c
    print(f"{l:>6}{l / nL:>8.0%}{c['px_shared']['rho_median']:>10.3f}"
          f"{c['px_shared']['top1']:>8.3f}{c['px_shared']['top3']:>8.3f}"
          f"{c['router_gap']['rho_median']:>12.3f}{c['random']['top3']:>11.3f}"
          f"{c['beneficial_rate']:>8.3f}{c['median_abs_dL']:>10.2e}")

print("\n" + "=" * 80)
print("alpha=0.125 (DIAGNOSTIC ONLY -- barred from the survival decision)")
print(f"{'layer':>6}{'rho_med':>10}")
for l in layers:
    print(f"{l:>6}{res['cells'][f'{l}|0.125|boundary|hard']['px_shared']['rho_median']:>10.3f}")

print("\n" + "=" * 80)
print("random candidate pool, alpha=1, hard")
print(f"{'layer':>6}{'rho_med':>10}{'top3':>8}")
for l in layers:
    c = res["cells"][f"{l}|1.0|random|hard"]
    print(f"{l:>6}{c['px_shared']['rho_median']:>10.3f}{c['px_shared']['top3']:>8.3f}")

# ---- adjudication ----
rhos = [prim[l]["px_shared"]["rho_median"] for l in PRIMARY_LAYERS]
t3s = [prim[l]["px_shared"]["top3"] for l in PRIMARY_LAYERS]
rg = [prim[l]["router_gap"]["rho_median"] for l in PRIMARY_LAYERS]
ben = [prim[l]["beneficial_rate"] for l in PRIMARY_LAYERS]
shallow = [prim[l]["px_shared"]["rho_median"] for l in (20, 28)]

conds = {
    "1. median rho over L20/28/36/44 >= 0.60": (float(np.median(rhos)), np.median(rhos) >= 0.60),
    "2. some layer at <=60% depth with rho >= 0.55": (float(max(shallow)), max(shallow) >= 0.55),
    "3. median top-3 >= 0.70": (float(np.median(t3s)), np.median(t3s) >= 0.70),
    "4. clearly beats router_gap": (float(np.median(rg)), np.median(rhos) - np.median(rg) > 0.25),
    "5. beneficial rate in 0.3-0.7": (float(np.median(ben)), 0.3 <= np.median(ben) <= 0.7),
}
print("\n" + "=" * 80)
print("ADJUDICATION (docs/E02_STAGEB_DESIGN.md section 5)")
for k, (v, ok) in conds.items():
    print(f"  [{'PASS' if ok else 'FAIL'}]  {k:<48} = {v:.3f}")
res["adjudication"] = {k: {"value": v, "pass": bool(o)} for k, (v, o) in conds.items()}
res["all_pass_1_to_5"] = bool(all(o for _, o in conds.values()))
print(f"\n  conditions 1-5: {'ALL PASS' if res['all_pass_1_to_5'] else 'NOT ALL PASS'}"
      "   (condition 6, cost, is computed separately)")
json.dump(res, open("results/e02_report.json", "w"), indent=1)
print("\nwrote results/e02_report.json")
