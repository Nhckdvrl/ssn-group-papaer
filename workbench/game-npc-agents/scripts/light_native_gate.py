#!/usr/bin/env python3
"""E11 native graph/events over original Dragon quests, no model/DB registry.

This is an event host, not a replacement game engine. Preconditions, parsing,
effects, probability and views are the unchanged upstream event implementations.
It does not reproduce the original learned partner, scoring model or RL policy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tarfile
import types


def load_event_modules(source):
    # LIGHT.__init__ registers legacy Hydra/ParlAI/database configurations. These
    # are unused for pure graph/event execution and conflict with modern Python.
    # Skip only that registration; import every graph and event from pinned source.
    package = types.ModuleType("light")
    package.__path__ = [str(source / "light")]
    sys.modules["light"] = package
    from light.graph.structured_graph import OOGraph
    from light.graph.events import graph_events as events
    from light.graph.events.base import ErrorEvent
    return OOGraph, events, ErrorEvent


class EventHost:
    def __init__(self, graph):
        self.oo_graph = graph
        self.messages = []
        self.debug = False

    def broadcast_to_room(self, event, exclude_agents=None):
        excluded = exclude_agents or []
        viewers = [n for n in event.actor.get_room().get_contents() if n.agent and n not in excluded]
        self.broadcast_to_agents(event, viewers)

    def broadcast_to_agents(self, event, agents):
        for viewer in agents:
            text = event.view_as(viewer)
            if text:
                self.messages.append({"viewer": viewer.node_id, "event": type(event).__name__, "text": text})


def parse_event(graph, actor, command, events, error_type):
    verb, _, arguments = command.partition(" ")
    registry = {name: cls for cls in vars(events).values() if isinstance(cls, type)
                and hasattr(cls, "NAMES") for name in cls.NAMES}
    if verb not in registry:
        raise ValueError(f"No native event for {verb}")
    cls = registry[verb]
    interpretations = cls.split_text_args(actor, arguments)
    if isinstance(interpretations, error_type):
        return interpretations
    result = None
    for parts in interpretations:
        result = cls.find_nodes_for_args(graph, actor, *parts)
        if not isinstance(result, error_type):
            break
    if isinstance(result, error_type):
        return result
    return cls.construct_from_args(actor, result.targets, result.text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("/home/xiang/.cache/game-npc-research/sources/LIGHT"))
    ap.add_argument("--archive", type=Path, default=Path("/home/xiang/.cache/game-npc-research/quest_stems.tar.gz"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    commit = subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True).strip()
    assert commit == "71a06cae8573048b1af41507ac52fe33b650fab3"
    assert hashlib.sha256(args.archive.read_bytes()).hexdigest() == "743d9a9dc85e9fd7737c6cb51762deae684382de326bf724cde5b72bcf7c7c7d"
    OOGraph, events, ErrorEvent = load_event_modules(args.source)
    result = {"source_sha": commit, "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
              "model_calls": 0, "gpu_hours": 0, "scope": "native event host; not original RL/partner reproduction",
              "cases": []}
    with tarfile.open(args.archive) as archive:
        for file in ["10000.json", "10001.json", "10002.json"]:
            data = json.load(archive.extractfile("quest_stems/" + file))["data"]
            for seed in [701, 702]:
                graph = OOGraph.from_json(data["graph"])
                actor = next(a for a in graph.agents.values() if
                             a.get_prefix_view() == data["character"] or
                             a.name == data["character"].removeprefix("the "))
                negative_before = graph.to_json()
                invalid = parse_event(graph, actor, "get definitely_missing_item", events, ErrorEvent)
                assert isinstance(invalid, ErrorEvent)
                assert graph.to_json() == negative_before
                event = parse_event(graph, actor, data["goal"], events, ErrorEvent)
                row = {"file": file, "seed": seed, "actor": actor.node_id, "goal": data["goal"],
                       "graph_nodes": len(graph.all_nodes), "invalid_rejected_without_change": True,
                       "legal": not isinstance(event, ErrorEvent)}
                before = json.loads(graph.to_json())
                if row["legal"]:
                    random.seed(seed)
                    host = EventHost(graph)
                    event.execute(host)
                    row.update(event_type=type(event).__name__, executed=event.executed,
                               stochastic_failure=getattr(event, "failed", False),
                               state_changed=json.loads(graph.to_json()) != before,
                               messages=host.messages)
                else:
                    row["native_error"] = event.view_as(actor)
                result["cases"].append(row)
    result["graph_cases"] = len(result["cases"])
    result["legal_goals"] = sum(r["legal"] for r in result["cases"])
    result["executed_events"] = sum(r.get("executed", False) for r in result["cases"])
    result["material_changes"] = sum(r.get("state_changed", False) for r in result["cases"])
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}), flush=True)


if __name__ == "__main__":
    main()
