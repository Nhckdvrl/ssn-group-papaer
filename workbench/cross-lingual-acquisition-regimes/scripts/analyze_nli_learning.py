"""Analyze complete preregistered E01 cells, never select surviving seeds."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ("baseline", "monoweb", "onlyparallel")
STEPS = (0, 64, 256, 1024)


def load(path):
    return json.loads(path.read_text())


def bootstrap(values, groups=None):
    rng = np.random.default_rng(20261002)
    draws = []
    for _ in range(100):
        indices = rng.integers(0, len(values), (100, len(values)))
        draws.extend(values[indices].mean(axis=1).tolist())
    result = dict(mean=float(values.mean()), paired_item_bootstrap95=np.quantile(draws, [.025, .975]).tolist())
    if groups is not None:
        unique, indices = np.unique(groups, return_inverse=True)
        sums = np.bincount(indices, weights=values)
        counts = np.bincount(indices)
        draws = []
        rng = np.random.default_rng(20261002)
        for _ in range(100):
            sampled = rng.integers(0, len(unique), (100, len(unique)))
            draws.extend((sums[sampled].sum(1)/counts[sampled].sum(1)).tolist())
        result["POST_HOC_promptID_cluster_bootstrap95"] = np.quantile(draws, [.025, .975]).tolist()
        result["n_promptID_clusters"] = len(unique)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    args = parser.parse_args()
    assert len(set(args.seeds)) == len(args.seeds)
    data = load(ROOT / "artifacts/nli_learning/data.json")
    pair_audit = load(ROOT / "results/nli_xnli_pair_audit.json")
    outcomes, table, cells = {}, [], []
    provenances = {}
    for seed in args.seeds:
        for condition in CONDITIONS:
            folder = ROOT / "artifacts/nli_learning" / f"train_{condition}_seed{seed}"
            done = load(folder / "completion.json")
            provenance = load(folder / "provenance.json")
            assert done["data_hashes"] == data["metadata"]["hashes"]
            assert len(load(folder / "curve.json")) == 4
            provenances[seed, condition] = provenance
            cells.append(dict(seed=seed, condition=condition, completion=done))
            for point in load(folder / "curve.json"):
                assert point["updates"] in STEPS
                for split, metric in point["metrics"].items():
                    labels = np.array([r["label"] for r in data["splits"][split]])
                    path = folder / f"predictions_{split}_{point['updates']}.json"
                    predictions = np.array(load(path))
                    assert len(labels) == len(predictions) == metric["n"]
                    correctness = predictions == labels
                    assert abs(correctness.mean()-metric["accuracy"]) < 1e-10
                    outcomes[seed, condition, point["updates"], split] = correctness
                    table.append(dict(seed=seed, condition=condition, updates=point["updates"],
                                      examples=point["examples"], split=split, **metric,
                                      predictions_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for seed in args.seeds:
        ref = provenances[seed, "baseline"]
        for condition in CONDITIONS:
            other = provenances[seed, condition]
            for key in ("encoded_hashes", "initial_head_sha256", "tokenizer_sha256", "config", "script_sha256", "device"):
                assert ref[key] == other[key], f"Condition mismatch: {key}"
    differences = []
    for a, b in (("monoweb", "baseline"), ("onlyparallel", "monoweb"), ("onlyparallel", "baseline")):
        for step in STEPS:
            for split in ("en_dev", "en_test", "de_test"):
                deltas = np.stack([outcomes[s, a, step, split].astype(float)
                                   - outcomes[s, b, step, split] for s in args.seeds])
                differences.append(dict(contrast=f"{a}-{b}", updates=step, examples=step*32,
                                        split=split, **bootstrap(deltas.mean(axis=0), pair_audit["promptIDs"] if split.endswith("test") else None),
                                        per_adaptation_seed=deltas.mean(axis=1).tolist(),
                                        adaptation_seed_std=float(deltas.mean(axis=1).std(ddof=1)) if len(args.seeds)>1 else None))
    report = dict(seeds=args.seeds, cells=cells, table=table, differences=differences,
                  uncertainty="Paired-item CI conditional on these adaptation seeds; seed SD separately. One pretraining checkpoint per condition, no pretraining replication.",
                  scope="Standard task-learning baseline, no novelty or mechanistic claim.")
    path = ROOT / "results" / ("nli_analysis_seeds_" + "_".join(map(str, args.seeds)) + ".json")
    path.write_text(json.dumps(report, indent=2) + "\n")
    for row in table:
        if row["updates"] == 1024:
            print(row["condition"], row["seed"], row["split"], round(row["accuracy"]*100, 2))
    for d in differences:
        if d["updates"] == 1024 and d["split"] == "de_test":
            print(d["contrast"], d["mean"]*100, np.array(d["paired_item_bootstrap95"])*100)
    print(path)


if __name__ == "__main__":
    main()
