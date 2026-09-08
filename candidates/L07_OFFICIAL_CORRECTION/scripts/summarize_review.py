#!/usr/bin/env python3
"""Validate E000 manual labels and compute stratified yield estimates."""

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def interval(estimate: float, variance: float) -> list[float]:
    radius = 1.96 * math.sqrt(max(variance, 0.0))
    return [max(0.0, estimate - radius), min(1.0, estimate + radius)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config_path = args.config.resolve()
    project = config_path.parent.parent
    queue_path = project / "data/processed/e000/manual_review_queue.csv"
    labels_path = project / "data/annotations/e000/manual_labels.json"
    rows = list(csv.DictReader(queue_path.open(encoding="utf-8")))
    annotation = json.loads(labels_path.read_text(encoding="utf-8"))

    label_by_pmid = {}
    for label, pmids in annotation["labels"].items():
        for pmid in pmids:
            if pmid in label_by_pmid:
                raise ValueError(f"Duplicate manual label for PMID {pmid}")
            label_by_pmid[pmid] = label
    queue_pmids = {row["pmid"] for row in rows}
    if set(label_by_pmid) != queue_pmids:
        raise ValueError(f"Label coverage mismatch: missing={sorted(queue_pmids-set(label_by_pmid))}, extra={sorted(set(label_by_pmid)-queue_pmids)}")

    class_by_pmid = {}
    for correction_class, pmids in annotation["t1_classes"].items():
        for pmid in pmids:
            if pmid in class_by_pmid:
                raise ValueError(f"Duplicate T1 class for PMID {pmid}")
            class_by_pmid[pmid] = correction_class
    t1_pmids = set(annotation["labels"]["T1"])
    if set(class_by_pmid) != t1_pmids:
        raise ValueError("Every and only T1 record must have one correction class")

    annotated_path = project / "data/annotations/e000/manual_review.csv"
    fields = list(rows[0])
    with annotated_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            label = label_by_pmid[row["pmid"]]
            row["gold_label"] = label
            row["correction_class"] = class_by_pmid.get(row["pmid"], "")
            row["direct_old_new"] = "yes" if label == "T1" else "no"
            row["visual_required"] = "yes" if label == "T3_VISUAL" else "no"
            row["review_note"] = "Pending linked-original verification; excluded from confirmed yield." if label == "T2_PENDING" else ""
            writer.writerow(row)

    strata = defaultdict(list)
    for row in rows:
        strata[row["parser_category"]].append(label_by_pmid[row["pmid"]])
    population_sizes = {row["parser_category"]: int(row["stratum_size"]) for row in rows}
    population_sizes["notice_fulltext_unavailable"] = 145
    total = 500

    def estimate_for(positive_labels: set[str]) -> dict:
        estimate = 0.0
        variance = 0.0
        details = {}
        for stratum, population in population_sizes.items():
            labels = strata.get(stratum, [])
            if stratum == "notice_fulltext_unavailable":
                reviewed = population
                positives = 0
            else:
                reviewed = len(labels)
                positives = sum(label in positive_labels for label in labels)
            proportion = positives / reviewed if reviewed else 0.0
            weight = population / total
            estimate += weight * proportion
            if reviewed > 1 and reviewed < population:
                sample_variance = proportion * (1 - proportion) * reviewed / (reviewed - 1)
                variance += weight * weight * (1 - reviewed / population) * sample_variance / reviewed
            details[stratum] = {"population": population, "reviewed": reviewed, "positives": positives, "proportion": proportion}
        return {
            "proportion": estimate,
            "estimated_count_in_500": estimate * total,
            "normal_95_ci": interval(estimate, variance),
            "strata": details,
        }

    summary = {
        "reviewed_records": len(rows),
        "manual_label_counts": dict(Counter(label_by_pmid.values())),
        "t1_class_counts_in_review": dict(Counter(class_by_pmid.values())),
        "confirmed_t1_yield": estimate_for({"T1"}),
        "t1_plus_unverified_t2_ceiling": estimate_for({"T1", "T2_PENDING"}),
        "interpretation_warning": "T2_PENDING is an upper-bound component, not confirmed gold. The 95% interval is a stratified normal design-based interval, not a simple-random Wilson interval.",
    }
    output = project / "results/e000/manual_review_summary.json"
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
