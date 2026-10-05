"""Structure grid (E01 calibration + E02 noise-vs-change, one paired design).

Every base (fixed inputs, names, labels words, query) is rendered under ~90 A/B
patterns.  B = demo labelled by the reversed rule.  Readout: LM log-odds of the
query label predicted by the reversed rule (lo_B).

Families (T=16, positions 0-indexed in code, 1-indexed in names):
  allA                    baseline
  single_t                one B at position t                -> position kernel w_t
  pair_i_j                two B                              -> additivity / adjacency
  suffix_k                last k are B                       -> change-like
  disp_k                  k B evenly spread                  -> noise-like
  noise_m__suffix_k       m isolated prefix B + last k B     -> stochasticity x volatility
  block_*                 B block at start / middle          -> transient blocks
  perm3_r                 3 B at random positions (r=0..7)   -> generic dispersion
"""
import json, os, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import episode_record, load_lexicon, make_base  # noqa: E402
from ices.oracle import all_oracles_fast  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
T = int(os.environ.get("T", 16)); N_ATTR = int(os.environ.get("N_ATTR", 5))
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 20000))
OUT = ROOT / "data" / os.environ.get("OUT", f"struct_n{N_ATTR}_T{T}")
OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))


def pat(bpos):
    p = ["A"] * T
    for i in bpos:
        p[i] = "B"
    return "".join(p)


def conditions():
    c = {"allA": pat([])}
    for t in range(T):
        c[f"single_{t+1}"] = pat([t])
    # pairs: adjacent vs separated, anchored at the end and in the middle
    for (i, j) in [(T-2, T-1), (T-3, T-1), (T-5, T-1), (T-9, T-1), (T-3, T-2), (T-4, T-3),
                   (5, 6), (5, 9), (2, T-1), (7, 8), (7, 11)]:
        c[f"pair_{i+1}_{j+1}"] = pat([i, j])
    for k in range(1, 9):
        c[f"suffix_{k}"] = pat(range(T - k, T))
    for k in (2, 3, 4, 6):
        pos = np.round(np.linspace(T / k - 1, T - 1, k)).astype(int)
        c[f"disp_{k}"] = pat(pos)
    noise_order = [1, 5, 8, 3]
    for m in range(0, 5):
        for k in (0, 2, 3, 4, 5):
            if m == 0 and k == 0:
                continue
            c[f"noise_{m}__suffix_{k}"] = pat(list(noise_order[:m]) + list(range(T - k, T)))
    c["block_start4"] = pat(range(0, 4))
    c["block_mid4"] = pat(range(6, 10))
    c["block_late4_return2"] = pat(range(T - 6, T - 2))   # B block then 2 A at the end
    c["late_disp4"] = pat([T - 7, T - 5, T - 3, T - 1])     # alternating in last 7
    rng = np.random.default_rng(12345)
    for r in range(8):
        c[f"perm3_{r}"] = pat(sorted(rng.choice(T, 3, replace=False)))
    return c


def one_base(i):
    conds = conditions()
    rows = []
    if True:
        seed = SEED0 + i * 7919
        base = make_base(seed, N_ATTR, T, attr_bank, label_bank, tag=f"s{N_ATTR}_{T}_")
        X = np.array(base.X)
        for name, p in conds.items():
            rec = episode_record(base, p, name)
            o = all_oracles_fast(X, rec["labels"], base.xq, N_ATTR)
            # express oracle predictions as P(query label = B-label)
            qb = rec["query_label_B"]
            for k in ("set", "sequence", "meta"):
                v = o[f"{k}_p_rule_query"]
                o[f"{k}_pB"] = v if qb == 1 else 1 - v
            rec.update({"uid": f"{name}|{base.base_id}", "oracle": o})
            rows.append(rec)
    return rows


def main():
    from multiprocessing import Pool
    conds = conditions()
    with Pool(int(os.environ.get("NPROC", 32))) as pool:
        rows = [r for rs in pool.map(one_base, range(N)) for r in rs]
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    json.dump(conds, open(OUT / "conditions.json", "w"), indent=1)
    print(len(conds), "conditions x", N, "bases =", len(rows), "rows ->", OUT)


if __name__ == "__main__":
    main()
