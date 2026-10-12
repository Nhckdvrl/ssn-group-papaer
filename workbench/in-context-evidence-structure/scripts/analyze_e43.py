"""E43 analysis: (a) temperature intervention, (b) perturbation spectrum, (c) LOO stability across orders."""
import json, sys, collections, re
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
meta = {}
for l in open(ROOT / "data/kernel/rows.jsonl"):
    r = json.loads(l)
    if r["var"] == -1: meta[r["base_id"]] = r["meta"]
out = {}
# (a)
z = np.load(ROOT / f"results/e43/temp_{tag}.npz"); uid = z["uid"]; base = np.array([u.split("|")[0] for u in uid])
ub = sorted(set(base))
a = {}
for c in [k for k in z.files if k != "uid"]:
    ld = z[c]; per = collections.defaultdict(list)
    for b, l in zip(base, ld): per[b].append(l)
    rms = float(np.median([np.std(v) for v in per.values()])); mu = {b: np.mean(v) for b, v in per.items()}
    ev = float(np.std(list(mu.values())))
    acc = float(np.mean([(mu[b] > 0) == (meta[b]["qA"] == 1) for b in ub if meta[b]["tau"] == "clean"]))
    sep = float(np.mean([mu[b] * (1 if meta[b]["qA"] == 0 else -1) * (1 if meta[b]["qa"] == 1 else -1) for b in ub if meta[b]["tau"] == "ann"]))
    a[c] = {"order_rms": round(rms, 3), "evidence_sd": round(ev, 3), "snr": round(ev / rms, 2), "clean_acc": round(acc, 3), "ann_sep": round(sep, 3)}
out["a_temperature"] = a
# (b, c)
p = np.load(ROOT / f"results/e43/pert_{tag}.npz"); P = dict(zip(p["uid"], p["ld"]))
pb = sorted({u.split("|")[0] for u in P})
spec = {}
for k in ("offset", "header", "names", "num", "swapadj", "perm1"):
    d = np.array([P[f"{b}|{k}"] - P[f"{b}|orig"] for b in pb])
    spec[k] = {"median_abs": round(float(np.median(np.abs(d))), 3), "rms": round(float(np.sqrt((d ** 2).mean())), 3)}
out["b_spectrum"] = spec
K = np.load(ROOT / f"results/kernel/{tag}.npz"); KD = dict(zip(K["uid"], K["ld"]))
rs, top3, pooled0, pooled1 = [], [], [], []
for b in pb:
    i0 = np.array([KD[f"{b}|-1"] - KD[f"{b}|{t}"] for t in range(16)])
    i1 = np.array([P[f"{b}|perm1"] - P[f"{b}|perm1_del{t}"] for t in range(16)])
    rs.append(spearmanr(i0, i1).correlation); top3.append(len(set(np.argsort(-np.abs(i0))[:3]) & set(np.argsort(-np.abs(i1))[:3])) / 3)
    pooled0 += list(i0); pooled1 += list(i1)
out["c_loo_stability"] = {"median_within_base_spearman": round(float(np.nanmedian(rs)), 3),
                          "mean_top3_overlap_abs": round(float(np.mean(top3)), 3), "chance_top3": round(3 / 16, 3),
                          "pooled_pearson": round(float(np.corrcoef(pooled0, pooled1)[0, 1]), 3)}
(ROOT / f"results/e43/{tag}_analysis.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
