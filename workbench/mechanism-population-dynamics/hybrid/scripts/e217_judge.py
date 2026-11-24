#!/usr/bin/env python3
"""E217: apply the pre-registered decision table (card E217) to the conv condition of each model; print all conditions.
Usage: e217_judge.py OUT217_DIR OUT_JSON"""
import json
import sys
from pathlib import Path

MODELS = [("H", "conv"), ("QH", "conv"), ("GH", "conv"), ("FH3", "convmean"), ("T", None), ("Llamba", "convmean")]
REF = {"T", "Llamba"}


def verdict(n, c):
    d_in, d_ini = c["nll_internal"] - n["nll_internal"], c["nll_initial"] - n["nll_initial"]
    r_mwe = c["mwe_adv"] / n["mwe_adv"]
    drop_l, drop_d = 100 * (n["blimp_local"] - c["blimp_local"]), 100 * (n["blimp_distant"] - c["blimp_distant"])
    if drop_d >= 10:
        v = "全局破坏"
    elif d_in >= 2 * d_ini and r_mwe >= .75 and drop_l <= 5 and drop_d <= 5:
        v = "专门负责拼词"
    elif (r_mwe <= .5 or drop_l >= 10) and drop_d <= 5:
        v = "负责一切局部组合"
    else:
        v = "中间"
    return {"dNLL_internal": d_in, "dNLL_initial": d_ini, "ratio_in_ini": d_in / d_ini if d_ini else None, "R_mwe": r_mwe,
            "drop_local": drop_l, "drop_distant": drop_d, "verdict": v}


def main():
    o = Path(sys.argv[1]); res = {}
    keys = ["nll_all50", "nll_internal", "nll_initial", "mwe_adv", "blimp_local", "blimp_distant"]
    for m, cc in MODELS:
        runs = {p.stem.split("_", 1)[1]: json.loads(p.read_text()) for p in sorted(o.glob(f"{m}_*.json"))}
        if "none" not in runs:
            continue
        n = runs["none"]; res[m] = {"runs": {k: {kk: v[kk] for kk in keys} for k, v in runs.items()}, "deltas": {}}
        print(f"== {m}")
        for k, v in runs.items():
            print(f"  {k:9s} " + " ".join(f"{kk}={v[kk]:.3f}" for kk in keys))
        for k, v in runs.items():
            if k == "none":
                continue
            j = verdict(n, v); res[m]["deltas"][k] = j
            tag = j["verdict"] if (k == cc and m not in REF) else "(描述)"
            print(f"  -> {k:9s} dNLL_in={j['dNLL_internal']:+.2f} dNLL_ini={j['dNLL_initial']:+.2f} R_mwe={j['R_mwe']:.2f} "
                  f"drop_local={j['drop_local']:+.1f} drop_distant={j['drop_distant']:+.1f}  {tag}")
    Path(sys.argv[2]).write_text(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
