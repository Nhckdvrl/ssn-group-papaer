"""E28 analysis. usage: analyze_imbal.py "RESULT_GLOB"
For each query role (maj / min): time-structure indices of logit P(B-mapping answer).
bias  = mean over the two queries of logit P(new-majority label)   (query-independent component)
cond  = (maj + min)/2 of logit P(B-mapping answer)  (moves both queries toward the B mapping)
bias  = (maj - min)/2 equivalently
Note: for the maj query the B answer IS the new-majority label; for the min query it is the new-minority label.
"""
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa

ROOT = Path(__file__).resolve().parents[1]
lg = lambda p: np.log(np.clip(p, 1e-9, 1 - 1e-9) / (1 - np.clip(p, 1e-9, 1 - 1e-9)))
CMP = (("cluster s4-d4", "suffix_4", "disp_4"), ("noise", "noise_2__suffix_3", "suffix_3"), ("s8-p8", "suffix_8", "prefix_8"),
       ("recency 16-1", "single_16", "single_1"))


def main():
    meta = {}
    for l in open(ROOT / "data" / __import__("os").environ.get("DATA", "imbal") / "rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = (r["cond"], r["qrole"], r["base_id"], lg(r["oracle"]["meta_pB"]))
    recs = []
    for f in [g for a in sys.argv[1:] for g in glob.glob(a)]:
        for l in open(f):
            s = json.loads(l)
            if s["uid"] in meta:
                c, q, b, o = meta[s["uid"]]; lp = np.array(s["lp"])
                recs.append(dict(task=c.split(":")[0], pat=c.split(":")[1], q=q, base=b, pB=lp[1] - lp[0], orc=o))
    D = pd.DataFrame(recs).drop_duplicates(["task", "pat", "q", "base"])
    for task, X in D.groupby("task"):
        print(f"\n=== {task}  bases {X.base.nunique()}")
        print(X.pivot_table(index="pat", columns="q", values=["pB", "orc"]).round(2).to_string())
        v = {q: X[X.q == q].pivot_table(index="base", columns="pat", values="pB") for q in ("maj", "min")}
        o = {q: X[X.q == q].groupby("pat").orc.mean() for q in ("maj", "min")}
        comp = {"maj": v["maj"], "min": v["min"], "bias": (v["maj"] - v["min"]) / 2, "cond": (v["maj"] + v["min"]) / 2}
        ocomp = {"maj": o["maj"], "min": o["min"], "bias": (o["maj"] - o["min"]) / 2, "cond": (o["maj"] + o["min"]) / 2}
        for k in ("maj", "min", "bias", "cond"):
            s = "  ".join(f"{n} {fmt(*boot_ci((comp[k][a] - comp[k][b]).dropna()))} (orc {ocomp[k][a] - ocomp[k][b]:+.2f})" for n, a, b in CMP)
            print(f"  {k:5s} {s}")


if __name__ == "__main__":
    main()
