#!/usr/bin/env python3
"""L15 E01/E02 runner.

Greedy decoding over every preregistered prompt cell, one model per invocation.
Writes raw generations plus a manifest; no scoring decision is made here.
"""
from __future__ import annotations

import argparse, json, os, pathlib, platform, re, time

ROOT = pathlib.Path(__file__).resolve().parents[1]

MODELS = {
    "qwen3_32b": {
        "path": "Qwen/Qwen3-32B",
        "chat_template_kwargs": {"enable_thinking": False},
    },
    "mistral_small_24b": {
        "path": "mistralai/Mistral-Small-24B-Instruct-2501",
        "chat_template_kwargs": {},
    },
    "gemma3_12b_it": {
        "path": "google/gemma-3-12b-it",
        "chat_template_kwargs": {},
    },
}

MAX_TOKENS = {"direct": 24, "cot": 1024}


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--cells", type=pathlib.Path, default=ROOT / "data" / "cells.jsonl")
    ap.add_argument("--tag", default="pilot_v1")
    ap.add_argument("--gpu-util", type=float, default=0.88)
    ap.add_argument("--max-model-len", type=int, default=2560)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: first N cells")
    return ap.parse_args()


def main():
    args = parse_args()
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("VLLM_LOGGING_LEVEL", "WARNING")

    import torch
    import vllm
    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer

    spec = MODELS[args.model]
    cells = [json.loads(l) for l in args.cells.read_text().splitlines() if l.strip()]
    if args.limit:
        cells = cells[: args.limit]

    tok = AutoTokenizer.from_pretrained(spec["path"])
    prompts = []
    for c in cells:
        text = tok.apply_chat_template(
            [{"role": "user", "content": c["prompt"]}],
            tokenize=False,
            add_generation_prompt=True,
            **spec["chat_template_kwargs"],
        )
        prompts.append(text)

    llm = LLM(
        model=spec["path"],
        dtype="bfloat16",
        gpu_memory_utilization=args.gpu_util,
        max_model_len=args.max_model_len,
        enforce_eager=False,
        seed=0,
    )

    out_dir = ROOT / "results" / args.tag / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    records = []
    for mode in ("direct", "cot"):
        idx = [i for i, c in enumerate(cells) if c["mode"] == mode]
        if not idx:
            continue
        sp = SamplingParams(
            temperature=0.0, top_p=1.0, max_tokens=MAX_TOKENS[mode], seed=0,
            stop=None,
        )
        outs = llm.generate([prompts[i] for i in idx], sp)
        for i, o in zip(idx, outs):
            c = dict(cells[i])
            c["raw"] = o.outputs[0].text
            c["finish_reason"] = o.outputs[0].finish_reason
            c["n_gen_tokens"] = len(o.outputs[0].token_ids)
            records.append(c)
    wall = time.time() - t0

    with (out_dir / "raw.jsonl").open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    manifest = {
        "model_slug": args.model,
        "model_path": spec["path"],
        "chat_template_kwargs": spec["chat_template_kwargs"],
        "n_cells": len(records),
        "decoding": {"temperature": 0.0, "top_p": 1.0, "seed": 0, "max_tokens": MAX_TOKENS},
        "cells_file": str(args.cells),
        "vllm": vllm.__version__,
        "torch": torch.__version__,
        "python": platform.python_version(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "wall_clock_s": round(wall, 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
