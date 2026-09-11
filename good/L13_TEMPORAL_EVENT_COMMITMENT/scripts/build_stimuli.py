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
from stimuli_ext import EXT_GOLD, ext_passages  # noqa: E402

VERSION = "stimuli_v1"

GOLD = {
    **EXT_GOLD,
    "after": "YES",
    "before_neutral": "NOT_DETERMINED",
    "before_confirm": "YES",
    "before_cancel": "NO",
    "nontemporal_neutral": "NOT_DETERMINED",
}


def passages(base):  # noqa: D401
    after = f"After {base['sub']}, {base['main']}."
    before = f"Before {base['sub']}, {base['main']}."
    return {
        "after": after,
        "before_neutral": before,
        "before_confirm": f"{before} {base['confirm']}",
        "before_cancel": f"{before} {base['cancel']}",
        "nontemporal_neutral": f"{base['plan']} {base['main_alone']}",
        **ext_passages(base),
    }


CORE_CONDS = ("after", "before_neutral", "before_confirm", "before_cancel", "nontemporal_neutral")


def main():
    # stimuli_v1 stays frozen at the five core conditions so that the recorded
    # results and raw outputs keep corresponding to it; E12's two extension
    # conditions are written to a separate file.
    out_path = os.path.join(PROJ, "data", f"{VERSION}.jsonl")
    ext_path = os.path.join(PROJ, "data", f"{VERSION}_ext.jsonl")
    n = ext_n = 0
    with open(out_path, "w", encoding="utf-8") as f, open(ext_path, "w", encoding="utf-8") as g:
        for base in BASES:
            ps = passages(base)
            for cond, passage in ps.items():
                item = {
                    "version": VERSION,
                    "item_id": f"{base['id']}_{cond}",
                    "base_id": base["id"],
                    "condition": cond,
                    "connective": {
                        "about_to": "when",
                        "before_modal": "before_could",
                        "after": "after",
                        "before_neutral": "before",
                        "before_confirm": "before",
                        "before_cancel": "before",
                        "nontemporal_neutral": "none",
                    }[cond],
                    "resolution": {
                        "about_to": "none",
                        "before_modal": "modal_marked",
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
                if cond in CORE_CONDS:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                    n += 1
                else:
                    g.write(json.dumps(item, ensure_ascii=False) + "\n")
                    ext_n += 1
    print(f"wrote {n} core items to {out_path}")
    print(f"wrote {ext_n} extension items to {ext_path}")


if __name__ == "__main__":
    main()
