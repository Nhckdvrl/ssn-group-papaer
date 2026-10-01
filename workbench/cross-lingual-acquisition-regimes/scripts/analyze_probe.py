"""Summarize complete probes and paired treatment effects over semantic item IDs."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

import numpy as np


def read(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines()]
    meta = json.loads(Path(path).with_suffix(".meta.json").read_text())
    expected = meta.get("expected_items", 4 * min(meta["args"]["limit"], 500 if meta["args"]["task"] == "xcopa" else 2490))
    if len(rows) != expected:
        raise ValueError(f"Incomplete probe {path}: {len(rows)} vs {expected}")
    scores = collections.defaultdict(dict)
    for row in rows:
        key = f"{row['premise_lang']}->{row['choice_lang']}"
        raw = [s["ll"] for s in row["scores"]]
        normalized = [s["ll"] / s["tokens"] for s in row["scores"]]
        methods = {"raw": raw, "token_norm": normalized, "char_norm": [s["ll"] / len(option.lstrip()) for s, option in zip(row["scores"], row["options"])]}
        if row["prior_scores"][0] is not None:
            methods["prior_adjusted"] = [a - b["ll"] for a, b in zip(raw, row["prior_scores"])]
        for method, values in methods.items():
            pred = int(np.argmax(values))
            scores[(method, key)][row["id"]] = {"correct": int(pred == row["gold"]), "prediction": pred,
                                                "gold": row["gold"], "slice": row["slice"],
                                                "margin": values[row["gold"]] - max(v for i, v in enumerate(values) if i != row["gold"])}
    return scores, meta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("control")
    parser.add_argument("--treated")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    control, cm = read(args.control)
    result = {"control": cm, "cells": {}}
    treated, tm = read(args.treated) if args.treated else ({}, {})
    if treated:
        assert cm["items_sha256"] == tm["items_sha256"], "Items/prompts differ across interventions"
        result["treated"] = tm
    rng = np.random.default_rng(20260930)
    for key, examples in control.items():
        ids = sorted(examples)
        baseline = np.array([examples[i]["correct"] for i in ids])
        cell = {"n": len(ids), "control_accuracy": 100 * baseline.mean(),
                "control_prediction_counts": dict(collections.Counter(examples[i]["prediction"] for i in ids))}
        if treated:
            assert ids == sorted(treated[key])
            treatment = np.array([treated[key][i]["correct"] for i in ids])
            delta = treatment - baseline
            samples = delta[rng.integers(len(ids), size=(10000, len(ids)))].mean(axis=1) * 100
            cell.update({"treated_accuracy": 100 * treatment.mean(), "delta_pp": 100 * delta.mean(),
                         "paired_bootstrap_95ci_pp": np.quantile(samples, [.025, .975]).tolist(),
                         "improved_items": int((delta == 1).sum()), "harmed_items": int((delta == -1).sum()),
                         "treated_prediction_counts": dict(collections.Counter(treated[key][i]["prediction"] for i in ids))})
        result["cells"]["/".join(key)] = cell
    # Difference-in-differences uses the same semantic item as the resampling unit.
    if treated:
        langs = sorted({cell.split("->")[0] for _, cell in control})
        for method in sorted({method for method, _ in control}):
            ids = sorted(control[(method, f"{langs[0]}->{langs[0]}")])
            effect = {}
            for cell in [f"{a}->{b}" for a in langs for b in langs]:
                effect[cell] = np.array([treated[(method, cell)][i]["correct"] - control[(method, cell)][i]["correct"] for i in ids])
            interaction = (effect[f"{langs[0]}->{langs[1]}"] + effect[f"{langs[1]}->{langs[0]}"] - effect[f"{langs[0]}->{langs[0]}"] - effect[f"{langs[1]}->{langs[1]}"]) / 2
            boot = interaction[rng.integers(len(ids), size=(10000, len(ids)))].mean(axis=1) * 100
            result.setdefault("cross_minus_mono_treatment_effect", {})[method] = {"delta_pp": interaction.mean() * 100, "paired_bootstrap_95ci_pp": np.quantile(boot, [.025, .975]).tolist()}
    result["interpretation_limits"] = "Exploratory CIs, no familywise correction; model seeds not replicated. Cross-language cells retain continuation/connector confounds."
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"cells": result["cells"], "interaction": result.get("cross_minus_mono_treatment_effect")}, indent=2))


if __name__ == "__main__":
    main()
