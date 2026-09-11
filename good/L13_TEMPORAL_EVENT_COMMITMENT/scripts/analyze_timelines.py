#!/usr/bin/env python
"""E03 (descriptive): does the model's own timeline list the unresolved event as a
plain realized node?

Heuristic, approximate, and never load-bearing for a claim. A generated line counts as
a *ghost node* when it lexically matches the unresolved target clause and carries no
hedge or negation.
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

sys.path.insert(0, os.path.join(PROJ, "src"))
from ghost_detect import output_asserts_target  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "pilot_v1.json"))
    args = ap.parse_args()
    cfg = json.load(open(args.config, encoding="utf-8"))
    stim = {
        j["item_id"]: j
        for j in (
            json.loads(l)
            for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8")
        )
    }

    report = {}
    for spec in cfg["models"]:
        import glob

        paths = sorted(
            glob.glob(
                os.path.join(PROJ, "results", cfg["tag"], spec["slug"], "context_turns*.jsonl")
            )
        )
        if not paths:
            continue
        counts = collections.defaultdict(lambda: [0, 0])
        for line in (l for path in paths for l in open(path, encoding="utf-8")):
            r = json.loads(line)
            if not r["task_order"].startswith("timeline"):
                continue
            it = stim[r["item_id"]]
            ghost = output_asserts_target(r["text"], it["target"])
            c = counts[(r["task_order"], it["condition"])]
            c[0] += int(ghost)
            c[1] += 1
        report[spec["slug"]] = {
            f"{k[0]}/{k[1]}": {"ghost_rate": round(v[0] / v[1], 3), "n": v[1]}
            for k, v in sorted(counts.items())
        }

    out = os.path.join(PROJ, "results", cfg["tag"], "timeline_nodes.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    for slug, r in report.items():
        print(slug, json.dumps(r))


if __name__ == "__main__":
    main()
