#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/pilot.json").read_text())
RUN = ROOT / "results/pilot_seed29"
SAMPLES_PER_CELL = 4


def expected_choice(prospect, frame):
    values = {
        "A": prospect["loss_a"] * prospect["prob_a"],
        "B": prospect["loss_b"] * prospect["prob_b"],
    }
    return max(values, key=values.get) if frame == "gain" else min(values, key=values.get)


def reasoning_and_separator(continuation):
    before, after = continuation.split("</think>", 1)
    answer = re.search(r"(?<![A-Za-z])([AB])(?![A-Za-z])", after, flags=re.I)
    if answer is None:
        raise ValueError("completed trace has no final A/B answer")
    return before + "</think>", after[: answer.start()]


def cluster_bootstrap(values, groups, rng, draws=5000):
    unique = np.unique(groups)
    sampled = np.empty(draws)
    for draw in range(draws):
        chosen_groups = rng.choice(unique, size=len(unique), replace=True)
        chosen = [rng.choice(values[groups == group]) for group in chosen_groups]
        sampled[draw] = np.mean(chosen)
    return [float(np.quantile(sampled, 0.025)), float(np.quantile(sampled, 0.975))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    spec = CONFIG["models"][2]
    source = RUN / "think_sft/raw.jsonl"
    rows = [json.loads(line) for line in source.open()]
    completed = [row for row in rows if "</think>" in row["continuation"] and row["shown_choice"]]
    by_key = {}
    for row in completed:
        key = (row["prospect"], row["frame"], row["order"])
        by_key.setdefault(key, []).append(row)
    selected = []
    for key, cell_rows in sorted(by_key.items()):
        selected.extend(sorted(cell_rows, key=lambda row: row["sample_index"])[:SAMPLES_PER_CELL])
    if len(selected) != 12 * SAMPLES_PER_CELL:
        raise ValueError(f"need {SAMPLES_PER_CELL} completed traces in every cell; selected {len(selected)}")

    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    tokenizer.padding_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], torch_dtype=torch.bfloat16,
        attn_implementation="sdpa", low_cpu_mem_usage=True,
    ).to(args.device).eval()
    label_ids = [tokenizer.encode(label, add_special_tokens=False)[0] for label in ["A", "B"]]
    prospects = {prospect["id"]: prospect for prospect in CONFIG["prospects"]}
    lookup = {(r["prospect"], r["frame"], r["order"], r["sample_index"]): r for r in completed}

    scored = []
    with torch.inference_mode():
        for row in selected:
            prompt = row["prompt"] if "prompt" in row else None
            if prompt is None:
                from run_model import make_prompt
                prompt = make_prompt(prospects[row["prospect"]], row["frame"], row["order"])
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
            )
            own_reasoning, separator = reasoning_and_separator(row["continuation"])
            other_frame = "loss" if row["frame"] == "gain" else "gain"
            donor = lookup.get((row["prospect"], other_frame, row["order"], row["sample_index"]))
            if donor is None:
                donor_candidates = by_key[(row["prospect"], other_frame, row["order"])]
                donor = sorted(donor_candidates, key=lambda item: item["sample_index"])[0]
            donor_reasoning, _ = reasoning_and_separator(donor["continuation"])
            prefixes = {
                "own_trace": rendered + own_reasoning + separator,
                "zero_trace": rendered.rstrip() + "</think>" + separator,
                "opposite_frame_trace": rendered + donor_reasoning + separator,
            }
            target_underlying = expected_choice(prospects[row["prospect"]], row["frame"])
            target_shown = target_underlying if row["order"] == "ab" else ("B" if target_underlying == "A" else "A")
            for mode, prefix in prefixes.items():
                encoded = tokenizer(prefix, return_tensors="pt", return_token_type_ids=False).to(args.device)
                logits = model(**encoded, use_cache=False).logits[0, -1, label_ids].float().cpu().numpy()
                correct_index = 0 if target_shown == "A" else 1
                margin = float(logits[correct_index] - logits[1 - correct_index])
                scored.append({
                    "prospect": row["prospect"], "frame": row["frame"], "order": row["order"],
                    "sample_index": row["sample_index"], "mode": mode, "target_shown": target_shown,
                    "margin_correct_minus_incorrect": margin, "argmax_correct": bool(margin > 0),
                    "donor_sample_index": donor["sample_index"] if mode == "opposite_frame_trace" else None,
                })

    out = RUN / "reasoning_prefix_intervention"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "raw.jsonl").open("w") as handle:
        for row in scored:
            handle.write(json.dumps(row) + "\n")
    rng = np.random.default_rng(CONFIG["seed"])
    modes = sorted({row["mode"] for row in scored})
    summary = {"model": spec, "source": str(source), "samples_per_cell": SAMPLES_PER_CELL, "modes": {}}
    keyed = {}
    for row in scored:
        key = (row["prospect"], row["frame"], row["order"], row["sample_index"])
        keyed.setdefault(key, {})[row["mode"]] = row["margin_correct_minus_incorrect"]
    groups = np.asarray(["|".join(key[:3]) for key in keyed])
    for mode in modes:
        mode_rows = [row for row in scored if row["mode"] == mode]
        margins = np.asarray([row["margin_correct_minus_incorrect"] for row in mode_rows])
        summary["modes"][mode] = {
            "n": len(mode_rows), "mean_correct_margin": float(margins.mean()),
            "argmax_correct_rate": float(np.mean([row["argmax_correct"] for row in mode_rows])),
        }
    for left, right in [("own_trace", "zero_trace"), ("own_trace", "opposite_frame_trace")]:
        diffs = np.asarray([entry[left] - entry[right] for entry in keyed.values()])
        name = f"{left}_minus_{right}"
        summary[name] = {
            "mean_margin_difference": float(diffs.mean()),
            "cluster_bootstrap_ci95": cluster_bootstrap(diffs, groups, rng),
        }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
