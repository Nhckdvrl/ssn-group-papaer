#!/usr/bin/env python3
"""Prepare pinned OLMo dense inference assets and small Dolma metadata only.

This script intentionally never downloads Dolma data shards and never uses GPU.
Model files are fetched one at a time with curl to avoid HF Xet client stalls.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

MODEL_ID = "allenai/OLMo-1B-0724-hf"
MODEL_API = f"https://huggingface.co/api/models/{MODEL_ID}"
MODEL_FILES = [
    "config.json", "generation_config.json", "model.safetensors.index.json",
    "model-00001-of-00002.safetensors", "model-00002-of-00002.safetensors",
    "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json",
]
DOLMA_API = "https://huggingface.co/api/datasets/allenai/dolma"
DOLMA_LIST = "https://huggingface.co/datasets/allenai/dolma/raw/{rev}/urls/v1_7.txt"
HF_DOLMA_CARD = "https://huggingface.co/datasets/allenai/dolma"
OLMO_CONFIG_REV = "e4786afc54b569223c2a801135daf31f4c9c5780"
OLMO_7B_CONFIG = "https://github.com/allenai/OLMo/blob/" + OLMO_CONFIG_REV + "/configs/official-0724/OLMo-7B-0724.yaml"
DEST = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")
OUT = Path(__file__).resolve().parents[1] / "results/e123/assets.json"


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    model = get_json(MODEL_API)
    model_rev = model["sha"]
    DEST.mkdir(parents=True, exist_ok=True)
    sibling_names = {x["rfilename"] for x in model.get("siblings", [])}
    missing = [name for name in MODEL_FILES if name not in sibling_names]
    if missing:
        raise RuntimeError(f"Pinned model revision lacks required files: {missing}")

    files = {}
    for name in MODEL_FILES:
        target = DEST / name
        if not target.is_file():
            tmp = target.with_suffix(target.suffix + ".partial")
            url = f"https://huggingface.co/{MODEL_ID}/resolve/{model_rev}/{name}"
            subprocess.run([
                "curl", "--fail", "--location", "--retry", "4", "--retry-all-errors",
                "--connect-timeout", "20", "--output", str(tmp), url,
            ], check=True)
            tmp.replace(target)
        files[name] = {"path": str(target), "size_bytes": target.stat().st_size,
                       "sha256": sha256(target)}

    dolma = get_json(DOLMA_API)
    dolma_rev = dolma["sha"]
    url_list_path = DEST.parent / "dolma-v1_7-urls.txt"
    url = DOLMA_LIST.format(rev=dolma_rev)
    if not url_list_path.is_file():
        subprocess.run(["curl", "--fail", "--location", "--retry", "4", "--retry-all-errors",
                        "--output", str(url_list_path), url], check=True)
    entries = []
    for raw in url_list_path.read_text().splitlines():
        raw = raw.strip()
        if raw and not raw.startswith("#"):
            entries.append(raw)
    groups: dict[str, int] = {}
    for u in entries:
        group = u.split("/dolma-v1_7/", 1)[-1].split("/", 1)[0]
        groups[group] = groups.get(group, 0) + 1

    card_rows = [
        ("Dolma CC", 1195.5, 50), ("Refined Web", 456.4, 100),
        ("StarCoder", 263.8, 100), ("C4", 138.4, 50),
        ("Reddit", 79.9, 100), ("Semantic Scholar", 57.2, 100),
        ("arXiv", 28.0, 100), ("StackExchange", 19.6, 100),
        ("Flan", 16.5, 100), ("CC News", 14.3, 100),
        ("OpenWebMath", 12.6, 100), ("Algebraic Stack", 12.6, 100),
        ("Project Gutenberg", 5.3, 100), ("MegaWika", 4.6, 100),
        ("Wikipedia & Wikibooks", 3.7, 200),
    ]
    effective = {name: tokens * proportion / 100 for name, tokens, proportion in card_rows}
    effective_total = sum(effective.values())
    card_mix = {
        name: {"olmo_tokens_billion": tokens, "sample_proportion_percent": proportion,
               "weighted_tokens_billion": effective[name],
               "normalized_weight_percent": effective[name] / effective_total * 100}
        for name, tokens, proportion in card_rows
    }

    result = {
        "model": {"repo": MODEL_ID, "revision": model_rev, "revision_url":
                  f"https://huggingface.co/{MODEL_ID}/tree/{model_rev}",
                  "download_method": "curl one file at a time; no HF Xet client",
                  "files": files},
        "dolma_v1_7_metadata": {
            "repo": "allenai/dolma", "revision": dolma_rev,
            "url_list": {"path": str(url_list_path), "url": url,
                         "size_bytes": url_list_path.stat().st_size,
                         "sha256": sha256(url_list_path)},
            "listed_shard_count": len(entries), "shards_by_source": groups,
            "data_shards_downloaded": False,
            "official_version_gzip_size": "4.5 TB",
            "official_summary_source_proportions_and_normalized_mix": card_mix,
            "weighted_row_sum_tokens_billion": effective_total,
            "dataset_card_reported_weighted_total_tokens_billion": 1715.1,
            "source_mix_note": "Normalized weights use the dataset-card source OLMo-token total times its Sample Proportion column. The row-derived denominator (1645.15B) does not equal the card's reported total (1715.1B); preserve this discrepancy in any use.",
            "official_olmo_7b_0724_training_config": {
                "url": OLMO_7B_CONFIG,
                "commit": OLMO_CONFIG_REV,
                "note": "Official config points to pretokenized v1_7 data and comments per-source GT; its recipe differs from the dataset-card summary and from OLMo-1B's v1_5 config."
            }
        },
        "environment": {"python": sys.version.split()[0],
                        "venv_python": sys.executable,
                        "cuda_visible_but_not_used": True},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"model_revision": model_rev, "model_total_bytes":
                      sum(v["size_bytes"] for v in files.values()),
                      "dolma_revision": dolma_rev, "dolma_shard_count": len(entries),
                      "dolma_sources": groups, "manifest": str(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
