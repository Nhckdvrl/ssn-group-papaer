"""E22 analysis. usage: analyze_marked.py "RESULT_GLOB" """
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
    for l in open(ROOT / "data/marked/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = (r["cond"], r["base_id"], lg(r["oracle"]["meta_pB"]))
    recs = []
    for f in glob.glob(sys.argv[1]):
        for l in open(f):
            s = json.loads(l)
            if s["uid"] not in meta:
                continue
            c, b, mo = meta[s["uid"]]
            p = np.exp(np.array(s["lp"])); tot = p.sum()
            lowA, lowB, upA, upB = p / tot
            recs.append(dict(fmt=c.split(":")[0], pat=c.split(":")[1], base=b, meta=mo, mass=tot,
                             upper=lg(upA + upB), bmap=lg(lowB + upB), bmap_given_upper=lg(upB / (upA + upB)),
                             bmap_given_lower=lg(lowB / (lowA + lowB))))
    D = pd.DataFrame(recs).drop_duplicates(["fmt", "pat", "base"])
    for fm in sorted(D.fmt.unique()):
        X = D[D.fmt == fm]
        print(f"\n=== {fm}  bases {X.base.nunique()}  mass {X.mass.mean():.3f}")
        g = X.groupby("pat")[["upper", "bmap", "bmap_given_upper", "bmap_given_lower", "meta"]].mean()
        print(g.round(2).to_string())
        pv = {k: X.pivot_table(index="base", columns="pat", values=k) for k in ("upper", "bmap", "bmap_given_upper")}
        for k, v in pv.items():
            cl = v.suffix_4 - v.disp_4; nz = v.noise_2__suffix_3 - v.suffix_3; sp = v.suffix_8 - v.prefix_8
            print(f"  {k:17s} suffix4-disp4 {fmt(*boot_ci(cl))}  noise2 {fmt(*boot_ci(nz))}  suffix8-prefix8 {fmt(*boot_ci(sp))}")
        m = X.groupby("pat").meta.mean()
        print(f"  meta oracle: suffix4-disp4 {m.suffix_4 - m.disp_4:+.2f} noise2 {m.noise_2__suffix_3 - m.suffix_3:+.2f} suffix8-prefix8 {m.suffix_8 - m.prefix_8:+.2f}")


if __name__ == "__main__":
    main()
