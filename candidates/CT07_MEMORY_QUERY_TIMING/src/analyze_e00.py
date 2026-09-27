"""E00 readout: R_s = (G_DEPLOY - G_s) / (G_DEPLOY - G_FUTURE) per source x budget, and the frozen rule.

usage: analyze_e00.py RESULTS_GLOB
"""
import glob, json, sys
import numpy as np

rng = np.random.default_rng(0)
recs = []
for f in sorted(glob.glob(sys.argv[1])):
    recs += [json.loads(l) for l in open(f)]
skips = [r for r in recs if "skip" in r]
recs = [r for r in recs if "skip" not in r]
print(f"{len(recs)} checkpoints ({len(skips)} skipped: no value/name), "
      f"{len({r['traj'] for r in recs})} trajectories")

STAGES = {"tau": ["HDR", "TOOL", "KEY", "PREVALUE", "LEX"], "swe": ["HDR", "PROSE", "TOOL", "PREVALUE", "LEX"]}


def R(sub, st, bud):
    d = np.mean([r["G"][f"DEPLOY@{bud}"] for r in sub])
    f = np.mean([r["G"][f"FUTURE@{bud}"] for r in sub])
    s = np.mean([r["G"][f"{st}@{bud}"] for r in sub])
    return (d - s) / (d - f) if abs(d - f) > 1e-9 else np.nan


def boot(sub, st, bud, n=2000):
    trajs = sorted({r["traj"] for r in sub})
    by = {t: [r for r in sub if r["traj"] == t] for t in trajs}
    vals = []
    for _ in range(n):
        pick = rng.choice(trajs, len(trajs))
        vals.append(R([r for t in pick for r in by[t]], st, bud))
    return np.nanpercentile(vals, [2.5, 97.5])


out = {}
for src in ["tau", "swe"]:
    S = [r for r in recs if r["src"] == src]
    print(f"\n=== {src}: {len(S)} checkpoints, value tokens/ckpt median {int(np.median([r['n_value'] for r in S]))}")
    for bud in ["0.25", "0.5"]:
        g = {p: np.mean([r["G"][f"{p}@{bud}"] for r in S if f"{p}@{bud}" in r["G"]])
             for p in ["DEPLOY", "HDR", "PROSE", "TOOL", "KEY", "PREVALUE", "FUTURE", "LEX", "oracle", "random"]
             if any(f"{p}@{bud}" in r["G"] for r in S)}
        print(f"  budget {bud}: mean value-token dNLL " + ", ".join(f"{k} {v:.2f}" for k, v in g.items()))
        for st in STAGES[src]:
            sub = [r for r in S if f"{st}@{bud}" in r["G"]]
            if not sub:
                continue
            v = R(sub, st, bud)
            lo, hi = boot(sub, st, bud)
            out[(src, bud, st)] = (v, lo, hi)
            print(f"     R_{st:9s} = {v:6.2f}  [{lo:6.2f}, {hi:6.2f}]  (n={len(sub)})")
    sp = {}
    for st in ["DEPLOY"] + STAGES[src][:-1] + ["FUTURE", "LEX"]:
        v = [r["spearman_oracle"].get(st) for r in S if r["spearman_oracle"].get(st) is not None]
        if v:
            sp[st] = round(float(np.mean(v)), 3)
    print("  within-ckpt Spearman(stage attention, CT05 block oracle):", sp)

print("\n=== frozen decision rule")
pv = {(s, b): out[(s, b, "PREVALUE")] for s in ["tau", "swe"] for b in ["0.25", "0.5"]}
kill1 = all(pv[k][0] < 0.3 for k in pv)
lexratio = {(s, b): out[(s, b, "LEX")][0] / pv[(s, b)][0] if pv[(s, b)][0] > 0 else np.inf
            for s in ["tau", "swe"] for b in ["0.25", "0.5"] if (s, b, "LEX") in out}
kill2 = all(lexratio.get(("tau", b), 0) >= 0.8 for b in ["0.25", "0.5"])
struct = all(any(pv[(s, b)][0] >= 0.5 and pv[(s, b)][1] > 0.2 and lexratio.get((s, b), 0) < 0.8
                 for b in ["0.25", "0.5"]) for s in ["tau", "swe"])
print("  R_PREVALUE:", {f"{k[0]}@{k[1]}": round(v[0], 2) for k, v in pv.items()})
print("  LEX / PREVALUE:", {f"{k[0]}@{k[1]}": round(v, 2) for k, v in lexratio.items()})
print("  KILL (no leverage):", kill1, "| KILL (lexical):", kill2, "| STRUCTURE PRESENT:", struct,
      "| otherwise ambiguous")
