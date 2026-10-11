"""Non-additivity test, robust to any (per-base) positional kernel.

For each base: w(t) = lo(single_t) - lo(allA) at t in {1,4,8,12,16}, linearly interpolated to 1..16.
Additive prediction for a pattern P: add(P) = sum_{t in B(P)} w(t).  Observed d(P) = lo(P) - lo(allA).
  excess_cluster = [d(suffix_4)-add(suffix_4)] - [d(disp_4)-add(disp_4)]       (structure inference: > 0)
  excess_noise   = [d(noise_2__suffix_3)-add(.)] - [d(suffix_3)-add(suffix_3)]  (structure inference: < 0)
Both are ~0 for any additive kernel (set or recency).  Reported in units of |lo(allA)| (scale-free) too.
usage: analyze_additivity.py DATA "RESULT_DIR_GLOB_OR_DIRS..." [--formats a,b] [--out CSV]
"""
import argparse, glob, json, os, re, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("data"); ap.add_argument("dirs", nargs="+")
    ap.add_argument("--formats"); ap.add_argument("--out")
    a = ap.parse_args()
    meta = {}
    for l in open(ROOT / "data" / a.data / "rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = (r["cond"], r["base_id"], r["query_label_B"], r["pattern"])
    out = []
    for d in a.dirs:
        models = sorted({re.sub(r"\.s\d+\.jsonl$", "", os.path.basename(f)) for f in glob.glob(d + "/*.s*.jsonl")})
        for m in models:
            recs = {}
            for f in glob.glob(f"{d}/{m}.s*.jsonl"):
                for l in open(f):
                    s = json.loads(l)
                    if s["uid"] not in meta:
                        continue
                    c, b, qb, pat = meta[s["uid"]]
                    lo1 = s["lp"][1] - s["lp"][0]
                    fm, p = c.split(":", 1)
                    recs[(fm, b, p)] = (lo1 if qb == 1 else -lo1, pat)
            fmts = sorted({k[0] for k in recs}) if not a.formats else a.formats.split(",")
            for fm in fmts:
                bases = sorted({k[1] for k in recs if k[0] == fm})
                ec, en, scale = [], [], []
                for b in bases:
                    g = lambda p: recs.get((fm, b, p), (None, None))
                    if any(g(p)[0] is None for p in ("allA", "single_1", "single_4", "single_8", "single_12", "single_16",
                                                     "suffix_4", "disp_4", "suffix_3", "noise_2__suffix_3")):
                        continue
                    base = g("allA")[0]
                    pts = [1, 4, 8, 12, 16]; ws = [g(f"single_{t}")[0] - base for t in pts]
                    w = np.interp(np.arange(1, T + 1), pts, ws)
                    def res(p):
                        lo, pat = g(p)
                        add = sum(w[i] for i, ch in enumerate(pat) if ch == "B")
                        return (lo - base) - add
                    ec.append(res("suffix_4") - res("disp_4")); en.append(res("noise_2__suffix_3") - res("suffix_3"))
                    scale.append(abs(base))
                if len(ec) < 20:
                    continue
                ec, en, sc = np.array(ec), np.array(en), np.mean(scale)
                out.append(dict(model=m, fmt=fm, n=len(ec), excess_cluster=ec.mean(), ec_lo=boot_ci(ec)[1], ec_hi=boot_ci(ec)[2],
                                excess_noise=en.mean(), en_lo=boot_ci(en)[1], en_hi=boot_ci(en)[2],
                                ecn=ec.mean() / sc, enn=en.mean() / sc))
    D = pd.DataFrame(out)
    pd.set_option("display.width", 220)
    print(D.round(2).to_string(index=False))
    if a.out:
        D.to_csv(a.out, index=False)


if __name__ == "__main__":
    main()
