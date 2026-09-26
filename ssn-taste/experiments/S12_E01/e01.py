#!/usr/bin/env python3
"""Frozen S12 E01 instrument, inference, and exact analysis."""
import argparse
import collections
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 120925
MODEL = "Qwen/Qwen2.5-14B-Instruct"
NONCES = ("dax", "wug", "kef", "zup", "mep", "tav", "blicket", "fep", "lorp", "narp", "vab", "gorp", "pim", "tud", "siv", "jep", "rux", "zib", "murp", "bex")
COLORS = ("red", "blue", "green", "yellow", "purple", "orange")
SHAPES = ("triangle", "square", "circle", "pentagon")
NAMES = ("Ari", "Bela", "Cato", "Dima", "Elo", "Fara", "Gino", "Hana", "Ivo", "Juna", "Kora", "Lemi")
FRAMES = (
    ("The following sentence is an entry in the glossary used by speakers in both worlds.",
     "The following sentence is an entry in a field report describing the objects in World A."),
    ("The following sentence states a terminology convention used in both worlds.",
     "The following sentence states a survey result about the objects in World A."),
    ("For this discussion, speakers in both worlds use the following sentence to fix a term's use.",
     "For this discussion, investigators use the following sentence to summarize observations in World A."),
)
INTRO = "World A and World B are separate places. The same language is spoken in both.\n"
TAIL = "\nReply with exactly A or B. A = Yes; B = No."


def item(base, role, readout, polarity, split="main"):
    word, color, shape, name, frame = (base[k] for k in ("word", "color", "shape", "name", "frame"))
    other_color = COLORS[(COLORS.index(color) + 1) % len(COLORS)]
    other_shape = SHAPES[(SHAPES.index(shape) + 1) % len(SHAPES)]
    relation = f"An object is a {word} if and only if it has color {color} and shape {shape}."
    # The extension is two positive and two negative objects, identical in both roles.
    a = (f"World A inventory: {NAMES[0]} and {NAMES[1]} each have color {color} and shape {shape} and are {word}s. "
         f"{NAMES[2]} has color {other_color} and shape {shape} and is not a {word}. "
         f"{NAMES[3]} has color {color} and shape {other_shape} and is not a {word}.")
    pre = INTRO + FRAMES[frame][0 if role == "definition" else 1] + "\n" + relation + "\n" + a + "\n"
    if readout == "positive":
        event = f"In World B, a new object called {name} has color {color} and shape {shape}. Nothing states whether {name} is a {word}."
        question = (f"Does it follow that {name} is a {word}?" if polarity == 0 else
                    f"Is it undetermined whether {name} is a {word}?")
    elif readout == "exception":
        event = f"In World B, a new object called {name} has color {other_color} and shape {shape}, and is a {word}."
        question = ("Does this conflict with the earlier information?" if polarity == 0 else
                    "Can this be true together with the earlier information?")
    else:
        raise ValueError(readout)
    target_yes = (role == "definition") == (polarity == 0)
    return dict(id=f"{split}-{base['id']}-{role}-{readout}", pair_id=f"{split}-{base['id']}-{readout}",
                base_id=base["id"], split=split, role=role, readout=readout, frame=frame,
                polarity=polarity, relation=relation, world_a=a, world_b=event,
                expected="A" if target_yes else "B", expected_transfer=(role == "definition"),
                prompt=pre + event + "\nQuestion: " + question + TAIL)


def bases(n, seed):
    rng = random.Random(seed)
    combos = [(c, s) for c in COLORS for s in SHAPES]
    result = []
    for i in range(n):
        color, shape = combos[(i + seed) % len(combos)]
        result.append(dict(id=f"{i:03d}", word=NONCES[(i * 7 + seed) % len(NONCES)], color=color,
                           shape=shape, name=NAMES[4 + rng.randrange(8)], frame=i % 3))
    return result


def control(base, kind, role):
    x = item(base, role, "positive", base["frame"] % 2, "control")
    color, shape, word = base["color"], base["shape"], base["word"]
    if kind == "a_world_a":
        # Positive and negative inventory queries, with balanced keys.
        name = NAMES[0] if int(base["id"]) % 2 == 0 else NAMES[2]
        yes = name == NAMES[0]
        question = f"In World A, is {name} a {word}?"
        body = x["prompt"].split("In World B, a new object")[0]
        x["prompt"] = body + "Question: " + question + TAIL
    elif kind == "b_world_change":
        body = x["prompt"].split("In World B, a new object")[0]
        x["prompt"] = (body + f"World A has a {color} {shape} named {base['name']}. In World B, that same object has a different color. "
                       "Question: Can the two color reports both be true because the worlds are separate?" + TAIL)
        yes = True
    elif kind == "c_definition":
        assert role == "definition"
        # Ordinary unseen reasoning in World A, with both answers represented.
        is_positive = int(base["id"]) % 2 == 0
        body = x["prompt"].split("In World B, a new object")[0]
        query_color = color if is_positive else COLORS[(COLORS.index(color) + 1) % len(COLORS)]
        x["prompt"] = body + f"In World A, a new object called {base['name']} has color {query_color} and shape {shape}. " + f"Question: Does it follow that {base['name']} is a {word}?" + TAIL
        yes = is_positive
    elif kind == "d_world_local":
        assert role == "fact"
        body = x["prompt"].split("In World B, a new object")[0]
        x["prompt"] = (body + "The field report establishes only what happened in World A; it does not report the status of objects in World B. "
                       f"In World B, a new object called {base['name']} has color {color} and shape {shape}. "
                       f"Question: Does the World A report by itself establish that {base['name']} is a {word}?" + TAIL)
        yes = False
    else:
        raise ValueError(kind)
    x.update(id=f"control-{kind}-{base['id']}-{role}", pair_id=None, split="control", control=kind,
             readout=kind, expected="A" if yes else "B", expected_transfer=None)
    return x


def generate():
    main_bases = bases(120, SEED)
    main = []
    for b in main_bases:
        for role in ("definition", "fact"):
            for readout in ("positive", "exception"):
                main.append(item(b, role, readout, (int(b["id"]) // 3) % 2))
    controls = []
    for b in bases(24, SEED + 991):
        for role in ("definition", "fact"):
            for kind in ("a_world_a", "b_world_change"):
                controls.append(control(b, kind, role))
            controls.append(control(b, "c_definition" if role == "definition" else "d_world_local", role))
    return main, controls


def write_jsonl(path, rows):
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(main, controls):
    assert len(main) == 480 and len(controls) == 144
    assert len({x["id"] for x in main + controls}) == 624
    pairs = collections.defaultdict(dict)
    for x in main:
        pairs[x["pair_id"]][x["role"]] = x
    assert len(pairs) == 240
    for pair in pairs.values():
        d, f = pair["definition"], pair["fact"]
        for key in ("relation", "world_a", "world_b", "frame", "polarity"):
            assert d[key] == f[key], (key, d["id"])
        assert d["expected"] != f["expected"]
        assert d["expected_transfer"] and not f["expected_transfer"]
        assert d["prompt"].replace(FRAMES[d["frame"]][0], "<ROLE>") == f["prompt"].replace(FRAMES[f["frame"]][1], "<ROLE>")
    for frame in range(3):
        subset = [x for x in main if x["frame"] == frame]
        assert len(subset) == 160
        for role in ("definition", "fact"):
            for readout in ("positive", "exception"):
                cell = [x for x in subset if x["role"] == role and x["readout"] == readout]
                assert len(cell) == 40 and collections.Counter(x["expected"] for x in cell) == {"A": 20, "B": 20}
    assert all("World A" in x["prompt"] for x in main + controls)
    assert all(x["expected"] in ("A", "B") for x in main + controls)


def parse_answer(raw):
    text = raw.strip()
    match = re.fullmatch(r"([AB])(?:\s*=\s*(Yes|No)\.?)?", text)
    if not match:
        return None
    choice, gloss = match.groups()
    if gloss is not None and gloss != ("Yes" if choice == "A" else "No"):
        return None
    return choice


def run(split, batch_size):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    path = ROOT / f"{split}.jsonl"
    rows = read_jsonl(path)
    out = ROOT / f"{split}_raw.jsonl"
    assert not out.exists(), f"Refusing overwrite: {out}"
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="auto", local_files_only=True).eval()
    revision = getattr(model.config, "_commit_hash", None)
    with out.open("w") as file, torch.inference_mode():
        for start in range(0, len(rows), batch_size):
            block = rows[start:start + batch_size]
            chats = [tokenizer.apply_chat_template([{"role": "user", "content": x["prompt"]}], tokenize=False, add_generation_prompt=True) for x in block]
            toks = tokenizer(chats, return_tensors="pt", padding=True).to(model.device)
            generated = model.generate(**toks, max_new_tokens=4, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            suffix = generated[:, toks["input_ids"].shape[1]:]
            outputs = tokenizer.batch_decode(suffix, skip_special_tokens=True)
            for x, raw in zip(block, outputs):
                record = dict(id=x["id"], model=MODEL, model_revision=revision, raw=raw,
                              parsed=parse_answer(raw), expected=x["expected"])
                file.write(json.dumps(record) + "\n")
            file.flush()
            print(f"{split}: {min(start+len(block), len(rows))}/{len(rows)}", flush=True)


def analyze():
    main, controls = (read_jsonl(ROOT / f"{s}.jsonl") for s in ("main", "controls"))
    check(main, controls)
    raw_main, raw_controls = (read_jsonl(ROOT / f"{s}_raw.jsonl") for s in ("main", "controls"))
    def join(items, outputs):
        assert len(items) == len(outputs)
        lookup = {x["id"]: x for x in outputs}
        assert len(lookup) == len(items)
        return [dict(x, **{k: lookup[x["id"]][k] for k in ("raw", "parsed")}) for x in items]
    main, controls = join(main, raw_main), join(controls, raw_controls)
    def rate(rows, key="correct"):
        return sum(x[key] for x in rows) / len(rows)
    for x in main + controls:
        x["correct"] = x["parsed"] == x["expected"]
        if x["split"] == "main":
            answered_yes = (x["parsed"] == "A")
            x["transfer_asserted"] = None if x["parsed"] is None else (answered_yes == (x["polarity"] == 0))
    summary = {"model": MODEL, "main_n": len(main), "controls_n": len(controls),
               "main_invalid": sum(x["parsed"] is None for x in main),
               "control_invalid": sum(x["parsed"] is None for x in controls), "controls": {}, "main": {}, "paired": {}}
    for kind in ("a_world_a", "b_world_change", "c_definition", "d_world_local"):
        cell = [x for x in controls if x["control"] == kind]
        summary["controls"][kind] = dict(n=len(cell), accuracy=rate(cell), invalid=sum(x["parsed"] is None for x in cell))
    for readout in ("positive", "exception"):
        summary["main"][readout] = {}
        pair = collections.defaultdict(dict)
        for role in ("definition", "fact"):
            cell = [x for x in main if x["role"] == role and x["readout"] == readout]
            summary["main"][readout][role] = dict(n=len(cell), accuracy=rate(cell),
                    transfer_assertion_rate=sum(x["transfer_asserted"] is True for x in cell)/len(cell),
                    invalid=sum(x["parsed"] is None for x in cell), frames={})
            for frame in range(3):
                sub = [x for x in cell if x["frame"] == frame]
                summary["main"][readout][role]["frames"][str(frame)] = dict(n=len(sub), accuracy=rate(sub),
                    transfer_assertion_rate=sum(x["transfer_asserted"] is True for x in sub)/len(sub))
            for x in cell:
                pair[x["pair_id"]][role] = x
        deltas = [int(v["definition"]["transfer_asserted"] is True) - int(v["fact"]["transfer_asserted"] is True) for v in pair.values()]
        summary["paired"][readout] = dict(n=len(deltas), mean_difference=sum(deltas)/len(deltas),
                                           positive=sum(v == 1 for v in deltas), zero=sum(v == 0 for v in deltas), negative=sum(v == -1 for v in deltas))
    write_jsonl(ROOT / "main_scored.jsonl", main)
    write_jsonl(ROOT / "controls_scored.jsonl", controls)
    (ROOT / "analysis.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=("generate", "check", "run", "analyze"))
    p.add_argument("--split", choices=("main", "controls"), default="controls")
    p.add_argument("--batch-size", type=int, default=16)
    a = p.parse_args()
    if a.command == "generate":
        main, controls = generate(); check(main, controls)
        write_jsonl(ROOT / "main.jsonl", main); write_jsonl(ROOT / "controls.jsonl", controls)
        print("generated", len(main), len(controls))
    elif a.command == "check":
        main, controls = read_jsonl(ROOT / "main.jsonl"), read_jsonl(ROOT / "controls.jsonl")
        check(main, controls)
        assert parse_answer(" A \n") == "A" and parse_answer("B") == "B"
        assert parse_answer("A = Yes") == "A" and parse_answer("B = No.") == "B"
        assert parse_answer("A = No") is None and parse_answer("A because") is None and parse_answer("AB") is None and parse_answer("") is None
        print("checks passed", sha(ROOT / "main.jsonl"), sha(ROOT / "controls.jsonl"))
    elif a.command == "run":
        run(a.split, a.batch_size)
    else:
        analyze()
