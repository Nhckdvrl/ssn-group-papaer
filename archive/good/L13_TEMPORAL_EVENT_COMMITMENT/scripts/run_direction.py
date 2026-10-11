#!/usr/bin/env python
"""L13 E21 — matched-format test of the causal direction between the model's
own judgement text and its own extraction text.

Both prior turns are teacher-forced into one-line-per-event format, so form is
held constant and content is identical across models.

Direction A: prior = correct status lines  -> measure extraction (does it stop?)
Direction B: prior = asserting list lines   -> measure judgement (does it move?)
Controls   : no prior turn; a correct list that omits the unlicensed event.
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
from scoring import build_candidate_map, generate, load_model, render, score_candidates  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--condition", default="before_post")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    spec = next(m for m in cfg["models"] if m["slug"] == args.model)
    items = [
        j
        for j in (json.loads(l) for l in open(os.path.join(PROJ, cfg["stimuli"]), encoding="utf-8"))
        if j["condition"] == args.condition
    ]
    out_dir = os.path.join(PROJ, "results", cfg["tag"], spec["slug"])
    os.makedirs(out_dir, exist_ok=True)

    torch.manual_seed(cfg["seed"])
    t0 = time.time()
    tok, model = load_model(spec["model_id"], args.device, dtype=cfg["dtype"])
    letters = probes.LETTERS[:3]
    letter_map = build_candidate_map(tok, letters)

    rows = []

    # ---- Direction A: correct status text -> extraction -------------------
    for ctx_kind in ("none", "status_correct"):
        prompts = []
        for it in items:
            if ctx_kind == "none":
                msgs = [{"role": "user", "content": probes.E21_LIST_TASK.format(passage=it["passage"])}]
            else:
                msgs = [
                    {"role": "user", "content": probes.E21_STATUS_TASK.format(passage=it["passage"])},
                    {"role": "assistant",
                     "content": probes.e21_context("status_correct", it["target"], it["main_event"])},
                    {"role": "user", "content": probes.E21_FOLLOWUP_LIST},
                ]
            prompts.append(render(tok, msgs))
        gens = generate(tok, model, prompts, args.device,
                        max_new_tokens=cfg["max_new_tokens"], batch_size=cfg["gen_batch_size"])
        for it, g in zip(items, gens):
            rows.append({"item_id": it["item_id"], "direction": "A_status_to_extraction",
                         "context": ctx_kind, "text": g,
                         "instantiated": output_asserts_target(g, it["target"])})
        print(f"[{spec['slug']}] A/{ctx_kind}: {len(prompts)} generated", flush=True)

    # ---- Direction B: asserting list text -> judgement --------------------
    for ctx_kind in ("none", "list_asserting", "list_correct"):
        flat, meta = [], []
        for it in items:
            for pi, perm in enumerate(probes.PERMUTATIONS):
                if ctx_kind == "none":
                    msgs = [{"role": "user",
                             "content": probes.strict_prompt(it["passage"], it["target"], perm)}]
                else:
                    msgs = [
                        {"role": "user", "content": probes.E21_LIST_TASK.format(passage=it["passage"])},
                        {"role": "assistant",
                         "content": probes.e21_context(ctx_kind, it["target"], it["main_event"])},
                        {"role": "user", "content": probes.strict_followup_prompt(it["target"], perm)},
                    ]
                flat.append(render(tok, msgs))
                meta.append((it, pi, perm))
        dists = score_candidates(tok, model, flat, letter_map, args.device, batch_size=cfg["batch_size"])
        for (it, pi, perm), d in zip(meta, dists):
            rows.append({"item_id": it["item_id"], "direction": "B_list_to_judgement",
                         "context": ctx_kind, "perm_idx": pi,
                         "probs": {lab: d[L] for L, lab in zip(letters, perm)}})
        print(f"[{spec['slug']}] B/{ctx_kind}: {len(flat)} scored", flush=True)

    with open(os.path.join(out_dir, "direction.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[{spec['slug']}] done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
