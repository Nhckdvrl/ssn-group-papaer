"""CT03 E01.5 report -- alpha sweep, linearity, stratification, depth drift, cost.

Adjudication quantity (docs/E015_DESIGN.md section 7):
  r1 = per-token median Spearman(px_shared, dL_seq) at layer 1, boundary, alpha=0.125
"""
import json, math
from collections import defaultdict
import numpy as np
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e01_report import spearman

ALPHAS = [0.125, 0.25, 0.5, 1.0]
D, F_, E, K, L, V = 2048, 1024, 64, 8, 16, 50304


def cell(groups):
    """groups: list of per-token candidate lists."""
    rhos, t1, t3, sign, reg = [], [], [], [], []
    for g in groups:
        ex = np.array([r["dL_seq"] for r in g])
        pr = np.array([r["px_shared"] for r in g])
        rho = spearman(pr, ex)
        if not math.isnan(rho):
            rhos.append(rho)
        best = int(ex.argmin()); order = pr.argsort()
        t1.append(float(order[0] == best)); t3.append(float(best in order[:3].tolist()))
        spread = ex.max() - ex.min()
        reg.append(float((ex[order[0]] - ex[best]) / spread) if spread > 0 else 0.0)
        ben = ex < 0
        if ben.any() and (~ben).any():
            sign.append(float(((pr < 0) == ben).mean()))
    return dict(n_tokens=len(groups),
                rho_median=float(np.median(rhos)) if rhos else float("nan"),
                top1=float(np.mean(t1)), top3=float(np.mean(t3)),
                norm_regret=float(np.mean(reg)),
                sign_acc=float(np.mean(sign)) if sign else float("nan"))


recs = [json.loads(l) for l in open("results/e015_records.jsonl")]
layers = sorted({r["layer"] for r in recs})
pools = ["boundary", "random"]

by = defaultdict(lambda: defaultdict(list))
for r in recs:
    by[(r["layer"], r["alpha"], r["pool"], r["stratum"])][(r["q"], r["pos"])].append(r)

res = {"n_records": len(recs), "cells": {}}
for k, toks in by.items():
    res["cells"]["|".join(map(str, k))] = cell(list(toks.values()))

# pooled over stratum, which is how the adjudication reads it
byp = defaultdict(lambda: defaultdict(list))
for r in recs:
    byp[(r["layer"], r["alpha"], r["pool"])][(r["q"], r["pos"], r["stratum"])].append(r)
res["cells_allstrata"] = {"|".join(map(str, k)): cell(list(t.values()))
                          for k, t in byp.items()}

print("=" * 78)
print("A. rho_med(px_shared, dL_seq) by layer x alpha   [hard tokens]")
for pool in pools:
    print(f"\n-- pool={pool}")
    print(f"{'layer':>6}" + "".join(f"{'a=' + str(a):>10}" for a in ALPHAS))
    for l in layers:
        row = [res["cells"].get(f"{l}|{a}|{pool}|hard", {}).get("rho_median", float('nan'))
               for a in ALPHAS]
        print(f"{l:>6}" + "".join(f"{v:>10.3f}" for v in row))

print("\n" + "=" * 78)
print("B. top-3 recall by layer x alpha  [hard, boundary]")
print(f"{'layer':>6}" + "".join(f"{'a=' + str(a):>10}" for a in ALPHAS))
for l in layers:
    row = [res["cells"].get(f"{l}|{a}|boundary|hard", {}).get("top3", float('nan'))
           for a in ALPHAS]
    print(f"{l:>6}" + "".join(f"{v:>10.3f}" for v in row))

print("\n" + "=" * 78)
print("C. lin_ratio = dL_exact / (alpha * g.dh), median -- 1.0 means first order is exact")
print(f"{'layer':>6}" + "".join(f"{'a=' + str(a):>10}" for a in ALPHAS))
lin = {}
for l in layers:
    row = []
    for a in ALPHAS:
        v = [r["lin_ratio"] for r in recs
             if r["layer"] == l and r["alpha"] == a and np.isfinite(r["lin_ratio"])]
        row.append(float(np.median(v)))
    lin[l] = row
    print(f"{l:>6}" + "".join(f"{x:>10.3f}" for x in row))
res["lin_ratio_median"] = lin

print("\n" + "=" * 78)
print("D. error stratified by perturbation size  [layer 1 and 7, alpha=1, hard]")
print(f"{'layer':>6}{'||dh|| quartile':>18}{'rho_med':>10}{'lin_ratio':>11}{'n':>7}")
for l in (1, 7):
    sub = [r for r in recs if r["layer"] == l and r["alpha"] == 1.0 and r["stratum"] == "hard"]
    qs = np.quantile([r["dh_norm"] for r in sub], [0.25, 0.5, 0.75])
    for qi, (lo, hi) in enumerate(zip([-np.inf] + list(qs), list(qs) + [np.inf])):
        s2 = [r for r in sub if lo <= r["dh_norm"] < hi]
        if len(s2) < 20:
            continue
        g2 = defaultdict(list)
        for r in s2:
            g2[(r["q"], r["pos"], r["pool"])].append(r)
        gs = [v for v in g2.values() if len(v) >= 3]
        rr = [spearman([x["px_shared"] for x in v], [x["dL_seq"] for x in v]) for v in gs]
        rr = [x for x in rr if not math.isnan(x)]
        lr = float(np.median([r["lin_ratio"] for r in s2 if np.isfinite(r["lin_ratio"])]))
        print(f"{l:>6}{'Q' + str(qi + 1):>18}"
              f"{(float(np.median(rr)) if rr else float('nan')):>10.3f}{lr:>11.3f}{len(s2):>7}")

print("\n" + "=" * 78)
print("E. by candidate router rank  [layer 1, alpha=1, hard]  rank 8..15 = boundary")
sub = [r for r in recs if r["layer"] == 1 and r["alpha"] == 1.0 and r["stratum"] == "hard"]
rk = defaultdict(list)
for r in sub:
    rk["boundary" if r["pool"] == "boundary" else "random"].append(r)
for pool, rs in rk.items():
    med_rank = float(np.median([r["rank_j"] for r in rs]))
    med_dh = float(np.median([r["dh_norm"] for r in rs]))
    lr = float(np.median([r["lin_ratio"] for r in rs if np.isfinite(r["lin_ratio"])]))
    print(f"  {pool:<10} median rank_j={med_rank:5.1f}  median||dh||={med_dh:.4f}  lin_ratio={lr:.3f}")

# ---- depth drift ----
print("\n" + "=" * 78)
print("F. direction drift cos(actual, linear) at alpha=1, by relative depth")
drift = [json.loads(l) for l in open("results/e015_drift.jsonl")]
ai = ALPHAS.index(1.0)
prof = defaultdict(lambda: defaultdict(list))
for d in drift:
    for dep in d["depth"]:
        for c in range(d["n_cand"]):
            prof[d["layer"]][dep["rel_depth"]].append(dep["cos_lin"][c * len(ALPHAS) + ai])
res["drift_cos_by_layer"] = {}
for l in sorted(prof):
    xs = sorted(prof[l])
    vals = [float(np.median(prof[l][x])) for x in xs]
    res["drift_cos_by_layer"][l] = dict(rel_depth=xs, cos_median=vals)
    print(f"  L{l:<2} " + " ".join(f"{v:5.2f}" for v in vals))

# ---- cost / break-even ----
def attn_flops(T): return 2 * 4 * D * D + 2 * 2 * T * D
def layer_flops(T): return attn_flops(T) + K * 2 * 3 * D * F_
expert_flops = 2 * 3 * D * F_
T = 334.0; tail = 129.0
bwd = 2 * L * T * layer_flops(T) + 2 * T * 2 * D * V

print("\n" + "=" * 78)
print("G. cost ratio (exact / proxy) vs candidates harvested per shared backward")
print(f"{'cands/seq':>10}" + "".join(f"{'L' + str(l):>9}" for l in layers))
cost = {}
for n in (4, 8, 16, 32, 64, 256, 768, 1024, 4096, 16384):
    proxy = expert_flops + bwd / n
    row = []
    for l in layers:
        exact = (L - 1 - l) * tail * layer_flops(T) + tail * 2 * D * V
        row.append(exact / proxy)
    cost[n] = row
    print(f"{n:>10}" + "".join(f"{v:>9.1f}" for v in row))
res["cost_ratio_by_cands"] = {str(k): v for k, v in cost.items()}

print("\n  break-even (ratio = 1x), candidates per sequence:")
be = {}
for l in layers:
    exact = (L - 1 - l) * tail * layer_flops(T) + tail * 2 * D * V
    be[l] = bwd / (exact - expert_flops) if exact > expert_flops else float("inf")
    print(f"    layer {l:>2}: {be[l]:8.1f}")
res["break_even_cands_per_seq"] = be

r1 = res["cells"].get("1|0.125|boundary|hard", {}).get("rho_median", float("nan"))
res["r1_layer1_boundary_a0125_hard"] = r1
print("\n" + "=" * 78)
print(f"ADJUDICATION  r1 = {r1:.3f}   (STAGE B if >= 0.60, SHRINK if < 0.40)")
json.dump(res, open("results/e015_report.json", "w"), indent=1)
print("wrote results/e015_report.json")
