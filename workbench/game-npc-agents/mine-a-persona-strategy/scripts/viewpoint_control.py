#!/usr/bin/env python3
"""E09: literal location and native execution under frozen natural observations."""
import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from native_actioncastle import LocalClient, SOURCE_SHA, core_state, dump, state_diff, run_episode

CONDITIONS = ["original", "one_sentence", "viewer_labels", "neutral", "no_history"]
SENTENCE = "The first location block describes your current position; subsequent Game blocks may describe the player's viewpoint rather than your own."
NEUTRAL = "The first observation block is followed by recent events; every game turn may include various objects and actions in the text adventure."
SEEDS = [201, 202, 203]


def normalize(x):
    return json.loads(json.dumps(x))


def restore_prefix(source, prefix, expected):
    from notebooks.hw1_llm.play import build_llm_game
    from text_adventure_games.webapp.web_parser import WebParser
    g = build_llm_game(None)
    g.set_parser(WebParser(g))
    for row in prefix:
        g.turn = row["turn"]
        actor = g.characters.get(row["actor"]) if row["actor"] else None
        ok = bool(g.parser.parse_command(row["command"], actor=actor))
        assert ok == row["success"], (row["command"], ok)
    # Turn is scheduling metadata, replayed separately from physical actions.
    g.turn = expected["turn"]
    assert normalize(core_state(g)) == expected["before"], "Native snapshot replay differs"
    return g


def cases_from_trace(source, trace):
    calls = [json.loads(l) for l in (trace / "model_calls.jsonl").read_text().splitlines()]
    actions = [json.loads(l) for l in (trace / "intruder_actions.jsonl").read_text().splitlines()]
    cases = []
    for index, row in enumerate(actions):
        if row["actor"] == "The player":
            continue
        if len(cases) == 3:
            break
        g = restore_prefix(source, actions[:index], row)
        actor = g.characters[row["actor"]]
        call = calls[len(cases)]
        cases.append({"actor": actor.name, "location": actor.location.name,
                      "messages": call["messages"], "prefix": actions[:index],
                      "expected": row})
    assert [c["actor"] for c in cases] == ["troll", "guard", "ghost"]
    return cases


def condition_messages(messages, condition):
    out = deepcopy(messages)
    if condition == "one_sentence":
        out[0]["content"] += "\n" + SENTENCE
    elif condition == "neutral":
        out[0]["content"] += "\n" + NEUTRAL
    elif condition == "viewer_labels":
        # Includes event summaries as well as second-person player-rendered rooms.
        # The attribution is correct for this pinned source's entire Game stream.
        out[1]["content"] = out[1]["content"].replace("  Game:", "  Game (player-view narration):")
    elif condition == "no_history":
        out[1]["content"] = out[1]["content"].split("\n\nRecent events:")[0]
    return out


def probe_messages(messages, condition):
    out = deepcopy(messages)
    out[0]["content"] = out[0]["content"].split("Based on your persona,")[0]
    out[0]["content"] += "\nName your own current location. Reply with exactly its location name, without explanations."
    if condition == "one_sentence":
        out[0]["content"] += "\n" + SENTENCE
    elif condition == "neutral":
        out[0]["content"] += "\n" + NEUTRAL
    # All source data are preserved; only the action-output contract is replaced.
    return out


def run_model(args, cases):
    from text_adventure_games.npc import _parse_decision
    client = LocalClient(args.model, 201, args.out / "calls.jsonl")
    requests = []
    for case_index, case in enumerate(cases):
        for condition in CONDITIONS:
            messages = condition_messages(case["messages"], condition)
            for seed in SEEDS:
                for kind in ["action", "location"]:
                    request = {"case": case_index, "actor": case["actor"], "condition": condition,
                               "seed": seed, "kind": kind,
                               "messages": probe_messages(messages, condition) if kind == "location" else messages,
                               "max_tokens": 48 if kind == "location" else 128}
                    requests.append(request)
    for case_index, case in enumerate(cases):
        for kind in ["expression", "intention"]:
            system = case["messages"][0]["content"].split("Based on your persona,")[0]
            if kind == "expression":
                system += "\nIntroduce yourself in first person, including what matters to you. Use two sentences."
                observation = "Please introduce yourself."
            else:
                system += "\nWhat concrete world state do you intend to bring about now? State this goal in one sentence without giving a command."
                observation = case["messages"][1]["content"]
            requests.append({"case": case_index, "actor": case["actor"], "condition": "original",
                             "seed": 301, "kind": kind,
                             "messages": [{"role": "system", "content": system}, {"role": "user", "content": observation}],
                             "max_tokens": 128})
    rows = client.batch(requests)
    measures = []
    for row in rows:
        case = cases[row["case"]]
        base = {k: row[k] for k in ["case", "actor", "condition", "seed", "kind", "response", "prompt_tokens", "completion_tokens", "finish_reason"]}
        base["current_location"] = case["location"]
        if row["kind"] == "location":
            # Exact equality after casing/punctuation normalization; no LLM judge.
            cleaned = row["response"].strip().strip('"\'`*. ').lower()
            base["location_correct"] = cleaned == case["location"].lower()
        elif row["kind"] == "action":
            g = restore_prefix(args.source, case["prefix"], case["expected"])
            actor = g.characters[case["actor"]]
            reason, command, duration = _parse_decision(row["response"])
            before = core_state(g)
            base.update(reasoning=reason, command=command, duration=duration)
            try:
                base["legal"] = bool(command and g.parser.parse_command(command, actor=actor))
                base["error"] = None
            except Exception as exc:
                base["legal"] = False
                base["error"] = f"{type(exc).__name__}: {exc}"
            base["departed"] = actor.location.name != case["location"]
            base["delta"] = state_diff(before, core_state(g))
            base["failure_reason"] = getattr(g.parser, "last_fail_message", None) if not base["legal"] else None
        measures.append(base)
    dump(args.out / "measurements.json", measures)
    grouped = defaultdict(list)
    for row in measures:
        grouped[(row["condition"], row["kind"])].append(row)
    summary = {}
    for (condition, kind), group in grouped.items():
        if kind == "location":
            summary[f"{condition}/location"] = {"n": len(group), "correct": sum(r["location_correct"] for r in group)}
        elif kind == "action":
            summary[f"{condition}/action"] = {"n": len(group), "legal": sum(r["legal"] for r in group),
                                                "departed": sum(r["departed"] for r in group),
                                                "material": sum(bool(r["delta"]) for r in group)}
    summary["cost"] = {"calls": len(rows), "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
                       "completion_tokens": sum(r["completion_tokens"] for r in rows)}
    dump(args.out / "summary.json", summary)
    print(json.dumps(summary), flush=True)
    if args.complete_e07:
        for episode, seed in [("intruder", 102), ("intruder", 103),
                              ("feed", 101), ("feed", 102), ("feed", 103)]:
            folder = args.out / f"e07_{episode}_s{seed}"
            folder.mkdir(exist_ok=False)
            client.seed, client.calls, client.trace_file = seed, [], folder / "model_calls.jsonl"
            episode_start = time.monotonic()
            result = run_episode(client, episode)
            result.update(wall_seconds=time.monotonic() - episode_start,
                          prompt_tokens=sum(r["prompt_tokens"] for r in client.calls),
                          completion_tokens=sum(r["completion_tokens"] for r in client.calls), seed=seed)
            dump(folder / "summary.json", result)
            print(json.dumps(result), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("/home/xiang/.cache/game-npc-research/sources/agent-sandbox"))
    ap.add_argument("--trace", type=Path, default=Path("/home/xiang/.cache/game-npc-research/runs/e07_qwen32_intruder_s101_r1"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", type=Path)
    ap.add_argument("--complete-e07", action="store_true")
    args = ap.parse_args()
    sys.path.insert(0, str(args.source))
    args.out.mkdir(parents=True, exist_ok=False)
    cases = cases_from_trace(args.source, args.trace)
    dump(args.out / "cases.json", cases)
    # The source's three initial choices must replay exactly before any model calls.
    for case in cases:
        g = restore_prefix(args.source, case["prefix"], case["expected"])
        assert bool(g.parser.parse_command(case["expected"]["command"], actor=g.characters[case["actor"]])) == case["expected"]["success"]
        assert normalize(core_state(g)) == case["expected"]["after"]
    dump(args.out / "replay_controls.json", {"checks": 3, "exact_state_matches": 3,
                                             "source_sha": SOURCE_SHA, "cloud_calls": 0})
    if args.model is None:
        print("3 native snapshot replay controls PASS", flush=True)
        return
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1")
    started = time.monotonic()
    run_model(args, cases)
    dump(args.out / "runtime.json", {"wall_seconds": time.monotonic() - started,
                                     "model": str(args.model), "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


if __name__ == "__main__":
    main()
