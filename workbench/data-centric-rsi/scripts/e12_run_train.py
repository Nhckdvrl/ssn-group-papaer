"""Launch one E12 LLaVA branch with the released fixed recipe and explicit seed.

The released curation-train runner does not expose TrainingArguments.seed in
its allowed overrides: each purported seed would otherwise train with the
default 42. This launcher reproduces its LLaVA argument list and adds the
precommitted seed. It refuses to run until full data/model manifests exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


TRAIN_SCRIPT = Path(
    "/home/xiang/.cache/research/data-centric-rsi/CurationBench/vendor/curation-train/"
    "src/curation_train/train_llava15.py"
)
VENDOR_ROOT = Path("/home/xiang/.cache/research/data-centric-rsi/CurationBench")
EXPECTED_VENDOR_SHA = "24eea1526492c00cee421f5db0793789e00aabb2"
EXPECTED_MODEL_REVISION = "5736a39125fce6ca4d4eb20033ca7c46895878ab"
EXPECTED_DATA_REVISION = "235a8adf266bb6dc02a099dc0221d28dec058f54"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def gpu_free_mb(index: int) -> int:
    output = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,memory.free", "--format=csv,noheader,nounits"],
        text=True,
    )
    for line in output.splitlines():
        gpu, free = (int(x.strip()) for x in line.split(","))
        if gpu == index:
            return free
    raise RuntimeError(f"GPU {index} not found")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--policy", choices=["random", "balanced", "icons_exact", "ards", "icons_released_map"], required=True)
    parser.add_argument("--seed", type=int, choices=[17, 29, 43], required=True)
    parser.add_argument("--gpu", type=int, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vendor_sha = subprocess.check_output(["git", "-C", str(VENDOR_ROOT), "rev-parse", "HEAD"], text=True).strip()
    if vendor_sha != EXPECTED_VENDOR_SHA:
        raise RuntimeError(f"Unexpected Curation-Bench source SHA: {vendor_sha}")
    audit = json.loads(args.audit.read_text())
    if audit.get("first_shard_only") or audit.get("same_position_conversation_count") != audit.get("original_rows"):
        raise RuntimeError("Complete Arrow identity audit has not passed")
    subset = args.root / "subsets" / f"{args.policy}_s{args.seed}"
    selection_file = subset / "e12_selection_manifest.json"
    selection = json.loads(selection_file.read_text())
    if selection["budget"] != 10000 or selection["arrow_dataset_revision"] != EXPECTED_DATA_REVISION:
        raise RuntimeError("Wrong E12 data budget or source revision")
    if selection["original_json_sha256"] != audit["source_json_sha256"]:
        raise RuntimeError("Original JSON changed after selection")
    model_manifest = json.loads((args.root / "llava_init_download.json").read_text())
    if model_manifest["revision"] != EXPECTED_MODEL_REVISION:
        raise RuntimeError("Wrong E12 parent model revision")
    model = args.root / "llava_init"
    if not all((model / f"model-0000{i}-of-00003.safetensors").exists() for i in (1, 2, 3)):
        raise RuntimeError("LLaVA init weights are incomplete")
    if subprocess.run(
        ["git", "-C", str(VENDOR_ROOT), "diff", "--quiet", "--", "vendor/curation-train/src/curation_train/train_llava15.py"],
        check=False,
    ).returncode != 0:
        raise RuntimeError("Pinned trainer source has local modifications")
    if not args.dry_run and gpu_free_mb(args.gpu) < 75000:
        raise RuntimeError("GPU has less than 75 GB free; full finetune would contend")

    run_dir = args.out_root / f"{args.policy}_s{args.seed}"
    if run_dir.exists():
        raise FileExistsError(f"Refusing to overwrite E12 run: {run_dir}")
    if not args.dry_run:
        run_dir.mkdir(parents=True)
    config = {
        "method": "llava",
        "data_path": str(subset),
        "model_name_or_path": str(model),
    }
    config_path = run_dir / "train_config.json"
    if not args.dry_run:
        config_path.write_text(json.dumps(config, indent=2) + "\n")
    output = run_dir / "model"
    command = [
        sys.executable, "-m", "accelerate.commands.launch",
        "--num_processes", "1", "--gpu_ids", "0",
        str(TRAIN_SCRIPT), "--config_json", str(config_path),
        "--output_dir", str(output),
        "--num_train_epochs", "1",
        "--per_device_train_batch_size", "1",
        "--gradient_accumulation_steps", "16",
        "--learning_rate", "2e-5",
        "--weight_decay", "0.0",
        "--warmup_ratio", "0.03",
        "--lr_scheduler_type", "cosine",
        "--bf16", "--optim", "adamw_torch_fused",
        "--gradient_checkpointing",
        "--dataloader_num_workers", "2",
        "--remove_unused_columns", "False",
        "--save_strategy", "no", "--report_to", "none",
        "--logging_steps", "1",
        "--seed", str(args.seed),
        "--data_seed", str(args.seed),
    ]
    launch = {
        "command": command,
        "policy": args.policy,
        "seed": args.seed,
        "gpu": args.gpu,
        "parent_revision": EXPECTED_MODEL_REVISION,
        "parent_path": str(model),
        "selection_manifest_sha256": sha256(selection_file),
        "full_audit_sha256": sha256(args.audit),
        "vendor_sha": vendor_sha,
        "train_script_sha256": sha256(TRAIN_SCRIPT),
        "python": sys.executable,
        "difference_from_released_runner": "Explicit seed and data_seed; released runner silently uses TrainingArguments default 42 for every dataset seed.",
    }
    if args.dry_run:
        print(json.dumps(launch, indent=2))
        return
    (run_dir / "launch_manifest.json").write_text(json.dumps(launch, indent=2) + "\n")
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    env["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    start = time.monotonic()
    with (run_dir / "train_stdout.log").open("w") as stdout, (run_dir / "train_stderr.log").open("w") as stderr:
        result = subprocess.run(command, env=env, stdout=stdout, stderr=stderr, check=False)
    summary = {
        "returncode": result.returncode,
        "wall_seconds": round(time.monotonic() - start, 1),
        "model_saved": (output / "model.safetensors").exists() or bool(list(output.glob("model-*.safetensors"))),
        "run_dir": str(run_dir),
    }
    (run_dir / "completion.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))
    if result.returncode != 0 or not summary["model_saved"]:
        raise RuntimeError("E12 train failed; inspect retained stdout/stderr and completion.json")


if __name__ == "__main__":
    main()
