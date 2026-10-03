"""E13 CPU metadata and matched partial-refresh actions; never launches GPU work.

Uses E12's audited full-record membership and exact token-count implementation.
Caches the complete pool once; fresh actions replace identical old slots in each
source/exact-supervision bin, leaving unsupported slots as shared old anchors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from e12_icons_mapping_audit import row_key
from e12_make_subsets import hash_lines, sha256
from e12_token_preflight import load_trainer, token_counts

_ORIGINAL = None
_PROCESSOR = None


def source_of(row):
    return str(row.get("image") or "text-only").split("/", 1)[0]


def metadata_chunk(bounds):
    start, stop = bounds
    records = []
    for position in range(start, stop):
        row = _ORIGINAL[position]
        records.append({"position": position, "row_key": row_key(row),
                        "source": source_of(row), "image": row.get("image"),
                        **token_counts(row, _PROCESSOR)})
    return records


def verify_source(args):
    audit = json.loads(args.audit.read_text())
    n = audit["original_rows"]
    if (audit["first_shard_only"] or audit["arrow_rows"] != n
            or audit["same_position_count"] != n
            or audit["same_position_conversation_count"] != n
            or audit["same_id_multiset"] is not True):
        raise RuntimeError("E12 full Arrow identity audit did not pass")
    original_path = args.root / "llava_json/llava_v1_5_mix665k.json"
    if sha256(original_path) != audit["source_json_sha256"]:
        raise RuntimeError("Original JSON changed since E12 audit")
    original = json.loads(original_path.read_text())
    if len(original) != n:
        raise RuntimeError("Original row count changed")
    return original, audit


def make_metadata(args, original, audit):
    global _ORIGINAL, _PROCESSOR
    from transformers import AutoProcessor

    args.out_root.mkdir(parents=True, exist_ok=True)
    cache = args.out_root / "pool_metadata.jsonl"
    identity_file = args.out_root / "pool_metadata_identity.json"
    token_script = Path(__file__).with_name("e12_token_preflight.py")
    trainer = load_trainer()
    processor = AutoProcessor.from_pretrained(str(args.root / "llava_init"), local_files_only=True)
    processor.chat_template = trainer.LLAVA_CHAT_TEMPLATE_WITH_EOS
    processor.tokenizer.chat_template = trainer.LLAVA_CHAT_TEMPLATE_WITH_EOS
    from e12_token_preflight import TRAIN_SCRIPT
    processor_files = {p.name: sha256(p) for p in sorted((args.root / "llava_init").iterdir())
                       if p.is_file() and p.suffix == ".json"}
    identity = {"source_json_sha256": audit["source_json_sha256"],
                "original_rows": len(original), "e12_token_script_sha256": sha256(token_script),
                "trainer_sha256": sha256(TRAIN_SCRIPT), "template_sha256": hashlib.sha256(
                    trainer.LLAVA_CHAT_TEMPLATE_WITH_EOS.encode()).hexdigest(),
                "processor_json_sha256": processor_files}
    sentinel = json.loads(args.sentinel.read_text())
    for ref in sentinel["rows"]:
        actual = token_counts(original[ref["position"]], processor)
        if any(actual[k] != ref[k] for k in (
                "input_tokens", "supervised_tokens", "last_supervised_token_is_eos")):
            raise RuntimeError(f"E12 processor sentinel differs at {ref['position']}")
    print(json.dumps({"event": "sentinel_passed", "rows": len(sentinel["rows"])}), flush=True)
    if cache.exists() or identity_file.exists():
        saved = json.loads(identity_file.read_text())
        if not cache.exists() or saved["identity"] != identity or saved["rows"] != len(original):
            raise RuntimeError("Incomplete or incompatible metadata cache; preserve and version it")
        if sha256(cache) != saved["cache_sha256"]:
            raise RuntimeError("Metadata cache hash changed")
        print(json.dumps({"event": "metadata_cache_reused", "path": str(cache)}), flush=True)
        return cache
    _ORIGINAL, _PROCESSOR = original, processor
    partial = cache.with_suffix(".jsonl.partial")
    if partial.exists():
        raise FileExistsError(f"Preserve incomplete metadata run: {partial}")
    chunks = [(i, min(i + 1000, len(original))) for i in range(0, len(original), 1000)]
    started = time.monotonic()
    count = 0
    with partial.open("w") as output, mp.get_context("fork").Pool(args.workers) as pool:
        for rows in pool.imap(metadata_chunk, chunks, chunksize=1):
            for row in rows:
                output.write(json.dumps(row, separators=(",", ":")) + "\n")
            count += len(rows)
            if count % 10000 == 0 or count == len(original):
                print(json.dumps({"event": "metadata_progress", "rows": count,
                                  "total": len(original), "wall_seconds": round(
                                      time.monotonic() - started, 1)}), flush=True)
    partial.rename(cache)
    report = {"identity": identity, "rows": count, "sentinel_matched": len(sentinel["rows"]),
              "workers": args.workers, "cache_sha256": sha256(cache),
              "wall_seconds": round(time.monotonic() - started, 1)}
    identity_file.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"event": "metadata_complete", **report}), flush=True)
    return cache


def seeded_rng(salt):
    digest = hashlib.sha256(f"E13|29|{salt}".encode()).digest()
    return random.Random(int.from_bytes(digest, "big"))


def make_actions(args, original, audit, cache):
    metadata = [json.loads(line) for line in cache.open()]
    if len(metadata) != len(original) or any(
            row["position"] != i for i, row in enumerate(metadata)):
        raise RuntimeError("Metadata does not cover original positions in order")
    icons_path = args.root / "icons_json/llava-icons-133k.json"
    icons = json.loads(icons_path.read_text())
    icons_keys = {row_key(row) for row in icons}
    if len(icons) != 133046 or len(icons_keys) != len(icons):
        raise RuntimeError("Unexpected released ICONS full-record membership")
    matches = Counter(row["row_key"] for row in metadata if row["row_key"] in icons_keys)
    if set(matches) != icons_keys or any(count != 1 for count in matches.values()):
        raise RuntimeError("Released ICONS records no longer map uniquely to original")
    old_manifest_path = args.root / "subsets/icons_exact_s17/e12_selection_manifest.json"
    old_manifest = json.loads(old_manifest_path.read_text())
    stable_icons = sorted((i for i, row in enumerate(metadata) if row["row_key"] in icons_keys),
                          key=lambda i: (str(original[i]["id"]), metadata[i]["row_key"]))
    old = sorted(random.Random(17).sample(stable_icons, 10000))
    if (hash_lines([str(i) for i in old]) != old_manifest["selected_positions_sha256"]
            or hash_lines([metadata[i]["row_key"] for i in old])
            != old_manifest["selected_full_records_sha256"]
            or old_manifest["original_json_sha256"] != audit["source_json_sha256"]):
        raise RuntimeError("Reconstructed S is not the frozen E12 ICONS seed17 action")
    old_keys = {metadata[i]["row_key"] for i in old}
    old_images = {metadata[i]["image"] for i in old if metadata[i]["image"]}
    slot_n = [metadata[i]["supervised_tokens"] for i in old]
    if len(old_keys) != 10000 or sum(slot_n) != 549353:
        raise RuntimeError("E12 S no longer has 10K unique records and 549353 label tokens")
    slots = defaultdict(list)
    for slot, i in enumerate(old):
        slots[(metadata[i]["source"], metadata[i]["supervised_tokens"])].append(slot)
    candidates = {"fresh_selected": defaultdict(list), "fresh_law": defaultdict(list)}
    exclusions = Counter()
    seen_fresh_keys = set()
    for row in metadata:
        if row["row_key"] in old_keys:
            exclusions["old_full_records"] += 1
            continue
        if row["image"] and row["image"] in old_images:
            exclusions["old_image_paths"] += 1
            continue
        if row["row_key"] in seen_fresh_keys:
            exclusions["duplicate_fresh_full_records"] += 1
            continue
        seen_fresh_keys.add(row["row_key"])
        action = "fresh_selected" if row["row_key"] in icons_keys else "fresh_law"
        candidates[action][(row["source"], row["supervised_tokens"])].append(row["position"])
    positions = {action: list(old) for action in ("replay", "fresh_selected", "fresh_law")}
    rngs = {action: seeded_rng(action) for action in positions}
    slot_rng = seeded_rng("shared_replacement_slots")
    replaced = []
    bins = []
    for (source, n), original_slots in sorted(slots.items()):
        inside = candidates["fresh_selected"][(source, n)]
        outside = candidates["fresh_law"][(source, n)]
        count = min(len(original_slots), len(inside), len(outside))
        chosen_slots = sorted(slot_rng.sample(original_slots, count))
        for action, pool in (("fresh_selected", inside), ("fresh_law", outside)):
            for slot, replacement in zip(chosen_slots, rngs[action].sample(pool, count)):
                positions[action][slot] = replacement
        replaced.extend(chosen_slots)
        bins.append({"source": source, "n": n, "old_slots": len(original_slots),
                     "fresh_in_available": len(inside), "fresh_out_available": len(outside),
                     "replaced_slots": count, "replaced_label_tokens": count * n})
    replaced.sort()
    replacement_set = set(replaced)
    anchors = [i for i in range(10000) if i not in replacement_set]
    label_coverage = sum(slot_n[i] for i in replaced) / sum(slot_n)
    row_coverage = len(replaced) / 10000
    per_source = {}
    for source in sorted({b["source"] for b in bins}):
        source_bins = [b for b in bins if b["source"] == source]
        old_rows = sum(b["old_slots"] for b in source_bins)
        old_tokens = sum(b["old_slots"] * b["n"] for b in source_bins)
        new_rows = sum(b["replaced_slots"] for b in source_bins)
        new_tokens = sum(b["replaced_label_tokens"] for b in source_bins)
        per_source[source] = {"old_rows": old_rows, "replaced_rows": new_rows,
                              "row_coverage": new_rows / old_rows,
                              "old_label_tokens": old_tokens, "replaced_label_tokens": new_tokens,
                              "label_token_coverage": new_tokens / old_tokens if old_tokens else None}
    support = {"sampling_seed": 29, "sampling_salt_prefix": "E13|29|",
               "budget": 10000, "supervised_tokens": sum(slot_n),
               "rows_replaced": len(replaced), "row_coverage": row_coverage,
               "label_token_coverage": label_coverage, "common_anchor_rows": len(anchors),
               "support_pass": row_coverage >= 0.90 and label_coverage >= 0.80,
               "source_support": per_source, "bins": bins, "exclusions": dict(exclusions),
               "old_selection_manifest": {"path": str(old_manifest_path),
                                          "sha256": sha256(old_manifest_path),
                                          "selected_positions_sha256": old_manifest[
                                              "selected_positions_sha256"]},
               "metadata_identity": str(args.out_root / "pool_metadata_identity.json"),
               "icons_json_sha256": sha256(icons_path), "actions": {}}
    fresh_key_sets = {}
    for action, selected in positions.items():
        records = [metadata[i] for i in selected]
        actual_n = [r["supervised_tokens"] for r in records]
        if actual_n != slot_n or len({r["row_key"] for r in records}) != 10000:
            raise RuntimeError(f"{action} changes slot labels or duplicates a full record")
        if [i for i in range(10000) if selected[i] != old[i]] != (
                [] if action == "replay" else replaced):
            raise RuntimeError("Actions do not share replacement slots and anchors")
        fresh = [records[slot] for slot in replaced] if action != "replay" else []
        fresh_keys = {r["row_key"] for r in fresh}
        old_image_overlap = len({r["image"] for r in fresh if r["image"]} & old_images)
        if fresh_keys & old_keys or old_image_overlap:
            raise RuntimeError("Fresh replacement contains previously used record or image")
        if action == "fresh_selected" and not fresh_keys <= icons_keys:
            raise RuntimeError("Fresh selected replacement is outside released ICONS pool")
        if action == "fresh_law" and fresh_keys & icons_keys:
            raise RuntimeError("Fresh law replacement is inside released ICONS pool")
        fresh_key_sets[action] = fresh_keys
        support["actions"][action] = {
            "selected_positions_sha256": hash_lines([str(i) for i in selected]),
            "selected_full_records_sha256": hash_lines([r["row_key"] for r in records]),
            "input_tokens": sum(r["input_tokens"] for r in records),
            "full_input_tokens": sum(r["full_input_tokens"] for r in records),
            "source_counts": dict(Counter(r["source"] for r in records)),
            "unique_full_records": len({r["row_key"] for r in records}),
            "unique_images": len({r["image"] for r in records if r["image"]}),
            "image_rows": sum(bool(r["image"]) for r in records),
            "fresh_unique_images": len({r["image"] for r in fresh if r["image"]}),
            "old_image_overlap_fresh": old_image_overlap,
            "slot_n_equal": True, "truncated_rows": sum(r["truncated"] for r in records),
            "rows_without_final_eos": sum(not r["last_supervised_token_is_eos"] for r in records)}
    if fresh_key_sets["fresh_selected"] & fresh_key_sets["fresh_law"]:
        raise RuntimeError("Fresh actions share complete record identities")
    support["fresh_full_record_disjoint"] = True
    support_path = args.out_root / "support_audit.json"
    support_path.write_text(json.dumps(support, indent=2) + "\n")
    print(json.dumps({"event": "support_complete", "path": str(support_path),
                      "rows_replaced": len(replaced), "row_coverage": row_coverage,
                      "label_token_coverage": label_coverage,
                      "support_pass": support["support_pass"], "source_support": per_source}), flush=True)
    if not support["support_pass"]:
        print("Support below prewritten thresholds; no materialization or GPU work", flush=True)
        return
    materialize(args, original, audit, metadata, positions, replaced, support)


def materialize(args, original, audit, metadata, positions, replaced, support):
    from datasets import DatasetDict, concatenate_datasets, load_from_disk
    from e12_index_audit import expected_turns
    sys.path.insert(0, "/home/xiang/.cache/research/data-centric-rsi/CurationBench/src")
    from benchmark.tools.contamination import EVAL_REGISTRY, audit_contamination

    ds = load_from_disk(str(args.root / "llava_arrow"))
    if isinstance(ds, DatasetDict):
        ds = concatenate_datasets([ds[k] for k in sorted(ds)])
    if len(ds) != len(original):
        raise RuntimeError("Arrow snapshot row count changed")
    old_ds = load_from_disk(str(args.root / "subsets/icons_exact_s17"))
    old_positions = positions["replay"]
    if ([str(x) for x in old_ds["id"]] != [str(original[i]["id"]) for i in old_positions]
            or list(old_ds["texts"]) != [expected_turns(original[i]) for i in old_positions]):
        raise RuntimeError("Replay does not preserve saved E12 Arrow row order and dialogue")
    slot_n = [metadata[i]["supervised_tokens"] for i in old_positions]
    for action, selected in positions.items():
        output = args.out_root / "subsets" / action
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite E13 action: {output}")
        subset = ds.select(selected)
        subset.save_to_disk(str(output))
        saved = load_from_disk(str(output))
        if ([str(x) for x in saved["id"]] != [str(original[i]["id"]) for i in selected]
                or list(saved["texts"]) != [expected_turns(original[i]) for i in selected]):
            raise RuntimeError(f"Saved {action} Arrow changes slot identity or dialogue")
        positions_file = output / "e13_positions.json"
        positions_file.write_text(json.dumps(selected) + "\n")
        contamination = audit_contamination(output, args.root / "LMUData", list(EVAL_REGISTRY))
        contamination_path = args.out_root / f"contamination_{action}.json"
        contamination_path.write_text(json.dumps(contamination, indent=2) + "\n")
        contamination_ready = (contamination["status"] == "clean"
                               and not contamination["skipped_benchmarks"]
                               and set(contamination["benchmarks_checked"]) == set(EVAL_REGISTRY))
        subset_files = [{"path": str(p.relative_to(output)), "bytes": p.stat().st_size,
                         "sha256": sha256(p)} for p in sorted(output.rglob("*")) if p.is_file()]
        contract = {"ready": support["support_pass"] and contamination_ready,
                    "rows_replaced": support["rows_replaced"],
                    "row_coverage": support["row_coverage"],
                    "label_token_coverage": support["label_token_coverage"],
                    "contamination_status": contamination["status"],
                    "skipped_benchmarks": contamination["skipped_benchmarks"],
                    "full_record_disjoint": True,
                    "old_image_overlap_fresh": 0, "slot_n_equal": True}
        manifest = {"action": action, "budget": 10000, "supervised_tokens": sum(slot_n),
                    "train_seed": 29, "data_seed": 29, "sampling_seed": 29,
                    "sampling_salt_prefix": "E13|29|", "subset_path": str(output),
                    "positions_path": positions_file.name, "subset_files": subset_files,
                    "slot_supervised_tokens": slot_n,
                    "sequential_window_supervised_tokens": [sum(slot_n[i:i + 16])
                                                              for i in range(0, 10000, 16)],
                    "sequential_window_note": "Original slot order only; actual sampler windows require runtime observation",
                    "replacement_slots": replaced, "common_anchor_rows": 10000 - len(replaced),
                    "original_json_sha256": audit["source_json_sha256"],
                    "old_selection_manifest": support["old_selection_manifest"],
                    "arrow_id_dialogue_audit": {"path": str(args.audit.resolve()),
                                                "sha256": sha256(args.audit)},
                    "arrow_dataset_revision": "235a8adf266bb6dc02a099dc0221d28dec058f54",
                    "icons_json_sha256": support["icons_json_sha256"],
                    "selector_script_sha256": sha256(Path(__file__)),
                    "support_audit": {"path": str(args.out_root / "support_audit.json"),
                                      "sha256": sha256(args.out_root / "support_audit.json")},
                    "contamination_audit": {"path": str(contamination_path),
                                            "sha256": sha256(contamination_path)},
                    "cpu_contract": contract, **support["actions"][action]}
        manifest_path = output / "e13_selection_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"event": "action_materialized", "action": action,
                          "manifest": str(manifest_path), "cpu_contract": contract}), flush=True)
        if not contamination_ready:
            raise RuntimeError(f"{action} contamination audit requires attention; retained files")


def make_processor_sentinel(args):
    """Copy the frozen eleven source rows into a self-contained tiny dataset."""
    from datasets import DatasetDict, Image, concatenate_datasets, load_from_disk
    audit = json.loads(args.audit.read_text())
    reference = json.loads(args.sentinel.read_text())
    positions = [row["position"] for row in reference["rows"]]
    if (audit["first_shard_only"] or audit["same_position_conversation_count"] != 665298
            or len(positions) != 11 or len(set(positions)) != 11):
        raise RuntimeError("Missing frozen complete audit or eleven-row sentinel")
    output = args.out_root / "processor_sentinel"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite processor sentinel: {output}")
    ds = load_from_disk(str(args.root / "llava_arrow"))
    if isinstance(ds, DatasetDict):
        ds = concatenate_datasets([ds[k] for k in sorted(ds)])
    selected = ds.select(positions)
    ids = [str(i) for i in selected["id"]]
    if ids != [str(row["id"]) for row in reference["rows"]]:
        raise RuntimeError("Source Arrow sentinel IDs differ from frozen E12 records")
    texts = list(selected["texts"])
    raw_images = list(selected.cast_column("images", Image(decode=False))["images"])
    if any(not image or not image.get("bytes") for image in raw_images):
        raise RuntimeError("Sentinel must embed image bytes, not reference external paths")
    image_hashes = [hashlib.sha256(image["bytes"]).hexdigest() for image in raw_images]
    selected = selected.add_column("original_position", positions)
    selected.save_to_disk(str(output))
    saved = load_from_disk(str(output))
    saved_raw_images = list(saved.cast_column("images", Image(decode=False))["images"])
    if ([str(i) for i in saved["id"]] != ids or list(saved["texts"]) != texts
            or list(saved["original_position"]) != positions
            or [hashlib.sha256(image["bytes"]).hexdigest()
                for image in saved_raw_images] != image_hashes):
        raise RuntimeError("Saved sentinel changes IDs, dialogue, image bytes or source mapping")
    files = [{"path": str(p.relative_to(output)), "bytes": p.stat().st_size,
              "sha256": sha256(p)} for p in sorted(output.rglob("*")) if p.is_file()]
    manifest = {"budget": 11, "sample_count": 11, "original_positions": positions,
                "source_sentinel_path": str(args.sentinel.resolve()),
                "source_sentinel_sha256": sha256(args.sentinel),
                "source_arrow_path": str(args.root / "llava_arrow"),
                "arrow_id_dialogue_audit": {"path": str(args.audit.resolve()),
                                            "sha256": sha256(args.audit)},
                "dataset_path": str(output), "dataset_files": files,
                "ids": ids, "source_image_bytes_sha256": image_hashes,
                "self_contained_image_bytes": True,
                "saved_ids_dialogues_images_and_positions_equal_source": True,
                "selector_script_sha256": sha256(Path(__file__))}
    path = output / "e13_processor_sentinel_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"event": "processor_sentinel_complete", "manifest": str(path),
                      "dataset_bytes": sum(f["bytes"] for f in files), **manifest}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--sentinel", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, choices=range(1, 9), default=8)
    parser.add_argument("--stage", choices=("metadata", "actions", "all", "sentinel"), default="all")
    args = parser.parse_args()
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    if args.stage == "sentinel":
        make_processor_sentinel(args)
        return
    original, audit = verify_source(args)
    cache = make_metadata(args, original, audit)
    if args.stage != "metadata":
        make_actions(args, original, audit, cache)


if __name__ == "__main__":
    main()
