"""E24 analysis. usage: analyze_ctxmark.py "RESULT_GLOB" """
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
    for dn in ("ctxmark", "ctxmark_s3"):
        if not (ROOT / "data" / dn / "rows.jsonl").exists():
            continue
        for l in open(ROOT / "data" / dn / "rows.jsonl"):
            r = json.loads(l); meta[r["uid"]] = (r["cond"], r["qmark"], r["base_id"], lg(r["oracle"]["meta_pB"]))
    recs = []
    for f in [g for a in sys.argv[1:] for g in glob.glob(a)]:
        for l in open(f):
            s = json.loads(l)
            if s["uid"] not in meta:
                continue
            c, qm, b, mo = meta[s["uid"]]
            p = np.exp(np.array(s["lp"]))
            recs.append(dict(task=c.split(":")[0], pat=c.split(":")[1], q=qm, base=b, meta=mo, mass=p.sum(), pB=lg(p[1] / p.sum())))
    D = pd.DataFrame(recs).drop_duplicates(["task", "pat", "q", "base"])
    for tk in sorted(D.task.unique()):
        X = D[D.task == tk]
        print(f"\n=== {tk}  bases {X.base.nunique()}  mass {X.mass.mean():.3f}")
        print(X.pivot_table(index="pat", columns="q", values="pB").round(2).to_string())
        pv = {q: X[X.q == q].pivot_table(index="base", columns="pat", values="pB") for q in X.q.unique()}
        if "A" in pv and "B" in pv:
            for pt in ("allA", "suffix_8", "prefix_8", "suffix_4", "block_start4"):
                d = (pv["B"][pt] - pv["A"][pt]).dropna()
                print(f"  bind[{pt:12s}] P(B|qB)-P(B|qA) {fmt(*boot_ci(d))}")
        for q, v in pv.items():
            print(f"  q={q:4s} suffix4-disp4 {fmt(*boot_ci(v.suffix_4 - v.disp_4))}  noise2 {fmt(*boot_ci(v.noise_2__suffix_3 - v.suffix_3)) if "suffix_3" in v else "n/a"}"
                  f"  suffix8-prefix8 {fmt(*boot_ci(v.suffix_8 - v.prefix_8))}")
        m = X.groupby("pat").meta.mean()
        print(f"  meta oracle (time only): suffix4-disp4 {m.suffix_4 - m.disp_4:+.2f}  suffix8-prefix8 {m.suffix_8 - m.prefix_8:+.2f}"
              + (f"  noise2 {m.noise_2__suffix_3 - m.suffix_3:+.2f}" if "suffix_3" in m else ""))


if __name__ == "__main__":
    main()
