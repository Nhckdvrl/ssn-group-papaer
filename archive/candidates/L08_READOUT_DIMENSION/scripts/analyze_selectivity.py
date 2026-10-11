"""The controlled test of capability-selective damage, with uncertainty.

The literature's claim is read off an UNCONTROLLED contrast:
    rank-scored knowledge   vs   generation-scored long reasoning
The controlled version holds protocol and output length fixed:
    generation-scored long knowledge  vs  generation-scored long reasoning

Both are reported here as ratios of relative performance, with a paired bootstrap over
items (items are shared across masks within a cell; cells are independent).
"""
import importlib.util, json, pathlib, collections
import numpy as np

spec = importlib.util.spec_from_file_location(
    "summ", pathlib.Path(__file__).resolve().parent / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)
ROOT = pathlib.Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(9109)
B = 10000


def vec(r):
    return np.array(r["correct"], dtype=float)


full, cond = {}, collections.defaultdict(dict)
TAGMAP = {"llama": "llama31_8b_instruct", "qwen": "qwen25_7b_instruct",
          "phi4": "phi4_mini_instruct", "olmo3": "olmo3_7b_base",
          "olmo3_7b_base": "olmo3_7b_base", "mistral": "mistral_7b_v03",
          "mistral_7b_v03": "mistral_7b_v03"}
for p in (ROOT / "results" / "e01").rglob("*.jsonl"):
    r = summ.score(p)
    if r.get("correct") is None: continue
    m = p.parent.name                       # directory, not checkpoint path
    if r["mask"] == "full": full[(m, r["cell"])] = r
    else: cond[(m, f"readout-{r['mask']}")][r["cell"]] = r
for p in (ROOT / "results" / "e10").rglob("*.jsonl"):
    if "calib" in str(p): continue
    r = summ.score(p)
    if r.get("correct") is None: continue
    cond[(TAGMAP.get(p.parent.name, p.parent.name), r["mask"])][r["cell"]] = r


def ratio(mdl, iv, cell_a, cell_b):
    """rel(cell_a)/rel(cell_b) with a bootstrap CI; None if any cell is missing."""
    need = [(mdl, c) for c in (cell_a, cell_b)]
    if any(k not in full for k in need): return None
    # a ratio is only meaningful if the FULL-precision baseline is non-degenerate
    if any(vec(full[k]).mean() < 0.05 for k in need): return None
    if any(c not in cond[(mdl, iv)] for c in (cell_a, cell_b)): return None
    # ...and if the denominator cell has not been driven to the floor.  When both
    # cells collapse to ~0 the ratio is not estimable, not infinite; reporting it as
    # a large number would invent a selectivity effect out of a floor effect.
    if vec(cond[(mdl, iv)][cell_b]).mean() < 0.02: return "floored"
    out = []
    for cell in (cell_a, cell_b):
        f, t = vec(full[(mdl, cell)]), vec(cond[(mdl, iv)][cell])
        n = min(len(f), len(t)); f, t = f[:n], t[:n]
        idx = RNG.integers(0, n, size=(B, n))
        with np.errstate(divide="ignore", invalid="ignore"):
            out.append(np.where(f[idx].mean(1) > 0, t[idx].mean(1) / f[idx].mean(1), np.nan))
        out[-1] = np.clip(out[-1], 1e-6, None)
    r = out[0] / out[1]
    point = ((vec(cond[(mdl, iv)][cell_a]).mean() / vec(full[(mdl, cell_a)]).mean())
             / max(1e-6, vec(cond[(mdl, iv)][cell_b]).mean() / vec(full[(mdl, cell_b)]).mean()))
    lo, hi = np.nanpercentile(r, [2.5, 97.5])
    return point, lo, hi


print("UNCONTROLLED contrast, as the literature reads it "
      "(rank-scored knowledge / generation-scored long reasoning):")
print(f"{'model':<18}{'intervention':<16}{'ratio':>9}{'95% CI':>20}")
rowsA = []
for (mdl, iv) in sorted(cond):
    r = ratio(mdl, iv, "mmlu_rank", "gsm8k_gen_cot")
    if r == "floored":
        print(f"{mdl[:17]:<18}{iv:<16}{'n/e':>9}   (denominator at floor)"); continue
    if r: rowsA.append((mdl, iv, *r)); print(
        f"{mdl.split('/')[-1][:13]:<14}{iv:<16}{r[0]:>9.2f}   [{r[1]:>6.2f},{r[2]:>7.2f}]")

print("\nCONTROLLED contrast, protocol and length held fixed "
      "(long-generation knowledge / long-generation reasoning):")
print(f"{'model':<18}{'intervention':<16}{'ratio':>9}{'95% CI':>20}   reading")
rowsB = []
for (mdl, iv) in sorted(cond):
    r = ratio(mdl, iv, "mmlu_gen_cot", "gsm8k_gen_cot")
    if r == "floored":
        print(f"{mdl[:17]:<18}{iv:<16}{'n/e':>9}   "
              f"{'':>18}   not estimable: both cells at the floor"); continue
    if not r: continue
    rowsB.append((mdl, iv, *r))
    if r[1] > 1: note = "reasoning genuinely more fragile"
    elif r[2] < 1: note = "reasoning genuinely MORE ROBUST"
    else: note = "no selectivity"
    print(f"{mdl[:17]:<18}{iv:<16}{r[0]:>9.2f}   "
          f"[{r[1]:>6.2f},{r[2]:>7.2f}]   {note}")

print("\nShare of the apparent capability effect that the controls remove:")
print(f"{'model':<18}{'intervention':<16}{'uncontrolled':>13}{'controlled':>12}{'removed':>9}")
dA = {(m, i): p for m, i, p, _, _ in rowsA}
dB = {(m, i): p for m, i, p, _, _ in rowsB}
for k in sorted(set(dA) & set(dB)):
    a, b = dA[k], dB[k]
    print(f"{k[0][:17]:<18}{k[1]:<16}{a:>13.2f}{b:>12.2f}"
          f"{(1 - (b - 1) / (a - 1) if a > 1 else float('nan')):>9.1%}")
json.dump({"uncontrolled": [[m, i, p, lo, hi] for m, i, p, lo, hi in rowsA],
           "controlled": [[m, i, p, lo, hi] for m, i, p, lo, hi in rowsB]},
          open(ROOT / "results" / "selectivity.json", "w"), indent=1)
