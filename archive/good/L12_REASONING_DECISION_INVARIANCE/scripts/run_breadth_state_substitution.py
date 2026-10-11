#!/usr/bin/env python3
"""Replicate E08 on a preregistered stratified subset of E10 decisions."""

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_state_substitution import (
    collect_donor_states,
    encode_prefix,
    get_layers,
    label_ids,
    logits_for_labels,
    prediction,
    run_with_patch,
    target_margin,
)
from run_trajectory_takeover import make_prompt, shown_label


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/breadth.json").read_text())
STATE = json.loads((ROOT / "configs/breadth_state_substitution.json").read_text())


def load_decisions():
    with (ROOT / CONFIG["output"]).open() as handle:
        rows = [json.loads(line) for line in handle]
    return {
        row["id"]: {
            "id": row["id"],
            "loss_a": row["amount_a"],
            "prob_a": row["prob_a"],
            "loss_b": row["amount_b"],
            "prob_b": row["prob_b"],
            "gain_optimal": row["gain_optimal"],
            "loss_optimal": row["loss_optimal"],
            "ev_gap_stratum": row["ev_gap_stratum"],
            "probability_gap_stratum": row["probability_gap_stratum"],
            "payoff_scale": row["payoff_scale"],
        }
        for row in rows
    }


def load_pairs():
    path = ROOT / CONFIG["result_dir"] / "think_sft/raw.jsonl"
    with path.open() as handle:
        rows = [json.loads(line) for line in handle]
    valid = {
        (row["prospect"], row["frame"], row["order"], row["sample_index"]): row
        for row in rows
        if row["valid"] and row.get("stripped_trace")
    }
    pairs = []
    for prospect in STATE["selected_decisions"]:
        matches = [
            sample for sample in range(CONFIG["samples_per_cell"])
            if (prospect, "gain", STATE["order"], sample) in valid
            and (prospect, "loss", STATE["order"], sample) in valid
        ]
        if not matches:
            raise RuntimeError(f"No valid matched traces for selected decision {prospect}")
        sample = min(matches)
        gain = valid[(prospect, "gain", STATE["order"], sample)]
        loss = valid[(prospect, "loss", STATE["order"], sample)]
        pairs.extend([(gain, loss), (loss, gain)])
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    spec = next(item for item in CONFIG["models"] if item["branch"] == "think_sft")
    decisions = load_decisions()
    pairs = load_pairs()
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    ids = label_ids(tokenizer)
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"],
        revision=spec["revision"],
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()
    layers = get_layers(model)
    scan_layers = list(range(0, len(layers), STATE["layer_stride"]))
    if scan_layers[-1] != len(layers) - 1:
        scan_layers.append(len(layers) - 1)

    out = ROOT / STATE["result_dir"]
    out.mkdir(parents=True, exist_ok=True)
    with (out / "raw.jsonl").open("w") as handle:
        for target, donor in pairs:
            decision = decisions[target["prospect"]]
            order = target["order"]
            target_choice = shown_label(
                decision[f"{target['frame']}_optimal"], order
            )
            donor_choice = shown_label(
                decision[f"{donor['frame']}_optimal"], order
            )
            target_rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": make_prompt(
                    decision, target["frame"], order
                )}],
                tokenize=False,
                add_generation_prompt=True,
            )
            donor_rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": make_prompt(
                    decision, donor["frame"], order
                )}],
                tokenize=False,
                add_generation_prompt=True,
            )
            target_encoded = encode_prefix(
                tokenizer,
                target_rendered + target["stripped_trace"].strip() + "\n</think>\n\n",
                args.device,
            )
            donor_encoded = encode_prefix(
                tokenizer,
                donor_rendered + donor["stripped_trace"].strip() + "\n</think>\n\n",
                args.device,
            )
            donor_states, donor_logits = collect_donor_states(
                model, layers, donor_encoded
            )
            with torch.inference_mode():
                baseline_logits = model(
                    **target_encoded, use_cache=False
                ).logits[0, -1]
            baseline_scores = logits_for_labels(baseline_logits, ids)
            donor_scores = logits_for_labels(donor_logits, ids)
            baseline_margin = target_margin(baseline_scores, target_choice)

            for layer_index in scan_layers:
                patched_logits = run_with_patch(
                    model,
                    layers[layer_index],
                    target_encoded,
                    donor_states[layer_index],
                )
                patched_scores = logits_for_labels(patched_logits, ids)
                patched_margin = target_margin(patched_scores, target_choice)
                handle.write(json.dumps({
                    "prospect": target["prospect"],
                    "frame": target["frame"],
                    "donor_frame": donor["frame"],
                    "order": order,
                    "sample_index": target["sample_index"],
                    "layer": layer_index,
                    "n_layers": len(layers),
                    "target_choice": target_choice,
                    "donor_choice": donor_choice,
                    "baseline_target_margin": baseline_margin,
                    "patched_target_margin": patched_margin,
                    "donor_shift": baseline_margin - patched_margin,
                    "baseline_prediction": prediction(baseline_scores),
                    "donor_baseline_prediction": prediction(donor_scores),
                    "patched_prediction": prediction(patched_scores),
                    "patched_flipped_to_donor": (
                        prediction(patched_scores) == donor_choice
                    ),
                    "ev_gap_stratum": decision["ev_gap_stratum"],
                    "probability_gap_stratum": decision[
                        "probability_gap_stratum"
                    ],
                    "payoff_scale": decision["payoff_scale"],
                }) + "\n")
                handle.flush()
    (out / "scan.json").write_text(json.dumps({
        "n_base_decisions": len(STATE["selected_decisions"]),
        "n_directional_pairs": len(pairs),
        "n_layers": len(layers),
        "scan_layers": scan_layers,
        "selection_rule": STATE["selection_rule"],
        "sample_rule": STATE["sample_rule"],
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
