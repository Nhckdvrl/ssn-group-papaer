#!/usr/bin/env python3
"""Run E21 form-by-evidence pre-answer residual-state substitution."""

import argparse
import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from cpc18_form_evidence_common import ROOT, load_problems, make_prompt
from cpc18_common import shown_choice
from run_state_substitution import (
    collect_donor_states,
    encode_prefix,
    get_layers,
    label_ids,
    logits_for_labels,
    run_with_patch,
)


STATE = json.loads((ROOT / "configs/cpc18_selective_state.json").read_text())


def prefix(tokenizer, prompt, trace):
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
    )
    if not rendered.rstrip().endswith("<think>"):
        raise ValueError("OLMo Think template no longer opens the reasoning channel")
    return rendered + trace.strip() + "\n</think>\n\n"


def probability_underlying_a(scores, order):
    probabilities = torch.softmax(
        torch.tensor([scores["A"], scores["B"]]), dim=0
    )
    return float(probabilities[0 if shown_choice("A", order) == "A" else 1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--num-shards", type=int)
    args = parser.parse_args()
    if (args.shard_index is None) != (args.num_shards is None):
        parser.error("--shard-index and --num-shards must be provided together")

    units = STATE["selected_units"]
    if args.num_shards is not None:
        units = [
            unit for index, unit in enumerate(units)
            if index % args.num_shards == args.shard_index
        ]
    source = ROOT / STATE["source_result_dir"] / "raw" / "olmo_think_sft.jsonl"
    rows = [json.loads(line) for line in source.open()]
    index = {
        (row["problem"], row["form"], row["order"], row["evidence_choice"], row["sample_index"]): row
        for row in rows
    }
    problems = {row["id"]: row for row in load_problems()}
    spec = STATE["model"]
    tokenizer = AutoTokenizer.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    labels = label_ids(tokenizer)
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"], revision=spec["revision"], local_files_only=True,
        torch_dtype=torch.bfloat16, attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()
    layers = get_layers(model)
    if max(STATE["scan_layers"]) >= len(layers):
        raise ValueError("Frozen E21 layer index exceeds model depth")

    output = ROOT / STATE["result_dir"]
    output.mkdir(parents=True, exist_ok=True)
    suffix = (
        f".shard{args.shard_index}of{args.num_shards}"
        if args.num_shards is not None else ""
    )
    with (output / f"raw{suffix}.jsonl").open("w") as handle:
        for unit in units:
            problem = problems[unit["problem"]]
            evidence = {row["evidence_choice"]: row for row in problem["evidence"]}
            encoded = {}
            for form in ("raw", "summary"):
                for choice in ("A", "B"):
                    sample = unit["sample_indices"][form][choice]
                    row = index[(unit["problem"], form, unit["order"], choice, sample)]
                    prompt = make_prompt(problem, evidence[choice], form, unit["order"])
                    encoded[form, choice] = encode_prefix(
                        tokenizer,
                        prefix(tokenizer, prompt, row["stripped_trace"]),
                        args.device,
                    )
            donor_states = {}
            for donor_key, donor_encoded in encoded.items():
                donor_states[donor_key], _ = collect_donor_states(
                    model, layers, donor_encoded
                )
            for (target_form, target_evidence), target_encoded in encoded.items():
                with torch.inference_mode():
                    baseline_logits = model(
                        **target_encoded, use_cache=False, logits_to_keep=1
                    ).logits[0, -1]
                baseline_scores = logits_for_labels(baseline_logits, labels)
                baseline_p_a = probability_underlying_a(
                    baseline_scores, unit["order"]
                )
                for donor_form in ("raw", "summary"):
                    for donor_evidence in ("A", "B"):
                        for layer_index in STATE["scan_layers"]:
                            logits = run_with_patch(
                                model, layers[layer_index], target_encoded,
                                donor_states[donor_form, donor_evidence][layer_index],
                            )
                            scores = logits_for_labels(logits, labels)
                            p_a = probability_underlying_a(scores, unit["order"])
                            handle.write(json.dumps({
                                "problem": unit["problem"],
                                "source_split": unit["source_split"],
                                "strength_quartile": unit["strength_quartile"],
                                "order": unit["order"],
                                "target_form": target_form,
                                "target_evidence": target_evidence,
                                "donor_form": donor_form,
                                "donor_evidence": donor_evidence,
                                "layer": layer_index,
                                "n_layers": len(layers),
                                "baseline_p_underlying_a": baseline_p_a,
                                "patched_p_underlying_a": p_a,
                            }) + "\n")
                            handle.flush()
    (output / f"scan{suffix}.json").write_text(json.dumps({
        "model": spec,
        "n_base_decisions": len(units),
        "scan_layers": STATE["scan_layers"],
        "n_rows": len(units) * 4 * 4 * len(STATE["scan_layers"]),
        "shard_index": args.shard_index,
        "num_shards": args.num_shards,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
