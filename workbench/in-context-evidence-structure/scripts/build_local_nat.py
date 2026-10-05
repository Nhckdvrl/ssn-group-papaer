"""E21: local (exemplar) vs global updating on a NATURAL classification task (small/large numbers).

Each base: 16 demo numbers (8 small <50, 8 large >=50) with natural labels small/large (A = correct
for even bases, flipped for odd bases; B = the other mapping).  Patterns: allA, suffix_8 (8 A then 8 B),
prefix_8 (8 B then 8 A), disp_8.  For each pattern and each class c, two held-out queries of class c:
  near : unseen number of class c closest to the class-c demos that are B-labelled in suffix_8
  far  : unseen number of class c closest to the class-c demos that are A-labelled in suffix_8
(the same two queries are reused for every pattern of the base, so near/far is defined by position in the
suffix_8 ordering).  A rule-level learner predicts identical P(B) for near and far queries.
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 650000))
OUT = ROOT / "data" / os.environ.get("OUT", "local_nat"); OUT.mkdir(parents=True, exist_ok=True)
HEADER = "Below are examples of numbers and their labels.\n\n"
PATS = {"allA": "A" * 16, "suffix_8": "A" * 8 + "B" * 8, "prefix_8": "B" * 8 + "A" * 8, "disp_8": "AB" * 8}


def main():
    rows = []
    cls = lambda x: int(x >= 50)
    for i in range(N):
        seed = SEED0 + i * 7919; rng = np.random.default_rng(seed)
        lw = ["small", "large"]; s = 0 if i % 2 == 0 else 1
        small = list(rng.choice(np.arange(10, 50), 8, replace=False)); large = list(rng.choice(np.arange(50, 90), 8, replace=False))
        xs = [int(v) for v in np.array(small + large)[rng.permutation(16)]]
        # in suffix_8, demos 8..15 are B
        used = set(xs)
        for c in (0, 1):
            pool = [x for x in (range(10, 50) if c == 0 else range(50, 90)) if x not in used]
            Bc = [x for t, x in enumerate(xs) if t >= 8 and cls(x) == c]; Ac = [x for t, x in enumerate(xs) if t < 8 and cls(x) == c]
            if not Bc or not Ac:
                continue
            dist = lambda q, S: min(abs(q - v) for v in S)
            score = [dist(q, Ac) - dist(q, Bc) for q in pool]          # high = near B demos, far from A demos
            near = pool[int(np.argmax(score))]; far = pool[int(np.argmin(score))]
            for tag, q in (("near", near), ("far", far)):
                for pname, pat in PATS.items():
                    labs = [(cls(x) ^ s) if ch == "A" else 1 - (cls(x) ^ s) for x, ch in zip(xs, pat)]
                    qA = cls(q) ^ s
                    prompt = HEADER + "".join(f"Number: {x}\nLabel: {lw[y]}\n\n" for x, y in zip(xs, labs)) + f"Number: {q}\nLabel:"
                    o = all_oracles_fast(np.array([[cls(x)] for x in xs]), labs, [cls(q)], 1)
                    v = o["meta_p_rule_query"]; o["meta_pB"] = v if (1 - qA) == 1 else 1 - v
                    v = o["set_p_rule_query"]; o["set_pB"] = v if (1 - qA) == 1 else 1 - v
                    rows.append({"uid": f"localnat:{pname}|{tag}{c}|ln_{seed}", "cond": f"localnat:{pname}", "qrank": tag,
                                 "base_id": f"ln_{seed}", "pattern": pat, "labels": labs, "prompt": prompt,
                                 "cands": [" " + lw[0], " " + lw[1]], "query_label_A": int(qA), "query_label_B": int(1 - qA),
                                 "escore": float(dist(q, Ac) - dist(q, Bc)), "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)


if __name__ == "__main__":
    main()
