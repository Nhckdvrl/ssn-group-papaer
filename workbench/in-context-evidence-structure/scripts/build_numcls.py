"""E15: same domain (two-digit numbers), class-conditional mapping vs global transformation.

Formats (T=16, E05 patterns; 200 bases each; numbers in [20,79], class balanced 8/8 among demos):
  parity_nat : label words 'even'/'odd'; A = correct parity labels, B = flipped (counterbalanced:
               odd bases have A = flipped, B = correct)
  parity_non : nonce label words; A = parity->label mapping, B = reversed mapping
  mag_non    : nonce labels by magnitude (x < 50 vs >= 50); B = reversed mapping
  (global transformation reference: E11b arith, +3 vs -3)
Oracle: rule oracle with one binary attribute = the class (parity / magnitude).
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
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 180000))
OUT = ROOT / "data" / os.environ.get("OUT", "numcls_pilot_T16"); OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))
HEADER = "Below are examples of numbers and their labels.\n\n"


def render(xs, ys, lw, q):
    parts = [HEADER]
    for x, y in zip(xs, ys):
        parts.append(f"Number: {x}\nLabel: {lw[y]}\n\n")
    parts.append(f"Number: {q}\nLabel:")
    return "".join(parts)


def main():
    conds = bd.conditions()
    rows = []
    for fmt in ("parity_nat", "parity_non", "mag_non"):
        for i in range(N):
            seed = SEED0 + 1000 * ("parity_nat", "parity_non", "mag_non").index(fmt) + i * 7919
            rng = np.random.default_rng(seed)
            cls = (lambda x: x % 2) if fmt.startswith("parity") else (lambda x: int(x >= 50))
            pool1 = [x for x in range(20, 80) if cls(x) == 1]; pool0 = [x for x in range(20, 80) if cls(x) == 0]
            c = np.array([1] * 8 + [0] * 8)[rng.permutation(T)]
            p1 = list(rng.choice(pool1, 9, replace=False)); p0 = list(rng.choice(pool0, 9, replace=False))
            xs = [int(p1.pop() if ci == 1 else p0.pop()) for ci in c]
            qc = int(rng.integers(2)); q = int(p1.pop() if qc == 1 else p0.pop())
            if fmt == "parity_nat":
                lw = ["even", "odd"]; s = 0 if i % 2 == 0 else 1     # A: label = class xor s (s=0 correct)
            else:
                while True:
                    lw = list(rng.choice(label_bank, 2, replace=False))
                    if lw[0][0] != lw[1][0]:
                        break
                s = int(rng.integers(2))
            X = c[:, None]
            for name, pat in conds.items():
                yA = c ^ s
                labs = [int(a) if ch == "A" else 1 - int(a) for a, ch in zip(yA, pat)]
                qA = qc ^ s; qb = 1 - qA
                o = all_oracles_fast(X, labs, [qc], 1)
                for k in ("set", "sequence", "meta"):
                    v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
                rows.append({"uid": f"{fmt}:{name}|{fmt}_{seed}", "cond": f"{fmt}:{name}", "base_id": f"{fmt}_{seed}",
                             "pattern": pat, "labels": labs, "prompt": render(xs, labs, lw, q),
                             "cands": [" " + lw[0], " " + lw[1]], "query_label_A": int(qA), "query_label_B": int(qb),
                             "base": {"xs": xs, "q": q, "s": s, "lw": lw}, "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "rows ->", OUT); print(rows[3]["prompt"][-150:])


if __name__ == "__main__":
    main()
