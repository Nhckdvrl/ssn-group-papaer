"""E08: long contexts and surface-run alignment in the RULE task.

Part 1 (long): n_attr=7 (128 inputs), T in {32, 64}; patterns scaled:
  allA, suffix_{T/8, T/4, T/2}, disp_{T/8, T/4, T/2}, noise_{T/8}__suffix_{T/4}, prefix_{T/2} (B then A).
Part 2 (aligned, T=16, n_attr=5): suffix B-items chosen so that their rule attribute equals
  the query's (their B label = the query's B label -> a SURFACE run of one label token at the end),
  vs the same items dispersed; and 'anti-aligned' (suffix items with the opposite rule value:
  their B label = the query's A label word).
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import Base, episode_record, load_lexicon, make_base  # noqa
from ices.oracle import all_oracles_fast  # noqa

ROOT = Path(__file__).resolve().parents[1]
N = int(os.environ.get("N_BASES", 150)); SEED0 = int(os.environ.get("SEED0", 120000))
OUT = ROOT / "data" / os.environ.get("OUT", "long_pilot"); OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))


def pat(T, bpos):
    p = ["A"] * T
    for i in bpos:
        p[i] = "B"
    return "".join(p)


def long_conds(T):
    e, q, h = T // 8, T // 4, T // 2
    sp = lambda k: np.round(np.linspace(T / k - 1, T - 1, k)).astype(int)
    noise = list(np.round(np.linspace(1, T - q - 3, e)).astype(int))
    return {"allA": pat(T, []), f"suffix_{e}": pat(T, range(T - e, T)), f"suffix_{q}": pat(T, range(T - q, T)),
            f"suffix_{h}": pat(T, range(T - h, T)), f"disp_{e}": pat(T, sp(e)), f"disp_{q}": pat(T, sp(q)),
            f"disp_{h}": pat(T, sp(h)), f"noise_{e}__suffix_{q}": pat(T, noise + list(range(T - q, T))),
            f"prefix_{h}": pat(T, range(0, h))}


def add(rows, base, p, name, tag):
    rec = episode_record(base, p, name)
    o = all_oracles_fast(np.array(base.X), rec["labels"], base.xq, base.n_attr)
    qb = rec["query_label_B"]
    for k in ("set", "sequence", "meta"):
        v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
    rec.update({"uid": f"{tag}:{name}|{base.base_id}", "cond": f"{tag}:{name}", "oracle": o})
    rows.append(rec)


def one(i):
    rows = []
    for T in (32, 64):
        base = make_base(SEED0 + 1000 * T + i * 7919, 7, T, attr_bank, label_bank, tag=f"L{T}_")
        for name, p in long_conds(T).items():
            add(rows, base, p, name, f"T{T}")
    # aligned / anti-aligned surface runs, T=16, n_attr=5
    T = 16
    base = make_base(SEED0 + 7 + i * 7919, 5, T, attr_bank, label_bank, tag="AL_")
    X = np.array(base.X); a = base.rule_attr; qa = base.xq[a]
    same = [t for t in range(T) if X[t, a] == qa]; opp = [t for t in range(T) if X[t, a] != qa]
    # reorder demos: put 4 same-class items at the end (aligned) or 4 opposite-class (anti)
    rng = np.random.default_rng(SEED0 + i)
    for kind, pool in (("aligned", same), ("anti", opp)):
        pick = list(rng.choice(pool, 4, replace=False))
        rest = [t for t in range(T) if t not in pick]
        rest = list(rng.permutation(rest))
        order_suffix = rest + pick                                  # picked items in the last 4 slots
        disp_slots = [3, 7, 11, 15]
        order_disp = []
        it_rest = iter(rest); it_pick = iter(pick)
        for s in range(T):
            order_disp.append(next(it_pick) if s in disp_slots else next(it_rest))
        for oname, order in (("suffix4", order_suffix), ("disp4", order_disp)):
            b2 = Base(base.base_id + f"_{kind}_{oname}", 5, T, base.attr_names, base.label_words, a,
                      base.rule_pol, X[order].tolist(), base.xq)
            bpos = [s for s, t in enumerate(order) if t in pick]
            add(rows, b2, pat(T, bpos), f"{kind}_{oname}_B", "AL")
            add(rows, b2, pat(T, []), f"{kind}_{oname}_allA", "AL")
    return rows


def main():
    from multiprocessing import Pool
    with Pool(20) as pool:
        rows = [r for rs in pool.map(one, range(N)) for r in rs]
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "rows ->", OUT)


if __name__ == "__main__":
    main()
