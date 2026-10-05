"""E24b analysis: tag binding net of tag-novelty, vs a tag-conditioning oracle.
usage: analyze_ctxmark2.py "RESULT_GLOB" """
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa

ROOT = Path(__file__).resolve().parents[1]
lg = lambda p: np.log(np.clip(p, 1e-9, 1 - 1e-9) / (1 - np.clip(p, 1e-9, 1 - 1e-9)))


def main():
    meta = {}
    for l in open(ROOT / "data/ctxmark2/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = (r["cond"], r["qmark"], r["base_id"], lg(r["oracle"]["ctx_meta_pB"]))
    recs = []
    for f in [g for a in sys.argv[1:] for g in glob.glob(a)]:
        for l in open(f):
            s = json.loads(l)
            if s["uid"] in meta:
                c, q, b, o = meta[s["uid"]]; lp = np.array(s["lp"])
                task, scheme = c.split(":")[0].rsplit("_", 1)
                recs.append(dict(task=task, scheme=scheme, pat=c.split(":")[1], q=q, base=b, pB=lp[1] - lp[0], orc=o))
    D = pd.DataFrame(recs).drop_duplicates(["task", "scheme", "pat", "q", "base"])
    for task, X in D.groupby("task"):
        print(f"\n=== {task}  bases {X.base.nunique()}")
        for pn in ("allA", "suffix_4", "disp_4", "suffix_8", "prefix_8"):
            out = []
            for col in ("pB", "orc"):
                v = X[X.pat == pn].pivot_table(index="base", columns=["scheme", "q"], values=col)
                bt = v[("annot", "B")] - v[("annot", "A")]; bs = v[("annotshuf", "B")] - v[("annotshuf", "A")]
                out.append((bt, bs, bt - bs))
            (bt, bs, net), (obt, obs, onet) = out
            print(f"  {pn:9s} LM: tagged {bt.mean():+.2f} shuffled {bs.mean():+.2f} net binding {fmt(*boot_ci(net.dropna()))}"
                  f"   | ctx-oracle net {onet.mean():+.2f}")


if __name__ == "__main__":
    main()
