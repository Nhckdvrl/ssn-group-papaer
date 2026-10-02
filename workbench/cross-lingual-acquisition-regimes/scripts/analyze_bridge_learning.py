"""Audit all four E02 cells and report the preregistered learning contrasts."""
import hashlib
import json
from pathlib import Path

import numpy as np

from analyze_nli_learning import bootstrap, load

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ("new_paired", "new_split", "reused_paired", "reused_split")
STEPS = (0, 64, 256, 1024)


def main():
    data = load(ROOT / "artifacts/nli_learning/data.json")
    groups = load(ROOT / "results/nli_xnli_pair_audit.json")["promptIDs"]
    outcomes, rows, cells, provenances = {}, [], [], {}
    for condition in CONDITIONS:
        pipeline = ROOT / "artifacts/bridge_learning" / f"{condition}_seed17"
        # The pipeline marker is written only after the task checkpoint is saved.
        completion = load(pipeline / "completion.json")
        folder = ROOT / "artifacts/nli_learning" / f"train_e02_{condition}_seed17"
        done = load(folder / "completion.json")
        provenance = load(folder / "provenance.json")
        assert done["data_hashes"] == data["metadata"]["hashes"]
        curve = load(folder / "curve.json")
        assert [p["updates"] for p in curve] == list(STEPS)
        provenances[condition] = provenance
        cells.append(dict(condition=condition, pipeline_completion=completion,
                          cpt=load(ROOT / "results" / f"e02_cpt_{condition}_seed17.json")))
        for point in curve:
            for split, metric in point["metrics"].items():
                labels = np.array([r["label"] for r in data["splits"][split]])
                path = folder / f"predictions_{split}_{point['updates']}.json"
                pred = np.array(load(path))
                correct = pred == labels
                assert len(pred) == len(labels) == metric["n"]
                assert abs(correct.mean()-metric["accuracy"]) < 1e-10
                outcomes[condition, point["updates"], split] = correct.astype(float)
                rows.append(dict(condition=condition, updates=point["updates"],
                                 examples=point["examples"], split=split, **metric,
                                 predictions_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for condition in CONDITIONS:
        for key in ("encoded_hashes", "initial_head_sha256", "tokenizer_sha256", "config", "script_sha256", "device"):
            assert provenances[condition][key] == provenances[CONDITIONS[0]][key], key
    cpt_ref = cells[0]["cpt"]["provenance"]
    for cell in cells:
        p = cell["cpt"]["provenance"]
        for key in ("seed", "config", "metadata", "mask_check", "script_sha256", "device", "numpy", "torch"):
            assert p[key] == cpt_ref[key], key
        assert p["metadata"]["source_data_hashes"] == data["metadata"]["hashes"]
        assert len(cell["cpt"]["losses"]) == p["config"]["updates"]
        assert cell["pipeline_completion"]["cpt"] == cell["cpt"]
    contrasts = {
        "new_paired-new_split": {"new_paired": 1, "new_split": -1},
        "reused_paired-reused_split": {"reused_paired": 1, "reused_split": -1},
        "new_paired-reused_paired": {"new_paired": 1, "reused_paired": -1},
        "new_split-reused_split": {"new_split": 1, "reused_split": -1},
        "coverage_x_conditioning": {"new_paired": 1, "new_split": -1,
                                    "reused_paired": -1, "reused_split": 1},
    }
    differences = []
    for name, weights in contrasts.items():
        for step in STEPS:
            for split in ("en_dev", "en_test", "de_test"):
                delta = sum(weight*outcomes[c, step, split] for c, weight in weights.items())
                stats = bootstrap(delta, groups if split.endswith("test") else None)
                # E02 registered the cluster sensitivity before any training.
                if "POST_HOC_promptID_cluster_bootstrap95" in stats:
                    stats["promptID_cluster_bootstrap95"] = stats.pop("POST_HOC_promptID_cluster_bootstrap95")
                differences.append(dict(contrast=name, updates=step, examples=step*32, split=split, **stats))
    anchor = load(ROOT / "artifacts/nli_learning/train_monoweb_seed17/curve.json")
    report = dict(seed=17, cells=cells, table=rows, differences=differences,
                  zero_cpt_anchor=anchor,
                  uncertainty="Single joint CPT/adaptation seed pilot. Item/cluster CIs do not quantify training-seed variation. No L2 evidence.",
                  scope="Content coverage and cross-document conditioning; zero-CPT anchor is not budget-matched. No novelty claim.")
    path = ROOT / "results/e02_learning_analysis_seed17.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    for row in rows:
        if row["updates"] == 1024:
            print(row["condition"], row["split"], round(100*row["accuracy"], 2))
    for d in differences:
        if d["updates"] == 1024 and d["split"].endswith("test"):
            print(d["contrast"], d["split"], round(d["mean"]*100, 2),
                  np.round(np.array(d["paired_item_bootstrap95"])*100, 2).tolist())
    print(path)


if __name__ == "__main__":
    main()
