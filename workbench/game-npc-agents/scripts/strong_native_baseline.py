#!/usr/bin/env python3
"""E10 native choose_action schema and modern local model; no new game rules."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time

from native_actioncastle import LocalClient, dump, run_episode
from viewpoint_control import SENTENCE


class ModelClient(LocalClient):
    def __init__(self, model, seed, trace_file):
        from vllm import LLM
        self.llm = LLM(model=str(model), tensor_parallel_size=1, dtype="bfloat16",
                       gpu_memory_utilization=0.82, max_model_len=8192,
                       enforce_eager=True, enable_prefix_caching=True, seed=seed,
                       language_model_only=True)
        self.tokenizer = self.llm.get_tokenizer()
        self.seed, self.calls, self.trace_file = seed, [], Path(trace_file)

    def native_tool(self, messages, tool, max_tokens=128, temperature=0.7, viewer=False):
        from vllm import SamplingParams
        from vllm.sampling_params import StructuredOutputsParams
        messages = [{"role": str(m["role"]), "content": m["content"]} for m in messages]
        schema = tool["parameters"]
        # The source's tool shape is unchanged; constrained arguments are decoded
        # locally rather than obtained from a hosted SDK. All calls return to parser.
        messages[0]["content"] += (
            "\nChoose one game action using the choose_action tool. Return only its JSON arguments; "
            "reasoning must be one short sentence. Schema: " + json.dumps(schema))
        if viewer:
            messages[0]["content"] += "\n" + SENTENCE
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False,
                    add_generation_prompt=True, enable_thinking=False)
        start = time.monotonic()
        result = self.llm.generate([prompt], SamplingParams(
            max_tokens=max_tokens, temperature=temperature, seed=self.seed + len(self.calls),
            structured_outputs=StructuredOutputsParams(json=schema)), use_tqdm=False)[0]
        completion = result.outputs[0]
        try:
            parsed = json.loads(completion.text)
            parse_error = None
        except Exception as exc:
            parsed, parse_error = None, f"{type(exc).__name__}: {exc}"
        row = {"kind": "native_choose_action", "id": len(self.calls),
               "seed": self.seed + len(self.calls), "messages": messages, "schema": schema,
               "response": completion.text, "parsed": parsed, "parse_error": parse_error,
               "finish_reason": completion.finish_reason,
               "prompt_tokens": len(result.prompt_token_ids),
               "completion_tokens": len(completion.token_ids),
               "wall_seconds": time.monotonic() - start,
               "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
        self.calls.append(row)
        with self.trace_file.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return parsed


class FreeClient:
    def __init__(self, base):
        self.base = base

    @property
    def calls(self):
        return self.base.calls

    @property
    def trace_file(self):
        return self.base.trace_file

    def chat(self, messages, max_tokens=128, temperature=0.7):
        return self.base.chat(messages, max_tokens=max_tokens, temperature=temperature)


class SchemaClient(FreeClient):
    def __init__(self, base, viewer=False):
        super().__init__(base)
        self.viewer = viewer

    def call_tool(self, messages, tool, max_tokens=128, temperature=0.7):
        return self.base.native_tool(messages, tool, max_tokens, temperature, self.viewer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("/home/xiang/.cache/game-npc-research/sources/agent-sandbox"))
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[101, 102, 103])
    ap.add_argument("--conditions", nargs="+", default=["freetext", "native_schema", "native_schema_viewer"])
    ap.add_argument("--episodes", nargs="+", default=["intruder", "feed"])
    args = ap.parse_args()
    sys.path.insert(0, str(args.source))
    args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1")
    manifest = {"model": str(args.model), "seeds": args.seeds, "conditions": args.conditions,
                "episodes": args.episodes, "backend": "vllm / local JSON argument constraint",
                "enable_thinking": False, "language_model_only": True, "cloud_calls": 0,
                "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "native_harness_sha256": hashlib.sha256(Path(__file__).with_name("native_actioncastle.py").read_bytes()).hexdigest(),
                "model_config_sha256": hashlib.sha256((args.model / "config.json").read_bytes()).hexdigest(),
                "tokenizer_config_sha256": hashlib.sha256((args.model / "tokenizer_config.json").read_bytes()).hexdigest(),
                "dependencies": {m: importlib.metadata.version(m) for m in ["torch", "transformers", "vllm", "prompty"]}}
    dump(args.out / "manifest.json", manifest)
    start = time.monotonic()
    client = ModelClient(args.model, 101, args.out / "unused_calls.jsonl")
    results = []
    # Start with the first full episode in each interface, then extend seeds.
    for seed in args.seeds:
        for condition in args.conditions:
            for episode in args.episodes:
                folder = args.out / f"{condition}_{episode}_s{seed}"
                folder.mkdir(exist_ok=False)
                client.seed, client.calls, client.trace_file = seed, [], folder / "model_calls.jsonl"
                wrapper = (FreeClient(client) if condition == "freetext" else
                           SchemaClient(client, viewer=condition == "native_schema_viewer"))
                episode_start = time.monotonic()
                result = run_episode(wrapper, episode)
                result.update(seed=seed, condition=condition, wall_seconds=time.monotonic() - episode_start,
                              prompt_tokens=sum(r["prompt_tokens"] for r in client.calls),
                              completion_tokens=sum(r["completion_tokens"] for r in client.calls))
                dump(folder / "summary.json", result)
                results.append(result)
                dump(args.out / "summary.json", results)
                print(json.dumps(result, ensure_ascii=False), flush=True)
    dump(args.out / "runtime.json", {"wall_seconds": time.monotonic() - start})


if __name__ == "__main__":
    main()
