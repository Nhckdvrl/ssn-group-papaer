#!/usr/bin/env python3
"""E222: pre-registered readings R1 (sink check), R2 (depth-aligned ladder), R3 (mid-conv re-entry), plus norm diagnostics.
Usage: e222_judge.py OUT222_DIR OUT_JSON"""
import json
import sys
from pathlib import Path

TF = ["T", "QT", "GT", "L1B"]; HYB = ["H", "QH", "GH", "FH3"]; OTHER = ["FM", "Llamba"]


def g(r, cond, cell="all", s="dnll"):
    return r["conds"][cond]["cells"][cell][s]


def main():
    d = Path(sys.argv[1]); M = {n: json.loads((d / f"{n}.json").read_text()) for n in TF + HYB + OTHER if (d / f"{n}.json").exists()}
    out = {}
    for n, r in M.items():
        print(f"== {n} L={r['n_layers']} d8={r['d8']} mid={r['mid']} restore={r.get('restore_check_max_abs')}")
        for c, v in r["conds"].items():
            ce = v["cells"]
            print(f"   {c:16s} norm {' '.join(f'{k}={x:.2f}' for k, x in v['norm_ratio'].items())} | all {ce['all']['dnll']:+.2f} "
                  f"| int_rep {ce['internal_rep']['dnll']:+.2f}/{ce['internal_rep']['dtop1']:+.3f} int_first {ce['internal_first']['dnll']:+.2f} "
                  f"| ini_first {ce['initial_first']['dnll']:+.2f}")
    # R1
    r1 = {}
    for n in TF:
        if n not in M:
            continue
        r = M[n]; ratio = g(r, "D8_sink") / g(r, "ALL_sink"); copy = g(r, "D8_sink", "internal_rep")
        r1[n] = {"ratio_sink": ratio, "copy_sink": copy, "ratio_self": g(r, "D8_self") / g(r, "ALL_self"), "copy_self": g(r, "D8_self", "internal_rep"),
                 "norm_after_d8_self": r["conds"]["D8_self"]["norm_ratio"].get("after_d8"), "norm_after_d8_sink": r["conds"]["D8_sink"]["norm_ratio"].get("after_d8")}
        if "B0_sink" in r["conds"]:
            r1[n].update({"ratio_B0_sink": g(r, "B0_sink") / g(r, "ALL_sink"), "copy_B0_sink": g(r, "B0_sink", "internal_rep")})
    real = sum(v["ratio_sink"] >= .8 and v["copy_sink"] >= 2.0 for v in r1.values())
    art = sum(v["ratio_sink"] <= .5 or v["copy_sink"] <= .8 for v in r1.values())
    out["R1"] = {"per_model": r1, "cliff_real": real >= 3, "sink_artifact": art >= 3}
    # R2
    r2 = {}
    for n in HYB + OTHER:
        if n in M:
            r = M[n]
            r2[n] = {"ratio_sink": g(r, "D8_all_sink") / g(r, "ALL_all_sink"), "copy_sink": g(r, "D8_all_sink", "internal_rep"),
                     "first_sink": g(r, "D8_all_sink", "internal_first"), "norm_after_d8": r["conds"]["D8_all_sink"]["norm_ratio"].get("after_d8")}
    for n in TF:
        if n in r1:
            r2[n] = {"ratio_sink": r1[n]["ratio_sink"], "copy_sink": r1[n]["copy_sink"], "first_sink": g(M[n], "D8_sink", "internal_first"),
                     "norm_after_d8": r1[n]["norm_after_d8_sink"]}
    out["R2"] = r2
    # R3
    r3 = {}
    for n in HYB + OTHER:
        if n not in M or "D8_all+MID_conv" not in M[n]["conds"]:
            continue
        r = M[n]; a = g(r, "D8_all_sink", "internal_rep"); b = g(r, "MID_conv", "internal_rep"); ab = g(r, "D8_all+MID_conv", "internal_rep")
        am = g(r, "D8_all+MID_mem", "internal_rep") if "D8_all+MID_mem" in r["conds"] else None
        ok = ab >= 2 * max(a, b) and ab >= 1.5 and (am is None or am <= .5 * ab)
        r3[n] = {"D8": a, "MID_conv": b, "D8+MID_conv": ab, "D8+MID_mem": am, "interaction": ab - a - b, "met": ok,
                 "all_tokens": {"D8": g(r, "D8_all_sink"), "MID_conv": g(r, "MID_conv"), "D8+MID_conv": g(r, "D8_all+MID_conv"),
                                "D8+MID_mem": g(r, "D8_all+MID_mem") if "D8_all+MID_mem" in r["conds"] else None},
                 "top1": {"D8": g(r, "D8_all_sink", "internal_rep", "dtop1"), "MID_conv": g(r, "MID_conv", "internal_rep", "dtop1"),
                          "D8+MID_conv": g(r, "D8_all+MID_conv", "internal_rep", "dtop1"),
                          "D8+MID_mem": g(r, "D8_all+MID_mem", "internal_rep", "dtop1") if "D8_all+MID_mem" in r["conds"] else None}}
    out["R3"] = {"per_model": r3, "met": sum(r3[n]["met"] for n in HYB if n in r3) >= 3}
    print(json.dumps(out, indent=1))
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
