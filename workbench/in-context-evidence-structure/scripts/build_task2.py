"""E11b: familiar but RELATIONAL task switch, vs surface-identifiable controls.

Formats (T=16, same A/B patterns as E05):
  arith   : x -> x+3 (A) vs x -> x-3 (B); x two-digit in [20, 79]; outputs are ordinary numbers,
            so which task produced a demo is only visible by relating output to input.
  arith_sw: roles swapped (A = -3, B = +3) for counterbalancing (merged in analysis)
  case    : x -> UPPER(x) vs x -> reversed(x) (E11; surface-identifiable) -- already run
  parity  : surface-identifiable arithmetic control: A: x -> x+3 written as digits, B: x -> x-3
            written in words? (not used)
Readout: exact log-odds of the B-task answer vs the A-task answer for the query number.
Oracle: label-stream style (each demo is A/B evidence; inputs uninformative about the task).
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa
import build_dim as bd  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 160000))
OUT = ROOT / "data" / os.environ.get("OUT", "task2_pilot_T16"); OUT.mkdir(parents=True, exist_ok=True)
HEADER = "Below are examples of inputs and outputs.\n\n"
K = 3


def render(xs, ys, q):
    parts = [HEADER]
    for x, y in zip(xs, ys):
        parts.append(f"Input: {x}\nOutput: {y}\n\n")
    parts.append(f"Input: {q}\nOutput:")
    return "".join(parts)


def main():
    conds = bd.conditions()
    rows = []
    for i in range(N):
        seed = SEED0 + i * 7919
        rng = np.random.default_rng(seed)
        sgn = 1 if i % 2 == 0 else -1          # A = +3 (even bases) or -3 (odd bases)
        fA = lambda x: x + sgn * K; fB = lambda x: x - sgn * K
        xs = [int(v) for v in rng.choice(np.arange(20, 80), T + 1, replace=False)]
        q = xs[T]; xs = xs[:T]
        for name, pat in conds.items():
            ys = [fA(x) if ch == "A" else fB(x) for x, ch in zip(xs, pat)]
            labs = [0 if ch == "A" else 1 for ch in pat]
            o = all_oracles_fast(np.ones((T, 1), int), labs, [1], 1)
            o["meta_pB"] = o["meta_p_rule_query"]; o["set_pB"] = o["set_p_rule_query"]; o["sequence_pB"] = o["sequence_p_rule_query"]
            rows.append({"uid": f"arith:{name}|ar_{seed}", "cond": f"arith:{name}", "base_id": f"ar_{seed}",
                         "pattern": pat, "labels": labs, "prompt": render(xs, ys, q),
                         "cands": [f" {fA(q)}", f" {fB(q)}"], "query_label_A": 0, "query_label_B": 1,
                         "base": {"xs": xs, "q": q, "sgn": sgn}, "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "rows ->", OUT); print(rows[5]["prompt"][-200:])


if __name__ == "__main__":
    main()
