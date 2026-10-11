"""Check whether the available LLaVA Arrow snapshot preserves original JSON IDs/order.

Read-only source audit for E12. Images are not decoded and no policy is selected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import pyarrow as pa
from datasets import DatasetDict, concatenate_datasets, load_from_disk


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def expected_turns(row: dict) -> list[dict[str, str]] | None:
    conversation = row.get("conversations", [])
    if len(conversation) % 2:
        return None
    return [
        {
            "user": conversation[i]["value"].replace("<image>", "").strip(),
            "assistant": conversation[i + 1]["value"].strip(),
        }
        for i in range(0, len(conversation), 2)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--first-shard", action="store_true", help="Audit only the first downloaded Arrow shard")
    args = parser.parse_args()
    arrow_path = args.root / "llava_arrow"
    json_path = args.root / "llava_json" / "llava_v1_5_mix665k.json"
    original = json.loads(json_path.read_text())
    original_ids = [str(row["id"]) for row in original]
    if args.first_shard:
        shard_path = arrow_path / "data-00000-of-00054.arrow"
        with pa.memory_map(str(shard_path), "r") as source:
            table = pa.ipc.open_stream(source).read_all()
        arrow_ids = [str(x) for x in table.column("id").to_pylist()]
        arrow_subsets = Counter(str(x) for x in table.column("subset").to_pylist())
        arrow_texts = table.column("texts").to_pylist()
        columns = table.column_names
        features = str(table.schema)
        comparison_ids = original_ids[: len(arrow_ids)]
    else:
        ds = load_from_disk(str(arrow_path))
        if isinstance(ds, DatasetDict):
            ds = concatenate_datasets([ds[k] for k in sorted(ds)])
        arrow_ids = [str(x) for x in ds["id"]]
        arrow_subsets = Counter(str(x) for x in ds["subset"])
        arrow_texts = list(ds["texts"])
        columns = list(ds.column_names)
        features = str(ds.features)
        comparison_ids = original_ids
        if len(original_ids) != len(arrow_ids):
            raise ValueError(f"row mismatch: original={len(original_ids)} arrow={len(arrow_ids)}")
    original_count = Counter(original_ids)
    arrow_count = Counter(arrow_ids)
    matches = sum(a == b for a, b in zip(comparison_ids, arrow_ids))
    content_matches = sum(expected_turns(row) == texts for row, texts in zip(original, arrow_texts))
    first_mismatches = [
        {"row": i, "original_id": a, "arrow_id": b}
        for i, (a, b) in enumerate(zip(comparison_ids, arrow_ids)) if a != b
    ][:10]
    report = {
        "first_shard_only": args.first_shard,
        "source_json_sha256": sha256(json_path),
        "source_arrow_path": str(arrow_path),
        "original_rows": len(original_ids),
        "arrow_rows": len(arrow_ids),
        "original_unique_ids": len(original_count),
        "arrow_unique_ids": len(arrow_count),
        "same_id_multiset": None if args.first_shard else original_count == arrow_count,
        "same_position_count": matches,
        "same_position_fraction": matches / len(arrow_ids),
        "same_position_conversation_count": content_matches,
        "same_position_conversation_fraction": content_matches / len(arrow_ids),
        "first_position_mismatches": first_mismatches,
        "arrow_subsets": dict(sorted(arrow_subsets.items())),
        "columns": columns,
        "features": features,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "features"}, indent=2))


if __name__ == "__main__":
    main()
