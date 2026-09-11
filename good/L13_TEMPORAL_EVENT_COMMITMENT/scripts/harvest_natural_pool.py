#!/usr/bin/env python
"""Harvest a large pool of natural `before`-clause sentences for adjudication.

Verbatim sentences from NeelNanda/pile-10k. Surface filtering only; the target
proposition and the realization judgement are supplied by hand afterwards.
Everything that reaches adjudication is recorded, including items later dropped.
"""
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

SENT = re.compile(r"(?<=[.!?])\s+")
# a finite clause under `before`: "before <NP> <verb> ..."
CLAUSE = re.compile(
    r"\bbefore\s+(?:the|a|an|his|her|their|its|my|our|your|I|we|he|she|they|it|you|[A-Z]\w*)\s+\w+",
    re.I,
)
MODAL = re.compile(r"\bbefore\s+\S+(?:\s+\S+)?\s+(?:could|would|can|will|might)\b", re.I)
# "before" used as a preposition or adverb, not a clause
NOT_CLAUSE = re.compile(
    r"\bbefore\s+(?:the\s+)?(?:\d|january|february|march|april|may|june|july|august|"
    r"september|october|november|december|monday|tuesday|wednesday|thursday|friday|"
    r"saturday|sunday|then|long|that|this|me|us|him|her|them|it\b(?!\s+\w+ed))",
    re.I,
)
NOISE = re.compile(r"(http|www\.|@|\||#|_{2,}|\[|\]|<|>|\\)")


def main():
    from datasets import load_dataset

    ds = load_dataset("NeelNanda/pile-10k", split="train")
    seen, pool = set(), []
    for row in ds:
        src = row["meta"].get("pile_set_name", "?")
        for s in SENT.split(row["text"]):
            s = " ".join(s.split())
            if " before " not in s.lower() or NOISE.search(s):
                continue
            if not s.endswith(".") or not s[:1].isupper():
                continue
            if not (8 <= len(s.split()) <= 34):
                continue
            if not CLAUSE.search(s) or NOT_CLAUSE.search(s):
                continue
            k = s.lower()
            if k in seen:
                continue
            seen.add(k)
            pool.append(
                {"sentence": s, "marked_modal": bool(MODAL.search(s)), "source": src}
            )

    for i, r in enumerate(pool, 1):
        r["cand_id"] = f"p{i:04d}"
    path = os.path.join(PROJ, "data", "natural_pool.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in pool:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"pool: {len(pool)}")
    print("modally marked:", sum(r["marked_modal"] for r in pool))
    print(collections.Counter(r["source"] for r in pool).most_common(8))
    print("->", path)


if __name__ == "__main__":
    main()
