"""POST-HOC checks (2026-10-10) of two readings proposed in an external re-audit.

(1) E24: is the recipe-level anti-correlation between copy fidelity and
    Substitution-conflict adoption (rho -0.685) carried by corpus families?
(2) E75: how many of the "task-mapped" heads are simply the target model's own
    top-3 (selected on target DLA)? If most are, the mapping re-discovers the
    target circuit rather than transferring source knowledge.

CPU only; reads existing result files. Writes results/posthoc_2026_10_10.json.
"""
import json

import numpy as np
from scipy.stats import spearmanr

import mp_common as mc

R = mc.RESULTS


def family(recipe):
    if "dolma1.7" in recipe:
        return "dclm_dolma_mix"
    if recipe.startswith("dclm-baseline"):
        return "dclm"
    if recipe.startswith("dolma"):
        return "dolma"
    if recipe.startswith("falcon"):
        return "falcon"
    if recipe.startswith("fineweb"):
        return "fineweb"
    return recipe.split("-")[0]


def e24_family():
    rows = {}
    for f in (R / "e24").glob("*__*.json"):
        r = json.loads(f.read_text())
        c = json.loads((R / "e20" / f.name).read_text())["conditions"]
        sub = np.mean([v["margin"] for k, v in c.items() if k.endswith("Substitution Conflict")])
        coh = np.mean([v["margin"] for k, v in c.items() if k.endswith("Coherent Conflict")])
        k_ = np.mean([v["clean_margin"] for v in c.values()])
        rows.setdefault(f.stem.split("__")[0], []).append((-r["loss_second"], sub, coh, k_))
    names = sorted(rows)
    M = np.array([np.mean(rows[n], 0) for n in names])
    fams = [family(n) for n in names]
    out = {"n_recipes": len(names),
           "rho_I1_Asub": spearmanr(M[:, 0], M[:, 1])[0],
           "rho_I1_Acoherent": spearmanr(M[:, 0], M[:, 2])[0],
           "drop_family": {}, "within_family": {}}
    for F in sorted(set(fams)):
        keep = [i for i, g in enumerate(fams) if g != F]
        out["drop_family"][F] = {"n": len(keep), "rho": spearmanr(M[keep, 0], M[keep, 1])[0]}
        idx = [i for i, g in enumerate(fams) if g == F]
        if len(idx) >= 4:
            out["within_family"][F] = {"n": len(idx), "rho": spearmanr(M[idx, 0], M[idx, 1])[0]}
    Z = M.copy()
    for F in set(fams):
        idx = [i for i, g in enumerate(fams) if g == F]
        Z[idx] -= M[idx].mean(0)
    out["family_demeaned_rho_I1_Asub"] = spearmanr(Z[:, 0], Z[:, 1])[0]
    out["recipes"] = {n: {"family": g, "I1": m[0], "A_sub": m[1], "A_coh": m[2], "K": m[3]}
                      for n, g, m in zip(names, fams, M)}
    return out


def e75_overlap():
    a = json.loads((R / "e75" / "analysis.json").read_text())
    out = {}
    for size, d in a.items():
        for tgt, t in d.items():
            if not isinstance(t, dict) or "sets" not in t:
                continue
            s = t["sets"]
            own = set(s["own"]["heads"])
            out[f"{size}/{tgt}"] = {
                k: {"heads": s[k]["heads"], "overlap_with_target_own_top3": len(own & set(s[k]["heads"])),
                    "ratio_total": s[k]["ratio_total"]}
                for k in ("own", "index", "profile_map", "corr_map")}
    return out


if __name__ == "__main__":
    res = {"e24_family": e24_family(), "e75_mapped_vs_target_own": e75_overlap()}
    (R / "posthoc_2026_10_10.json").write_text(json.dumps(res, indent=1, default=float))
    e = res["e24_family"]
    print("E24 rho(I1,A_sub) all", round(e["rho_I1_Asub"], 3), "| family-demeaned",
          round(e["family_demeaned_rho_I1_Asub"], 3), "| rho(I1,A_coh)", round(e["rho_I1_Acoherent"], 3))
    print("  drop family:", {k: round(v["rho"], 2) for k, v in e["drop_family"].items()})
    print("  within family:", {k: round(v["rho"], 2) for k, v in e["within_family"].items()})
    for k, v in res["e75_mapped_vs_target_own"].items():
        print("E75", k, {m: (x["overlap_with_target_own_top3"], round(x["ratio_total"], 2)) for m, x in v.items()})
