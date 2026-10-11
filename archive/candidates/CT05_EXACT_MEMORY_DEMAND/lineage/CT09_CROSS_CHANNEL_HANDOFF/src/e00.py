"""CT09 E00 runner. usage: e00.py MODEL ITEMS OUT SHARD NSHARDS [LIMIT]

Condition = (KV source, recurrent source, hide context KV during query, hide all KV at probe, query).
X in {A, B} is the context; "0" is the shared donor context (third value v0).
Each condition is scored for both values: lp[cond][X + v] = log P(value v | ...).
"""
import json, sys, torch
from handoff import load, prefill, run_rows

CONDS = {
    #            kv          rec         q_drop p_drop query
    "FULL_NAT":  ("X",        "X",        False, False, "late"),
    "FULL_SWAP": ("X",        "0",        False, False, "late"),
    "POST":      ("X",        "0",        False, True,  "late"),   # primary
    "POST_NAT":  ("X",        "X",        False, True,  "late"),
    "PRE":       ("X",        "0",        True,  True,  "late"),   # identical rows by construction
    "RECONLY":   ("X",        "X",        True,  True,  "late"),   # 2609.04434 rec-only
    "RECENT":    ("X_recent", "X_recent", True,  True,  "late"),   # readability ceiling
    "NOREAD":    ("X",        "0",        False, True,  "noread"),
    "E_FULL_SWAP": ("X",      "0",        False, False, "early"),
    "E_POST":    ("X",        "0",        False, True,  "early"),
}
PROBE = {"late": "late", "noread": "late", "early": "early"}


def main():
    path, items, out, shard, ns = sys.argv[1:6]
    limit = int(sys.argv[6]) if len(sys.argv) > 6 else None
    tok, model = load(path)
    rows = [json.loads(l) for l in open(items)]
    rows = [r for r in rows if r["id"] % int(ns) == int(shard)][:limit]
    T = lambda x: torch.tensor(x, device="cuda")
    with open(out, "w") as f:
        for it in rows:
            caches = {k: prefill(model, T(v)) for k, v in it["ctx"].items()}
            res = {}
            for query in ("late", "noread", "early"):
                conds = [c for c, s in CONDS.items() if s[4] == query]
                spec = [(c, X, v) for c in conds for X in "AB" for v in "AB"]
                src = lambda s, X: caches[s.replace("X", X)]
                pr = it["p_" + PROBE[query]]
                lp = run_rows(
                    model, it["N"],
                    [src(CONDS[c][0], X) for c, X, v in spec],
                    [src(CONDS[c][1], X) for c, X, v in spec],
                    T(it["q_" + query]),
                    [CONDS[c][2] for c, X, v in spec],
                    T([pr + it["val_ids"][v] for c, X, v in spec]),
                    [CONDS[c][3] for c, X, v in spec],
                    len(it["val_ids"]["A"]))
                for (c, X, v), x in zip(spec, lp.tolist()):
                    res.setdefault(c, {})[X + v] = x
            f.write(json.dumps(dict(id=it["id"], target_index=it["target_index"], lp=res)) + "\n")
            f.flush()


if __name__ == "__main__":
    main()
