#!/usr/bin/env python
"""L13 E13: does the ghost node propagate to a downstream consumer?

Real pipelines extract a structure and then answer from the structure, not from
the source text. Stage 2 here sees ONLY the model's own timeline; the passage is
removed. If the timeline contains the unresolved event as a realized node, a
faithful downstream reader must answer YES.

Compares, on the same items and the same question:
  passage_grounded  - answer from the passage (upper bound)
  timeline_grounded - answer from the model's own emitted timeline
"""
import argparse
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "src"))

import torch  # noqa: E402

import probes  # noqa: E402
from scoring import build_candidate_map, load_model, render, score_candidates  # noqa: E402

TIMELINE_PROMPT = (
    "Event timeline:\n{timeline}\n\n"
    "This timeline is the only record you have of what happened.\n\n"
    "Statement: {target}\n\n"
    "Based only on the timeline, is the statement true?\n\n"
    "{options}\n\n"
    "Answer with a single letter."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "pilot_v1.json"))
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="cuda:0")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    spec = next(m for m in cfg["models"] if m["slug"] == args.model)
    stim = {
        j["item_id"]: j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
    }
    d = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
    timelines = {}
    for line in open(os.path.join(d, "context_turns.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        if r["task_order"] == "timeline_first":
            timelines[r["item_id"]] = r["text"]

    torch.manual_seed(cfg["seed"])
    t0 = time.time()
    tok, model = load_model(spec["model_id"], args.device, dtype=cfg["dtype"])
    letters = probes.LETTERS[:3]
    letter_map = build_candidate_map(tok, letters)

    prompts, meta = [], []
    for iid, tl in timelines.items():
        it = stim[iid]
        for pi, perm in enumerate(probes.PERMUTATIONS):
            opts = "\n".join(
                f"{L}. {probes.STRICT_OPTIONS[lab]}" for L, lab in zip(letters, perm)
            )
            msg = TIMELINE_PROMPT.format(timeline=tl, target=it["target"], options=opts)
            prompts.append(render(tok, [{"role": "user", "content": msg}]))
            meta.append((it, pi, perm))

    dists = score_candidates(
        tok, model, prompts, letter_map, args.device, batch_size=cfg["batch_size"]
    )
    out = os.path.join(d, "pipeline_qa.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for (it, pi, perm), dist in zip(meta, dists):
            f.write(
                json.dumps(
                    {
                        "item_id": it["item_id"],
                        "base_id": it["base_id"],
                        "condition": it["condition"],
                        "gold_strict": it["gold_strict"],
                        "task_order": "timeline_grounded",
                        "perm_idx": pi,
                        "probs": {lab: dist[L] for L, lab in zip(letters, perm)},
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    n = collections.Counter(m[0]["condition"] for m in meta)
    print(f"[{spec['slug']}] pipeline QA on {len(timelines)} timelines "
          f"({dict(n)}) in {time.time()-t0:.0f}s -> {out}")


if __name__ == "__main__":
    main()
