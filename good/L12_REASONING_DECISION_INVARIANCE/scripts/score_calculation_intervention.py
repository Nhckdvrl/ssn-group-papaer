#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_model import make_prompt

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/pilot.json").read_text())
RUN = ROOT / "results/pilot_seed29/calculation_intervention"


def bootstrap(values, groups, rng, draws=5000):
    unique = np.unique(groups)
    samples = []
    for _ in range(draws):
        chosen = rng.choice(unique, len(unique), replace=True)
        samples.append(np.mean([rng.choice(values[groups == group]) for group in chosen]))
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    spec = CONFIG["models"][2]
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], torch_dtype=torch.bfloat16,
        attn_implementation="sdpa", low_cpu_mem_usage=True,
    ).to(args.device).eval()
    label_ids = [tokenizer.encode(label, add_special_tokens=False)[0] for label in ["A", "B"]]
    rows = []
    with torch.inference_mode():
        for prospect in CONFIG["prospects"]:
            values = {
                "A": prospect["loss_a"] * prospect["prob_a"],
                "B": prospect["loss_b"] * prospect["prob_b"],
            }
            for frame in CONFIG["frames"]:
                target = max(values, key=values.get) if frame == "gain" else min(values, key=values.get)
                rule = "prefer the larger expected magnitude" if frame == "gain" else "prefer the smaller expected loss magnitude"
                for order in CONFIG["orders"]:
                    identities = ["A", "B"] if order == "ab" else ["B", "A"]
                    shown_target = target if order == "ab" else ("B" if target == "A" else "A")
                    first, second = values[identities[0]], values[identities[1]]
                    prompt = make_prompt(prospect, frame, order)
                    rendered = tokenizer.apply_chat_template(
                        [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
                    )
                    traces = {
                        "correct_calculation": (
                            f"The two expected magnitudes in display order are {first:g} and {second:g}. "
                            f"The decision rule is to {rule}."
                        ),
                        "swapped_calculation": (
                            f"The two expected magnitudes in display order are {second:g} and {first:g}. "
                            f"The decision rule is to {rule}."
                        ),
                        "rule_only": f"Compute amount times probability for both displayed options, then {rule}.",
                    }
                    for mode, trace in traces.items():
                        if " A" in trace or " B" in trace:
                            raise ValueError("controlled trace must not name an answer label")
                        prefix = rendered + trace + "</think>\n\n"
                        encoded = tokenizer(prefix, return_tensors="pt", return_token_type_ids=False).to(args.device)
                        logits = model(**encoded, use_cache=False).logits[0, -1, label_ids].float().cpu().numpy()
                        correct_index = 0 if shown_target == "A" else 1
                        margin = float(logits[correct_index] - logits[1 - correct_index])
                        rows.append({
                            "prospect": prospect["id"], "frame": frame, "order": order, "mode": mode,
                            "target_shown": shown_target, "margin_correct_minus_incorrect": margin,
                            "argmax_correct": bool(margin > 0), "trace": trace,
                        })
    RUN.mkdir(parents=True, exist_ok=True)
    with (RUN / "raw.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    report = {"model": spec, "n_stimuli": 12, "answer_labels_absent_from_traces": True, "modes": {}}
    for mode in sorted({row["mode"] for row in rows}):
        selected = [row for row in rows if row["mode"] == mode]
        margins = np.asarray([row["margin_correct_minus_incorrect"] for row in selected])
        report["modes"][mode] = {
            "mean_correct_margin": float(margins.mean()),
            "argmax_correct_rate": float(np.mean([row["argmax_correct"] for row in selected])),
        }
    keyed = {}
    for row in rows:
        key = (row["prospect"], row["frame"], row["order"])
        keyed.setdefault(key, {})[row["mode"]] = row["margin_correct_minus_incorrect"]
    groups = np.asarray([key[0] for key in keyed])
    rng = np.random.default_rng(CONFIG["seed"])
    for left, right in [("correct_calculation", "rule_only"), ("correct_calculation", "swapped_calculation")]:
        diffs = np.asarray([entry[left] - entry[right] for entry in keyed.values()])
        report[f"{left}_minus_{right}"] = {
            "mean_margin_difference": float(diffs.mean()),
            "prospect_cluster_bootstrap_ci95": bootstrap(diffs, groups, rng),
        }
    (RUN / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
