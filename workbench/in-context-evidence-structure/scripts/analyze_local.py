"""E04 analysis: local (exemplar) vs global (rule) updating.
usage: analyze_local.py DATA_DIR "RESULT_GLOB"
"""
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))


def main():
    data, res = sys.argv[1], sys.argv[2]
    sc = {}
    for f in glob.glob(res):
        for l in open(f):
            s = json.loads(l); sc[s["uid"]] = s["lp"]
    recs = []
    for l in open(Path(data) / "rows.jsonl"):
        r = json.loads(l)
        if r["uid"] not in sc:
            continue
        lp = sc[r["uid"]]; lo1 = lp[1] - lp[0]
        recs.append(dict(cond=r["cond"], q=r["qrank"][:2], base=r["base_id"], E=r["escore"],
                         lo_B=lo1 if r["query_label_B"] == 1 else -lo1,
                         meta=logit(r["oracle"]["meta_pB"]), set=logit(r["oracle"]["set_pB"])))
    df = pd.DataFrame(recs)
    print("cond          LM hi-lo            meta hi-lo   E hi-lo   | LM hi   LM lo")
    out = {}
    for c in ["allA", "disp_4", "disp_8", "suffix_4", "suffix_6", "suffix_8", "prefix_8"]:
        D = df[df.cond == c]
        p = D.groupby(["base", "q"]).agg(lo=("lo_B", "mean"), meta=("meta", "mean"), E=("E", "mean")).unstack()
        d = (p["lo"]["hi"] - p["lo"]["lo"]).dropna()
        out[c] = boot_ci(d)
        print(f"{c:12s} {fmt(*boot_ci(d))}   {(p['meta']['hi'] - p['meta']['lo']).mean():+.2f}      "
              f"{(p['E']['hi'] - p['E']['lo']).mean():+.2f}   | {p['lo']['hi'].mean():+.2f}  {p['lo']['lo'].mean():+.2f}")
    m = smf.mixedlm("lo_B ~ meta + E", df, groups=df["base"]).fit()
    print(m.summary().tables[1])
    for c in ["allA", "suffix_8", "disp_8"]:
        D = df[df.cond == c]
        mm = smf.ols("lo_B ~ meta + E", D).fit()
        print(c, "E coef", round(mm.params["E"], 3), "+-", round(mm.bse["E"], 3), " meta coef", round(mm.params["meta"], 3))


if __name__ == "__main__":
    main()
