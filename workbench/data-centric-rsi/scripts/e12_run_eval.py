"""Run and validate the pinned Curation-Bench eight-task evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


BENCHMARK_SRC = Path("/home/xiang/.cache/research/data-centric-rsi/CurationBench/src")
VENDOR_ROOT = BENCHMARK_SRC.parent
EXPECTED_VENDOR_SHA = "24eea1526492c00cee421f5db0793789e00aabb2"
TASK = BENCHMARK_SRC / "benchmark/tasks/llava665k_llava_8bench_10k_unlimited.yaml"
sys.path.insert(0, str(BENCHMARK_SRC))
from benchmark.core.task import load_task_spec  # noqa: E402
from benchmark.tools.evaluation import run_evaluation  # noqa: E402

from e12_validate_eval import validate_results  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--eval-data", type=Path, required=True)
    parser.add_argument("--judge-url", required=True)
    parser.add_argument("--gpu", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    vendor_sha = subprocess.check_output(
        ["git", "-C", str(VENDOR_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    if vendor_sha != EXPECTED_VENDOR_SHA:
        raise RuntimeError(f"Unexpected Curation-Bench SHA: {vendor_sha}")
    if not args.model.is_dir() or len(list(args.eval_data.glob("*.tsv"))) < 8:
        raise RuntimeError("Model directory or eight eval TSVs are missing")
    if not args.judge_url.endswith("/v1/chat/completions"):
        raise ValueError("Judge URL must be the full chat/completions endpoint")
    if args.out.exists():
        raise FileExistsError(f"Refusing to overwrite evaluation: {args.out}")
    args.out.mkdir(parents=True)

    # The pinned vendor imports an absent submission-only helper before it
    # evaluates any dataset. This shim provides failing stubs for those two
    # unused branches without editing the pinned source or changing E12 tasks.
    compat_dir = Path(__file__).resolve().parent.parent / "compat"
    if not (compat_dir / "sitecustomize.py").is_file():
        raise RuntimeError(f"Missing E12 import shim: {compat_dir}")
    os.environ["PYTHONPATH"] = os.pathsep.join(
        (str(compat_dir), os.environ.get("PYTHONPATH", ""))
    )

    task = load_task_spec(TASK)
    config = task.eval_config
    assert config is not None
    config.judge_api_base = args.judge_url
    config.gpu_id = args.gpu
    config.timeout_seconds = 28800
    manifest = {
        "source_git_sha": vendor_sha,
        "task_yaml_sha256": sha256(TASK),
        "model_path": str(args.model),
        "eval_data_path": str(args.eval_data),
        "judge_url": args.judge_url,
        "judge_model": config.judge_model,
        "benchmarks": config.benchmarks,
        "use_vllm": config.use_vllm,
        "mode": config.mode,
        "api_nproc": config.api_nproc,
        "gpu": args.gpu,
        "vlmeval_venv": os.environ.get("UV_PROJECT_ENVIRONMENT", ""),
        "import_shim": str(compat_dir / "sitecustomize.py"),
    }
    (args.out / "eval_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    start = time.monotonic()
    result = run_evaluation(
        str(args.model), task.model_key, config, args.out,
        eval_data_dir=str(args.eval_data),
    )
    result["wall_seconds"] = round(time.monotonic() - start, 1)
    (args.out / "completion.json").write_text(json.dumps(result, indent=2) + "\n")
    if result["status"] != "completed":
        raise RuntimeError(f"Evaluation process failed: {result}")
    for log_name in ("eval_stdout.txt", "eval_stderr.txt"):
        if "will use exact matching for evaluation" in (args.out / log_name).read_text(errors="replace"):
            raise RuntimeError(f"Judge fallback detected in {log_name}")
    score_path = args.out / "results/results.json"
    scores = validate_results(json.loads(score_path.read_text()))
    scores["source_results"] = str(score_path)
    (args.out / "validated_scores.json").write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps({"wall_seconds": result["wall_seconds"], "accuracy_percent": scores["accuracy_percent"]}))


if __name__ == "__main__":
    main()
