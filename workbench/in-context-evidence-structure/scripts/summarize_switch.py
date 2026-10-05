"""Cross-model surface-vs-latent signatures on switch_core / switch_pilot runs.
usage: summarize_switch.py RESULT_DIR [extra RESULT_DIR ...] [--out CSV]
For each model x format (const / irr5 / rule5):
  cluster  = LM[suffix_4 - disp_4]              (oracle meta value printed alongside)
  CSI      = cluster / meta[suffix_4 - disp_4]   (1 = normative clustering sensitivity, 0 = set)
  noise    = LM[noise_2__suffix_3 - suffix_3]    (oracle meta < 0)
  NDI      = -noise / |meta noise|               (+ = normative direction, - = wrong direction)
  recency  = LM[single_16 - single_1]
"""
import argparse, glob, json, os, re, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci  # noqa

ROOT = Path(__file__).resolve().parents[1]


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--out")
    a = ap.parse_args()
    meta = {}
    for l in open(ROOT / "data/switch_pilot_T16/rows.jsonl"):
        r = json.loads(l)
        meta[r["uid"]] = (r["cond"], r["base_id"], r["query_label_B"], logit(r["oracle"]["meta_pB"]))
    out = []
    for d in a.dirs:
        models = sorted({re.sub(r"\.s\d+\.jsonl$", "", os.path.basename(f)) for f in glob.glob(d + "/*.s*.jsonl")})
        for m in models:
            recs = []
            for f in glob.glob(f"{d}/{m}.s*.jsonl"):
                for l in open(f):
                    s = json.loads(l)
                    if s["uid"] not in meta:
                        continue
                    c, b, qb, mo = meta[s["uid"]]
                    lo1 = s["lp"][1] - s["lp"][0]
                    fm, p = c.split(":", 1)
                    recs.append((fm, p, b, lo1 if qb == 1 else -lo1, mo))
            df = pd.DataFrame(recs, columns=["fmt", "pat", "base", "lo", "meta"]).drop_duplicates(["fmt", "pat", "base"])
            for fm in ("const", "irr5", "rule5"):
                D = df[df.fmt == fm]
                if D.empty or D.pat.nunique() < 10:
                    continue
                pv = D.pivot_table(index="base", columns="pat", values="lo")
                pm = D.groupby("pat").meta.mean()
                need = ["suffix_4", "disp_4", "noise_2__suffix_3", "suffix_3", "single_16", "single_1", "allA"]
                if any(n not in pv for n in need):
                    continue
                cl = pv.suffix_4 - pv.disp_4; nz = pv.noise_2__suffix_3 - pv.suffix_3; rc = pv.single_16 - pv.single_1
                mcl = pm.suffix_4 - pm.disp_4; mnz = pm.noise_2__suffix_3 - pm.suffix_3
                out.append(dict(model=m, fmt=fm, n=len(pv), accA=float((pv.allA < 0).mean()),
                                cluster=cl.mean(), cluster_lo=boot_ci(cl)[1], cluster_hi=boot_ci(cl)[2], meta_cluster=mcl,
                                CSI=cl.mean() / mcl, noise=nz.mean(), noise_lo=boot_ci(nz)[1], noise_hi=boot_ci(nz)[2],
                                meta_noise=mnz, NDI=-nz.mean() / abs(mnz), recency=rc.mean(), scale=float(pv.allA.abs().mean()),
                                CSIn=(cl.mean() / abs(pv.allA.mean())) / (mcl / abs(pm.allA)),
                                NDIn=(-nz.mean() / abs(pv.allA.mean())) / (abs(mnz) / abs(pm.allA))))
    D = pd.DataFrame(out)
    pd.set_option("display.width", 250)
    print(D.round(2).to_string(index=False))
    if a.out:
        D.to_csv(a.out, index=False)


if __name__ == "__main__":
    main()
