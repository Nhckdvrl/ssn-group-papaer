"""E85: does a random 10% mask change the winning induction head more often when the two leading candidates are close?

Usage: e85_analyze.py -> results/e85/analysis.json + printed verdicts (protocol: experiments/E85-*.md)
"""
import json

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc

E46 = mc.RESULTS / "e46"
OUT = mc.RESULTS / "e85"


def load(name):
    f = E46 / f"{name}.json"
    return json.loads(f.read_text()) if f.exists() else None


def top2(M):
    M = np.array(M)
    o = np.argsort(M.ravel())[::-1]
    H = M.shape[1]
    return (int(o[0] // H), int(o[0] % H)), float(M.ravel()[o[0]] - M.ravel()[o[1]])


def main():
    rows = []
    for i in range(1, 16):
        b = load(f"L_i{i}_c4_o1_st3000")
        if b is None:
            continue
        h, gap = top2(b["measures"]["3000"]["M1"])
        _, gap1000 = top2(b["measures"]["1000"]["M1"])
        for ms, name in ((0, f"L_i{i}_c4_o1_st3000_maskrandom0.1_500-2000"), (1, f"L_i{i}_c4_o1_st3000_maskrandom0.1_500-2000_ms1")):
            d = load(name)
            if d is None:
                continue
            hm, _ = top2(d["measures"]["3000"]["M1"])
            rows.append({"init": i, "mask_seed": ms, "base_head": f"{h[0]}.{h[1]}", "masked_head": f"{hm[0]}.{hm[1]}",
                         "swap": hm != h, "gap3000": gap, "gap1000": gap1000,
                         "copy_ratio": d["measures"]["3000"]["copy_gain"] / b["measures"]["3000"]["copy_gain"]})
    gaps = np.array([r["gap3000"] for r in rows])
    swaps = np.array([r["swap"] for r in rows], dtype=float)
    res = {"rows": rows, "n_runs": len(rows), "n_inits": len({r["init"] for r in rows}), "swap_rate": float(swaps.mean())}
    if len(rows) >= 6 and swaps.std() > 0:
        res["spearman_gap_swap"] = float(spearmanr(gaps, swaps)[0])
        res["spearman_gap1000_swap"] = float(spearmanr([r["gap1000"] for r in rows], swaps)[0])
        med = np.median([r["gap3000"] for r in rows])
        lo, hi = swaps[gaps < med], swaps[gaps >= med]
        res["swap_rate_close"] = float(lo.mean())
        res["swap_rate_clear"] = float(hi.mean())
        res["median_gap"] = float(med)
        res["P1"] = res["spearman_gap_swap"] < 0
        res["P2"] = res["swap_rate_close"] >= 2 * max(res["swap_rate_clear"], 1e-9) and res["swap_rate_close"] > 0
        sw = [r["copy_ratio"] for r in rows if r["swap"]]
        res["P3_copy_ratio_in_swaps"] = sw
        res["P3"] = bool(sw) and min(sw) >= 0.9
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
    for r in rows:
        print(f"init {r['init']:2d} ms{r['mask_seed']} gap {r['gap3000']:.3f} (@1000 {r['gap1000']:.3f}) base {r['base_head']:5s} "
              f"masked {r['masked_head']:5s} swap {int(r['swap'])} copy {r['copy_ratio']:.2f}")
    print({k: v for k, v in res.items() if k != "rows"})


if __name__ == "__main__":
    main()
