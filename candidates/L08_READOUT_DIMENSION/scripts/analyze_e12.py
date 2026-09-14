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
    ids = [json.loads(l)["id"] for l in list(open(path))[1:]]
    return dict(zip(ids, s["correct"])), s


def retention(full_map, run_map, only=None):
    """indicator over items the full model gets right, optionally restricted"""
    v = [run_map[i] for i, c in full_map.items()
         if c and i in run_map and (only is None or i in only)]
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
        if "clamp" not in h:       # a control-prefix generation, not a clamp run
            continue
        # `corrupted` was used as the CLI tag for two different controls -- the
        # temperature-sampled one and the surgical one -- which silently collided in
        # this dict.  Disambiguate by the clamp source that was actually used.
        arm = h["clamp"]
        if arm == "corrupted":
            src = h.get("clamp_source", "")
            arm = "surgical" if "surgical" in src else "temp-corrupt"
        runs[(p.parent.name, h["cell"], h["mask"])][(arm, h["frac"])] = p

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

        # the surgical control only exists for trajectories that actually contained a
        # calculator annotation; every contrast involving it is computed on that
        # subset, free-running included, so the arms share an item set.
        sg = ROOT / "results" / "e12" / tag / f"{cell}__surgical_ref.jsonl"
        elig = None
        if sg.exists():
            elig = {json.loads(l)["id"] for l in list(open(sg))[1:]
                    if json.loads(l).get("n_annotations_corrupted", 0) > 0}
        if elig and ("surgical", 0.5) in cells:
            print(f"\n  surgical contrast, restricted to the {len(elig)} trajectories "
                  f"with a corrupted annotation:")
            fm2 = {i: c for i, c in fm.items() if i in elig}
            sub = {}
            for (arm, fr), pth in sorted(cells.items()):
                rm, _ = per_item(pth)
                sub[(arm, fr)] = retention(fm2, rm, only=elig)
            f0 = sub.get(("none", 0.0))
            for arm, lab in (("surgical", "Y(R~s)  on-task, structured, WRONG"),
                             ("reference", "Y(R)    on-task, structured, right"),
                             ("foreign", "Y(T')   another treatment")):
                v = sub.get((arm, 0.5))
                if v is None or f0 is None:
                    continue
                lo, hi = boot_diff(v, f0)
                print(f"    {lab:<44}{v.mean():>8.4f}   vs free {f0.mean():.4f}   "
                      f"diff {v.mean()-f0.mean():>+7.4f}  [{lo:>+6.3f},{hi:>+6.3f}]")

        fracs = sorted({f for a, f in table if a != "none"})
        free = table.get(("none", 0.0))
        if free is None or not fracs:
            continue
        # V4: clamping a model to its OWN free-running prefix must be a no-op
        selfc = table.get(("self", 0.5))
        if selfc is not None and free is not None:
            d = abs(selfc.mean() - free.mean())
            print(f"\n  V4 self-clamp no-op check: self {selfc.mean():.4f} vs "
                  f"free-running {free.mean():.4f}  ->  "
                  f"{'PASS' if d <= 0.01 else 'FAIL'} (|diff| {d:.4f})")
        print(f"\n{'contrast':<44}{'estimate':>10}{'95% CI':>18}")
        for f in fracs:
            R = table.get(("reference", f)); Rt = table.get(("surgical", f))
            Tc = table.get(("temp-corrupt", f))
            if R is not None:
                lo, hi = boot_diff(R, free)
                print(f"{f'Y(R,f={f:g}) - Y(F)   total mediation':<44}"
                      f"{R.mean()-free.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
            F2 = table.get(("foreign", f))
            if F2 is not None:
                lo, hi = boot_diff(F2, free)
                print(f"{f'Y(foreign,f={f:g}) - Y(F)   another treatment prefix':<44}"
                      f"{F2.mean()-free.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
                if R is not None:
                    lo, hi = boot_diff(R, F2)
                    print(f"{f'Y(R,f={f:g}) - Y(foreign,f={f:g})   correctness':<44}"
                          f"{R.mean()-F2.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
            if R is not None and Rt is not None:
                lo, hi = boot_diff(R, Rt)
                print(f"{f'Y(R,f={f:g}) - Y(R~s,f={f:g})   content (surgical)':<44}"
                      f"{R.mean()-Rt.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
                lo, hi = boot_diff(Rt, free)
                print(f"{f'Y(R~s,f={f:g}) - Y(F)   RESIDUAL (surgical)':<44}"
                      f"{Rt.mean()-free.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
            if Tc is not None:
                lo, hi = boot_diff(Tc, free)
                print(f"{f'Y(temp-corrupt,f={f:g}) - Y(F)   [FAILED CONTROL]':<44}"
                      f"{Tc.mean()-free.mean():>10.4f}   [{lo:>5.3f},{hi:>6.3f}]")
        if len(fracs) >= 2:
            early, late = fracs[0], fracs[-1]
            a, b = table.get(("reference", late)), table.get(("reference", early))
            if a is not None and b is not None:
                print(f"\n  clamped depth response  Y(f={late:g}) - Y(f={early:g}) "
                      f"= {a.mean()-b.mean():+.4f}")
                print(f"  (free-running is the f=0 point, retention {free.mean():.4f})")


if __name__ == "__main__":
    main()
