#!/usr/bin/env python3
"""Retain exact E131 common-suffix step 24576 checkpoint inodes without copying weights."""
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
BASE = Path("/tmp/xiang-moe-20261025")
TARGET_STEP = 24576
PARENT_SHA = "13bb7ec0c8dc899744e7e4e6c7938c80a80c1b8079d1e3c89f764251524dbabf"
FROZEN_SHA = "565b9dacb123aab3e1f296bcc1bad8928fa7811492b80aface1809530a0b6c03"
EXPECTED = {
    "ordered": "79c59a104ac3a900b60b9605bd0f8a7597f430adf2e174b357103aa363dfd6f3",
    "permuted": "2c41393739b63961ed4ca611a87d9243f94a6244285ca2db3e7ee6c8f7e13319",
}
TERMINAL = {"retained", "missed", "invalid_source", "timed_out"}


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, path)


def checkpoint_metadata(path):
    # mmap keeps checkpoint tensor storage backed by the immutable file inode;
    # only Python metadata is read by this watcher.
    state = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
    meta = {
        "schema": state.get("schema"),
        "experiment": state.get("experiment"),
        "step": state.get("step"),
        # E131 child checkpoints may omit branch/phase; immutable pulse-stage
        # metadata and the branch-specific config hash bind the source instead.
        "branch": state.get("branch"),
        "config_hash": state.get("config_hash"),
        "frozen_sample_hash": state.get("frozen_sample_hash"),
        "parent_checkpoint_sha256": state.get("parent", {}).get("checkpoint_sha256"),
    }
    del state
    return meta


def validate(meta, branch):
    return (
        meta["schema"] == "E131-child-v1"
        and meta["experiment"] == "E131"
        and meta["config_hash"] == EXPECTED[branch]
        and meta["frozen_sample_hash"] == FROZEN_SHA
        and meta["parent_checkpoint_sha256"] == PARENT_SHA
        and meta.get("branch") in (None, branch)
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval-seconds", type=float, default=30)
    parser.add_argument("--timeout-hours", type=float, default=8)
    args = parser.parse_args()
    interval = min(max(args.interval_seconds, 1.0), 30.0)
    manifest_path = ROOT / "results/e131/diagnostic_staging.json"
    pid_path = ROOT / "results/e131/diagnostic_watcher.pid"
    if manifest_path.exists():
        raise FileExistsError(f"Refusing to replace existing manifest: {manifest_path}")
    pid_path.write_text(f"{os.getpid()}\n")
    started = time.monotonic()
    state = {
        "schema": "E131 common-suffix diagnostic retention v1",
        "created_utc": now(),
        "target_step": TARGET_STEP,
        "poll_interval_seconds": interval,
        "timeout_hours": args.timeout_hours,
        "parent_checkpoint_sha256": PARENT_SHA,
        "frozen_sample_hash": FROZEN_SHA,
        "branches": {},
    }
    for branch in EXPECTED:
        source = BASE / f"e131_{branch}" / "checkpoint.pt"
        dest = BASE / f"e131_{branch}" / "snapshots" / "diagnostic_step024576.pt"
        pulse = ROOT / f"results/e131/pulse_stage/{branch}/training_summary.json"
        pulse_provenance = ROOT / f"results/e131/pulse_stage/{branch}/provenance.json"
        pulse_meta = json.loads(pulse.read_text())
        provenance_meta = json.loads(pulse_provenance.read_text())
        pulse_branch = pulse_meta.get("branch") or provenance_meta.get("args", {}).get("branch")
        if pulse_meta.get("config_hash") != EXPECTED[branch] or provenance_meta.get("config_hash") != EXPECTED[branch]:
            raise ValueError(f"Immutable pulse-stage config mismatch for {branch}")
        if pulse_branch != branch:
            raise ValueError(f"Immutable pulse-stage branch metadata mismatch for {branch}: {pulse_branch}")
        state["branches"][branch] = {
            "status": "watching",
            "source_checkpoint": str(source),
            "diagnostic_checkpoint": str(dest),
            "pulse_stage_summary": str(pulse),
            "pulse_stage_provenance": str(pulse_provenance),
            "pulse_stage_branch": pulse_branch,
            "expected_config_hash": EXPECTED[branch],
            "step": None,
            "source_inode": None,
            "diagnostic_inode": None,
            "same_inode_hardlink": None,
            "verified_metadata": None,
            "note": None,
        }
    atomic_json(manifest_path, state)

    while True:
        any_watching = False
        for branch, record in state["branches"].items():
            if record["status"] in TERMINAL:
                continue
            any_watching = True
            source = Path(record["source_checkpoint"])
            dest = Path(record["diagnostic_checkpoint"])
            if not source.is_file():
                record["note"] = "source checkpoint not present yet"
                continue
            try:
                before = source.stat()
                meta = checkpoint_metadata(source)
                after = source.stat()
            except Exception as exc:  # metadata may be in the middle of an atomic save
                record["note"] = f"transient checkpoint read error: {type(exc).__name__}: {exc}"
                continue
            record["step"] = meta["step"]
            record["source_inode"] = after.st_ino
            record["source_size_bytes"] = after.st_size
            if not validate(meta, branch):
                record["status"] = "invalid_source"
                record["note"] = "schema/config/parent/frozen metadata did not match registered source"
                record["verified_metadata"] = meta
                continue
            record["verified_metadata"] = meta
            if meta["step"] > TARGET_STEP:
                record["status"] = "missed"
                record["note"] = "published source advanced past exact target step; no adjacent checkpoint will be substituted"
                continue
            if meta["step"] < TARGET_STEP:
                continue

            # Do not link if the source path was atomically replaced between the
            # metadata read and this check. The next poll will inspect the new inode.
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
                record["note"] = "source inode changed during metadata read; retrying"
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                try:
                    os.link(source, dest)
                except FileExistsError:
                    pass
            try:
                linked = dest.stat()
                linked_meta = checkpoint_metadata(dest)
            except Exception as exc:
                record["note"] = f"linked checkpoint metadata read error: {type(exc).__name__}: {exc}"
                continue
            record["diagnostic_inode"] = linked.st_ino
            record["same_inode_hardlink"] = (linked.st_dev, linked.st_ino) == (after.st_dev, after.st_ino)
            record["diagnostic_size_bytes"] = linked.st_size
            record["diagnostic_metadata"] = linked_meta
            if (
                linked_meta.get("step") == TARGET_STEP
                and validate(linked_meta, branch)
                and record["same_inode_hardlink"]
            ):
                record["status"] = "retained"
                record["note"] = "exact step retained by same-filesystem hard link; source inode left untouched"
            else:
                record["status"] = "missed"
                record["note"] = "destination was not the exact target checkpoint hard-linked from source; preserved and marked missed"

        if time.monotonic() - started >= args.timeout_hours * 3600:
            for record in state["branches"].values():
                if record["status"] == "watching":
                    record["status"] = "timed_out"
                    record["note"] = "watcher reached configured timeout before exact target checkpoint was published"
        state["updated_utc"] = now()
        atomic_json(manifest_path, state)
        if all(record["status"] in TERMINAL for record in state["branches"].values()):
            break
        time.sleep(interval)


if __name__ == "__main__":
    main()
