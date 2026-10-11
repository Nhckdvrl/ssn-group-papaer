#!/usr/bin/env python
"""Build a blinded annotation sheet for stimuli_v1.

Items are shuffled with a fixed seed and stripped of condition, gold and base id,
so the annotator cannot anchor on condition blocks. (Blinding is partial by
nature: a `before`-clause is visible in the passage itself. This is stated in the
audit rather than claimed away.)
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

SEED = 4013


def main():
    items = [json.loads(l) for l in open(os.path.join(PROJ, "data", "stimuli_v1.jsonl"), encoding="utf-8")]
    rng = random.Random(SEED)
    rng.shuffle(items)
    key, sheet = {}, []
    for i, it in enumerate(items, 1):
        aid = f"a{i:03d}"
        key[aid] = {"item_id": it["item_id"], "condition": it["condition"], "gold_strict": it["gold_strict"]}
        sheet.append({"aid": aid, "passage": it["passage"], "target": it["target"]})
    with open(os.path.join(PROJ, "data", "annotation_sheet.jsonl"), "w", encoding="utf-8") as f:
        for r in sheet:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(PROJ, "data", "annotation_key.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=2)
    print(f"{len(sheet)} items, seed {SEED}")


if __name__ == "__main__":
    main()
