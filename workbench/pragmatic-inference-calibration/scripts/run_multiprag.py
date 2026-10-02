#!/usr/bin/env python3
"""Native MultiPragEval questions, sampling T=.5; no added instruction."""
import argparse
import hashlib
import importlib.metadata
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from scoring import parse_choice, summarize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--revision", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--languages", nargs="+", default=["english", "german", "korean", "chinese"])
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--format-only", action="store_true", help="E06: append a response-format instruction")
    args = ap.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refuse to overwrite a run: {args.output}")
    args.output.mkdir(parents=True)
    start = time.monotonic()
    rows = [json.loads(s) for s in args.data.read_text().splitlines()]
    rows = [r for r in rows if r["language"] in args.languages]
    if args.limit is not None:
        rows = rows[:args.limit]
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True, padding_side="left")
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
        torch_dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa").eval()
    instruction = "\n\nReturn only the letter (A, B, C, D, or E) of the selected option." if args.format_only else ""
    texts = [tokenizer.apply_chat_template([{"role": "user", "content": r["prompt"] + instruction}],
             tokenize=False, add_generation_prompt=True, enable_thinking=False) for r in rows]
    metadata = {"model_id": args.model_id, "revision": args.revision, "model_path": str(args.model),
        "data_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "tokenizer_sha256": hashlib.sha256((args.model / "tokenizer_config.json").read_bytes()).hexdigest(),
        "prompt_sha256": hashlib.sha256(json.dumps(texts, ensure_ascii=False).encode()).hexdigest(),
        "generation": {"temperature": .5, "do_sample": True, "top_p": 1., "top_k": 0,
                       "max_new_tokens": args.max_new_tokens},
        "model_generation_defaults": model.generation_config.to_dict(),
        "seeds": args.seeds, "batch_size": args.batch_size, "n_per_seed": len(rows),
        "format_only_instruction": instruction,
        "enable_thinking": False,
        "gpu": torch.cuda.get_device_name(),
        "packages": {k: importlib.metadata.version(k) for k in ["torch", "transformers", "accelerate"]},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scorer_sha256": hashlib.sha256(Path(__file__).with_name("scoring.py").read_bytes()).hexdigest(),
        "limitations": ["Parent did not release inference code, top_p/top_k/max_tokens or system prompt; these choices are explicit local reconstruction",
                        "Wilson CI describes item accuracy for each seed, not independence of translations or repeated seeds"]}
    (args.output / "config.json").write_text(json.dumps(metadata, indent=2) + "\n")
    summaries = {}
    for seed in args.seeds:
        set_seed(seed)
        outputs = []
        with (args.output / f"seed{seed}.jsonl").open("w") as f:
            for i in range(0, len(rows), args.batch_size):
                rs = rows[i:i+args.batch_size]
                inp = tokenizer(texts[i:i+args.batch_size], return_tensors="pt", padding=True,
                                add_special_tokens=False).to(model.device)
                with torch.inference_mode():
                    generated = model.generate(**inp, do_sample=True, temperature=.5, top_p=1., top_k=0,
                        max_new_tokens=args.max_new_tokens, pad_token_id=tokenizer.pad_token_id)
                new = generated[:, inp.input_ids.shape[1]:]
                for r, tokens in zip(rs, new):
                    response = tokenizer.decode(tokens, skip_special_tokens=True)
                    eos = model.generation_config.eos_token_id
                    eos = [eos] if isinstance(eos, int) else (eos or [])
                    truncated = len(tokens) >= args.max_new_tokens and not any(int(t) in eos for t in tokens)
                    rec = {**r, "model": args.model_id, "revision": args.revision, "seed": seed,
                           "response": response, "prediction": parse_choice(response, r["choices"]),
                           "truncated": truncated, "prompt_sha256": hashlib.sha256(r["prompt"].encode()).hexdigest()}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    outputs.append(rec)
                f.flush()
                if i % (args.batch_size * 5) == 0:
                    print(json.dumps({"seed": seed, "done": len(outputs), "total": len(rows),
                                      "seconds": round(time.monotonic()-start, 1)}), flush=True)
        summaries[str(seed)] = summarize(outputs)
        (args.output / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    metadata.update({"wall_seconds": time.monotonic()-start,
                     "peak_gpu_memory_bytes": torch.cuda.max_memory_allocated()})
    (args.output / "config.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"complete": True, "output": str(args.output), "wall_seconds": metadata["wall_seconds"]}))


if __name__ == "__main__":
    main()
