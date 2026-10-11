"""E52 analysis: convention-dependent accuracy on offensive-but-not-hate tweets."""
import json, sys, glob, os
import numpy as np
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.npz")):
    z = np.load(f); L = z["ld"]; Y = z["y"]; QC = z["qc"]; C = list(z["conds"])
    acc = lambda c, w, cls: np.nanmean(np.where(QC == cls, ((L[:, C.index(c), w] > 0) == (Y[:, w] == 1)).astype(float), np.nan), -1)
    r = {}; rng = np.random.default_rng(0)
    for w, own, cross, side in ((0, "single_A", "cross_A", "A"), (1, "single_B", "cross_B", "B")):
        gain = acc(own, w, 1) - acc(cross, w, 1); B = [rng.integers(0, len(gain), len(gain)) for _ in range(2000)]
        r[f"{side}_offensive_acc_own_cross"] = [float(acc(own, w, 1).mean()), float(acc(cross, w, 1).mean())]
        r[f"{side}_gain"] = float(gain.mean())
        r[f"{side}_hate_neither_acc_own"] = [float(acc(own, w, 0).mean()), float(acc(own, w, 2).mean())]
        for c in ["mixed", "mixed_instr"] + (["mixed_far"] if w == 0 else []):
            kept = acc(c, w, 1) - acc(cross, w, 1)
            r[f"{side}_offensive_acc_{c}"] = float(acc(c, w, 1).mean())
            r[f"{side}_retained_{c}"] = float(kept.mean() / gain.mean())
            r[f"{side}_retained_{c}_ci"] = np.percentile([kept[b].mean() / gain[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
    r["B_offensive_acc_far_vs_singlefar"] = [float(acc("mixed_far", 1, 1).mean()), float(acc("single_B_far", 1, 1).mean())]
    out[os.path.basename(f)[:-4]] = r
json.dump(out, open(sys.argv[1] + "/analysis.json", "w"), indent=1)
print(json.dumps(out, indent=1))
