#!/usr/bin/env python3
"""E07: pinned native engine controls and local-only, fully recorded NPC episodes.

Source code, model weights and large traces stay outside Git. No hosted clients.
The wrapper records parser calls; it does not change action rules or rewards.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

SOURCE_SHA = "d7b872e396df2ef05ff8391de53e0563ca698cf3"
DEFAULT_CACHE = Path("/home/xiang/.cache/game-npc-research")
NPC_GOALS = {
    "troll": "Keep intruders from crossing the drawbridge",
    "guard": "Stop strangers from entering the castle",
    "ghost": "Drive the living out of the dungeon",
}
PLAYER_SCRIPTS = {
    "intruder": ["go out", "go north", "go east", "wait", "go east", "wait"],
    "feed": ["get pole", "go out", "go south", "catch fish with pole", "go north",
             "go north", "go east", "give fish to troll", "go east", "wait"],
}


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def core_state(game):
    from text_adventure_games.world_state import world_state
    s = world_state(game).to_jsonable()
    return {k: s[k] for k in ("locations", "characters")}


def state_diff(a, b, prefix=""):
    if type(a) is not type(b):
        return [{"path": prefix, "before": a, "after": b}]
    if isinstance(a, dict):
        out = []
        for k in sorted(a.keys() | b.keys()):
            out.extend(state_diff(a.get(k), b.get(k), f"{prefix}/{k}"))
        return out
    if isinstance(a, (list, tuple)):
        # Records have stable names; resolve by name rather than array position.
        if all(isinstance(x, dict) and "name" in x for x in a + b):
            return state_diff({x["name"]: x for x in a}, {x["name"]: x for x in b}, prefix)
        return [] if a == b else [{"path": prefix, "before": a, "after": b}]
    return [] if a == b else [{"path": prefix, "before": a, "after": b}]


def fresh_game():
    from text_adventure_games.adventures.action_castle import build_game
    from text_adventure_games.webapp.web_parser import WebParser
    g = build_game()
    g.set_parser(WebParser(g))
    return g


def prepare(g, commands):
    """CPU control fixture through legal player actions, without NPC round ticks."""
    for command in commands:
        if not g.parser.parse_command(command, actor=g.player):
            raise RuntimeError(f"Control preparation failed: {command}: {g.parser.last_fail_message}")


def cpu_controls():
    cases = []
    for repetition in range(2):
        g = fresh_game()
        prepare(g, ["go out", "go north", "go east"])
        troll = g.characters["troll"]
        for name, command, expected, material in [
            ("expressive_growl", "growl The player", True, False),
            ("unowned_weapon", "attack The player with sword", False, False),
            ("club_attack", "attack The player with club", True, True),
        ]:
            before = core_state(g)
            ok = bool(g.parser.parse_command(command, actor=troll))
            after = core_state(g)
            delta = state_diff(before, after)
            assert ok == expected, (name, ok, g.parser.last_fail_message)
            # The world snapshot's visited flags do not change for these controls.
            assert bool(delta) == material, (name, delta)
            if name == "club_attack":
                assert g.player.get_property("is_unconscious")
            cases.append({"repetition": repetition, "name": name, "command": command,
                          "success": ok, "delta": delta})
        g = fresh_game()
        prepare(g, ["get pole", "go out", "go south", "catch fish with pole", "go north",
                    "go north", "go east"])
        before = core_state(g)
        assert g.parser.parse_command("give fish to troll", actor=g.player)
        after = core_state(g)
        assert not g.characters["troll"].get_property("is_hungry")
        assert not g.characters["troll"].location.blocks["east"].is_blocked()
        cases.append({"repetition": repetition, "name": "native_feed_unblocks",
                      "command": "give fish to troll", "success": True,
                      "delta": state_diff(before, after)})
    a = [{k: v for k, v in r.items() if k != "repetition"} for r in cases[:4]]
    b = [{k: v for k, v in r.items() if k != "repetition"} for r in cases[4:]]
    assert a == b
    return {"checks": len(cases), "all_passed": True, "deterministic_replay": True,
            "model_calls": 0, "gpu_hours": 0, "cases": cases}


class LocalClient:
    """vLLM in-process client. No SDK or network fallback exists."""
    def __init__(self, model, seed, trace_file):
        from vllm import LLM
        self.llm = LLM(model=str(model), tensor_parallel_size=1, dtype="bfloat16",
                       gpu_memory_utilization=0.82, max_model_len=8192,
                       enforce_eager=True, enable_prefix_caching=True, seed=seed,
                       language_model_only=True)
        self.tokenizer = self.llm.get_tokenizer()
        self.seed = seed
        self.calls = []
        self.trace_file = Path(trace_file)

    def chat(self, messages, max_tokens=128, temperature=0.7, kind="action"):
        from vllm import SamplingParams
        prompt = self.tokenizer.apply_chat_template(
            [{"role": str(m["role"]), "content": m["content"]} for m in messages],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        call_id = len(self.calls)
        started = time.monotonic()
        result = self.llm.generate([prompt], SamplingParams(
            max_tokens=max_tokens, temperature=temperature, seed=self.seed + call_id),
            use_tqdm=False)[0]
        completion = result.outputs[0]
        row = {"id": call_id, "kind": kind, "seed": self.seed + call_id,
               "messages": [{"role": str(m["role"]), "content": m["content"]} for m in messages],
               "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
               "response": completion.text, "finish_reason": completion.finish_reason,
               "prompt_tokens": len(result.prompt_token_ids),
               "completion_tokens": len(completion.token_ids),
               "wall_seconds": time.monotonic() - started}
        self.calls.append(row)
        with self.trace_file.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return completion.text

    def batch(self, requests):
        """Independent, explicitly seeded requests; no conversational state."""
        from vllm import SamplingParams
        prompts = [self.tokenizer.apply_chat_template(
            r["messages"], tokenize=False, add_generation_prompt=True,
            enable_thinking=False) for r in requests]
        params = [SamplingParams(max_tokens=r.get("max_tokens", 128), temperature=0.7,
                                 seed=r["seed"]) for r in requests]
        started = time.monotonic()
        results = self.llm.generate(prompts, params, use_tqdm=False)
        elapsed = time.monotonic() - started
        rows = []
        with self.trace_file.open("a") as f:
            for request, prompt, result in zip(requests, prompts, results):
                completion = result.outputs[0]
                row = {**request, "response": completion.text,
                       "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                       "prompt_tokens": len(result.prompt_token_ids),
                       "completion_tokens": len(completion.token_ids),
                       "finish_reason": completion.finish_reason,
                       "batch_wall_seconds": elapsed}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows.append(row)
        self.calls.extend(rows)
        return rows


def instrument(g, target):
    original = g.parser.parse_command
    records = []
    def parse(command, actor=None):
        before = core_state(g)
        actor_name = actor.name if actor is not None else None
        started = time.monotonic()
        try:
            ok = original(command, actor=actor)
            error = None
        except Exception as exc:
            ok, error = False, f"{type(exc).__name__}: {exc}"
        after = core_state(g)
        row = {"turn": g.turn, "command": command, "actor": actor_name,
               "success": bool(ok), "exception": error,
               "failure_reason": getattr(g.parser, "last_fail_message", None) if not ok else None,
               "before": before, "after": after, "delta": state_diff(before, after),
               "wall_seconds": time.monotonic() - started}
        records.append(row)
        with Path(target).open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        # Preserve native exception semantics; do not turn crashes into failures.
        if error is not None:
            raise RuntimeError(error)
        return ok
    g.parser.parse_command = parse
    return records


def run_episode(client, name):
    from notebooks.hw1_llm.play import build_llm_game
    from text_adventure_games.webapp.web_parser import WebParser
    g = build_llm_game(client)
    g.set_parser(WebParser(g))
    rows = instrument(g, client.trace_file.parent / f"{name}_actions.jsonl")
    start_calls = len(client.calls)
    turns = []
    for command in PLAYER_SCRIPTS[name]:
        if g.is_game_over():
            break
        ok = g.do_command(command)
        turns.append({"command": command, "success": bool(ok), "turn": g.turn,
                      "messages": g.parser.get_messages(), "state": core_state(g)})
    dump(client.trace_file.parent / f"{name}_episode.json", turns)
    return {"name": name, "player_turns": len(turns), "actions": len(rows),
            "parser_successes": sum(r["success"] for r in rows),
            "model_calls": len(client.calls) - start_calls,
            "world_change_actions": sum(bool(r["delta"]) for r in rows),
            "player_state": dict(g.player.properties),
            "npc_action_counts": dict(Counter(r["actor"] for r in rows if r["actor"])),
            "fallback_script_calls": 0, "final_location": g.player.location.name}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_CACHE / "sources/agent-sandbox")
    ap.add_argument("--mode", choices=["cpu", "model"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", type=Path)
    ap.add_argument("--seed", type=int, default=101)
    ap.add_argument("--episode", choices=list(PLAYER_SCRIPTS), default="intruder")
    args = ap.parse_args()
    commit = subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True).strip()
    assert commit == SOURCE_SHA, commit
    sys.path.insert(0, str(args.source))
    args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE="1", HF_DATASETS_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
                      TOKENIZERS_PARALLELISM="false")
    t0 = time.monotonic()
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_sha": commit, "harness_sha256": sha(__file__), "mode": args.mode,
                "seed": args.seed, "python": sys.version, "model": str(args.model),
                "cloud_calls": 0, "cuda_visible_devices": os.getenv("CUDA_VISIBLE_DEVICES", ""),
                "flashinfer_sampler": os.getenv("VLLM_USE_FLASHINFER_SAMPLER", "default"),
                "dependencies": {m: importlib.metadata.version(m) for m in ["prompty", "jinja2", "pyyaml"]}}
    if args.mode == "model":
        manifest["dependencies"].update({m: importlib.metadata.version(m) for m in ["torch", "vllm", "transformers"]})
        manifest["model_config_sha256"] = sha(args.model / "config.json")
        manifest["tokenizer_config_sha256"] = sha(args.model / "tokenizer_config.json")
    dump(args.out / "manifest.json", manifest)
    if args.mode == "cpu":
        result = cpu_controls()
    else:
        assert args.model is not None
        client = LocalClient(args.model, args.seed, args.out / "model_calls.jsonl")
        result = run_episode(client, args.episode)
        result.update(prompt_tokens=sum(c["prompt_tokens"] for c in client.calls),
                      completion_tokens=sum(c["completion_tokens"] for c in client.calls))
    result["wall_seconds"] = time.monotonic() - t0
    dump(args.out / "summary.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
