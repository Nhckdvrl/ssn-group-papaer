#!/usr/bin/env python3
"""Audit whether PMC's currently exposed linked article retains old or new state.

The old/new selectors are direct publisher-notice quotations curated in E001.
This script does not generate or adjudicate gold; it only performs normalized
substring tests against NCBI metadata and JATS snapshots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

import requests


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("±", " plusminus ").replace("−", " minus ")
    value = value.replace("–", " dash ").replace("—", " dash ").replace("+", " plus ").replace("-", " hyphen ")
    value = value.replace("μ", "u").replace("µ", "u")
    return re.sub(r"[^a-z0-9]+", "", value)


class Client:
    def __init__(self, config: dict):
        self.interval = float(config["request_interval_seconds"])
        self.params = {"tool": config["tool"]}
        if config.get("email"):
            self.params["email"] = config["email"]
        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"{config['tool']}/1.0 ({config.get('email') or 'no-email'})"
        self.last_request = 0.0

    def fetch(self, database: str, identifiers: list[str], path: Path) -> None:
        delay = self.interval - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)
        response = self.session.get(
            f"{EUTILS}/efetch.fcgi",
            params={**self.params, "db": database, "id": ",".join(identifiers), "retmode": "xml"},
            timeout=120,
        )
        self.last_request = time.monotonic()
        response.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)


def batches(values: list[str], size: int):
    for start in range(0, len(values), size):
        yield values[start : start + size]


def parse_pubmed(paths: list[Path]) -> dict[str, dict]:
    records = {}
    for path in paths:
        root = ET.parse(path).getroot()
        for article in root.iter():
            if local(article.tag) != "PubmedArticle":
                continue
            pmid = next((text(n) for n in article.iter() if local(n.tag) == "PMID"), "")
            pubmed_data = next((n for n in article if local(n.tag) == "PubmedData"), None)
            id_list = next(
                (n for n in (pubmed_data if pubmed_data is not None else []) if local(n.tag) == "ArticleIdList"),
                None,
            )
            ids = {
                n.attrib.get("IdType", "").lower(): text(n)
                for n in (id_list if id_list is not None else [])
                if local(n.tag) == "ArticleId"
            }
            if pmid:
                records[pmid] = {"pmid": pmid, "pmcid": ids.get("pmc", ""), "doi": ids.get("doi", "")}
    return records


def parse_pmc(paths: list[Path]) -> dict[str, dict]:
    records = {}
    for path in paths:
        root = ET.parse(path).getroot()
        articles = [root] if local(root.tag) == "article" else [n for n in root.iter() if local(n.tag) == "article"]
        for article in articles:
            pmid = next(
                (text(n) for n in article.iter() if local(n.tag) == "article-id" and n.attrib.get("pub-id-type") == "pmid"),
                "",
            )
            pmcid = next(
                (text(n) for n in article.iter() if local(n.tag) == "article-id" and n.attrib.get("pub-id-type") in {"pmc", "pmcid"}),
                "",
            )
            if pmid:
                title_nodes = [n for n in article.iter() if local(n.tag) == "article-title"]
                abstract_nodes = [n for n in article.iter() if local(n.tag) == "abstract"]
                body_nodes = [n for n in article if local(n.tag) == "body"]
                back_nodes = [n for n in article if local(n.tag) == "back"]
                records[pmid] = {
                    "pmid": pmid,
                    "pmcid": "PMC" + pmcid.removeprefix("PMC"),
                    "content_text": " ".join(text(n) for n in [*title_nodes, *abstract_nodes, *body_nodes]),
                    "back_text": " ".join(text(n) for n in back_nodes),
                }
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--annotations", required=True, type=Path)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    project = args.config.resolve().parent.parent
    config = json.loads(args.config.read_text(encoding="utf-8"))
    annotations = json.loads(args.annotations.read_text(encoding="utf-8"))
    pairs = annotations["pairs"]
    original_pmids = list(dict.fromkeys(pair["original_pmid"] for pair in pairs))
    raw = project / "data/raw/e001"
    results = project / "results/e001"
    raw.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)
    client = Client(config)

    pubmed_paths = []
    for index, batch in enumerate(batches(original_pmids, int(config["pubmed_batch_size"]))):
        path = raw / f"original_pubmed_{index:03d}.xml"
        pubmed_paths.append(path)
        if args.refresh or not path.exists():
            client.fetch("pubmed", batch, path)
    metadata = parse_pubmed(pubmed_paths)

    pmc_ids = [metadata[pmid]["pmcid"] for pmid in original_pmids if pmid in metadata and metadata[pmid]["pmcid"]]
    pmc_paths = []
    for index, batch in enumerate(batches(pmc_ids, int(config["pmc_batch_size"]))):
        path = raw / f"original_pmc_{index:03d}.xml"
        pmc_paths.append(path)
        if args.refresh or not path.exists():
            client.fetch("pmc", batch, path)
    articles = parse_pmc(pmc_paths)

    rows = []
    for pair in pairs:
        pmid = pair["original_pmid"]
        article = articles.get(pmid)
        old_selector = pair["old"]
        new_selector = pair["new"]
        if article is None:
            state = "no_pmc_fulltext"
            old_present = new_present = False
        else:
            article_text = normalized(article["content_text"])
            back_text = normalized(article["back_text"])
            old_present = normalized(old_selector) in article_text
            new_present = new_selector == "[deleted]" or normalized(new_selector) in article_text
            if new_selector == "[deleted]":
                state = "old_only" if old_present else "new_only"
                new_present = not old_present
            elif old_present and new_present:
                state = "both"
            elif old_present:
                state = "old_only"
            elif new_present:
                state = "new_only"
            else:
                state = "neither"
        rows.append({
            **pair,
            "original_pmcid": (article or {}).get("pmcid", metadata.get(pmid, {}).get("pmcid", "")),
            "old_present": old_present,
            "new_present": new_present,
            "old_present_in_back_matter": bool(article) and normalized(old_selector) in back_text,
            "new_present_in_back_matter": bool(article) and new_selector != "[deleted]" and normalized(new_selector) in back_text,
            "current_pmc_state": state,
        })

    counts = Counter(row["current_pmc_state"] for row in rows)
    recoverable = counts["old_only"] + counts["both"]
    observed = len(rows) - counts["no_pmc_fulltext"]
    output = {
        "completed_utc": now_utc(),
        "estimand": "state exposed by title/abstract/body of the current PMC JATS snapshot, excluding back-matter change notes; not a historical version archive",
        "n_notice_pairs": len(rows),
        "n_originals_with_pmc_fulltext": observed,
        "state_counts": dict(sorted(counts.items())),
        "old_state_recoverable_count": recoverable,
        "old_state_recoverable_rate_all_pairs": recoverable / len(rows),
        "old_state_recoverable_rate_pmc_available": recoverable / observed if observed else None,
        "items": rows,
        "artifacts": {},
    }
    for path in [*pubmed_paths, *pmc_paths]:
        output["artifacts"][str(path.relative_to(project))] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    result_path = results / "original_state_audit.json"
    result_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: output[key] for key in output if key not in {"items", "artifacts"}}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
