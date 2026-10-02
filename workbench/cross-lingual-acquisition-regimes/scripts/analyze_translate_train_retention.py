"""E07 standard supervised reference versus the English-only task baseline."""
import hashlib
import json
from pathlib import Path

import numpy as np
import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

import translation_control as tc
import translation_retention_protocol as protocol

ROOT = Path(__file__).resolve().parents[1]


def main():
    def read(path):
        return json.loads(path.read_text())
    calibration = read(ROOT / "results/e08_retention_hardware_control.json")
    original = calibration["models"]["monoweb"]["completion"]
    folder = ROOT / "artifacts/qa_translate_train/retention"
    done = read(folder / "completion.json")
    assert done["device"] == original["device"] and done["items_sha256"] == original["items_sha256"]
    assert done["weight_dtype"] == done["compute_dtype"] == "fp32" and done["use_cache"]
    assert done["protocol_reference_sha256"] == protocol.assert_protocol()
    assert done["protocol_script_sha256"] == hashlib.sha256(Path(protocol.__file__).read_bytes()).hexdigest()
    assert done["runner_sha256"] == hashlib.sha256((ROOT / "scripts/translate_train_retention.py").read_bytes()).hexdigest()
    bases = dict(before=ROOT / "artifacts/retention_hardware_control/monoweb",
                 english_only=ROOT / "artifacts/qa_retention/monoweb_seed17",translate_train=folder)
    paths = {(model,mode):base / f"{mode}.jsonl" for model,base in bases.items() for mode in ("primary","instruction")}
    rows = {key:[json.loads(line) for line in path.read_text().splitlines()] for key,path in paths.items()}
    ids = [(r["id"],r["direction"]) for r in rows["before","primary"]]
    assert len(set(ids)) == len(ids) == 400
    for sample in rows.values():
        assert [(r["id"],r["direction"]) for r in sample] == ids
        assert tc.digest([{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in sample]) == original["items_sha256"]
    directions = {}
    for direction in ("en->de","de->en"):
        selected = {key:[r for r in sample if r["direction"] == direction] for key,sample in rows.items()}
        refs = [r["reference"] for r in selected["before","primary"]]
        assert len(refs) == 200 and all([r["reference"] for r in s] == refs for s in selected.values())
        indices = np.random.default_rng(20261002).integers(0,200,size=(2000,200))
        metrics,contrasts = {},{}
        for name,metric in (("bleu",BLEU(tokenize="13a")),("chrf",CHRF())):
            points,distributions = {},{}
            for key,sample in selected.items():
                predictions = [r["prediction"] for r in sample]
                point = metric.corpus_score(predictions,[refs]).score
                stats = np.asarray(metric._extract_corpus_statistics(predictions,[refs]))
                assert abs(metric._compute_score_from_stats(stats.sum(axis=0).tolist()).score-point) < 1e-8
                dist = np.array([metric._compute_score_from_stats(s.tolist()).score for s in stats[indices].sum(axis=1)])
                points[key],distributions[key] = point,dist
                metrics["_".join(key)+"_"+name] = dict(score=point,sentence_bootstrap95=np.quantile(dist,[.025,.975]).tolist(),signature=str(metric.get_signature()))
            for mode in ("primary","instruction"):
                for a,b in (("translate_train","before"),("english_only","before"),("translate_train","english_only")):
                    contrasts[f"{a}-{b}_{mode}_{name}"] = dict(delta=points[a,mode]-points[b,mode],paired_sentence_bootstrap95=np.quantile(distributions[a,mode]-distributions[b,mode],[.025,.975]).tolist())
        directions[direction] = dict(metrics=metrics,contrasts=contrasts,diagnostics={"_".join(key):dict(source_copies=sum(r["source_copied"] for r in s),empty=sum(not r["prediction"] for r in s),cap=sum(r["token_cap_reached"] for r in s),overflow=sum(r.get("overflow",False) for r in s)) for key,s in selected.items()})
    path = ROOT / "results/e07_translation_retention_analysis.json"
    path.write_text(json.dumps(dict(completion=done,directions=directions,sacrebleu_version=sacrebleu.__version__,resamples=2000,
        prediction_sha256={"_".join(key):hashlib.sha256(p.read_bytes()).hexdigest() for key,p in paths.items()},
        limits="Single seed17, fixed200 news sentences per direction. Translation supervision changes language exposure and increases input tokens13.29%; not pure correspondence or equal-compute comparison."),indent=2)+"\n")
    print(path)


if __name__ == "__main__":
    main()
