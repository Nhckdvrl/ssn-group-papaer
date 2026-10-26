"""Frozen text-preserving retokenization for the two E150 mature endpoints."""
import hashlib
import json
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
import e144145_common as old

WB = Path(__file__).resolve().parents[1]
RESULT = WB / "results/e150"
RAW = Path.home() / "mechpop_cache/e150_native_protocol_cube"
sha, read, write = old.sha, old.read, old.write


def masked_mean(values, mask):
    values, mask = np.asarray(values), np.asarray(mask, dtype=bool)
    if values.shape[:mask.ndim] != mask.shape or np.any(mask.sum(-1) == 0):
        raise ValueError("Expected at least one target in every sequence")
    expanded = mask[(...,)+(None,)*(values.ndim-mask.ndim)]
    return np.where(expanded, values, 0).sum(1)/mask.sum(1).reshape((-1,)+(1,)*(values.ndim-mask.ndim))


def tokenize_texts(tokenizer, texts):
    ids = np.full((len(texts), 513), tokenizer.pad_token_id, np.uint32)
    lengths = []
    for i, text in enumerate(texts):
        tokens = tokenizer.encode(text, add_special_tokens=False)[:513]
        if len(tokens) < 2 or max(tokens) >= 100352: raise ValueError("Invalid E150 text/token IDs")
        ids[i, :len(tokens)] = tokens; lengths.append(len(tokens))
    lengths = np.array(lengths, np.int32)
    mask = np.arange(512)[None, :] < lengths[:, None]-1
    return ids, mask, lengths


def prepare():
    metadata = read(RESULT / "metadata.json")
    roots = [Path(v["path"]) for v in metadata["models"].values()]
    for key in ("config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"):
        if sha(roots[0]/key) != sha(roots[1]/key): raise ValueError("Mature pair tokenizer/config differs")
    source = read(WB / "results/e148/plan.json")
    if sha(source["plan_path"]) != source["plan_sha256"]: raise ValueError("E148 source input changed")
    original = AutoTokenizer.from_pretrained("/tmp/xiang-moe-20261026/e148/model", local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(roots[0], local_files_only=True, trust_remote_code=False)
    arrays, rows = {}, {}
    RAW.mkdir(exist_ok=True, parents=True)
    text_path = RAW / "text_windows.jsonl"
    text_rows = []
    with np.load(source["plan_path"]) as prior:
        for split in ("held", "cal"):
            texts = [original.decode(row.tolist(), skip_special_tokens=False, clean_up_tokenization_spaces=False)
                     .replace(original.eos_token, "\n\n") for row in prior[split]]
            ids, mask, lengths = tokenize_texts(tokenizer, texts)
            arrays.update({split: ids, split+"_mask": mask})
            rows[split] = []
            for i, (text, length) in enumerate(zip(texts, lengths)):
                text_rows.append(json.dumps({"split": split, "index": i, "text": text}, ensure_ascii=False))
                rows[split].append({"index": i, "input_tokens": int(length), "target_tokens": int(length)-1,
                    "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "token_sha256_u32le": hashlib.sha256(ids[i, :length].astype("<u4").tobytes()).hexdigest()})
    payload = "\n".join(text_rows)+"\n"
    if text_path.exists() and text_path.read_text() != payload: raise ValueError("Refusing to replace input text")
    if not text_path.exists(): text_path.write_text(payload)
    path = RAW / "plan.npz"
    if path.exists():
        with np.load(path) as previous:
            if set(previous.files) != set(arrays) or any(not np.array_equal(previous[k], v) for k, v in arrays.items()):
                raise ValueError("Refusing to replace frozen E150 inputs")
    else: np.savez(path, **arrays)
    selected = [{**s, "tokens": rows["held"][i]["target_tokens"]} for i, s in enumerate(source["selected"])]
    result = {"experiment": "E150", "status": "prepared", "data_source_sha256": sha(__file__),
        "source_E148_plan_sha256": source["plan_sha256"], "path": str(path), "sha256": sha(path),
        "text_path": str(text_path), "text_sha256": sha(text_path), "rows": rows, "selected": selected,
        "tokenizer_sha256": sha(roots[0]/"tokenizer.json"), "input_dtype": "uint32", "target_mask": "position < input_length - 1",
        "sequence_weighting": "Mean over real targets within sequence; equal sequences, paired file-cluster bootstrap",
        "scope": "Previously explored language windows, decoded with original tokenizer/EOS -> two newlines, retokenized without added specials; not guaranteed whole documents. Absolute NLL is not compared across tokenizers."}
    old.immutable_json(RESULT / "plan.json", result)
    return {"status": "prepared", "held_target_tokens": int(arrays["held_mask"].sum()),
            "held_sequences": len(arrays["held"]), "input_file_clusters": len({(v["source"],v["file_id"]) for v in selected})}


if __name__ == "__main__": print(json.dumps(prepare(), indent=2))
