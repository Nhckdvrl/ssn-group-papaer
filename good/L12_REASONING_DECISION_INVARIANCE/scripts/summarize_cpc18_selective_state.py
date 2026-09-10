#!/usr/bin/env python3
"""Summarize E21 state-carried form and evidence sensitivity."""

import hashlib
import json

import numpy as np
import pandas as pd

from cpc18_form_evidence_common import ROOT


CONFIG = json.loads((ROOT / "configs/cpc18_selective_state.json").read_text())
OUTPUT = ROOT / CONFIG["result_dir"]


def interval(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, len(values), (CONFIG["bootstrap_samples"], len(values)))].mean(axis=1)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def report(values, seed):
    return {
        "mean": float(values.mean()),
        "base_decision_bootstrap_ci95": interval(values, seed),
        "positive_base_decision_fraction": float((values > 0).mean()),
    }


def compute_unit_metrics(frame):
    cells = frame.pivot(
        index=["problem", "layer", "target_form", "target_evidence"],
        columns=["donor_form", "donor_evidence"],
        values="patched_p_a",
    )
    unit_rows = []
    for (problem, layer), part in cells.groupby(level=["problem", "layer"]):
        evidence_effect = np.mean([
            part[(form, "A")].mean() - part[(form, "B")].mean()
            for form in ("raw", "summary")
        ])
        form_sensitivity = np.mean([
            abs(part[("raw", evidence)].mean() - part[("summary", evidence)].mean())
            for evidence in ("A", "B")
        ])
        unit_rows.append({
            "problem": problem,
            "layer": int(layer),
            "donor_evidence_effect": float(evidence_effect),
            "donor_form_sensitivity": float(form_sensitivity),
            "state_selectivity": float(evidence_effect - form_sensitivity),
        })
    return pd.DataFrame(unit_rows)


def main():
    raw_path = OUTPUT / "raw.jsonl"
    frame = pd.read_json(raw_path, lines=True)
    units = compute_unit_metrics(frame)
    unit_rows = units.to_dict(orient="records")
    profile = []
    for layer in CONFIG["scan_layers"]:
        part = units[units.layer == layer]
        profile.append({
            "layer": layer,
            "n_base_decisions": int(len(part)),
            "donor_evidence_effect": report(part.donor_evidence_effect, CONFIG["seed"] + layer),
            "donor_form_sensitivity": report(part.donor_form_sensitivity, CONFIG["seed"] + 100 + layer),
            "state_selectivity": report(part.state_selectivity, CONFIG["seed"] + 200 + layer),
        })
    with (OUTPUT / "unit_metrics.jsonl").open("w") as handle:
        for row in unit_rows:
            handle.write(json.dumps(row) + "\n")
    summary = {
        "design": CONFIG["design"],
        "n_base_decisions": int(frame.problem.nunique()),
        "layer_profile": profile,
        "primary_final_layer": profile[-1],
        "identification_boundary": (
            "within OLMo Think, last-token residual states from natural stripped "
            "trajectories are substituted without donor text; this identifies state "
            "content mediation, not a unique neuron or training-step effect"
        ),
        "raw_artifact": {
            "path": str(raw_path.relative_to(ROOT)),
            "bytes": raw_path.stat().st_size,
            "rows": int(len(frame)),
            "sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
            "git_policy": "ignored regenerable intervention output",
        },
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
