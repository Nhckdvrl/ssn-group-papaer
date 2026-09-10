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

HEDGES = re.compile(
    r"\b(not|never|n't|unclear|unknown|unresolved|may|might|would|could|if|whether|"
    r"planned|intended|hoped|meant|wanted|possible|possibly|uncertain|did not)\b",
    re.I,
)
STOP = set(
    "the a an of to and or in on at for with his her their its by that this it".split()
)


def content(s):
    return {w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP}


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
            tgt = content(it["target"])
            ghost = False
            for ln in r["text"].splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                if HEDGES.search(ln):
                    continue
                overlap = len(tgt & content(ln)) / max(1, len(tgt))
                if overlap >= 0.7:
                    ghost = True
                    break
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
