"""E25 analysis. usage: analyze_mc.py "RESULT_GLOB" """
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa

ROOT = Path(__file__).resolve().parents[1]


def lg(p):
    p = np.clip(p, 1e-9, 1 - 1e-9); return np.log(p / (1 - p))


def main():
    meta = {}
    for l in open(ROOT / "data/mc/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = (r["cond"], r["base_id"], r["query_label_A"], r["query_label_B"], lg(r["oracle"]["meta_pB"]), r["A_is_identity"])
    recs = []
    for f in [g for a in sys.argv[1:] for g in glob.glob(a)]:
        for l in open(f):
            s = json.loads(l)
            if s["uid"] not in meta:
                continue
            c, b, a, bb, mo, ident = meta[s["uid"]]
            lp = np.array(s["lp"]); pred = int(np.argmax(lp))
            recs.append(dict(task=c.split(":")[0], pat=c.split(":")[1], base=b, pB=lp[bb] - lp[a], meta=mo, ident=ident,
                             predA=pred == a, predB=pred == bb))
    D = pd.DataFrame(recs).drop_duplicates(["task", "pat", "base"])
    for tk in sorted(D.task.unique()):
        X = D[D.task == tk]
        g = X.groupby("pat")
        print(f"\n=== {tk} bases {X.base.nunique()}  acc(allA→A) {g.predA.mean()['allA']:.2f}  acc(allB→B) {g.predB.mean()['allB']:.2f}"
              f"  [A=identity: {X[(X.pat=='allA') & X.ident].predA.mean():.2f}, A=derangement: {X[(X.pat=='allA') & ~X.ident].predA.mean():.2f}]")
        v = X.pivot_table(index="base", columns="pat", values="pB"); m = X.groupby("pat").meta.mean()
        for name, a, b in (("cluster s4-d4", "suffix_4", "disp_4"), ("noise", "noise_2__suffix_3", "suffix_3"),
                           ("s8-p8", "suffix_8", "prefix_8"), ("recency 16-1", "single_16", "single_1"), ("stale bs4-allA", "block_start4", "allA")):
            print(f"  {name:15s} LM {fmt(*boot_ci(v[a] - v[b]))}   oracle {m[a] - m[b]:+.2f}")


if __name__ == "__main__":
    main()
