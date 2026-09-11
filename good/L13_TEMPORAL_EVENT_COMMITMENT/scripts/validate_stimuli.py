#!/usr/bin/env python
"""Structural validation of data/stimuli_v1.jsonl.

Fails loudly if any invariant of DATA_AND_GOLD.md is violated.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

CONDS = [
    "after",
    "before_neutral",
    "before_confirm",
    "before_cancel",
    "nontemporal_neutral",
]


def main():
    version = os.environ.get("L13_STIMULI_VERSION", "stimuli_v1")
    path = os.path.join(PROJ, "data", f"{version}.jsonl")
    items = [json.loads(l) for l in open(path, encoding="utf-8")]
    ext = [json.loads(l) for l in open(os.path.join(PROJ, "data", f"{version}_ext.jsonl"), encoding="utf-8")]
    for it in ext:
        p = it["passage"]
        if not p.endswith(".") or "  " in p:
            print(f"EXT MALFORMED: {it['item_id']}")
            sys.exit(1)
        if it["condition"] == "before_modal" and " could " not in p:
            print(f"EXT missing modal: {it['item_id']}")
            sys.exit(1)
        if it["condition"] == "about_to" and " about to " not in p:
            print(f"EXT missing construction: {it['item_id']}")
            sys.exit(1)
        if it["condition"] == "purpose" and " there to " not in p:
            print(f"EXT missing purpose construction: {it['item_id']}")
            sys.exit(1)
        for bad in (" The engineers was ", " The students was ", " The volunteers was "):
            if bad in " " + p:
                print(f"EXT agreement error: {it['item_id']}")
                sys.exit(1)
    print(f"extension items: {len(ext)} ok")
    by_base = collections.defaultdict(dict)
    for it in items:
        by_base[it["base_id"]][it["condition"]] = it

    errors = []
    if len(items) != len(by_base) * len(CONDS):
        errors.append(f"item count {len(items)} != bases*conds")

    seen_passages = collections.Counter(it["passage"] for it in items)
    for p, c in seen_passages.items():
        if c > 1:
            errors.append(f"duplicate passage: {p!r}")

    for base_id, conds in by_base.items():
        missing = [c for c in CONDS if c not in conds]
        if missing:
            errors.append(f"{base_id}: missing conditions {missing}")
            continue

        a = conds["after"]["passage"]
        b = conds["before_neutral"]["passage"]
        # minimal-pair invariant: identical except the leading connective
        if a.split(" ", 1)[1:] != b.split(" ", 1)[1:]:
            errors.append(f"{base_id}: after/before_neutral not a minimal pair")
        if not (a.startswith("After ") and b.startswith("Before ")):
            errors.append(f"{base_id}: connective prefix wrong")

        # the resolved conditions must literally extend before_neutral
        for c in ("before_confirm", "before_cancel"):
            if not conds[c]["passage"].startswith(b + " "):
                errors.append(f"{base_id}: {c} does not extend before_neutral")

        # invariant probe string
        targets = {conds[c]["target"] for c in CONDS}
        if len(targets) != 1:
            errors.append(f"{base_id}: target string varies across conditions")
        target = targets.pop()
        # target must be the subordinate clause, modulo capitalisation
        sub = b[len("Before "):].split(",")[0]
        if target[:-1].lower() != sub.lower():
            errors.append(f"{base_id}: target {target!r} != subordinate clause {sub!r}")

        # the non-temporal control must not contain a temporal connective
        nt = conds["nontemporal_neutral"]["passage"].lower()
        for w in ("before", "after", "until", "when", "once"):
            if f" {w} " in f" {nt} ":
                errors.append(f"{base_id}: nontemporal control contains {w!r}")

        for c in CONDS:
            p = conds[c]["passage"]
            if not p.endswith("."):
                errors.append(f"{base_id}/{c}: passage does not end with a period")
            if "  " in p:
                errors.append(f"{base_id}/{c}: double space")

    gold_counts = collections.Counter(it["gold_strict"] for it in items)
    print(f"items: {len(items)}  bases: {len(by_base)}")
    print(f"gold distribution: {dict(gold_counts)}")
    if errors:
        print(f"\nFAILED with {len(errors)} error(s):")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("all structural invariants hold")


if __name__ == "__main__":
    main()
