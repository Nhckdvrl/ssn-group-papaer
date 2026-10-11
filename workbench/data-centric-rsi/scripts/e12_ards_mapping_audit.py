"""Check ARDS global_id against the pinned original LLaVA JSON before E12 GPU use."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def digest(row: dict) -> str:
    body = {k: row.get(k) for k in ("id", "image", "conversations")}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    original = json.loads((args.root / "llava_json/llava_v1_5_mix665k.json").read_text())
    ards = json.loads((args.root / "ards_selected.json").read_text())
    selected_positions: set[int] = set()
    counts = Counter()
    offset_counts = {str(offset): Counter() for offset in (-2, -1, 0, 1, 2)}
    mismatches = []
    unexpected_keys = Counter()
    for row in ards:
        unexpected_keys.update(set(row) - {"global_id", "id", "image", "conversations"})
        try:
            position = int(row["global_id"]) - 1
        except (KeyError, TypeError, ValueError):
            counts["invalid_global_id"] += 1
            continue
        if not 0 <= position < len(original):
            counts["out_of_range"] += 1
            continue
        selected_positions.add(position)
        target = original[position]
        for offset in (-2, -1, 0, 1, 2):
            pos = int(row["global_id"]) + offset
            if not 0 <= pos < len(original):
                offset_counts[str(offset)]["out_of_range"] += 1
                continue
            candidate = original[pos]
            if digest(row) == digest(candidate):
                offset_counts[str(offset)]["full_record"] += 1
            if str(row.get("id")) == str(candidate.get("id")) and row.get("image") == candidate.get("image"):
                offset_counts[str(offset)]["id_and_image"] += 1
        if digest(row) == digest(target):
            counts["exact_full_record"] += 1
        elif str(row.get("id")) == str(target.get("id")) and row.get("image") == target.get("image"):
            counts["same_id_and_image_different_content"] += 1
        else:
            counts["different_id_or_image"] += 1
        if len(mismatches) < 10 and digest(row) != digest(target):
            mismatches.append({
                "global_id": row.get("global_id"),
                "released_id": row.get("id"),
                "original_id_at_position": target.get("id"),
                "released_image": row.get("image"),
                "original_image_at_position": target.get("image"),
            })
    report = {
        "original_rows": len(original),
        "ards_rows": len(ards),
        "unique_valid_positions": len(selected_positions),
        "counts": dict(counts),
        "candidate_global_id_offsets": {key: dict(value) for key, value in offset_counts.items()},
        "unexpected_keys": dict(unexpected_keys),
        "first_mismatches": mismatches,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
