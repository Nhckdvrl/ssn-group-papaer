#!/usr/bin/env python
"""L13 E01/E02 runner: commitment probes under three task orders.

One model per invocation. Deterministic: label scoring uses log-probabilities,
the context turn uses greedy decoding.
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
from scoring import (  # noqa: E402
    build_candidate_map,
    generate,
    load_model,
    render,
    score_candidates,
)


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "pilot_v1.json"))
    ap.add_argument("--model", required=True, help="model slug from the config")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--suffix", default="", help="suffix for output files")
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
    digit_map = build_candidate_map(tok, probes.LIKELIHOOD_DIGITS)

    sfx = args.suffix
    raw_path = os.path.join(out_dir, f"strict{sfx}.jsonl")
    gen_path = os.path.join(out_dir, f"context_turns{sfx}.jsonl")
    lik_path = os.path.join(out_dir, f"likelihood{sfx}.jsonl")

    with open(raw_path, "w", encoding="utf-8") as raw_f, open(
        gen_path, "w", encoding="utf-8"
    ) as gen_f:
        for order in cfg["task_orders"]:
            task = probes.TASK_ORDERS[order]
            contexts = [None] * len(items)
            if task is not None:
                prompts = [
                    render(tok, [{"role": "user", "content": task.format(passage=it["passage"])}])
                    for it in items
                ]
                contexts = generate(
                    tok,
                    model,
                    prompts,
                    args.device,
                    max_new_tokens=cfg["max_new_tokens"],
                    batch_size=cfg["gen_batch_size"],
                )
                for it, c in zip(items, contexts):
                    gen_f.write(
                        json.dumps(
                            {"item_id": it["item_id"], "task_order": order, "text": c},
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

            flat_prompts, meta = [], []
            for it, ctx in zip(items, contexts):
                for perm_idx, perm in enumerate(probes.PERMUTATIONS):
                    if task is None:
                        msgs = [
                            {
                                "role": "user",
                                "content": probes.strict_prompt(
                                    it["passage"], it["target"], perm
                                ),
                            }
                        ]
                    else:
                        msgs = [
                            {
                                "role": "user",
                                "content": task.format(passage=it["passage"]),
                            },
                            {"role": "assistant", "content": ctx},
                            {
                                "role": "user",
                                "content": probes.strict_followup_prompt(
                                    it["target"], perm
                                ),
                            },
                        ]
                    flat_prompts.append(render(tok, msgs))
                    meta.append((it, perm_idx, perm))

            dists = score_candidates(
                tok,
                model,
                flat_prompts,
                letter_map,
                args.device,
                batch_size=cfg["batch_size"],
            )
            for (it, perm_idx, perm), dist in zip(meta, dists):
                label_probs = {
                    label: dist[letter] for letter, label in zip(letters, perm)
                }
                raw_f.write(
                    json.dumps(
                        {
                            "item_id": it["item_id"],
                            "base_id": it["base_id"],
                            "condition": it["condition"],
                            "gold_strict": it["gold_strict"],
                            "task_order": order,
                            "perm_idx": perm_idx,
                            "probs": label_probs,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            print(f"[{spec['slug']}] {order}: {len(flat_prompts)} scored", flush=True)

    lik_prompts = [
        render(tok, [{"role": "user", "content": probes.likelihood_prompt(it["passage"], it["target"])}])
        for it in items
    ]
    lik = score_candidates(
        tok, model, lik_prompts, digit_map, args.device, batch_size=cfg["batch_size"]
    )
    with open(lik_path, "w", encoding="utf-8") as f:
        for it, dist in zip(items, lik):
            expected = sum(int(d) * p for d, p in dist.items())
            f.write(
                json.dumps(
                    {
                        "item_id": it["item_id"],
                        "base_id": it["base_id"],
                        "condition": it["condition"],
                        "probs": dist,
                        "expected_rating": expected,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    manifest = {
        "config": os.path.relpath(args.config, PROJ),
        "tag": cfg["tag"],
        "model_id": spec["model_id"],
        "family": spec["family"],
        "device": args.device,
        "dtype": cfg["dtype"],
        "seed": cfg["seed"],
        "n_items": len(items),
        "task_orders": cfg["task_orders"],
        "n_permutations": len(probes.PERMUTATIONS),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(out_dir, f"manifest{sfx}.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
