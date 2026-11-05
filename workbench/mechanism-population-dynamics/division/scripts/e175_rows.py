#!/usr/bin/env python3
"""E175 data step only: anchor rows with a next token, and their input/next token IDs, word forms, UPOS
(same rules as e175_input_vs_next.py) -> results/e175/e175_rows.json (used by e175_crossfit.py)."""
import json
import sys
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from e175_input_vs_next import CAP, OUT, TOKENIZER_DIR, WB, word_token_index  # noqa: E402

tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
P = json.loads((WB / "results/e167/passages.json").read_text())
passages, words, sel = P["passages"], P["words"], P["sel"]
enc, pos = word_token_index(tok, passages, words)
aw = np.load(CAP / "pairs.npz")["anchor_word"]
assert np.array_equal(np.array([n for n in sel if pos[n] >= 0]), aw)
ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())
D = {k: [] for k in ["rows", "in_tok", "next_tok", "in_form", "next_form", "in_upos", "next_upos"]}
for r, n in enumerate(aw):
    pid = words[n][0]; ids = enc[pid][0]; p = int(pos[n])
    if p >= len(ids) or not (n + 1 < len(words) and words[n + 1][0] == pid):
        continue
    D["rows"].append(r); D["in_tok"].append(ids[p - 1]); D["next_tok"].append(ids[p])
    D["in_form"].append(words[n][3].lower()); D["next_form"].append(words[n + 1][3].lower())
    D["in_upos"].append(ann[n]["upos"]); D["next_upos"].append(ann[n]["next_upos"])
D["rows"] = [int(x) for x in D["rows"]]
D["in_tok_str"] = [tok.decode([i]) for i in D["in_tok"]]
D["next_tok_str"] = [tok.decode([i]) for i in D["next_tok"]]
(OUT / "e175_rows.json").write_text(json.dumps(D))
print(len(D["rows"]))
