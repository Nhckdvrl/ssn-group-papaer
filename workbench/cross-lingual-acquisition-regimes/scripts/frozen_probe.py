"""Matched-item frozen probes; complete likelihoods retained for alternative readouts."""
import argparse
import csv
import hashlib
import json
import math
import re
import time
from pathlib import Path

import pyarrow.parquet as pq
import torch
import transformers
from huggingface_hub import hf_hub_download
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
DATA = {
    "xcopa": ("cambridgeltl/xcopa", "042f78955ba48e6404616762fa6e05e839c3907a"),
    "xnli": ("facebook/xnli", "b8dd5d7af51114dbda02c0e3f6133f332186418e"),
    "hellaswag": ("alexandrainst/m_hellaswag", "9d31dc982bd6285e081e3e3136332a38b9c1d7b7"),
    "xstorycloze": ("juletxara/xstory_cloze", "c4c2d88a1ec8b37fe22166d2a610f272726724b6"),
}
CONNECTORS = {"id": {"cause": "karena", "effect": "maka"}, "zh": {"cause": "因为", "effect": "所以"}}
NLI = {"en": [", right? Yes, ", ", right? Also, ", ", right? No, "],
       "de": [", richtig? Ja, ", ", richtig? Auch, ", ", richtig? Nein, "]}


def read_data(task, language, split):
    repo, revision = DATA[task]
    if task == "xstorycloze":
        path = hf_hub_download(repo, f"spring2016.val.{language}.tsv.split_20_80_{split}.tsv", repo_type="dataset", revision=revision)
        with open(path) as source:
            return list(csv.DictReader(source, delimiter="\t"))
    if task == "hellaswag":
        path = hf_hub_download(repo, f"data/{language}/val.jsonl", repo_type="dataset", revision=revision)
        return [json.loads(line) for line in Path(path).read_text().splitlines()]
    path = hf_hub_download(repo, f"{language}/{split}-00000-of-00001.parquet", repo_type="dataset", revision=revision)
    return pq.read_table(path).to_pylist()


class Scorer:
    def __init__(self, path, batch, legacy_pickle=False, compute_dtype="bf16", weight_dtype="bf16"):
        if weight_dtype == "fp32" and compute_dtype != "fp32":
            raise ValueError("Native FP32 weights require FP32 computation")
        dtype = torch.float32 if weight_dtype == "fp32" else torch.bfloat16
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        if legacy_pickle:
            # Transformers 5.3 drops weights_only=False in one unsharded loading path.
            # Load the pinned official state dict explicitly and check every key.
            config = AutoConfig.from_pretrained(path, local_files_only=True)
            self.model = AutoModelForCausalLM.from_config(config, dtype=dtype, attn_implementation="sdpa")
            state = torch.load(Path(path) / "pytorch_model.bin", map_location="cpu", weights_only=False)
            self.model.load_state_dict(state, strict=True)
            del state
        else:
            self.model = AutoModelForCausalLM.from_pretrained(path, dtype=dtype, local_files_only=True, attn_implementation="sdpa")
        self.model = self.model.to("cuda").eval()
        if compute_dtype == "fp32":
            # Default experiments hold BF16-rounded weights fixed; FP32 loading is explicit.
            self.model = self.model.float()
        self.batch = batch
        self.pad = self.tokenizer.pad_token_id
        if self.pad is None:
            self.pad = self.tokenizer.eos_token_id

    def encode(self, context, continuation):
        # Match harness boundary handling: move context trailing whitespace to continuation.
        trailing = len(context) - len(context.rstrip())
        if trailing:
            continuation = context[-trailing:] + continuation
            context = context[:-trailing]
        if not context:
            target = self.tokenizer.encode(continuation, add_special_tokens=False)
            return [self.tokenizer.bos_token_id or self.tokenizer.eos_token_id] + target, 1
        full = self.tokenizer.encode(context + continuation, add_special_tokens=False)
        prefix = self.tokenizer.encode(context, add_special_tokens=False)
        if full[:len(prefix)] != prefix:
            raise ValueError("Tokenizer changes context boundary; adjust prompt separator")
        return full, len(prefix)

    @torch.inference_mode()
    def score(self, requests):
        encoded = [self.encode(*request) for request in requests]
        results = []
        for start in range(0, len(encoded), self.batch):
            block = encoded[start:start + self.batch]
            length = max(len(ids) for ids, _ in block)
            if length > self.model.config.max_position_embeddings:
                raise ValueError(f"Context too long: {length}; never silently truncate")
            inputs = torch.full((len(block), length), self.pad, device="cuda", dtype=torch.long)
            mask = torch.zeros_like(inputs)
            for row, (ids, _) in enumerate(block):
                inputs[row, :len(ids)] = torch.tensor(ids, device="cuda")
                mask[row, :len(ids)] = 1
            logits = self.model(input_ids=inputs, attention_mask=mask, use_cache=False).logits
            for row, (ids, boundary) in enumerate(block):
                selected = logits[row, boundary - 1:len(ids) - 1].float()
                target = inputs[row, boundary:len(ids)]
                ll = selected.gather(1, target[:, None]).squeeze(1) - selected.logsumexp(-1)
                results.append({"ll": ll.sum().item(), "tokens": len(target), "token_ll": ll.tolist()})
        return results


def build_items(task, target_languages, limit, shots, readout="joint"):
    if task == "xstorycloze":
        if shots or readout != "joint":
            raise ValueError("XStoryCloze uses a fixed zero-shot continuation readout")
        docs = {lang: read_data(task, lang, "eval") for lang in target_languages}
        identifiers = [row["story_id"] for row in docs[target_languages[0]]]
        for lang in target_languages:
            indexed = {row["story_id"]: row for row in docs[lang]}
            assert len(indexed) == len(docs[lang])
            assert set(indexed) == set(identifiers)
            docs[lang] = [indexed[i] for i in identifiers]
        items = []
        for a in target_languages:
            for b in target_languages:
                for index in range(min(limit, len(identifiers))):
                    premise, choice = docs[a][index], docs[b][index]
                    assert premise["answer_right_ending"] == choice["answer_right_ending"]
                    context = " ".join(premise[f"input_sentence_{j}"] for j in range(1, 5))
                    items.append({"task": task, "id": index, "source_id": identifiers[index],
                                  "premise_lang": a, "choice_lang": b, "slice": "story",
                                  "context": context, "gold": int(choice["answer_right_ending"]) - 1,
                                  "options": [" " + choice[f"sentence_quiz{j}"] for j in [1, 2]]})
        return items, []
    if task == "hellaswag":
        def clean(text):
            return re.sub(r"\[.*?\]", "", text.strip().replace(" [title]", ". ")).replace("  ", " ")
        documents = {lang: read_data(task, lang, "val") for lang in target_languages}
        canonical_ids = [row["id"] for row in documents[target_languages[0]]]
        for lang in target_languages:
            indexed = {row["id"]: row for row in documents[lang]}
            assert len(indexed) == len(documents[lang])
            documents[lang] = [indexed[item_id] for item_id in canonical_ids]
        items = []
        for a in target_languages:
            for b in target_languages:
                examples = []
                for i in range(shots):
                    p, c = documents[a][i], documents[b][i]
                    assert p["id"] == c["id"]
                    query = clean(p["activity_label"] + ": " + p["ctx_a"] + " " + p["ctx_b"].capitalize())
                    examples.append(query + " " + clean(c["endings"][int(c["label"])]))
                for i in range(shots, min(shots + limit, len(documents[a]))):
                    p, c = documents[a][i], documents[b][i]
                    assert p["id"] == c["id"]
                    if "ind" in p:
                        assert p["ind"] == c["ind"]
                    query = clean(p["activity_label"] + ": " + p["ctx_a"] + " " + p["ctx_b"].capitalize())
                    items.append({"task": task, "id": i, "premise_lang": a, "choice_lang": b, "slice": p["activity_label"],
                                  "source_id": p["id"], "gold": int(c["label"]), "context": "\n\n".join(examples + [query]),
                                  "options": [" " + clean(text) for text in c["endings"]]})
        return items, []
    languages = ["id", "zh"] if task == "xcopa" else ["en", "de"]
    split = "test" if task == "xcopa" else "validation"
    docs = {lang: read_data(task, lang, split) for lang in languages}
    count = min(len(rows) for rows in docs.values())
    valid = []
    exclusions = []
    for index in range(min(count, limit)):
        if task == "xcopa":
            assert len({docs[lang][index]["idx"] for lang in languages}) == 1
            # XCOPA reannotates some translations. Such items cannot form a controlled
            # cross-language composition pair, even when numeric labels happen to match.
            if any(docs[lang][index].get("changed", False) for lang in languages) or len({docs[lang][index]["question"] for lang in languages}) != 1 or len({docs[lang][index]["label"] for lang in languages}) != 1:
                exclusions.append(index)
                continue
        else:
            assert len({docs[lang][index]["label"] for lang in languages}) == 1, "Cross-language row labels disagree"
        valid.append(index)
    demos = {lang: read_data(task, lang, "validation" if task == "xcopa" else "train")[:shots] for lang in languages} if shots else {}
    items = []
    for premise_lang in target_languages:
        for choice_lang in target_languages:
            for index in valid:
                premise, choice = docs[premise_lang][index], docs[choice_lang][index]
                if task == "xcopa":
                    context = premise["premise"].strip()[:-1] + " " + CONNECTORS[premise_lang][premise["question"]]
                    options = [" " + choice[key][0].lower() + choice[key][1:] for key in ["choice1", "choice2"]]
                    if shots:
                        examples = []
                        for dp, dc in zip(demos[premise_lang], demos[choice_lang]):
                            assert dp["label"] == dc["label"] and dp["idx"] == dc["idx"]
                            answer = dc[f"choice{dc['label'] + 1}"]
                            examples.append(dp["premise"].strip()[:-1] + " " + CONNECTORS[premise_lang][dp["question"]] + " " + answer[0].lower() + answer[1:])
                        context = "\n\n".join(examples + [context])
                    unit = premise["question"]
                else:
                    # Joint likelihood matches the published harness NLI style. Cross-language
                    # cells change only hypothesis language, preserving premise/connector language.
                    context = ""
                    options = [premise["premise"] + conn + choice["hypothesis"] for conn in NLI[premise_lang]]
                    if shots:
                        examples = []
                        for dp, dc in zip(demos[premise_lang], demos[choice_lang]):
                            assert dp["label"] == dc["label"]
                            examples.append(dp["premise"] + NLI[premise_lang][dp["label"]] + dc["hypothesis"])
                        context = "\n\n".join(examples) + "\n\n"
                    if readout == "label":
                        # One pre-specified readout control: all outputs are the same short
                        # English labels, so target-language hypothesis likelihood cannot win.
                        labels = ["entailment", "neutral", "contradiction"]
                        def prompt(dp, dc):
                            return "Premise: " + dp["premise"] + "\nHypothesis: " + dc["hypothesis"] + "\nRelation:"
                        context = prompt(premise, choice)
                        if shots:
                            context = "\n\n".join([prompt(dp, dc) + " " + labels[dp["label"]] for dp, dc in zip(demos[premise_lang], demos[choice_lang])] + [context])
                        options = [" " + label for label in labels]
                    unit = str(premise["label"])
                items.append({"task": task, "id": index, "premise_lang": premise_lang, "choice_lang": choice_lang,
                              "slice": unit, "gold": premise["label"], "context": context, "options": options})
    return items, exclusions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--task", choices=list(DATA), required=True)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--shots", type=int, default=0)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--compute-dtype", choices=["bf16", "fp32"], default="bf16",
                        help="FP32 compute on the same BF16-rounded weights; numerical sensitivity control")
    parser.add_argument("--weight-dtype", choices=["bf16", "fp32"], default="bf16", help="Preserve native FP32 weights when explicitly selected")
    parser.add_argument("--languages", nargs=2, help="Override default language pair; dataset must contain aligned splits")
    parser.add_argument("--legacy-pickle", action="store_true", help="For pinned official JGP protocol-5 torch checkpoints")
    parser.add_argument("--readout", choices=["joint", "label"], default="joint")
    parser.add_argument("--context-control", choices=["original", "shuffled"], default="original")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    languages = args.languages or (["id", "zh"] if args.task in ["xcopa", "xstorycloze"] else ["en", "de"])
    items, exclusions = build_items(args.task, languages, args.limit, args.shots, args.readout)
    semantic_digest = hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if args.context_control == "shuffled":
        if args.task not in ["xcopa", "xstorycloze"] or args.shots:
            raise ValueError("Context shuffle is pre-specified for zero-shot XCOPA/XStoryCloze only")
        groups = {}
        for item in items:
            key = (item["premise_lang"], item["choice_lang"], item["slice"])
            groups.setdefault(key, []).append(item)
        for group in groups.values():
            contexts = [item["context"] for item in group]
            identifiers = [item["id"] for item in group]
            offset = len(group) // 2
            for index, item in enumerate(group):
                donor = (index + offset) % len(group)
                item["context"] = contexts[donor]
                item["context_donor_id"] = identifiers[donor]
    digest = hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite probe output: {path}")
    metadata = {"model": manifest, "args": vars(args), "data": DATA[args.task], "items_sha256": digest, "semantic_items_sha256": semantic_digest, "expected_items": len(items), "excluded_reannotated_ids": exclusions,
                "torch": torch.__version__, "transformers": transformers.__version__, "device": torch.cuda.get_device_name(0)}
    path.with_suffix(".meta.json").write_text(json.dumps(metadata, indent=2) + "\n")
    if args.legacy_pickle and not manifest["repo"].startswith("nusnlp/JGP-"):
        raise ValueError("Legacy loading is restricted to the audited official JGP family")
    scorer = Scorer(manifest["path"], args.batch, args.legacy_pickle, args.compute_dtype, args.weight_dtype)
    started = time.time()
    with path.open("w") as output:
        for start in range(0, len(items), 32):
            block = items[start:start + 32]
            requests = [(item["context"], option) for item in block for option in item["options"]]
            scores = scorer.score(requests)
            # Choice-only scores diagnose priors; for NLI only hypothesis is held fixed and
            # joint connector scoring is the primary readout (PMI is not interpreted).
            prior = scorer.score([("", option) for item in block for option in item["options"]]) if args.task in ["xcopa", "hellaswag", "xstorycloze"] else [None] * len(scores)
            cursor = 0
            for item in block:
                n = len(item["options"])
                row = {**item, "scores": scores[cursor:cursor + n], "prior_scores": prior[cursor:cursor + n]}
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
                cursor += n
            output.flush()
            print(f"{start + len(block)}/{len(items)} items, {time.time() - started:.1f}s", flush=True)
    print(f"COMPLETE {path}", flush=True)


if __name__ == "__main__":
    main()
