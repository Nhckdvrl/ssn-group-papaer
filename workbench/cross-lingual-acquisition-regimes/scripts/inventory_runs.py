"""Freeze checksums and completeness of local exploratory probe outputs."""
import hashlib
import json
from pathlib import Path

from analyze_probe import read


def main():
    root = Path(__file__).resolve().parents[1]
    records = []
    for path in sorted((root / "artifacts").rglob("*.jsonl")):
        payload = path.read_bytes()
        metadata = json.loads(path.with_suffix(".meta.json").read_text())
        # The first two XNLI runs predate explicit expected_items metadata.
        rows = [json.loads(line) for line in payload.splitlines()]
        qa = bool(rows and "question_index" in rows[0])
        location = bool(rows and "context_language" in rows[0] and "swap" in rows[0])
        translation = bool(rows and "direction" in rows[0] and "generated_raw" in rows[0])
        if qa:
            identifiers = [(r["pair"], r["question_index"], r["context_lang"], r["question_lang"], r["answer_lang"]) for r in rows]
        elif location:
            identifiers = [(r["pair_id"], r["swap"], r["context_language"], r["answer_language"]) for r in rows]
        elif translation:
            identifiers = [(r["id"], r["direction"]) for r in rows]
        else:
            read(path)
            identifiers = [(r["id"], r["premise_lang"], r["choice_lang"]) for r in rows]
        if "expected_items" in metadata:
            assert len(rows) == metadata["expected_items"], path
        assert len(set(identifiers)) == len(rows), path
        if not translation:
            assert all(len(r["scores"]) == len(r["options"]) for r in rows), path
        records.append({"path": str(path.relative_to(root)), "sha256": hashlib.sha256(payload).hexdigest(),
                        "items": len(rows), "kind": "qa_binding" if qa else "location_binding" if location else "translation" if translation else "frozen_probe", "metadata": metadata})
    result = {"runs": records, "run_count": len(records),
              "item_cell_count": sum(r["items"] for r in records),
              "note": "Corrupted contexts and diagnostic formats counted; not independent questions."}
    output = root / "results" / "run_inventory.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "runs"}))


if __name__ == "__main__":
    main()
