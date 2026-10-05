"""Grouped structural signatures for runs whose cond = '<group>:<pattern>' (E03 cue, E05 dim).
usage: analyze_groups.py DATA_DIR "RESULT_GLOB" [--json OUT]
Signatures per group (paired within base vs the group's allA):
  single_t kernel (first/last), suffix_k curve, disp_k, suffix4-disp4, noise effects, blocks,
  correlation of condition means with set / meta oracle.
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_common import boot_ci, fmt  # noqa


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("data"); ap.add_argument("res"); ap.add_argument("--json")
    a = ap.parse_args()
    sc = {}
    for f in glob.glob(a.res):
        for l in open(f):
            s = json.loads(l); sc[s["uid"]] = s["lp"]
    recs = []
    for l in open(Path(a.data) / "rows.jsonl"):
        r = json.loads(l)
        if r["uid"] not in sc:
            continue
        lp = sc[r["uid"]]; lo1 = lp[1] - lp[0]
        g, pat = r["cond"].split(":", 1)
        recs.append(dict(uid=r["uid"], group=g, pat=pat, base=r["base_id"],
                         lo_B=lo1 if r["query_label_B"] == 1 else -lo1, mass=float(np.exp(lp).sum()),
                         meta=logit(r["oracle"]["meta_pB"]), set=logit(r["oracle"]["set_pB"])))
    df = pd.DataFrame(recs).drop_duplicates("uid")
    R = {}
    for g in sorted(df.group.unique(), key=lambda x: (len(x), x)):
        D = df[df.group == g]
        ref = D[D.pat == "allA"].set_index("base")
        D = D.assign(d=D.lo_B - D.base.map(ref.lo_B), dm=D.meta - D.base.map(ref.meta), ds=D.set - D.base.map(ref.set))
        piv = D.pivot_table(index="base", columns="pat", values="lo_B")
        gm = D.groupby("pat").agg(lm=("d", "mean"), meta=("dm", "mean"), set=("ds", "mean"))

        def diff(p1, p0):
            x = (piv[p1] - piv[p0]).dropna(); return boot_ci(x)
        res = {"n_bases": int(D.base.nunique()), "mass": float(D.mass.mean()),
               "allA_lo_B": boot_ci(ref.lo_B), "accA": float((ref.lo_B < 0).mean()),
               "kernel": {p: float(gm.loc[p, "lm"]) for p in gm.index if p.startswith("single_")},
               "suffix": {p: float(gm.loc[p, "lm"]) for p in gm.index if p.startswith("suffix_")},
               "disp": {p: float(gm.loc[p, "lm"]) for p in gm.index if p.startswith("disp_")},
               "suf4_minus_disp4": diff("suffix_4", "disp_4"),
               "oracle_suf4_minus_disp4": {"meta": float(gm.loc["suffix_4", "meta"] - gm.loc["disp_4", "meta"]),
                                           "set": float(gm.loc["suffix_4", "set"] - gm.loc["disp_4", "set"])},
               "r_set": float(np.corrcoef(gm.lm, gm.set)[0, 1]), "r_meta": float(np.corrcoef(gm.lm, gm.meta)[0, 1])}
        if "single_16" in piv and "single_1" in piv:
            res["last_minus_first_single"] = diff("single_16", "single_1")
        for m in (2, 4):
            for k in (3, 5):
                c = f"noise_{m}__suffix_{k}"
                if c in piv and f"suffix_{k}" in piv:
                    res[f"noise{m}_on_suffix{k}"] = diff(c, f"suffix_{k}")
                    res[f"noise{m}_on_suffix{k}_meta"] = float(gm.loc[c, "meta"] - gm.loc[f"suffix_{k}", "meta"])
        for b in ("block_start4", "block_mid4", "block_late4_return2"):
            if b in gm.index:
                res[b] = {"lm": float(gm.loc[b, "lm"]), "meta": float(gm.loc[b, "meta"]), "set": float(gm.loc[b, "set"])}
        R[g] = res
        print(f"\n=== group {g}: bases {res['n_bases']} mass {res['mass']:.3f} allA {fmt(*res['allA_lo_B'])} accA {res['accA']:.2f}")
        if "last_minus_first_single" in res:
            print(f"  single_16 - single_1: {fmt(*res['last_minus_first_single'])}")
        print("  kernel:", {k: round(v, 2) for k, v in res["kernel"].items()})
        print("  suffix:", {k: round(v, 2) for k, v in res["suffix"].items()})
        print("  disp  :", {k: round(v, 2) for k, v in res["disp"].items()})
        print(f"  suffix4 - disp4: LM {fmt(*res['suf4_minus_disp4'])}  meta {res['oracle_suf4_minus_disp4']['meta']:+.2f} set {res['oracle_suf4_minus_disp4']['set']:+.2f}")
        for k in [k for k in res if k.startswith("noise") and not k.endswith("_meta")]:
            print(f"  {k}: LM {fmt(*res[k])}  meta {res[k + '_meta']:+.2f}")
        for b in ("block_start4", "block_mid4", "block_late4_return2"):
            if b in res:
                print(f"  {b}: LM {res[b]['lm']:+.2f} meta {res[b]['meta']:+.2f} set {res[b]['set']:+.2f}")
        print(f"  r(cond means): set {res['r_set']:.3f} meta {res['r_meta']:.3f}")
    if a.json:
        json.dump(R, open(a.json, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
