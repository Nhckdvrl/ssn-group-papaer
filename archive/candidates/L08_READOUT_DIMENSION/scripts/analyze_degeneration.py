"""Free-running failure-mode analysis on generations we already have.

E04 showed the damage is confined to the top few candidates (vocabulary size is
irrelevant beyond K~8), and per-step top-1 agreement is 0.62-0.92.  Over a 60-100
token chain, independent per-step failure at those rates predicts essentially zero
chance of reproducing the trajectory -- yet 9-24% of the task accuracy survives.
So the chain is far more error-tolerant than an accumulation account allows, and the
collapse must have a different shape.  This looks at what the collapsed outputs
actually do.
"""
import json, pathlib, re, sys, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]


def rep_stats(text, n=8):
    toks = text.split()
    if len(toks) < n * 2:
        return {"distinct_ratio": 1.0, "max_ngram_rep": 0.0, "loop_start": None}
    grams = [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    c = collections.Counter(grams)
    top, cnt = c.most_common(1)[0]
    loop = None
    if cnt >= 3:
        loop = grams.index(top) / max(1, len(grams))
    return {"distinct_ratio": len(set(toks)) / len(toks),
            "max_ngram_rep": cnt / len(grams),
            "loop_start": loop}


rows = []
for p in sorted((ROOT / "results" / "e01").rglob("*_cot__*.jsonl")):
    lines = [json.loads(l) for l in open(p)]
    meta, recs = lines[0], lines[1:]
    budget = {"gsm8k_gen_cot": 400, "mmlu_gen_cot": 512}[meta["cell"]]
    st = [rep_stats(r["output"]) for r in recs]
    # "ran to the budget" = the generation never produced a stop condition
    lens = np.array([len(r["output"].split()) for r in recs])
    rows.append({
        "model": meta["model"].split("/")[-1], "cell": meta["cell"], "mask": meta["mask"],
        "mean_words": float(lens.mean()),
        "distinct_ratio": float(np.mean([s["distinct_ratio"] for s in st])),
        "frac_looping": float(np.mean([s["max_ngram_rep"] >= 0.10 for s in st])),
        "median_loop_start": float(np.median([s["loop_start"] for s in st
                                              if s["loop_start"] is not None])
                                   if any(s["loop_start"] is not None for s in st) else float("nan")),
    })

print(f"{'model':<28}{'cell':<16}{'mask':<7}{'words':>8}{'distinct':>10}"
      f"{'looping':>9}{'loop@':>8}")
for r in rows:
    print(f"{r['model']:<28}{r['cell']:<16}{r['mask']:<7}{r['mean_words']:>8.1f}"
          f"{r['distinct_ratio']:>10.3f}{r['frac_looping']:>9.3f}"
          f"{r['median_loop_start']:>8.2f}")
print("\ndistinct = distinct/total word ratio;  looping = fraction of outputs whose "
      "most frequent 8-gram covers >=10% of the output;  loop@ = median relative "
      "position where that 8-gram first appears.")
(ROOT / "results" / "degeneration.json").write_text(json.dumps(rows, indent=1))
