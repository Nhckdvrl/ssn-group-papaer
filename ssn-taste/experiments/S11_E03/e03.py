#!/usr/bin/env python3
"""Frozen S11 E03: rounded-report versus directly supplied interval."""
import argparse
import collections
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S11_E01"))
sys.path.insert(0, str(HERE.parent / "S11_E02"))
import e01  # noqa: E402
import e02  # noqa: E402

SEED = 110326
N_BASES = 80
REPRESENTATIONS = ("rounded_report", "explicit_interval")
VARIANTS = ("coarse", "fine")
DIRECTIONS = ("greater", "less")


def used_numbers():
    return ({int(Decimal(x["coarse"]) * 10) for x in e01.bases()} |
            {int(Decimal(x["coarse"]) * 10) for x in e02.rows()})


def make_rows():
    available = [n for n in range(10, 1000) if n not in used_numbers()]
    numbers = random.Random(SEED).sample(available, N_BASES)
    result = []
    for i, number in enumerate(numbers):
        base_id = f"{i:03d}"
        coarse = f"{number//10}.{number%10}"
        fine = coarse + "0"
        direction = DIRECTIONS[i % 2]
        center = Decimal(number) / 10
        threshold = center + (Decimal("-0.02") if direction == "greater" else Decimal("0.02"))
        threshold_text = f"{threshold:.2f}"
        comparator = "greater than" if direction == "greater" else "less than"
        downstream = (f"Can this report alone certify that the true length is "
                      f"{comparator} {threshold_text} m?")
        for variant, display in (("coarse", coarse), ("fine", fine)):
            lower, upper = e01.interval(display)
            expected = "A" if e01.certifies(display, threshold, direction) else "B"
            for representation in REPRESENTATIONS:
                if representation == "rounded_report":
                    evidence = e01.EXPLICIT + "\n" + f"A length is reported as {display} m. "
                else:
                    evidence = (f"For this question, a report states that the true length lies "
                                f"in [{lower} m, {upper} m). Assume no other instrument error.\n")
                result.append(dict(id=f"s11-e03-{base_id}-{representation}-{variant}",
                                   base_id=base_id, representation=representation,
                                   variant=variant, direction=direction, coarse=coarse, fine=fine,
                                   displayed=display, threshold=threshold_text,
                                   interval=[str(lower), str(upper)], expected=expected,
                                   prompt=evidence + downstream + e01.TAIL))
    return result


def check(items):
    assert len(items) == 4 * N_BASES and len({x["id"] for x in items}) == len(items)
    assert {int(Decimal(x["coarse"]) * 10) for x in items}.isdisjoint(used_numbers())
    assert len({x["coarse"] for x in items}) == N_BASES
    assert collections.Counter(x["direction"] for x in items) == {"greater": 160, "less": 160}
    assert collections.Counter(x["expected"] for x in items) == {"A": 160, "B": 160}
    assert e01.parse_answer("A") == "A" and e01.parse_answer("B") == "B"
    assert e01.parse_answer("A = No") is None and e01.parse_answer("A because") is None
    groups = collections.defaultdict(dict)
    for x in items:
        groups[x["base_id"]][(x["representation"], x["variant"])] = x
        lower, upper = e01.interval(x["displayed"])
        assert x["interval"] == [str(lower), str(upper)]
        assert x["expected"] == ("A" if e01.certifies(x["displayed"], x["threshold"], x["direction"]) else "B")
        t = Decimal(x["threshold"])
        assert t not in (lower, upper)
        comparator = "greater than" if x["direction"] == "greater" else "less than"
        suffix = (f"Can this report alone certify that the true length is {comparator} "
                  f"{x['threshold']} m?" + e01.TAIL)
        if x["representation"] == "rounded_report":
            assert x["prompt"] == e01.EXPLICIT + "\n" + f"A length is reported as {x['displayed']} m. " + suffix
        else:
            assert x["representation"] == "explicit_interval"
            assert x["prompt"] == (f"For this question, a report states that the true length lies "
                                   f"in [{lower} m, {upper} m). Assume no other instrument error.\n" + suffix)
    assert len(groups) == N_BASES
    expected_keys = {(r, v) for r in REPRESENTATIONS for v in VARIANTS}
    for group in groups.values():
        assert set(group) == expected_keys
        first = next(iter(group.values()))
        assert all(x["coarse"] == first["coarse"] and x["fine"] == first["fine"] and
                   x["threshold"] == first["threshold"] and x["direction"] == first["direction"]
                   for x in group.values())
        c0, c1 = e01.interval(first["coarse"])
        f0, f1 = e01.interval(first["fine"])
        t = Decimal(first["threshold"])
        assert c0 < f0 < f1 < c1
        assert (c0 < t < f0) if first["direction"] == "greater" else (f1 < t < c1)
        for variant in VARIANTS:
            a = group[("rounded_report", variant)]
            b = group[("explicit_interval", variant)]
            assert a["expected"] == b["expected"] and a["interval"] == b["interval"]
        for representation in REPRESENTATIONS:
            assert group[(representation, "coarse")]["expected"] == "B"
            assert group[(representation, "fine")]["expected"] == "A"
    for representation in REPRESENTATIONS:
        for direction in DIRECTIONS:
            for variant in VARIANTS:
                subset = [x for x in items if (x["representation"], x["direction"], x["variant"]) ==
                          (representation, direction, variant)]
                assert len(subset) == 40


def run(batch_size, gpu_cap_gib):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    items = e01.read_jsonl(HERE / "items.jsonl")
    check(items)
    out = HERE / "raw.jsonl"
    assert not out.exists(), "Refusing overwrite"
    tokenizer = AutoTokenizer.from_pretrained(e01.MODEL, local_files_only=True)
    tokenizer.padding_side = "left"
    cap = {i: f"{gpu_cap_gib}GiB" for i in range(torch.cuda.device_count())} if gpu_cap_gib is not None else None
    model = AutoModelForCausalLM.from_pretrained(e01.MODEL, dtype=torch.bfloat16, device_map="auto",
                                                 max_memory=cap, local_files_only=True).eval()
    revision = getattr(model.config, "_commit_hash", None)
    with out.open("w") as f, torch.inference_mode():
        for start in range(0, len(items), batch_size):
            block = items[start:start + batch_size]
            chats = [tokenizer.apply_chat_template([{"role": "user", "content": x["prompt"]}],
                                                    tokenize=False, add_generation_prompt=True) for x in block]
            inputs = tokenizer(chats, return_tensors="pt", padding=True).to(model.device)
            result = model.generate(**inputs, max_new_tokens=4, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            outputs = tokenizer.batch_decode(result[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            for item, raw in zip(block, outputs):
                f.write(json.dumps(dict(id=item["id"], model=e01.MODEL, model_revision=revision,
                                        batch_size=batch_size, gpu_cap_gib=gpu_cap_gib,
                                        raw=raw, parsed=e01.parse_answer(raw), expected=item["expected"])) + "\n")
            f.flush()
            print(f"{min(start + len(block), len(items))}/{len(items)}", flush=True)


def analyze():
    items = e01.read_jsonl(HERE / "items.jsonl")
    check(items)
    raw = e01.read_jsonl(HERE / "raw.jsonl")
    assert len(raw) == len(items) and len({x["id"] for x in raw}) == len(items)
    lookup = {x["id"]: x for x in raw}
    scored = []
    for item in items:
        output = lookup[item["id"]]
        assert output["expected"] == item["expected"]
        assert output["parsed"] == e01.parse_answer(output["raw"])
        scored.append(dict(item, raw=output["raw"], parsed=output["parsed"],
                           correct=output["parsed"] == item["expected"]))
    summary = dict(n=len(scored), invalid=sum(x["parsed"] is None for x in scored),
                   model=e01.MODEL, revisions=sorted({x["model_revision"] for x in raw}),
                   runtimes=sorted({(x["batch_size"], x["gpu_cap_gib"]) for x in raw}),
                   table={}, pair_patterns={})
    for representation in REPRESENTATIONS:
        summary["table"][representation] = {}
        summary["pair_patterns"][representation] = {}
        for direction in DIRECTIONS:
            summary["table"][representation][direction] = {}
            subset = [x for x in scored if x["representation"] == representation and x["direction"] == direction]
            for variant in VARIANTS:
                cell = [x for x in subset if x["variant"] == variant]
                summary["table"][representation][direction][variant] = dict(
                    n=len(cell), correct=sum(x["correct"] for x in cell),
                    invalid=sum(x["parsed"] is None for x in cell))
            pairs = collections.defaultdict(dict)
            for x in subset:
                pairs[x["base_id"]][x["variant"]] = x["parsed"] or "invalid"
            assert len(pairs) == 40 and all(set(x) == set(VARIANTS) for x in pairs.values())
            summary["pair_patterns"][representation][direction] = dict(collections.Counter(
                pair["coarse"] + "/" + pair["fine"] for pair in pairs.values()))
    e01.write_jsonl(HERE / "scored.jsonl", scored)
    (HERE / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("generate", "check", "run", "analyze"))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--gpu-cap-gib", type=int, default=2)
    args = parser.parse_args()
    if args.command == "generate":
        items = make_rows(); check(items); e01.write_jsonl(HERE / "items.jsonl", items)
        print("generated", len(items))
    elif args.command == "check":
        items = e01.read_jsonl(HERE / "items.jsonl"); check(items)
        print("checked", len(items))
    elif args.command == "run":
        run(args.batch_size, args.gpu_cap_gib)
    else:
        analyze()
