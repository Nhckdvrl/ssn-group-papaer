#!/usr/bin/env python3
"""Frozen S12 E03: can an identical biconditional be localized to World A?"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "S12_E01"))
import e01

MAIN_SEED = 3092603
CONTROL_SEED = 3092699
MODEL = e01.MODEL
NONCES = ("nuv", "sarn", "pov", "kelm", "driv", "wemp", "fuz", "nalp", "borm", "sepp",
          "torv", "gilm", "hup", "vexl", "dorn", "kavu", "plit", "zem", "ripa", "chom")
COLORS = ("cyan", "magenta", "brown", "gray", "pink", "white")
SHAPES = ("hexagon", "oval", "diamond", "octagon")
NAMES = ("Nora", "Oren", "Pavo", "Quin", "Rena", "Sola", "Timo", "Uma", "Vera", "Wilo", "Yara", "Zeno")
ROLES = ("definition", "fact_natural", "fact_explicit")
INTRO = "World A and World B are separate places. The same language is spoken in both.\n"
CONTAINERS = {
    "definition": "The glossary for this language contains the following line:",
    "fact_natural": "The survey report describing World A contains the following line:",
    "fact_explicit": ("The survey report describing World A contains the following line:\n"
                      "This report describes World A only and makes no claim about any other world."),
}
TAIL = e01.TAIL


def bases(count, seed):
    rng = random.Random(seed)
    combos = [(color, shape) for color in COLORS for shape in SHAPES]
    out = []
    for index in range(count):
        color, shape = combos[(index + seed) % len(combos)]
        out.append(dict(id=f"{index:03d}", word=NONCES[(index * 7 + seed) % len(NONCES)],
                        color=color, shape=shape, name=NAMES[4+rng.randrange(8)]))
    return out


def components(base):
    word, color, shape = base["word"], base["color"], base["shape"]
    other_color = COLORS[(COLORS.index(color)+1) % len(COLORS)]
    other_shape = SHAPES[(SHAPES.index(shape)+1) % len(SHAPES)]
    relation = f"An object is a {word} if and only if it has color {color} and shape {shape}."
    world_a = (f"World A inventory: {NAMES[0]} and {NAMES[1]} each have color {color} and shape {shape} and are {word}s. "
               f"{NAMES[2]} has color {other_color} and shape {shape} and is not a {word}. "
               f"{NAMES[3]} has color {color} and shape {other_shape} and is not a {word}.")
    return relation, world_a, other_color


def prefix(base, role):
    relation, world_a, _ = components(base)
    return INTRO + CONTAINERS[role] + "\n\"" + relation + "\"\n" + world_a + "\n"


def main_item(base, role, readout, polarity):
    relation, world_a, other_color = components(base)
    word, color, shape, name = base["word"], base["color"], base["shape"], base["name"]
    if readout == "positive":
        world_b = f"In World B, a new object called {name} has color {color} and shape {shape}."
        question = (f"Does it follow that {name} is a {word}?" if polarity == 0 else
                    f"Is it undetermined whether {name} is a {word}?")
    elif readout == "exception":
        world_b = f"In World B, a new object called {name} has color {other_color} and shape {shape}, and is a {word}."
        question = ("Given the stated scope of the earlier sentence, is this World B observation impossible while the World A inventory remains as reported?" if polarity == 0 else
                    "Given the stated scope of the earlier sentence, can this World B observation and the World A inventory both be true?")
    else:
        raise ValueError(readout)
    expected_yes = (role == "definition") == (polarity == 0)
    return dict(id=f"e03-main-{base['id']}-{role}-{readout}", pair_id=f"e03-main-{base['id']}-{readout}",
                base_id=base["id"], split="main", role=role, readout=readout, polarity=polarity,
                relation=relation, world_a=world_a, world_b=world_b,
                expected="A" if expected_yes else "B", expected_transfer=(role == "definition"),
                prompt=prefix(base, role) + world_b + "\nQuestion: " + question + TAIL)


def control_item(base, role, kind):
    relation, world_a, other_color = components(base)
    word, color, shape, name = base["word"], base["color"], base["shape"], base["name"]
    positive = int(base["id"]) % 2 == 0
    if kind == "a_world_a":
        target = NAMES[0] if positive else NAMES[2]
        event = ""
        question = f"In World A, is {target} a {word}?"
        yes = positive
    elif kind == "b_world_change":
        event = f"In World A, {name} has color {color}. In World B, the same object has color {other_color}."
        question = "Can both color reports be true because the worlds are separate?"
        yes = True
    elif kind == "c_definition":
        assert role == "definition"
        query_color = color if positive else other_color
        event = f"In World A, a new object called {name} has color {query_color} and shape {shape}."
        question = f"Does it follow that {name} is a {word}?"
        yes = positive
    elif kind == "d_world_local":
        assert role in ("fact_natural", "fact_explicit")
        event = ("The survey report establishes only what happened in World A; it does not establish the status of objects in World B. "
                 f"In World B, a new object called {name} has color {color} and shape {shape}.")
        question = f"Does the World A report by itself establish that {name} is a {word}?"
        yes = False
    else:
        raise ValueError(kind)
    return dict(id=f"e03-control-{base['id']}-{role}-{kind}", base_id=base["id"], split="control",
                role=role, readout=kind, control=kind, relation=relation, world_a=world_a,
                expected="A" if yes else "B", prompt=prefix(base, role) + event + "\nQuestion: " + question + TAIL)


def generate():
    main = []
    for base in bases(60, MAIN_SEED):
        for role in ROLES:
            for readout in ("positive", "exception"):
                main.append(main_item(base, role, readout, int(base["id"]) % 2))
    controls = []
    for base in bases(24, CONTROL_SEED):
        for role in ROLES:
            for kind in ("a_world_a", "b_world_change"):
                controls.append(control_item(base, role, kind))
            controls.append(control_item(base, role, "c_definition" if role == "definition" else "d_world_local"))
    return main, controls


def check(main, controls):
    assert len(main) == 360 and len(controls) == 216
    assert len({x["id"] for x in main+controls}) == 576
    pairs = collections.defaultdict(dict)
    for item in main:
        pairs[item["pair_id"]][item["role"]] = item
    assert len(pairs) == 120
    for pair in pairs.values():
        assert set(pair) == set(ROLES)
        for key in ("relation", "world_a", "world_b", "polarity"):
            assert len({pair[role][key] for role in ROLES}) == 1
        assert pair["fact_explicit"]["prompt"].replace(CONTAINERS["fact_explicit"], CONTAINERS["fact_natural"]) == pair["fact_natural"]["prompt"]
        for role in ROLES:
            assert pair[role]["prompt"].replace(CONTAINERS[role], "ROLE") == pair["definition"]["prompt"].replace(CONTAINERS["definition"], "ROLE")
            assert pair[role]["prompt"].count('"'+pair[role]["relation"]+'"') == 1
            assert pair[role]["expected"] == ("A" if ((role == "definition") == (pair[role]["polarity"] == 0)) else "B")
        assert "Nothing states whether" not in pair["definition"]["prompt"]
    for role in ROLES:
        for readout in ("positive", "exception"):
            cell = [x for x in main if x["role"] == role and x["readout"] == readout]
            assert len(cell) == 60 and collections.Counter(x["expected"] for x in cell) == {"A": 30, "B": 30}
    for item in main:
        target_color = item["relation"].split("color ")[1].split(" and")[0]
        b_color = item["world_b"].split("color ")[1].split(" and")[0]
        assert (target_color == b_color) == (item["readout"] == "positive")
    assert all(x["expected"] in ("A", "B") for x in main+controls)
    assert set(x["control"] for x in controls) == {"a_world_a", "b_world_change", "c_definition", "d_world_local"}
    assert not (set(NONCES) & set(e01.NONCES))
    assert not (set(COLORS) & set(e01.COLORS))
    assert not (set(SHAPES) & set(e01.SHAPES))
    assert not (set(NAMES) & set(e01.NAMES))


def run(split, batch_size):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    items = e01.read_jsonl(HERE / f"{split}.jsonl")
    out = HERE / f"{split}_raw.jsonl"
    assert not out.exists(), f"Refusing overwrite: {out}"
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="auto", local_files_only=True).eval()
    revision = getattr(model.config, "_commit_hash", None)
    with out.open("w") as file, torch.inference_mode():
        for start in range(0, len(items), batch_size):
            block = items[start:start+batch_size]
            chats = [tokenizer.apply_chat_template([{"role": "user", "content": x["prompt"]}], tokenize=False, add_generation_prompt=True) for x in block]
            tokens = tokenizer(chats, return_tensors="pt", padding=True).to(model.device)
            result = model.generate(**tokens, max_new_tokens=4, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            strings = tokenizer.batch_decode(result[:, tokens["input_ids"].shape[1]:], skip_special_tokens=True)
            for item, raw in zip(block, strings):
                file.write(json.dumps(dict(id=item["id"], model=MODEL, model_revision=revision,
                                           raw=raw, parsed=e01.parse_answer(raw), expected=item["expected"])) + "\n")
            file.flush()
            print(f"{split}: {min(start+len(block),len(items))}/{len(items)}", flush=True)


def analyze():
    main, controls = (e01.read_jsonl(HERE / f"{split}.jsonl") for split in ("main", "controls"))
    check(main, controls)
    def join(items, split):
        output = e01.read_jsonl(HERE / f"{split}_raw.jsonl")
        assert len(items) == len(output)
        lookup = {x["id"]: x for x in output}
        assert len(lookup) == len(items)
        scored = []
        for item in items:
            x = dict(item)
            x.update(raw=lookup[x["id"]]["raw"], parsed=lookup[x["id"]]["parsed"])
            x["correct"] = x["parsed"] == x["expected"]
            if split == "main":
                x["transfer_asserted"] = None if x["parsed"] is None else ((x["parsed"] == "A") == (x["polarity"] == 0))
            scored.append(x)
        e01.write_jsonl(HERE / f"{split}_scored.jsonl", scored)
        return scored
    main, controls = join(main, "main"), join(controls, "controls")
    summary = dict(model=MODEL, main_n=len(main), controls_n=len(controls),
                   main_invalid=sum(x["parsed"] is None for x in main),
                   control_invalid=sum(x["parsed"] is None for x in controls), controls={}, main={}, paired={})
    for kind in ("a_world_a", "b_world_change", "c_definition", "d_world_local"):
        summary["controls"][kind] = {}
        for role in ROLES:
            cell = [x for x in controls if x["control"] == kind and x["role"] == role]
            if cell:
                summary["controls"][kind][role] = dict(n=len(cell), correct=sum(x["correct"] for x in cell),
                                                          invalid=sum(x["parsed"] is None for x in cell))
    for readout in ("positive", "exception"):
        summary["main"][readout] = {}
        by_base = collections.defaultdict(dict)
        for role in ROLES:
            cell = [x for x in main if x["readout"] == readout and x["role"] == role]
            summary["main"][readout][role] = dict(n=len(cell), correct=sum(x["correct"] for x in cell),
                   transfer_assertions=sum(x["transfer_asserted"] is True for x in cell),
                   invalid=sum(x["parsed"] is None for x in cell),
                   by_polarity={str(p): dict(n=sum(x["polarity"] == p for x in cell),
                        correct=sum(x["correct"] for x in cell if x["polarity"] == p)) for p in (0,1)})
            for x in cell:
                by_base[x["base_id"]][role] = x
        summary["paired"][readout] = {}
        for fact_role in ("fact_natural", "fact_explicit"):
            delta = [int(v["definition"]["transfer_asserted"] is True) - int(v[fact_role]["transfer_asserted"] is True) for v in by_base.values()]
            summary["paired"][readout][fact_role] = dict(n=len(delta), mean_difference=sum(delta)/len(delta),
                                                           positive=delta.count(1), zero=delta.count(0), negative=delta.count(-1))
    (HERE / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=("generate", "check", "run", "analyze"))
    p.add_argument("--split", choices=("main", "controls"), default="controls")
    p.add_argument("--batch-size", type=int, default=16)
    args = p.parse_args()
    if args.command == "generate":
        main, controls = generate(); check(main, controls)
        e01.write_jsonl(HERE / "main.jsonl", main); e01.write_jsonl(HERE / "controls.jsonl", controls)
        print("generated", len(main), len(controls))
    elif args.command == "check":
        main, controls = (e01.read_jsonl(HERE / f"{split}.jsonl") for split in ("main", "controls"))
        check(main, controls)
        assert e01.parse_answer("A = Yes") == "A" and e01.parse_answer("B = No.") == "B"
        assert e01.parse_answer("A = No") is None and e01.parse_answer("B because") is None
        print("checks passed", e01.sha(HERE / "main.jsonl"), e01.sha(HERE / "controls.jsonl"))
    elif args.command == "run":
        run(args.split, args.batch_size)
    else:
        analyze()
