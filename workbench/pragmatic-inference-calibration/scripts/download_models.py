#!/usr/bin/env python3
"""Pinned download with bounded retry; no partially downloaded model is evaluated."""
import argparse
import json
import time
from pathlib import Path
from download_network import configure_direct_downloads
ENDPOINT = configure_direct_downloads()
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
            endpoint=ENDPOINT, token=False,
            allow_patterns=["*.json", "*.txt", "*.model", "*.jinja"], max_workers=2)
        index = target / ("pytorch_model.bin.index.json" if args.pytorch_only else "model.safetensors.index.json")
        if index.exists():
            files = set(json.loads(index.read_text())["weight_map"].values())
        else:
            files = {"pytorch_model.bin" if args.pytorch_only else "model.safetensors"}
        assert files and all(not Path(f).is_absolute() and ".." not in Path(f).parts for f in files)
        snapshot_download(args.model_id, revision=args.revision, local_dir=target,
            endpoint=ENDPOINT, token=False, allow_patterns=sorted(files), max_workers=2)
        assert all((target / f).is_file() and (target / f).stat().st_size > 0 for f in files)
        (target / "DOWNLOAD_COMPLETE.json").write_text(json.dumps({"model": args.model_id, "revision": args.revision}))
        print(json.dumps({"download_complete": str(target)}), flush=True)
        break
    except Exception as error:
        print(json.dumps({"attempt": attempt, "error_type": type(error).__name__}), flush=True)
        if attempt == 3:
            raise
        time.sleep(5 * attempt)
