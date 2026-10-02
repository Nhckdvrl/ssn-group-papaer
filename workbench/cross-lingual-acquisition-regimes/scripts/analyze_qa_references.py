"""Complete audits for E07 translated supervision and E09 learning repeats."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import qa_learning as qa
from analyze_nli_learning import load
from analyze_qa_bridge import intervals

ROOT = Path(__file__).resolve().parents[1]
STEPS = (0,128,512,1024)


def audit(condition,seed,data):
    folder = ROOT / "artifacts/qa_learning" / f"train_{condition}_seed{seed}"
    done,p = load(folder / "completion.json"),load(folder / "provenance.json")
    core_hash = hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
    assert done["script_sha256"] == p["script_sha256"] == core_hash
    assert done["data_hashes"] == p["metadata"]["hashes"] == data["metadata"]["hashes"]
    assert p["config"] == qa.CONFIG and p["seed"] == seed and p["phase"] == "train"
    assert p["metadata"] == data["metadata"]
    assert (folder / "checkpoint/model.safetensors").is_file()
    curve = load(folder / "curve.json")
    assert tuple(r["updates"] for r in curve) == STEPS
    scorer = qa.scorer()
    assert hashlib.sha256((ROOT / "artifacts/qa_learning/evaluate_squad.py").read_bytes()).hexdigest() == data["metadata"]["scorer"]["sha256"]
    values,table,controls = {},[],[]
    def score(path,split,metric,expected):
        predictions,source = load(path),data["splits"][split]
        assert [r["id"] for r in predictions] == [r["id"] for r in source]
        function = scorer.f1_score if metric == "f1" else scorer.exact_match_score
        scores = np.array([0. if pred["overflow"] else scorer.metric_max_over_ground_truths(
            function,pred["prediction"],row["answers"]["text"]) for pred,row in zip(predictions,source)],dtype=float)
        assert np.allclose(scores,[r[metric] for r in predictions])
        assert abs(scores.mean()-expected[metric]) < 1e-10
        diagnostics = dict(overflow=sum(r["overflow"] for r in predictions),cap=sum(r["cap"] for r in predictions),
            empty=sum(not r["prediction"] for r in predictions))
        assert all(diagnostics[k] == expected[k] for k in diagnostics)
        clusters = np.array([hashlib.sha256(r["context"].encode()).hexdigest() for r in source])
        return scores,clusters,dict(**diagnostics,predictions_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    for point in curve:
        assert set(point["metrics"]) == {"en_dev","en_test","de_test"}
        for split,expected in point["metrics"].items():
            for metric in ("f1","exact_match"):
                scores,clusters,diagnostics = score(folder / f"predictions_{split}_{point['updates']}.json",split,metric,expected)
                values[point["updates"],split,metric] = scores
                table.append(dict(condition=condition,seed=seed,updates=point["updates"],split=split,metric=metric,
                    **intervals(scores,clusters),**diagnostics))
    for split in ("en_test","de_test"):
        for metric in ("f1","exact_match"):
            scores,clusters,diagnostics = score(folder / f"predictions_{split}_instruction.json",split,metric,done["instruction_control"][split])
            controls.append(dict(condition=condition,seed=seed,split=split,metric=metric,instruction_score=float(scores.mean()),
                delta_instruction_minus_primary=intervals(scores-values[1024,split,metric],clusters),**diagnostics))
    return dict(provenance=p,completion=done,table=table,instruction_control=controls,
        source_learning_gate=bool(values[1024,"en_dev","f1"].mean() >= .5)),values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment",choices=("e07","e09"))
    args = parser.parse_args()
    source_data = load(qa.DATA)
    reports,values = {},{}
    if args.experiment == "e07":
        data = load(ROOT / "artifacts/qa_translate_train/run_inputs/data.json")
        wrapper_done = load(ROOT / "artifacts/qa_translate_train/run_inputs/completion.json")
        assert wrapper_done["wrapper_sha256"] == hashlib.sha256((ROOT / "scripts/qa_translate_train_reference.py").read_bytes()).hexdigest()
        assert data["metadata"]["hashes"]["train"] == wrapper_done["train_sha256"]
        requests = (("e07_translate_train",17,data),("monoweb",17,source_data))
    else:
        requests = tuple((condition,seed,source_data) for condition in ("baseline","monoweb","onlyparallel") for seed in (17,29,43))
    for condition,seed,data in requests:
        key = f"{condition}_seed{seed}"
        reports[key],values[condition,seed] = audit(condition,seed,data)
    ref = next(iter(reports.values()))["provenance"]
    for report in reports.values():
        for key in ("config","script_sha256","device","torch","numpy"):
            assert report["provenance"][key] == ref[key]
    differences = []
    contrasts = (("e07_translate_train","monoweb"),) if args.experiment == "e07" else (("onlyparallel","monoweb"),("onlyparallel","baseline"),("monoweb","baseline"))
    seeds = (17,) if args.experiment == "e07" else (17,29,43)
    for a,b in contrasts:
        for seed in seeds:
            for step in STEPS:
                for split in ("en_dev","en_test","de_test"):
                    clusters = np.array([hashlib.sha256(r["context"].encode()).hexdigest() for r in source_data["splits"][split]])
                    for metric in ("f1","exact_match"):
                        delta = values[a,seed][step,split,metric]-values[b,seed][step,split,metric]
                        differences.append(dict(contrast=a+"-"+b,seed=seed,updates=step,split=split,metric=metric,**intervals(delta,clusters)))
    aggregates = []
    if args.experiment == "e09":
        for condition in ("baseline","monoweb","onlyparallel"):
            for step in STEPS:
                for split in ("en_dev","en_test","de_test"):
                    for metric in ("f1","exact_match"):
                        points = [float(values[condition,seed][step,split,metric].mean()) for seed in seeds]
                        aggregates.append(dict(condition=condition,updates=step,split=split,metric=metric,
                            seed_scores=points,mean=float(np.mean(points)),adaptation_seed_sd=float(np.std(points,ddof=1))))
    path = ROOT / "results" / f"{args.experiment}_qa_reference_analysis.json"
    path.write_text(json.dumps(dict(experiment=args.experiment,runs=reports,differences=differences,aggregates=aggregates,
        limits="Item/context intervals and adaptation-seed variation are distinct. Fixed pretraining family, extractive QA. E07 replaces English exposure and changes token cost; E09 seed17 is a discovery run."),indent=2)+"\n")
    for key,report in reports.items():
        print(key,"source gate",report["source_learning_gate"],
              {r["split"]:round(100*r["mean"],2) for r in report["table"] if r["updates"] == 1024 and r["metric"] == "f1"})
    print(path)


if __name__ == "__main__":
    main()
