#!/usr/bin/env python3
"""Reproducible PubMed/PMC correction-notice yield audit (E000).

The deterministic labels produced here are triage categories, never gold tiers.
Gold requires inspection of the publisher-authored evidence preserved in JATS.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import random
import re
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

import requests


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
SPACE = re.compile(r"\s+")
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
CORRECTION_CUE = re.compile(
    r"\b(?:correct(?:ed|ion)|err(?:or|oneous|atum)|incorrect(?:ly)?|mistake|"
    r"should\s+(?:instead\s+)?(?:read|be)|replace(?:d|ment)?|instead\s+of|"
    r"change[sd]?\s+from|was\s+changed\s+to|has\s+been\s+amended)\b", re.I
)
EXACT_CUE = re.compile(
    r"(?:should\s+(?:instead\s+)?read|should\s+be|instead\s+of|"
    r"replace(?:d)?\s+(?:by|with)|change[sd]?\s+from.{0,240}?\s+to|"
    r"(?:was|were)\s+incorrect(?:ly)?.{0,180}?(?:correct(?:ed)?\s+to|should))",
    re.I | re.S,
)
LOCATION_CUE = re.compile(
    r"\b(?:sentence|paragraph|line|section|page|column|equation|formula|"
    r"table|figure|fig\.?|legend|caption|heading|abstract|methods?|results?|"
    r"discussion|conclusion)\b", re.I
)
VISUAL_CUE = re.compile(r"\b(?:table|figure|fig\.?|image|panel|legend|caption)\b", re.I)
METADATA_CUE = re.compile(
    r"\b(?:author(?:ship)?|affiliation|orcid|corresponding\s+author|surname|"
    r"first\s+name|last\s+name|middle\s+initial|email|postal\s+address|"
    r"acknowledg(?:e)?ments?|funding|fund(?:er)?|grant|reference|citation|"
    r"doi|copyright|license|supplementary\s+file)\b", re.I
)
FORMAT_CUE = re.compile(r"\b(?:typograph(?:ic|ical)|formatting|misspell(?:ed|ing)|spacing|punctuation)\b", re.I)
NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*(?:\s?%|\s?[A-Za-zµμ]+)?")


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


def clean(text: str) -> str:
    return SPACE.sub(" ", html.unescape(text or "")).strip()


def node_text(node: ET.Element | None) -> str:
    return clean(" ".join(node.itertext())) if node is not None else ""


class Client:
    def __init__(self, config: dict):
        self.interval = float(config["request_interval_seconds"])
        self.params = {"tool": config["tool"]}
        if config.get("email"):
            self.params["email"] = config["email"]
        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"{config['tool']}/1.0 ({config.get('email') or 'no-email'})"
        self.last_request = 0.0

    def get(self, endpoint: str, params: dict, attempts: int = 6) -> requests.Response:
        merged = {**self.params, **params}
        for attempt in range(attempts):
            delay = self.interval - (time.monotonic() - self.last_request)
            if delay > 0:
                time.sleep(delay)
            try:
                response = self.session.get(f"{EUTILS}/{endpoint}", params=merged, timeout=120)
                self.last_request = time.monotonic()
                response.raise_for_status()
                return response
            except requests.RequestException:
                if attempt + 1 == attempts:
                    raise
                time.sleep(min(2 ** attempt, 30))
        raise AssertionError("unreachable")


def chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def save_response(path: Path, response: requests.Response) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)


def esearch_result(client: Client, query: str, retmax: int = 0) -> tuple[int, list[str], str]:
    response = client.get(
        "esearch.fcgi",
        {"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax, "retstart": 0},
    )
    result = response.json()["esearchresult"]
    return int(result["count"]), result["idlist"], response.url


def esearch(client: Client, query: str) -> tuple[int, list[str], list[dict]]:
    """Enumerate a PubMed frame despite the public ESearch 9,999-ID cap."""
    count, _, initial_url = esearch_result(client, query)
    leaves: list[dict] = []

    def collect(start: date, end: date) -> list[str]:
        dated_query = (
            f"({query}) AND (\"{start.isoformat().replace('-', '/')}\"[Date - Publication] : "
            f"\"{end.isoformat().replace('-', '/')}\"[Date - Publication])"
        )
        shard_count, _, count_url = esearch_result(client, dated_query)
        if shard_count == 0:
            return []
        if shard_count <= 9999:
            checked_count, ids, ids_url = esearch_result(client, dated_query, shard_count)
            if checked_count != shard_count or len(ids) != shard_count:
                raise RuntimeError(f"Unstable ESearch shard {start}..{end}: {shard_count}, {checked_count}, {len(ids)}")
            leaves.append({"start": str(start), "end": str(end), "count": shard_count, "count_url": count_url, "ids_url": ids_url})
            return ids
        if start >= end:
            raise RuntimeError(f"A one-day PubMed shard exceeds 9,999 records: {start} ({shard_count})")
        midpoint = start + (end - start) // 2
        return collect(start, midpoint) + collect(midpoint + timedelta(days=1), end)

    # PubMed's historical coverage begins well after 1500; 2100 leaves room for
    # ahead-of-print date metadata. The recovered count is checked below.
    ids = collect(date(1500, 1, 1), date(2100, 12, 31))
    ids = list(dict.fromkeys(ids))
    if len(ids) != count:
        raise RuntimeError(
            f"Date-sharded frame has {len(ids)} unique IDs but undated query reports {count}; "
            "do not sample from an incomplete frame"
        )
    leaves.insert(0, {"initial_count": count, "initial_url": initial_url})
    return count, ids, leaves


def parse_pubmed(xml_paths: list[Path]) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for path in xml_paths:
        root = ET.parse(path).getroot()
        for article in root.iter():
            if local(article.tag) not in {"PubmedArticle", "PubmedBookArticle"}:
                continue
            pmid_node = next((n for n in article.iter() if local(n.tag) == "PMID"), None)
            pmid = node_text(pmid_node)
            if not pmid:
                continue
            # Only the record-level PubmedData/ArticleIdList identifies this
            # article. ReferenceList descendants also contain ArticleId nodes
            # and must never be allowed to overwrite the record identifiers.
            article_ids = {}
            pubmed_data = next((n for n in article if local(n.tag) == "PubmedData"), None)
            id_list = next(
                (n for n in (pubmed_data if pubmed_data is not None else []) if local(n.tag) == "ArticleIdList"),
                None,
            )
            for item in (id_list if id_list is not None else []):
                if local(item.tag) == "ArticleId":
                    article_ids[item.attrib.get("IdType", "unknown").lower()] = node_text(item)
            refs = []
            for item in article.iter():
                if local(item.tag) == "CommentsCorrections" and item.attrib.get("RefType") == "ErratumFor":
                    ref_pmid = next((node_text(n) for n in item.iter() if local(n.tag) == "PMID"), "")
                    refs.append({"pmid": ref_pmid, "citation": node_text(item)})
            title_node = next((n for n in article.iter() if local(n.tag) == "ArticleTitle"), None)
            journal_node = next((n for n in article.iter() if local(n.tag) == "Title"), None)
            date_text = " ".join(
                node_text(n) for n in article.iter() if local(n.tag) in {"PubDate", "ArticleDate", "PubMedPubDate"}
            )
            year_match = YEAR.search(date_text)
            pub_types = [node_text(n) for n in article.iter() if local(n.tag) == "PublicationType"]
            records[pmid] = {
                "pmid": pmid,
                "pmcid": article_ids.get("pmc", ""),
                "doi": article_ids.get("doi", ""),
                "title": node_text(title_node),
                "journal": node_text(journal_node),
                "year": int(year_match.group()) if year_match else None,
                "publication_types": pub_types,
                "erratum_for": refs,
            }
    return records


def extract_notice_articles(path: Path) -> list[dict]:
    root = ET.parse(path).getroot()
    articles = [root] if local(root.tag) == "article" else [n for n in root.iter() if local(n.tag) == "article"]
    output = []
    for article in articles:
        pmcid = ""
        pmid = ""
        for node in article.iter():
            if local(node.tag) == "article-id" and node.attrib.get("pub-id-type") in {"pmc", "pmcid"}:
                pmcid = "PMC" + node_text(node).removeprefix("PMC")
            elif local(node.tag) == "article-id" and node.attrib.get("pub-id-type") == "pmid":
                pmid = node_text(node)
        blocks = []
        bodies = [node for node in article if local(node.tag) == "body"]
        for body in bodies:
            for node in body.iter():
                if local(node.tag) in {"p", "title", "caption"}:
                    value = node_text(node)
                    if value and value not in blocks:
                        blocks.append(value)
        output.append({"pmcid": pmcid, "pmid": pmid, "text": "\n".join(blocks), "blocks": blocks})
    return output


def evidence_snippets(blocks: list[str], max_snippets: int = 8) -> list[str]:
    scored = []
    for index, block in enumerate(blocks):
        if not CORRECTION_CUE.search(block):
            continue
        score = 4 * bool(EXACT_CUE.search(block)) + 2 * bool(LOCATION_CUE.search(block))
        score += min(len(NUMBER.findall(block)), 3)
        score -= 2 * bool(METADATA_CUE.search(block))
        start = max(0, index - 1)
        end = min(len(blocks), index + 3)
        window = " ⟦NEXT⟧ ".join(blocks[start:end])
        scored.append((score, index, window[:3000]))
    scored.sort(key=lambda item: (-item[0], item[1]))
    snippets = []
    for _, _, snippet in scored:
        if snippet not in snippets:
            snippets.append(snippet)
        if len(snippets) == max_snippets:
            break
    return snippets


def classify(text: str, snippets: list[str]) -> tuple[str, list[str]]:
    body = "\n".join(snippets) or text[:5000]
    flags = []
    if EXACT_CUE.search(body):
        flags.append("exact_language")
    if LOCATION_CUE.search(body):
        flags.append("location")
    if VISUAL_CUE.search(body):
        flags.append("visual")
    if METADATA_CUE.search(body):
        flags.append("metadata")
    if FORMAT_CUE.search(body):
        flags.append("formatting")
    numbers = NUMBER.findall(body)
    if len(numbers) >= 2:
        flags.append("multiple_numbers")

    substantive_hint = bool(re.search(r"\b(?:result|method|dose|value|rate|risk|effect|conclusion|data|participant|patient)\b", body, re.I))
    metadata_dominant = bool(METADATA_CUE.search(body)) and not substantive_hint and not VISUAL_CUE.search(body)
    if EXACT_CUE.search(body) and not metadata_dominant:
        label = "exact_replacement_candidate"
    elif CORRECTION_CUE.search(body) and len(numbers) >= 2 and not metadata_dominant:
        label = "numeric_or_symbolic_candidate"
    elif CORRECTION_CUE.search(body) and LOCATION_CUE.search(body) and not metadata_dominant:
        label = "location_plus_new_candidate"
    elif metadata_dominant or FORMAT_CUE.search(body):
        label = "metadata_or_nonpropositional"
    elif CORRECTION_CUE.search(body):
        label = "semantic_not_alignable"
    else:
        label = "unusable_or_ambiguous"
    return label, flags


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--refresh", action="store_true", help="redownload existing raw files")
    args = parser.parse_args()

    config_path = args.config.resolve()
    project = config_path.parent.parent
    config = json.loads(config_path.read_text(encoding="utf-8"))
    raw = project / "data/raw/e000"
    processed = project / "data/processed/e000"
    results = project / "results/e000"
    for directory in (raw, processed, results):
        directory.mkdir(parents=True, exist_ok=True)

    client = Client(config)
    frame_path = raw / "sampling_frame.json"
    if frame_path.exists() and not args.refresh:
        frame = json.loads(frame_path.read_text(encoding="utf-8"))
        universe = frame["eligible_pmids"]
        sampled = frame["sampled_pmids"]
    else:
        count, universe, shards = esearch(client, config["query"])
        if count < config["sample_size"]:
            raise RuntimeError(f"Only {count} eligible records for requested sample of {config['sample_size']}")
        sampled = random.Random(config["seed"]).sample(universe, config["sample_size"])
        frame = {
            "created_utc": now_utc(),
            "database": "pubmed",
            "query": config["query"],
            "esearch_shards": shards,
            "eligible_count": count,
            "eligible_pmids": universe,
            "sample_size": len(sampled),
            "seed": config["seed"],
            "sampled_pmids": sampled,
        }
        write_json(frame_path, frame)

    pubmed_paths = []
    for index, batch in enumerate(chunks(sampled, config["pubmed_batch_size"])):
        path = raw / f"pubmed_{index:03d}.xml"
        pubmed_paths.append(path)
        if not path.exists() or args.refresh:
            response = client.get("efetch.fcgi", {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"})
            save_response(path, response)

    metadata = parse_pubmed(pubmed_paths)
    valid = [metadata[pmid] for pmid in sampled if pmid in metadata and metadata[pmid]["pmcid"] and metadata[pmid]["erratum_for"]]
    missing = [pmid for pmid in sampled if pmid not in {item["pmid"] for item in valid}]

    pmc_paths = []
    for index, batch in enumerate(chunks([item["pmcid"] for item in valid], config["pmc_batch_size"])):
        path = raw / f"pmc_{index:03d}.xml"
        pmc_paths.append(path)
        if not path.exists() or args.refresh:
            response = client.get("efetch.fcgi", {"db": "pmc", "id": ",".join(batch), "retmode": "xml"})
            save_response(path, response)

    notices = {}
    parse_errors = []
    for path in pmc_paths:
        try:
            for item in extract_notice_articles(path):
                if item["pmcid"]:
                    notices[item["pmcid"]] = item
        except ET.ParseError as error:
            parse_errors.append({"path": str(path.relative_to(project)), "error": str(error)})

    rows = []
    for item in valid:
        notice = notices.get(item["pmcid"], {"text": "", "blocks": []})
        notice_matches_record = notice.get("pmid") == item["pmid"]
        if notice_matches_record:
            snippets = evidence_snippets(notice["blocks"])
            label, flags = classify(notice["text"], snippets)
        else:
            snippets = []
            label, flags = "notice_fulltext_unavailable", []
        rows.append({
            **item,
            "parser_category": label,
            "parser_flags": flags,
            "jats_pmid": notice.get("pmid", ""),
            "notice_matches_pubmed_record": notice_matches_record,
            "text_characters": len(notice["text"]) if notice_matches_record else 0,
            "evidence_snippets": snippets,
            "source_pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/",
            "source_pmc_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{item['pmcid']}/",
        })

    jsonl_path = processed / "notices.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    review_path = processed / "review_sheet.csv"
    fields = [
        "pmid", "pmcid", "year", "journal", "title", "parser_category", "parser_flags",
        "erratum_for_pmids", "evidence_snippets", "source_pubmed_url", "source_pmc_url",
        "gold_label", "correction_class", "old_text", "new_text", "review_note",
    ]
    with review_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "pmid": row["pmid"], "pmcid": row["pmcid"], "year": row["year"],
                "journal": row["journal"], "title": row["title"],
                "parser_category": row["parser_category"], "parser_flags": "|".join(row["parser_flags"]),
                "erratum_for_pmids": "|".join(ref["pmid"] for ref in row["erratum_for"] if ref["pmid"]),
                "evidence_snippets": " || ".join(row["evidence_snippets"]),
                "source_pubmed_url": row["source_pubmed_url"], "source_pmc_url": row["source_pmc_url"],
                "gold_label": "", "correction_class": "", "old_text": "", "new_text": "", "review_note": "",
            })

    counts = Counter(row["parser_category"] for row in rows)
    years = Counter(str(row["year"] or "unknown") for row in rows)
    journals = Counter(row["journal"] or "unknown" for row in rows)
    manifest = {
        "completed_utc": now_utc(),
        "config": config,
        "frame_count": len(universe),
        "requested_sample": len(sampled),
        "valid_linked_fulltext_records": len(valid),
        "missing_after_metadata_validation": missing,
        "pmc_documents_parsed": len(notices),
        "correction_notice_documents_matched": sum(row["notice_matches_pubmed_record"] for row in rows),
        "parse_errors": parse_errors,
        "parser_category_counts": dict(sorted(counts.items())),
        "year_range": [min((r["year"] for r in rows if r["year"]), default=None), max((r["year"] for r in rows if r["year"]), default=None)],
        "unique_journals": len(journals),
        "top_journals": journals.most_common(20),
        "year_counts": dict(sorted(years.items())),
        "artifacts": {},
        "warning": "Parser categories are triage labels, not gold tiers.",
    }
    for path in [frame_path, *pubmed_paths, *pmc_paths, jsonl_path, review_path]:
        if path.exists():
            manifest["artifacts"][str(path.relative_to(project))] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    write_json(results / "manifest.json", manifest)
    print(json.dumps({k: manifest[k] for k in ["frame_count", "requested_sample", "valid_linked_fulltext_records", "pmc_documents_parsed", "parser_category_counts", "year_range", "unique_journals"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
