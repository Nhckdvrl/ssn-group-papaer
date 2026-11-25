#!/usr/bin/env python3
"""E230 summary: knowledge gate from E229 clean judgments; per model x fmt x ds x frame, rates of
correct final answer (judge) and explicit flagging (flag) for C / S / O, with paired bootstrap O-C, S-C.
usage: python e230_summarize.py out.json base=<e230 judged>,<e229 judged> sft=... instruct=...
"""
import json, sys, collections
from e229_summarize import wilson, boot


def main():
    out, specs = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
    res = {}
    for name, paths in specs.items():
        p230, p229 = paths.split(",")
        gate = {(r["fmt"], r["ds"], r["id"]): r["judge"] for r in map(json.loads, open(p229)) if r["cond"] == "clean"}
        by = collections.defaultdict(dict)
        for r in map(json.loads, open(p230)):
            by[(r["fmt"], r["ds"], r["id"], r["frame"])][r["cond"]] = (r["judge"], r["flag"])
        for fmt, ds, fr in sorted({(k[0], k[1], k[3]) for k in by}):
            keys = [k for k in by if (k[0], k[1], k[3]) == (fmt, ds, fr) and gate.get(k[:3])]
            cell = dict(gate_pass=len(keys))
            for c in "CSO":
                cell[c] = wilson(sum(by[k][c][0] for k in keys), len(keys))
                cell[c + "_flag"] = wilson(sum(by[k][c][1] for k in keys), len(keys))
            for a, b in [("O", "C"), ("S", "C")]:
                cell[f"{a}-{b}"] = boot([(by[k][a][0], by[k][b][0]) for k in keys])
                cell[f"{a}-{b}_flag"] = boot([(by[k][a][1], by[k][b][1]) for k in keys])
            res[f"{name}|{fmt}|{ds}|{fr}"] = cell
    json.dump(res, open(out, "w"), indent=1)
    f = lambda v: f"{v[0]:.2f}[{v[1]:.2f},{v[2]:.2f}]" if v and v[0] is not None else "-"
    print(f"{'model|fmt|ds|frame':30s} n   C            S            O            O-C               S-C              | flag C/S/O")
    for k, c in res.items():
        print(f"{k:30s} {c['gate_pass']:3d} {c['C'][0]:.2f} {c['S'][0]:.2f} {c['O'][0]:.2f}   {f(c['O-C']):18s} {f(c['S-C']):18s} | "
              f"{c['C_flag'][0]:.2f} {c['S_flag'][0]:.2f} {c['O_flag'][0]:.2f}")


if __name__ == "__main__":
    main()
