"""Fetch the pinned E12 public assets to node-local storage.

This script does no curation, training, or evaluation. It records the exact
Hugging Face revision and total on-disk bytes so the E12 data audit can begin.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from huggingface_hub import snapshot_download


ASSETS = {
    "llava_arrow": ("dataset", "Ethlake/llava-665k", "235a8adf266bb6dc02a099dc0221d28dec058f54"),
    "llava_json": ("dataset", "liuhaotian/LLaVA-Instruct-150K", "9d451dc7629cfe0469f6ae4432b765cd603d5fcb"),
    "icons_json": ("dataset", "xindiw/LLAVA-ICONS-133K", "c9b3bf7be76871575b739f28bed1cdc872db8e75"),
    "llava_init": ("model", "anonneuripsmail/llava-1.5-7b-init", "5736a39125fce6ca4d4eb20033ca7c46895878ab"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("asset", choices=ASSETS)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    kind, repo, revision = ASSETS[args.asset]
    dest = args.root / args.asset
    dest.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    snapshot_download(
        repo_id=repo,
        repo_type=kind,
        revision=revision,
        local_dir=str(dest),
        max_workers=args.workers,
        allow_patterns=["llava_v1_5_mix665k.json"] if args.asset == "llava_json" else None,
    )
    files = [p for p in dest.rglob("*") if p.is_file() and ".cache/huggingface" not in str(p)]
    manifest = {
        "asset": args.asset,
        "repo": repo,
        "repo_type": kind,
        "revision": revision,
        "path": str(dest),
        "files": len(files),
        "bytes": sum(p.stat().st_size for p in files),
        "wall_seconds": round(time.monotonic() - start, 1),
    }
    out = args.root / f"{args.asset}_download.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
