#!/usr/bin/env python3
"""Validate CPC18 raw execution against the frozen nested design and manifest."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail_if(condition, message, failures):
    if condition:
        failures.append(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    config = json.loads(config_path.read_text())
    result_dir = ROOT / config["result_dir"]
    problems = [json.loads(line) for line in (ROOT / config["output"]).open()]
    problem_ids = {row["id"] for row in problems}
    failures = []
    audit = {
        "config": str(config_path.relative_to(ROOT)),
        "result_dir": str(result_dir.relative_to(ROOT)),
        "n_frozen_base_decisions": len(problem_ids),
        "behavior": {},
        "control": {},
        "manifest": {},
    }

    behavior_key = ["problem", "presentation", "history_id", "order", "sample_index"]
    expected_per_problem = (
        (1 + config["histories_per_problem"])
        * len(config["orders"])
        * config["samples_per_cell"]
    )
    behavior_summary = json.loads((result_dir / "behavior_summary.json").read_text())
    control_summary = json.loads((result_dir / "control_summary.json").read_text())

    for regime in config["regimes"]:
        name = regime["name"]
        path = result_dir / "raw" / f"{name}.jsonl"
        frame = pd.read_json(path, lines=True, dtype={"history_id": "string"})
        counts = frame.groupby("problem", dropna=False).size()
        duplicate_count = int(frame.duplicated(behavior_key).sum())
        unexpected = sorted(set(frame.problem) - problem_ids)
        missing = sorted(problem_ids - set(frame.problem))
        fail_if(duplicate_count != 0, f"{name}: duplicate behavior keys", failures)
        fail_if(bool(unexpected), f"{name}: unexpected problems {unexpected}", failures)
        fail_if(bool(missing), f"{name}: missing problems {missing}", failures)
        fail_if(
            not (counts == expected_per_problem).all(),
            f"{name}: behavior count is not {expected_per_problem} for every problem",
            failures,
        )
        fail_if(
            len(frame) != behavior_summary[name]["n_generations"],
            f"{name}: behavior summary row count mismatch",
            failures,
        )
        audit["behavior"][name] = {
            "rows": int(len(frame)),
            "base_decisions": int(frame.problem.nunique()),
            "expected_rows_per_base_decision": expected_per_problem,
            "duplicate_keys": duplicate_count,
            "valid_rate": float(frame.valid.mean()),
        }

        control_path = result_dir / "raw" / "control" / f"{name}.jsonl"
        control = pd.read_json(control_path, lines=True, dtype={"history_id": "string"})
        trace_key = ["problem", "history_id", "order", "sample_index"]
        cell_key = trace_key + ["prompt_presentation", "trajectory_presentation"]
        duplicate_cells = int(control.duplicated(cell_key).sum())
        cells_per_trace = control.groupby(trace_key, dropna=False).size()
        trace_units = int(len(cells_per_trace))
        control_problems = int(control.problem.nunique())
        fail_if(duplicate_cells != 0, f"{name}: duplicate control cells", failures)
        fail_if(
            not (cells_per_trace == 4).all(),
            f"{name}: incomplete prompt-by-trajectory factorial",
            failures,
        )
        fail_if(
            trace_units != control_summary[name]["n_trace_units"],
            f"{name}: control trace-unit count mismatch",
            failures,
        )
        fail_if(
            control_problems != control_summary[name]["n_base_decisions"],
            f"{name}: control base-decision count mismatch",
            failures,
        )
        audit["control"][name] = {
            "rows": int(len(control)),
            "trace_units": trace_units,
            "base_decisions": control_problems,
            "cells_per_trace": sorted(set(int(value) for value in cells_per_trace)),
            "duplicate_cells": duplicate_cells,
        }

    manifest = json.loads((result_dir / "raw_manifest.json").read_text())
    for item in manifest["artifacts"]:
        path = ROOT / item["path"]
        with path.open("rb") as handle:
            rows = sum(1 for _ in handle)
        checks = {
            "bytes_match": path.stat().st_size == item["bytes"],
            "rows_match": rows == item["rows"],
            "sha256_match": sha256(path) == item["sha256"],
        }
        fail_if(not all(checks.values()), f"manifest mismatch: {item['path']}", failures)
        audit["manifest"][item["path"]] = checks

    audit["status"] = "PASS" if not failures else "FAIL"
    audit["failures"] = failures
    output = Path(args.output) if args.output else result_dir / "execution_audit.json"
    if not output.is_absolute():
        output = ROOT / output
    output.write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
