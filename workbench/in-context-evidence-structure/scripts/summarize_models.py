"""One-line structural signatures per model for a structure-grid run.
usage: summarize_models.py DATA_DIR RESULT_DIR [--out CSV]"""
import argparse, glob, json, os, re, sys
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_struct import load  # noqa: E402
from analyze_common import boot_ci  # noqa: E402


def sim_features(data_dir):
    feats = {}
    for l in open(Path(data_dir) / "rows.jsonl"):
        r = json.loads(l)
        if not r["cond"].startswith("single_"):
            continue
        b = r["base"]; X = np.array(b["X"]); xq = np.array(b["xq"]); a = b["rule_attr"]
        t = int(r["cond"].split("_")[1]) - 1; x = X[t]
        feats[r["uid"]] = (int(x[a] == xq[a]), int(sum(x[j] == xq[j] for j in range(len(xq)) if j != a)), t + 1)
    return feats


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("data"); ap.add_argument("resdir"); ap.add_argument("--out")
    a = ap.parse_args()
    feats = sim_features(a.data)
    models = sorted({re.sub(r"\.s\d+\.jsonl$", "", os.path.basename(f)) for f in glob.glob(a.resdir + "/*.s*.jsonl")})
    n_rows = sum(1 for _ in open(Path(a.data) / "rows.jsonl"))
    out = []
    for m in models:
        files = glob.glob(f"{a.resdir}/{m}.s*.jsonl")
        n = sum(1 for f in files for _ in open(f))
        if n < n_rows:
            print(f"{m}: incomplete {n}/{n_rows}"); continue
        df = load(a.data, f"{a.resdir}/{m}.s*.jsonl")
        df = df.drop_duplicates("uid")
        g = lambda c: df[df.cond == c].set_index("base")
        A = g("allA")
        k = {t: g(f"single_{t}").d_lo_B.mean() for t in range(1, 17)}
        early = np.mean([k[t] for t in range(1, 5)]); late = np.mean([k[t] for t in range(13, 17)])
        pairs = [c for c in df.cond.unique() if c.startswith("pair_")]
        # interaction of pairs vs singles
        inter = []
        for c in pairs:
            i, j = map(int, c.split("_")[1:])
            x = g(c).d_lo_B - g(f"single_{i}").d_lo_B - g(f"single_{j}").d_lo_B
            inter.append(x.mean())
        s4d4 = (g("suffix_4").lo_B - g("disp_4").lo_B).dropna()
        rev = (g("noise_2__suffix_4").lo_B - g("noise_0__suffix_4").lo_B).dropna()
        revm = (g("noise_2__suffix_4").meta - g("noise_0__suffix_4").meta).mean()
        cm = df.groupby("cond").agg(lm=("lo_B", "mean"), meta=("meta", "mean"), set=("set", "mean"))
        # similarity regression on single flips
        S = df[df.cond.str.startswith("single_")].copy()
        S[["same", "dsim", "t"]] = [feats[u] for u in S.uid]
        fit = smf.ols("d_lo_B ~ same + dsim + t + same:t", S).fit()
        P = df[df.cond.str.startswith("perm3_")]
        row = dict(model=m, mass=df.mass.mean(), accA=(A.lo_B < 0).mean(), loA=A.lo_B.mean(),
                   k_early=early, k_late=late, pair_inter=np.mean(inter),
                   suf4_minus_disp4=s4d4.mean(), suf4_minus_disp4_lo=boot_ci(s4d4)[1], suf4_minus_disp4_hi=boot_ci(s4d4)[2],
                   noise2_effect=rev.mean(), noise2_lo=boot_ci(rev)[1], noise2_hi=boot_ci(rev)[2], noise2_meta=revm,
                   r_set=np.corrcoef(cm.lm, cm.set)[0, 1], r_meta=np.corrcoef(cm.lm, cm.meta)[0, 1],
                   b_same=fit.params["same"], b_dsim=fit.params["dsim"], b_t=fit.params["t"], b_same_t=fit.params["same:t"],
                   perm_sd=P.groupby("base").lo_B.std().mean(),
                   suffix8=g("suffix_8").d_lo_B.mean())
        out.append(row)
    D = pd.DataFrame(out)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print(D.round(2).to_string(index=False))
    if a.out:
        D.to_csv(a.out, index=False)


if __name__ == "__main__":
    main()
