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
      f"{'rand mean':>11}{'rand sd':>9}{'rand min-max':>16}{'f/l ratio':>10}")
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
    print(f"{m[:19]:<20}{c:<16}{(fl[0] if fl[0] is not None else float('nan')):>8.3f}"
          f"{(fl[1] if fl[1] is not None else float('nan')):>8.3f}"
          f"{np.mean(rnd):>11.3f}{np.std(rnd):>9.3f}"
          f"   [{min(rnd):.3f},{max(rnd):.3f}]{ratio:>10.1f}x")
print("\nIf the random spread is comparable to the first/last gap, generation is "
      "sensitive to which coordinates survive in general, not to the identity of the "
      "structured halves.  If the random masks cluster tightly and first/last sit "
      "outside, the structured halves are special.")
