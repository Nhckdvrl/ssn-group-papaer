"""E10 corpus-level factorial readouts; require every pre/post cell."""
import hashlib
import json
from pathlib import Path

import numpy as np
import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

import translation_control as tc
import translation_retention_protocol as protocol
from analyze_qa_bridge import CONTRASTS

ROOT = Path(__file__).resolve().parents[1]
CELLS = ("new_paired", "new_split", "reused_paired", "reused_split")


def read(path):
    return json.loads(path.read_text())


def main():
    reference_hash = protocol.assert_protocol()
    calibration = read(ROOT / "results/e08_retention_hardware_control.json")
    device = calibration["models"]["monoweb"]["completion"]["device"]
    rows, completions, hashes = {}, {}, {}
    for cell in CELLS:
        for phase in ("cpt", "post"):
            folder = ROOT / "artifacts/bridge_retention" / f"{cell}_seed17" / phase
            done = read(folder / "completion.json")
            assert done["condition"] == cell and done["phase"] == phase and done["seed"] == 17
            assert done["device"] == device and done["use_cache"]
            assert done["weight_dtype"] == done["compute_dtype"] == "fp32"
            assert done["max_new_tokens"] == 256
            assert done["protocol_reference_sha256"] == reference_hash
            assert done["protocol_script_sha256"] == hashlib.sha256(Path(protocol.__file__).read_bytes()).hexdigest()
            runner = ROOT / "scripts/bridge_translation_retention.py"
            assert done["runner_sha256"] == hashlib.sha256(runner.read_bytes()).hexdigest()
            assert done["provenance"]["cpt"] == read(ROOT / "results" / f"e04_cpt_{cell}_seed17.json")
            assert done["items_sha256"] == calibration["models"]["monoweb"]["completion"]["items_sha256"]
            completions[f"{cell}_{phase}"] = done
            for mode in ("primary", "instruction"):
                path = folder / f"{mode}.jsonl"
                sample = [json.loads(line) for line in path.read_text().splitlines()]
                assert len(sample) == 400
                assert tc.digest([{k:r[k] for k in ("id", "direction", "source", "reference", "prompt")} for r in sample]) == done["items_sha256"]
                rows[cell, phase, mode] = sample
                hashes[f"{cell}_{phase}_{mode}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    directions = {}
    for direction in ("en->de", "de->en"):
        selected = {key:[r for r in sample if r["direction"] == direction] for key,sample in rows.items()}
        identifiers = [(r["id"], r["direction"]) for r in next(iter(selected.values()))]
        assert len(set(identifiers)) == len(identifiers) == 200
        assert all([(r["id"],r["direction"]) for r in s] == identifiers for s in selected.values())
        refs = [r["reference"] for r in next(iter(selected.values()))]
        assert all([r["reference"] for r in s] == refs for s in selected.values())
        indices = np.random.default_rng(20261002).integers(0,200,size=(2000,200))
        metrics, contrasts = {}, {}
        for name, metric in (("bleu", BLEU(tokenize="13a")), ("chrf", CHRF())):
            points, distributions = {}, {}
            for key, sample in selected.items():
                predictions = [r["prediction"] for r in sample]
                score = metric.corpus_score(predictions,[refs]).score
                stats = np.asarray(metric._extract_corpus_statistics(predictions,[refs]))
                assert abs(metric._compute_score_from_stats(stats.sum(axis=0).tolist()).score-score) < 1e-8
                dist = np.array([metric._compute_score_from_stats(s.tolist()).score for s in stats[indices].sum(axis=1)])
                points[key], distributions[key] = score, dist
                metrics["_".join(key)+"_"+name] = dict(score=score, sentence_bootstrap95=np.quantile(dist,[.025,.975]).tolist(),signature=str(metric.get_signature()))

            def contrast(label, weights):
                delta = sum(weight*points[key] for key,weight in weights.items())
                distribution = sum(weight*distributions[key] for key,weight in weights.items())
                contrasts[label+"_"+name] = dict(delta=delta, paired_sentence_bootstrap95=np.quantile(distribution,[.025,.975]).tolist())

            for mode in ("primary", "instruction"):
                for cell in CELLS:
                    contrast(f"{cell}_{mode}_post-cpt", {(cell,"post",mode):1,(cell,"cpt",mode):-1})
                for label, weights in CONTRASTS.items():
                    for phase in ("cpt", "post"):
                        contrast(f"{label}_{phase}_{mode}", {(cell,phase,mode):w for cell,w in weights.items()})
                    contrast(f"{label}_retention_{mode}", {(cell,phase,mode):w*sign for cell,w in weights.items() for phase,sign in (("post",1),("cpt",-1))})
        directions[direction] = dict(n=200, metrics=metrics, contrasts=contrasts,
            diagnostics={"_".join(key):dict(source_copies=sum(r["source_copied"] for r in sample),empty=sum(not r["prediction"] for r in sample),cap=sum(r["token_cap_reached"] for r in sample),overflow=sum(r.get("overflow",False) for r in sample)) for key,sample in selected.items()})
    report = dict(directions=directions,completions=completions,prediction_sha256=hashes,
        sacrebleu_version=sacrebleu.__version__,resamples=2000,bootstrap_seed=20261002,
        limits="Single joint training seed; fixed 200 news sentences per direction. Item intervals are not training-seed uncertainty. CPT retention comparisons do not identify knowledge erasure. No zero-CPT budget-matched claim.")
    path = ROOT / "results/e10_bridge_retention_analysis_seed17.json"
    path.write_text(json.dumps(report,indent=2)+"\n")
    print(path)


if __name__ == "__main__":
    main()
