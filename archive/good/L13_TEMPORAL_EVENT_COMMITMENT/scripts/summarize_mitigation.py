#!/usr/bin/env python
"""L13 E10 summary: status-first mitigation vs the plain and strict timelines."""
import collections
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))
from ghost_detect import output_asserts_target  # noqa: E402

N_BOOT = 10000
CONDS = ["before_neutral", "before_cancel", "after", "nontemporal_neutral"]


def boot(vals, rng):
    a = np.array(vals, dtype=float)
    idx = rng.integers(0, len(a), size=(N_BOOT, len(a)))
    s = a[idx].mean(axis=1)
    return (float(a.mean()), *[float(x) for x in np.percentile(s, [2.5, 97.5])])


def baseline(d, stim, task):
    out = collections.defaultdict(list)
    for name in ("context_turns.jsonl", "context_turns_e04.jsonl"):
        p = os.path.join(d, name)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["task_order"] != task:
                continue
            it = stim[r["item_id"]]
            out[it["condition"]].append(float(output_asserts_target(r["text"], it["target"])))
    return out


def main():
    cfg = json.load(open(os.path.join(PROJ, "configs", "pilot_v1.json"), encoding="utf-8"))
    stim = {
        j["item_id"]: j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
    }
    rng = np.random.default_rng(cfg["seed"])
    lines = ["# L13 E10 — status-first mitigation", "",
             "Ghost rate: the target event emitted as a realized node of the timeline.", ""]
    report = {}
    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        mp = os.path.join(d, "mitigation.jsonl")
        if not os.path.exists(mp):
            continue
        mit = collections.defaultdict(list)
        for line in open(mp, encoding="utf-8"):
            r = json.loads(line)
            mit[r["condition"]].append(float(r["ghost"]))
        plain = baseline(d, stim, "timeline_first")
        strict = baseline(d, stim, "timeline_strict_first")
        report[spec["slug"]] = {
            c: {
                "plain": [round(x, 3) for x in boot(plain[c], rng)] if plain.get(c) else None,
                "strict_instruction": [round(x, 3) for x in boot(strict[c], rng)] if strict.get(c) else None,
                "status_first": [round(x, 3) for x in boot(mit[c], rng)] if mit.get(c) else None,
            }
            for c in CONDS
        }
        lines.append(f"## {spec['slug']}\n")
        lines.append("| condition | plain timeline | + prohibition | **status-first** |")
        lines.append("|---|---|---|---|")
        for c in CONDS:
            r = report[spec["slug"]][c]
            def f(x, bold=False):
                if not x:
                    return "n/a"
                s = f"{x[0]:.3f}"
                return f"**{s}**" if bold else s
            lines.append(f"| {c} | {f(r['plain'])} | {f(r['strict_instruction'])} | {f(r['status_first'], True)} |")
        lines.append("")
    with open(os.path.join(PROJ, "results", cfg["tag"], "mitigation_summary.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
