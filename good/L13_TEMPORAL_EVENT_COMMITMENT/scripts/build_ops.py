#!/usr/bin/env python
"""Build data/stimuli_ops.jsonl — the E19 operator battery."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))

from stimuli_bases import BASES  # noqa: E402
from stimuli_ops import OP_GOLD, op_passages  # noqa: E402
from stimuli_surface import SURFACE_FORM, SURFACE_GOLD, surface_passages  # noqa: E402


def main():
    out = os.path.join(PROJ, "data", "stimuli_ops.jsonl")
    out_s = os.path.join(PROJ, "data", "stimuli_surface.jsonl")
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for base in BASES:
            for cond, passage in op_passages(base).items():
                f.write(
                    json.dumps(
                        {
                            "version": "stimuli_ops",
                            "item_id": f"{base['id']}_{cond}",
                            "base_id": base["id"],
                            "condition": cond,
                            "operator": cond.replace("op_", ""),
                            "passage": passage,
                            "target": base["target"] + ".",
                            "main_event": base["main"][0].upper() + base["main"][1:] + ".",
                            "gold_strict": OP_GOLD[cond],
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                n += 1
    print(f"wrote {n} items to {out}")

    m = 0
    with open(out_s, "w", encoding="utf-8") as f:
        for base in BASES:
            for cond, passage in surface_passages(base).items():
                f.write(
                    json.dumps(
                        {
                            "version": "stimuli_surface",
                            "item_id": f"{base['id']}_{cond}",
                            "base_id": base["id"],
                            "condition": cond,
                            "surface_form": SURFACE_FORM[cond],
                            "passage": passage,
                            "target": base["target"] + ".",
                            "main_event": base["main"][0].upper() + base["main"][1:] + ".",
                            "gold_strict": SURFACE_GOLD[cond],
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                m += 1
    print(f"wrote {m} items to {out_s}")


if __name__ == "__main__":
    main()
