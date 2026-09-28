"""E02 — evaluate the three pre-registered contrasts with paired uncertainty.

Every cell is scored on the same item ids across masks (fixed data_seed), so the
relative-performance ratio acc(mask)/acc(full) is bootstrapped with items paired
within a cell, and contrasts between cells are bootstrapped independently across
cells (different item sets) but jointly across masks.

Read-out rule was fixed in EXPERIMENTS.md before any E02 cell was scored:
a factor is "carrying" if its matched contrast shows a relative-performance gap of
at least 0.15 in the same direction for both models and both masks.
"""
from __future__ import annotations
import json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(20260910)
B = 10000

CONTRASTS = [
    ("PROTOCOL", "rank K=4 vs argmax over V", "mmlu_rank", "mmlu_gen_letter", "exact"),
    ("DEPTH (reasoning)", "short vs long generation", "gsm8k_gen_direct", "gsm8k_gen_cot", "exact"),
    ("DEPTH (knowledge)", "short vs long generation", "mmlu_gen_letter", "mmlu_gen_cot", "prompt-format caveat"),
    ("CONTENT (short gen)", "knowledge vs reasoning", "mmlu_gen_letter", "gsm8k_gen_direct", "exact"),
    ("CONTENT (long gen)", "knowledge vs reasoning", "mmlu_gen_cot", "gsm8k_gen_cot", "length-matched?"),
]


def load():
    rows = json.loads((ROOT / "results" / "e01_summary.json").read_text())
    d = {}
    for r in rows:
        if r.get("correct") is None:
            continue
        d[(r["model"], r["cell"], r["mask"])] = np.array(r["correct"], dtype=float)
    return d


def rel_boot(full, trunc):
    """Bootstrap acc(trunc)/acc(full) with items paired."""
    n = len(full)
    idx = RNG.integers(0, n, size=(B, n))
    f = full[idx].mean(1)
    t = trunc[idx].mean(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(f > 0, t / f, np.nan)
    return trunc.mean() / full.mean(), r


def main():
    d = load()
    models = sorted({k[0] for k in d})
    print(f"bootstrap B={B}, items paired within cell\n")
    verdict = {}
    for name, desc, cellA, cellB, note in CONTRASTS:
        print(f"### {name}: {desc}   [{cellA} vs {cellB}]   ({note})")
        ok = []
        for m in models:
            for mask in ("first", "last"):
                need = [(m, c, k) for c in (cellA, cellB) for k in ("full", mask)]
                if any(x not in d for x in need):
                    print(f"  {m.split('/')[-1]:<28} {mask:<6} (missing cells)"); ok.append(None); continue
                relA, bA = rel_boot(d[(m, cellA, "full")], d[(m, cellA, mask)])
                relB, bB = rel_boot(d[(m, cellB, "full")], d[(m, cellB, mask)])
                diff = bA - bB
                lo, hi = np.nanpercentile(diff, [2.5, 97.5])
                gap = relA - relB
                ok.append(gap >= 0.15 and lo > 0)
                print(f"  {m.split('/')[-1]:<28} {mask:<6} "
                      f"rel({cellA})={relA:.3f}  rel({cellB})={relB:.3f}  "
                      f"gap={gap:+.3f}  95%CI[{lo:+.3f},{hi:+.3f}]")
        good = [x for x in ok if x is not None]
        v = "CARRYING" if good and all(good) else ("not carrying" if good else "incomplete")
        verdict[name] = v
        print(f"  -> {v}\n")
    print("=== pre-registered verdicts ===")
    for k, v in verdict.items():
        print(f"  {k:<24} {v}")


if __name__ == "__main__":
    main()
