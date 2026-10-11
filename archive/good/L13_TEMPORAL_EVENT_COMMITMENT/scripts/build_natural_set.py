#!/usr/bin/env python
"""E08: the hand-adjudicated natural `before` set.

Sentences are verbatim from the Pile (via NeelNanda/pile-10k); only selection and
the target proposition are authored. Adjudication is recorded in
`data/NATURAL_SET_AUDIT.md`.

`gold_realized`:
  False - the sentence indicates the subordinate event did not occur
  True  - the sentence indicates it did occur
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

PREVENTED = [
    ("n015", "I made it out of the kitchen."),
    ("n028", "I spiralled down into another unhelpful panic attack."),
    ("n032", "He answered."),
    ("n033", "I figured it out."),
    ("n034", "I cried."),
    ("n036", "I stopped it."),
    ("n039", "The thoughts took hold."),
    ("n042", "Nathan argued."),
    ("n044", "He remembered his attack."),
    ("n047", "Christian reacted."),
    ("n050", "I got in the way."),
    ("n053", "Mark retaliated."),
    ("n063", "He said something."),
    ("n072", "Jamie said something."),
    ("n078", "The gun fell to the ground."),
    ("n080", "He did something else."),
    ("n131", "The defendant responded."),
    ("n182", "I got there."),
    ("n191", "The moves developed into something more tangible."),
]

# plain past tense in the before-clause, yet still prevented: the surface cue
# `could` is not what makes a natural before-clause non-veridical
PREVENTED_PLAIN = [
    ("n040", "I reached the third sentence."),
    ("n049", "We reached the halo of light that emanated from the porch."),
    ("n051", "I reached the trees."),
]

VERIDICAL = [
    ("n002", "He popped the question."),
    ("n007", "They moved to Arkansas as a couple."),
    ("n011", "I picked up the piece of wood."),
    ("n014", "He stopped the car."),
    ("n024", "We headed to the dog park."),
    ("n025", "I reached the first bush."),
    ("n027", "I started to wonder about Friday."),
    ("n029", "I realized that he wasn't moving."),
    ("n030", "I regretted not going with her."),
    ("n045", "I realized that Heavenly Father didn't think I was damaged."),
    ("n046", "I closed mine."),
    ("n054", "She obtained the 9471 loan."),
    ("n058", "She violated the four person occupancy limit."),
]


def main():
    cands = {
        j["cand_id"]: j
        for j in (
            json.loads(l)
            for l in open(
                os.path.join(PROJ, "data", "natural_before_candidates.jsonl"), encoding="utf-8"
            )
        )
    }
    rows = []
    for group, realized, cue in (
        (PREVENTED, False, "modal"),
        (PREVENTED_PLAIN, False, "plain_past"),
        (VERIDICAL, True, "plain_past"),
    ):
        for cid, target in group:
            rows.append(
                {
                    "item_id": cid,
                    "base_id": cid,
                    "passage": cands[cid]["sentence"],
                    "target": target,
                    "gold_realized": realized,
                    "clause_cue": cue,
                    "condition": "natural_prevented" if not realized else "natural_veridical",
                    "gold_strict": "YES" if realized else "NO",
                    "source": cands[cid]["source"],
                }
            )
    path = os.path.join(PROJ, "data", "natural_before_v1.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} items ({sum(1 for r in rows if not r['gold_realized'])} prevented) -> {path}")


if __name__ == "__main__":
    main()
