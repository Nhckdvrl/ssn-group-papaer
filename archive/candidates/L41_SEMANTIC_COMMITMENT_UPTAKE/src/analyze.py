"""L41 analysis: proposition-level uptake U, cell means, D, checkerboard I.

Independent unit = proposition identity.  Query paraphrases are averaged within
proposition.  Runs/seeds are blocking factors, never independent units.
"""
import json, sys, random, argparse, statistics as st
from collections import defaultdict

IFACE = "fs"   # frozen primary neutral-query interface (see FREEZE.md)


def mean(x): return sum(x) / len(x)


def load_runs(paths, iface=IFACE):
    """-> per_prop {pid: {cell: {"U":..,"Unm":..,"Ba":..}}}, meta"""
    acc = defaultdict(lambda: defaultdict(list))
    meta = []
    for path in paths:
        r = json.load(open(path))
        bb, ba = r["B_before"], r["B_after"]
        for pid, cell in r["assign"].items():
            u = mean(ba[pid][iface]) - mean(bb[pid][iface])
            unm = ba[pid]["nm_" + iface] - bb[pid]["nm_" + iface]
            acc[pid][cell].append((u, unm, mean(ba[pid][iface])))
        meta.append({"path": path.split("/")[-1],
                     "nll_before": r["generic_nll_before"],
                     "nll_after": r["generic_nll_after"],
                     "lr": r["args"]["lr"], "epochs": r["args"]["epochs"],
                     "n_docs": r["args"]["n_docs"], "bs": r["args"]["bs"],
                     "seed": r["args"]["seed"]})
    per = {pid: {c: {"U": mean([v[0] for v in vs]),
                     "Unm": mean([v[1] for v in vs]),
                     "Ba": mean([v[2] for v in vs])}
                 for c, vs in d.items()} for pid, d in acc.items()}
    return per, meta


def cell_table(per, field="U"):
    cells = defaultdict(list)
    for pid, d in per.items():
        for c, v in d.items():
            cells[c].append(v[field])
    return {c: {"n": len(v), "mean": mean(v), "sd": st.pstdev(v),
                "se": st.pstdev(v) / len(v) ** 0.5} for c, v in sorted(cells.items())}


def contrast(plus, minus, field="U"):
    def f(per, pids):
        vs = []
        for pid in pids:
            d = per[pid]
            if all(c in d for c in plus + minus):
                vs.append(sum(d[c][field] for c in plus) - sum(d[c][field] for c in minus))
        return mean(vs) if vs else float("nan")
    return f


def unpaired_contrast(plus, minus, field="U"):
    def f(per, pids):
        a = [per[pid][c][field] for pid in pids for c in plus if c in per[pid]]
        b = [per[pid][c][field] for pid in pids for c in minus if c in per[pid]]
        return (mean(a) - mean(b)) if a and b else float("nan")
    return f


def boot(per, fn, B=10000, seed=7):
    pids = list(per); rng = random.Random(seed)
    point = fn(per, pids)
    dr = sorted(fn(per, [pids[rng.randrange(len(pids))] for _ in pids]) for _ in range(B))
    dr = [d for d in dr if d == d]
    lo, hi = dr[int(.025 * len(dr))], dr[int(.975 * len(dr))]
    p = 2 * min(sum(d <= 0 for d in dr), sum(d >= 0 for d in dr)) / len(dr)
    return {"point": point, "lo": lo, "hi": hi, "p": min(1.0, p)}


def show(name, r):
    print(f"  {name:28} {r['point']:+7.3f}   95% CI [{r['lo']:+7.3f}, {r['hi']:+7.3f}]   p={r['p']:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["direct", "checker"])
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--iface", default=IFACE)
    ap.add_argument("--paired", action="store_true",
                    help="each proposition appears in every cell across runs")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    per, meta = load_runs(a.runs, a.iface)
    C = contrast if a.paired else unpaired_contrast
    tab = cell_table(per); tabnm = cell_table(per, "Unm")

    print(f"\n  interface={a.iface}  paired={a.paired}  props={len(per)}  runs={len(meta)}")
    print(f"\n  {'cell':5} {'n':>4} {'mean U':>9} {'sd':>7} {'se':>7} | {'nearmiss U':>11} {'se':>6}")
    for c in tab:
        d, e = tab[c], tabnm[c]
        print(f"  {c:5} {d['n']:4d} {d['mean']:+9.3f} {d['sd']:7.3f} {d['se']:7.3f} |"
              f" {e['mean']:+11.3f} {e['se']:6.3f}")
    out = {"iface": a.iface, "paired": a.paired, "cells": tab,
           "cells_nearmiss": tabnm, "runs": meta}
    print()
    if a.kind == "direct":
        out["D"] = boot(per, C(["Ap"], ["An"])); show("D = U(A+) - U(A-)", out["D"])
        out["D_nm"] = boot(per, C(["Ap"], ["An"], "Unm")); show("  same, near-miss probe", out["D_nm"])
    else:
        out["manage"] = boot(per, C(["Mp"], ["Mn"])); show("manage: U(M+) - U(M-)", out["manage"])
        out["fail"] = boot(per, C(["Fp"], ["Fn"])); show("fail  : U(F+) - U(F-)", out["fail"])
        out["I"] = boot(per, C(["Mp", "Fn"], ["Mn", "Fp"])); show("I = checkerboard", out["I"])
        out["pol"] = boot(per, C(["Mp", "Fp"], ["Mn", "Fn"])); show("surface polarity main eff", out["pol"])
        out["verb"] = boot(per, C(["Mp", "Mn"], ["Fp", "Fn"])); show("verb main effect", out["verb"])
        out["I_nm"] = boot(per, C(["Mp", "Fn"], ["Mn", "Fp"], "Unm")); show("I on near-miss probe", out["I_nm"])
    print()
    for r in meta:
        print(f"  [{r['path']}] lr={r['lr']:.0e} exp={r['n_docs']*r['epochs']:>3} "
              f"generic NLL {r['nll_before']:.4f} -> {r['nll_after']:.4f} "
              f"({r['nll_after']-r['nll_before']:+.4f})")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
        print(f"\n  wrote {a.out}")


if __name__ == "__main__":
    main()
