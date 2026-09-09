#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_trajectory_takeover import expected_underlying, make_prompt, shown_label

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/control_reorganization.json").read_text())
TRACE_CONFIG = json.loads((ROOT / "configs/trajectory_takeover.json").read_text())


def load_units():
    path = ROOT / CONFIG["source_result_dir"] / "traces.jsonl"
    rows = [json.loads(line) for line in path.open()]
    valid = {
        (row["prospect"], row["frame"], row["order"], row["sample_index"]): row
        for row in rows
        if row.get("valid_trace") and row.get("stripped_trace")
    }
    units = []
    for prospect in sorted({key[0] for key in valid}):
        for order in ["ab", "ba"]:
            sample_ids = sorted({
                key[3] for key in valid
                if key[0] == prospect and key[2] == order
                and (prospect, "gain", order, key[3]) in valid
                and (prospect, "loss", order, key[3]) in valid
            })
            for sample_id in sample_ids:
                units.append({
                    "prospect": prospect,
                    "order": order,
                    "sample_index": sample_id,
                    "gain_trace": valid[(prospect, "gain", order, sample_id)]["stripped_trace"],
                    "loss_trace": valid[(prospect, "loss", order, sample_id)]["stripped_trace"],
                })
    return units


def answer_prefix(tokenizer, branch, prompt, trace):
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
    )
    if branch == "think_sft":
        if not rendered.rstrip().endswith("<think>"):
            raise ValueError("Think template does not end in <think>")
        return rendered + trace.strip() + "\n</think>\n\n"
    return rendered + trace.strip() + "\n\n"


def bootstrap(values, prospects, seed):
    values = np.asarray(values, dtype=float)
    prospects = np.asarray(prospects)
    unique = np.unique(prospects)
    rng = np.random.default_rng(seed)
    draws = np.empty(CONFIG["bootstrap_samples"])
    for index in range(len(draws)):
        groups = rng.choice(unique, len(unique), replace=True)
        draws[index] = np.mean([
            rng.choice(values[prospects == group]) for group in groups
        ])
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def summarize(rows):
    by_model = {}
    unit_keys = sorted({
        (row["prospect"], row["order"], row["sample_index"], row["branch"])
        for row in rows
    })
    effects = []
    for prospect, order, sample_index, branch in unit_keys:
        part = [row for row in rows if (
            row["prospect"], row["order"], row["sample_index"], row["branch"]
        ) == (prospect, order, sample_index, branch)]
        cell = {(row["prompt_frame"], row["trajectory_frame"]): row["p_gain_choice"] for row in part}
        trajectory_effect = np.mean([
            cell[(prompt_frame, "gain")] - cell[(prompt_frame, "loss")]
            for prompt_frame in ["gain", "loss"]
        ])
        prompt_effect = np.mean([
            cell[("gain", trajectory_frame)] - cell[("loss", trajectory_frame)]
            for trajectory_frame in ["gain", "loss"]
        ])
        effects.append({
            "prospect": prospect, "order": order, "sample_index": sample_index,
            "branch": branch, "trajectory_control": float(trajectory_effect),
            "prompt_control": float(prompt_effect),
            "trajectory_minus_prompt": float(trajectory_effect - prompt_effect),
        })
    for branch in sorted({row["branch"] for row in effects}):
        part = [row for row in effects if row["branch"] == branch]
        by_model[branch] = {}
        for offset, metric in enumerate(["trajectory_control", "prompt_control", "trajectory_minus_prompt"]):
            values = [row[metric] for row in part]
            by_model[branch][metric] = {
                "mean_probability_effect": float(np.mean(values)),
                "prospect_cluster_bootstrap_ci95": bootstrap(
                    values, [row["prospect"] for row in part], CONFIG["seed"] + offset
                ),
                "per_prospect": {
                    prospect: float(np.mean([
                        row[metric] for row in part if row["prospect"] == prospect
                    ]))
                    for prospect in sorted({row["prospect"] for row in part})
                },
            }
    paired = []
    for key in sorted({(row["prospect"], row["order"], row["sample_index"]) for row in effects}):
        pair = {row["branch"]: row for row in effects if (
            row["prospect"], row["order"], row["sample_index"]
        ) == key}
        if set(pair) == {"instruct_sft", "think_sft"}:
            paired.append({
                "prospect": key[0],
                "trajectory_control_difference": pair["think_sft"]["trajectory_control"] - pair["instruct_sft"]["trajectory_control"],
                "control_reorganization_difference": pair["think_sft"]["trajectory_minus_prompt"] - pair["instruct_sft"]["trajectory_minus_prompt"],
            })
    bridge = {}
    for offset, metric in enumerate(["trajectory_control_difference", "control_reorganization_difference"]):
        values = [row[metric] for row in paired]
        bridge[metric] = {
            "mean_probability_effect": float(np.mean(values)),
            "prospect_cluster_bootstrap_ci95": bootstrap(
                values, [row["prospect"] for row in paired], CONFIG["seed"] + 10 + offset
            ),
        }
    return effects, {"models": by_model, "think_minus_instruct": bridge}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    units = load_units()
    prospects = {item["id"]: item for item in TRACE_CONFIG["prospects"]}
    rows = []
    out = ROOT / CONFIG["result_dir"]
    out.mkdir(parents=True, exist_ok=True)
    for spec in CONFIG["models"]:
        tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        label_ids = [tokenizer.encode(label, add_special_tokens=False)[0] for label in ["A", "B"]]
        model = AutoModelForCausalLM.from_pretrained(
            spec["id"], revision=spec["revision"], torch_dtype=torch.bfloat16,
            attn_implementation="sdpa", low_cpu_mem_usage=True,
        ).to(args.device).eval()
        with torch.inference_mode():
            for unit in units:
                p = prospects[unit["prospect"]]
                gain_choice = shown_label(expected_underlying(p, "gain"), unit["order"])
                gain_index = 0 if gain_choice == "A" else 1
                for prompt_frame in ["gain", "loss"]:
                    prompt = make_prompt(p, prompt_frame, unit["order"])
                    for trajectory_frame in ["gain", "loss"]:
                        prefix = answer_prefix(
                            tokenizer, spec["branch"], prompt, unit[f"{trajectory_frame}_trace"]
                        )
                        encoded = tokenizer(prefix, return_tensors="pt", return_token_type_ids=False).to(args.device)
                        logits = model(**encoded, use_cache=False).logits[0, -1, label_ids].float()
                        p_gain = float(torch.softmax(logits, dim=0)[gain_index].item())
                        rows.append({
                            "branch": spec["branch"], "prospect": unit["prospect"],
                            "order": unit["order"], "sample_index": unit["sample_index"],
                            "prompt_frame": prompt_frame, "trajectory_frame": trajectory_frame,
                            "gain_choice": gain_choice, "p_gain_choice": p_gain,
                        })
        del model
        torch.cuda.empty_cache()
    effects, summary = summarize(rows)
    summary.update({
        "design": "L12-E09 matched prompt-by-trajectory causal-control factorial",
        "n_trace_pairs": len(units), "n_scored_prefixes": len(rows),
        "probability_reference": "displayed choice optimal in the gain frame",
        "template_scope": "each sibling checkpoint's native answer transition",
    })
    for name, payload in [("raw.jsonl", rows), ("unit_effects.jsonl", effects)]:
        with (out / name).open("w") as handle:
            for row in payload:
                handle.write(json.dumps(row) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
