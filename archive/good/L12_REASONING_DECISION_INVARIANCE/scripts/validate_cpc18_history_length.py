#!/usr/bin/env python3
"""Validate paired 20/100 diagnostic behavior and raw provenance."""

import hashlib
import json

import pandas as pd

from cpc18_history_length_common import CONFIG, ROOT, load_problems


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    output = ROOT / CONFIG["result_dir"]
    problems = {row["id"]: row for row in load_problems()}
    summary = json.loads((output / "behavior_summary.json").read_text())
    expected = (
        1 + CONFIG["histories_per_problem"] * len(CONFIG["history_lengths"])
    ) * len(CONFIG["orders"]) * CONFIG["samples_per_cell"]
    failures = []
    audit = {
        "design": "L12 paired 20/100 execution audit",
        "n_base_decisions": len(problems),
        "expected_rows_per_base_decision": expected,
        "regimes": {},
    }
    keys = ["problem", "presentation", "history_id", "order", "sample_index"]
    for spec in CONFIG["regimes"]:
        name = spec["name"]
        frame = pd.read_json(output / "raw" / f"{name}.jsonl", lines=True)
        counts = frame.groupby("problem").size()
        duplicate = int(frame.duplicated(keys).sum())
        max_prompt_variants = int(frame.groupby(keys[:-1]).prompt_sha256.nunique().max())
        length_counts = {
            str(int(length)): int(len(frame[frame.history_length == length]))
            for length in CONFIG["history_lengths"]
        }
        if set(frame.problem) != set(problems) or not (counts == expected).all():
            failures.append(f"{name}: problem or row coverage mismatch")
        if duplicate or max_prompt_variants != 1:
            failures.append(f"{name}: duplicate key or prompt mismatch")
        if len(frame) != summary[name]["n_generations"]:
            failures.append(f"{name}: summary count mismatch")
        audit["regimes"][name] = {
            "rows": int(len(frame)), "base_decisions": int(frame.problem.nunique()),
            "duplicate_keys": duplicate, "maximum_prompt_hashes_per_condition": max_prompt_variants,
            "history_length_rows": length_counts, "valid_rate": float(frame.valid.mean()),
        }
    manifest = json.loads((output / "raw_manifest.json").read_text())
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
    (output / "execution_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
