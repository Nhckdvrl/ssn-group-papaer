#!/usr/bin/env python
"""L13 E13 summary: error propagation from the emitted timeline to a downstream reader."""
import collections
import json
import os
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
N_BOOT = 10000
CONDS = ["after", "before_neutral", "before_confirm", "before_cancel", "nontemporal_neutral"]


def boot(vals, rng):
    a = np.array(vals, dtype=float)
    idx = rng.integers(0, len(a), size=(N_BOOT, len(a)))
    return (float(a.mean()), *[float(x) for x in np.percentile(a[idx].mean(axis=1), [2.5, 97.5])])


def collect(path, want_order):
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["task_order"] != want_order:
            continue
        per[r["condition"]][r["base_id"]].append((r["probs"], r["gold_strict"]))
    return per


def main():
    cfg = json.load(open(os.path.join(PROJ, "configs", "pilot_v1.json"), encoding="utf-8"))
    rng = np.random.default_rng(cfg["seed"])
    lines = ["# L13 E13 — pipeline error propagation", "",
             "Stage 2 sees only the model's own emitted timeline; the passage is removed.", ""]
    report = {}
    for spec in cfg["models"]:
        d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
        qa = os.path.join(d, "pipeline_qa.jsonl")
        if not os.path.exists(qa):
            continue
        tl = collect(qa, "timeline_grounded")
        src = collect(os.path.join(d, "strict.jsonl"), "fact_first")
        e = {}
        lines.append(f"## {spec['slug']}\n")
        lines.append("| condition | P(YES) from passage | P(YES) from own timeline | accuracy from passage | accuracy from own timeline |")
        lines.append("|---|---|---|---|---|")
        for c in CONDS:
            if c not in tl:
                continue
            def agg(per):
                yes = [statistics.fmean(p["YES"] for p, _ in v) for v in per[c].values()]
                acc = [
                    statistics.fmean(float(max(p, key=p.get) == g) for p, g in v)
                    for v in per[c].values()
                ]
                return boot(yes, rng), boot(acc, rng)
            (sy, sa), (ty, ta) = agg(src), agg(tl)
            e[c] = {"src_yes": sy, "tl_yes": ty, "src_acc": sa, "tl_acc": ta}
            lines.append(
                f"| {c} | {sy[0]:.3f} | **{ty[0]:.3f}** | {sa[0]:.3f} | **{ta[0]:.3f}** |"
            )
        report[spec["slug"]] = e
        lines.append("")
    with open(os.path.join(PROJ, "results", cfg["tag"], "pipeline_qa_summary.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
