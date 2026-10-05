"""E07: natural-language substrate (external validity).

SST-5 sentences with the two extreme human labels only (0 very negative, 4 very positive;
fine-grained human annotation, so polarity is unambiguous), 6-25 words.  Labels are nonce
words; rule = polarity -> label word (randomised per base).  A/B patterns as in E05
(B = reversed mapping).  Oracle: one binary attribute = gold polarity.
Train split for demos and queries (no model training involved); disjoint sentences per base.
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import load_lexicon  # noqa
from ices.oracle import all_oracles_fast  # noqa
import build_dim as bd  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 90000))
OUT = ROOT / "data" / os.environ.get("OUT", "nl_sst_pilot_T16"); OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))
HEADER = "Below are examples of reviews and their labels.\n\n"


def pool():
    from datasets import load_dataset
    ds = load_dataset("SetFit/sst5")["train"]
    P = {0: [], 1: []}
    for r in ds:
        n = len(r["text"].split())
        if r["label"] in (0, 4) and 6 <= n <= 25:
            P[1 if r["label"] == 4 else 0].append(r["text"].strip())
    return P


def render(texts, labels, lw, qtext):
    parts = [HEADER]
    for t, y in zip(texts, labels):
        parts.append(f"Review: {t}\nLabel: {lw[y]}\n\n")
    parts.append(f"Review: {qtext}\nLabel:")
    return "".join(parts)


def main():
    P = pool()
    print({k: len(v) for k, v in P.items()})
    conds = bd.conditions()
    rows = []
    for i in range(N):
        seed = SEED0 + i * 7919
        rng = np.random.default_rng(seed)
        while True:
            lw = list(rng.choice(label_bank, 2, replace=False))
            if lw[0][0] != lw[1][0]:
                break
        s = int(rng.integers(2))                  # label index of positive under rule A
        pol = np.array([1] * 8 + [0] * 8)[rng.permutation(T)]
        pos = list(rng.choice(len(P[1]), 9, replace=False)); neg = list(rng.choice(len(P[0]), 9, replace=False))
        texts = []
        for p in pol:
            texts.append(P[1][pos.pop()] if p == 1 else P[0][neg.pop()])
        qpol = int(rng.integers(2)); qtext = P[1][pos.pop()] if qpol == 1 else P[0][neg.pop()]
        X = pol[:, None]
        for name, pat in conds.items():
            yA = np.where(pol == 1, s, 1 - s)
            labs = [int(a) if ch == "A" else 1 - int(a) for a, ch in zip(yA, pat)]
            qA = s if qpol == 1 else 1 - s
            o = all_oracles_fast(X, labs, [qpol], 1)
            qb = 1 - qA
            for k in ("set", "sequence", "meta"):
                v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
            rows.append({"uid": f"sst:{name}|sst_{seed}", "cond": f"sst:{name}", "base_id": f"sst_{seed}",
                         "pattern": pat, "labels": labs, "prompt": render(texts, labs, lw, qtext),
                         "cands": [" " + lw[0], " " + lw[1]], "query_label_A": qA, "query_label_B": qb,
                         "base": {"pol": pol.tolist(), "qpol": qpol, "label_words": lw, "s": s},
                         "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "rows ->", OUT)
    print(rows[0]["prompt"][:600])


if __name__ == "__main__":
    main()
