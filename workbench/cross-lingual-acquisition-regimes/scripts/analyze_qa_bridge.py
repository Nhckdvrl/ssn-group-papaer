"""Audit E04's complete factorial, including source learning and recovery controls."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import qa_learning as qa
from analyze_nli_learning import bootstrap, load

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ("new_paired", "new_split", "reused_paired", "reused_split")
STEPS = (0, 128, 512, 1024)
CONTRASTS = {
    "new_paired-new_split": {"new_paired": 1, "new_split": -1},
    "reused_paired-reused_split": {"reused_paired": 1, "reused_split": -1},
    "new_paired-reused_paired": {"new_paired": 1, "reused_paired": -1},
    "new_split-reused_split": {"new_split": 1, "reused_split": -1},
    "coverage_x_conditioning": {"new_paired": 1, "new_split": -1,
                                "reused_paired": -1, "reused_split": 1},
}


def intervals(values, clusters):
    stats = bootstrap(values, clusters)
    stats["context_cluster_bootstrap95"] = stats.pop("POST_HOC_promptID_cluster_bootstrap95")
    stats["n_context_clusters"] = stats.pop("n_promptID_clusters")
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, choices=(17, 29, 43), default=17)
    args = parser.parse_args()
    data = load(qa.DATA)
    scorer = qa.scorer()
    assert hashlib.sha256((ROOT / "artifacts/qa_learning/evaluate_squad.py").read_bytes()).hexdigest() == data["metadata"]["scorer"]["sha256"]
    clusters = {split: np.array([hashlib.sha256(r["context"].encode()).hexdigest()
                                for r in source])
                for split, source in data["splits"].items() if split != "train"}
    values, rows, controls, cells, provenance = {}, [], [], [], {}

    def scores(path, split, metric, function, expected):
        predictions = load(path)
        source = data["splits"][split]
        assert [r["id"] for r in predictions] == [r["id"] for r in source]
        result = np.array([0. if p["overflow"] else scorer.metric_max_over_ground_truths(
            function, p["prediction"], r["answers"]["text"])
                           for p, r in zip(predictions, source)], dtype=float)
        assert np.allclose(result, [r[metric] for r in predictions])
        assert abs(result.mean() - expected[metric]) < 1e-10
        audit = dict(predictions_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     overflow=sum(r["overflow"] for r in predictions),
                     cap=sum(r["cap"] for r in predictions),
                     empty=sum(not r["prediction"] for r in predictions))
        for key in ("overflow", "cap", "empty"):
            assert audit[key] == expected[key], key
        return result, audit

    for condition in CONDITIONS:
        pipeline = ROOT / "artifacts/qa_bridge" / f"{condition}_seed{args.seed}"
        completed = load(pipeline / "completion.json")
        cpt = load(ROOT / "results" / f"e04_cpt_{condition}_seed{args.seed}.json")
        assert completed["cpt"] == cpt
        assert cpt["finite"] and len(cpt["losses"]) == cpt["provenance"]["config"]["updates"]
        folder = ROOT / completed["task_folder"]
        assert folder == ROOT / "artifacts/qa_learning" / f"train_e04_{condition}_seed{args.seed}"
        done = load(folder / "completion.json")
        assert done["data_hashes"] == data["metadata"]["hashes"]
        p = load(folder / "provenance.json")
        provenance[condition] = p
        assert p["model"]["local_intervention"]["condition"] == condition
        assert p["model"]["local_intervention"]["seed"] == args.seed
        curve = load(folder / "curve.json")
        assert tuple(r["updates"] for r in curve) == STEPS
        cells.append(dict(condition=condition, cpt=cpt, task_completion=done))
        for point in curve:
            assert set(point["metrics"]) == {"en_dev", "en_test", "de_test"}
            for split, expected in point["metrics"].items():
                for metric, function in (("f1", scorer.f1_score), ("exact_match", scorer.exact_match_score)):
                    path = folder / f"predictions_{split}_{point['updates']}.json"
                    result, audit = scores(path, split, metric, function, expected)
                    values[condition, point["updates"], split, metric] = result
                    rows.append(dict(condition=condition, updates=point["updates"], split=split,
                                     metric=metric, **intervals(result, clusters[split]), **audit))
        for split in ("en_test", "de_test"):
            for metric, function in (("f1", scorer.f1_score), ("exact_match", scorer.exact_match_score)):
                result, audit = scores(folder / f"predictions_{split}_instruction.json", split,
                                       metric, function, done["instruction_control"][split])
                controls.append(dict(condition=condition, split=split, metric=metric,
                                     instruction_score=float(result.mean()),
                                     delta_instruction_minus_primary=intervals(
                                         result-values[condition, 1024, split, metric], clusters[split]), **audit))
    ref = provenance[CONDITIONS[0]]
    cpt_ref = cells[0]["cpt"]["provenance"]
    for condition, p in provenance.items():
        for key in ("config", "metadata", "script_sha256", "train_encoded_sha256", "device", "seed"):
            assert p[key] == ref[key], key
    for cell in cells:
        p = cell["cpt"]["provenance"]
        for key in ("seed", "config", "metadata", "mask_check", "script_sha256", "mask_script_sha256",
                    "qa_script_sha256", "device", "numpy", "torch"):
            assert p[key] == cpt_ref[key], key
        assert p["metadata"]["task_hashes"] == data["metadata"]["hashes"]
        coverage = cell["condition"].split("_")[0]
        assert cell["cpt"]["loss_tokens"] == sum(p["metadata"]["token_totals"][coverage].values())
    differences = []
    for name, weights in CONTRASTS.items():
        for step in STEPS:
            for split in ("en_dev", "en_test", "de_test"):
                for metric in ("f1", "exact_match"):
                    delta = sum(w*values[c, step, split, metric] for c, w in weights.items())
                    differences.append(dict(contrast=name, updates=step, split=split, metric=metric,
                                            **intervals(delta, clusters[split])))
    report = dict(seed=args.seed, cells=cells, table=rows, differences=differences,
                  instruction_control=controls,
                  zero_cpt_anchor=load(ROOT / "artifacts/qa_learning/train_monoweb_seed17/curve.json"),
                  uncertainty="One joint CPT/adaptation seed. Item/context intervals are not training-seed intervals.",
                  scope="Content coverage and conditioning. Zero-CPT anchor is not budget-matched; no novelty claim.")
    path = ROOT / "results" / f"e04_learning_analysis_seed{args.seed}.json"
    path.write_text(json.dumps(report, indent=2)+"\n")
    for row in rows:
        if row["updates"] == 1024 and row["metric"] == "f1":
            print(row["condition"], row["split"], round(100*row["mean"], 2))
    print(path)


if __name__ == "__main__":
    main()
