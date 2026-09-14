"""E12 Stage 1 — the direct / trajectory-mediated decomposition.

For each (model, cell, intervention), across the clamp fraction grid:

    Y(R)  - Y(F)    total trajectory mediation
    Y(R)  - Y(R~)   the part explained by prefix content being worse (exposure bias)
    Y(R~) - Y(F)    residual: produced under the same perturbation, beyond content

and the primary estimand, the depth x trajectory-dependence interaction

    delta = [Y(late) - Y(early)]_free-running - [Y(late) - Y(early)]_clamped

Accuracy is computed on items the full-precision model answers correctly, so the
quantity is retention and cell difficulty is conditioned out.
"""
from __future__ import annotations
import importlib.util, json, pathlib, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("summ", ROOT / "scripts" / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)
RNG = np.random.default_rng(9109); B = 10000


def key(r):
    return "acc_permissive" if r.get("acc_permissive") is not None else "acc"


def per_item(path):
    s = summ.score(path)
    if s.get("correct") is None:
        return None
    ids = [json.loads(l)["id"] for l in open(path)][1:]
    return dict(zip(ids, s["correct"])), s


def retention(full_map, run_map):
    """indicator over items the full model gets right"""
    v = [run_map[i] for i, c in full_map.items() if c and i in run_map]
    return np.array(v, float)


def boot_diff(a, b):
    d = []
    for _ in range(B):
        ia = RNG.integers(0, len(a), len(a)); ib = RNG.integers(0, len(b), len(b))
        d.append(a[ia].mean() - b[ib].mean())
    return np.percentile(d, [2.5, 97.5])


def main():
    runs = collections.defaultdict(dict)
    for p in (ROOT / "results" / "e12").rglob("*.jsonl"):
        h = json.loads(open(p).readline())
        runs[(p.parent.name, h["cell"], h["mask"])][(h["clamp"], h["frac"])] = p

    for (tag, cell, iv), cells in sorted(runs.items()):
        fullp = ROOT / "results" / "e01" / tag / f"{cell}__full.jsonl"
        if not fullp.exists():
            continue
        fm, fs = per_item(fullp)
        print(f"\n=== {tag} / {cell} / {iv} ===")
        print(f"    full-precision baseline {fs[key(fs)]:.4f} on {sum(fm.values())} "
              f"correct of {len(fm)} items")
        print(f"\n{'arm':<12}{'frac':>6}{'retention':>12}{'n':>7}")
        table = {}
        for (arm, frac), p in sorted(cells.items()):
            rm, _ = per_item(p)
            v = retention(fm, rm)
            table[(arm, frac)] = v
            print(f"{arm:<12}{frac:>6.2f}{v.mean():>12.4f}{len(v):>7}")

        fracs = sorted({f for a, f in table if a != "none"})
        free = table.get(("none", 0.0))
        if free is None or not fracs:
            continue
        print(f"\n{'contrast':<44}{'estimate':>10}{'95% CI':>18}")
        for f in fracs:
            R = table.get(("reference", f)); Rt = table.get(("corrupted", f))
            if R is not None:
                lo, hi = boot_diff(R, free)
                print(f"{f'Y(R,f={f:g}) - Y(F)   total mediation':<44}"
                      f"{R.mean()-free.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
            if R is not None and Rt is not None:
                lo, hi = boot_diff(R, Rt)
                print(f"{f'Y(R,f={f:g}) - Y(R~,f={f:g})   content / exposure bias':<44}"
                      f"{R.mean()-Rt.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
                lo, hi = boot_diff(Rt, free)
                print(f"{f'Y(R~,f={f:g}) - Y(F)   RESIDUAL':<44}"
                      f"{Rt.mean()-free.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
        if len(fracs) >= 2:
            early, late = fracs[0], fracs[-1]
            a, b = table.get(("reference", late)), table.get(("reference", early))
            if a is not None and b is not None:
                print(f"\n  clamped depth response  Y(f={late:g}) - Y(f={early:g}) "
                      f"= {a.mean()-b.mean():+.4f}")
                print(f"  (free-running is the f=0 point, retention {free.mean():.4f})")


if __name__ == "__main__":
    main()
