"""Within-language LM diagnostics on native and disjoint translated text."""
import argparse
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from frozen_probe import DATA, Scorer, read_data

WIKI = ("wikimedia/wikipedia", "b04c8d1ceb2f5cd4588862100d08de323dccfbaa")


def prepare(output):
    texts = []
    for lang in ["id", "zh"]:
        shard = f"20231101.{lang}/train-00000-of-000{'03' if lang == 'id' else '06'}.parquet"
        path = hf_hub_download(WIKI[0], shard, repo_type="dataset", revision=WIKI[1])
        selected = 0
        for batch in pq.ParquetFile(path).iter_batches(batch_size=512):
            for row in batch.to_pylist():
                if len(row["text"].strip()) < 400:
                    continue
                # A fixed character window defines this diagnostic, not silent truncation.
                text = row["text"].strip()[:400]
                texts.append({"domain": "native_wikipedia", "language": lang,
                              "id": row["id"], "text": text})
                selected += 1
                if selected == 128:
                    break
            if selected == 128:
                break
        assert selected == 128
        evaluated = {r["story_id"] for r in read_data("xstorycloze", lang, "eval")}
        for row in read_data("xstorycloze", lang, "train"):
            assert row["story_id"] not in evaluated
            texts.append({"domain": "translated_story_train", "language": lang,
                          "id": row["story_id"],
                          "text": " ".join(row[f"input_sentence_{i}"] for i in range(1, 5))})
    corpus = {"sources": {"wikipedia": WIKI, "story": DATA["xstorycloze"]},
              "texts": texts, "sha256": hashlib.sha256(json.dumps(texts, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
              "limits": "Not proven unseen during model pretraining. Native wiki first eligible rows are a convenience sample. Compare interventions within a language/domain only; absolute cross-language BPB does not rank competence."}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"items": len(texts), "sha256": corpus["sha256"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--manifest")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.prepare:
        if Path(args.corpus).exists():
            raise FileExistsError(args.corpus)
        prepare(args.corpus)
        return
    if not args.manifest or not args.output:
        parser.error("Scoring requires --manifest and --output")
    if Path(args.output).exists():
        raise FileExistsError(args.output)
    corpus = json.loads(Path(args.corpus).read_text())
    manifest = json.loads(Path(args.manifest).read_text())
    if not manifest["repo"].startswith("nusnlp/JGP-"):
        raise ValueError("This pilot is restricted to JGP")
    scorer = Scorer(manifest["path"], 8, True, "fp32")
    rows = []
    for start in range(0, len(corpus["texts"]), 32):
        block = corpus["texts"][start:start + 32]
        scores = scorer.score([("", row["text"]) for row in block])
        rows.extend({**row, "scores": score} for row, score in zip(block, scores))
        print(f"{len(rows)}/{len(corpus['texts'])}", flush=True)
    result = {"model": manifest, "corpus_sha256": corpus["sha256"], "sources": corpus["sources"],
              "limits": corpus["limits"], "compute": "FP32 on BF16-rounded weights", "rows": rows}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
