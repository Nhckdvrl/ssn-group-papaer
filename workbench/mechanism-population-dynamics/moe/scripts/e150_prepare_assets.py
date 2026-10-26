"""Fetch pinned public mature EMO artifacts; never imports or executes model code."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
from huggingface_hub import snapshot_download

WB = Path(__file__).resolve().parents[1]
RESULT = WB / "results/e150"
CACHE = Path.home() / "mechpop_cache/hf_emo_mature"
PINS = WB / "results/mature_assets_2026-10-27/emo_repo_pins.json"
ENDPOINTS = ("StdMoE_1b14b_1T", "StdMoE_1b14b_1T_EmoAnnealed")


def sha(path):
    with Path(path).open("rb") as stream: return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".partial")
    temporary.write_text(json.dumps(value, indent=2)+"\n"); temporary.replace(path)


def main(mode):
    if not (WB / "experiments/E150-native-mature-routing-protocol-cross.md").exists():
        raise ValueError("Preregistered E150 card required")
    pins = json.loads(PINS.read_text())
    result = {"experiment": "E150", "status": "partial", "asset_fetch_source_sha256": sha(__file__),
              "public_metadata_sha256": sha(PINS), "cache": str(CACHE), "models": {}}
    for name in ENDPOINTS:
        pin = pins[name]
        small = [f["rfilename"] for f in pin["files"] if f["rfilename"].endswith((".json", ".py", ".txt", ".model", ".jinja"))]
        weights = [f["rfilename"] for f in pin["files"] if f["rfilename"].endswith(".safetensors")]
        requested = small if mode == "metadata" else small+weights
        print(json.dumps({"event": "E150_asset_fetch", "model": name, "revision": pin["sha"], "mode": mode}), flush=True)
        directory = Path(snapshot_download(pin["id"], revision=pin["sha"], allow_patterns=requested,
                                           cache_dir=str(CACHE), max_workers=2, token=False))
        files = {}
        for remote in pin["files"]:
            filename = remote["rfilename"]
            if filename not in requested: continue
            path = directory / filename
            actual = sha(path)
            expected = remote.get("lfs", {}).get("sha256")
            if path.stat().st_size != remote["size"] or (expected and actual != expected):
                raise ValueError(f"Size/LFS SHA mismatch: {name}/{filename}")
            if not expected:
                data = path.read_bytes()
                blob = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
                if blob != remote["blobId"]: raise ValueError(f"Git blob mismatch: {name}/{filename}")
            files[filename] = {"path": str(path), "size_bytes": path.stat().st_size, "sha256": actual,
                               "public_lfs_sha256": expected, "public_blob_id": remote["blobId"]}
            print(json.dumps({"event": "E150_asset_verified", "model": name, "file": filename,
                              "size_bytes": path.stat().st_size}), flush=True)
        result["models"][name] = {"repo_id": pin["id"], "revision": pin["sha"], "path": str(directory), "files": files}
        write(RESULT / ("metadata.json" if mode == "metadata" else "asset_manifest.json"), result)
    result.update(status="metadata_complete" if mode == "metadata" else "complete",
                  verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  model_code_executed=False, training_or_inference_performed=False)
    write(RESULT / ("metadata.json" if mode == "metadata" else "asset_manifest.json"), result)
    print(json.dumps({"status": result["status"], "models": len(result["models"])}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("metadata", "weights")); args = parser.parse_args()
    try: main(args.mode)
    except Exception as error:
        message = re.sub(r"https?://\S+", "<URL omitted>", str(error))[:400]
        write(RESULT / f"{args.mode}_failure.json", {"status": "failed", "type": type(error).__name__, "message": message})
        raise SystemExit(f"E150 asset retrieval failed ({type(error).__name__}); see recorded failure.")
