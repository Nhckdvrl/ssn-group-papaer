"""Separate released training-seed variability from item-conditional uncertainty."""
import collections
import hashlib
import json
from pathlib import Path

import numpy as np

from analyze_probe import read

ROOT = Path(__file__).resolve().parents[1]


def main():
    scores = {}
    metadata = {}
    tokenizers = set()
    hashes = set()
    for condition in ["noswitch", "switch", "par"]:
        for seed in [42, 43, 44]:
            path = ROOT / "artifacts" / "p3" / f"macaroni_{condition}_s{seed}_xstory.jsonl"
            scores[(condition, seed)], meta = read(path)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            items = [{k: v for k, v in row.items() if k not in ["scores", "prior_scores"]} for row in rows]
            assert hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == meta["items_sha256"]
            assert all(np.isfinite(s["ll"]) and s["tokens"] > 0 for r in rows for field in ["scores", "prior_scores"] for s in r[field])
            metadata[f"{condition}/s{seed}"] = meta
            hashes.add(meta["items_sha256"])
            tokenizers.add(hashlib.sha256((Path(meta["model"]["path"]) / "tokenizer.json").read_bytes()).hexdigest())
    assert len(hashes) == len(tokenizers) == 1
    keys = sorted(scores[("noswitch", 42)])
    rng = np.random.default_rng(20260930)
    result = {"metadata": metadata, "tokenizer_sha256": next(iter(tokenizers)), "accuracy": {}, "contrasts": {}}
    differences = collections.defaultdict(dict)
    for key in keys:
        ids = sorted(scores[("noswitch", 42)][key])
        values = {}
        for condition in ["noswitch", "switch", "par"]:
            per_seed = []
            for seed in [42, 43, 44]:
                assert sorted(scores[(condition, seed)][key]) == ids
                per_seed.append([scores[(condition, seed)][key][i]["correct"] for i in ids])
            values[condition] = np.array(per_seed)
            result["accuracy"]["/".join(key) + "/" + condition] = {"seed_accuracy_pct": (100 * values[condition].mean(axis=1)).tolist(), "mean_accuracy_pct": float(values[condition].mean() * 100)}
        for condition in ["switch", "par"]:
            delta = values[condition] - values["noswitch"]
            differences[condition][key] = delta
            averaged = delta.mean(axis=0)
            boot = averaged[rng.integers(len(ids), size=(10000, len(ids)))].mean(axis=1) * 100
            result["contrasts"][condition + "/" + "/".join(key)] = {"matched_seed_effect_pp": (delta.mean(axis=1) * 100).tolist(),
                "mean_effect_pp": float(delta.mean() * 100), "item_bootstrap_fixed_seeds_95ci_pp": np.quantile(boot, [.025, .975]).tolist()}
    result["cross_minus_mono"] = {}
    for condition, cells in differences.items():
        for method in sorted({key[0] for key in keys}):
            delta = (cells[(method, "en->zh")] + cells[(method, "zh->en")] - cells[(method, "en->en")] - cells[(method, "zh->zh")]) / 2
            average = delta.mean(axis=0)
            boot = average[rng.integers(len(average), size=(10000, len(average)))].mean(axis=1) * 100
            result["cross_minus_mono"][condition + "/" + method] = {"matched_seed_interaction_pp": (delta.mean(axis=1)*100).tolist(), "mean_interaction_pp": float(delta.mean()*100), "item_bootstrap_fixed_seeds_95ci_pp": np.quantile(boot, [.025, .975]).tolist()}
    result["limits"] = "Three released seeds, not the paper's eight. Seed-label matching does not prove common initialization. Item CIs condition on these seeds; no training-population CI or multiplicity correction. Data content/exposure differ across interventions."
    output = ROOT / "results" / "p3_macaroni_xstory.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(output), "interactions": result["cross_minus_mono"]}, indent=2))


if __name__ == "__main__":
    main()
