#!/usr/bin/env python3
"""Stream small, source-stratified Dolma v1.7 token prefixes for E123 feasibility.

Only downloads compressed bytes until each source/file budget is met. No GPU is
used. Input shard URL lists and train/held assignments are deterministic.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time

import numpy as np
import requests
from transformers import AutoTokenizer

MODEL_DIR = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")
URL_LIST = Path("/home/xiang/mechpop_cache/dolma-v1_7-urls.txt")
DATA_DIR = Path("/home/xiang/mechpop_cache/dolma_e123")
RESULTS = Path(__file__).resolve().parents[1] / "results/e123"
TRAIN_TOKENS = 32_000_000
HELD_TOKENS = 1_000_000
SEED = "e123-dolma17-v1"
DOLMA_REVISION = "7f48140530a023e9ea4c5cfb141160922727d4d3"

ROWS = [
    ("Dolma CC", 1195.5, 50), ("Refined Web", 456.4, 100),
    ("StarCoder", 263.8, 100), ("C4", 138.4, 50),
    ("Reddit", 79.9, 100), ("Semantic Scholar", 57.2, 100),
    ("arXiv", 28.0, 100), ("StackExchange", 19.6, 100),
    ("Flan", 16.5, 100), ("CC News", 14.3, 100),
    ("OpenWebMath", 12.6, 100), ("Algebraic Stack", 12.6, 100),
    ("Project Gutenberg", 5.3, 100), ("MegaWika", 4.6, 100),
    ("Wikipedia & Wikibooks", 3.7, 200),
]

GROUP_TO_SOURCE = {
    "cc_en_head": "Dolma CC", "cc_en_middle": "Dolma CC", "cc_en_tail": "Dolma CC",
    "falcon-refinedweb-filtered": "Refined Web", "starcoder": "StarCoder",
    "c4-filtered": "C4", "reddit": "Reddit", "pes2o": "Semantic Scholar",
    "redpajama-arxiv": "arXiv", "redpajama-stackexchange": "StackExchange",
    "tulu_flan": "Flan", "cc_news_head": "CC News", "cc_news_middle": "CC News",
    "cc_news_tail": "CC News", "proof_pile_2-open_web_math": "OpenWebMath",
    "proof_pile_2-algebraic_stack": "Algebraic Stack", "books": "Project Gutenberg",
    "wikiref_megawika": "MegaWika", "wiki": "Wikipedia & Wikibooks",
}


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_url_source(url: str) -> tuple[str, str]:
    remainder = url.split("/dolma-v1_7/", 1)[1]
    group, filename = remainder.split("/", 1)
    return group, filename


def assign_shards(urls: list[str]) -> tuple[list[str], list[str], dict[str, str]]:
    groups: dict[str, list[str]] = {}
    for url in urls:
        group, _ = parse_url_source(url)
        if group not in GROUP_TO_SOURCE:
            raise ValueError(f"Unmapped Dolma v1.7 source: {group}")
        groups.setdefault(group, []).append(url)
    selected_train: dict[str, list[str]] = {s: [] for s, _, _ in ROWS}
    selected_held: dict[str, list[str]] = {s: [] for s, _, _ in ROWS}
    assignment: dict[str, str] = {}
    for group, items in sorted(groups.items()):
        # Stable ordering avoids taking the same source shard for train and held.
        items.sort(key=lambda u: hashlib.sha256((SEED + u).encode()).hexdigest())
        source = GROUP_TO_SOURCE[group]
        # Prefer two distinct input shards per side. Tiny groups use one per side;
        # no document-level split is used, so all selected data remains file-disjoint.
        n_side = 2 if len(items) >= 4 else 1
        train = items[:n_side]
        held = items[n_side:2 * n_side]
        if not held and len(items) >= 2:
            held = [items[-1]]
        selected_train[source].extend(train)
        selected_held[source].extend(held)
        assignment.update({u: "train" for u in train})
        assignment.update({u: "held" for u in held})
    train_urls = [u for values in selected_train.values() for u in values]
    held_urls = [u for values in selected_held.values() for u in values]
    if set(train_urls) & set(held_urls):
        raise AssertionError("train/held source files overlap")
    return train_urls, held_urls, assignment


def stream_tokens(url: str, target: int, tokenizer, out_path: Path) -> dict:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ids: list[int] = []
    eos = tokenizer.eos_token_id
    started = time.time()
    response = requests.get(url, stream=True, timeout=(20, 90))
    response.raise_for_status()
    # The origin serves the .gz object with Content-Encoding: gzip as well. Let
    # urllib3 remove that HTTP layer, then GzipFile expands the stored JSONL shard.
    response.raw.decode_content = True
    try:
        with gzip.GzipFile(fileobj=response.raw, mode="rb") as stream:
            for line_number, raw in enumerate(stream, 1):
                if not raw.strip():
                    continue
                try:
                    row = json.loads(raw)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    raise RuntimeError(f"Malformed Dolma JSONL record {line_number} from {url}") from exc
                if not isinstance(row, dict):
                    raise RuntimeError(f"Non-object Dolma JSONL record {line_number} from {url}: {type(row).__name__}")
                text = row.get("text")
                if not isinstance(text, str) or not text:
                    continue
                ids.extend(tokenizer.encode(text, add_special_tokens=False))
                if eos is not None:
                    ids.append(eos)
                if len(ids) >= target:
                    del ids[target:]
                    break
    finally:
        response.close()
    if not ids:
        raise RuntimeError(f"No text tokens read from {url}")
    arr = np.asarray(ids, dtype=np.uint16)
    np.save(out_path, arr, allow_pickle=False)
    return {"path": str(out_path), "source_url": url, "token_count": int(arr.size),
            "size_bytes": out_path.stat().st_size, "sha256": digest_file(out_path),
            "stream_seconds": round(time.time() - started, 2)}


def main() -> int:
    if not URL_LIST.is_file():
        raise FileNotFoundError(f"Download the pinned URL list first: {URL_LIST}")
    if not (MODEL_DIR / "tokenizer.json").is_file():
        raise FileNotFoundError(f"Pinned OLMo tokenizer is not ready: {MODEL_DIR}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True, use_fast=True)
    if tokenizer.vocab_size > 65536:
        raise ValueError(f"uint16 cannot represent vocab size {tokenizer.vocab_size}")
    urls = [u.strip() for u in URL_LIST.read_text().splitlines() if u.strip() and not u.lstrip().startswith("#")]
    train_urls, held_urls, assignment = assign_shards(urls)
    mix_raw = {name: tokens * proportion / 100 for name, tokens, proportion in ROWS}
    denom = sum(mix_raw.values())
    mix = {name: amount / denom for name, amount in mix_raw.items()}
    mix_recipe = [{"source": name, "olmo_tokens_billion": tokens,
                   "sample_proportion_percent": proportion}
                  for name, tokens, proportion in ROWS]
    mix_hash = hashlib.sha256(json.dumps(mix_recipe, sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest()
    manifest = {"version": 1, "seed": SEED, "tokenizer": str(MODEL_DIR),
                "tokenizer_vocab_size": tokenizer.vocab_size,
                "eos_token_id": tokenizer.eos_token_id,
                "input_url_list_sha256": digest_file(URL_LIST),
                "input_url_list_path": str(URL_LIST),
                "input_url_list_revision": DOLMA_REVISION,
                "mix_recipe_sha256": mix_hash,
                "mix": {k: {"weight": mix[k], "weighted_tokens_billion": mix_raw[k]} for k, _, _ in ROWS},
                "mix_denominator_tokens_billion": denom,
                "reported_dataset_card_total_tokens_billion": 1715.1,
                "notes": ["Dataset-card source totals × Sample Proportion, normalized by row-derived total 1645.15B.",
                          "Card-reported total is 1715.1B, so the row-sum discrepancy is retained.",
                          "Initial transport probe exposed the origin's HTTP Content-Encoding gzip layer; decoder was corrected to remove the HTTP layer before expanding stored .json.gz. No source was silently skipped and no tokens were written by the failed probe.",
                          "Prefix sampling within selected compressed shards is a feasibility subset, not a representative full-Dolma sample.",
                          "Shards are file-disjoint between train and held. Source groups with only 2–3 available files use one file per side; the one-shard cc_news_tail group has no held shard, while CC News remains represented in held through its other groups. No document-level split is mislabeled as file isolation."],
                "train": [], "held": []}
    by_source_side: dict[tuple[str, str], list[str]] = {}
    for u in train_urls + held_urls:
        source = GROUP_TO_SOURCE[parse_url_source(u)[0]]
        side = assignment[u]
        by_source_side.setdefault((source, side), []).append(u)
    for side, budget in (("train", TRAIN_TOKENS), ("held", HELD_TOKENS)):
        for source, _, _ in ROWS:
            source_budget = round(budget * mix[source])
            source_urls = sorted(by_source_side.get((source, side), []),
                                 key=lambda u: hashlib.sha256((SEED + side + u).encode()).hexdigest())
            if not source_urls:
                raise RuntimeError(f"No {side} shards assigned for source {source}")
            remaining = source_budget
            for idx, url in enumerate(source_urls):
                count = len(source_urls) - idx
                target = math.ceil(remaining / count)
                if target <= 0:
                    break
                group, filename = parse_url_source(url)
                file_id = f"{group}/{filename}"
                slug = re.sub(r"[^a-z0-9]+", "_", source.lower()).strip("_")
                shard_key = hashlib.sha256(url.encode()).hexdigest()[:10]
                out = DATA_DIR / "tokens" / side / f"{slug}__{group}__{shard_key}.npy"
                record = stream_tokens(url, target, tokenizer, out)
                record.update({"source": source, "file_id": file_id, "input_group": group, "dtype": "uint16",
                               "source_sampling_weight": mix[source],
                               "input_shard_count_for_source_side": len(source_urls)})
                manifest[side].append(record)
                remaining -= record["token_count"]
                if remaining <= 0:
                    break
    train_set = {x["source_url"] for x in manifest["train"]}
    held_set = {x["source_url"] for x in manifest["held"]}
    if train_set & held_set:
        raise AssertionError("train and held output records share an input shard")
    manifest["source_file_disjoint"] = True
    manifest["train_tokens"] = sum(x["token_count"] for x in manifest["train"])
    manifest["held_tokens"] = sum(x["token_count"] for x in manifest["held"])
    for side in ("train", "held"):
        side_total = sum(x["token_count"] for x in manifest[side])
        for record in manifest[side]:
            record["sampling_weight"] = record["token_count"] / side_total
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"train_tokens": manifest["train_tokens"], "held_tokens": manifest["held_tokens"],
                      "train_files": len(manifest["train"]), "held_files": len(manifest["held"]),
                      "manifest": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
