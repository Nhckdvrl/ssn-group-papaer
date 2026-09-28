#!/usr/bin/env python
"""E18: downstream propagation on natural text.

Stage 2 reads only the model's own extracted event list; the real sentence is
removed. Cells follow the adjudicated natural set.
"""
import collections
import json
import os
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
N_BOOT = 10000


def boot(v, rng):
    a = np.array(v, dtype=float)
    if len(a) < 2:
        return (float(a.mean()) if len(a) else float("nan"),) * 3
    idx = rng.integers(0, len(a), size=(N_BOOT, len(a)))
    return (float(a.mean()), *[float(x) for x in np.percentile(a[idx].mean(axis=1), [2.5, 97.5])])


def yes_by_cell(path, order, stim, key):
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["task_order"] != order:
            continue
        it = stim[r["item_id"]]
        per[key(it)][r["item_id"]].append(r["probs"]["YES"])
    return {k: [statistics.fmean(v) for v in d.values()] for k, d in per.items()}


def main():
    cfg = json.load(open(os.path.join(PROJ, "configs", "natural_v2.json"), encoding="utf-8"))
    stim = {
        j["item_id"]: j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
    }

    def cell(it):
        if it["condition"] == "natural_realized":
            return "realized"
        return ("nonveridical_unmarked" if it["clause_cue"] == "plain_past"
                else "nonveridical_marked")

    rng = np.random.default_rng(cfg["seed"])
    lines = ["# L13 E18 — downstream propagation on natural text", "",
             "P(YES) reading the sentence vs reading only the model's own extracted list.", "",
             "| model | cell | from sentence | from own list | Δ |", "|---|---|---|---|---|"]
    report = {}
    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        qa = os.path.join(d, "pipeline_qa.jsonl")
        if not os.path.exists(qa):
            continue
        src = yes_by_cell(os.path.join(d, "strict.jsonl"), "fact_first", stim, cell)
        tl = yes_by_cell(qa, "timeline_grounded", stim, cell)
        report[spec["slug"]] = {}
        for c in ("nonveridical_unmarked", "nonveridical_marked", "realized"):
            if c not in tl:
                continue
            s, t = boot(src[c], rng), boot(tl[c], rng)
            delta = boot([b - a for a, b in zip(src[c], tl[c])], rng)
            report[spec["slug"]][c] = {"src": [round(x, 3) for x in s],
                                       "list": [round(x, 3) for x in t],
                                       "delta": [round(x, 3) for x in delta],
                                       "n": len(src[c])}
            lines.append(
                f"| {spec['slug']} | {c} (n={len(src[c])}) | {s[0]:.3f} | **{t[0]:.3f}** | "
                f"{delta[0]:+.3f} [{delta[1]:+.3f}, {delta[2]:+.3f}] |"
            )
    with open(os.path.join(PROJ, "results", cfg["tag"], "pipeline_qa_summary.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
