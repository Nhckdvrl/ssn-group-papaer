"""One-shot durable copy of already sealed E148 files; never launches GPU work."""
from __future__ import annotations
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path

WB = Path(__file__).resolve().parents[1]
RESULT = WB / "results/e148"
LOCAL = Path("/tmp/xiang-moe-20261026/e148")
DEST = Path.home() / "mechpop_cache/e148_native_order_forks"


def sha(path):
    with Path(path).open("rb") as f: return hashlib.file_digest(f, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    temp = path.with_suffix(".partial")
    temp.write_text(json.dumps(value, indent=2)+"\n"); temp.replace(path)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    with (RESULT / "archive.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = RESULT / "archive.json"
        state = read(path) if path.exists() else {"experiment": "E148", "destination": str(DEST), "files": {}}
        requested = {}
        plan = read(RESULT / "plan.json")
        requested[plan["plan_path"]] = plan["plan_sha256"]
        assets = LOCAL / "model_assets.json"
        requested[str(assets)] = sha(assets)
        for branch in ("parent", "A", "B", "A-repeat"):
            source = RESULT / f"{branch}.json"
            if not source.exists(): continue
            record = read(source)
            for proof in record["snapshots"]:
                requested[proof["path"]] = proof["sha256"]
                sidecar = LOCAL / branch / f"snapshot_{proof['step']:06d}.json"
                requested[str(sidecar)] = sha(sidecar)
            for evaluation in record["evaluations"]:
                for key in ("logits", "routing"):
                    info = evaluation[key]
                    if info is not None: requested[info["path"]] = info["sha256"]
                sidecar = LOCAL / branch / f"evaluation_{evaluation['step']:06d}.json"
                requested[str(sidecar)] = sha(sidecar)
            if record["status"] == "complete":
                if "update_log" in record:
                    p = record["update_log"]; requested[p["path"]] = p["sha256"]
        graft_file = RESULT / "grafts.json"
        if graft_file.exists():
            for receiver in read(graft_file)["receivers"].values():
                p = receiver["raw"]; requested[p["path"]] = p["sha256"]
        for source, expected in requested.items():
            source = Path(source)
            relative = source.relative_to(LOCAL)
            target = DEST / relative
            previous = state["files"].get(str(relative))
            if previous and target.exists() and target.stat().st_size == previous["size_bytes"] and target.stat().st_mtime_ns == previous["destination_mtime_ns"] and previous["sha256"] == expected:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if sha(target) != expected: raise ValueError(f"Refusing to replace a different durable file: {target}")
            else:
                temporary = target.with_suffix(target.suffix+".partial")
                digest = hashlib.sha256()
                with source.open("rb") as src, temporary.open("wb") as dst:
                    while block := src.read(16 << 20):
                        digest.update(block); dst.write(block)
                    dst.flush(); os.fsync(dst.fileno())
                if digest.hexdigest() != expected: raise ValueError(f"Source changed while archiving: {source}")
                temporary.replace(target)
                if sha(target) != expected: raise ValueError(f"Durable bytes differ: {target}")
            state["files"][str(relative)] = {"source": str(source), "path": str(target), "sha256": expected,
                "size_bytes": target.stat().st_size, "destination_mtime_ns": target.stat().st_mtime_ns,
                "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            state["verified_files"] = len(state["files"])
            state["verified_bytes"] = sum(v["size_bytes"] for v in state["files"].values())
            write(path, state)
            print(json.dumps({"event": "E148_durable_verified", "file": str(relative), "size_bytes": target.stat().st_size}), flush=True)
        state["verified_files"] = len(state["files"])
        state["verified_bytes"] = sum(v["size_bytes"] for v in state["files"].values())
        write(path, state)
        # A manifest is small and replaced atomically; mutable training ledgers
        # are not mistaken for immutable model or prediction snapshots.
        write(DEST / "archive_manifest.json", state)
        print(json.dumps({"verified_files": state["verified_files"], "verified_bytes": state["verified_bytes"]}), flush=True)


if __name__ == "__main__":
    main()
