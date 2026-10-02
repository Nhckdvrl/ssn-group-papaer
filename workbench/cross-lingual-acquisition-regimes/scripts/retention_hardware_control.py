"""E08: original full LMs, using exactly the E06 generation protocol."""
import argparse
import gc
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
    post = json.loads((ROOT / "artifacts/qa_retention" / f"{condition}_seed17/completion.json").read_text())
    before_path = ROOT / "artifacts/p2" / f"translation_{condition}_34k.jsonl"
    assert hashlib.sha256(before_path.read_bytes()).hexdigest() == post["before_sha256"]
    before = [json.loads(line) for line in before_path.read_text().splitlines()]
    items = [{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in before]
    assert tc.digest(items) == post["items_sha256"]
    manifest = json.loads((ROOT / "artifacts/model_manifests" / f"UCLNLP__monoweb__ckpt_exp_en_de_{condition}.json").read_text())
    out = ROOT / "artifacts/retention_hardware_control" / condition
    out.mkdir(parents=True, exist_ok=False)
    scorer = Scorer(manifest["path"], 8, compute_dtype="fp32", weight_dtype="fp32")
    tok, model = scorer.tokenizer, scorer.model
    assert torch.cuda.get_device_name() == post["device"]
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
    record = dict(condition=condition, model=manifest,items_sha256=tc.digest(items),device=torch.cuda.get_device_name(),
        before_sha256=post["before_sha256"],script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        protocol_reference_sha256=post["script_sha256"],torch=torch.__version__,elapsed_seconds=time.time()-start,
        weight_dtype="fp32",compute_dtype="fp32",use_cache=True,max_new_tokens=256)
    nli.dump(out / "completion.json",record)
    del model,scorer,encoded,generated
    gc.collect()
    torch.cuda.empty_cache()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition",choices=("baseline","monoweb","onlyparallel","all"),default="all")
    args = parser.parse_args()
    for condition in (("baseline","monoweb","onlyparallel") if args.condition == "all" else (args.condition,)):
        run(condition)
