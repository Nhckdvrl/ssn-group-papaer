#!/usr/bin/env python3
"""E230 verdict summary (primary after 11-25 validation): per model x fmt x ds x frame, share of
B = rejects / changes the given answer, A = endorses / keeps it, C = no verdict, for C / S / O; knowledge gate from E229 clean.
usage: python e230_summarize2.py out.json base=<e230 verdict>,<e229 judged> sft=... instruct=...  [--judge-only]"""
import json, sys, collections
from e229_summarize import wilson, boot
from e230_rule import final
FR = {"V": "Let me check whether this answer is correct.", "W": "Wait,"}


def main():
    judge_only = "--judge-only" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--judge-only"]
    out, specs = args[0], dict(a.split("=", 1) for a in args[1:])
    res = {}
    for name, paths in specs.items():
        p230, p229 = paths.split(",")
        gate = {(r["fmt"], r["ds"], r["id"]): r["judge"] for r in map(json.loads, open(p229)) if r["cond"] == "clean"}
        by = collections.defaultdict(dict)
        for r in map(json.loads, open(p230)):
            by[(r["fmt"], r["ds"], r["id"], r["frame"])][r["cond"]] = r["verdict"] if judge_only else final(r, FR)
        for fmt, ds, fr in sorted({(k[0], k[1], k[3]) for k in by}):
            keys = [k for k in by if (k[0], k[1], k[3]) == (fmt, ds, fr) and gate.get(k[:3])]
            cell = dict(n=len(keys))
            for c in "CSO":
                for v in "ABC":
                    cell[f"{c}_{v}"] = wilson(sum(by[k][c] == v for k in keys), len(keys))
            cell["O-C_B"] = boot([(by[k]["O"] == "B", by[k]["C"] == "B") for k in keys])
            cell["S-C_B"] = boot([(by[k]["S"] == "B", by[k]["C"] == "B") for k in keys])
            res[f"{name}|{fmt}|{ds}|{fr}"] = cell
    json.dump(res, open(out, "w"), indent=1)
    f = lambda v: f"{v[0]:+.2f}[{v[1]:+.2f},{v[2]:+.2f}]"
    print(f"{'model|fmt|ds|frame':28s}  n   reject C / S / O     endorse C / S / O    none C / S / O    O-C(reject)          S-C(reject)")
    for k, c in res.items():
        g = lambda v: " ".join(f"{c[x + '_' + v][0]:.2f}" for x in "CSO")
        print(f"{k:28s} {c['n']:3d}  {g('B'):18s}  {g('A'):18s}  {g('C'):16s}  {f(c['O-C_B']):20s} {f(c['S-C_B'])}")


if __name__ == "__main__":
    main()
