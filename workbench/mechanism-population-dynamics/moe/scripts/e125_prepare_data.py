#!/usr/bin/env python3
"""Extend E123's exact per-file Dolma prefixes into the E125 coverage pool.

This creates train prefixes only. The original E123 held records are reused
byte-for-byte in the new manifest. Completed train shards are resumable.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np
import requests
from transformers import AutoTokenizer

DEFAULT_REFERENCE = Path(__file__).resolve().parents[1] / "results/e123/manifest.json"
DEFAULT_DATA_DIR = Path("~/mechpop_cache/dolma_e125_512m")
DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "results/e125/cover_manifest.json"
DEFAULT_SMALL_MANIFEST = Path(__file__).resolve().parents[1] / "results/e125/small_manifest.json"
MODEL_DIR = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def allocate_targets(weights: list[float], total: int) -> list[int]:
    """Largest-remainder allocation while preserving the exact probability vector."""
    if total <= 0 or not weights or any(w <= 0 for w in weights):
        raise ValueError("Need a positive total and positive per-file weights")
    wsum = sum(weights)
    if not math.isclose(wsum, 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError(f"Reference sampling_weight vector sums to {wsum}, expected 1")
    raw = [total * w for w in weights]
    targets = [math.floor(x) for x in raw]
    remainder = total - sum(targets)
    ranked = sorted(range(len(weights)), key=lambda i: (-(raw[i] - targets[i]), i))
    for i in ranked[:remainder]:
        targets[i] += 1
    if sum(targets) != total or any(x <= 0 for x in targets):
        raise AssertionError("Failed to allocate positive exact per-file token targets")
    return targets


def stream_prefix(url: str, target_tokens: int, tokenizer, out_path: Path) -> dict:
    """Stream one compressed Dolma shard to an exact uint16 token prefix."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    partial = out_path.with_suffix(out_path.suffix + ".partial")
    partial.unlink(missing_ok=True)
    chunks: list[np.ndarray] = []
    count = 0
    eos = tokenizer.eos_token_id
    started = time.time()
    response = requests.get(url, stream=True, timeout=(20, 90))
    try:
        response.raise_for_status()
        # Origin HTTP Content-Encoding is gzip in addition to the stored .json.gz.
        response.raw.decode_content = True
        with gzip.GzipFile(fileobj=response.raw, mode="rb") as stream:
            for line_number, raw in enumerate(stream, 1):
                if not raw.strip():
                    continue
                try:
                    row = json.loads(raw)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    raise RuntimeError(f"Malformed Dolma record {line_number} from {url}") from exc
                if not isinstance(row, dict):
                    raise RuntimeError(f"Non-object Dolma record {line_number} from {url}")
                text = row.get("text")
                if not isinstance(text, str) or not text:
                    continue
                ids = tokenizer.encode(text, add_special_tokens=False)
                if eos is not None:
                    ids.append(eos)
                remaining = target_tokens - count
                if remaining <= 0:
                    break
                piece = np.asarray(ids[:remaining], dtype=np.uint16)
                if piece.size:
                    chunks.append(piece)
                    count += int(piece.size)
                if count >= target_tokens:
                    break
    finally:
        response.close()
    if count != target_tokens:
        raise RuntimeError(f"Shard prefix too short for {url}: got {count}, need {target_tokens}")
    arr = np.concatenate(chunks)
    with partial.open("wb") as f:
        np.save(f, arr, allow_pickle=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(partial, out_path)
    return {"path": str(out_path), "source_url": url, "token_count": int(arr.size),
            "size_bytes": out_path.stat().st_size, "sha256": sha256_file(out_path),
            "stream_seconds": round(time.time() - started, 2)}


def reuse_or_generate(record: dict, target: int, index: int, data_dir: Path, tokenizer) -> dict:
    url = record["source_url"]
    key = hashlib.sha256(f"{index}\n{url}\n{target}".encode()).hexdigest()[:12]
    out = data_dir / "tokens/train" / f"{index:03d}__{key}.npy"
    if out.is_file():
        try:
            arr = np.load(out, mmap_mode="r", allow_pickle=False)
            old = np.load(record["path"], mmap_mode="r", allow_pickle=False)
            valid = (arr.dtype == np.uint16 and arr.ndim == 1 and len(arr) == target
                     and len(arr) >= len(old) and np.array_equal(arr[:len(old)], old))
            if valid:
                return {"path": str(out), "source_url": url, "token_count": int(len(arr)),
                        "size_bytes": out.stat().st_size, "sha256": sha256_file(out),
                        "stream_seconds": None, "resumed": True}
        except (OSError, ValueError):
            pass
        out.unlink(missing_ok=True)
    last_error = None
    for attempt in range(4):
        try:
            return {**stream_prefix(url, target, tokenizer, out), "resumed": False}
        except (requests.RequestException, OSError, EOFError) as exc:
            last_error = exc
            if attempt == 3:
                break
            delay = 2 ** attempt
            print(f"retry {attempt + 1}/3 for {record['file_id']} after {type(exc).__name__}; sleep={delay}s", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"Failed to stream shard after retries: {url}") from last_error


def verify_prefix(small: dict, large: dict) -> None:
    old = np.load(small["path"], mmap_mode="r", allow_pickle=False)
    new = np.load(large["path"], mmap_mode="r", allow_pickle=False)
    if len(new) < len(old) or not np.array_equal(new[:len(old)], old):
        raise RuntimeError(f"Large prefix is not an exact extension of E123: {small['source_url']}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--train-tokens", type=int, default=512_000_000)
    p.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    p.add_argument("--manifest-path", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--small-manifest-path", type=Path, default=DEFAULT_SMALL_MANIFEST)
    p.add_argument("--reference-manifest", type=Path, default=DEFAULT_REFERENCE)
    p.add_argument("--reuse-held", action="store_true", help="required: use exact held records from reference manifest")
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()
    if not args.reuse_held:
        p.error("--reuse-held is required; this script never regenerates held data")
    if not 1 <= args.workers <= 4:
        p.error("--workers must be between 1 and 4")
    if args.train_tokens <= 0:
        p.error("--train-tokens must be positive")

    reference_path = args.reference_manifest.resolve()
    reference = json.loads(reference_path.read_text())
    old_train, old_held = reference["train"], reference["held"]
    if not old_train or not old_held:
        raise ValueError("Reference manifest must contain train and held records")
    urls = [r["source_url"] for r in old_train]
    if len(urls) != len(set(urls)):
        raise ValueError("Reference train source_url records are not unique")
    if set(urls) & {r["source_url"] for r in old_held}:
        raise ValueError("Reference train/held source_url overlap")
    weights = [float(r["sampling_weight"]) for r in old_train]
    targets = allocate_targets(weights, args.train_tokens)

    data_dir = args.data_dir.expanduser().resolve()
    manifest_path = args.manifest_path.resolve()
    small_path = args.small_manifest_path.resolve()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True, use_fast=True)
    if tokenizer.vocab_size > 65536:
        raise ValueError("Tokenizer vocabulary exceeds uint16 capacity")

    # Publish this reference-only comparison manifest first; it never copies token assets.
    small = dict(reference)
    small.update({"manifest_kind": "E125 small-pool reference; token records are referenced, not copied",
                  "reference_manifest": str(reference_path),
                  "train_sampling_probability_source": "exact E123 per-file sampling_weight",
                  "held_reused_from_reference": True})
    small_path.parent.mkdir(parents=True, exist_ok=True)
    small_path.write_text(json.dumps(small, indent=2, sort_keys=True) + "\n")

    # Results are restored to original E123 file order after concurrent streaming.
    new_train: list[dict | None] = [None] * len(old_train)
    data_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(reuse_or_generate, record, target, i, data_dir, tokenizer): i
                   for i, (record, target) in enumerate(zip(old_train, targets))}
        finished = 0
        for future in as_completed(futures):
            i = futures[future]
            generated = future.result()
            source = old_train[i]
            # Keep provenance and sampling probabilities exactly aligned to E123.
            generated.update({"source": source["source"], "file_id": source["file_id"],
                              "input_group": source.get("input_group"), "dtype": "uint16",
                              "sampling_weight": source["sampling_weight"],
                              "source_sampling_weight": source.get("source_sampling_weight"),
                              "target_tokens": targets[i],
                              "reference_small_path": source["path"],
                              "reference_small_sha256": source["sha256"],
                              "reference_small_token_count": source["token_count"]})
            new_train[i] = generated
            finished += 1
            print(f"completed {finished}/{len(old_train)}: {source['source']} {source['file_id']} "
                  f"target={targets[i]} resumed={generated['resumed']}", flush=True)

    records = [r for r in new_train if r is not None]
    if len(records) != len(old_train):
        raise AssertionError("Not all train shards completed")
    if [r["source_url"] for r in records] != urls:
        raise AssertionError("Train source URL order changed")
    if [r["file_id"] for r in records] != [r["file_id"] for r in old_train]:
        raise AssertionError("Train file ID order changed")
    if [r["sampling_weight"] for r in records] != [r["sampling_weight"] for r in old_train]:
        raise AssertionError("Per-file probabilities differ from E123")

    for old, new in zip(old_train, records):
        verify_prefix(old, new)
    held_records = old_held  # Reuse original paths, hashes, IDs, order, and bytes exactly.
    train_urls, held_urls = set(urls), {r["source_url"] for r in held_records}
    train_ids = {(r["source"], r["file_id"]) for r in records}
    held_ids = {(r["source"], r["file_id"]) for r in held_records}
    train_hashes, held_hashes = {r["sha256"] for r in records}, {r["sha256"] for r in held_records}
    if train_urls & held_urls or train_ids & held_ids or train_hashes & held_hashes:
        raise ValueError("Cover train/held source URL, file ID, or content hash overlap")

    manifest = {
        "version": 1, "manifest_kind": "E125 512M coverage pool; train regenerated, held reused",
        "reference_manifest": str(reference_path), "reference_manifest_sha256": sha256_file(reference_path),
        "small_manifest": str(small_path), "data_dir": str(data_dir),
        "train_tokens": sum(r["token_count"] for r in records),
        "held_tokens": sum(r["token_count"] for r in held_records),
        "requested_train_tokens": args.train_tokens,
        "train_file_order_matches_reference": True,
        "sampling_weights_exact_copy_from_reference": True,
        "sampling_weight_sum": sum(r["sampling_weight"] for r in records),
        "per_file_prefix_matches_small_pool": True,
        "held_records_reused_exactly": True,
        "source_file_disjoint": True, "content_sha256_disjoint": True,
        "workers": args.workers,
        "notes": ["Train is in E123 order. Each E125 train file extends the same Dolma source_url prefix; per-file sampling_weight is copied exactly from E123, not recomputed from larger token counts.",
                  "Held is the exact E123 held record list, including paths, hashes, file IDs, order, and bytes.",
                  "Completed train shards are atomically written and reused on rerun; failed/incomplete shards do not replace complete outputs."],
        "mix_recipe_sha256": reference.get("mix_recipe_sha256"),
        "input_url_list_sha256": reference.get("input_url_list_sha256"),
        "tokenizer": reference.get("tokenizer"),
        "tokenizer_vocab_size": tokenizer.vocab_size,
        "train": records, "held": held_records,
    }
    if manifest["train_tokens"] != args.train_tokens:
        raise AssertionError(f"Actual train token count {manifest['train_tokens']} != requested {args.train_tokens}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"train_tokens": manifest["train_tokens"], "held_tokens": manifest["held_tokens"],
                      "train_files": len(records), "held_files": len(held_records),
                      "manifest": str(manifest_path), "small_manifest": str(small_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
