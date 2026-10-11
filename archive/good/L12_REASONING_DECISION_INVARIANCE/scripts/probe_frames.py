#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/pilot_seed29"
RNG = np.random.default_rng(29)


def balanced_accuracy(y, pred):
    return float(np.mean([np.mean(pred[y == label] == label) for label in [0, 1]]))


def nearest_centroid_cv(x, y, groups):
    predictions, labels = [], []
    for heldout in np.unique(groups):
        train, test = groups != heldout, groups == heldout
        center0, center1 = x[train & (y == 0)].mean(0), x[train & (y == 1)].mean(0)
        direction = center1 - center0
        midpoint = (center1 + center0) / 2
        pred = ((x[test] - midpoint) @ direction > 0).astype(int)
        predictions.extend(pred.tolist()); labels.extend(y[test].tolist())
    return balanced_accuracy(np.asarray(labels), np.asarray(predictions))


def main():
    report = {}
    canonical = [RUN / branch / "prompt_activations.npz" for branch in ["base", "instruct_sft", "think_sft"]]
    for path in [path for path in canonical if path.exists()]:
        branch = path.parent.name
        bundle = np.load(path)
        x = bundle["activations"]
        meta = [json.loads(v) for v in bundle["metadata"]]
        y = np.asarray([int(m["frame"] == "loss") for m in meta])
        groups = np.asarray([m["prospect"] for m in meta])
        layer_scores, null95 = [], []
        for layer in range(x.shape[1]):
            layer_x = x[:, layer]
            layer_scores.append(nearest_centroid_cv(layer_x, y, groups))
            shuffled = [nearest_centroid_cv(layer_x, RNG.permutation(y), groups) for _ in range(500)]
            null95.append(float(np.quantile(shuffled, 0.95)))
        report[branch] = {
            "n_conditions": int(len(y)), "n_layers_including_embedding": int(x.shape[1]),
            "leave_one_prospect_out_balanced_accuracy": layer_scores,
            "label_shuffle_95th_percentile": null95,
            "best_layer": int(np.argmax(layer_scores)), "best_score": float(np.max(layer_scores)),
            "final_layer_score": float(layer_scores[-1]),
            "activation_source": str(path),
        }
    (RUN / "frame_probe.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__": main()
