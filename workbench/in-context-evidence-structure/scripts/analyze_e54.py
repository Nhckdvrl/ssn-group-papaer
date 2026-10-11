"""E54 analysis: retention of the A-B separation, threshold-type vs marginal-type source differences."""
import json, sys, glob, os
import numpy as np
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.npz")):
    z = np.load(f); L = z["ld"]; C = list(z["conds"]); qs = z["qscore"]
    q = np.nanmean(L, -1)
    rng = np.random.default_rng(0); B = [rng.integers(0, q.shape[0], q.shape[0]) for _ in range(2000)]
    r = {}
    for ty in ("thr", "mar"):
        Ds = q[:, C.index(f"{ty}|single_A"), 0] - q[:, C.index(f"{ty}|single_B"), 1]
        Dm = q[:, C.index(f"{ty}|mixed"), 0] - q[:, C.index(f"{ty}|mixed"), 1]
        r[f"{ty}_D_single"] = float(Ds.mean()); r[f"{ty}_D_mixed"] = float(Dm.mean())
        r[f"{ty}_retention"] = float(Dm.mean() / Ds.mean())
        r[f"{ty}_retention_ci"] = np.percentile([Dm[b].mean() / Ds[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
        # where on the content axis is the single-context separation (borderline vs extremes)?
        per_q = np.nanmean(L[:, C.index(f"{ty}|single_A"), 0, :] - L[:, C.index(f"{ty}|single_B"), 1, :], 0)
        r[f"{ty}_sep_by_score"] = {k: float(per_q[m].mean()) for k, m in (("low<0", qs < 0), ("mid0-1", (qs >= 0) & (qs <= 1)), ("high>1", qs > 1))}
    Dt = lambda ty, c, w: q[:, C.index(f"{ty}|{c}"), w]
    diff = (Dt("mar", "mixed", 0) - Dt("mar", "mixed", 1)) / (Dt("mar", "single_A", 0) - Dt("mar", "single_B", 1)).mean() - \
           (Dt("thr", "mixed", 0) - Dt("thr", "mixed", 1)) / (Dt("thr", "single_A", 0) - Dt("thr", "single_B", 1)).mean()
    r["mar_minus_thr_retention_ci"] = np.percentile([diff[b].mean() for b in B], [2.5, 97.5]).round(3).tolist()
    out[os.path.basename(f)[:-4]] = r
json.dump(out, open(sys.argv[1] + "/analysis.json", "w"), indent=1)
for m, r in out.items():
    print(f"{m:18s} thr: single {r['thr_D_single']:.2f} retention {r['thr_retention']:.2f} {r['thr_retention_ci']} | "
          f"mar: single {r['mar_D_single']:.2f} retention {r['mar_retention']:.2f} {r['mar_retention_ci']} | mar-thr CI {r['mar_minus_thr_retention_ci']}")
