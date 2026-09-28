#!/usr/bin/env python
"""E08 summary: external validity on naturally occurring `before`-clauses."""
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


def boot(vals, rng):
    a = np.array(vals, dtype=float)
    idx = rng.integers(0, len(a), size=(N_BOOT, len(a)))
    s = a[idx].mean(axis=1)
    return float(a.mean()), *[float(x) for x in np.percentile(s, [2.5, 97.5])]


def main():
    cfg = json.load(open(os.path.join(PROJ, "configs", "natural_e08.json"), encoding="utf-8"))
    stim = {
        j["item_id"]: j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
    }
    rng = np.random.default_rng(cfg["seed"])
    report = {}
    lines = ["# L13 E08 — natural `before`-clauses from the Pile", ""]
    lines.append(f"{sum(1 for v in stim.values() if not v['gold_realized'])} prevented, "
                 f"{sum(1 for v in stim.values() if v['gold_realized'])} veridical; hand-adjudicated.\n")

    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        if not os.path.exists(os.path.join(d, "manifest.json")):
            continue
        e = {}
        ghost = collections.defaultdict(list)
        for line in open(os.path.join(d, "context_turns.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            if r["task_order"] != "timeline_first":
                continue
            it = stim[r["item_id"]]
            ghost[it["condition"]].append(float(output_asserts_target(r["text"], it["target"])))
        e["ghost"] = {k: [round(x, 3) for x in boot(v, rng)] for k, v in ghost.items()}

        probs = collections.defaultdict(lambda: collections.defaultdict(list))
        for line in open(os.path.join(d, "strict.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            probs[(r["task_order"], stim[r["item_id"]]["condition"])][r["item_id"]].append(r["probs"])
        e["commit"] = {}
        for (order, cond), by_item in probs.items():
            vals = [statistics.fmean(p["YES"] for p in ps) for ps in by_item.values()]
            e["commit"][f"{order}/{cond}"] = [round(x, 3) for x in boot(vals, rng)]
        report[spec["slug"]] = e

        lines.append(f"## {spec['slug']}\n")
        lines.append("| quantity | prevented | veridical |")
        lines.append("|---|---|---|")
        g = e["ghost"]
        lines.append(
            f"| listed on the timeline as a realized node | **{g['natural_prevented'][0]:.3f}** "
            f"[{g['natural_prevented'][1]:.2f}, {g['natural_prevented'][2]:.2f}] | "
            f"{g['natural_veridical'][0]:.3f} |"
        )
        for order in ("fact_first", "timeline_first"):
            c = e["commit"]
            lines.append(
                f"| P(YES) direct, {order} | {c[f'{order}/natural_prevented'][0]:.3f} | "
                f"{c[f'{order}/natural_veridical'][0]:.3f} |"
            )
        lines.append("")

    with open(os.path.join(PROJ, "results", cfg["tag"], "summary.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    with open(os.path.join(PROJ, "results", cfg["tag"], "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
