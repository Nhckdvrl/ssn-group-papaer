"""Audit whether Curation-Bench's released ICONS mapping selects the intended rows.

Uses the original LLaVA JSON and the released ICONS JSON only. Full Arrow
position equivalence is checked separately by e12_index_audit.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def row_key(row: dict) -> str:
    raw = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    original = json.loads((args.root / "llava_json/llava_v1_5_mix665k.json").read_text())
    icons = json.loads((args.root / "icons_json/llava-icons-133k.json").read_text())

    exact_positions: dict[str, list[int]] = defaultdict(list)
    official_lookup: dict[str, int] = {}
    original_ids = Counter()
    image_positions = []
    for original_idx, row in enumerate(original):
        exact_positions[row_key(row)].append(original_idx)
        original_ids[str(row["id"])] += 1
        if "image" in row:
            image_positions.append(original_idx)
            arrow_idx_assumed = len(image_positions) - 1
            official_lookup[str(row["id"])] = arrow_idx_assumed
            official_lookup[str(row["image"])] = arrow_idx_assumed

    n_exact = n_ambiguous = n_missed = n_official_correct = n_official_wrong = 0
    official_selected = set()
    exact_selected = set()
    wrong_examples = []
    for row in icons:
        matches = exact_positions.get(row_key(row), [])
        if not matches:
            n_missed += 1
            continue
        n_exact += 1
        if len(matches) > 1:
            n_ambiguous += 1
        intended = matches[0]
        exact_selected.add(intended)
        found = official_lookup.get(str(row["id"])) or official_lookup.get(str(row.get("image", "")))
        if found is not None:
            official_selected.add(found)
        if found == intended:
            n_official_correct += 1
        else:
            n_official_wrong += 1
            if len(wrong_examples) < 10:
                wrong_examples.append({"id": row["id"], "intended_original_position": intended, "official_arrow_index": found})

    text_only_positions = [i for i, row in enumerate(original) if "image" not in row]
    report = {
        "original_rows": len(original),
        "original_unique_ids": len(original_ids),
        "original_ids_repeated": sum(c > 1 for c in original_ids.values()),
        "original_max_id_multiplicity": max(original_ids.values()),
        "image_rows": len(image_positions),
        "text_only_rows": len(text_only_positions),
        "first_text_only_position": min(text_only_positions),
        "last_image_position": max(image_positions),
        "icons_rows": len(icons),
        "icons_exact_original_record_matches": n_exact,
        "icons_ambiguous_exact_records": n_ambiguous,
        "icons_unmatched_full_records": n_missed,
        "official_mapping_exact_position_matches": n_official_correct,
        "official_mapping_wrong_or_missing": n_official_wrong,
        "official_mapping_unique_positions": len(official_selected),
        "intended_unique_positions": len(exact_selected),
        "official_intended_position_overlap": len(official_selected & exact_selected),
        "first_wrong_examples": wrong_examples,
        "qualification": "Official positions are compared with original JSON positions; validate Arrow order independently.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
