"""Materialize preregistered E14 source-only fresh action on CPU.

Reuse E13's SHA-bound complete metadata and E12's complete Arrow audit. Never
rank by labels, losses or evaluation scores; keep old source slots only. Failed
outputs remain on disk and a second invocation refuses to overwrite them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import socket
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from e12_icons_mapping_audit import row_key
from e12_make_subsets import hash_lines, sha256

ACTION = "source_only_fresh"
SALT = "E14|29|source_only_fresh"
COUNTS = {"coco": 6460, "gqa": 1589, "ocr_vqa": 1028,
          "vg": 755, "textvqa": 85, "text-only": 83}
TRAIN_SCRIPT = Path("/home/xiang/.cache/research/data-centric-rsi/CurationBench/"
                    "vendor/curation-train/src/curation_train/train_llava15.py")


def write_new(path, value):
    with path.open("x") as file:
        file.write(json.dumps(value, indent=2) + "\n")


def file_ref(path):
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def stats(values):
    ordered = sorted(values)
    return {"sum": sum(values), "mean": sum(values) / len(values),
            "median": ordered[len(values) // 2], "p95": ordered[int(len(values) * .95)],
            "min": ordered[0], "max": ordered[-1]}


def dose(records):
    return {"rows": len(records),
            "supervised_tokens": stats([r["supervised_tokens"] for r in records]),
            "input_tokens": stats([r["input_tokens"] for r in records]),
            "full_input_tokens": stats([r["full_input_tokens"] for r in records]),
            "unique_full_records": len({r["row_key"] for r in records}),
            "unique_images": len({r["image"] for r in records if r["image"]}),
            "image_rows": sum(bool(r["image"]) for r in records),
            "zero_supervised_rows": sum(r["supervised_tokens"] == 0 for r in records),
            "truncated_rows": sum(r["truncated"] for r in records),
            "rows_without_final_eos": sum(not r["last_supervised_token_is_eos"] for r in records)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="Existing E12 assets")
    parser.add_argument("--e13-root", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--sentinel", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    started = time.monotonic()
    phases = {}
    args.out_root.mkdir(parents=True, exist_ok=True)
    output = args.out_root / "subsets" / ACTION
    run_path = args.out_root / "cpu_materialization_started.json"
    if output.exists() or run_path.exists() or args.summary.exists():
        raise FileExistsError("Preserve existing E14 outputs; use a versioned path after review")
    write_new(run_path, {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                         "hostname": socket.gethostname(), "argv": sys.argv,
                         "selector_script_sha256": sha256(Path(__file__))})

    checkpoint = time.monotonic()
    audit = json.loads(args.audit.read_text())
    if (audit["first_shard_only"] or audit["original_rows"] != 665298
            or audit["arrow_rows"] != 665298 or audit["same_position_count"] != 665298
            or audit["same_position_conversation_count"] != 665298
            or not audit["same_id_multiset"]):
        raise RuntimeError("Frozen E12 complete Arrow audit did not pass")
    original_path = args.root / "llava_json/llava_v1_5_mix665k.json"
    metadata_path = args.e13_root / "pool_metadata.jsonl"
    metadata_identity_path = args.e13_root / "pool_metadata_identity.json"
    identity = json.loads(metadata_identity_path.read_text())
    if (sha256(original_path) != audit["source_json_sha256"]
            or identity["identity"]["source_json_sha256"] != audit["source_json_sha256"]
            or identity["rows"] != 665298 or identity["sentinel_matched"] != 11
            or sha256(metadata_path) != identity["cache_sha256"]
            or sha256(Path(__file__).with_name("e12_token_preflight.py")) !=
            identity["identity"]["e12_token_script_sha256"]
            or sha256(TRAIN_SCRIPT) != identity["identity"]["trainer_sha256"]):
        raise RuntimeError("Frozen metadata source/token implementation identity changed")
    for name, expected_hash in identity["identity"]["processor_json_sha256"].items():
        if sha256(args.root / "llava_init" / name) != expected_hash:
            raise RuntimeError(f"Frozen processor file changed: {name}")
    sentinel = json.loads(args.sentinel.read_text())
    if len(sentinel["rows"]) != 11:
        raise RuntimeError("Missing frozen eleven-row actual processor sentinel")
    metadata = [json.loads(line) for line in metadata_path.open()]
    if len(metadata) != 665298 or any(r["position"] != i for i, r in enumerate(metadata)):
        raise RuntimeError("Metadata no longer covers all source positions in order")
    for ref in sentinel["rows"]:
        if any(metadata[ref["position"]][k] != ref[k] for k in (
                "input_tokens", "supervised_tokens", "last_supervised_token_is_eos")):
            raise RuntimeError("Metadata differs from frozen actual row processor sentinel")
    phases["source_metadata_identity_seconds"] = time.monotonic() - checkpoint

    checkpoint = time.monotonic()
    icons_path = args.root / "icons_json/llava-icons-133k.json"
    replay_manifest_path = args.e13_root / "subsets/replay/e13_selection_manifest.json"
    replay = json.loads(replay_manifest_path.read_text())
    if sha256(icons_path) != replay["icons_json_sha256"]:
        raise RuntimeError("Frozen ICONS pool changed")
    icons_keys = {row_key(row) for row in json.loads(icons_path.read_text())}
    if len(icons_keys) != 133046:
        raise RuntimeError("Unexpected ICONS complete membership count")
    old_path = args.e13_root / "subsets/replay/e13_positions.json"
    old = json.loads(old_path.read_text())
    old_records = [metadata[i] for i in old]
    old_manifest_path = Path(replay["old_selection_manifest"]["path"])
    old_manifest = json.loads(old_manifest_path.read_text())
    if (len(old) != 10000 or len(set(old)) != 10000
            or hash_lines(list(map(str, old))) != replay["selected_positions_sha256"]
            or hash_lines([r["row_key"] for r in old_records]) != replay["selected_full_records_sha256"]
            or sha256(old_manifest_path) != replay["old_selection_manifest"]["sha256"]
            or old_manifest["selected_positions_sha256"] != replay["selected_positions_sha256"]
            or old_manifest["original_json_sha256"] != audit["source_json_sha256"]
            or dict(Counter(r["source"] for r in old_records)) != COUNTS
            or sum(r["supervised_tokens"] for r in old_records) != 549353):
        raise RuntimeError("Frozen S/replay identity or source/label reference changed")
    old_keys = {r["row_key"] for r in old_records}
    old_images = {r["image"] for r in old_records if r["image"]}
    slots = defaultdict(list)
    pools = defaultdict(list)
    exclusions = Counter()
    for slot, row in enumerate(old_records):
        slots[row["source"]].append(slot)
    seen = set()
    for row in metadata:
        if row["row_key"] in old_keys:
            exclusions["old_full_records"] += 1
        elif row["image"] and row["image"] in old_images:
            exclusions["old_image_paths"] += 1
        elif row["row_key"] in icons_keys:
            exclusions["inside_ICONS_pool"] += 1
        elif row["row_key"] in seen:
            exclusions["duplicate_fresh_full_records"] += 1
        else:
            seen.add(row["row_key"])
            pools[row["source"]].append(row["position"])
    rng = random.Random(int.from_bytes(hashlib.sha256(SALT.encode()).digest(), "big"))
    selected = [None] * 10000
    for source, source_slots in sorted(slots.items()):
        for slot, position in zip(source_slots, rng.sample(pools[source], len(source_slots))):
            selected[slot] = position
    records = [metadata[i] for i in selected]
    keys = {r["row_key"] for r in records}
    images = {r["image"] for r in records if r["image"]}
    if (len(keys) != 10000 or keys & (old_keys | icons_keys) or images & old_images
            or [r["source"] for r in records] != [r["source"] for r in old_records]):
        raise RuntimeError("Selection violates full-fresh/pool/source-slot contract")
    ns = [r["supervised_tokens"] for r in records]
    law_path = args.e13_root / "subsets/fresh_law/e13_positions.json"
    law_manifest_path = args.e13_root / "subsets/fresh_law/e13_selection_manifest.json"
    law = json.loads(law_path.read_text())
    law_manifest = json.loads(law_manifest_path.read_text())
    if hash_lines(list(map(str, law))) != law_manifest["selected_positions_sha256"]:
        raise RuntimeError("Frozen E13 fresh-law positions changed")
    law_records = [metadata[i] for i in law]
    if hash_lines([r["row_key"] for r in law_records]) != law_manifest["selected_full_records_sha256"]:
        raise RuntimeError("Frozen E13 fresh-law full-record identity changed")
    action_dose = dose(records)
    per_source = {source: dose([r for r in records if r["source"] == source])
                  for source in sorted(slots)}
    overlaps = {"old_full_records": len(keys & old_keys),
                "old_original_image_paths": len(images & old_images),
                "ICONS_full_records": len(keys & icons_keys),
                "E13_fresh_law_full_records": len(keys & {r["row_key"] for r in law_records}),
                "E13_fresh_law_original_image_paths": len(images & {r["image"] for r in law_records if r["image"]}),
                "E13_fresh_law_same_slot_records": sum(a == b for a, b in zip(selected, law)),
                "qualification": "E13 fresh-law overlap is allowed and never used to select records; image-path exclusion is not pixel deduplication."}
    phases["membership_and_source_sampling_seconds"] = time.monotonic() - checkpoint
    print(json.dumps({"event": "selection_frozen", "supervised_tokens": sum(ns),
                      "source_counts": dict(Counter(r["source"] for r in records)),
                      "overlaps": overlaps}), flush=True)

    checkpoint = time.monotonic()
    from datasets import DatasetDict, concatenate_datasets, load_from_disk
    from e12_index_audit import expected_turns
    sys.path.insert(0, "/home/xiang/.cache/research/data-centric-rsi/CurationBench/src")
    from benchmark.tools.contamination import EVAL_REGISTRY, audit_contamination
    original = json.loads(original_path.read_text())
    ds = load_from_disk(str(args.root / "llava_arrow"))
    if isinstance(ds, DatasetDict):
        ds = concatenate_datasets([ds[k] for k in sorted(ds)])
    if len(ds) != 665298:
        raise RuntimeError("Original Arrow snapshot row count changed")
    subset = ds.select(selected)
    subset.save_to_disk(str(output))
    saved = load_from_disk(str(output))
    if ([str(x) for x in saved["id"]] != [str(original[i]["id"]) for i in selected]
            or list(saved["texts"]) != [expected_turns(original[i]) for i in selected]
            or any(row_key(original[i]) != metadata[i]["row_key"] for i in selected)):
        raise RuntimeError("New saved subset ID/full dialogue/full record identity changed")
    positions_path = output / "e14_positions.json"
    write_new(positions_path, selected)
    phases["import_materialize_save_load_identity_seconds"] = time.monotonic() - checkpoint

    checkpoint = time.monotonic()
    contamination = audit_contamination(output, args.root / "LMUData", list(EVAL_REGISTRY))
    contamination_path = args.out_root / "contamination_source_only_fresh.json"
    write_new(contamination_path, contamination)
    contamination_ready = (contamination["status"] == "clean"
                           and not contamination["skipped_benchmarks"]
                           and set(contamination["benchmarks_checked"]) == set(EVAL_REGISTRY))
    phases["eight_task_contamination_seconds"] = time.monotonic() - checkpoint
    checkpoint = time.monotonic()
    files = [{"path": str(p.relative_to(output)), "bytes": p.stat().st_size,
              "sha256": sha256(p)} for p in sorted(output.rglob("*")) if p.is_file()]
    phases["subset_file_sha256_seconds"] = time.monotonic() - checkpoint
    contract = {"ready": contamination_ready, "all_rows_fresh": True,
                "rows_replaced": 10000, "row_coverage": 1.0, "common_anchor_rows": 0,
                "source_slot_equal": True, "same_source_slots": True,
                "supervision_matching_required": False, "full_record_disjoint": True,
                "old_image_overlap_fresh": 0, "outside_ICONS_pool": True, "outside_icons": True,
                "contamination_status": contamination["status"],
                "skipped_benchmarks": contamination["skipped_benchmarks"],
                "saved_ids_full_dialogue_and_record_identity_equal_source": True}
    support_path = args.out_root / "support_audit.json"
    write_new(support_path, {"action": ACTION, "sampling_seed": 29, "sampling_salt": SALT,
                             "cpu_contract": contract, "dose": action_dose,
                             "dose_by_source": per_source, "overlaps": overlaps,
                             "selected_positions_sha256": hash_lines(list(map(str, selected))),
                             "selected_full_records_sha256": hash_lines([r["row_key"] for r in records]),
                             "n_matching_or_label_coverage_gate": False})
    manifest = {"action": ACTION, "budget": 10000, "supervised_tokens": sum(ns),
                "sampling_seed": 29, "train_seed": 29, "data_seed": 29,
                "sampling_salt": SALT, "source_iteration": "sorted source names",
                "candidate_iteration": "original positions ascending; first full-key duplicate retained",
                "selection_rule": "Uniform random without replacement per source, preserve old source slots; no label/input/score matching or anchors",
                "subset_path": str(output), "positions_path": positions_path.name,
                "subset_files": files, "slot_supervised_tokens": ns,
                "slot_sources": [r["source"] for r in records],
                "slot_input_tokens": [r["input_tokens"] for r in records],
                "sequential_window_supervised_tokens": [sum(ns[i:i + 16]) for i in range(0, 10000, 16)],
                "sequential_window_note": "Original slot order only; actual seed29 sampler windows and labels must be checked at runtime",
                "replacement_slots": list(range(10000)), "common_anchor_rows": 0,
                "selected_positions_sha256": hash_lines(list(map(str, selected))),
                "selected_full_records_sha256": hash_lines([r["row_key"] for r in records]),
                "original_json_sha256": audit["source_json_sha256"],
                "arrow_dataset_revision": "235a8adf266bb6dc02a099dc0221d28dec058f54",
                "arrow_id_dialogue_audit": file_ref(args.audit),
                "metadata_cache_sha256": identity["cache_sha256"],
                "metadata_identity": file_ref(metadata_identity_path),
                "old_selection_manifest": replay["old_selection_manifest"],
                "icons_json_sha256": replay["icons_json_sha256"],
                "processor_sentinel": {"path": str(args.e13_root / "processor_sentinel"),
                                       "original_reference": file_ref(args.sentinel), "reused": True},
                "selector_script_sha256": sha256(Path(__file__)),
                "contamination_audit": file_ref(contamination_path),
                "support_audit": file_ref(support_path),
                "source_counts": dict(Counter(r["source"] for r in records)),
                "input_tokens": action_dose["input_tokens"]["sum"],
                "full_input_tokens": action_dose["full_input_tokens"]["sum"],
                "dose": action_dose, "dose_by_source": per_source, "overlaps": overlaps,
                "reference_E13_supervised_tokens": 549353,
                "supervised_tokens_delta_vs_E13": sum(ns) - 549353,
                "supervised_tokens_ratio_vs_E13": sum(ns) / 549353,
                "candidate_source_counts": {source: len(pools[source]) for source in sorted(slots)},
                "exclusions": dict(exclusions), "cpu_contract": contract,
                "cpu_wall_phases_seconds": phases,
                "cpu_wall_to_manifest_seconds": time.monotonic() - started,
                "hostname": socket.gethostname(), "completed_at_utc": datetime.now(timezone.utc).isoformat()}
    manifest_path = output / "e14_selection_manifest.json"
    write_new(manifest_path, manifest)
    summary = {k: v for k, v in manifest.items() if k not in (
        "slot_supervised_tokens", "slot_input_tokens", "slot_sources", "replacement_slots",
        "sequential_window_supervised_tokens")}
    summary.update({"manifest_path": str(manifest_path), "manifest_sha256": sha256(manifest_path),
                    "gpu_runs_started": 0, "cpu_wall_total_seconds": time.monotonic() - started,
                    "contamination_summary": {"status": contamination["status"],
                        "benchmarks_checked": contamination["benchmarks_checked"],
                        "skipped_benchmarks": contamination["skipped_benchmarks"],
                        "hash_exact": contamination["hash_exact"],
                        "ngram_near_counts": {k: {"total_eval_pairs": v["total_eval_pairs"], "near_matches": v["near_matches"]}
                                              for k, v in contamination["ngram_near"].items()}},
                    "label_provenance": "E13 full-pool SHA-bound metadata, frozen EOS token code and processor files; frozen 11 actual-row sentinels reused; E14 runtime checks all selected labels",
                    "training_variance_ci": "unknown; CPU data action only"})
    write_new(args.summary, summary)
    print(json.dumps({"event": "e14_cpu_complete", "manifest": str(manifest_path),
                      "manifest_sha256": summary["manifest_sha256"], "cpu_contract": contract,
                      "cpu_wall_total_seconds": summary["cpu_wall_total_seconds"]}), flush=True)
    if not contamination_ready:
        raise RuntimeError("Contamination requires attention; retained all E14 outputs")


if __name__ == "__main__":
    main()
