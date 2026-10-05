"""E08 analysis. usage: analyze_long.py DATA_DIR "RESULT_GLOB" """
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))


def main():
    sc = {}
    for f in glob.glob(sys.argv[2]):
        for l in open(f):
            s = json.loads(l); sc[s["uid"]] = s["lp"]
    recs = []
    for l in open(Path(sys.argv[1]) / "rows.jsonl"):
        r = json.loads(l)
        if r["uid"] not in sc:
            continue
        lp = sc[r["uid"]]; lo1 = lp[1] - lp[0]
        g, p = r["cond"].split(":", 1)
        recs.append(dict(g=g, p=p, base=r["base_id"].split("_aligned")[0].split("_anti")[0],
                         lo=lo1 if r["query_label_B"] == 1 else -lo1, meta=logit(r["oracle"]["meta_pB"]),
                         set=logit(r["oracle"]["set_pB"]), mass=float(np.exp(lp).sum())))
    df = pd.DataFrame(recs)
    for g in ("T32", "T64"):
        D = df[df.g == g]
        if D.empty:
            continue
        piv = D.pivot_table(index="base", columns="p", values="lo")
        print(f"\n=== {g}: bases {D.base.nunique()} mass {D.mass.mean():.3f} accA {(piv['allA'] < 0).mean():.2f}")
        for p in sorted(D.p.unique(), key=lambda x: (x.split('_')[0], len(x), x)):
            x = D[D.p == p]
            print(f"  {p:22s} LM {x.lo.mean():+6.2f}   meta {x.meta.mean():+6.2f}  set {x.set.mean():+6.2f}")
        h = {"T32": 16, "T64": 32}[g]; q = h // 2; e = h // 4
        for a_, b_ in ((f"suffix_{h}", f"prefix_{h}"), (f"suffix_{q}", f"disp_{q}"), (f"suffix_{e}", f"disp_{e}"),
                       (f"noise_{e}__suffix_{q}", f"suffix_{q}")):
            d = (piv[a_] - piv[b_]).dropna()
            m = D[D.p == a_].meta.mean() - D[D.p == b_].meta.mean()
            print(f"  {a_} - {b_}: LM {fmt(*boot_ci(d))}   meta {m:+.2f}")
    D = df[df.g == "AL"]
    if not D.empty:
        print("\n=== aligned surface runs (T=16): effect = lo(B pattern) - lo(allA, same order)")
        D = D.assign(kind=D.p.str.split("_").str[0], order=D.p.str.split("_").str[1], pat=D.p.str.split("_").str[2])
        piv = D.pivot_table(index=["base", "kind", "order"], columns="pat", values="lo")
        eff = (piv["B"] - piv["allA"]).rename("eff").reset_index()
        pm = D.pivot_table(index=["base", "kind", "order"], columns="pat", values="meta")
        effm = (pm["B"] - pm["allA"]).rename("effm").reset_index()
        E = eff.merge(effm)
        for k in ("aligned", "anti"):
            w = E[E.kind == k].pivot_table(index="base", columns="order", values="eff")
            wm = E[E.kind == k].pivot_table(index="base", columns="order", values="effm")
            d = (w["suffix4"] - w["disp4"]).dropna()
            print(f"  {k:8s} suffix4 {w['suffix4'].mean():+.2f}  disp4 {w['disp4'].mean():+.2f}  diff {fmt(*boot_ci(d))}"
                  f"   | meta suffix {wm['suffix4'].mean():+.2f} disp {wm['disp4'].mean():+.2f}")


if __name__ == "__main__":
    main()
