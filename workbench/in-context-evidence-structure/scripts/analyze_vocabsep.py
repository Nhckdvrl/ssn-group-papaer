"""E31 analysis. usage: analyze_vocabsep.py "RESULT_GLOB" ..."""
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa

ROOT = Path(__file__).resolve().parents[1]


def main():
    meta = {}
    for l in open(ROOT / "data" / __import__("os").environ.get("DATA", "vocabsep") / "rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    recs = []
    for f in [g for a in sys.argv[1:] for g in glob.glob(a)]:
        for l in open(f):
            s = json.loads(l)
            if s["uid"] in meta:
                r = meta[s["uid"]]; lp = np.array(s["lp"]); qA = r["qA"]
                task, vn = (r["cond"].split(":")[0].split("_", 2)[0] + "_" + r["cond"].split(":")[0].split("_", 2)[1], r["cond"].split(":")[0].split("_", 2)[2]) if r["cond"].startswith("mag_nat") else r["cond"].split(":")[0].split("_", 1)
                recs.append(dict(task=task, vocab=vn, mp=r["cond"].split(":")[1], base=r["base_id"], ann=r["qann"], qc=r["qclass"],
                                 pB=lp[1 - qA] - lp[qA], mass=np.exp(lp).sum()))
    D = pd.DataFrame(recs).drop_duplicates(["task", "vocab", "mp", "base", "ann", "qc"])
    for task, X in D.groupby("task"):
        print(f"\n=== {task}  bases {X.base.nunique()}")
        for vn in [v for v in ("same", "case", "syn", "nonce") if v in set(X.vocab)] or sorted(set(X.vocab), key=lambda v: list(X.vocab.unique()).index(v)):
            Y = X[X.vocab == vn]
            v = Y.pivot_table(index=["base", "qc"], columns=["mp", "ann"], values="pB")
            sam = v[("inter", 1)] - v[("A", 1)]; alex = v[("inter", 0)] - v[("A", 0)]
            m = Y[Y.ann == 1].mass.mean()
            print(f"  {vn:6s} Sam shift {fmt(*boot_ci(sam.dropna()))}  Alex spill {fmt(*boot_ci(alex.dropna()))}  spill ratio {alex.mean() / sam.mean():.2f}"
                  f"  binding {fmt(*boot_ci((sam - alex).dropna()))}  [Sam-query cand mass {m:.2f}; P(B|Sam,A) {v[('A', 1)].mean():+.2f}]")


if __name__ == "__main__":
    main()
