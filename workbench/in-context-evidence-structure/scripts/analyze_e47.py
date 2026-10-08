"""E47 analysis: interaction separation (race minus gender queries) A vs B, single vs mixed."""
import json, sys, glob, os
import numpy as np
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.npz")):
    z = np.load(f); L = z["ld"]; conds = list(z["conds"])
    I = np.nanmean(L[..., :30], -1) - np.nanmean(L[..., 30:], -1)      # [pair, cond, who]
    Ds = I[:, 0, 0] - I[:, 1, 1]
    rng = np.random.default_rng(0); B = [rng.integers(0, len(Ds), len(Ds)) for _ in range(2000)]
    r = {"D_single": float(Ds.mean())}
    for c in [x for x in ("mixed", "mixed_near", "mixed_far", "mixed_instr") if x in conds]:
        ci = conds.index(c); Dm = I[:, ci, 0] - I[:, ci, 1]
        r[f"ratio_{c}"] = float(Dm.mean() / Ds.mean())
        r[f"ratio_{c}_ci"] = np.percentile([Dm[b].mean() / Ds[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
    out[os.path.basename(f)[:-4]] = r
json.dump(out, open(sys.argv[1] + "/analysis.json", "w"), indent=1)
print(json.dumps(out, indent=1))
