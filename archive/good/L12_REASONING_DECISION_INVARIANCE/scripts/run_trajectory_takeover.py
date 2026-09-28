#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/trajectory_takeover.json").read_text())

BARE_LABEL = re.compile(r"^\s*(?:(?i:option)\s+)?[AB]\s*[.!]?$")
CONCLUSION_LABEL = re.compile(
    r"^\s*(?i:therefore|thus|hence|so)[,:]?\s*(?:(?i:option)\s+)?[AB]\s*[.!]?$",
)


def decision_labels(segment):
    labels = {
        match.upper()
        for match in re.findall(r"\b(?:option\s+|EV_?)([AB])\b", segment, flags=re.I)
    }
    labels.update(re.findall(r"(?<![A-Za-z_])([AB])(?![A-Za-z_])", segment))
    return labels


def is_decision_segment(segment):
    if BARE_LABEL.match(segment) or CONCLUSION_LABEL.match(segment):
        return True
    labels = decision_labels(segment)
    if not labels:
        return False
    planning = re.search(
        r"\b(?:choose|select|decide)\s+between\b|\bwhich\s+option\b.{0,80}\bbetween\b"
        r"|\bwhether\s+to\b.{0,80}\b(?:A|B)\b",
        segment,
        flags=re.I,
    )
    directed_relation = re.search(
        r"\b(?:higher|lower|better|worse)\s+than\b|\bprefer\b.{0,80}\bover\b"
        r"|\b(?:rather than|instead of)\b",
        segment,
        flags=re.I,
    )
    if planning and not directed_relation:
        return False
    if directed_relation:
        return True
    if len(labels) > 1 and not re.search(
        r"\b(over|rather than|instead of)\b", segment, flags=re.I
    ):
        return False
    if re.search(r"\b(better|worse|optimal|preferred)\b", segment, flags=re.I):
        return True
    if re.search(r"\b(higher|lower)\b", segment, flags=re.I) and re.search(
        r"\b(expected|EV|value|payoff|return|utility)\b", segment, flags=re.I
    ):
        return True
    return bool(re.search(
        r"\b(choose|select|prefer|pick|go with|answer|choice)\b",
        segment,
        flags=re.I,
    ))


def option_text(p, frame, identity):
    verb = "Gain" if frame == "gain" else "Lose"
    amount = p[f"loss_{identity.lower()}"]
    probability = p[f"prob_{identity.lower()}"]
    if probability == 1.0:
        return f"{verb} {amount} with certainty."
    return f"{verb} {amount} with probability {probability:.2f}; otherwise 0."


def make_prompt(p, frame, order):
    identities = ["A", "B"] if order == "ab" else ["B", "A"]
    shown = [option_text(p, frame, identity) for identity in identities]
    return (
        "You will be provided with two options with different payoffs and uncertainties.\n"
        "Respond your choice with 'A' or 'B' only.\n\n"
        f"Option A: {shown[0]}\n"
        f"Option B: {shown[1]}"
    )


def expected_underlying(p, frame):
    ev = {
        "A": p["loss_a"] * p["prob_a"],
        "B": p["loss_b"] * p["prob_b"],
    }
    return max(ev, key=ev.get) if frame == "gain" else min(ev, key=ev.get)


def shown_label(underlying, order):
    if order == "ab":
        return underlying
    return "B" if underlying == "A" else "A"


def split_trace(continuation):
    if "</think>" not in continuation:
        return None
    return continuation.split("</think>", 1)[0].replace("<think>", "").strip()


def strip_terminal_conclusion(trace):
    parts = [
        x.strip()
        for x in re.split(r"(?<=[.!?])\s+|\n+", trace.strip())
        if x.strip()
    ]
    first_commitment = next(
        (index for index, part in enumerate(parts) if is_decision_segment(part)),
        None,
    )
    if first_commitment is None:
        return " ".join(parts).strip(), []
    stripped = " ".join(parts[:first_commitment]).strip()
    return stripped, parts[first_commitment:]


def next_token_margin(model, tokenizer, device, prefix, expected):
    a_ids = tokenizer.encode("A", add_special_tokens=False)
    b_ids = tokenizer.encode("B", add_special_tokens=False)
    if len(a_ids) != 1 or len(b_ids) != 1:
        raise RuntimeError("A/B are not single tokenizer tokens; use sequence scoring instead.")
    batch = tokenizer(prefix, return_tensors="pt", return_token_type_ids=False).to(device)
    with torch.inference_mode():
        logits = model(**batch).logits[0, -1]
    a = float(logits[a_ids[0]].item())
    b = float(logits[b_ids[0]].item())
    margin = a - b if expected == "A" else b - a
    prediction = "A" if a > b else "B"
    return margin, prediction, a, b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()

    spec = CONFIG["model"]
    tokenizer = AutoTokenizer.from_pretrained(spec["id"], revision=spec["revision"])
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        spec["id"],
        revision=spec["revision"],
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).to(args.device).eval()

    out_dir = ROOT / CONFIG["result_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"
    trace_path = out_dir / "traces.jsonl"

    cells = []
    rendered_by_key = {}
    for p in CONFIG["prospects"]:
        for frame in CONFIG["frames"]:
            for order in CONFIG["orders"]:
                key = (p["id"], frame, order)
                prompt = make_prompt(p, frame, order)
                rendered = tokenizer.apply_chat_template(
                    [{"role": "user", "content": prompt}],
                    tokenize=False,
                    add_generation_prompt=True,
                )
                cells.append((p, frame, order, prompt, rendered))
                rendered_by_key[key] = rendered

    for p in CONFIG["prospects"]:
        for order in CONFIG["orders"]:
            gain = shown_label(expected_underlying(p, "gain"), order)
            loss = shown_label(expected_underlying(p, "loss"), order)
            if gain == loss:
                raise ValueError(
                    f"{p['id']} {order}: opposite-frame donor does not imply the opposite displayed choice"
                )

    traces = {}
    with trace_path.open("w") as trace_handle, torch.inference_mode():
        for cell_index, (p, frame, order, prompt, rendered) in enumerate(cells):
            batch = tokenizer(
                [rendered] * CONFIG["traces_per_cell"],
                padding=True,
                return_tensors="pt",
                return_token_type_ids=False,
            ).to(args.device)
            seed = CONFIG["seed"] + cell_index
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            generated = model.generate(
                **batch,
                do_sample=True,
                temperature=CONFIG["temperature"],
                top_p=CONFIG["top_p"],
                max_new_tokens=spec["max_new_tokens"],
                pad_token_id=tokenizer.pad_token_id,
            )
            continuation = generated[:, batch["input_ids"].shape[1]:]
            texts = tokenizer.batch_decode(continuation, skip_special_tokens=False)
            for sample_index, text in enumerate(texts):
                body = split_trace(text)
                valid = body is not None
                stripped, removed = strip_terminal_conclusion(body) if valid else ("", [])
                record = {
                    "prospect": p["id"],
                    "frame": frame,
                    "order": order,
                    "sample_index": sample_index,
                    "seed": seed,
                    "valid_trace": valid,
                    "trace": body,
                    "stripped_trace": stripped,
                    "removed_terminal_segments": removed,
                    "removed_any_terminal_conclusion": bool(removed),
                    "remaining_decision_marker": any(
                        is_decision_segment(part)
                        for part in re.split(r"(?<=[.!?])\s+|\n+", stripped)
                        if part.strip()
                    ) if stripped else False,
                    "continuation": text,
                }
                traces[(p["id"], frame, order, sample_index)] = record
                trace_handle.write(json.dumps(record) + "\n")
            trace_handle.flush()

    by_id = {p["id"]: p for p in CONFIG["prospects"]}
    with raw_path.open("w") as handle:
        for (prospect, frame, order, sample_index), target in traces.items():
            if not target["valid_trace"]:
                continue
            opposite_frame = "loss" if frame == "gain" else "gain"
            donor = traces.get((prospect, opposite_frame, order, sample_index))
            if donor is None or not donor["valid_trace"]:
                continue

            p = by_id[prospect]
            expected = shown_label(expected_underlying(p, frame), order)
            rendered = rendered_by_key[(prospect, frame, order)]
            conditions = {
                "own_full": target["trace"],
                "own_stripped": target["stripped_trace"],
                "opposite_stripped": donor["stripped_trace"],
                "empty": "",
            }

            row = {
                "prospect": prospect,
                "frame": frame,
                "order": order,
                "sample_index": sample_index,
                "expected_shown": expected,
                "target_removed_segments": target["removed_terminal_segments"],
                "target_remaining_decision_marker": target["remaining_decision_marker"],
                "donor_remaining_decision_marker": donor["remaining_decision_marker"],
            }
            for name, trace in conditions.items():
                prefix = rendered + trace.strip() + "\n</think>\n\n"
                margin, prediction, logit_a, logit_b = next_token_margin(
                    model, tokenizer, args.device, prefix, expected
                )
                row[f"{name}_margin"] = margin
                row[f"{name}_prediction"] = prediction
                row[f"{name}_correct"] = prediction == expected
                row[f"{name}_logit_a"] = logit_a
                row[f"{name}_logit_b"] = logit_b
            handle.write(json.dumps(row) + "\n")
            handle.flush()

    (out_dir / "model.json").write_text(json.dumps(spec, indent=2) + "\n")
    print(raw_path)


if __name__ == "__main__":
    main()
