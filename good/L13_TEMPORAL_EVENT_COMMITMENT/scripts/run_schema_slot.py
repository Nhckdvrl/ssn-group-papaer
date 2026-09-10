#!/usr/bin/env python
"""L13 E06b: forced-slot measurement of the three-state schema.

The model is given the structure-building task with an explicit `unresolved`
status code, and its own table row for the target event is teacher-forced up to
the status slot. We then score the three status codes directly. This removes
parsing noise and yields a probability directly comparable to the direct probe
P1, answering: given a first-class slot for `unresolved`, does the model use it?

Status codes are neutral letters with a permuted legend (6 permutations), so no
mnemonic or position bias can carry the result.
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


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(PROJ, "configs", "e06_schema.json"))
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
    letters = probes.SCHEMA_CODE_LETTERS
    letter_map = build_candidate_map(tok, letters)

    prompts, meta = [], []
    for it in items:
        for perm_idx, perm in enumerate(probes.SCHEMA_PERMUTATIONS):
            msgs = [
                {
                    "role": "user",
                    "content": probes.schema_slot_task(it["passage"], perm),
                }
            ]
            # teacher-force the model's own table row up to the status slot
            text = render(tok, msgs) + probes.schema_slot_prefix(it["target"])
            prompts.append(text)
            meta.append((it, perm_idx, perm))

    dists = score_candidates(
        tok, model, prompts, letter_map, args.device, batch_size=cfg["batch_size"]
    )

    out_path = os.path.join(out_dir, "schema_slot.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for (it, perm_idx, perm), dist in zip(meta, dists):
            f.write(
                json.dumps(
                    {
                        "item_id": it["item_id"],
                        "base_id": it["base_id"],
                        "condition": it["condition"],
                        "gold_strict": it["gold_strict"],
                        "perm_idx": perm_idx,
                        "probs": {
                            status: dist[letter]
                            for letter, status in zip(letters, perm)
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    with open(os.path.join(out_dir, "manifest_schema.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_id": spec["model_id"],
                "family": spec["family"],
                "dtype": cfg["dtype"],
                "seed": cfg["seed"],
                "n_items": len(items),
                "n_permutations": len(probes.SCHEMA_PERMUTATIONS),
                "torch": torch.__version__,
                "transformers": transformers.__version__,
                "elapsed_s": round(time.time() - t0, 1),
            },
            f,
            indent=2,
        )
    print(f"[{spec['slug']}] schema slot: {len(prompts)} scored in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
