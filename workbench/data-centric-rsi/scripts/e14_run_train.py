"""Two E14 source-only branches under the unchanged E12/E13 training recipe.

The frozen E13 observer is reused without changing its globals or behavior.
Its window expectations come from this action's actual label vector; E13's
549353-token matching requirement is deliberately absent from this launcher.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import e13_run_train as baseline

ACTION = "source_only_fresh"
SOURCE_COUNTS = {"coco": 6460, "gqa": 1589, "ocr_vqa": 1028,
                 "vg": 755, "textvqa": 85, "text-only": 83}
E13_LAUNCHER_SHA = "2217d7741525303de2a03ba9a097bbb1907b2824603662ea276333a0e2ce7550"


def verify_selection(path: Path) -> tuple[dict, Path]:
    read, require, sha = baseline.read, baseline.require, baseline.sha256
    selection = read(path)
    require(selection["action"] == ACTION and selection["budget"] == baseline.BUDGET,
            "Wrong E14 action or row budget")
    require(all(selection[k] == baseline.SEED for k in
                ("train_seed", "data_seed", "sampling_seed")), "E14 seeds must be 29")
    ns = selection["slot_supervised_tokens"]
    require(len(ns) == baseline.BUDGET and all(type(n) is int and n >= 0 for n in ns)
            and sum(ns) == selection["supervised_tokens"] and sum(ns) > 0,
            "E14 label vector does not describe the actual action")
    require(selection["sequential_window_supervised_tokens"] ==
            [sum(ns[j:j + 16]) for j in range(0, baseline.BUDGET, 16)],
            "E14 original-slot label windows differ")
    require(selection["source_counts"] == SOURCE_COUNTS, "Frozen source recipe changed")
    c = selection["cpu_contract"]
    require(c["ready"] and c["contamination_status"] == "clean"
            and not c["skipped_benchmarks"] and c["full_record_disjoint"]
            and c["old_image_overlap_fresh"] == 0 and c["rows_replaced"] == 10000
            and c["common_anchor_rows"] == 0 and c["same_source_slots"]
            and c["outside_icons"], "E14 full-refresh identity contract failed")
    require(selection["arrow_dataset_revision"] == baseline.EXPECTED_DATA_REVISION,
            "Arrow revision changed")
    for key in ("arrow_id_dialogue_audit", "old_selection_manifest",
                "support_audit", "contamination_audit"):
        ref = selection[key]
        p = baseline.bound_path(ref["path"], path.parent)
        require(sha(p) == ref["sha256"], f"Frozen {key} changed")
    audit = read(baseline.bound_path(selection["arrow_id_dialogue_audit"]["path"], path.parent))
    require(not audit.get("first_shard_only") and audit["original_rows"] == 665298
            and audit["arrow_rows"] == 665298 and audit["same_position_count"] == 665298
            and audit["same_id_multiset"] is True
            and audit["same_position_conversation_count"] == 665298
            and audit["source_json_sha256"] == selection["original_json_sha256"],
            "Inherited full Arrow/JSON identity changed")
    old = read(baseline.bound_path(selection["old_selection_manifest"]["path"], path.parent))
    require(old["policy"] == "icons_exact" and old["seed"] == 17
            and old["budget"] == 10000, "Wrong old S asset")
    contamination = read(baseline.bound_path(selection["contamination_audit"]["path"], path.parent))
    require(contamination["status"] == "clean" and not contamination["skipped_benchmarks"]
            and len(set(contamination["benchmarks_checked"])) == 8,
            "New action eight-task contamination check incomplete")
    subset = baseline.bound_path(selection["subset_path"], path.parent)
    declared = set()
    for entry in selection["subset_files"]:
        p = subset / entry["path"]
        require(p.resolve().is_relative_to(subset.resolve()) and p.stat().st_size == entry["bytes"]
                and sha(p) == entry["sha256"], f"Saved E14 subset changed: {p}")
        declared.add(entry["path"])
    require({str(p.relative_to(subset)) for p in subset.rglob("*.arrow")} <= declared,
            "Unlisted Arrow shard")
    positions = read(baseline.bound_path(selection["positions_path"], path.parent))
    require(len(positions) == 10000 and len(set(positions)) == 10000
            and all(type(i) is int and 0 <= i < 665298 for i in positions),
            "E14 positions invalid or duplicated")
    import hashlib
    require(hashlib.sha256(("\n".join(map(str, positions)) + "\n").encode()).hexdigest()
            == selection["selected_positions_sha256"], "E14 positions SHA differs")
    from datasets import load_from_disk
    require(len(load_from_disk(str(subset))) == 10000, "Saved subset is not 10K rows")
    return selection, subset


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--_observe-trainer":
        baseline.observe_child()
        return
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--e12-root", type=Path, required=True)
    p.add_argument("--init-parent", type=Path, required=True)
    p.add_argument("--used-parent", type=Path, required=True)
    p.add_argument("--processor-sentinel-path", type=Path, required=True)
    p.add_argument("--parent", choices=("init", "used"), required=True)
    p.add_argument("--gpu", type=int, required=True)
    p.add_argument("--out-root", type=Path, required=True)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    require, read, sha = baseline.require, baseline.read, baseline.sha256
    require(sha(Path(baseline.__file__)) == E13_LAUNCHER_SHA, "Frozen E13 observer changed")
    vendor = subprocess.check_output(["git", "-C", str(baseline.VENDOR_ROOT),
                                      "rev-parse", "HEAD"], text=True).strip()
    require(vendor == baseline.EXPECTED_VENDOR_SHA, "Vendor revision changed")
    subprocess.run(["git", "-C", str(baseline.VENDOR_ROOT), "diff", "--exit-code", "--quiet",
                    "--", "vendor/curation-train/src/curation_train/train_llava15.py"], check=True)
    selection_path = a.root / "subsets" / ACTION / "e14_selection_manifest.json"
    selection, subset = verify_selection(selection_path)
    init_download = a.e12_root / "llava_init_download.json"
    require(read(init_download)["revision"] == baseline.EXPECTED_MODEL_REVISION, "Init revision changed")
    for i, expected in enumerate(baseline.INIT_SHAS, 1):
        require(sha(a.init_parent / f"model-0000{i}-of-00003.safetensors") == expected,
                "Init weights differ from the E12 paper parent")
    old_dir = a.used_parent.parent
    old_launch, old_completion = read(old_dir / "launch_manifest.json"), read(old_dir / "completion.json")
    require(old_completion["returncode"] == 0 and old_completion["model_saved"]
            and old_launch["policy"] == "icons_exact" and old_launch["seed"] == 17
            and old_launch["vendor_sha"] == baseline.EXPECTED_VENDOR_SHA
            and old_launch["parent_revision"] == baseline.EXPECTED_MODEL_REVISION
            and old_launch["train_script_sha256"] == sha(baseline.TRAIN_SCRIPT)
            and old_launch["selection_manifest_sha256"] == selection["old_selection_manifest"]["sha256"],
            "Used parent is not the successful frozen E12 ICONS branch")
    parent = a.init_parent if a.parent == "init" else a.used_parent
    parent_files = baseline.file_manifest(parent)
    frozen_parents = read(Path(__file__).resolve().parents[1] /
                          "results/E13_asset_staging_manifest.json")
    if a.parent == "used":
        require(parent_files == frozen_parents["parent_source_hashes"]["models"]["used"]["files"],
                "Used model content differs from E13's frozen E12 parent")
    packages = baseline.package_audit()
    processor = baseline.processor_and_sampler_audit(a.init_parent, a.used_parent,
                                                    a.processor_sentinel_path,
                                                    selection["slot_supervised_tokens"])
    require(all(n > 0 for n in processor["expected_window_supervised_tokens"]),
            "A sampled E14 accumulation window has no supervised tokens")
    run_dir = a.out_root / f"{a.parent}_{ACTION}_s29"
    require(not run_dir.exists(), f"Preserve existing run: {run_dir}")
    config = {"method": "llava", "data_path": str(subset), "model_name_or_path": str(parent)}
    command = [sys.executable, "-m", "accelerate.commands.launch", "--num_processes", "1",
               "--gpu_ids", str(a.gpu), str(Path(__file__).resolve()), "--_observe-trainer",
               "--config_json", str(run_dir / "train_config.json"), "--output_dir", str(run_dir / "model"),
               "--num_train_epochs", "1", "--per_device_train_batch_size", "1",
               "--gradient_accumulation_steps", "16", "--learning_rate", "2e-5", "--weight_decay", "0.0",
               "--warmup_ratio", "0.03", "--lr_scheduler_type", "cosine", "--bf16",
               "--optim", "adamw_torch_fused", "--gradient_checkpointing", "--dataloader_num_workers", "2",
               "--remove_unused_columns", "False", "--save_strategy", "no", "--report_to", "none",
               "--logging_steps", "1", "--seed", "29", "--data_seed", "29"]
    manifest = {"experiment": "E14", "parent": a.parent, "action": ACTION,
                "seed": 29, "gpu": a.gpu, "command": command, "config": config,
                "expected_rows": 10000, "expected_steps": 625,
                "expected_supervised_tokens": selection["supervised_tokens"],
                "optimizer_scheduler_reset": True, "resume_from_checkpoint": None,
                "parent_path": str(parent), "parent_file_manifest": parent_files,
                "init_revision": baseline.EXPECTED_MODEL_REVISION,
                "init_download_manifest_sha256": sha(init_download),
                "e12_launch_manifest": old_launch, "e12_completion": old_completion,
                "selection_manifest_path": str(selection_path), "selection_manifest_sha256": sha(selection_path),
                "selection_slot_supervised_tokens": selection["slot_supervised_tokens"],
                "processor_sampler_audit": processor, "packages": packages, "vendor_sha": vendor,
                "train_script_sha256": sha(baseline.TRAIN_SCRIPT), "launcher_sha256": sha(Path(__file__)),
                "reused_e13_observer_sha256": sha(Path(baseline.__file__)), "python": sys.executable,
                "normalization": "Unchanged sum CE / this action's actual 16-row label denominator",
                "device_mapping": "Outer physical CUDA_VISIBLE_DEVICES and Accelerate gpu_ids agree; child logical 0"}
    if a.dry_run:
        print(json.dumps(manifest, indent=2))
        return
    require(baseline.gpu_free_mb(a.gpu) >= 75000, "GPU not idle enough for full-parameter training")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "train_config.json").write_text(json.dumps(config, indent=2) + "\n")
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    env = os.environ.copy()
    # Compatibility keys consumed by the unchanged, read-only E13 observer.
    env.update(CUDA_VISIBLE_DEVICES=str(a.gpu), CUDA_DEVICE_ORDER="PCI_BUS_ID",
               E13_RUN_MANIFEST=str(run_dir / "run_manifest.json"),
               E13_RUNTIME_MANIFEST=str(run_dir / "runtime_manifest.json"),
               E13_WINDOW_TRACE=str(run_dir / "window_trace.jsonl"))
    start = time.monotonic()
    with (run_dir / "train_stdout.log").open("w") as out, (run_dir / "train_stderr.log").open("w") as err:
        result = subprocess.run(command, env=env, stdout=out, stderr=err, check=False)
    trace = run_dir / "window_trace.jsonl"
    windows = len(trace.read_text().splitlines()) if trace.exists() else 0
    saved = bool(list((run_dir / "model").glob("model*.safetensors")))
    completion = {"returncode": result.returncode, "wall_seconds": round(time.monotonic() - start, 3),
                  "model_saved": saved, "observed_windows": windows, "run_dir": str(run_dir),
                  "preflight_included": False, "preflight_cost_source": "E14 train_queue wrapper"}
    (run_dir / "completion.json").write_text(json.dumps(completion, indent=2) + "\n")
    print(json.dumps(completion))
    require(result.returncode == 0 and saved and windows == 625,
            "E14 failed; retain all original artifacts and costs")


if __name__ == "__main__":
    main()
