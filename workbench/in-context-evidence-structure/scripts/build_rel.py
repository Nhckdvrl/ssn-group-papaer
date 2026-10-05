"""More RELATIONAL global transformations (regime only visible by relating output to input).

  letter : single lowercase letter b..y -> next letter (A) vs previous letter (B); roles swapped on odd bases
  plus1  : two-digit number -> x+1 (A) vs x-1 (B); roles swapped on odd bases
  plus10 : two-digit number in [20,79] -> x+10 vs x-10
Same 27 A/B patterns (T=16).  Oracle: per-demo A/B evidence stream (inputs carry no regime info).
"""
import json, os, sys, string
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa
import build_dim as bd  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 560000))
OUT = ROOT / "data" / os.environ.get("OUT", "conf_rel"); OUT.mkdir(parents=True, exist_ok=True)
HEADER = "Below are examples of inputs and outputs.\n\n"
LET = list(string.ascii_lowercase[1:-1])        # b..y so that next/prev exist
ALL = ["letter", "plus1", "plus10", "condarith"]
FMTS = os.environ.get("FMTS", "letter,plus1,plus10").split(",")


def render(xs, ys, q):
    return HEADER + "".join(f"Input: {x}\nOutput: {y}\n\n" for x, y in zip(xs, ys)) + f"Input: {q}\nOutput:"


def main():
    conds = bd.conditions(); rows = []
    for fmt in FMTS:
        for i in range(N):
            seed = SEED0 + 1000 * ALL.index(fmt) + i * 7919
            rng = np.random.default_rng(seed); sgn = 1 if i % 2 == 0 else -1
            if fmt == "letter":
                xs = list(rng.choice(LET, T + 1, replace=(T + 1 > len(LET))))
                fA = lambda x: chr(ord(x) + sgn); fB = lambda x: chr(ord(x) - sgn)
            elif fmt == "condarith":
                # class-conditional transformation: A: even -> x+2, odd -> x-2 ; B: even -> x-2, odd -> x+2
                ev = [x for x in range(20, 80) if x % 2 == 0]; od = [x for x in range(20, 80) if x % 2 == 1]
                c = np.array([1] * 8 + [0] * 8)[rng.permutation(T)]
                pe = list(rng.choice(ev, 9, replace=False)); po = list(rng.choice(od, 9, replace=False))
                xs = [int(pe.pop() if ci == 1 else po.pop()) for ci in c] + [int(pe.pop() if rng.random() < .5 else po.pop())]
                fA = (lambda sg: (lambda x: x + 2 * sg if x % 2 == 0 else x - 2 * sg))(sgn)
                fB = (lambda sg: (lambda x: x - 2 * sg if x % 2 == 0 else x + 2 * sg))(sgn)
            else:
                k = 1 if fmt == "plus1" else 10
                xs = [int(v) for v in rng.choice(np.arange(20, 80), T + 1, replace=False)]
                fA = (lambda k: (lambda x: x + sgn * k))(k); fB = (lambda k: (lambda x: x - sgn * k))(k)
            q = xs[T]; xs = xs[:T]
            for name, pat in conds.items():
                ys = [fA(x) if ch == "A" else fB(x) for x, ch in zip(xs, pat)]
                labs = [0 if ch == "A" else 1 for ch in pat]
                o = all_oracles_fast(np.ones((T, 1), int), labs, [1], 1)
                o["meta_pB"] = o["meta_p_rule_query"]; o["set_pB"] = o["set_p_rule_query"]; o["sequence_pB"] = o["sequence_p_rule_query"]
                rows.append({"uid": f"{fmt}:{name}|{fmt}_{seed}", "cond": f"{fmt}:{name}", "base_id": f"{fmt}_{seed}",
                             "pattern": pat, "labels": labs, "prompt": render(xs, ys, q),
                             "cands": [f" {fA(q)}", f" {fB(q)}"], "query_label_A": 0, "query_label_B": 1,
                             "base": {"xs": xs, "q": q, "sgn": sgn}, "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT); print(rows[5]["prompt"][-120:], rows[5]["cands"])


if __name__ == "__main__":
    main()
