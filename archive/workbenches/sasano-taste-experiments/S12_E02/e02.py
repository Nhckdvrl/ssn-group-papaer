#!/usr/bin/env python3
"""Held-out, predeclared diagnosis of E01 readout wording."""
import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S12_E01"))
import e01

SEED = 220926


def make():
    rows = []
    for base in e01.bases(60, SEED):
        for role in ("definition", "fact"):
            for readout in ("positive", "exception"):
                polarity = (int(base["id"]) // 3) % 2
                original = e01.item(base, role, readout, polarity, "e02")
                for wording in ("original", "scope_clean"):
                    x = dict(original)
                    x["wording"] = wording
                    x["id"] = x["id"] + "-" + wording
                    x["pair_id"] = x["pair_id"] + "-" + wording
                    if wording == "scope_clean" and readout == "positive":
                        x["prompt"] = x["prompt"].replace(f" Nothing states whether {base['name']} is a {base['word']}.", "")
                    elif wording == "scope_clean" and readout == "exception":
                        old = ("Does this conflict with the earlier information?" if polarity == 0 else
                               "Can this be true together with the earlier information?")
                        new = ("Given the stated scope of the earlier sentence, is this World B observation impossible while the World A inventory remains as reported?" if polarity == 0 else
                               "Given the stated scope of the earlier sentence, can this World B observation and the World A inventory both be true?")
                        assert old in x["prompt"]
                        x["prompt"] = x["prompt"].replace(old, new)
                    rows.append(x)
    return rows


def check(rows):
    assert len(rows) == 480 and len({r["id"] for r in rows}) == 480
    pairs = collections.defaultdict(dict)
    for r in rows:
        pairs[r["pair_id"]][r["role"]] = r
    assert len(pairs) == 240
    for pair in pairs.values():
        d, f = pair["definition"], pair["fact"]
        for key in ("relation", "world_a", "world_b", "wording", "polarity", "frame"):
            assert d[key] == f[key]
        assert d["prompt"].replace(e01.FRAMES[d["frame"]][0], "ROLE") == f["prompt"].replace(e01.FRAMES[f["frame"]][1], "ROLE")
        assert d["expected"] != f["expected"]
    for readout in ("positive", "exception"):
        for wording in ("original", "scope_clean"):
            for role in ("definition", "fact"):
                for frame in range(3):
                    cell = [r for r in rows if (r["readout"], r["wording"], r["role"], r["frame"]) == (readout, wording, role, frame)]
                    assert len(cell) == 20
                    assert collections.Counter(r["expected"] for r in cell) == {"A": 10, "B": 10}
    for r in rows:
        if r["wording"] == "scope_clean" and r["readout"] == "positive":
            assert "Nothing states whether" not in r["prompt"]
        if r["wording"] == "scope_clean" and r["readout"] == "exception":
            assert "stated scope" in r["prompt"]


def run(batch_size):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    rows = e01.read_jsonl(HERE / "items.jsonl")
    check(rows)
    out = HERE / "raw.jsonl"
    assert not out.exists(), "Refusing to overwrite frozen run"
    tokenizer = AutoTokenizer.from_pretrained(e01.MODEL, local_files_only=True)
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(e01.MODEL, dtype=torch.bfloat16, device_map="auto", local_files_only=True).eval()
    revision = getattr(model.config, "_commit_hash", None)
    with out.open("w") as file, torch.inference_mode():
        for start in range(0, len(rows), batch_size):
            block = rows[start:start+batch_size]
            chats = [tokenizer.apply_chat_template([{"role": "user", "content": x["prompt"]}], tokenize=False, add_generation_prompt=True) for x in block]
            tokens = tokenizer(chats, return_tensors="pt", padding=True).to(model.device)
            outputs = model.generate(**tokens, max_new_tokens=4, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            strings = tokenizer.batch_decode(outputs[:, tokens["input_ids"].shape[1]:], skip_special_tokens=True)
            for x, raw in zip(block, strings):
                file.write(json.dumps(dict(id=x["id"], model=e01.MODEL, model_revision=revision, raw=raw,
                                           parsed=e01.parse_answer(raw), expected=x["expected"])) + "\n")
            file.flush()
            print(f"{min(start+len(block),len(rows))}/{len(rows)}", flush=True)


def analyze():
    items = e01.read_jsonl(HERE / "items.jsonl")
    output = e01.read_jsonl(HERE / "raw.jsonl")
    assert len(items) == len(output) == 480
    lookup = {r["id"]: r for r in output}
    assert len(lookup) == 480
    scored = []
    for item in items:
        x = dict(item)
        x.update(raw=lookup[x["id"]]["raw"], parsed=lookup[x["id"]]["parsed"])
        x["correct"] = x["parsed"] == x["expected"]
        x["transfer_asserted"] = None if x["parsed"] is None else ((x["parsed"] == "A") == (x["polarity"] == 0))
        scored.append(x)
    summary = {"n": len(scored), "invalid": sum(x["parsed"] is None for x in scored), "cells": {}, "paired": {}}
    for readout in ("positive", "exception"):
        summary["cells"][readout] = {}
        summary["paired"][readout] = {}
        for wording in ("original", "scope_clean"):
            summary["cells"][readout][wording] = {}
            pair = collections.defaultdict(dict)
            for role in ("definition", "fact"):
                cell = [x for x in scored if (x["readout"], x["wording"], x["role"]) == (readout, wording, role)]
                summary["cells"][readout][wording][role] = dict(n=len(cell), accuracy=sum(x["correct"] for x in cell)/len(cell),
                    transfer_assertion_rate=sum(x["transfer_asserted"] is True for x in cell)/len(cell),
                    by_polarity={str(p): dict(n=sum(x["polarity"] == p for x in cell),
                     accuracy=sum(x["correct"] for x in cell if x["polarity"] == p)/sum(x["polarity"] == p for x in cell)) for p in (0, 1)})
                for x in cell:
                    pair[x["base_id"]][role] = x
            deltas = [int(v["definition"]["transfer_asserted"] is True) - int(v["fact"]["transfer_asserted"] is True) for v in pair.values()]
            summary["paired"][readout][wording] = dict(n=len(deltas), mean_difference=sum(deltas)/len(deltas),
                                                         positive=deltas.count(1), zero=deltas.count(0), negative=deltas.count(-1))
    e01.write_jsonl(HERE / "scored.jsonl", scored)
    (HERE / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("generate", "check", "run", "analyze"))
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    if args.command == "generate":
        rows = make(); check(rows); e01.write_jsonl(HERE / "items.jsonl", rows)
        print("generated", len(rows))
    elif args.command == "check":
        check(e01.read_jsonl(HERE / "items.jsonl")); print("checked", e01.sha(HERE / "items.jsonl"))
    elif args.command == "run":
        run(args.batch_size)
    else:
        analyze()
