#!/usr/bin/env python3
"""Create the frozen stratified human-review queue for E000."""

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config_path = args.config.resolve()
    project = config_path.parent.parent
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source = project / "data/processed/e000/notices.jsonl"
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    by_category = defaultdict(list)
    for row in rows:
        by_category[row["parser_category"]].append(row)

    rng = random.Random(config["review_seed"])
    selected = []
    for category, quota in config["review_quotas"].items():
        population = sorted(by_category[category], key=lambda row: row["pmid"])
        take = min(int(quota), len(population))
        for row in rng.sample(population, take):
            selected.append({**row, "stratum_size": len(population), "stratum_reviewed": take})
    selected.sort(key=lambda row: (row["parser_category"], row["pmid"]))

    output = project / "data/processed/e000/manual_review_queue.csv"
    fields = [
        "pmid", "pmcid", "parser_category", "stratum_size", "stratum_reviewed", "year", "journal", "title",
        "evidence_snippets", "source_pmc_url", "gold_label", "correction_class", "direct_old_new",
        "visual_required", "review_note",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in selected:
            writer.writerow({
                "pmid": row["pmid"], "pmcid": row["pmcid"], "parser_category": row["parser_category"],
                "stratum_size": row["stratum_size"], "stratum_reviewed": row["stratum_reviewed"],
                "year": row["year"], "journal": row["journal"], "title": row["title"],
                "evidence_snippets": " || ".join(row["evidence_snippets"]), "source_pmc_url": row["source_pmc_url"],
                "gold_label": "", "correction_class": "", "direct_old_new": "", "visual_required": "",
                "review_note": "",
            })
    print(json.dumps({
        "review_items": len(selected),
        "by_category": {key: sum(r["parser_category"] == key for r in selected) for key in config["review_quotas"]},
    }, indent=2))


if __name__ == "__main__":
    main()
