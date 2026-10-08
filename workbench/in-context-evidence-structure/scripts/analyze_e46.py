"""E46 analysis: separation of annotator A vs B under single vs mixed contexts (pair-level bootstrap)."""
import json, sys, glob, os
import numpy as np
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.npz")):
    z = np.load(f); L = z["ld"]; conds = list(z["conds"])
    q = np.nanmean(L, -1)                       # [pair, cond, who]
    Ds = q[:, 0, 0] - q[:, 1, 1]
    rng = np.random.default_rng(0); B = [rng.integers(0, len(Ds), len(Ds)) for _ in range(2000)]
    r = {"D_single": float(Ds.mean()), "n_pairs": int(len(Ds))}
    for c in [x for x in ("mixed", "mixed_near", "mixed_far", "mixed_instr") if x in conds]:
        ci = conds.index(c); Dm = q[:, ci, 0] - q[:, ci, 1]
        r[f"D_{c}"] = float(Dm.mean())
        r[f"ratio_{c}"] = float(Dm.mean() / Ds.mean())
        r[f"ratio_{c}_ci"] = np.percentile([Dm[b].mean() / Ds[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
        r[f"level_{c}_A_B"] = [float(q[:, ci, 0].mean()), float(q[:, ci, 1].mean())]
    r["level_single_A_B"] = [float(q[:, 0, 0].mean()), float(q[:, 1, 1].mean())]
    out[os.path.basename(f)[:-4]] = r
json.dump(out, open(sys.argv[1] + "/analysis.json", "w"), indent=1)
print(json.dumps(out, indent=1))
