#!/usr/bin/env python3
"""E12 local adapter for upstream per-action tools and bounded tool-result retry.

Game, menu generation, argument-to-command conversion, parser and retry loop
are imported unchanged. Only normalized tool messages/model I/O are adapted.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from native_actioncastle import dump, run_episode, fresh_game, instrument
from strong_native_baseline import ModelClient, FreeClient

SENTENCE = ("Choose actions involving targets visible at your current location; "
            "a continuing guard duty can be maintained by waiting when nobody is intruding.")


def template_messages(messages):
    """Translate the upstream provider-neutral block messages losslessly."""
    out = []
    for message in messages:
        role, content = str(message["role"]), message["content"]
        if isinstance(content, str):
            out.append({"role": role, "content": content})
            continue
        if role == "assistant":
            prose = "\n".join(x["text"] for x in content if x["type"] == "text")
            calls = [{"id": x["id"], "type": "function", "function": {
                "name": x["name"], "arguments": x["arguments"]}}
                for x in content if x["type"] == "tool_use"]
            out.append({"role": "assistant", "content": prose, "tool_calls": calls})
        else:
            for block in content:
                if block["type"] == "tool_result":
                    out.append({"role": "tool", "tool_call_id": block["tool_use_id"],
                                "content": block["content"]})
                elif block["type"] == "text":
                    out.append({"role": role, "content": block["text"]})
                else:
                    raise ValueError(f"Unsupported native message {block['type']}")
    return out


class ToolClient(FreeClient):
    def __init__(self, base, sentence=False):
        super().__init__(base)
        self.sentence = sentence
        self.context = {}

    def call_tools(self, messages, tools, tool_choice="any", max_tokens=128, temperature=.7):
        from vllm import SamplingParams
        from vllm.sampling_params import StructuredOutputsParams
        from text_adventure_games.llm_client import ToolCallResult
        assert tool_choice == "any"
        # Original descriptions/parameter schemas are preserved. The outer
        # envelope is the local substitute for provider tool selection only.
        schema = {"oneOf": [{"type": "object", "properties": {
            "name": {"const": t["name"]}, "arguments": t["parameters"]},
            "required": ["name", "arguments"], "additionalProperties": False} for t in tools]}
        normalized = template_messages(messages)
        normalized[0]["content"] += (
            '\nCall exactly one offered action tool. Return a JSON object with "name" and '
            '"arguments". Use the tool description and schema; keep reasoning brief. Tools: '
            + json.dumps(tools, ensure_ascii=False))
        if self.sentence:
            normalized[0]["content"] += "\n" + SENTENCE
        prompt = self.base.tokenizer.apply_chat_template(normalized, tokenize=False,
                    add_generation_prompt=True, enable_thinking=False)
        start = time.monotonic()
        result = self.base.llm.generate([prompt], SamplingParams(
            max_tokens=max_tokens, temperature=temperature,
            seed=self.base.seed + len(self.base.calls),
            structured_outputs=StructuredOutputsParams(json=schema)), use_tqdm=False)[0]
        completion = result.outputs[0]
        try:
            parsed, error = json.loads(completion.text), None
        except Exception as exc:
            parsed, error = None, f"{type(exc).__name__}: {exc}"
        call_id = f"native_{len(self.base.calls)}"
        row = {"id": len(self.base.calls), "kind": "native_per_action_tools",
               "context": dict(self.context), "messages": copy.deepcopy(messages),
               "template_messages": normalized, "tools": tools, "schema": schema,
               "seed": self.base.seed + len(self.base.calls), "response": completion.text,
               "parsed": parsed, "parse_error": error, "finish_reason": completion.finish_reason,
               "prompt_tokens": len(result.prompt_token_ids),
               "completion_tokens": len(completion.token_ids),
               "wall_seconds": time.monotonic()-start,
               "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
        self.base.calls.append(row)
        with self.base.trace_file.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        if parsed is None:
            return ToolCallResult(text=completion.text, tool_calls=[])
        return ToolCallResult(text=None, tool_calls=[{"id": call_id,
            "name": parsed["name"], "arguments": parsed["arguments"]}])


def cpu_controls(out):
    from text_adventure_games.npc import LLMAgent, _decide_and_route_loop, build_npc_context, tools_for
    from text_adventure_games.llm_client import ToolCallResult
    checks = []
    for with_retry in [False, True]:
        class MockTools:
            def __init__(self):
                self.calls, self.context = [], {}
            def call_tools(self, messages, tools, **kwargs):
                self.calls.append(copy.deepcopy(messages))
                first = with_retry and len(self.calls) == 1
                name = "attack" if first else "wait"
                args = {"target": "definitely_missing_person", "weapon": "club"} if first else {}
                return ToolCallResult(text=None, tool_calls=[{"id": str(len(self.calls)),
                                       "name": name, "arguments": args}])
        game, client = fresh_game(), MockTools()
        troll = game.characters["troll"]
        agent = LLMAgent(client, persona=troll.persona)
        agent.action_names = ["attack", "wait"]
        records = instrument(game, out / f"cpu_{with_retry}_actions.jsonl")
        handled, acted = _decide_and_route_loop(troll, game, agent,
                                build_npc_context(troll, game), max_rounds=2)
        assert handled and acted
        assert len(client.calls) == 1 + int(with_retry)
        if with_retry:
            assert client.calls[1][-1]["content"][0]["is_error"]
            assert not records[0]["success"] and records[-1]["success"]
        checks.append({"retry": with_retry, "calls": len(client.calls),
                       "parser_successes": [r["success"] for r in records],
                       "tool_names": [t["name"] for t in tools_for(game.parser, troll, ["attack", "wait"])]})
    dump(out / "cpu_controls.json", {"all_passed": True, "checks": checks, "cloud_calls": 0})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("/home/xiang/.cache/game-npc-research/sources/agent-sandbox"))
    ap.add_argument("--model", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--mode", choices=["cpu", "model"], required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[101,102,103])
    args = ap.parse_args()
    sys.path.insert(0, str(args.source))
    assert subprocess.check_output(["git","-C",str(args.source),"rev-parse","HEAD"], text=True).strip() == "d7b872e396df2ef05ff8391de53e0563ca698cf3"
    args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1")
    dump(args.out / "manifest.json", {"model": str(args.model), "seeds": args.seeds,
        "source_sha": "d7b872e396df2ef05ff8391de53e0563ca698cf3", "cloud_calls": 0,
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sentence": SENTENCE, "tool_choice": "any", "output_budget": 128, "thinking": False})
    start = time.monotonic()
    if args.mode == "cpu":
        cpu_controls(args.out)
    else:
        model = ModelClient(args.model, 101, args.out/"unused.jsonl")
        rows = []
        for seed in args.seeds:
            for condition in ["native_tools", "native_tools_sentence"]:
                for episode in ["intruder", "feed"]:
                    folder = args.out / f"{condition}_{episode}_s{seed}"
                    folder.mkdir()
                    model.seed, model.calls, model.trace_file = seed, [], folder/"model_calls.jsonl"
                    client = ToolClient(model, sentence=condition.endswith("sentence"))
                    episode_start = time.monotonic()
                    row = run_episode(client, episode)
                    row.update(seed=seed, condition=condition, wall_seconds=time.monotonic()-episode_start,
                        prompt_tokens=sum(c["prompt_tokens"] for c in model.calls),
                        completion_tokens=sum(c["completion_tokens"] for c in model.calls))
                    dump(folder/"summary.json", row)
                    rows.append(row)
                    dump(args.out/"summary.json", rows)
                    print(json.dumps(row, ensure_ascii=False), flush=True)
    dump(args.out/"runtime.json", {"wall_seconds": time.monotonic()-start})


if __name__ == "__main__":
    main()
