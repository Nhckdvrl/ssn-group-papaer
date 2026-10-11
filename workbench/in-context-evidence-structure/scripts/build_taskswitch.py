"""E27: switching to another recognizable task vs flipping the labels of the same task.

Numbers 10-89 with attributes even and large (>=50); labels yes/no (1 = yes).
Rules are (attribute, polarity): label = attr ^ polarity.
  switch_pm: A=(even,0)  B=(large,0)      switch_mp: A=(large,0) B=(even,0)
  flip_p:    A=(even,0)  B=(even,1)       flip_m:    A=(large,0) B=(large,1)
16 demos, 4 per cell (even/odd x small/large); query from a cell where the switch tasks disagree
(even-small or odd-large) for every base type.  Exact oracle: 2-attribute rule HMM (ices.oracle).
"""
import json, os, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 780000))
OUT = ROOT / "data" / os.environ.get("OUT", "taskswitch"); OUT.mkdir(parents=True, exist_ok=True)
LW = os.environ.get("LW", "no,yes").split(",")
HEAD = "Below are examples of numbers and their labels.\n\n"
TYPES = {"switch_pm": ((0, 0), (1, 0)), "switch_mp": ((1, 0), (0, 0)), "flip_p": ((0, 0), (0, 1)), "flip_m": ((1, 0), (1, 1))}


def pat(b):
    p = ["A"] * T
    for i in b:
        p[i] = "B"
    return "".join(p)


PATS = {"allA": pat([]), "allB": pat(range(16)), "single_1": pat([0]), "single_16": pat([15]), "suffix_3": pat(range(13, 16)),
        "suffix_4": pat(range(12, 16)), "disp_4": pat([3, 7, 11, 15]), "noise_2__suffix_3": pat([1, 5, 13, 14, 15]),
        "suffix_8": pat(range(8, 16)), "prefix_8": pat(range(8)), "block_start4": pat(range(4))}


def orc(a):
    X, y, xq, qB = a
    o = all_oracles_fast(np.array(X), list(y), list(xq), 2)
    v = o["meta_p_rule_query"]; m = v if qB == 1 else 1 - v
    v = o["set_p_rule_query"]; s = v if qB == 1 else 1 - v
    return {"meta_pB": m, "set_pB": s, "meta_p_volatile": o["meta_p_volatile"]}


def lab(rule, x):
    return x[rule[0]] ^ rule[1]


def main():
    cells = {(e, l): [v for v in range(10, 90) if (v % 2 == 0) == e and (v >= 50) == l] for e in (0, 1) for l in (0, 1)}
    rows, jobs = [], []
    for ti, (tn, (rA, rB)) in enumerate(TYPES.items()):
        for i in range(N):
            seed = SEED0 + 10000 * ti + i * 7919; rng = np.random.default_rng(seed)
            used = set(); xs = []
            for cell in cells:
                pick = rng.choice(cells[cell], 4, replace=False); xs += [int(v) for v in pick]; used |= set(xs)
            xs = [xs[j] for j in rng.permutation(T)]
            qcell = [(1, 0), (0, 1)][int(rng.integers(2))]           # even-small or odd-large
            qx = int(rng.choice([v for v in cells[qcell] if v not in used]))
            attr = lambda v: (int(v % 2 == 0), int(v >= 50))
            Xd = [attr(v) for v in xs]; xq = attr(qx)
            qA = lab(rA, xq); qB = lab(rB, xq); assert qA != qB
            for pn, pt in PATS.items():
                y = [lab(rA, x) if ch == "A" else lab(rB, x) for x, ch in zip(Xd, pt)]
                body = "".join(f"Number: {v}\nLabel: {LW[l]}\n\n" for v, l in zip(xs, y))
                rows.append({"uid": f"{tn}:{pn}|ts_{tn}_{seed}", "cond": f"{tn}:{pn}", "base_id": f"ts_{tn}_{seed}",
                             "pattern": pt, "labels": y, "prompt": HEAD + body + f"Number: {qx}\nLabel:",
                             "cands": [" " + LW[qA], " " + LW[qB]], "query_label_A": 0, "query_label_B": 1})
                jobs.append((Xd, y, xq, qB))
    with Pool(32) as pool:
        res = pool.map(orc, jobs, chunksize=32)
    for r, o in zip(rows, res):
        r["oracle"] = o
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    for k in (8, 3 * 11 * N + 8):
        print("-----", rows[k]["uid"], rows[k]["pattern"], rows[k]["oracle"]); print(rows[k]["prompt"][-160:], rows[k]["cands"])


if __name__ == "__main__":
    main()
