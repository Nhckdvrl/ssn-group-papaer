"""E00: task-learning instrument.  Clean single-rule contexts, varying T and n_attr.

Writes data/e00/{rows.jsonl, meta.jsonl}.  Seeds: pilot range 0..9999 (confirm seeds >= 100000 untouched).
"""
import copy, json, sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import Base, episode_record, load_lexicon, make_base, render, labels_for  # noqa
from ices.oracle import all_oracles_fast  # noqa

ROOT = Path(__file__).resolve().parents[1]
import os
OUT = ROOT / "data" / os.environ.get("E00_OUT", "e00"); OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))
N = int(os.environ.get("E00_N", 300))
rows = []


def remap(base: Base, seed: int) -> Base:
    rng = np.random.default_rng(seed)
    b = copy.deepcopy(base)
    b.attr_names = list(rng.choice(attr_bank, base.n_attr, replace=False))
    while True:
        lw = list(rng.choice(label_bank, 2, replace=False))
        if lw[0][0] != lw[1][0]:
            break
    b.label_words = lw
    b.base_id = f"{base.base_id}_r{seed}"
    return b


def add(rec, gold_idx, cond):
    b = rec["base"]
    o = all_oracles_fast(np.array(b["X"]).reshape(-1, b["n_attr"]) if b["T"] else np.zeros((0, b["n_attr"])),
                         rec["labels"], b["xq"], b["n_attr"]) if b["T"] else {}
    rec.update({"uid": f"{cond}|{rec['base_id']}", "gold": gold_idx,
                "oracle": {k: v for k, v in o.items()}})
    rows.append(rec)


for n_attr, Ts in ((5, (4, 8, 12, 16, 24)), (3, (4, 6))):
    for T in Ts:
        for i in range(N):
            seed = 1000 * n_attr + 10 * T + i * 7919
            base = make_base(seed, n_attr, T, attr_bank, label_bank, tag=f"n{n_attr}T{T}_")
            rec = episode_record(base, "A" * T, f"clean_n{n_attr}_T{T}")
            add(rec, rec["query_label_A"], rec["cond"])

# shuffled-label control (labels independent of the rule, balanced counts)
for i in range(N):
    seed = 555000 + i
    base = make_base(seed, 5, 16, attr_bank, label_bank, tag="shuf_")
    rng = np.random.default_rng(seed)
    labs = [0] * 8 + [1] * 8; rng.shuffle(labs)
    rec = episode_record(base, "A" * 16, "shuffled_n5_T16")
    rec["labels"] = labs; rec["prompt"] = render(base, labs)
    add(rec, rec["query_label_A"], "shuffled_n5_T16")

# dictionary remaps of the same bases (T=16)
for i in range(N):
    seed = 1000 * 5 + 10 * 16 + i * 7919
    base = make_base(seed, 5, 16, attr_bank, label_bank, tag="n5T16_")
    for r in (1, 2):
        b2 = remap(base, seed * 10 + r)
        rec = episode_record(b2, "A" * 16, f"remap{r}_n5_T16")
        add(rec, rec["query_label_A"], rec["cond"])

with open(OUT / "rows.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(len(rows), "rows")
print(rows[0]["prompt"])
