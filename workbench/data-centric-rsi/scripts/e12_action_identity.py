"""E12 CPU-only check that frozen 10k strategies are distinct data actions."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from e12_make_subsets import POLICIES, hash_lines, policies_from_sources, select_positions


def source(row: dict) -> str:
    return str(row.get("image", "text-only")).split("/", 1)[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    original = json.loads((args.root / "llava_json/llava_v1_5_mix665k.json").read_text())
    pools = policies_from_sources(original, args.root)
    selected = {name: set(select_positions(original, pools, name, args.seed)) for name in POLICIES}
    report = {"seed": args.seed, "policies": {}, "pairwise": {}}
    for name, positions in selected.items():
        report["policies"][name] = {
            "pool_rows": len(pools[name]),
            "selected_rows": len(positions),
            "positions_sha256": hash_lines([str(i) for i in sorted(positions)]),
            "source_counts": dict(sorted(Counter(source(original[i]) for i in positions).items())),
        }
    for a in POLICIES:
        report["pairwise"][a] = {}
        for b in POLICIES:
            overlap = len(selected[a] & selected[b])
            report["pairwise"][a][b] = {
                "overlap_rows": overlap,
                "overlap_fraction_of_10k": overlap / 10000,
                "jaccard": overlap / (20000 - overlap),
            }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
