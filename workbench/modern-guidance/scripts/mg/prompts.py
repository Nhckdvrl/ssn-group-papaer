"""Versioned prompt sets. Each entry is a dict with at least 'prompt' and 'tag'."""
import csv
import json
import os

MG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GENEVAL = os.path.join(MG, "vendor", "geneval", "prompts", "evaluation_metadata.jsonl")  # geneval@af4902f
DPG_CSV = os.path.join(MG, "vendor", "ella", "dpg_bench", "dpg_bench.csv")  # ELLA@3c228f1
DPG_DIR = os.path.join(MG, "vendor", "ella", "dpg_bench", "prompts")

_cache = {}


def load(name):
    if name in _cache:
        return _cache[name]
    if name == "geneval":
        out = [json.loads(l) for l in open(GENEVAL)]
    elif name == "dpg":
        items = sorted(os.listdir(DPG_DIR))
        out = []
        for f in items:
            out.append({"prompt": open(os.path.join(DPG_DIR, f)).read().strip(), "tag": "dpg",
                        "item_id": f[:-4]})
    elif name.startswith("file:"):
        out = [json.loads(l) for l in open(name[5:])]
    else:
        raise KeyError(name)
    _cache[name] = out
    return out
