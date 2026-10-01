"""Correct-context dependence, conditional on released seeds and one donor assignment."""
import hashlib
import json
from pathlib import Path

import numpy as np

from analyze_probe import read

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = {}
    metadata = {}
    for condition in ["noswitch", "switch"]:
        for seed in [42, 43, 44]:
            for context in ["original", "shuffled"]:
                suffix = "_shuffled" if context == "shuffled" else ""
                path = ROOT / "artifacts/p3" / f"macaroni_{condition}_s{seed}_xstory{suffix}.jsonl"
                data[(condition, seed, context)], meta = read(path)
                rows = [json.loads(line) for line in path.read_text().splitlines()]
                items = [{k: v for k, v in row.items() if k not in ["scores", "prior_scores"]} for row in rows]
                assert hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == meta["items_sha256"]
                assert all(np.isfinite(s["ll"]) and s["tokens"] > 0 for r in rows for field in ["scores", "prior_scores"] for s in r[field])
                metadata[f"{condition}/s{seed}/{context}"] = meta
    assert len({m["semantic_items_sha256"] for m in metadata.values()}) == 1
    for context in ["original", "shuffled"]:
        assert len({m["items_sha256"] for k, m in metadata.items() if k.endswith(context)}) == 1
    for condition in ["noswitch", "switch"]:
        for seed in [42, 43, 44]:
            assert metadata[f"{condition}/s{seed}/original"]["model"] == metadata[f"{condition}/s{seed}/shuffled"]["model"]
    rng = np.random.default_rng(20260930)
    result = {"metadata": metadata, "cells": {}}
    for key in sorted(data[("noswitch", 42, "original")]):
        ids = sorted(data[("noswitch", 42, "original")][key])
        assert all(sorted(d[key]) == ids for d in data.values())
        cell = {}
        for metric in ["correct", "margin"]:
            values = {(condition, context): np.array([[data[(condition, seed, context)][key][i][metric] for i in ids] for seed in [42, 43, 44]])
                      for condition in ["noswitch", "switch"] for context in ["original", "shuffled"]}
            original = values[("switch", "original")] - values[("noswitch", "original")]
            shuffled = values[("switch", "shuffled")] - values[("noswitch", "shuffled")]
            interaction = original - shuffled
            average = interaction.mean(axis=0)
            scale = 100 if metric == "correct" else 1
            boot = average[rng.integers(len(ids), size=(10000, len(ids)))].mean(axis=1) * scale
            cell[metric] = {"means": {"/".join(k): float(v.mean()*scale) for k, v in values.items()},
                            "original_treatment_effect": float(original.mean()*scale), "shuffled_treatment_effect": float(shuffled.mean()*scale),
                            "context_dependence": float(interaction.mean()*scale), "per_seed_context_dependence": (interaction.mean(axis=1)*scale).tolist(),
                            "item_bootstrap_fixed_seeds_95ci": np.quantile(boot, [.025, .975]).tolist()}
        result["cells"]["/".join(key)] = cell
    result["limits"] = "Exploratory uncorrected intervals conditional on three released seeds and one deterministic donor assignment. Unrelated contexts change lexical/topic compatibility too; not a pure intervention on reasoning. Positive DiD must be accompanied by improved useful original-context performance."
    output = ROOT / "results/p3_macaroni_context.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(output), "zh_to_en": {k: v for k, v in result["cells"].items() if k.endswith("zh->en")}}, indent=2))


if __name__ == "__main__":
    main()
