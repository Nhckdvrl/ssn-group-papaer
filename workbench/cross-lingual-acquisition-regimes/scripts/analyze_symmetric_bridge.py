"""Audit all E11 learning and MT conditions, without choosing a direction or snapshot."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

from analyze_nli_learning import load
from analyze_qa_bridge import intervals
from analyze_qa_references import audit, STEPS
import nli_learning as nli
import qa_learning as qa
import translation_control as tc
import translation_retention_protocol as protocol

ROOT = Path(__file__).resolve().parents[1]


def cpt_audit(mode):
    folder = ROOT / "artifacts/symmetric_bridge" / f"{mode}_seed17"
    record = load(ROOT / "results" / f"e11_cpt_{mode}_seed17.json")
    done = load(folder / "completion.json")
    metadata = load(ROOT / "results/e11_data_manifest.json")
    assert done["cpt"] == record and record["finite"] and len(record["losses"]) == 256
    assert record["provenance"]["metadata"] == metadata
    assert record["provenance"]["script_sha256"] == hashlib.sha256((ROOT / "scripts/symmetric_bridge_learning.py").read_bytes()).hexdigest()
    assert record["loss_tokens"] == sum(metadata["token_totals"].values())
    assert all(check["split"] < 1e-5 and check["paired"] > 1e-5 for check in record["provenance"]["mask_checks"].values())
    assert (folder / "checkpoint/model.safetensors").is_file()
    return record


def qa_analysis():
    data = load(qa.DATA)
    conditions = ("e11_paired", "e11_split", "e04_reused_paired", "e04_reused_split", "monoweb")
    reports, values, records = {}, {}, {}
    for mode in ("paired", "split"):
        records[mode] = cpt_audit(mode)
    for condition in conditions:
        reports[condition], values[condition] = audit(condition, 17, data)
    reference = reports["monoweb"]["provenance"]
    for report in reports.values():
        for key in ("config", "script_sha256", "device", "torch", "numpy"):
            assert report["provenance"][key] == reference[key]
    for mode in ("paired", "split"):
        intervention = reports[f"e11_{mode}"]["provenance"]["model"]["local_intervention"]
        assert intervention["experiment"] == "E11" and intervention["condition"] == mode
        assert intervention["data_hash"] == records[mode]["provenance"]["metadata"]["pool_sha256"]
    contrasts = (("e11_paired", "e11_split"), ("e11_paired", "e04_reused_paired"),
        ("e11_split", "e04_reused_split"), ("e11_paired", "monoweb"), ("e11_split", "monoweb"))
    differences = []
    for a, b in contrasts:
        for step in STEPS:
            for split in ("en_dev", "en_test", "de_test"):
                clusters = np.array([hashlib.sha256(r["context"].encode()).hexdigest() for r in data["splits"][split]])
                for metric in ("f1", "exact_match"):
                    delta = values[a][step, split, metric] - values[b][step, split, metric]
                    differences.append(dict(contrast=a+"-"+b, updates=step, split=split, metric=metric,
                        **intervals(delta, clusters)))
    report = dict(runs=reports, cpt=records, differences=differences,
        limits="Single joint seed. Symmetric paired/split share content and positions. Forward-only comparison changes language position and direction; zero-CPT is not equal total training cost. E07 translated supervision changes English exposure and input tokens.")
    nli.dump(ROOT / "results/e11_qa_analysis_seed17.json", report)
    for condition, run in reports.items():
        print(condition, "source gate", run["source_learning_gate"],
            {r["split"]: round(100*r["mean"], 2) for r in run["table"] if r["updates"] == 1024 and r["metric"] == "f1"}, flush=True)


def mt_analysis():
    calibration = load(ROOT / "results/e08_retention_hardware_control.json")
    reference = calibration["models"]["monoweb"]["completion"]
    protocol_hash = protocol.assert_protocol()
    rows, completions, hashes = {}, {}, {}
    for mode in ("paired", "split"):
        record = cpt_audit(mode)
        for phase in ("cpt", "post"):
            folder = ROOT / "artifacts/symmetric_bridge_retention" / f"{mode}_seed17" / phase
            done = load(folder / "completion.json")
            assert done["provenance"]["cpt"] == record
            assert done["condition"] == mode and done["phase"] == phase and done["seed"] == 17
            assert done["runner_sha256"] == hashlib.sha256((ROOT / "scripts/symmetric_bridge_retention.py").read_bytes()).hexdigest()
            assert done["protocol_reference_sha256"] == protocol_hash
            assert done["protocol_script_sha256"] == hashlib.sha256(Path(protocol.__file__).read_bytes()).hexdigest()
            assert done["device"] == reference["device"] and done["use_cache"]
            assert done["weight_dtype"] == done["compute_dtype"] == "fp32" and done["max_new_tokens"] == 256
            assert done["items_sha256"] == reference["items_sha256"]
            completions[mode+"_"+phase] = done
            for prompt_mode in ("primary", "instruction"):
                path = folder / f"{prompt_mode}.jsonl"
                sample = [json.loads(line) for line in path.read_text().splitlines()]
                assert len(sample) == 400
                assert tc.digest([{k: r[k] for k in ("id", "direction", "source", "reference", "prompt")} for r in sample]) == reference["items_sha256"]
                rows["symmetric_"+mode, phase, prompt_mode] = sample
                hashes["_".join((mode, phase, prompt_mode))] = hashlib.sha256(path.read_bytes()).hexdigest()
    old_report = load(ROOT / "results/e10_bridge_retention_analysis_seed17.json")
    for mode in ("paired", "split"):
        for phase in ("cpt", "post"):
            for prompt_mode in ("primary", "instruction"):
                path = ROOT / "artifacts/bridge_retention" / f"reused_{mode}_seed17" / phase / f"{prompt_mode}.jsonl"
                assert hashlib.sha256(path.read_bytes()).hexdigest() == old_report["prediction_sha256"][f"reused_{mode}_{phase}_{prompt_mode}"]
                rows["forward_"+mode, phase, prompt_mode] = [json.loads(line) for line in path.read_text().splitlines()]
    directions = {}
    for direction in ("en->de", "de->en"):
        selected = {key: [r for r in sample if r["direction"] == direction] for key, sample in rows.items()}
        first = next(iter(selected.values()))
        identifiers, refs = [r["id"] for r in first], [r["reference"] for r in first]
        assert len(set(identifiers)) == len(identifiers) == 200
        assert all([r["id"] for r in sample] == identifiers and [r["reference"] for r in sample] == refs for sample in selected.values())
        indices = np.random.default_rng(20261002).integers(0, 200, size=(2000, 200))
        metrics, contrasts = {}, {}
        for name, metric in (("bleu", BLEU(tokenize="13a")), ("chrf", CHRF())):
            points, distributions = {}, {}
            for key, sample in selected.items():
                predictions = [r["prediction"] for r in sample]
                score = metric.corpus_score(predictions, [refs]).score
                stats = np.asarray(metric._extract_corpus_statistics(predictions, [refs]))
                assert abs(metric._compute_score_from_stats(stats.sum(axis=0).tolist()).score-score) < 1e-8
                distribution = np.array([metric._compute_score_from_stats(s.tolist()).score for s in stats[indices].sum(axis=1)])
                points[key], distributions[key] = score, distribution
                metrics["_".join(key)+"_"+name] = dict(score=score,
                    sentence_bootstrap95=np.quantile(distribution, [.025, .975]).tolist(), signature=str(metric.get_signature()))

            def contrast(label, weights):
                delta = sum(weight*points[key] for key, weight in weights.items())
                distribution = sum(weight*distributions[key] for key, weight in weights.items())
                contrasts[label+"_"+name] = dict(delta=delta,
                    paired_sentence_bootstrap95=np.quantile(distribution, [.025, .975]).tolist())

            for prompt_mode in ("primary", "instruction"):
                for mode in ("paired", "split"):
                    contrast(f"symmetric_{mode}_{prompt_mode}_post-cpt",
                        {(f"symmetric_{mode}", "post", prompt_mode): 1, (f"symmetric_{mode}", "cpt", prompt_mode): -1})
                    for phase in ("cpt", "post"):
                        contrast(f"symmetric-forward_{mode}_{phase}_{prompt_mode}",
                            {(f"symmetric_{mode}", phase, prompt_mode): 1, (f"forward_{mode}", phase, prompt_mode): -1})
                for phase in ("cpt", "post"):
                    contrast(f"symmetric_paired-split_{phase}_{prompt_mode}",
                        {("symmetric_paired", phase, prompt_mode): 1, ("symmetric_split", phase, prompt_mode): -1})
                contrast(f"symmetric_paired-split_retention_{prompt_mode}",
                    {(f"symmetric_{mode}", phase, prompt_mode): weight*sign for mode, weight in (("paired", 1), ("split", -1))
                        for phase, sign in (("post", 1), ("cpt", -1))})
        directions[direction] = dict(n=200, metrics=metrics, contrasts=contrasts,
            diagnostics={"_".join(key): dict(source_copies=sum(r["source_copied"] for r in sample),
                empty=sum(not r["prediction"] for r in sample), cap=sum(r["token_cap_reached"] for r in sample),
                overflow=sum(r.get("overflow", False) for r in sample)) for key, sample in selected.items()})
    nli.dump(ROOT / "results/e11_translation_analysis_seed17.json", dict(directions=directions,
        completions=completions, prediction_sha256=hashes, resamples=2000, sacrebleu_version=sacrebleu.__version__,
        limits="Single joint seed and 200 news sentences per direction. Prompt-matched costs reported; no knowledge-erasure or novel direction-failure claim."))
    print("E11_MT_ANALYSIS_COMPLETE", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("qa", "mt"))
    args = parser.parse_args()
    qa_analysis() if args.phase == "qa" else mt_analysis()
