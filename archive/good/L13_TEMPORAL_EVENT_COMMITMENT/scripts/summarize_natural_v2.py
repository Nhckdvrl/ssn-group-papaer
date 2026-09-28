#!/usr/bin/env python
"""Natural set v2: 176 hand-adjudicated Pile sentences, by realization status and cue."""
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
CELLS = [
    ("natural_unresolved", "plain_past"),
    ("natural_prevented", "plain_past"),
    ("natural_prevented", "modal"),
    ("natural_unresolved", "modal"),
    ("natural_realized", "plain_past"),
]
# the natural analogue of `before_neutral`: non-veridical with no lexical marking
UNMARKED_NONVERIDICAL = {("natural_unresolved", "plain_past"), ("natural_prevented", "plain_past")}
MARKED_NONVERIDICAL = {("natural_unresolved", "modal"), ("natural_prevented", "modal")}


def boot(v, rng):
    a = np.array(v, dtype=float)
    if len(a) < 2:
        return (float(a.mean()) if len(a) else float("nan"), float("nan"), float("nan"))
    idx = rng.integers(0, len(a), size=(N_BOOT, len(a)))
    return (float(a.mean()), *[float(x) for x in np.percentile(a[idx].mean(axis=1), [2.5, 97.5])])


def main():
    cfg = json.load(open(os.path.join(PROJ, "configs", "natural_v2.json"), encoding="utf-8"))
    stim = {
        j["item_id"]: j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
    }
    rng = np.random.default_rng(cfg["seed"])
    lines = ["# L13 — natural set v2 (176 adjudicated Pile sentences)", "",
             "Instantiation = the subordinate event emitted as a realized timeline node.", "",
             "| model | " + " | ".join(f"{c}/{q}" for c, q in CELLS) + " |",
             "|---" * (len(CELLS) + 1) + "|"]
    report = {}
    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        if not os.path.exists(os.path.join(d, "manifest.json")):
            continue
        g = collections.defaultdict(list)
        for line in open(os.path.join(d, "context_turns.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            if r["task_order"] != "timeline_first":
                continue
            it = stim[r["item_id"]]
            g[(it["condition"], it["clause_cue"])].append(
                float(output_asserts_target(r["text"], it["target"]))
            )
        row, e = [], {}
        for cell in CELLS:
            v = g.get(cell, [])
            m = boot(v, rng) if v else (float("nan"),) * 3
            e[f"{cell[0]}/{cell[1]}"] = [round(x, 3) for x in m] + [len(v)]
            row.append(f"{m[0]:.3f} (n={len(v)})" if v else "—")
        for name, cells in (("unmarked_nonveridical", UNMARKED_NONVERIDICAL),
                            ("marked_nonveridical", MARKED_NONVERIDICAL)):
            pooled = [x for c in cells for x in g.get(c, [])]
            e[name] = [round(x, 3) for x in boot(pooled, rng)] + [len(pooled)]
        report[spec["slug"]] = e
        lines.append(f"| {spec['slug']} | " + " | ".join(row) + " |")

    lines += ["", "Pooled by lexical marking (the study's scope claim, on natural text):", "",
              "| model | unmarked non-veridical | marked non-veridical |", "|---|---|---|"]
    for slug, e in report.items():
        u, m = e["unmarked_nonveridical"], e["marked_nonveridical"]
        lines.append(
            f"| {slug} | **{u[0]:.3f}** [{u[1]:.2f}, {u[2]:.2f}] (n={u[3]}) | "
            f"{m[0]:.3f} [{m[1]:.2f}, {m[2]:.2f}] (n={m[3]}) |"
        )

    # direct probe, for the same cells
    lines += ["", "Direct probe P(YES), fact_first:", "",
              "| model | " + " | ".join(f"{c}/{q}" for c, q in CELLS) + " |",
              "|---" * (len(CELLS) + 1) + "|"]
    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        p = os.path.join(d, "strict.jsonl")
        if not os.path.exists(p) or spec["slug"] not in report:
            continue
        per = collections.defaultdict(lambda: collections.defaultdict(list))
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["task_order"] != "fact_first":
                continue
            it = stim[r["item_id"]]
            per[(it["condition"], it["clause_cue"])][r["item_id"]].append(r["probs"]["YES"])
        row = []
        for cell in CELLS:
            vals = [statistics.fmean(v) for v in per.get(cell, {}).values()]
            row.append(f"{statistics.fmean(vals):.3f}" if vals else "—")
            if vals:
                report[spec["slug"]][f"direct/{cell[0]}/{cell[1]}"] = round(statistics.fmean(vals), 3)
        lines.append(f"| {spec['slug']} | " + " | ".join(row) + " |")

    with open(os.path.join(PROJ, "results", cfg["tag"], "summary_v2.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
