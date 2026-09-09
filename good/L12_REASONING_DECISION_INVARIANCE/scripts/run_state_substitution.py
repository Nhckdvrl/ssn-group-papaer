#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_trajectory_takeover import (
    expected_underlying,
    make_prompt,
    shown_label,
)

ROOT = Path(__file__).resolve().parents[1]
STATE_CONFIG = json.loads((ROOT / "configs/state_substitution.json").read_text())
TRACE_CONFIG = json.loads((ROOT / "configs/trajectory_takeover.json").read_text())


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        return model.transformer.h
    raise RuntimeError("Cannot locate decoder layers for this model architecture.")


def first_hidden(output):
    if torch.is_tensor(output):
        return output
    if isinstance(output, tuple) and output and torch.is_tensor(output[0]):
        return output[0]
    raise RuntimeError(f"Unsupported decoder-layer output type: {type(output)}")


def replace_first_hidden(output, hidden):
    if torch.is_tensor(output):
        return hidden
    if isinstance(output, tuple):
        return (hidden,) + output[1:]
    raise RuntimeError(f"Unsupported decoder-layer output type: {type(output)}")


def label_ids(tokenizer):
    ids = {}
    for label in ["A", "B"]:
        encoded = tokenizer.encode(label, add_special_tokens=False)
        if len(encoded) != 1:
            raise RuntimeError(f"{label} is not a single tokenizer token: {encoded}")
        ids[label] = encoded[0]
    return ids


def logits_for_labels(logits, ids):
    return {
        "A": float(logits[ids["A"]].item()),
        "B": float(logits[ids["B"]].item()),
    }


def target_margin(scores, target):
    other = "B" if target == "A" else "A"
    return scores[target] - scores[other]


def prediction(scores):
    return "A" if scores["A"] > scores["B"] else "B"


def encode_prefix(tokenizer, prefix, device):
    return tokenizer(
        prefix,
        return_tensors="pt",
        return_token_type_ids=False,
    ).to(device)


def collect_donor_states(model, layers, encoded):
    states = {}
    handles = []

    for layer_idx, layer in enumerate(layers):
        def make_hook(idx):
            def hook(_module, _inputs, output):
                hidden = first_hidden(output)
                states[idx] = hidden[:, -1, :].detach().clone()
            return hook
        handles.append(layer.register_forward_hook(make_hook(layer_idx)))

    try:
        with torch.inference_mode():
            logits = model(**encoded, use_cache=False).logits[0, -1]
    finally:
        for handle in handles:
            handle.remove()

    return states, logits


def run_with_patch(model, layer, encoded, donor_state):
    def hook(_module, _inputs, output):
        hidden = first_hidden(output).clone()
        hidden[:, -1, :] = donor_state.to(device=hidden.device, dtype=hidden.dtype)[0]
        return replace_first_hidden(output, hidden)

    handle = layer.register_forward_hook(hook)
    try:
        with torch.inference_mode():
            logits = model(**encoded, use_cache=False).logits[0, -1]
    finally:
        handle.remove()
    return logits


def load_trace_pairs():
    source = ROOT / STATE_CONFIG["source_result_dir"] / "traces.jsonl"
    if not source.exists():
        raise FileNotFoundError(
            f"{source} does not exist. Run scripts/run_trajectory_takeover.sh first."
        )
    rows = [json.loads(line) for line in source.open()]
    valid = {
        (r["prospect"], r["frame"], r["order"], r["sample_index"]): r
        for r in rows
        if r.get("valid_trace") and r.get("stripped_trace")
    }

    pairs = []
    for key, target in sorted(valid.items()):
        prospect, frame, order, sample_index = key
        donor_frame = "loss" if frame == "gain" else "gain"
        donor = valid.get((prospect, donor_frame, order, sample_index))
        if donor is None:
            continue
        pairs.append((target, donor))
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    spec = TRACE_CONFIG["model"]
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
    stride = int(STATE_CONFIG["layer_stride"])
    scan_layers = list(range(0, len(layers), stride))
    if scan_layers[-1] != len(layers) - 1:
        scan_layers.append(len(layers) - 1)

    prospects = {p["id"]: p for p in TRACE_CONFIG["prospects"]}
    pairs = load_trace_pairs()
    if not pairs:
        raise RuntimeError("No matched valid stripped target/donor trace pairs found.")

    out_dir = ROOT / STATE_CONFIG["result_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"

    with raw_path.open("w") as handle:
        for target, donor in pairs:
            prospect = target["prospect"]
            frame = target["frame"]
            donor_frame = donor["frame"]
            order = target["order"]
            p = prospects[prospect]

            target_choice = shown_label(expected_underlying(p, frame), order)
            donor_choice = shown_label(expected_underlying(p, donor_frame), order)
            if target_choice == donor_choice:
                raise ValueError(
                    f"{prospect} {order}: donor and target imply the same displayed choice"
                )

            target_prompt = make_prompt(p, frame, order)
            donor_prompt = make_prompt(p, donor_frame, order)
            target_rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": target_prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
            donor_rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": donor_prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
            target_prefix = (
                target_rendered + target["stripped_trace"].strip() + "\n</think>\n"
            )
            donor_prefix = (
                donor_rendered + donor["stripped_trace"].strip() + "\n</think>\n"
            )

            target_encoded = encode_prefix(tokenizer, target_prefix, args.device)
            donor_encoded = encode_prefix(tokenizer, donor_prefix, args.device)

            donor_states, donor_logits = collect_donor_states(
                model, layers, donor_encoded
            )
            with torch.inference_mode():
                base_logits = model(
                    **target_encoded, use_cache=False
                ).logits[0, -1]

            base_scores = logits_for_labels(base_logits, ids)
            donor_scores = logits_for_labels(donor_logits, ids)
            base_margin = target_margin(base_scores, target_choice)

            for layer_idx in scan_layers:
                patched_logits = run_with_patch(
                    model,
                    layers[layer_idx],
                    target_encoded,
                    donor_states[layer_idx],
                )
                patched_scores = logits_for_labels(patched_logits, ids)
                patched_margin = target_margin(patched_scores, target_choice)

                handle.write(json.dumps({
                    "prospect": prospect,
                    "frame": frame,
                    "donor_frame": donor_frame,
                    "order": order,
                    "sample_index": target["sample_index"],
                    "layer": layer_idx,
                    "n_layers": len(layers),
                    "target_choice": target_choice,
                    "donor_choice": donor_choice,
                    "baseline_target_margin": base_margin,
                    "patched_target_margin": patched_margin,
                    "donor_shift": base_margin - patched_margin,
                    "baseline_prediction": prediction(base_scores),
                    "patched_prediction": prediction(patched_scores),
                    "donor_baseline_prediction": prediction(donor_scores),
                    "patched_flipped_to_donor": prediction(patched_scores) == donor_choice,
                    "target_remaining_decision_marker": target.get(
                        "remaining_decision_marker", False
                    ),
                    "donor_remaining_decision_marker": donor.get(
                        "remaining_decision_marker", False
                    ),
                }) + "\n")
                handle.flush()

    (out_dir / "model.json").write_text(json.dumps(spec, indent=2) + "\n")
    (out_dir / "scan.json").write_text(json.dumps({
        "n_layers": len(layers),
        "scan_layers": scan_layers,
        "n_trace_pairs": len(pairs),
        "source_result_dir": STATE_CONFIG["source_result_dir"],
    }, indent=2) + "\n")
    print(raw_path)


if __name__ == "__main__":
    main()
