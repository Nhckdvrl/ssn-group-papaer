#!/usr/bin/env python3
"""Extract high-precision old/new proposals from E003 notices for review.

Outputs are proposals, never gold. Each accepted item still requires direct
notice verification and linked-original state verification.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from audit_original_state import normalized


QUOTE = r'"([^"]{2,600})"'
PATTERNS = [
    (
        "old_should_read_new",
        re.compile(QUOTE + r"\s*(?:,|\.)?\s*(?:which\s+)?should\s+(?:instead\s+)?read\s*:?[\s\n]*" + QUOTE, re.I),
        (1, 2),
    ),
    (
        "new_instead_of_old",
        re.compile(r"should\s+(?:instead\s+)?(?:read|be)\s*:?[\s\n]*" + QUOTE + r"\s*(?:,|\.)?\s*instead\s+of\s*" + QUOTE, re.I),
        (2, 1),
    ),
    (
        "old_corrected_to_new",
        re.compile(QUOTE + r".{0,100}?(?:has\s+been|was|is)\s+corrected\s+(?:to|as|to\s+read)\s*" + QUOTE, re.I | re.S),
        (1, 2),
    ),
    (
        "old_should_be_corrected_to_new",
        re.compile(QUOTE + r".{0,100}?(?:it\s+|which\s+)?should\s+be\s+corrected\s+to\s*" + QUOTE, re.I | re.S),
        (1, 2),
    ),
    (
        "new_rather_than_old",
        re.compile(r"should\s+(?:be|read)\s*:?[\s\n]*" + QUOTE + r"\s*(?:,|\.)?\s*rather\s+than\s*" + QUOTE, re.I),
        (2, 1),
    ),
    (
        "old_replaced_with_new",
        re.compile(QUOTE + r"\s*should\s+be\s+(?:replaced|changed)\s+(?:by|with|to)\s*" + QUOTE, re.I),
        (1, 2),
    ),
    (
        "from_old_to_new",
        re.compile(r"(?:changed|corrected|updated)\s+from\s*" + QUOTE + r"\s+to\s*" + QUOTE, re.I),
        (1, 2),
    ),
    (
        "old_incorrect_new_correct",
        re.compile(
            r"(?:incorrect(?:ly)?\s+(?:given|listed|reported|written|printed|spelled|stated)?\s*(?:as|was|is)?|"
            r"erroneously\s+(?:given|listed|reported|written|printed|spelled|stated)?\s*(?:as|was|is)?)\s*:?"
            + QUOTE
            + r".{0,260}?(?:correct(?:ed)?(?:\s+(?:value|text|term|name|version))?\s*(?:is|was|to|as|should\s+be)?|"
            r"should\s+(?:read|be))\s*:?"
            + QUOTE,
            re.I | re.S,
        ),
        (1, 2),
    ),
]


def clean(value: str) -> str:
    return " ".join(value.split()).strip(" ,;:.")


def proposals(text: str) -> list[dict]:
    text = text.replace("“", '"').replace("”", '"').replace("‘", '"').replace("’", '"')
    output = []
    for name, pattern, groups in PATTERNS:
        for match in pattern.finditer(text):
            old = clean(match.group(groups[0]))
            new = clean(match.group(groups[1]))
            if not old or not new or normalized(old) == normalized(new):
                continue
            output.append({
                "pattern": name,
                "old": old,
                "new": new,
                "evidence": " ".join(match.group(0).split()),
            })
    unique = {}
    for item in output:
        unique[(normalized(item["old"]), normalized(item["new"]))] = item
    return list(unique.values())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    project = args.project.resolve()
    source = project / "data/processed/e003/notices.jsonl"
    rows = list(map(json.loads, source.read_text(encoding="utf-8").splitlines()))

    extracted = []
    for row in rows:
        if row["parser_category"] != "exact_replacement_candidate":
            continue
        text = " ⟦BLOCK⟧ ".join(row["blocks"])
        for index, item in enumerate(proposals(text), 1):
            extracted.append({
                "candidate_id": f"{row['pmid']}-{index:02d}",
                "correction_pmid": row["pmid"],
                "correction_pmcid": row["pmcid"],
                "original_pmids": [ref["pmid"] for ref in row["erratum_for"] if ref["pmid"]],
                "year": row["year"],
                "journal": row["journal"],
                "title": row["title"],
                **item,
                "source_pmc_url": row["source_pmc_url"],
                "review_label": "",
                "review_note": "",
            })

    output_dir = project / "data/processed/e003"
    jsonl = output_dir / "pair_candidates.jsonl"
    jsonl.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in extracted),
        encoding="utf-8",
    )
    csv_path = output_dir / "pair_candidates.csv"
    fields = [
        "candidate_id", "correction_pmid", "correction_pmcid", "original_pmids",
        "year", "journal", "title", "pattern", "old", "new", "evidence",
        "source_pmc_url", "review_label", "review_note",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in extracted:
            writer.writerow({**row, "original_pmids": "|".join(row["original_pmids"])})

    manifest = {
        "exact_notice_records": sum(row["parser_category"] == "exact_replacement_candidate" for row in rows),
        "records_with_extracted_pairs": len({row["correction_pmid"] for row in extracted}),
        "extracted_pair_candidates": len(extracted),
        "pattern_counts": dict(Counter(row["pattern"] for row in extracted)),
        "warning": "All outputs are review proposals, not gold.",
    }
    (project / "results/e003/pair_extraction_summary.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
