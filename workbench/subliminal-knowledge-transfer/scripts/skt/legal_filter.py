#!/usr/bin/env python3
"""Drop training rows whose completion uses a token outside Beyond Owls' 29 LEGAL_IDS (the student is
distilled only over those ids, so such rows cannot be trained on). Applied identically to every teacher's
train_<TAG>.jsonl before the student; prints how many rows were dropped.

    python legal_filter.py IN.jsonl OUT.jsonl
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bo_backdoor" / "logit_distillation"))
from shared import LEGAL_IDS, get_tokenizer, training_example  # noqa: E402

LEGAL = set(LEGAL_IDS)
tok = get_tokenizer()
src, dst = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(src)]
keep = []
for r in rows:
    ids, w = training_example(tok, r["prompt"], r["completion"])
    if all(ids[i] in LEGAL for i in range(len(ids)) if w[i] == 1.0):
        keep.append(r)
with open(dst, "w") as f:
    for r in keep:
        f.write(json.dumps(r) + "\n")
print(f"{src}: kept {len(keep)}/{len(rows)} (dropped {len(rows) - len(keep)})")
