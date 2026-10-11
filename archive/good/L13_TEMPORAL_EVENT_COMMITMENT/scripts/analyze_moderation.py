#!/usr/bin/env python
"""L13 E11: does the effect depend on item-level pragmatic bias?

The `before` norming literature identifies item veridicality bias as the main
nuisance variable. If the instantiation effect were just "the model believes the
event probably happened", it should track `pragmatic_bias`. Pure analysis of
existing runs; no new generation.
"""
import collections
import json
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))
from ghost_detect import output_asserts_target  # noqa: E402

N_BOOT = 10000
BIASES = ["no_leaning", "neutral", "yes_leaning"]


def boot(vals, rng):
    a = np.array(vals, dtype=float)
    if len(a) < 2:
        return (float(a.mean()), float("nan"), float("nan"))
    idx = rng.integers(0, len(a), size=(N_BOOT, len(a)))
    s = a[idx].mean(axis=1)
    return (float(a.mean()), *[float(x) for x in np.percentile(s, [2.5, 97.5])])


def main():
    cfg = json.load(open(os.path.join(PROJ, "configs", "pilot_v1.json"), encoding="utf-8"))
    stim = {
        j["item_id"]: j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
    }
    bias = {j["base_id"]: j["pragmatic_bias"] for j in stim.values()}
    rng = np.random.default_rng(cfg["seed"])
    report, lines = {}, ["# L13 E11 — pragmatic-bias moderation", ""]

    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        if not os.path.exists(os.path.join(d, "strict.jsonl")):
            continue
        # ghost rate on before_neutral, split by item bias
        g = collections.defaultdict(list)
        for line in open(os.path.join(d, "context_turns.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            if r["task_order"] != "timeline_first" or not r["item_id"].endswith("_before_neutral"):
                continue
            it = stim[r["item_id"]]
            g[bias[it["base_id"]]].append(float(output_asserts_target(r["text"], it["target"])))

        # timeline - paraphrase commitment shift, split by item bias
        per = collections.defaultdict(lambda: collections.defaultdict(list))
        for line in open(os.path.join(d, "strict.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            if r["condition"] != "before_neutral":
                continue
            per[r["task_order"]][r["base_id"]].append(r["probs"]["YES"])
        shift = collections.defaultdict(list)
        for b in per.get("timeline_first", {}):
            if b in per.get("paraphrase_first", {}):
                shift[bias[b]].append(
                    statistics.fmean(per["timeline_first"][b])
                    - statistics.fmean(per["paraphrase_first"][b])
                )
        report[spec["slug"]] = {
            "ghost": {k: [round(x, 3) for x in boot(v, rng)] for k, v in g.items()},
            "shift": {k: [round(x, 3) for x in boot(v, rng)] for k, v in shift.items()},
        }
        lines.append(f"## {spec['slug']}\n")
        lines.append("| item pragmatic bias | n | ghost rate | timeline − paraphrase |")
        lines.append("|---|---|---|---|")
        for b in BIASES:
            if b not in g:
                continue
            gg, ss = report[spec["slug"]]["ghost"][b], report[spec["slug"]]["shift"].get(b)
            st = f"{ss[0]:+.3f}" if ss else "n/a"
            lines.append(f"| {b} | {len(g[b])} | {gg[0]:.3f} | {st} |")
        lines.append("")

    with open(os.path.join(PROJ, "results", cfg["tag"], "moderation.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
