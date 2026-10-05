"""E05: does input richness switch evidence aggregation from time-based to similarity-based?

n_attr = 0 : every item has the SAME single feature value (pure label sequence; no retrieval cue)
n_attr = 1, 2, 3, 5 : the usual rule task with that many binary attributes
Identical prompt format and the same A/B patterns (T=16).  For n_attr<=1 the
query input necessarily appears in the context (only 1-2 distinct inputs).
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import Base, episode_record, load_lexicon, make_base  # noqa
from ices.oracle import all_oracles_fast  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 60000))
OUT = ROOT / "data" / os.environ.get("OUT", "dim_pilot_T16"); OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))
DIMS = [0, 1, 2, 3, 5]


def pat(bpos):
    p = ["A"] * T
    for i in bpos:
        p[i] = "B"
    return "".join(p)


def conditions():
    c = {"allA": pat([])}
    for t in (1, 4, 8, 12, 16):
        c[f"single_{t}"] = pat([t - 1])
    for k in range(1, 9):
        c[f"suffix_{k}"] = pat(range(T - k, T))
    for k in (2, 3, 4, 6):
        c[f"disp_{k}"] = pat(np.round(np.linspace(T / k - 1, T - 1, k)).astype(int))
    for m in (2, 4):
        for k in (0, 3, 5):
            c[f"noise_{m}__suffix_{k}"] = pat([1, 5, 8, 3][:m] + list(range(T - k, T)))
    c["block_start4"] = pat(range(0, 4)); c["block_mid4"] = pat(range(6, 10))
    c["block_late4_return2"] = pat(range(T - 6, T - 2))
    return c


def make_const_base(seed):
    rng = np.random.default_rng(seed)
    names = list(rng.choice(attr_bank, 1, replace=False))
    while True:
        lw = list(rng.choice(label_bank, 2, replace=False))
        if lw[0][0] != lw[1][0]:
            break
    v = int(rng.integers(2)); s = int(rng.integers(2))
    return Base(f"d0_{seed}", 1, T, names, lw, 0, s, [[v]] * T, [v])


def make_rep_base(seed, d):
    """demos sampled with replacement (only 2^d inputs); rule attribute balanced;
    distractor agreement with the rule labels <= 0.75."""
    rng = np.random.default_rng(seed)
    names = list(rng.choice(attr_bank, d, replace=False))
    while True:
        lw = list(rng.choice(label_bank, 2, replace=False))
        if lw[0][0] != lw[1][0]:
            break
    a = int(rng.integers(d)); s = int(rng.integers(2))
    while True:
        X = rng.integers(0, 2, size=(T, d))
        X[:, a] = np.array([1] * 8 + [0] * 8)[rng.permutation(T)]
        yA = X[:, a] ^ s
        if all(max(np.mean(X[:, j] == yA), 1 - np.mean(X[:, j] == yA)) <= 0.75 for j in range(d) if j != a):
            break
    xq = rng.integers(0, 2, size=d).tolist()
    return Base(f"d{d}_{seed}", d, T, names, lw, a, s, X.tolist(), xq)


def one(i):
    rows = []
    conds = conditions()
    for d in DIMS:
        seed = SEED0 + 1000 * d + i * 7919
        if d == 0:
            base = make_const_base(seed)
        elif d == 1:
            # balanced single attribute; query is one of the two inputs
            rng = np.random.default_rng(seed)
            names = list(rng.choice(attr_bank, 1, replace=False))
            while True:
                lw = list(rng.choice(label_bank, 2, replace=False))
                if lw[0][0] != lw[1][0]:
                    break
            X = [[1]] * 8 + [[0]] * 8; X = [X[j] for j in rng.permutation(T)]
            base = Base(f"d1_{seed}", 1, T, names, lw, 0, int(rng.integers(2)), X, [int(rng.integers(2))])
        elif d in (2, 3):
            base = make_rep_base(seed, d)
        else:
            base = make_base(seed, d, T, attr_bank, label_bank, tag=f"d{d}_")
        n_eff = base.n_attr
        Xa = np.array(base.X)
        for name, p in conds.items():
            rec = episode_record(base, p, name)
            o = all_oracles_fast(Xa, rec["labels"], base.xq, n_eff)
            qb = rec["query_label_B"]
            for k in ("set", "sequence", "meta"):
                v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
            rec.update({"uid": f"d{d}:{name}|{base.base_id}", "dim": d, "oracle": o})
            rec["cond"] = f"d{d}:{name}"
            rows.append(rec)
    return rows


def main():
    from multiprocessing import Pool
    with Pool(20) as pool:
        rows = [r for rs in pool.map(one, range(N)) for r in rs]
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    json.dump(conditions(), open(OUT / "conditions.json", "w"), indent=1)
    print(len(rows), "rows ->", OUT)


if __name__ == "__main__":
    main()
