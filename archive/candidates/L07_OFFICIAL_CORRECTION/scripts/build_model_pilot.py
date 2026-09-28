#!/usr/bin/env python3
"""Build the E002 arbitration pilot from verified E001 operations and JATS.

No answer is generated here: questions and old/new candidates are human-checked
publisher quotations. The script only joins records and extracts bounded source
windows for model input.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

from audit_original_state import normalized, parse_pmc


def normalized_with_map(value: str) -> tuple[str, list[int]]:
    chars = []
    source_positions = []
    for index, char in enumerate(value):
        folded = unicodedata.normalize("NFKC", char).casefold()
        folded = folded.replace("±", " plusminus ").replace("−", " minus ")
        folded = folded.replace("–", " dash ").replace("—", " dash ").replace("+", " plus ").replace("-", " hyphen ")
        folded = folded.replace("μ", "u").replace("µ", "u")
        for out in folded:
            if out.isascii() and out.isalnum():
                chars.append(out)
                source_positions.append(index)
    return "".join(chars), source_positions


def source_window(source: str, selector: str, radius: int = 220) -> str:
    compact, positions = normalized_with_map(source)
    target = normalized(selector)
    start = compact.find(target)
    if start < 0:
        raise ValueError(f"Selector absent from source: {selector}")
    left = max(0, positions[start] - radius)
    right_index = min(len(positions) - 1, start + len(target) - 1)
    right = min(len(source), positions[right_index] + radius + 1)
    return " ".join(source[left:right].split())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    project = args.project.resolve()

    selectors_doc = json.loads((project / "data/annotations/e001/old_new_selectors.json").read_text())
    selectors = {item["correction_pmid"]: item for item in selectors_doc["pairs"]}
    state_doc = json.loads((project / "results/e001/original_state_audit.json").read_text())
    states = {item["correction_pmid"]: item for item in state_doc["items"]}
    questions_doc = json.loads((project / "data/annotations/e002/pilot_questions.json").read_text())
    questions = {item["correction_pmid"]: item["question"] for item in questions_doc["questions"]}
    notices = {
        item["pmid"]: item
        for item in map(json.loads, (project / "data/processed/e000/notices.jsonl").read_text().splitlines())
    }
    articles = parse_pmc(sorted((project / "data/raw/e001").glob("original_pmc_*.xml")))

    items = []
    for correction_pmid, question in questions.items():
        pair = selectors[correction_pmid]
        state = states[correction_pmid]
        if state["current_pmc_state"] not in {"old_only", "both"}:
            raise ValueError(f"Pilot item {correction_pmid} lacks old state in current PMC content")
        article = articles[pair["original_pmid"]]
        notice = notices[correction_pmid]
        old_excerpt = source_window(article["content_text"], pair["old"])
        snippets = notice["evidence_snippets"]
        ranked = sorted(
            snippets,
            key=lambda value: (
                normalized(pair["old"]) in normalized(value),
                pair["new"] == "[deleted]" or normalized(pair["new"]) in normalized(value),
                -len(value),
            ),
            reverse=True,
        )
        if not ranked:
            raise ValueError(f"No correction evidence for {correction_pmid}")
        items.append({
            "item_id": f"L07-{correction_pmid}",
            "correction_pmid": correction_pmid,
            "original_pmid": pair["original_pmid"],
            "original_pmcid": state["original_pmcid"],
            "current_pmc_state": state["current_pmc_state"],
            "location": pair["location"],
            "question": question,
            "old_candidate": pair["old"],
            "new_candidate": pair["new"],
            "original_excerpt": old_excerpt,
            "correction_excerpt": ranked[0],
            "original_source": f"https://pubmed.ncbi.nlm.nih.gov/{pair['original_pmid']}/",
            "correction_source": f"https://pubmed.ncbi.nlm.nih.gov/{correction_pmid}/",
        })

    output = project / "data/processed/e002/pilot_items.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items), encoding="utf-8")
    print(json.dumps({"items": len(items), "states": {s: sum(i["current_pmc_state"] == s for i in items) for s in {"old_only", "both"}}}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
