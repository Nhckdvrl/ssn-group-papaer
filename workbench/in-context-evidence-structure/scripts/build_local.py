"""E04: local (exemplar) vs global (rule) updating after a change.

For each base and A/B pattern, several held-out queries are rendered.  Queries
are chosen by an a-priori exemplar score
    E(q) = log sum_{t: y_t = lB(q)} s(x_t, q) - log sum_{t: y_t = lA(q)} s(x_t, q),
    s(x, q) = exp(-2 * [x_rule != q_rule] - 1 * #distractor mismatches)
(fixed weights, not fitted), i.e. how strongly *label copying from similar demos*
favours the reversed-rule label.  Every rule-based oracle (set/sequence/meta)
gives the same P(B) for all queries of one context up to the query's own rule
value, so any LM difference between high-E and low-E queries is exemplar-local.

Per (base, pattern): 2 queries with the highest E and 2 with the lowest E
among unseen inputs (ties broken at random); rows tagged qrank = hi1, hi2, lo1, lo2.
"""
import copy, json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import episode_record, load_lexicon, make_base, labels_for  # noqa
from ices.oracle import all_oracles_fast  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16; N_ATTR = 5
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 40000))
OUT = ROOT / "data" / os.environ.get("OUT", "local_pilot_n5_T16"); OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))


def pat(bpos):
    p = ["A"] * T
    for i in bpos:
        p[i] = "B"
    return "".join(p)


PATTERNS = {
    "allA": pat([]),
    "suffix_4": pat(range(12, 16)), "suffix_6": pat(range(10, 16)), "suffix_8": pat(range(8, 16)),
    "disp_4": pat([3, 7, 11, 15]), "disp_8": pat([1, 3, 5, 7, 9, 11, 13, 15]),
    "prefix_8": pat(range(0, 8)),      # B first then A (change back to A): rule says A
}


def escore(X, labels, q, a, lB):
    d_rule = (X[:, a] != q[a]).astype(float)
    m = np.ones(X.shape[1], bool); m[a] = False
    d_dist = (X[:, m] != q[m]).sum(1)
    s = np.exp(-2 * d_rule - 1 * d_dist)
    sb = s[labels == lB].sum() + 1e-9; sa = s[labels != lB].sum() + 1e-9
    return float(np.log(sb) - np.log(sa))


def one_base(i):
    rows = []
    allx = np.array([[(i >> (N_ATTR - 1 - j)) & 1 for j in range(N_ATTR)] for i in range(2 ** N_ATTR)])
    if True:
        seed = SEED0 + i * 7919
        base = make_base(seed, N_ATTR, T, attr_bank, label_bank, tag=f"l{N_ATTR}_{T}_")
        X = np.array(base.X)
        used = {tuple(r) for r in X}
        unseen = np.array([r for r in allx if tuple(r) not in used])
        rng = np.random.default_rng(seed + 1)
        for pname, p in PATTERNS.items():
            labels = np.array(labels_for(base, p))
            sc, ml = [], []
            for q in unseen:
                lA = int(q[base.rule_attr]) ^ base.rule_pol
                sc.append(escore(X, labels, q, base.rule_attr, 1 - lA) + 1e-6 * rng.random())
                o = all_oracles_fast(X, labels, q, N_ATTR)
                pB = o["meta_p_rule_query"] if lA == 0 else 1 - o["meta_p_rule_query"]
                pB = min(max(pB, 1e-6), 1 - 1e-6); ml.append(np.log(pB / (1 - pB)))
            sc, ml = np.array(sc), np.array(ml)
            ok = np.where(np.abs(ml - np.median(ml)) <= 0.5)[0]
            if len(ok) < 4:
                ok = np.argsort(np.abs(ml - np.median(ml)))[:4]
            order = ok[np.argsort(sc[ok])]
            pick = {"lo1": order[0], "lo2": order[1], "hi1": order[-1], "hi2": order[-2]}
            for tag, j in pick.items():
                b2 = copy.deepcopy(base); b2.xq = list(map(int, unseen[j]))
                rec = episode_record(b2, p, pname)
                o = all_oracles_fast(X, rec["labels"], b2.xq, N_ATTR)
                qb = rec["query_label_B"]
                for k in ("set", "sequence", "meta"):
                    v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
                rec.update({"uid": f"{pname}|{tag}|{base.base_id}", "qrank": tag, "escore": sc[j],
                            "oracle": o})
                rows.append(rec)
    return rows


def main():
    from multiprocessing import Pool
    with Pool(20) as pool:
        rows = [r for rs in pool.map(one_base, range(N)) for r in rs]
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "rows ->", OUT)


if __name__ == "__main__":
    main()
