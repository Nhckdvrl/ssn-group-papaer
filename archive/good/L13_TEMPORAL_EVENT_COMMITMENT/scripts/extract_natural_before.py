#!/usr/bin/env python
"""E08: harvest naturally occurring `before`-clause sentences for external validity.

Source: NeelNanda/pile-10k (local cache, offline). Surface-form filtering only; no
model selects, rewrites or labels anything. Every kept sentence is adjudicated by hand.

Two natural sub-constructions are collected:
  prevented — ", before <NP> could/would <VP>": prototypically non-veridical
  veridical — ", before <NP> <past-tense VP>":  the ordinary narrative use
"""
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

SENT = re.compile(r"(?<=[.!?])\s+")
PREVENTED = re.compile(r"\bbefore\s+(?:the|a|an|his|her|their|its|I|we|he|she|they|it|you|[A-Z]\w*)\s+(?:could|would)\s+[a-z]\w+", re.I)
VERIDICAL = re.compile(r"\bbefore\s+(?:the|a|an|his|her|their|its|I|we|he|she|they|[A-Z]\w*)\s+\w+ed\s+\w", re.I)
BAD = re.compile(r"(http|www\.|@|\||#|_{2,}|\[|\]|<|>)")


def main():
    from datasets import load_dataset

    ds = load_dataset("NeelNanda/pile-10k", split="train")
    seen, out, n_sent = set(), [], 0
    for row in ds:
        for s in SENT.split(row["text"]):
            s = " ".join(s.split())
            n_sent += 1
            if not s.endswith(".") or BAD.search(s):
                continue
            if not (8 <= len(s.split()) <= 40) or not s[:1].isupper():
                continue
            if PREVENTED.search(s):
                kind = "prevented"
            elif VERIDICAL.search(s):
                kind = "veridical"
            else:
                continue
            if s.lower() in seen:
                continue
            seen.add(s.lower())
            out.append({"sentence": s, "kind": kind, "source": row["meta"].get("pile_set_name", "?")})

    print(f"scanned {n_sent} sentences")
    print(collections.Counter(r["kind"] for r in out))
    path = os.path.join(PROJ, "data", "natural_before_candidates.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for i, r in enumerate(out, 1):
            r["cand_id"] = f"n{i:03d}"
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(out)} candidates -> {path}")


if __name__ == "__main__":
    main()
