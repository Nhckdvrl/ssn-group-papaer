"""Pre-registered support audit: does each channel have anything to act on?

A null in a channel where the 18 selected ids never occur would be an artifact of
zero opportunity, not evidence that the channel is unimportant. Selection §4
requires >=250 Flores devtest sentences with at least one selected-token
occurrence in each of the source and reference-target spans.
"""
import json
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import (ROOT, SEG_INSTR, SEG_SOURCE, SEL_IDS, read_jsonl)  # noqa: E402

rows = read_jsonl(ROOT / "data" / "devtest_en_ca.jsonl")
sel = set(SEL_IDS)
have = {"instruction": 0, "source": 0, "target": 0}
occ = {k: 0 for k in have}
per_tok = {k: Counter() for k in have}
n_tok = {k: 0 for k in have}

for r in rows:
    spans = {"instruction": [t for t, s in zip(r["ids"], r["seg"]) if s == SEG_INSTR],
             "source": [t for t, s in zip(r["ids"], r["seg"]) if s == SEG_SOURCE],
             "target": list(r["y"])}
    for k, toks in spans.items():
        hits = [t for t in toks if t in sel]
        n_tok[k] += len(toks)
        occ[k] += len(hits)
        per_tok[k].update(hits)
        if hits:
            have[k] += 1

out = {
    "n_sentences": len(rows),
    "sentences_with_support": have,
    "total_selected_occurrences": occ,
    "total_tokens": n_tok,
    "selected_token_share": {k: occ[k] / n_tok[k] for k in occ},
    "mean_occurrences_per_sentence": {k: occ[k] / len(rows) for k in occ},
    "top_tokens": {k: per_tok[k].most_common(8) for k in per_tok},
    "gate_pass": have["source"] >= 250 and have["target"] >= 250,
}
(ROOT / "results" / "support_audit.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
