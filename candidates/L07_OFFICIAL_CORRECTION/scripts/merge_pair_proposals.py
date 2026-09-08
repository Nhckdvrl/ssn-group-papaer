#!/usr/bin/env python3
"""Merge deterministic and LLM recall proposals into a deduplicated review queue."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from audit_original_state import normalized


def main() -> None:
    project = Path(__file__).resolve().parent.parent
    processed = project / "data/processed/e003"
    sources = {
        "rule": processed / "pair_candidates.jsonl",
        "llm": processed / "llm_pair_proposals.jsonl",
    }
    available_sources = {method: path for method, path in sources.items() if path.exists()}
    if not available_sources:
        raise FileNotFoundError("No E003 proposal source exists; run an extractor first")
    merged = {}
    for method, path in available_sources.items():
        for row in map(json.loads, path.read_text(encoding="utf-8").splitlines()):
            key = (row["correction_pmid"], normalized(row["old"]), normalized(row["new"]))
            if key not in merged:
                merged[key] = {**row, "proposal_methods": [method]}
            elif method not in merged[key]["proposal_methods"]:
                merged[key]["proposal_methods"].append(method)

    rows = sorted(merged.values(), key=lambda row: (row["correction_pmid"], row["candidate_id"]))
    jsonl_path = processed / "pair_review_queue.jsonl"
    jsonl_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    csv_path = processed / "pair_review_queue.csv"
    fields = [
        "candidate_id", "correction_pmid", "correction_pmcid", "original_pmids",
        "year", "journal", "title", "proposal_methods", "old", "new", "location",
        "evidence", "source_pmc_url", "review_label", "review_note",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                field: "|".join(row.get(field, [])) if field in {"original_pmids", "proposal_methods"} else row.get(field, "")
                for field in fields
            })
    summary = {
        "available_sources": sorted(available_sources),
        "missing_optional_sources": sorted(set(sources) - set(available_sources)),
        "unique_proposals": len(rows),
        "unique_notices": len({row["correction_pmid"] for row in rows}),
        "method_membership": dict(Counter(method for row in rows for method in row["proposal_methods"])),
        "review_status": "all pending; proposals are not gold",
    }
    (project / "results/e003/pair_review_queue_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
