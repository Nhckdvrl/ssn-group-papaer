"""E09 all-seed retention, separating item intervals from adaptation variation."""
import hashlib
import json
from pathlib import Path

import numpy as np
import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

import qa_learning as qa
import translation_control as tc
import translation_retention_protocol as protocol

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ("baseline", "monoweb", "onlyparallel")
SEEDS = (17,29,43)


def read(path):
    return json.loads(path.read_text())


def main():
    calibration = read(ROOT / "results/e08_retention_hardware_control.json")
    assert calibration["protocol_ast_equal"]
    core_hash = hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
    data = read(qa.DATA)
    reports, aggregates = {}, []
    for condition in CONDITIONS:
        original = calibration["models"][condition]["completion"]
        pre_folder = ROOT / "artifacts/retention_hardware_control" / condition
        for seed in SEEDS:
            folder = ROOT / ("artifacts/qa_retention" if seed == 17 else "artifacts/qa_retention_repeats") / f"{condition}_seed{seed}"
            done = read(folder / "completion.json")
            p = done["qa_provenance"]
            assert done["condition"] == condition and done["seed"] == p["seed"] == seed
            assert done["device"] == original["device"] and done["use_cache"]
            assert done["weight_dtype"] == done["compute_dtype"] == "fp32"
            assert done["items_sha256"] == original["items_sha256"]
            assert p["script_sha256"] == core_hash and p["metadata"]["hashes"] == data["metadata"]["hashes"]
            assert p["config"] == qa.CONFIG and p["model"] == original["model"]
            if seed == 17:
                assert done["script_sha256"] == protocol.assert_protocol()
            else:
                assert done["protocol_reference_sha256"] == protocol.assert_protocol()
                assert done["protocol_script_sha256"] == hashlib.sha256(Path(protocol.__file__).read_bytes()).hexdigest()
                assert done["runner_sha256"] == hashlib.sha256((ROOT / "scripts/qa_repeat_translation_retention.py").read_bytes()).hexdigest()
                assert done["qa_completion"] == read(ROOT / "artifacts/qa_learning" / f"train_{condition}_seed{seed}/completion.json")
            paths = {f"{phase}_{mode}":base / f"{mode}.jsonl" for phase,base in (("before",pre_folder),("post",folder)) for mode in ("primary","instruction")}
            rows = {key:[json.loads(line) for line in path.read_text().splitlines()] for key,path in paths.items()}
            ids = [(r["id"],r["direction"]) for r in rows["before_primary"]]
            assert len(set(ids)) == len(ids) == 400
            for sample in rows.values():
                assert [(r["id"],r["direction"]) for r in sample] == ids
                assert tc.digest([{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in sample]) == original["items_sha256"]
            directions = {}
            for direction in ("en->de","de->en"):
                selected = {key:[r for r in sample if r["direction"] == direction] for key,sample in rows.items()}
                refs = [r["reference"] for r in selected["before_primary"]]
                assert len(refs) == 200
                assert all([r["reference"] for r in sample] == refs for sample in selected.values())
                indices = np.random.default_rng(20261002).integers(0,200,size=(2000,200))
                metrics, contrasts = {}, {}
                for name,metric in (("bleu",BLEU(tokenize="13a")),("chrf",CHRF())):
                    points, distributions = {}, {}
                    for mode,sample in selected.items():
                        predictions = [r["prediction"] for r in sample]
                        point = metric.corpus_score(predictions,[refs]).score
                        stats = np.asarray(metric._extract_corpus_statistics(predictions,[refs]))
                        assert abs(metric._compute_score_from_stats(stats.sum(axis=0).tolist()).score-point) < 1e-8
                        dist = np.array([metric._compute_score_from_stats(s.tolist()).score for s in stats[indices].sum(axis=1)])
                        points[mode], distributions[mode] = point, dist
                        metrics[mode+"_"+name] = dict(score=point,sentence_bootstrap95=np.quantile(dist,[.025,.975]).tolist(),signature=str(metric.get_signature()))
                    for mode in ("primary","instruction"):
                        a,b = "post_"+mode,"before_"+mode
                        contrasts[mode+"_post-before_"+name] = dict(delta=points[a]-points[b],paired_sentence_bootstrap95=np.quantile(distributions[a]-distributions[b],[.025,.975]).tolist())
                directions[direction] = dict(metrics=metrics,contrasts=contrasts,
                    diagnostics={mode:dict(source_copies=sum(r["source_copied"] for r in sample),empty=sum(not r["prediction"] for r in sample),cap=sum(r["token_cap_reached"] for r in sample),overflow=sum(r.get("overflow",False) for r in sample)) for mode,sample in selected.items()})
            reports[f"{condition}_seed{seed}"] = dict(completion=done,directions=directions,prediction_sha256={mode:hashlib.sha256(path.read_bytes()).hexdigest() for mode,path in paths.items()})
        for direction in ("en->de","de->en"):
            for mode in ("primary","instruction"):
                for metric in ("bleu","chrf"):
                    deltas = [reports[f"{condition}_seed{seed}"]["directions"][direction]["contrasts"][mode+"_post-before_"+metric]["delta"] for seed in SEEDS]
                    aggregates.append(dict(condition=condition,direction=direction,mode=mode,metric=metric,seeds=list(SEEDS),seed_deltas=deltas,mean=float(np.mean(deltas)),adaptation_seed_sd=float(np.std(deltas,ddof=1))))
    path = ROOT / "results/e09_retention_reliability.json"
    path.write_text(json.dumps(dict(runs=reports,aggregates=aggregates,sacrebleu_version=sacrebleu.__version__,resamples=2000,
        limits="Seed17 discovery; all29/43 validation. Adaptation seeds are not pretraining replicas. Item intervals are distinct from seed SD. Fixed200 news per direction; same-instruction pre/post, no universal knowledge-erasure or parallel-causality claim."),indent=2)+"\n")
    print(path)


if __name__ == "__main__":
    main()
