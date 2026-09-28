"""E11 — is the first/last spread mask *identity*, or generic geometric variance?

C1.4 reports that which half of the readout is removed changes relative performance by
up to 13x under generation while making no difference at all under ranking (1.0x).
That is read as evidence that the parent's "removing first or last does not have an
impact, indicating inefficient representation space usage" is protocol-bound.

But first/last are only two masks. If any two random half-masks differ by a similar
amount, then the finding is that *generation is sensitive to which coordinates survive*
— generic geometry — rather than that the first and last halves are special. Both
readings support C1.4's protocol point; they differ in what the residual variance
means, and only random seeds can tell them apart.

This compares the structured masks against three random half-masks per cell.
"""
import importlib.util, pathlib, re, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("summ", ROOT / "scripts" / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)


def key(r):
    return ("acc_permissive" if r.get("acc_permissive") is not None else
            "HasAns_exact" if r.get("HasAns_exact") is not None else "acc")


full, cond = {}, collections.defaultdict(dict)
for p in (ROOT / "results" / "e01").rglob("*.jsonl"):
    r = summ.score(p)
    m = p.parent.name
    tag = r["mask"] if r["mask"] != "random" else f"random{r['mask_seed']}"
    if r["mask"] == "full": full[(m, r["cell"])] = r
    else: cond[(m, r["cell"])][tag] = r

CELLS = ["mmlu_rank", "mmlu_gen_cot", "gsm8k_gen_cot"]
print(f"{'model':<20}{'cell':<16}{'first':>8}{'last':>8}"
      f"{'rand mean':>11}{'rand CV':>9}{'rand min-max':>16}{'f/l':>7}{'all-mask range':>16}")
for (m, c), d in sorted(cond.items()):
    if c not in CELLS: continue
    f = full.get((m, c))
    if not f: continue
    k = key(f); fv = f.get(k, f["acc"])
    if not fv: continue
    rel = {t: r.get(k, r["acc"]) / fv for t, r in d.items()}
    rnd = [v for t, v in rel.items() if t.startswith("random")]
    if not rnd: continue
    fl = [rel.get("first"), rel.get("last")]
    ratio = (max(fl) / min(fl)) if all(x is not None and x > 0 for x in fl) else float("nan")
    cv = np.std(rnd) / np.mean(rnd) if np.mean(rnd) else float("nan")
    # the honest "does the choice of mask matter" statistic: best vs worst of all five
    allm = rnd + [x for x in fl if x is not None]
    span = max(allm) / min(allm) if min(allm) > 0 else float("inf")
    note = f"{min(allm):.3f}-{max(allm):.3f} = {span:.1f}x"
    print(f"{m[:19]:<20}{c:<16}{(fl[0] if fl[0] is not None else float('nan')):>8.3f}"
          f"{(fl[1] if fl[1] is not None else float('nan')):>8.3f}"
          f"{np.mean(rnd):>11.3f}{cv:>8.1%}"
          f"   [{min(rnd):.3f},{max(rnd):.3f}]{ratio:>6.1f}x{note:>16}")
print("\nCV is the coefficient of variation across the three random half-masks.  "
      "'all-mask range' is the best over the worst of all five half-masks tried "
      "(first, last, and three random seeds) -- the honest answer to 'does it matter "
      "which half of the readout survives, at a fixed count of surviving dimensions'.")
