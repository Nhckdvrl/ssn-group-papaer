#!/usr/bin/env python3
"""Run E19 state substitution on frozen CPC18 explicit/history pairs."""

import argparse
import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from cpc18_common import ROOT, load_problems, make_prompt
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


STATE = json.loads((ROOT / "configs/cpc18_state_substitution.json").read_text())


def prefix(tokenizer, prompt, trace):
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
    )
    if not rendered.rstrip().endswith("<think>"):
        raise ValueError("OLMo Think template no longer opens the reasoning channel")
    return rendered + trace.strip() + "\n</think>\n\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    spec = STATE["model"]
    source = ROOT / STATE["source_result_dir"] / "raw" / "olmo_think_sft.jsonl"
    rows = [json.loads(line) for line in source.open()]
    index = {
        (row["problem"], row["presentation"], row["order"],
         row["history_id"], row["sample_index"]): row
        for row in rows
    }
    problems = {row["id"]: row for row in load_problems()}
    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    ids = label_ids(tokenizer)
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True,
        torch_dtype=torch.bfloat16, attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()
    layers = get_layers(model)
    scan_layers = list(range(0, len(layers), STATE["layer_stride"]))
    if scan_layers[-1] != len(layers) - 1:
        scan_layers.append(len(layers) - 1)

    out = ROOT / STATE["result_dir"]
    out.mkdir(parents=True, exist_ok=True)
    with (out / "raw.jsonl").open("w") as handle:
        for unit in STATE["selected_units"]:
            problem = problems[unit["problem"]]
            history = next(
                value for value in problem["histories"]
                if value["id"] == unit["history_id"]
            )
            explicit_key = (
                unit["problem"], "explicit", unit["order"], None,
                unit["sample_index"],
            )
            history_key = (
                unit["problem"], "history", unit["order"], unit["history_id"],
                unit["sample_index"],
            )
            pair = {"explicit": index[explicit_key], "history": index[history_key]}
            for target_presentation, donor_presentation in [
                ("explicit", "history"), ("history", "explicit")
            ]:
                target = pair[target_presentation]
                donor = pair[donor_presentation]
                target_prompt = make_prompt(
                    problem, target_presentation, unit["order"],
                    history if target_presentation == "history" else None,
                )
                donor_prompt = make_prompt(
                    problem, donor_presentation, unit["order"],
                    history if donor_presentation == "history" else None,
                )
                target_encoded = encode_prefix(
                    tokenizer,
                    prefix(tokenizer, target_prompt, target["stripped_trace"]),
                    args.device,
                )
                donor_encoded = encode_prefix(
                    tokenizer,
                    prefix(tokenizer, donor_prompt, donor["stripped_trace"]),
                    args.device,
                )
                donor_states, donor_logits = collect_donor_states(
                    model, layers, donor_encoded
                )
                with torch.inference_mode():
                    baseline_logits = model(
                        **target_encoded, use_cache=False, logits_to_keep=1
                    ).logits[0, -1]
                baseline_scores = logits_for_labels(baseline_logits, ids)
                donor_scores = logits_for_labels(donor_logits, ids)
                baseline_margin = target_margin(
                    baseline_scores, target["shown_choice"]
                )
                for layer_index in scan_layers:
                    patched_logits = run_with_patch(
                        model, layers[layer_index], target_encoded,
                        donor_states[layer_index]
                    )
                    patched_scores = logits_for_labels(patched_logits, ids)
                    patched_margin = target_margin(
                        patched_scores, target["shown_choice"]
                    )
                    handle.write(json.dumps({
                        **unit,
                        "target_presentation": target_presentation,
                        "donor_presentation": donor_presentation,
                        "target_choice": target["shown_choice"],
                        "donor_choice": donor["shown_choice"],
                        "layer": layer_index,
                        "n_layers": len(layers),
                        "baseline_target_margin": baseline_margin,
                        "patched_target_margin": patched_margin,
                        "donor_shift": baseline_margin - patched_margin,
                        "baseline_prediction": prediction(baseline_scores),
                        "donor_baseline_prediction": prediction(donor_scores),
                        "patched_prediction": prediction(patched_scores),
                        "patched_flipped_to_donor": (
                            prediction(patched_scores) == donor["shown_choice"]
                        ),
                    }) + "\n")
                    handle.flush()
    (out / "scan.json").write_text(json.dumps({
        "model": spec,
        "n_base_decisions": len(STATE["selected_units"]),
        "n_directional_pairs": 2 * len(STATE["selected_units"]),
        "n_layers": len(layers),
        "scan_layers": scan_layers,
        "selection_rule": STATE["selection_rule"],
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
