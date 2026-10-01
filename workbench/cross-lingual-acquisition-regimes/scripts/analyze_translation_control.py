"""Retain absolute directional metrics and diagnostic generation failures."""
import hashlib
import json
from pathlib import Path

from sacrebleu.metrics import BLEU, CHRF

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main():
    results = {}
    input_hashes = set()
    for condition in ["baseline", "monoweb", "onlyparallel"]:
        path = ROOT / "artifacts/p2" / f"translation_{condition}_34k.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        metadata = json.loads(path.with_suffix(".meta.json").read_text())
        assert len(rows) == metadata["expected_items"]
        assert len({(r["id"], r["direction"]) for r in rows}) == len(rows)
        items = [{k: r[k] for k in ["id", "direction", "source", "reference", "prompt"]} for r in rows]
        assert digest(items) == metadata["items_sha256"]
        input_hashes.add(metadata["items_sha256"])
        result = {"metadata": metadata, "directions": {}}
        for direction in ["en->de", "de->en"]:
            selected = [r for r in rows if r["direction"] == direction]
            hypotheses = [r["prediction"] for r in selected]
            references = [[r["reference"] for r in selected]]
            metrics = {}
            for name, metric in [("bleu", BLEU(tokenize="13a")), ("chrf", CHRF()), ("chrfpp", CHRF(word_order=2))]:
                score = metric.corpus_score(hypotheses, references)
                metrics[name] = {"score": score.score, "signature": str(metric.get_signature())}
            result["directions"][direction] = {"n": len(selected), "metrics": metrics,
                "empty_outputs": sum(not r["prediction"] for r in selected),
                "source_copies": sum(r["source_copied"] for r in selected),
                "cap_reached": sum(r["token_cap_reached"] for r in selected),
                "mean_generated_tokens": sum(len(r["token_ids"]) for r in selected)/len(selected),
                "fixed_sample": [{k: r[k] for k in ["id", "source", "reference", "prediction"]}
                                 for r in selected if r["id"] in [0, 50, 100, 150, 199]]}
        results[condition] = result
    assert len(input_hashes) == 1
    contrasts = {}
    for direction in ["en->de", "de->en"]:
        values = {condition: result["directions"][direction]["metrics"]["bleu"]["score"] for condition, result in results.items()}
        contrasts[direction] = {"mwb_minus_fwb_bleu": values["monoweb"]-values["baseline"],
                               "parallel_minus_mwb_bleu": values["onlyparallel"]-values["monoweb"]}
    output = ROOT / "results/p2_translation_control_34k.json"
    output.write_text(json.dumps({"models": results, "contrasts": contrasts,
        "limits": "First 200 WMT16 examples, news-topic dependence; descriptive, not exact paper reproduction or novelty. Exact source copying is not a comprehensive language classifier. No uncertainty/equivalence claim."}, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps({"output": str(output), "contrasts": contrasts,
        "diagnostics": {k: {d: {x: v[x] for x in ["n", "metrics", "empty_outputs", "source_copies", "cap_reached"]}
                             for d, v in r["directions"].items()} for k, r in results.items()}}, indent=2))


if __name__ == "__main__":
    main()
