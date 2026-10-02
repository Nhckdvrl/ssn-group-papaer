"""Corpus-level paired retention intervals using sacreBLEU sufficient statistics."""
import hashlib
import json
from pathlib import Path

import numpy as np
import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

import translation_control as tc

ROOT = Path(__file__).resolve().parents[1]


def main():
    reports, all_hashes = {}, set()
    for condition in ("baseline", "monoweb", "onlyparallel"):
        folder = ROOT / "artifacts/qa_retention" / f"{condition}_seed17"
        done = json.loads((folder / "completion.json").read_text())
        assert done["script_sha256"] == hashlib.sha256((ROOT / "scripts/qa_translation_retention.py").read_bytes()).hexdigest()
        before_path = ROOT / "artifacts/p2" / f"translation_{condition}_34k.jsonl"
        assert hashlib.sha256(before_path.read_bytes()).hexdigest() == done["before_sha256"]
        paths = dict(before=before_path, primary=folder / "primary.jsonl", instruction=folder / "instruction.jsonl")
        rows = {mode:[json.loads(line) for line in path.read_text().splitlines()] for mode,path in paths.items()}
        identifiers = [(r["id"],r["direction"]) for r in rows["before"]]
        assert len(set(identifiers)) == len(identifiers) == done["before_metadata"]["expected_items"]
        for mode, sample in rows.items():
            assert [(r["id"],r["direction"]) for r in sample] == identifiers
            assert tc.digest([{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in sample]) == done["items_sha256"]
        all_hashes.add(done["items_sha256"])
        directions = {}
        for direction in ("en->de", "de->en"):
            selected = {mode:[r for r in sample if r["direction"]==direction] for mode,sample in rows.items()}
            references = [r["reference"] for r in selected["before"]]
            n = len(references)
            metrics, contrasts = {}, {}
            sample_ids = np.random.default_rng(20261002).integers(0,n,size=(2000,n))
            for name,metric in (("bleu",BLEU(tokenize="13a")),("chrf",CHRF())):
                distributions, point = {}, {}
                for mode,sample in selected.items():
                    hypotheses = [r["prediction"] for r in sample]
                    score = metric.corpus_score(hypotheses,[references]).score
                    # Use library statistics, not a hand-rolled BLEU or chrF formula.
                    stats = np.asarray(metric._extract_corpus_statistics(hypotheses,[references]))
                    assert len(stats)==n
                    assert abs(metric._compute_score_from_stats(stats.sum(axis=0).tolist()).score-score)<1e-8
                    distribution = np.array([metric._compute_score_from_stats(s.tolist()).score
                                             for s in stats[sample_ids].sum(axis=1)])
                    distributions[mode], point[mode] = distribution, score
                    metrics[mode+"_"+name] = dict(score=score,signature=str(metric.get_signature()),
                        sentence_bootstrap95=np.quantile(distribution,[.025,.975]).tolist())
                for a,b in (("primary","before"),("instruction","primary"),("instruction","before")):
                    contrasts[a+"-"+b+"_"+name] = dict(delta=point[a]-point[b],
                        paired_sentence_bootstrap95=np.quantile(distributions[a]-distributions[b],[.025,.975]).tolist())
            directions[direction] = dict(n=n, metrics=metrics, contrasts=contrasts,
                diagnostics={mode:dict(empty=sum(not r["prediction"] for r in sample),
                    source_copies=sum(r["source_copied"] for r in sample),
                    cap=sum(r["token_cap_reached"] for r in sample),
                    overflow=sum(r.get("overflow",False) for r in sample)) for mode,sample in selected.items()})
        reports[condition] = dict(completion=done,directions=directions,
            prediction_sha256={mode:hashlib.sha256(path.read_bytes()).hexdigest() for mode,path in paths.items()})
    assert len(all_hashes)==1
    report = dict(models=reports,sacrebleu_version=sacrebleu.__version__,bootstrap_seed=20261002,
        resamples=2000,limits="Fixed 200 news sentences and one adaptation seed. Sentence intervals do not model topic or training-seed variation. Instruction recovery is not a universal competence test.")
    path = ROOT / "results/e06_qa_translation_retention.json"
    path.write_text(json.dumps(report,indent=2)+"\n")
    for condition,r in reports.items():
        for direction,v in r["directions"].items():
            print(condition,direction,{k:round(x["score"],2) for k,x in v["metrics"].items() if k.endswith("_bleu")})
    print(path)


if __name__ == "__main__":
    main()
