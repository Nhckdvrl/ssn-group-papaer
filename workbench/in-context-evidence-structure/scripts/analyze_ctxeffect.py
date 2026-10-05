"""E30 analysis. usage: analyze_ctxeffect.py "RESULT_GLOB" ...
interaction binding = [P(B-map|Sam) - P(B-map|Alex)]_inter - [same]_same      (logit of the B-mapping answer)
main effect         = [logit P(L|Sam) - logit P(L|Alex)]_main - [same]_same
Normative references (annotator-conditioned counting learner, Beta(1,1) per annotator x class):
  interaction: Sam's 4 demos/class all reversed -> P(B|Sam)=5/6, Alex 1/6  -> binding = 2*log(5) = +3.22
  main: Sam gives L on 3/4 demos per class (incl. the A-correct ones) -> handled empirically per class
"""
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa

ROOT = Path(__file__).resolve().parents[1]


def main():
    meta = {}
    for l in open(ROOT / "data/ctxeffect/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    recs = []
    for f in [g for a in sys.argv[1:] for g in glob.glob(a)]:
        for l in open(f):
            s = json.loads(l)
            if s["uid"] not in meta:
                continue
            r = meta[s["uid"]]; lp = np.array(s["lp"])
            qB = 1 - r["qA"]
            recs.append(dict(task=r["cond"].split(":")[0], cond=r["cond"].split(":")[1], base=r["base_id"], ann=r["qann"], qc=r["qclass"],
                             pB=lp[qB] - lp[r["qA"]], pL=lp[r["L"]] - lp[1 - r["L"]]))
    D = pd.DataFrame(recs).drop_duplicates(["task", "cond", "base", "ann", "qc"])
    for task, X in D.groupby("task"):
        print(f"\n=== {task}  bases {X.base.nunique()}")
        piv = {k: X.pivot_table(index=["base", "qc"], columns=["cond", "ann"], values=k) for k in ("pB", "pL")}
        v = piv["pB"]
        inter = (v[("inter", 1)] - v[("inter", 0)]) - (v[("same", 1)] - v[("same", 0)])
        v = piv["pL"]
        main = (v[("main", 1)] - v[("main", 0)]) - (v[("same", 1)] - v[("same", 0)])
        # also: how much does each manipulation move the ALEX queries (spill-over, should be ~0 for a conditioning learner)
        spill_inter = piv["pB"][("inter", 0)] - piv["pB"][("same", 0)]
        spill_main = piv["pL"][("main", 0)] - piv["pL"][("same", 0)]
        sam_inter = piv["pB"][("inter", 1)] - piv["pB"][("same", 1)]
        sam_main = piv["pL"][("main", 1)] - piv["pL"][("same", 1)]
        print(f"  interaction binding {fmt(*boot_ci(inter.dropna()))}   [Sam shift {sam_inter.mean():+.2f}, Alex spill-over {spill_inter.mean():+.2f}]")
        print(f"  main effect         {fmt(*boot_ci(main.dropna()))}   [Sam shift {sam_main.mean():+.2f}, Alex spill-over {spill_main.mean():+.2f}]")


if __name__ == "__main__":
    main()
