"""E50 analysis: personalization gain in log-loss on each annotator's own held-out labels."""
import json, sys, glob, os
import numpy as np
LL = lambda ld, y: np.log1p(np.exp(-np.where(y == 1, 1, -1) * ld))
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.npz")):
    z = np.load(f); L = z["ld"].astype(np.float64); Y = z["y"]; C = list(z["conds"])
    g = lambda c, w: np.nanmean(LL(L[:, C.index(c), w], Y[:, w]), -1)          # per pair
    acc = lambda c, w: np.nanmean((L[:, C.index(c), w] > 0) == (Y[:, w] == 1), -1)
    r = {}
    for w, own, cross in ((0, "single_A", "single_B_as_A"), (1, "single_B", "single_A_as_B")):
        side = "A" if w == 0 else "B"
        gain = g(cross, w) - g(own, w)
        r[f"{side}_gain_LL"] = float(gain.mean())
        r[f"{side}_acc_own_cross"] = [float(acc(own, w).mean()), float(acc(cross, w).mean())]
        conds = ["mixed", "mixed_instr"] + (["mixed_far"] if w == 0 else [])
        for c in conds:
            kept = (g(cross, w) - g(c, w))
            r[f"{side}_retained_{c}"] = float(kept.mean() / gain.mean())
            rng = np.random.default_rng(0); B = [rng.integers(0, len(gain), len(gain)) for _ in range(2000)]
            r[f"{side}_retained_{c}_ci"] = np.percentile([kept[b].mean() / gain[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
            r[f"{side}_acc_{c}"] = float(acc(c, w).mean())
    out[os.path.basename(f)[:-4]] = r
json.dump(out, open(sys.argv[1] + "/analysis.json", "w"), indent=1)
print(json.dumps(out, indent=1))
