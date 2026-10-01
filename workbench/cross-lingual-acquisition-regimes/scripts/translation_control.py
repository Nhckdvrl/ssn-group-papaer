"""Pinned five-shot WMT16 diagnostic for the existing MONOWEB intervention."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REVISION = "41d8a4013aa1489f28fea60ec0932af246086482"
HARNESS = "d6de81643928d653435c431bae19945d41d32520"
DATA = ROOT / "artifacts/wmt16_control.json"
LANGUAGES = {"en": "English", "de": "German"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def prepare():
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    if DATA.exists():
        raise FileExistsError(DATA)
    splits = {}
    paths = {}
    for split in ["test", "validation"]:
        path = hf_hub_download("wmt/wmt16", f"de-en/{split}-00000-of-00001.parquet", repo_type="dataset", revision=REVISION)
        splits[split] = pq.read_table(path).to_pylist()
        paths[split] = {"path": path, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
    demonstration_ids = random.Random(1234).sample(range(len(splits["validation"])), 5)
    examples = [splits["validation"][i]["translation"] for i in demonstration_ids]
    items = []
    excluded = []
    for index, doc in enumerate(splits["test"][:200]):
        text = doc["translation"]
        if any(text[lang] == example[lang] for example in examples for lang in LANGUAGES):
            excluded.append(index)
            continue
        for source, target in [("en", "de"), ("de", "en")]:
            def prompt(translation):
                return f"{LANGUAGES[source]} phrase: {translation[source]}\n{LANGUAGES[target]} phrase:"
            context = "\n\n".join([prompt(example)+" "+example[target] for example in examples] + [prompt(text)])
            items.append({"id": index, "direction": source+"->"+target, "source": text[source], "reference": text[target], "prompt": context})
    configs = {}
    folder = ROOT / "artifacts/harness_translation"
    folder.mkdir(exist_ok=True)
    for filename in ["wmt16_en-de.yaml", "wmt16_de-en.yaml", "wmt_common_yaml", "utils.py"]:
        url = f"https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/{HARNESS}/lm_eval/tasks/translation/{filename}"
        payload = urllib.request.urlopen(url, timeout=30).read()
        (folder / filename).write_bytes(payload)
        configs[filename] = {"url": url, "sha256": hashlib.sha256(payload).hexdigest()}
    record = {"revision": REVISION, "files": paths, "harness_revision": HARNESS, "configs": configs,
              "demonstration_ids": demonstration_ids, "demonstrations": examples,
              "excluded_demonstration_overlap": excluded, "items": items, "items_sha256": digest(items)}
    DATA.write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps({"prepared": str(DATA), "rows": len(items), "demonstration_ids": demonstration_ids}), flush=True)


def run(condition):
    import torch
    from frozen_probe import Scorer
    corpus = json.loads(DATA.read_text())
    assert digest(corpus["items"]) == corpus["items_sha256"]
    path = ROOT / "artifacts/model_manifests" / f"UCLNLP__monoweb__ckpt_exp_en_de_{condition}.json"
    manifest = json.loads(path.read_text())
    output = ROOT / "artifacts/p2" / f"translation_{condition}_34k.jsonl"
    if output.exists():
        raise FileExistsError(output)
    scorer = Scorer(manifest["path"], 8, compute_dtype="fp32", weight_dtype="fp32")
    tokenizer = scorer.tokenizer
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    items, excluded = [], []
    maximum = scorer.model.config.max_position_embeddings
    by_id = {}
    for item in corpus["items"]:
        by_id.setdefault(item["id"], []).append(item)
    for index, pair in by_id.items():
        if any(len(tokenizer.encode(r["prompt"], add_special_tokens=False))+256 > maximum for r in pair):
            excluded.append(index)
        else:
            items.extend(pair)
    start = time.time()
    with output.open("w") as target:
        with torch.inference_mode():
            for offset in range(0, len(items), 8):
                block = items[offset:offset+8]
                encoded = tokenizer([r["prompt"] for r in block], padding=True, add_special_tokens=False, return_tensors="pt").to("cuda")
                assert encoded.input_ids.shape[1]+256 <= maximum
                generated = scorer.model.generate(**encoded, do_sample=False, max_new_tokens=256,
                    eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.pad_token_id,
                    stop_strings=["\n"], tokenizer=tokenizer)
                for row, token_ids in zip(block, generated[:, encoded.input_ids.shape[1]:].tolist()):
                    if tokenizer.eos_token_id in token_ids:
                        token_ids = token_ids[:token_ids.index(tokenizer.eos_token_id)]
                    raw = tokenizer.decode(token_ids, skip_special_tokens=True)
                    prediction = raw.split("\n", 1)[0].strip()
                    result = {**row, "generated_raw": raw, "prediction": prediction, "token_ids": token_ids,
                              "token_cap_reached": len(token_ids) >= 256 and "\n" not in raw,
                              "source_copied": prediction == row["source"].strip()}
                    target.write(json.dumps(result, ensure_ascii=False)+"\n")
                target.flush()
                print(f"{condition}: {min(offset+8,len(items))}/{len(items)}, {time.time()-start:.1f}s", flush=True)
    metadata = {"model": manifest, "items_sha256": digest(items), "corpus_items_sha256": corpus["items_sha256"],
                "data_revision": REVISION, "harness_revision": HARNESS, "expected_items": len(items),
                "excluded_context_overflow": excluded, "demonstration_ids": corpus["demonstration_ids"],
                "weight_dtype": "fp32", "compute_dtype": "fp32", "max_new_tokens": 256,
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "elapsed_seconds": time.time()-start}
    output.with_suffix(".meta.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(f"COMPLETE {output}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--condition", choices=["baseline", "monoweb", "onlyparallel"])
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.condition:
        run(args.condition)
    else:
        parser.error("Choose --prepare or --condition")


if __name__ == "__main__":
    main()
