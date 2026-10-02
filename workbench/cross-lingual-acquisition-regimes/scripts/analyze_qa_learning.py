"""Recompute official QA scores and preregistered context-cluster intervals."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import qa_learning as qa
from analyze_nli_learning import bootstrap, load

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("pilot", "train"))
    args = parser.parse_args()
    data = load(qa.DATA)
    scorer = qa.scorer()
    assert hashlib.sha256((ROOT / "artifacts/qa_learning/evaluate_squad.py").read_bytes()).hexdigest() == data["metadata"]["scorer"]["sha256"]
    conditions = ("baseline",) if args.phase == "pilot" else ("baseline", "monoweb", "onlyparallel")
    rows, values, provenance, controls = [], {}, {}, []
    for condition in conditions:
        folder = ROOT / "artifacts/qa_learning" / f"{args.phase}_{condition}_seed17"
        done = load(folder / "completion.json")
        p = load(folder / "provenance.json")
        assert done["data_hashes"] == data["metadata"]["hashes"]
        provenance[condition] = p
        curve = load(folder / "curve.json")
        steps = (0,128,512) if args.phase == "pilot" else (0,128,512,1024)
        assert tuple(r["updates"] for r in curve) == steps
        for point in curve:
            for split, metrics in point["metrics"].items():
                path = folder / f"predictions_{split}_{point['updates']}.json"
                predictions = load(path)
                source = data["splits"][split]
                assert [r["id"] for r in predictions] == [r["id"] for r in source]
                clusters = np.array([hashlib.sha256(r["context"].encode()).hexdigest() for r in source])
                for metric, function in (("f1",scorer.f1_score),("exact_match",scorer.exact_match_score)):
                    scores = np.array([0. if pred["overflow"] else scorer.metric_max_over_ground_truths(function,pred["prediction"],r["answers"]["text"]) for pred,r in zip(predictions,source)],dtype=float)
                    assert np.allclose(scores, [r[metric] for r in predictions])
                    assert abs(scores.mean()-metrics[metric]) < 1e-10
                    values[condition,point["updates"],split,metric] = scores
                    stats = bootstrap(scores,clusters)
                    stats["context_cluster_bootstrap95"] = stats.pop("POST_HOC_promptID_cluster_bootstrap95")
                    stats["n_context_clusters"] = stats.pop("n_promptID_clusters")
                    rows.append(dict(condition=condition,updates=point["updates"],split=split,metric=metric,**stats,
                                     predictions_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                     overflow=metrics["overflow"],cap=metrics["cap"],empty=metrics["empty"]))
        if args.phase == "train":
            for split in ("en_test","de_test"):
                source = data["splits"][split]
                path = folder / f"predictions_{split}_instruction.json"
                predictions = load(path)
                assert [r["id"] for r in predictions] == [r["id"] for r in source]
                clusters = np.array([hashlib.sha256(r["context"].encode()).hexdigest() for r in source])
                for metric,function in (("f1",scorer.f1_score),("exact_match",scorer.exact_match_score)):
                    scores = np.array([0. if pred["overflow"] else scorer.metric_max_over_ground_truths(function,pred["prediction"],r["answers"]["text"]) for pred,r in zip(predictions,source)],dtype=float)
                    assert np.allclose(scores,[r[metric] for r in predictions])
                    assert abs(scores.mean()-done["instruction_control"][split][metric]) < 1e-10
                    stats = bootstrap(scores-values[condition,1024,split,metric],clusters)
                    stats["context_cluster_bootstrap95"] = stats.pop("POST_HOC_promptID_cluster_bootstrap95")
                    stats["n_context_clusters"] = stats.pop("n_promptID_clusters")
                    controls.append(dict(condition=condition,updates=1024,split=split,metric=metric,
                                         instruction_score=float(scores.mean()),delta_instruction_minus_primary=stats,
                                         predictions_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                         overflow=sum(r["overflow"] for r in predictions),
                                         cap=sum(r["cap"] for r in predictions),empty=sum(not r["prediction"] for r in predictions)))
    ref = provenance["baseline"]
    for p in provenance.values():
        for key in ("config","metadata","script_sha256","train_encoded_sha256","device"):
            assert p[key] == ref[key], key
    differences = []
    if args.phase == "train":
        for a,b in (("monoweb","baseline"),("onlyparallel","monoweb"),("onlyparallel","baseline")):
            for step in steps:
                for split in ("en_test","de_test"):
                    clusters = np.array([hashlib.sha256(r["context"].encode()).hexdigest() for r in data["splits"][split]])
                    for metric in ("f1","exact_match"):
                        delta = values[a,step,split,metric]-values[b,step,split,metric]
                        stats = bootstrap(delta,clusters)
                        stats["context_cluster_bootstrap95"] = stats.pop("POST_HOC_promptID_cluster_bootstrap95")
                        stats["n_context_clusters"] = stats.pop("n_promptID_clusters")
                        differences.append(dict(contrast=f"{a}-{b}",updates=step,split=split,metric=metric,**stats))
    report = dict(phase=args.phase, seed=17, table=rows, differences=differences,instruction_control=controls,
                  uncertainty="One adaptation seed; item/context intervals do not quantify training-seed uncertainty.",
                  scope="Effective generation-learning baseline, not new causal mechanism or novelty.")
    path = ROOT / "results" / f"e03_{args.phase}_analysis_seed17.json"
    path.write_text(json.dumps(report,indent=2)+"\n")
    for row in rows:
        if row["updates"] == steps[-1]:
            print(row["condition"],row["split"],row["metric"],round(100*row["mean"],2),
                  np.round(np.array(row["context_cluster_bootstrap95"])*100,2).tolist())
    print(path)


if __name__ == "__main__":
    main()
