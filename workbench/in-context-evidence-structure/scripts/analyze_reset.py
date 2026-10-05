"""E26 analysis: deletion-influence 'support' profiles and reset index.
usage: analyze_reset.py "RESULT_GLOB" [--profile]

support_t = (logit_full - logit_without_t) * (+1 if demo t is B else -1)
  = how much demo t pushes the query toward its own regime's answer.
Channels: map (P(new mapping)), upper (P(uppercase), marked only), oracle (exact meta, mapping).
R = mean support of positions 0-7 / mean support of positions 8-15.
  suffix_8: positions 0-7 are the pre-change A demos -> normative learner discounts them (R << 1).
  disp_8:   same positions, alternating A/B, no change point -> pure positional kernel.
reset ratio = R_suffix / R_disp  (1 = no extra discount from the change point).
"""
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
    for l in open(ROOT / "data/reset/rows.jsonl"):
        r = json.loads(l)
        meta[r["uid"]] = (r["cond"], r["del"], r["base_id"], r["pattern"], r["same_class"], lg(r["oracle"]["meta_pB"]))
    recs = []
    for f in [g for a in sys.argv[1:] if not a.startswith("--") for g in glob.glob(a)]:
        for l in open(f):
            s = json.loads(l)
            if s["uid"] not in meta:
                continue
            c, d, b, pt, sc, mo = meta[s["uid"]]
            p = np.exp(np.array(s["lp"])); p = p / p.sum()
            if len(p) == 4:
                mp = lg(p[1] + p[3]); up = lg(p[2] + p[3])
            else:
                mp = lg(p[1]); up = np.nan
            task, pres = c.split(":")[0].rsplit("_", 1); pn = c.split(":")[1]
            recs.append(dict(task=task, pres=pres, pat=pn, base=b, d=-1 if d is None else d, map=mp, upper=up, oracle=mo))
    D = pd.DataFrame(recs).drop_duplicates(["task", "pres", "pat", "base", "d"])
    pat_of = {}; sc_of = {}
    for u, (c, d, b, pt, sc, mo) in meta.items():
        pat_of[(c.split(":")[1], b)] = pt; sc_of[b] = sc
    full = D[D.d < 0].set_index(["task", "pres", "pat", "base"])
    X = D[D.d >= 0].join(full[["map", "upper", "oracle"]], on=["task", "pres", "pat", "base"], rsuffix="_full")
    sign = np.array([1 if pat_of[(p, b)][d] == "B" else -1 for p, b, d in zip(X.pat, X.base, X.d)])
    for ch in ("map", "upper", "oracle"):
        X[f"sup_{ch}"] = (X[f"{ch}_full"] - X[ch]) * sign
    X["same"] = [sc_of[b][d] for b, d in zip(X.base, X.d)]
    X["early"] = X.d < 8
    for (task, pres), G in X.groupby(["task", "pres"]):
        print(f"\n=== {task} / {pres}  bases {G.base.nunique()}")
        for ch in ("map", "upper", "oracle"):
            if G[f"sup_{ch}"].isna().all():
                continue
            out = []
            for pn in ("suffix_8", "disp_8"):
                H = G[G.pat == pn]
                per = H.groupby(["base", "early"])[f"sup_{ch}"].mean().unstack()
                out.append((pn, per[True].mean(), per[False].mean(), per[True].mean() / per[False].mean()))
            rs = out[0][3] / out[1][3]
            # bootstrap the reset ratio over bases
            Hs = G[G.pat == "suffix_8"].groupby(["base", "early"])[f"sup_{ch}"].mean().unstack()
            Hd = G[G.pat == "disp_8"].groupby(["base", "early"])[f"sup_{ch}"].mean().unstack()
            bs = Hs.index.intersection(Hd.index); rng = np.random.default_rng(0); B = []
            for _ in range(2000):
                k = rng.choice(len(bs), len(bs)); i = bs[k]
                B.append((Hs.loc[i, True].mean() / Hs.loc[i, False].mean()) / (Hd.loc[i, True].mean() / Hd.loc[i, False].mean()))
            lo, hi = np.percentile(B, [2.5, 97.5])
            print(f"  {ch:6s} suffix_8 early {out[0][1]:+.3f} late {out[0][2]:+.3f} R {out[0][3]:.2f} | disp_8 early {out[1][1]:+.3f} late {out[1][2]:+.3f} R {out[1][3]:.2f}"
                  f" | reset ratio {rs:.2f} [{lo:.2f},{hi:.2f}]")
            if "--split" in sys.argv:
                for same in (1, 0):
                    H = G[(G.pat == "suffix_8") & (G.same == same)].groupby("early")[f"sup_{ch}"].mean()
                    print(f"         suffix_8 {'same' if same else 'other'}-class demos: early {H[True]:+.3f} late {H[False]:+.3f}")
            if "--profile" in sys.argv:
                prof = G[G.pat == "suffix_8"].groupby("d")[f"sup_{ch}"].mean().round(2).tolist()
                print(f"         profile suffix_8: {prof}")


if __name__ == "__main__":
    main()
