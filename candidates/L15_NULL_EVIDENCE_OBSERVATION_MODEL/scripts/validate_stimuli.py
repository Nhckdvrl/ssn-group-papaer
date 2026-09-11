#!/usr/bin/env python3
"""Structural invariants required by DATA_AND_GOLD.md.

Fails loudly rather than letting a malformed grid reach a model.
"""
import json, sys, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stimuli import PRIORS, SENSITIVITIES, posterior_null, likelihood_null_given_h, pct

def load(name):
    with (ROOT / "data" / name).open() as f:
        return [json.loads(l) for l in f if l.strip()]

def fail(msg):
    print("FAIL:", msg); sys.exit(1)

def main():
    items = load("items.jsonl")
    cells = load("cells.jsonl")

    if len(items) != 12 * len(PRIORS) * len(SENSITIVITIES):
        fail(f"item count {len(items)}")
    if len({i["item_id"] for i in items}) != len(items):
        fail("duplicate item_id")

    for i in items:
        if abs(i["gold_p1"] - likelihood_null_given_h(i["s"])) > 1e-12:
            fail(f"gold_p1 {i['item_id']}")
        if abs(i["gold_p2"] - posterior_null(i["p"], i["s"])) > 1e-12:
            fail(f"gold_p2 {i['item_id']}")
        if i["f"] != 0.0:
            fail("primary grid must use f=0")

    # gold posterior must be strictly decreasing in s at fixed p
    for p in PRIORS:
        golds = [posterior_null(p, s) for s in SENSITIVITIES]
        if any(a <= b for a, b in zip(golds, golds[1:])):
            fail(f"gold not monotone at p={p}")

    by = collections.defaultdict(list)
    for c in cells:
        by[(c["condition"], c["mode"])].append(c)

    # the visible outcome sentence must be identical across the sensitivity grid
    for (cond, mode), rows in by.items():
        if cond not in ("P1_NULL", "P2_NULL", "P3_DECIDE"):
            continue
        groups = collections.defaultdict(set)
        for c in rows:
            sc, w, p = c["scenario"], c["wording"], c["p"]
            outcome = c["prompt"].split("\n\n")[0].split(". ")[-1]
            groups[(sc, w, p)].add(outcome)
        for k, v in groups.items():
            if len(v) != 1:
                fail(f"visible outcome varies with s for {cond}/{mode}/{k}: {v}")

    # every probability the item needs must be printed in the item text
    for c in cells:
        if c["condition"] in ("P1_NULL", "P2_NULL", "P2_POS", "P3_DECIDE"):
            for want in (pct(c["p"]), pct(c["s"]), pct(1 - c["s"])):
                if want not in c["prompt"]:
                    fail(f"{c['cell_id']} missing stated probability {want}")
        if c["condition"] == "P2_HANDED":
            if pct(1 - c["s"]) not in c["prompt"]:
                fail(f"{c['cell_id']} missing handed likelihood")
            if "% of the time" in c["prompt"]:
                fail(f"{c['cell_id']} handed condition must not restate the rate form")

    # no cell may be empty or duplicated
    if len({c["cell_id"] for c in cells}) != len(cells):
        fail("duplicate cell_id")

    frames = collections.Counter(i["frame"] for i in items)
    nonmed = [f for f in frames if f != "diagnostic"]
    if len(nonmed) < 3:
        fail("fewer than three non-medical frames")

    print(f"OK  items={len(items)}  cells={len(cells)}  frames={dict(frames)}")
    print("    conditions x modes:", {f"{k[0]}/{k[1]}": len(v) for k, v in sorted(by.items())})

if __name__ == "__main__":
    main()
