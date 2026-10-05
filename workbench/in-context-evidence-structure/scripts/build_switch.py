"""E06: what switches aggregation from time-based to set/similarity-based?

The LABEL STREAM is generated exactly as in E05 d0 (one regime label, flips by A/B
pattern); only the item descriptions differ:
  const : every item 'Item: <name>=<v>' identical                      (= E05 d0)
  irr1  : one binary attribute, random, independent of the label
  irr5  : five binary attributes, random, independent of the label
  ids   : each item is a distinct nonce name 'Item: <word>' (distinct, no shared features)
  rule5 : the E02a rule task (label depends on attribute) for reference
The normative oracle for const/irr*/ids is the label-stream model (inputs carry no
information): we evaluate the oracle on a constant input.
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import Base, episode_record, load_lexicon, make_base, HEADER  # noqa
from ices.oracle import all_oracles_fast  # noqa
import build_dim as bd  # noqa  (conditions)

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 80000))
OUT = ROOT / "data" / os.environ.get("OUT", "switch_pilot_T16"); OUT.mkdir(parents=True, exist_ok=True)
attr_bank, label_bank = load_lexicon(os.environ.get("LEXICON"))
FORMATS = ["const", "irr1", "irr5", "ids", "rule5"]


def labels_stream(pattern, s):
    # regime label index s for A, 1-s for B
    return [s if ch == "A" else 1 - s for ch in pattern]


def render_ids(names, labels, lw, qname):
    parts = [HEADER]
    for n, y in zip(names, labels):
        parts.append(f"Item: {n}\nLabel: {lw[y]}\n\n")
    parts.append(f"Item: {qname}\nLabel:")
    return "".join(parts)


def one(i):
    rows = []
    conds = bd.conditions()
    for fmt in FORMATS:
        seed = SEED0 + 1000 * FORMATS.index(fmt) + i * 7919
        rng = np.random.default_rng(seed)
        while True:
            lw = list(rng.choice(label_bank, 2, replace=False))
            if lw[0][0] != lw[1][0]:
                break
        s = int(rng.integers(2))
        if fmt == "rule5":
            base = make_base(seed, 5, T, attr_bank, label_bank, tag="sw5_")
        elif fmt in ("const", "irr1", "irr5"):
            d = {"const": 1, "irr1": 1, "irr5": 5}[fmt]
            names = list(rng.choice(attr_bank, d, replace=False))
            if fmt == "const":
                v = int(rng.integers(2)); X = [[v]] * T; xq = [v]
            else:
                allx = np.array([[(k >> (d - 1 - j)) & 1 for j in range(d)] for k in range(2 ** d)])
                if d == 5:
                    idx = rng.choice(32, T + 1, replace=False); X = allx[idx[:T]].tolist(); xq = allx[idx[T]].tolist()
                else:
                    X = rng.integers(0, 2, size=(T, 1)).tolist(); xq = rng.integers(0, 2, size=1).tolist()
            # rule_attr/pol unused for label generation here: labels come from the stream
            base = Base(f"sw{fmt}_{seed}", d, T, names, lw, 0, 0, X, xq)
        else:  # ids
            names = list(rng.choice(attr_bank, T + 1, replace=False))
            base = None
        for name, p in conds.items():
            if fmt == "rule5":
                rec = episode_record(base, p, name)
                o = all_oracles_fast(np.array(base.X), rec["labels"], base.xq, 5)
                qb = rec["query_label_B"]
            else:
                labs = labels_stream(p, s)
                if fmt == "ids":
                    prompt = render_ids(names[:T], labs, lw, names[T])
                    rec = {"base_id": f"swids_{seed}", "pattern": p, "labels": labs, "prompt": prompt,
                           "cands": [" " + lw[0], " " + lw[1]], "query_label_A": s, "query_label_B": 1 - s,
                           "base": {"names": names, "label_words": lw, "s": s}}
                else:
                    from ices.generator import render
                    rec = {"base_id": base.base_id, "pattern": p, "labels": labs,
                           "prompt": render(base, labs), "cands": [" " + lw[0], " " + lw[1]],
                           "query_label_A": s, "query_label_B": 1 - s,
                           "base": {"X": base.X, "xq": base.xq, "names": base.attr_names, "label_words": lw, "s": s}}
                # label-stream oracle: constant input, rule (attr 0, polarity = 1 - s) so that label = s for x=1
                o = all_oracles_fast(np.ones((T, 1), int), labs, [1], 1)
                qb = 1 - s
            for k in ("set", "sequence", "meta"):
                v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
            rec.update({"uid": f"{fmt}:{name}|{rec['base_id']}", "cond": f"{fmt}:{name}", "oracle": o})
            rows.append(rec)
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
