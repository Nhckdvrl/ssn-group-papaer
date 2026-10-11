#!/usr/bin/env python3
"""Frozen held-out replication of E01's explicit measurement question."""
import argparse
import collections
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S11_E01"))
import e01  # noqa: E402

SEED = 110226
N_BASES = 60


def rows():
    used = {int(Decimal(x["coarse"]) * 10) for x in e01.bases()}
    candidates = [x for x in range(10, 1000) if x not in used]
    chosen = random.Random(SEED).sample(candidates, N_BASES)
    result = []
    for i, number in enumerate(chosen):
        base_id = f"{i:03d}"
        coarse = f"{number//10}.{number%10}"
        fine = coarse + "0"
        direction = "greater" if i % 2 == 0 else "less"
        center = Decimal(number) / 10
        threshold = center + (Decimal("-0.02") if direction == "greater" else Decimal("0.02"))
        threshold_text = f"{threshold:.2f}"
        comparator = "greater than" if direction == "greater" else "less than"
        for variant, display in (("coarse", coarse), ("fine", fine)):
            answer = e01.certifies(display, threshold, direction)
            question = (f"A length is reported as {display} m. Can this report alone certify that "
                        f"the true length is {comparator} {threshold_text} m?")
            result.append(dict(id=f"s11-e02-{base_id}-{variant}", base_id=base_id,
                               coarse=coarse, fine=fine, direction=direction,
                               threshold=threshold_text, variant=variant,
                               displayed=display, interval=[str(x) for x in e01.interval(display)],
                               expected="A" if answer else "B",
                               prompt=e01.EXPLICIT + "\n" + question + e01.TAIL))
    return result


def check(items):
    assert len(items) == 120 and len({x["id"] for x in items}) == 120
    assert {x["coarse"] for x in items}.isdisjoint({x["coarse"] for x in e01.bases()})
    assert collections.Counter(x["direction"] for x in items) == {"greater": 60, "less": 60}
    assert collections.Counter(x["expected"] for x in items) == {"A": 60, "B": 60}
    groups = collections.defaultdict(dict)
    for x in items:
        groups[x["base_id"]][x["variant"]] = x
        assert x["expected"] == ("A" if e01.certifies(x["displayed"], x["threshold"], x["direction"]) else "B")
        assert Decimal(x["threshold"]) not in e01.interval(x["displayed"])
        assert x["prompt"] == e01.EXPLICIT + "\n" + (
            f"A length is reported as {x['displayed']} m. Can this report alone certify that "
            f"the true length is {'greater than' if x['direction'] == 'greater' else 'less than'} "
            f"{x['threshold']} m?") + e01.TAIL
    assert len(groups) == N_BASES
    for pair in groups.values():
        assert set(pair) == {"coarse", "fine"}
        assert pair["coarse"]["expected"] == "B" and pair["fine"]["expected"] == "A"
        c0, c1 = e01.interval(pair["coarse"]["displayed"])
        f0, f1 = e01.interval(pair["fine"]["displayed"])
        t = Decimal(pair["coarse"]["threshold"])
        assert c0 < f0 < f1 < c1
        assert (c0 < t < f0) if pair["coarse"]["direction"] == "greater" else (f1 < t < c1)


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
            block = items[start:start+batch_size]
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
            print(f"{min(start+len(block), len(items))}/{len(items)}", flush=True)


def analyze():
    items = e01.read_jsonl(HERE / "items.jsonl")
    check(items)
    outputs = e01.read_jsonl(HERE / "raw.jsonl")
    assert len(outputs) == len(items) and len({x["id"] for x in outputs}) == len(items)
    lookup = {x["id"]: x for x in outputs}
    pairs = collections.defaultdict(dict)
    scored = []
    for item in items:
        output = lookup[item["id"]]
        assert output["expected"] == item["expected"]
        assert output["parsed"] == e01.parse_answer(output["raw"])
        row = dict(item, raw=output["raw"], parsed=output["parsed"],
                   correct=output["parsed"] == item["expected"])
        scored.append(row)
        pairs[(item["direction"], item["base_id"])][item["variant"]] = row
    summary = dict(n=len(scored), invalid=sum(x["parsed"] is None for x in scored),
                   correct=sum(x["correct"] for x in scored), by_variant={}, by_direction={}, pair_patterns={})
    for variant in ("coarse", "fine"):
        subset = [x for x in scored if x["variant"] == variant]
        summary["by_variant"][variant] = dict(n=len(subset), correct=sum(x["correct"] for x in subset))
    for direction in ("greater", "less"):
        subset = [x for x in scored if x["direction"] == direction]
        summary["by_direction"][direction] = dict(n=len(subset), correct=sum(x["correct"] for x in subset))
        patterns = collections.Counter((pair["coarse"]["parsed"] or "invalid") + "/" +
                                       (pair["fine"]["parsed"] or "invalid")
                                       for (d, _), pair in pairs.items() if d == direction)
        summary["pair_patterns"][direction] = dict(patterns)
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
        items = rows(); check(items); e01.write_jsonl(HERE / "items.jsonl", items)
        print("generated", len(items))
    elif args.command == "check":
        items = e01.read_jsonl(HERE / "items.jsonl"); check(items)
        print("checked", len(items))
    elif args.command == "run":
        run(args.batch_size, args.gpu_cap_gib)
    else:
        analyze()
