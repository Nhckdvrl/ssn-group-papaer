#!/usr/bin/env python3
"""E231 signal-detection summary. H = share rejecting a WRONG given answer (E230 for V/W, E229 verdict for N);
F = share rejecting a CORRECT given answer (E231). Items paired by (fmt, ds, id); knowledge gate from E229 clean.
Reports H, F, H-F per condition and paired bootstrap of (H-F)_O - (H-F)_C and (H-F)_S - (H-F)_C.
usage: python e231_summarize.py out.json base=<e231 verdict>,<e230 verdict>,<e229 verdict>,<e229 judged> sft=... instruct=..."""
import json, sys, random, collections
from e229_summarize import wilson
from e230_rule import final
FR = {"V": "Let me check whether this answer is correct.", "W": "Wait,", "N": ""}


def boot(diffs, B=2000, seed=0):
    rng = random.Random(seed); n = len(diffs)
    if n == 0:
        return None
    s = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(B))
    return [round(sum(diffs) / n, 3), round(s[int(.025 * B)], 3), round(s[int(.975 * B)], 3)]


def load(path, frame=None):
    d = {}
    for r in map(json.loads, open(path)):
        fr = r.get("frame", frame or "N")
        if r["cond"] == "clean":
            continue
        d[(r["fmt"], r["ds"], r["id"], fr, r["cond"])] = final(r, FR) == "B"
    return d


def main():
    out, specs = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
    res = {}
    for name, paths in specs.items():
        p231, p230, p229v, p229j = paths.split(",")
        gate = {(r["fmt"], r["ds"], r["id"]): r["judge"] for r in map(json.loads, open(p229j)) if r["cond"] == "clean"}
        F = load(p231)
        H = {**load(p230), **load(p229v, "N")}
        cells = sorted({(k[0], k[1], k[3]) for k in F})
        for fmt, ds, fr in cells:
            ids = sorted({k[2] for k in F if (k[0], k[1], k[3]) == (fmt, ds, fr) and gate.get((fmt, ds, k[2]))
                          and all((fmt, ds, k[2], fr, c) in H and (fmt, ds, k[2], fr, c) in F for c in "CSO")})
            cell = dict(n=len(ids))
            for c in "CSO":
                h = [H[(fmt, ds, i, fr, c)] for i in ids]; f = [F[(fmt, ds, i, fr, c)] for i in ids]
                cell[c + "_H"] = wilson(sum(h), len(h)); cell[c + "_F"] = wilson(sum(f), len(f))
                cell[c + "_HmF"] = round((sum(h) - sum(f)) / max(1, len(h)), 3)
            dd = lambda a, b: [(H[(fmt, ds, i, fr, a)] - F[(fmt, ds, i, fr, a)]) - (H[(fmt, ds, i, fr, b)] - F[(fmt, ds, i, fr, b)]) for i in ids]
            cell["dO-C"] = boot(dd("O", "C")); cell["dS-C"] = boot(dd("S", "C"))
            cell["F_O-C"] = boot([F[(fmt, ds, i, fr, "O")] - F[(fmt, ds, i, fr, "C")] for i in ids])
            res[f"{name}|{fmt}|{ds}|{fr}"] = cell
    json.dump(res, open(out, "w"), indent=1)
    g = lambda v: f"{v[0]:+.2f}[{v[1]:+.2f},{v[2]:+.2f}]" if v else "-"
    print(f"{'model|fmt|ds|frame':28s}  n   H  C/S/O         F  C/S/O         H-F C/S/O          (H-F)O-C            (H-F)S-C            F O-C")
    for k, c in res.items():
        t = lambda x: " ".join(f"{c[y + '_' + x][0]:.2f}" if x != "HmF" else f"{c[y + '_HmF']:+.2f}" for y in "CSO")
        print(f"{k:28s} {c['n']:3d}  {t('H'):16s} {t('F'):16s} {t('HmF'):19s} {g(c['dO-C']):19s} {g(c['dS-C']):19s} {g(c['F_O-C'])}")


if __name__ == "__main__":
    main()
