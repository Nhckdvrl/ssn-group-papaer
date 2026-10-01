"""Natural question-swap controls and independent answer-language burden in XQuAD."""
import argparse
import collections
import hashlib
import itertools
import json
from pathlib import Path

import pyarrow.parquet as pq
import torch
from huggingface_hub import hf_hub_download
from transformers.data.metrics.squad_metrics import compute_exact, compute_f1

from frozen_probe import Scorer

DATA = ("google/xquad", "51adfef1c1287aab1d2d91b5bead9bcfb9c68583")
LANGS = ["en", "de"]


def read_docs():
    documents = {}
    invalid = []
    for lang in LANGS:
        path = hf_hub_download(DATA[0], f"xquad.{lang}/validation-00000-of-00001.parquet", repo_type="dataset", revision=DATA[1])
        documents[lang] = pq.read_table(path).to_pylist()
    ids = [r["id"] for r in documents["en"]]
    for lang in LANGS:
        indexed = {r["id"]: r for r in documents[lang]}
        assert len(indexed) == len(ids) and set(indexed) == set(ids)
        documents[lang] = {i: indexed[i] for i in ids}
        for row in documents[lang].values():
            for answer, start in zip(row["answers"]["text"], row["answers"]["answer_start"]):
                if row["context"][start:start + len(answer)] != answer:
                    invalid.append({"lang": lang, "id": row["id"], "answer": answer, "start": start})
    excluded = {r["id"] for r in invalid}
    ids = [i for i in ids if i not in excluded]
    print("Annotation-offset exclusions:", json.dumps(invalid, ensure_ascii=False), flush=True)
    return documents, ids, invalid


def question_prompt(context, question):
    return "Context: " + context + "\nQuestion: " + question + "\nAnswer:"


def construct(documents, ids, limit):
    groups = collections.defaultdict(list)
    for identifier in ids:
        groups[documents["en"][identifier]["context"]].append(identifier)
    pairs = []
    for group in groups.values():
        for a, b in itertools.combinations(group, 2):
            if any(documents[lang][a]["context"] != documents[lang][b]["context"] for lang in LANGS):
                continue
            answers = [[documents[lang][i]["answers"]["text"][0] for i in [a, b]] for lang in LANGS]
            if any(not all(2 <= len(s) <= 80 for s in options) for options in answers):
                continue
            if any(x.lower() in y.lower() or y.lower() in x.lower() for x, y in answers):
                continue
            pairs.append((a, b))
            break
    # Five short demonstrations, selected by text length only, from different paragraphs.
    demos = sorted(pairs, key=lambda pair: max(len(documents[lang][pair[0]]["context"]) for lang in LANGS))[:5]
    candidates = [pair for pair in pairs if pair not in demos][:limit]
    assert len(demos) == 5 and len(candidates) == limit
    return demos, candidates


def build_items(documents, demos, pairs):
    items = []
    for index, pair in enumerate(pairs):
        sensitive = any(documents["en"][i]["answers"]["text"][0].casefold() != documents["de"][i]["answers"]["text"][0].casefold() for i in pair)
        for context_lang, question_lang, answer_lang in itertools.product(LANGS, repeat=3):
            examples = [question_prompt(documents[context_lang][p[0]]["context"], documents[question_lang][p[0]]["question"]) + " " + documents[answer_lang][p[0]]["answers"]["text"][0] for p in demos]
            prefix = "\n\n".join(examples) + "\n\n"
            options = [" " + documents[answer_lang][i]["answers"]["text"][0] for i in pair]
            for question_index, identifier in enumerate(pair):
                context = documents[context_lang][identifier]["context"]
                question = documents[question_lang][identifier]["question"]
                items.append({"pair": index, "source_id": identifier, "question_index": question_index,
                              "context_lang": context_lang, "question_lang": question_lang, "answer_lang": answer_lang,
                              "answer_language_sensitive": sensitive, "options": options, "gold": question_index,
                              "references": documents[answer_lang][identifier]["answers"]["text"],
                              "prompt": prefix + question_prompt(context, question),
                              "question_only_prompt": prefix + question_prompt("", question)})
    return items


@torch.inference_mode()
def generate(scorer, prompts):
    scorer.tokenizer.padding_side = "left"
    if scorer.tokenizer.pad_token_id is None:
        scorer.tokenizer.pad_token = scorer.tokenizer.eos_token
    encoded = scorer.tokenizer(prompts, padding=True, add_special_tokens=False, return_tensors="pt").to("cuda")
    assert encoded.input_ids.shape[1] + 64 <= scorer.model.config.max_position_embeddings
    output = scorer.model.generate(**encoded, do_sample=False, max_new_tokens=64,
                                  eos_token_id=scorer.tokenizer.eos_token_id,
                                  pad_token_id=scorer.tokenizer.pad_token_id,
                                  stop_strings=["\n"], tokenizer=scorer.tokenizer)
    continuations = output[:, encoded.input_ids.shape[1]:]
    return scorer.tokenizer.batch_decode(continuations, skip_special_tokens=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--pairs", type=int, default=50)
    parser.add_argument("--output", required=True)
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    path = Path(args.output)
    if path.exists():
        raise FileExistsError(path)
    manifest = json.loads(Path(args.manifest).read_text())
    scorer = Scorer(manifest["path"], 4, compute_dtype="fp32")
    documents, ids, invalid = read_docs()
    demos, pairs = construct(documents, ids, args.pairs)
    items = build_items(documents, demos, pairs)
    # Exclude a whole semantic pair from every cell if any prompt cannot fit.
    oversized = {item["pair"] for item in items if any(len(scorer.tokenizer.encode(item[key], add_special_tokens=False)) + 64 > scorer.model.config.max_position_embeddings for key in ["prompt", "question_only_prompt"])}
    items = [item for item in items if item["pair"] not in oversized]
    assert len(items) > 0
    digest = hashlib.sha256(json.dumps(items, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    metadata = {"model": manifest, "data": DATA, "args": vars(args), "demos": demos,
                "expected_items": len(items), "excluded_oversized_pairs": sorted(oversized), "annotation_offset_exclusions": invalid, "items_sha256": digest,
                "scope": "Five English-frame demonstrations; output language specified by demonstration answers only. Binary natural question-swap and free generation diagnostic, not a full parent reproduction.",
                "precision": "FP32 compute on BF16-rounded weights"}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".meta.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with path.open("w") as output:
        for start in range(0, len(items), 16):
            block = items[start:start + 16]
            full = scorer.score([(i["prompt"], option) for i in block for option in i["options"]])
            question_only = scorer.score([(i["question_only_prompt"], option) for i in block for option in i["options"]])
            generated = []
            if args.generate:
                for k in range(0, len(block), 4):
                    generated.extend(generate(scorer, [i["prompt"] for i in block[k:k + 4]]))
            for k, item in enumerate(block):
                row = {**item, "scores": full[2 * k:2 * k + 2], "question_only_scores": question_only[2 * k:2 * k + 2]}
                if args.generate:
                    raw = generated[k]
                    prediction = raw.split("\n", 1)[0].strip()
                    row.update({"generated_raw": raw, "generated_answer": prediction,
                                "em": max(compute_exact(r, prediction) for r in item["references"]),
                                "f1": max(compute_f1(r, prediction) for r in item["references"])})
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
            output.flush()
            print(f"{min(start + 16, len(items))}/{len(items)}", flush=True)
    print("COMPLETE", path, flush=True)


if __name__ == "__main__":
    main()
