#!/usr/bin/env python
"""L13 E05: does a NON-GENERATIVE temporal demand move realization commitment?

The context turn is a single letter (the model's own answer to a multiple-choice
question), so no declarative sentence about the target event can enter the
context. Two demands are compared on identical passages:

  order_mc_first : "Which of these happened earlier?"  (temporal computation)
  topic_mc_first : "Is this passage written in the past tense?"  (control)

If commitment moves only after the temporal demand, the effect cannot be
explained by generic self-conditioning on the model's own generated text.
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
import transformers  # noqa: E402

import probes  # noqa: E402
from scoring import build_candidate_map, load_model, render, score_candidates  # noqa: E402

ORDER_PERM = ("FIRST_MAIN", "FIRST_TARGET", "UNDETERMINED")
TOPIC_PERM = ("LONGER", "SHORTER", "UNDETERMINED")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "pilot_v1.json"))
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="cuda:0")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    spec = next(m for m in cfg["models"] if m["slug"] == args.model)
    items = read_jsonl(os.path.join(PROJ, cfg["stimuli"]))
    out_dir = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
    os.makedirs(out_dir, exist_ok=True)

    torch.manual_seed(cfg["seed"])
    t0 = time.time()
    tok, model = load_model(spec["model_id"], args.device, dtype=cfg["dtype"])
    letters = probes.LETTERS[:3]
    letter_map = build_candidate_map(tok, letters)

    demands = {
        "order_mc_first": lambda it: probes.order_mc_prompt(
            it["passage"], it["main_event"], it["target"], ORDER_PERM
        ),
        "topic_mc_first": lambda it: probes.topic_mc_prompt(it["passage"], TOPIC_PERM),
    }

    raw_path = os.path.join(out_dir, "strict_coupling.jsonl")
    ctx_path = os.path.join(out_dir, "context_turns_coupling.jsonl")
    with open(raw_path, "w", encoding="utf-8") as raw_f, open(
        ctx_path, "w", encoding="utf-8"
    ) as ctx_f:
        for order, build in demands.items():
            demand_prompts = [build(it) for it in items]
            rendered = [
                render(tok, [{"role": "user", "content": p}]) for p in demand_prompts
            ]
            dists = score_candidates(
                tok, model, rendered, letter_map, args.device, batch_size=cfg["batch_size"]
            )
            chosen = []
            for it, p, d in zip(items, demand_prompts, dists):
                letter = max(d, key=d.get)
                chosen.append((p, letter))
                ctx_f.write(
                    json.dumps(
                        {
                            "item_id": it["item_id"],
                            "task_order": order,
                            "demand_prompt": p,
                            "letter": letter,
                            "letter_probs": d,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

            flat, meta = [], []
            for it, (demand, letter) in zip(items, chosen):
                for perm_idx, perm in enumerate(probes.PERMUTATIONS):
                    msgs = [
                        {"role": "user", "content": demand},
                        {"role": "assistant", "content": letter},
                        {
                            "role": "user",
                            "content": probes.strict_followup_prompt(it["target"], perm),
                        },
                    ]
                    flat.append(render(tok, msgs))
                    meta.append((it, perm_idx, perm))
            scored = score_candidates(
                tok, model, flat, letter_map, args.device, batch_size=cfg["batch_size"]
            )
            for (it, perm_idx, perm), dist in zip(meta, scored):
                raw_f.write(
                    json.dumps(
                        {
                            "item_id": it["item_id"],
                            "base_id": it["base_id"],
                            "condition": it["condition"],
                            "gold_strict": it["gold_strict"],
                            "task_order": order,
                            "perm_idx": perm_idx,
                            "probs": {
                                label: dist[letter]
                                for letter, label in zip(letters, perm)
                            },
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            print(f"[{spec['slug']}] {order}: {len(flat)} scored", flush=True)

    with open(os.path.join(out_dir, "manifest_coupling.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_id": spec["model_id"],
                "family": spec["family"],
                "dtype": cfg["dtype"],
                "seed": cfg["seed"],
                "n_items": len(items),
                "orders": list(demands),
                "torch": torch.__version__,
                "transformers": transformers.__version__,
                "elapsed_s": round(time.time() - t0, 1),
            },
            f,
            indent=2,
        )
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
