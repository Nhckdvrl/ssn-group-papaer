#!/usr/bin/env python3
"""Frozen S11 E01: analytic value/precision/notation contrasts."""
import argparse
import collections
import json
import random
import re
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 110126
MODEL = "Qwen/Qwen2.5-7B-Instruct"
N_BASES = 100
EXPLICIT = ("For this question, a displayed measurement is obtained by rounding the true length "
            "to the last shown decimal place. Assume no other instrument error.")
NATURAL = "This is a standard laboratory report of a measured length."
TAIL = "\nReply with exactly A or B. A = Yes; B = No."
SCIENTIFIC = re.compile(r"^([+-]?\d+\.\d+)\s*×\s*10\^([+-]?\d+)$")
PLAIN = re.compile(r"^[+-]?\d+\.\d+$")


def parse_expression(text):
    """Return exact value and displayed unit step; preserve trailing zeros."""
    text = text.strip()
    match = SCIENTIFIC.fullmatch(text)
    if match:
        mantissa, exponent = match.groups()
        exponent = int(exponent)
    else:
        assert PLAIN.fullmatch(text), text
        mantissa, exponent = text, 0
    digits = len(mantissa.split(".")[1])
    scale = Decimal(10) ** exponent
    return Decimal(mantissa) * scale, (Decimal(10) ** -digits) * scale


def interval(text):
    center, step = parse_expression(text)
    half = step / 2
    return center - half, center + half


def certifies(text, threshold, direction):
    lower, upper = interval(text)
    threshold = Decimal(threshold)
    # All generated thresholds avoid endpoints, so the open upper endpoint is immaterial.
    assert threshold not in (lower, upper)
    if direction == "greater":
        return lower > threshold
    if direction == "less":
        return upper < threshold
    raise ValueError(direction)


def parse_answer(raw):
    match = re.fullmatch(r"([AB])(?:\s*=\s*(Yes|No)\.?)?", raw.strip())
    if not match:
        return None
    letter, gloss = match.groups()
    if gloss is not None and gloss != ("Yes" if letter == "A" else "No"):
        return None
    return letter


def bases():
    rng = random.Random(SEED)
    # One-decimal central values; no zero/negative lengths or repeated base values.
    numbers = rng.sample(range(10, 1000), N_BASES)
    out = []
    for i, number in enumerate(numbers):
        coarse = f"{number//10}.{number%10}"
        fine = coarse + "0"
        sci = fine + " × 10^0"
        direction = "greater" if i % 2 == 0 else "less"
        center = Decimal(number) / Decimal(10)
        threshold = center + (Decimal("-0.02") if direction == "greater" else Decimal("0.02"))
        threshold_text = f"{threshold:.2f}"
        out.append(dict(base_id=f"{i:03d}", coarse=coarse, fine=fine, notation=sci,
                        direction=direction, threshold=threshold_text))
    return out


def base_fields(base):
    return {key: base[key] for key in ("base_id", "coarse", "fine", "notation", "direction", "threshold")}


def make_rows():
    rows = []
    for i, base in enumerate(bases()):
        common = base_fields(base)
        coarse, fine, notation = base["coarse"], base["fine"], base["notation"]
        value_same = parse_expression(coarse)[0] == parse_expression(fine)[0]
        assert value_same
        ask_same = i % 2 == 0
        math_question = ("Do these numerals denote the same mathematical value?" if ask_same else
                         "Do these numerals denote different mathematical values?")
        rows.append(dict(common, id=f"s11-e01-{i:03d}-value", cell="value", layer="math", variant="pair",
                         question_polarity="same" if ask_same else "different",
                         expected="A" if value_same == ask_same else "B",
                         prompt=f"In arithmetic, compare the exact numbers {coarse} and {fine}.\nQuestion: {math_question}" + TAIL))
        for layer, intro in (("explicit", EXPLICIT), ("natural", NATURAL)):
            for variant, display in (("coarse", coarse), ("fine", fine)):
                truth = certifies(display, base["threshold"], base["direction"])
                comparator = "greater than" if base["direction"] == "greater" else "less than"
                question = (f"A length is reported as {display} m. Can this report alone certify that "
                            f"the true length is {comparator} {base['threshold']} m?")
                rows.append(dict(common, id=f"s11-e01-{i:03d}-measurement-{layer}-{variant}",
                                 cell="measurement", layer=layer, variant=variant,
                                 displayed=display, interval=[str(v) for v in interval(display)],
                                 expected="A" if truth else "B", prompt=intro + "\n" + question + TAIL))
            same_info = (interval(fine) == interval(notation) and
                         parse_expression(fine)[0] == parse_expression(notation)[0])
            assert same_info
            ask_same_notation = i % 2 == 1
            notation_question = ("Do these two reports allow exactly the same possible true lengths?" if ask_same_notation else
                                 "Do these two reports allow different sets of possible true lengths?")
            rows.append(dict(common, id=f"s11-e01-{i:03d}-notation-{layer}", cell="notation", layer=layer,
                             variant="pair", question_polarity="same" if ask_same_notation else "different",
                             expected="A" if same_info == ask_same_notation else "B",
                             prompt=(intro + "\n" + f"Two reports of a measured length are {fine} m and {notation} m.\n"
                                     f"Question: {notation_question}" + TAIL)))
    return rows


def check(rows):
    assert len(rows) == 700 and len({x["id"] for x in rows}) == 700
    by_base = collections.defaultdict(list)
    for row in rows:
        by_base[row["base_id"]].append(row)
        assert row["expected"] in ("A", "B")
    assert len(by_base) == N_BASES
    for group in by_base.values():
        assert len(group) == 7
        first = group[0]
        coarse, fine, notation = first["coarse"], first["fine"], first["notation"]
        assert all(x["coarse"] == coarse and x["fine"] == fine and x["notation"] == notation for x in group)
        c0, c1 = interval(coarse)
        f0, f1 = interval(fine)
        threshold = Decimal(first["threshold"])
        assert f0 > c0 and f1 < c1 and c0 < threshold < c1
        if first["direction"] == "greater":
            assert c0 < threshold < f0
        else:
            assert f1 < threshold < c1
        assert not certifies(coarse, threshold, first["direction"])
        assert certifies(fine, threshold, first["direction"])
        assert interval(fine) == interval(notation)
        assert parse_expression(coarse)[0] == parse_expression(fine)[0] == parse_expression(notation)[0]
        assert set((x["cell"], x["layer"], x["variant"]) for x in group) == {
            ("value", "math", "pair"), ("measurement", "explicit", "coarse"),
            ("measurement", "explicit", "fine"), ("measurement", "natural", "coarse"),
            ("measurement", "natural", "fine"), ("notation", "explicit", "pair"),
            ("notation", "natural", "pair")}
        for layer in ("explicit", "natural"):
            pair = [x for x in group if x["cell"] == "measurement" and x["layer"] == layer]
            assert {x["expected"] for x in pair} == {"A", "B"}
    for cell, layer, count in (("value", "math", 100), ("measurement", "explicit", 200),
                               ("measurement", "natural", 200), ("notation", "explicit", 100),
                               ("notation", "natural", 100)):
        selected = [x for x in rows if (x["cell"], x["layer"]) == (cell, layer)]
        assert len(selected) == count
        assert collections.Counter(x["expected"] for x in selected) == {"A": count//2, "B": count//2}
    assert collections.Counter(x["direction"] for x in rows if x["cell"] == "value") == {"greater":50,"less":50}
    assert parse_answer("A = Yes") == "A" and parse_answer("B = No.") == "B"
    assert parse_answer("A = No") is None and parse_answer("A because") is None


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def write_jsonl(path, rows):
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run(batch_size, gpu_cap_gib):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    rows = read_jsonl(HERE / "items.jsonl")
    check(rows)
    out = HERE / "raw.jsonl"
    assert not out.exists(), "Refusing overwrite"
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    tokenizer.padding_side = "left"
    cap = {i: f"{gpu_cap_gib}GiB" for i in range(torch.cuda.device_count())} if gpu_cap_gib is not None else None
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="auto",
                                                 max_memory=cap, local_files_only=True).eval()
    revision = getattr(model.config, "_commit_hash", None)
    with out.open("w") as f, torch.inference_mode():
        for start in range(0, len(rows), batch_size):
            block = rows[start:start+batch_size]
            chats = [tokenizer.apply_chat_template([{"role":"user", "content":x["prompt"]}],
                                                    tokenize=False, add_generation_prompt=True) for x in block]
            inputs = tokenizer(chats, return_tensors="pt", padding=True).to(model.device)
            result = model.generate(**inputs, max_new_tokens=4, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            outputs = tokenizer.batch_decode(result[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            for row, raw in zip(block, outputs):
                f.write(json.dumps(dict(id=row["id"], model=MODEL, model_revision=revision,
                                        batch_size=batch_size, gpu_cap_gib=gpu_cap_gib,
                                        raw=raw, parsed=parse_answer(raw), expected=row["expected"])) + "\n")
            f.flush()
            print(f"{min(start+len(block),len(rows))}/{len(rows)}", flush=True)


def analyze():
    items = read_jsonl(HERE / "items.jsonl")
    output = read_jsonl(HERE / "raw.jsonl")
    check(items)
    assert len(output) == len(items)
    lookup = {x["id"]: x for x in output}
    assert len(lookup) == len(items)
    scored = []
    for item in items:
        raw = lookup[item["id"]]
        assert raw["expected"] == item["expected"]
        x = dict(item, raw=raw["raw"], parsed=raw["parsed"], correct=(raw["parsed"] == item["expected"]))
        scored.append(x)
    summary = dict(model=MODEL, n=len(scored), invalid=sum(x["parsed"] is None for x in scored), cells={},
                   measurement_pairs={})
    for cell, layers in (("value", ("math",)), ("measurement", ("explicit", "natural")),
                         ("notation", ("explicit", "natural"))):
        summary["cells"][cell] = {}
        for layer in layers:
            rows = [x for x in scored if x["cell"] == cell and x["layer"] == layer]
            result = dict(n=len(rows), correct=sum(x["correct"] for x in rows),
                          invalid=sum(x["parsed"] is None for x in rows), by_expected={}, by_direction={})
            for expected in ("A", "B"):
                subset = [x for x in rows if x["expected"] == expected]
                result["by_expected"][expected] = dict(n=len(subset), correct=sum(x["correct"] for x in subset))
            if cell == "measurement":
                for variant in ("coarse", "fine"):
                    subset = [x for x in rows if x["variant"] == variant]
                    result[variant] = dict(n=len(subset), correct=sum(x["correct"] for x in subset))
                for direction in ("greater", "less"):
                    subset = [x for x in rows if x["direction"] == direction]
                    result["by_direction"][direction] = dict(n=len(subset), correct=sum(x["correct"] for x in subset))
            summary["cells"][cell][layer] = result
    for layer in ("explicit", "natural"):
        pairs = collections.defaultdict(dict)
        for x in scored:
            if x["cell"] == "measurement" and x["layer"] == layer:
                pairs[x["base_id"]][x["variant"]] = x
        assert len(pairs) == N_BASES and all(set(v) == {"coarse", "fine"} for v in pairs.values())
        summary["measurement_pairs"][layer] = dict(n=N_BASES,
            normatively_differentiated=sum(v["coarse"]["parsed"] == "B" and v["fine"]["parsed"] == "A" for v in pairs.values()),
            same_answer=sum(v["coarse"]["parsed"] == v["fine"]["parsed"] for v in pairs.values()),
            reversed=sum(v["coarse"]["parsed"] == "A" and v["fine"]["parsed"] == "B" for v in pairs.values()))
    write_jsonl(HERE / "scored.jsonl", scored)
    (HERE / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("generate", "check", "run", "analyze"))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--gpu-cap-gib", type=int, default=2)
    args = parser.parse_args()
    if args.command == "generate":
        rows = make_rows(); check(rows); write_jsonl(HERE / "items.jsonl", rows)
        print("generated", len(rows))
    elif args.command == "check":
        rows = read_jsonl(HERE / "items.jsonl"); check(rows)
        print("checked", len(rows))
    elif args.command == "run":
        run(args.batch_size, args.gpu_cap_gib)
    else:
        analyze()
