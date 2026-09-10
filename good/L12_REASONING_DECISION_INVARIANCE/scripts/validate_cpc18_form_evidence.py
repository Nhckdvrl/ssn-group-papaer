#!/usr/bin/env python3
"""Validate E20 behavior rows, summaries, prompts, and raw checksums."""

import hashlib
import json

import pandas as pd

from cpc18_form_evidence_common import CONFIG, ROOT


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    result_dir = ROOT / CONFIG["result_dir"]
    problems = {
        row["id"]: row
        for row in (json.loads(line) for line in (ROOT / CONFIG["output"]).open())
    }
    summary = json.loads((result_dir / "behavior_summary.json").read_text())
    expected_per_problem = 2 * 2 * len(CONFIG["orders"]) * CONFIG["samples_per_cell"]
    failures = []
    audit = {
        "design": "L12-E20 execution audit",
        "n_frozen_base_decisions": len(problems),
        "expected_rows_per_base_decision": expected_per_problem,
        "regimes": {},
    }
    keys = ["problem", "evidence_choice", "form", "order", "sample_index"]
    for spec in CONFIG["regimes"]:
        name = spec["name"]
        path = result_dir / "raw" / f"{name}.jsonl"
        frame = pd.read_json(path, lines=True)
        duplicate_count = int(frame.duplicated(keys).sum())
        counts = frame.groupby("problem").size()
        expected_histories = {
            problem: {item["evidence_choice"]: item["history_id"] for item in row["evidence"]}
            for problem, row in problems.items()
        }
        history_mismatches = int(sum(
            row.evidence_history_id != expected_histories[row.problem][row.evidence_choice]
            for row in frame.itertuples()
        ))
        prompt_variants = int(frame.groupby(keys[:-1]).prompt_sha256.nunique().max())
        checks = {
            "rows": int(len(frame)),
            "base_decisions": int(frame.problem.nunique()),
            "duplicate_keys": duplicate_count,
            "history_id_mismatches": history_mismatches,
            "maximum_prompt_hashes_per_condition": prompt_variants,
            "valid_rate": float(frame.valid.mean()),
        }
        if set(frame.problem) != set(problems):
            failures.append(f"{name}: frozen problem coverage mismatch")
        if not (counts == expected_per_problem).all():
            failures.append(f"{name}: per-problem row count mismatch")
        if duplicate_count or history_mismatches or prompt_variants != 1:
            failures.append(f"{name}: key/history/prompt validation failed")
        if len(frame) != summary[name]["n_generations"]:
            failures.append(f"{name}: summary row count mismatch")
        audit["regimes"][name] = checks

    control_summary_path = result_dir / "control_summary.json"
    if control_summary_path.exists():
        control_summary = json.loads(control_summary_path.read_text())
        audit["control"] = {}
        control_keys = [
            "problem", "form", "order", "a_sample_index", "b_sample_index",
            "prompt_evidence", "trajectory_evidence",
        ]
        unit_keys = control_keys[:5]
        expected_cells = {
            (prompt, trajectory)
            for prompt in ("A", "B") for trajectory in ("A", "B")
        }
        for spec in CONFIG["regimes"]:
            name = spec["name"]
            path = result_dir / "raw" / "control" / f"{name}.jsonl"
            frame = pd.read_json(path, lines=True)
            duplicate_count = int(frame.duplicated(control_keys).sum())
            bad_factorials = 0
            for _, group in frame.groupby(unit_keys, dropna=False):
                observed = set(zip(group.prompt_evidence, group.trajectory_evidence))
                if observed != expected_cells or len(group) != 4:
                    bad_factorials += 1
            forms = {}
            for form in ("raw", "summary"):
                subset = frame[frame.form == form]
                expected_units = int(subset.problem.nunique())
                reported = control_summary[name]["forms"][form]["n_base_decisions"]
                forms[form] = {
                    "base_decisions": expected_units,
                    "summary_base_decisions": reported,
                }
                if expected_units != reported:
                    failures.append(f"{name}: {form} control summary count mismatch")
            checks = {
                "rows": int(len(frame)),
                "base_decisions": int(frame.problem.nunique()),
                "duplicate_keys": duplicate_count,
                "incomplete_factorial_units": bad_factorials,
                "forms": forms,
            }
            if duplicate_count or bad_factorials:
                failures.append(f"{name}: duplicate or incomplete control factorial")
            audit["control"][name] = checks

    manifest = json.loads((result_dir / "raw_manifest.json").read_text())
    audit["manifest"] = {}
    for item in manifest["artifacts"]:
        path = ROOT / item["path"]
        with path.open("rb") as handle:
            rows = sum(1 for _ in handle)
        checks = {
            "bytes_match": path.stat().st_size == item["bytes"],
            "rows_match": rows == item["rows"],
            "sha256_match": sha256(path) == item["sha256"],
        }
        if not all(checks.values()):
            failures.append(f"manifest mismatch: {item['path']}")
        audit["manifest"][item["path"]] = checks
    audit["status"] = "PASS" if not failures else "FAIL"
    audit["failures"] = failures
    (result_dir / "execution_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
