#!/usr/bin/env python
"""L13 E09b: does the emitted timeline get the ORDER right, independently of
whether it instantiates the unresolved event?

For `before <target>, <main>` the chronologically correct emitted order is
main-event-first. This measures order correctness and instantiation on the same
generations, so the two can move in opposite directions.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))
from ghost_detect import content, line_asserts_target, output_asserts_target  # noqa: E402


def first_index(lines, text, thr=0.6):
    tw = content(text)
    for i, ln in enumerate(lines):
        if not tw:
            continue
        if len(tw & content(ln)) / len(tw) >= thr:
            return i
    return None


def measure(path, stim, task, cond="before_neutral"):
    order_ok, order_n, ghost = 0, 0, []
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["task_order"] != task or not r["item_id"].endswith("_" + cond):
            continue
        it = stim[r["item_id"]]
        lines = [l.strip() for l in r["text"].splitlines() if l.strip()]
        ghost.append(float(output_asserts_target(r["text"], it["target"])))
        i_t = first_index(lines, it["target"])
        i_m = first_index(lines, it["main_event"])
        if i_t is not None and i_m is not None and i_t != i_m:
            order_n += 1
            order_ok += int(i_m < i_t)  # main event should come first
    return {
        "n": len(ghost),
        "instantiation_rate": round(sum(ghost) / max(1, len(ghost)), 3),
        "order_scorable": order_n,
        "order_correct": round(order_ok / order_n, 3) if order_n else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stimuli", default=os.path.join(PROJ, "data", "stimuli_v1.jsonl"))
    args = ap.parse_args()
    stim = {j["item_id"]: j for j in (json.loads(l) for l in open(args.stimuli, encoding="utf-8"))}

    rows = []
    for tag, slug, label in [
        ("pilot_v1", "qwen3_8b", "Qwen3-8B, no thinking"),
        ("e09_thinking", "qwen3_8b", "Qwen3-8B, thinking"),
        ("pilot_v1", "qwen3_32b", "Qwen3-32B, no thinking"),
        ("e09_thinking", "qwen3_32b", "Qwen3-32B, thinking"),
        ("pilot_v1", "llama31_8b_instruct", "Llama-3.1-8B"),
        ("pilot_v1", "gemma3_12b_it", "Gemma-3-12B"),
    ]:
        p = os.path.join(PROJ, "results", tag, slug, "context_turns.jsonl")
        if not os.path.exists(p):
            continue
        rows.append((label, measure(p, stim, "timeline_first")))

    print(f"{'setting':26s}{'instantiation':>15s}{'order correct':>15s}{'(scorable)':>12s}")
    for label, m in rows:
        oc = "n/a" if m["order_correct"] is None else f"{m['order_correct']:.3f}"
        print(f"{label:26s}{m['instantiation_rate']:>15.3f}{oc:>15s}{m['order_scorable']:>12d}")
    with open(os.path.join(PROJ, "results", "order_vs_realization.json"), "w", encoding="utf-8") as f:
        json.dump({l: m for l, m in rows}, f, indent=2)


if __name__ == "__main__":
    main()
