#!/usr/bin/env python3
"""Collect an E000-disjoint correction-notice expansion from the frozen frame."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from run_yield_audit import (
    Client,
    chunks,
    classify,
    evidence_snippets,
    extract_notice_articles,
    parse_pubmed,
    save_response,
    sha256,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    project = args.config.resolve().parent.parent
    config = json.loads(args.config.read_text(encoding="utf-8"))
    frame = json.loads((project / "data/raw/e000/sampling_frame.json").read_text(encoding="utf-8"))
    excluded = set(frame["sampled_pmids"])
    eligible = [pmid for pmid in frame["eligible_pmids"] if pmid not in excluded]
    candidate_count = int(config["sample_size"]) + int(config["reserve_size"])
    candidates = random.Random(config["seed"]).sample(eligible, candidate_count)

    raw = project / "data/raw/e003"
    processed = project / "data/processed/e003"
    results = project / "results/e003"
    for directory in (raw, processed, results):
        directory.mkdir(parents=True, exist_ok=True)
    client = Client(config)
    pubmed_paths = []
    for index, batch in enumerate(chunks(candidates, int(config["pubmed_batch_size"]))):
        path = raw / f"pubmed_{index:03d}.xml"
        pubmed_paths.append(path)
        if args.refresh or not path.exists():
            response = client.get("efetch.fcgi", {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"})
            save_response(path, response)
    metadata = parse_pubmed(pubmed_paths)
    accepted_pmids = [
        pmid for pmid in candidates
        if pmid in metadata and metadata[pmid]["pmcid"] and metadata[pmid]["erratum_for"]
    ][: int(config["sample_size"])]
    if len(accepted_pmids) != int(config["sample_size"]):
        raise RuntimeError(
            f"Only {len(accepted_pmids)} valid records in {len(candidates)} deterministic candidates"
        )
    accepted = set(accepted_pmids)
    rejected = [
        {
            "pmid": pmid,
            "reason": "missing_record" if pmid not in metadata else
                "missing_record_pmcid" if not metadata[pmid]["pmcid"] else
                "missing_erratum_for",
        }
        for pmid in candidates[: candidates.index(accepted_pmids[-1]) + 1]
        if pmid not in accepted
    ]
    valid = [metadata[pmid] for pmid in accepted_pmids]
    sample_path = raw / "sample.json"
    write_json(sample_path, {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "parent_frame_sha256": sha256(project / "data/raw/e000/sampling_frame.json"),
        "parent_frame_size": len(frame["eligible_pmids"]),
        "excluded_e000_pmids": len(excluded),
        "candidate_count": len(candidates),
        "sample_size": len(accepted_pmids),
        "seed": config["seed"],
        "rejected_before_sample_complete": rejected,
        "sampled_pmids": accepted_pmids,
    })

    pmc_paths = []
    for index, batch in enumerate(chunks([item["pmcid"] for item in valid], int(config["pmc_batch_size"]))):
        path = raw / f"pmc_{index:03d}.xml"
        pmc_paths.append(path)
        if args.refresh or not path.exists():
            response = client.get("efetch.fcgi", {"db": "pmc", "id": ",".join(batch), "retmode": "xml"})
            save_response(path, response)

    notices = {}
    for path in pmc_paths:
        for item in extract_notice_articles(path):
            if item["pmcid"]:
                notices[item["pmcid"]] = item

    rows = []
    for item in valid:
        notice = notices.get(item["pmcid"])
        if notice is None or notice.get("pmid") != item["pmid"]:
            raise RuntimeError(
                f"Record/JATS identity failure for correction PMID {item['pmid']} and PMCID {item['pmcid']}"
            )
        snippets = evidence_snippets(notice["blocks"])
        category, flags = classify(notice["text"], snippets)
        rows.append({
            **item,
            "parser_category": category,
            "parser_flags": flags,
            "text_characters": len(notice["text"]),
            "blocks": notice["blocks"],
            "evidence_snippets": snippets,
            "source_pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/",
            "source_pmc_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{item['pmcid']}/",
        })

    notices_path = processed / "notices.jsonl"
    notices_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    counts = Counter(row["parser_category"] for row in rows)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "sample_size": len(accepted_pmids),
        "candidate_count": len(candidates),
        "rejected_before_sample_complete": rejected,
        "e000_overlap": len(set(accepted_pmids) & excluded),
        "validated_records": len(valid),
        "jats_identity_matches": len(rows),
        "parser_category_counts": dict(sorted(counts.items())),
        "artifacts": {
            str(path.relative_to(project)): {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in [sample_path, *pubmed_paths, *pmc_paths, notices_path]
        },
        "warning": "Parser categories and extracted candidates are triage only, never gold.",
    }
    write_json(results / "manifest.json", manifest)
    print(json.dumps({key: manifest[key] for key in [
        "sample_size", "e000_overlap", "validated_records", "jats_identity_matches", "parser_category_counts"
    ]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
