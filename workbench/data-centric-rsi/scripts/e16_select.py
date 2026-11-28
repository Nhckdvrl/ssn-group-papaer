"""E16 stage 0: stratified choice of 100 problems (by Codeforces rating bins) and a 10-problem pilot subset.
Only problems with at least one human WA bug are in problems.jsonl already (see e16_prepare.py).
Usage: python3 e16_select.py --src problems.jsonl --n 100 --pilot 10
"""
import argparse
import json
import random

BINS = [(0, 1199), (1200, 1599), (1600, 1999), (2000, 2399), (2400, 9999)]

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True); ap.add_argument("--n", type=int, default=100)
ap.add_argument("--pilot", type=int, default=10)
a = ap.parse_args()
probs = [json.loads(l) for l in open(a.src)]
rng = random.Random(20261128)
by = {b: sorted([p for p in probs if b[0] <= (p["cf_rating"] or 0) <= b[1]], key=lambda p: p["id"]) for b in BINS}
for b in by:
    rng.shuffle(by[b])
chosen, i = [], 0
while len(chosen) < min(a.n, len(probs)):          # round-robin over bins keeps the rating mix balanced
    b = BINS[i % len(BINS)]
    if by[b]:
        chosen.append(by[b].pop())
    i += 1
    if all(not v for v in by.values()):
        break
pilot = [chosen[k] for k in range(0, len(chosen), max(1, len(chosen) // a.pilot))][: a.pilot]
base = a.src.rsplit(".", 1)[0]
for name, rows in [(f"{base}_{len(chosen)}.jsonl", chosen), (f"{base}_pilot{len(pilot)}.jsonl", pilot)]:
    with open(name, "w") as f:
        for p in rows:
            f.write(json.dumps(p) + "\n")
    print(name, len(rows), "ratings", sorted(p["cf_rating"] for p in rows)[:: max(1, len(rows) // 10)],
          "with_mutants", sum(1 for p in rows if p["mutants"]))
