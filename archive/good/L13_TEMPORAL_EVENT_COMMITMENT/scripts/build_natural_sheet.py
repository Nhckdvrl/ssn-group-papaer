#!/usr/bin/env python
"""Stratified, in-scope adjudication sheet from the natural pool."""
import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))
from before_scope import in_scope  # noqa: E402

SEED = 913
N_UNMARKED = 170


def main():
    pool = [json.loads(l) for l in open(os.path.join(PROJ, "data", "natural_pool.jsonl"), encoding="utf-8")]
    kept, reasons = [], collections.Counter()
    for r in pool:
        ok, why = in_scope(r["sentence"])
        if ok:
            r["clause_span"] = why
            kept.append(r)
        else:
            reasons[why] += 1
    print(f"pool {len(pool)} -> in scope {len(kept)}")
    print("excluded:", dict(reasons))

    marked = [r for r in kept if r["marked_modal"]]
    unmarked = [r for r in kept if not r["marked_modal"]]
    rng = random.Random(SEED)
    rng.shuffle(unmarked)
    sample = marked + unmarked[:N_UNMARKED]
    rng.shuffle(sample)
    path = os.path.join(PROJ, "data", "natural_sheet.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in sample:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(sample)} to adjudicate ({len(marked)} modally marked) -> {path}")


if __name__ == "__main__":
    main()
