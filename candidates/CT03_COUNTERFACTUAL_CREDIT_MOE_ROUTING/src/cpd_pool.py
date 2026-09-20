"""CPD v1 training pool: MATH train only, disjoint from MATH-500 AND from the
locked FG0 free-generation dev set. NuminaMath is deliberately held back until
the method is shown to work, to keep one variable out of the first round."""
import json, random, sys
from datasets import load_dataset
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fg0_pool import CFGS, boxed, norm

def main(n, seed, out):
    m500 = {norm(r["problem"]) for r in load_dataset("HuggingFaceH4/MATH-500", split="test")}
    fg0 = {norm(x["problem"]) for x in json.load(open("results/fg0_devpool.json"))["items"]}
    rows, c500, cfg0 = [], 0, 0
    for c in CFGS:
        for r in load_dataset("EleutherAI/hendrycks_math", c, split="train"):
            k = norm(r["problem"])
            if k in m500:
                c500 += 1; continue
            if k in fg0:
                cfg0 += 1; continue
            if boxed(r["solution"]) is None:
                continue
            if not (120 <= len(r["problem"]) + len(r["solution"]) <= 1400):
                continue
            rows.append(dict(cfg=c, level=r.get("level"), problem=r["problem"],
                             solution=r["solution"], answer=boxed(r["solution"])))
    random.Random(seed).shuffle(rows)
    pool = rows[:n]
    json.dump(dict(source="EleutherAI/hendrycks_math:train", seed=seed, n=len(pool),
                   excluded_math500=c500, excluded_fg0=cfg0, items=pool),
              open(out, "w"), indent=1)
    print(f"pool {len(pool)} of {len(rows)} eligible | excluded: MATH-500 {c500}, FG0 dev {cfg0}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 600, 1, "results/cpd_trainpool.json")
