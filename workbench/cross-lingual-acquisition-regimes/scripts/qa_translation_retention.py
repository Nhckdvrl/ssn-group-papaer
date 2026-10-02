"""Translation after actual LM adaptation, with fixed instruction recovery."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import nli_learning as nli
import translation_control as tc

ROOT = Path(__file__).resolve().parents[1]


def run(condition):
    import torch
    from frozen_probe import Scorer
    folder = ROOT / "artifacts/qa_learning" / f"train_{condition}_seed17"
    done = json.loads((folder / "completion.json").read_text())
    provenance = json.loads((folder / "provenance.json").read_text())
    assert done["script_sha256"] == provenance["script_sha256"] == hashlib.sha256((ROOT / "scripts/qa_learning.py").read_bytes()).hexdigest()
    assert done["data_hashes"] == provenance["metadata"]["hashes"]
    corpus = json.loads(tc.DATA.read_text())
    assert tc.digest(corpus["items"]) == corpus["items_sha256"]
    before_path = ROOT / "artifacts/p2" / f"translation_{condition}_34k.jsonl"
    before = [json.loads(line) for line in before_path.read_text().splitlines()]
    meta = json.loads(before_path.with_suffix(".meta.json").read_text())
    assert len(before) == meta["expected_items"]
    items = [{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in before]
    assert tc.digest(items) == meta["items_sha256"]
    assert meta["weight_dtype"] == meta["compute_dtype"] == "fp32"
    out = ROOT / "artifacts/qa_retention" / f"{condition}_seed17"
    out.mkdir(parents=True, exist_ok=False)
    scorer = Scorer(str(folder / "checkpoint"), 8, compute_dtype="fp32", weight_dtype="fp32")
    tok, model = scorer.tokenizer, scorer.model
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    start = time.time()
    for mode in ("primary", "instruction"):
        with (out / f"{mode}.jsonl").open("w") as target, torch.inference_mode():
            for offset in range(0, len(items), 8):
                block, outputs = [], {}
                for row in items[offset:offset+8]:
                    instruction = ""
                    if mode == "instruction":
                        language = tc.LANGUAGES[row["direction"].split("->")[1]]
                        instruction = f"Translate the final phrase into {language}. Output only the translation.\n"
                    full_prompt = instruction+row["prompt"]
                    if len(tok.encode(full_prompt, add_special_tokens=False))+256 > model.config.max_position_embeddings:
                        outputs[row["id"],row["direction"]] = dict(**row, generated_raw="", prediction="", token_ids=[],
                            token_cap_reached=False, source_copied=False, overflow=True)
                    else:
                        block.append((row, full_prompt))
                if block:
                    encoded = tok([p for _,p in block], padding=True, add_special_tokens=False, return_tensors="pt").to("cuda")
                    generated = model.generate(**encoded, do_sample=False, max_new_tokens=256, use_cache=True,
                        eos_token_id=tok.eos_token_id, pad_token_id=tok.pad_token_id,
                        stop_strings=["\n"], tokenizer=tok)
                    for (row,_), ids in zip(block, generated[:,encoded.input_ids.shape[1]:].tolist()):
                        if tok.eos_token_id in ids:
                            ids = ids[:ids.index(tok.eos_token_id)]
                        raw = tok.decode(ids, skip_special_tokens=True)
                        prediction = raw.split("\n",1)[0].strip()
                        outputs[row["id"],row["direction"]] = dict(**row, generated_raw=raw, prediction=prediction, token_ids=ids,
                            token_cap_reached=len(ids)>=256 and "\n" not in raw,
                            source_copied=prediction==row["source"].strip(), overflow=False)
                for row in items[offset:offset+8]:
                    target.write(json.dumps(outputs[row["id"],row["direction"]], ensure_ascii=False)+"\n")
                target.flush()
                print(condition, mode, min(offset+8,len(items)), len(items), round(time.time()-start,1), flush=True)
    nli.dump(out / "completion.json", dict(condition=condition, seed=17, model_path=str(folder / "checkpoint"),
        qa_provenance=provenance, before_sha256=hashlib.sha256(before_path.read_bytes()).hexdigest(),
        before_metadata=meta, items_sha256=tc.digest(items), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        device=torch.cuda.get_device_name(), elapsed_seconds=time.time()-start,
        weight_dtype="fp32", compute_dtype="fp32", max_new_tokens=256, use_cache=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", required=True, choices=("baseline","monoweb","onlyparallel"))
    run(parser.parse_args().condition)
