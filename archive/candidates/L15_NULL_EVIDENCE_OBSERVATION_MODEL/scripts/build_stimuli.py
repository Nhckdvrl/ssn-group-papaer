#!/usr/bin/env python3
"""Deterministically materialise the L15 pilot items and prompt cells."""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stimuli import build_items
from prompts import build_cells

def main() -> None:
    out = ROOT / "data"
    out.mkdir(exist_ok=True)
    items = build_items()
    with (out / "items.jsonl").open("w") as f:
        for row in items:
            f.write(json.dumps(row) + "\n")
    cells = build_cells()
    with (out / "cells.jsonl").open("w") as f:
        for row in cells:
            f.write(json.dumps(row) + "\n")
    print(f"items={len(items)} cells={len(cells)} -> {out}")

if __name__ == "__main__":
    main()
