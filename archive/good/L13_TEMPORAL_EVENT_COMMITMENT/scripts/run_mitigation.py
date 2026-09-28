#!/usr/bin/env python
"""L13 E10: can a cheap pipeline change stop the instantiation?

Mitigation under test — **status-first**: the model is asked to state each
mentioned event's realization status *before* it is asked for a timeline. The
timeline is then generated in the same conversation and scored for ghost nodes,
so the comparison against the plain timeline is on identical text and identical
final instruction.

This is a deployable recommendation if it works, and a negative result about
prompt-level repair if it does not.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))

import torch  # noqa: E402

import probes  # noqa: E402
from ghost_detect import output_asserts_target  # noqa: E402
from scoring import generate, load_model, render  # noqa: E402

STATUS_TURN = (
    "Passage:\n{passage}\n\n"
    "For each event mentioned in this passage, state whether the passage "
    "guarantees that it happened. Answer one per line as "
    "<event> :: guaranteed | left open | ruled out."
)

TIMELINE_TURN = (
    "Now list only the events that actually happened, in chronological order, "
    "one per line, earliest first. Do not add commentary."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "pilot_v1.json"))
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="cuda:0")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    spec = next(m for m in cfg["models"] if m["slug"] == args.model)
    items = [json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8")]
    out_dir = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
    os.makedirs(out_dir, exist_ok=True)

    torch.manual_seed(cfg["seed"])
    t0 = time.time()
    tok, model = load_model(spec["model_id"], args.device, dtype=cfg["dtype"])

    step1 = generate(
        tok,
        model,
        [render(tok, [{"role": "user", "content": STATUS_TURN.format(passage=it["passage"])}]) for it in items],
        args.device,
        max_new_tokens=240,
        batch_size=cfg["gen_batch_size"],
    )
    step2 = generate(
        tok,
        model,
        [
            render(
                tok,
                [
                    {"role": "user", "content": STATUS_TURN.format(passage=it["passage"])},
                    {"role": "assistant", "content": s1},
                    {"role": "user", "content": TIMELINE_TURN},
                ],
            )
            for it, s1 in zip(items, step1)
        ],
        args.device,
        max_new_tokens=cfg["max_new_tokens"],
        batch_size=cfg["gen_batch_size"],
    )

    with open(os.path.join(out_dir, "mitigation.jsonl"), "w", encoding="utf-8") as f:
        for it, s1, s2 in zip(items, step1, step2):
            f.write(
                json.dumps(
                    {
                        "item_id": it["item_id"],
                        "base_id": it["base_id"],
                        "condition": it["condition"],
                        "status_turn": s1,
                        "timeline": s2,
                        "ghost": output_asserts_target(s2, it["target"]),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"[{spec['slug']}] mitigation done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
