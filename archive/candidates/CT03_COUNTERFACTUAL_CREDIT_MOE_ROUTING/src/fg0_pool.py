"""CT03 FG0 -- build and LOCK the free-generation dev pool. Zero GPU.

hendrycks_math train, deduplicated against MATH-500 (which is drawn from the
MATH test split, so the pools are already disjoint by construction -- the dedup
is a belt-and-braces check, and it reports how many collisions it found).

The result is written once and must never enter CPD training.
"""
import json, re, random, sys
from datasets import load_dataset

CFGS = ["algebra", "counting_and_probability", "geometry", "intermediate_algebra",
        "number_theory", "prealgebra", "precalculus"]


def boxed(sol):
    k = sol.rfind("\\boxed")
    if k < 0:
        return None
    i = sol.find("{", k)
    if i < 0:
        return None
    d, j = 1, i + 1
    while j < len(sol) and d:
        d += (sol[j] == "{") - (sol[j] == "}")
        j += 1
    return sol[i + 1:j - 1].strip() if d == 0 else None


def norm(s):
    s = re.sub(r"\s+", "", s or "")
    s = s.replace("\\left", "").replace("\\right", "").replace("\\!", "")
    s = s.replace("dfrac", "frac").replace("tfrac", "frac")
    s = s.rstrip(".").replace("\\%", "").replace("%", "")
    if s.startswith("\\text{") and s.endswith("}"):
        s = s[6:-1]
    return s


def main(n, seed, out):
    m500 = {norm(r["problem"]) for r in load_dataset("HuggingFaceH4/MATH-500", split="test")}
    rows, collisions = [], 0
    for c in CFGS:
        for r in load_dataset("EleutherAI/hendrycks_math", c, split="train"):
            if norm(r["problem"]) in m500:
                collisions += 1
                continue
            ans = boxed(r["solution"])
            if ans is None or len(ans) > 24:
                continue
            if not (120 <= len(r["problem"]) + len(r["solution"]) <= 1400):
                continue
            rows.append(dict(cfg=c, level=r.get("level"), type=r.get("type"),
                             problem=r["problem"], solution=r["solution"], answer=ans))
    random.Random(seed).shuffle(rows)
    pool = rows[:n]
    json.dump(dict(source="EleutherAI/hendrycks_math:train", seed=seed,
                   n=len(pool), math500_collisions=collisions, items=pool),
              open(out, "w"), indent=1)
    from collections import Counter
    print(f"candidates after filtering: {len(rows)}   MATH-500 collisions removed: {collisions}")
    print(f"locked pool: {len(pool)}  -> {out}")
    print("levels:", dict(Counter(x["level"] for x in pool)))
    print("types :", dict(Counter(x["cfg"] for x in pool)))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 120,
         0, "results/fg0_devpool.json")
