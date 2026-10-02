"""Fixed E06/E08 translation generation for additional actual learning runs."""
import ast
import gc
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time

import translation_control as tc

ROOT = Path(__file__).resolve().parents[1]


def generate(scorer,items,out,condition):
    import torch
    tok,model = scorer.tokenizer,scorer.model
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
    return time.time()-start


def assert_protocol():
    def loop(path):
        nodes = [node for node in ast.walk(ast.parse(path.read_text())) if isinstance(node,ast.For)
                 and isinstance(node.target,ast.Name) and node.target.id == "mode"]
        assert len(nodes) == 1
        return ast.dump(nodes[0],include_attributes=False)
    reference = ROOT / "scripts/qa_translation_retention.py"
    assert loop(Path(__file__)) == loop(reference)
    return hashlib.sha256(reference.read_bytes()).hexdigest()


def evaluate_checkpoint(path,items,out,condition,expected_device):
    import torch
    from frozen_probe import Scorer
    reference_hash = assert_protocol()
    out.mkdir(parents=True,exist_ok=False)
    stage = Path(tempfile.mkdtemp(prefix="C_retention_",dir="/var/tmp"))
    started = time.time()
    hashes = {}
    # Sequential local copies avoid NFS demand paging during tensor-to-GPU transfer.
    for source in sorted(Path(path).iterdir()):
        if not source.is_file():
            continue
        target = stage / source.name
        shutil.copyfile(source,target)
        with source.open("rb") as stream:
            original_hash = hashlib.file_digest(stream,"sha256").hexdigest()
        with target.open("rb") as stream:
            copied_hash = hashlib.file_digest(stream,"sha256").hexdigest()
        assert original_hash == copied_hash
        hashes[source.name] = original_hash
    assert "model.safetensors" in hashes and "config.json" in hashes
    stage_seconds = time.time()-started
    load_started = time.time()
    scorer = Scorer(str(stage),8,compute_dtype="fp32",weight_dtype="fp32")
    assert torch.cuda.get_device_name() == expected_device
    load_seconds = time.time()-load_started
    generation_seconds = generate(scorer,items,out,condition)
    del scorer
    gc.collect()
    torch.cuda.empty_cache()
    shutil.rmtree(stage)
    return dict(model_source_path=str(path),loaded_file_sha256=hashes,staging_seconds=stage_seconds,
        load_seconds=load_seconds,generation_seconds=generation_seconds,device=expected_device,torch=torch.__version__,
        protocol_reference_sha256=reference_hash,protocol_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        weight_dtype="fp32",compute_dtype="fp32",use_cache=True,max_new_tokens=256,items_sha256=tc.digest(items))
