"""Test whether a pairing gain is specifically dependent on the correct evidence."""
import argparse
import json
from pathlib import Path

import numpy as np

from analyze_probe import read


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("control_original")
    parser.add_argument("control_shuffled")
    parser.add_argument("treated_original")
    parser.add_argument("treated_shuffled")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    paths = [args.control_original, args.control_shuffled, args.treated_original, args.treated_shuffled]
    loaded = [read(path) for path in paths]
    scores = [pair[0] for pair in loaded]
    metadata = [pair[1] for pair in loaded]
    semantic_hashes = [m.get("semantic_items_sha256", m["items_sha256"]) for m in metadata]
    assert len(set(semantic_hashes)) == 1, "Semantic items differ"
    assert metadata[0]["items_sha256"] == metadata[2]["items_sha256"]
    assert metadata[1]["items_sha256"] == metadata[3]["items_sha256"]
    for i, j in [(0, 1), (2, 3)]:
        assert metadata[i]["model"] == metadata[j]["model"], "Evidence control changes model"
    result = {"inputs": paths, "metadata": metadata, "cells": {}}
    rng = np.random.default_rng(20260930)
    for key in scores[0]:
        ids = sorted(scores[0][key])
        assert all(ids == sorted(s[key]) for s in scores)
        values = [np.array([s[key][i]["correct"] for i in ids]) for s in scores]
        sensitivity = [values[0] - values[1], values[2] - values[3]]
        interaction = sensitivity[1] - sensitivity[0]
        boot = interaction[rng.integers(len(ids), size=(10000, len(ids)))].mean(axis=1) * 100
        margins = [np.array([s[key][i]["margin"] for i in ids]) for s in scores]
        margin_interaction = (margins[2] - margins[3]) - (margins[0] - margins[1])
        margin_boot = margin_interaction[rng.integers(len(ids), size=(10000, len(ids)))].mean(axis=1)
        result["cells"]["/".join(key)] = {"n": len(ids), "accuracy_control_original_shuffled_treated_original_shuffled": [100 * v.mean() for v in values],
            "control_evidence_sensitivity_pp": 100 * sensitivity[0].mean(), "treated_evidence_sensitivity_pp": 100 * sensitivity[1].mean(),
            "pairing_by_evidence_interaction_pp": 100 * interaction.mean(), "paired_bootstrap_95ci_pp": np.quantile(boot, [.025, .975]).tolist(),
            "gold_margin_interaction": margin_interaction.mean(), "margin_95ci": np.quantile(margin_boot, [.025, .975]).tolist()}
    result["limits"] = "Unrelated context retains cause/effect but changes topic and lexical co-occurrence; not a clean intervention on causal reasoning computation. Exploratory CIs, one training seed."
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["cells"], indent=2))


if __name__ == "__main__":
    main()
