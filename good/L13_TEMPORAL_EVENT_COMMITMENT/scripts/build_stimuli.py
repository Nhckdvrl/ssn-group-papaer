#!/usr/bin/env python
"""Build data/stimuli_v1.jsonl from the hand-authored bases.

Deterministic: no randomness, no model in the loop.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))

from stimuli_bases import BASES  # noqa: E402

VERSION = "stimuli_v1"

GOLD = {
    "after": "YES",
    "before_neutral": "NOT_DETERMINED",
    "before_confirm": "YES",
    "before_cancel": "NO",
    "nontemporal_neutral": "NOT_DETERMINED",
}


def passages(base):
    after = f"After {base['sub']}, {base['main']}."
    before = f"Before {base['sub']}, {base['main']}."
    return {
        "after": after,
        "before_neutral": before,
        "before_confirm": f"{before} {base['confirm']}",
        "before_cancel": f"{before} {base['cancel']}",
        "nontemporal_neutral": f"{base['plan']} {base['main_alone']}",
    }


def main():
    out_path = os.path.join(PROJ, "data", f"{VERSION}.jsonl")
    n = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for base in BASES:
            ps = passages(base)
            for cond, passage in ps.items():
                item = {
                    "version": VERSION,
                    "item_id": f"{base['id']}_{cond}",
                    "base_id": base["id"],
                    "condition": cond,
                    "connective": {
                        "after": "after",
                        "before_neutral": "before",
                        "before_confirm": "before",
                        "before_cancel": "before",
                        "nontemporal_neutral": "none",
                    }[cond],
                    "resolution": {
                        "after": "none",
                        "before_neutral": "none",
                        "before_confirm": "confirm",
                        "before_cancel": "cancel",
                        "nontemporal_neutral": "none",
                    }[cond],
                    "passage": passage,
                    "target": base["target"] + ".",
                    "main_event": base["main_alone"]
                    if cond == "nontemporal_neutral"
                    else base["main"][0].upper() + base["main"][1:] + ".",
                    "pragmatic_bias": base["pragmatic_bias"],
                    "gold_strict": GOLD[cond],
                }
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                n += 1
    print(f"wrote {n} items to {out_path}")


if __name__ == "__main__":
    main()
