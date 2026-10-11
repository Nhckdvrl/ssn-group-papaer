"""E51 analysis: personalization gain on real co-rated movies (log-loss / accuracy)."""
import json, sys, glob, os
import numpy as np
LL = lambda ld, y: np.log1p(np.exp(-np.where(y == 1, 1, -1) * ld))
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.npz")):
    z = np.load(f); L = z["ld"].astype(np.float64); Y = z["y"]; C = list(z["conds"])
    valid = Y >= 0
    def g(c, w, fn):
        v = fn(L[:, C.index(c), w], Y[:, w]); v = np.where(valid[:, w], v, np.nan); return np.nanmean(v, -1)
    ll = lambda ld, y: LL(ld, y); acc = lambda ld, y: ((ld > 0) == (y == 1)).astype(float)
    r = {}
    rng = np.random.default_rng(0)
    for w, own, cross, side in ((0, "single_A", "cross_A", "A"), (1, "single_B", "cross_B", "B")):
        gain = g(cross, w, ll) - g(own, w, ll); B = [rng.integers(0, len(gain), len(gain)) for _ in range(2000)]
        r[f"{side}_gain_LL"] = float(gain.mean()); r[f"{side}_gain_LL_ci"] = np.percentile([gain[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
        r[f"{side}_acc_own_cross"] = [float(g(own, w, acc).mean()), float(g(cross, w, acc).mean())]
        for c in ["mixed", "mixed_instr"] + (["mixed_far"] if w == 0 else []):
            kept = g(cross, w, ll) - g(c, w, ll)
            r[f"{side}_retained_{c}"] = float(kept.mean() / gain.mean())
            r[f"{side}_retained_{c}_ci"] = np.percentile([kept[b].mean() / gain[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
            r[f"{side}_acc_{c}"] = float(g(c, w, acc).mean())
    r["B_acc_far_vs_singlefar"] = [float(g("mixed_far", 1, acc).mean()), float(g("single_B_far", 1, acc).mean())]
    out[os.path.basename(f)[:-4]] = r
json.dump(out, open(sys.argv[1] + "/analysis.json", "w"), indent=1)
print(json.dumps(out, indent=1))
