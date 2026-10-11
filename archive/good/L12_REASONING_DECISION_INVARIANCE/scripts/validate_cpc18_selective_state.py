#!/usr/bin/env python3
"""Validate E21 state-intervention coverage and summary integrity."""

import hashlib
import json

import pandas as pd

from cpc18_form_evidence_common import ROOT


def main():
    config = json.loads((ROOT / "configs/cpc18_selective_state.json").read_text())
    output = ROOT / config["result_dir"]
    raw_path = output / "raw.jsonl"
    frame = pd.read_json(raw_path, lines=True)
    keys = [
        "problem", "target_form", "target_evidence", "donor_form",
        "donor_evidence", "layer",
    ]
    expected_rows = config["n_selected_base_decisions"] * 4 * 4 * len(config["scan_layers"])
    selected = {row["problem"] for row in config["selected_units"]}
    failures = []
    if len(frame) != expected_rows:
        failures.append("row count mismatch")
    if int(frame.duplicated(keys).sum()):
        failures.append("duplicate intervention cells")
    if set(frame.problem) != selected:
        failures.append("selected problem coverage mismatch")
    if set(frame.layer) != set(config["scan_layers"]):
        failures.append("layer coverage mismatch")
    per_problem = frame.groupby("problem").size()
    if not (per_problem == 4 * 4 * len(config["scan_layers"])).all():
        failures.append("per-problem factorial incomplete")
    summary = json.loads((output / "summary.json").read_text())
    if summary["n_base_decisions"] != config["n_selected_base_decisions"]:
        failures.append("summary base-decision count mismatch")
    if summary["raw_artifact"]["sha256"] != hashlib.sha256(raw_path.read_bytes()).hexdigest():
        failures.append("raw hash mismatch")
    audit = {
        "design": "L12-E21 execution audit",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "rows": int(len(frame)),
        "expected_rows": expected_rows,
        "base_decisions": int(frame.problem.nunique()),
        "duplicate_keys": int(frame.duplicated(keys).sum()),
        "layers": sorted(int(value) for value in frame.layer.unique()),
    }
    (output / "execution_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
