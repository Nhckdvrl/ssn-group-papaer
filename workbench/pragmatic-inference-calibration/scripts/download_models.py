#!/usr/bin/env python3
"""Pinned download with bounded retry; no partially downloaded model is evaluated."""
import argparse
import json
import time
from pathlib import Path
from huggingface_hub import snapshot_download

ap = argparse.ArgumentParser()
ap.add_argument("--model-id", required=True)
ap.add_argument("--revision", required=True)
ap.add_argument("--root", type=Path, required=True)
ap.add_argument("--pytorch-only", action="store_true", help="Explicit fallback for public checkpoints released only as PyTorch weights")
args = ap.parse_args()
target = args.root / "models" / args.model_id.split("/")[-1]
for attempt in range(1, 4):
    try:
        snapshot_download(args.model_id, revision=args.revision, local_dir=target,
            allow_patterns=["*.json", "*.bin" if args.pytorch_only else "*.safetensors", "*.txt", "*.model", "*.jinja"], max_workers=2)
        index = target / ("pytorch_model.bin.index.json" if args.pytorch_only else "model.safetensors.index.json")
        if index.exists():
            files = set(json.loads(index.read_text())["weight_map"].values())
            assert all((target / f).is_file() and (target / f).stat().st_size > 0 for f in files)
        else:
            assert list(target.glob("*.bin" if args.pytorch_only else "*.safetensors")), "No model weights downloaded"
        (target / "DOWNLOAD_COMPLETE.json").write_text(json.dumps({"model": args.model_id, "revision": args.revision}))
        print(json.dumps({"download_complete": str(target)}), flush=True)
        break
    except Exception as error:
        print(json.dumps({"attempt": attempt, "error_type": type(error).__name__}), flush=True)
        if attempt == 3:
            raise
        time.sleep(5 * attempt)
