"""Analyse a structure grid run.  usage: analyze_struct.py DATA_DIR RESULT_GLOB [--json OUT]

All LM readouts are paired within base: d(cond) = lo_B(cond) - lo_B(allA).
Oracle readouts are the same transform of logit(P_B) for set / meta oracles.
"""
import argparse, glob, json, re, sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa: E402


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def load(data_dir, res_glob):
    rows = {}
    for l in open(Path(data_dir) / "rows.jsonl"):
        r = json.loads(l)
        rows[r["uid"]] = r
    recs = []
    for f in glob.glob(res_glob):
        for l in open(f):
            s = json.loads(l)
            r = rows[s["uid"]]
            o = r["oracle"]
            lo1 = s["lp"][1] - s["lp"][0]
            qb = r["query_label_B"]
            recs.append({"uid": s["uid"], "cond": r["cond"], "base": r["base_id"],
                         "lo_B": lo1 if qb == 1 else -lo1,
                         "mass": float(np.exp(s["lp"]).sum()),
                         "set": logit(o["set_pB"]), "meta": logit(o["meta_pB"]), "seq": logit(o["sequence_pB"]),
                         "log_bf": o["log_bf_change_vs_stable"], "p_vol": o["meta_p_volatile"],
                         "eps_hat": o["meta_post_eps_mean"]})
    df = pd.DataFrame(recs)
    base_ref = df[df.cond == "allA"].set_index("base")
    for c in ("lo_B", "set", "meta", "seq"):
        df["d_" + c] = df[c] - df["base"].map(base_ref[c])
    df["allA_correct"] = df["base"].map(base_ref["lo_B"] < 0)
    return df


def cond_table(df, conds, col="d_lo_B"):
    out = {}
    for c in conds:
        x = df[df.cond == c]
        if len(x) == 0:
            continue
        out[c] = {"lm": boot_ci(x[col]), "set": float(x.d_set.mean()), "meta": float(x.d_meta.mean()),
                  "n": int(len(x))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("res"); ap.add_argument("--json")
    ap.add_argument("--only_correct", action="store_true")
    a = ap.parse_args()
    df = load(a.data, a.res)
    if a.only_correct:
        df = df[df.allA_correct]
    T = max(int(m.group(1)) for m in (re.match(r"single_(\d+)", c) for c in df.cond.unique()) if m)
    R = {"n_rows": int(len(df)), "n_bases": int(df.base.nunique()), "mass": float(df.mass.mean())}
    A = df[df.cond == "allA"]
    R["allA"] = {"lo_B": boot_ci(A.lo_B), "acc_A": float((A.lo_B < 0).mean())}
    print(f"rows {len(df)} bases {df.base.nunique()} mass {df.mass.mean():.3f}  allA lo_B {fmt(*R['allA']['lo_B'])} acc {R['allA']['acc_A']:.3f}")

    # 1. position kernel
    w = {}
    print("\n[kernel] single-flip effect d_lo_B by position (LM | set | meta)")
    for t in range(1, T + 1):
        x = df[df.cond == f"single_{t}"]
        w[t] = float(x.d_lo_B.mean())
        m, lo, hi = boot_ci(x.d_lo_B)
        print(f"  t={t:2d}  {fmt(m,lo,hi)}   set {x.d_set.mean():+.2f}  meta {x.d_meta.mean():+.2f}")
    R["kernel"] = w
    # per-base kernel for additive predictions
    single = df[df.cond.str.match(r"single_\d+$")].copy()
    single["t"] = single.cond.str.extract(r"(\d+)").astype(int)
    Wb = single.pivot(index="base", columns="t", values="d_lo_B")

    conds = json.load(open(Path(a.data) / "conditions.json"))

    def additive_pred(cname):
        pos = [i + 1 for i, ch in enumerate(conds[cname]) if ch == "B"]
        return Wb[pos].sum(axis=1) if pos else pd.Series(0.0, index=Wb.index)

    # 2. pairs: interaction = d(pair) - (w_i + w_j)
    print("\n[pairs] observed vs additive (LM), interaction with CI")
    R["pairs"] = {}
    for c in [c for c in conds if c.startswith("pair_")]:
        x = df[df.cond == c].set_index("base")
        inter = x.d_lo_B - additive_pred(c).reindex(x.index)
        R["pairs"][c] = {"obs": float(x.d_lo_B.mean()), "add": float(additive_pred(c).mean()),
                         "inter": boot_ci(inter.dropna())}
        print(f"  {c:12s} obs {x.d_lo_B.mean():+.2f}  additive {additive_pred(c).mean():+.2f}  interaction {fmt(*R['pairs'][c]['inter'])}"
              f"   | meta {x.d_meta.mean():+.2f}")

    # 3. families
    fam = [c for c in conds if c.startswith(("suffix_", "disp_", "block_", "late_disp"))]
    print("\n[families] LM d_lo_B | additive-from-kernel | set | meta")
    R["families"] = {}
    for c in fam:
        x = df[df.cond == c].set_index("base")
        ad = additive_pred(c).reindex(x.index)
        R["families"][c] = {"lm": boot_ci(x.d_lo_B), "add": float(ad.mean()),
                            "excess": boot_ci((x.d_lo_B - ad).dropna()),
                            "set": float(x.d_set.mean()), "meta": float(x.d_meta.mean())}
        print(f"  {c:22s} {fmt(*R['families'][c]['lm'])}  add {ad.mean():+.2f}  excess {fmt(*R['families'][c]['excess'])}"
              f"  set {x.d_set.mean():+.2f} meta {x.d_meta.mean():+.2f}")

    # 4. noise x suffix surface (absolute lo_B, not differenced) + reversal tests
    print("\n[noise x suffix] LM mean lo_B   (rows m=prefix noise, cols k=suffix)")
    ks = (0, 2, 3, 4, 5)
    surf_lm = np.full((5, len(ks)), np.nan); surf_meta = surf_lm.copy(); surf_set = surf_lm.copy()
    for m in range(5):
        for j, k in enumerate(ks):
            c = "allA" if (m == 0 and k == 0) else f"noise_{m}__suffix_{k}"
            x = df[df.cond == c]
            surf_lm[m, j] = x.lo_B.mean(); surf_meta[m, j] = x.meta.mean(); surf_set[m, j] = x.set.mean()
    for name, S in (("LM", surf_lm), ("meta", surf_meta), ("set", surf_set)):
        print(f"  {name}")
        for m in range(5):
            print("   m=%d " % m + " ".join(f"{v:+6.2f}" for v in S[m]))
    R["surface"] = {"ks": ks, "lm": surf_lm.tolist(), "meta": surf_meta.tolist(), "set": surf_set.tolist()}
    print("\n[reversal test] effect of adding m prefix-noise items given suffix k (paired, LM)  vs additive prediction")
    R["reversal"] = {}
    for k in (3, 4, 5):
        for m in (1, 2, 3, 4):
            c1 = f"noise_{m}__suffix_{k}"; c0 = f"noise_0__suffix_{k}"
            x1 = df[df.cond == c1].set_index("base"); x0 = df[df.cond == c0].set_index("base")
            d = (x1.lo_B - x0.lo_B).dropna()
            ad = (additive_pred(c1) - additive_pred(c0)).reindex(d.index)
            dm = (x1.meta - x0.meta).mean(); ds = (x1.set - x0.set).mean()
            R["reversal"][c1] = {"lm": boot_ci(d), "add": float(ad.mean()), "meta": float(dm), "set": float(ds)}
            print(f"  k={k} m={m}: LM {fmt(*boot_ci(d))}  additive {ad.mean():+.2f}  meta {dm:+.2f}  set {ds:+.2f}")

    # 5. across-condition fit
    g = df.groupby("cond").agg(lm=("lo_B", "mean"), meta=("meta", "mean"), set=("set", "mean"), seq=("seq", "mean"))
    g["add"] = [float(A.lo_B.mean() + additive_pred(c).mean()) if c in conds else np.nan for c in g.index]
    print("\n[fit across conditions] Pearson r of condition means")
    R["fit"] = {}
    for col in ("meta", "set", "seq", "add"):
        r = float(np.corrcoef(g.lm, g[col])[0, 1]); R["fit"][col] = r
        print(f"  LM vs {col:5s}: r={r:.3f}")
    # perm dispersion
    P = df[df.cond.str.startswith("perm3_")]
    R["perm3_between_cond_sd"] = float(P.groupby("cond").lo_B.mean().std())
    R["perm3_within_base_sd"] = float(P.groupby("base").lo_B.std().mean())
    print(f"\n[perm3] mean within-base SD of lo_B across 8 orders: {R['perm3_within_base_sd']:.2f} (set oracle: 0)")
    if a.json:
        json.dump(R, open(a.json, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
