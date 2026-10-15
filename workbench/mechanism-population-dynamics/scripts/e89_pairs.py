"""E89 relation classes: which relation between two models preserves which level of the division of labour.

Classes: same run at different checkpoints (lineage ceiling); same init + same data order + deduped data (410M);
Pythia-160M weight-seed (init changed, data order kept) vs data-seed (data order changed, init kept) vs full seed.
Per pair (independent prompt halves, averaged both ways):
  index   correlation of globally standardised head maps by head index (no alignment), mean over tasks
  top1    fraction of tasks whose top head is the same index
  S       correlation of the task-sharing matrices (off-diagonal)
  hub     agreement on which task pairs share a top-3 head (fraction of task pairs with the same yes/no)
Usage: e89_pairs.py -> results/e89/pairs.json
"""
import itertools
import json

import numpy as np

import mp_common as mc
from e89_analyze import load
from e89_analyze2 import S_of, corr, g, off

DIR = mc.RESULTS / "e89"


def name(size, v):
    return f"hf__pythia-{size}{v}__main" if not v.startswith("@") else f"hf__pythia-{size}__{v[1:]}"


CLASSES = {
    "410m lineage (step123k/133k vs 143k)": [("410m", "@step123000", ""), ("410m", "@step133000", "")],
    "410m same init+order, deduped data": [("410m", "-deduped", "")],
    "410m different seed": [("410m", a, b) for a, b in itertools.combinations([""] + [f"-seed{i}" for i in range(1, 10)], 2)],
    "160m init changed, order kept (weight-seed)": [("160m", "", f"-weight-seed{i}") for i in (1, 2, 3)],
    "160m order changed, init kept (data-seed)": [("160m", "", f"-data-seed{i}") for i in (1, 2, 3)],
    "160m weight-seed vs weight-seed (init differs)": [("160m", f"-weight-seed{i}", f"-weight-seed{j}") for i, j in ((1, 2), (1, 3), (2, 3))],
    "160m data-seed vs data-seed (order differs)": [("160m", f"-data-seed{i}", f"-data-seed{j}") for i, j in ((1, 2), (1, 3), (2, 3))],
    "160m different seed": [("160m", a, b) for a, b in itertools.combinations([""] + [f"-seed{i}" for i in range(1, 10)], 2)],
}


def top3(m):
    return set(np.argsort(-m.ravel())[:3].tolist())


def pair_stats(A, B, tasks):
    idx, top1 = [], []
    for t in tasks:
        a0, a1, b0, b1 = (g(A["maps"][(t, "all")][0]), g(A["maps"][(t, "all")][1]),
                          g(B["maps"][(t, "all")][0]), g(B["maps"][(t, "all")][1]))
        idx.append(np.mean([corr(a0, b1), corr(a1, b0)]))
        top1.append(int(np.argmax(A["maps"][(t, "all")].mean(0)) == np.argmax(B["maps"][(t, "all")].mean(0))))
    S = np.mean([corr(off(S_of(A, tasks, 0)), off(S_of(B, tasks, 1))), corr(off(S_of(A, tasks, 1)), off(S_of(B, tasks, 0)))])
    hubA = [len(top3(A["maps"][(i, "all")].mean(0)) & top3(A["maps"][(j, "all")].mean(0))) > 0 for i, j in itertools.combinations(tasks, 2)]
    hubB = [len(top3(B["maps"][(i, "all")].mean(0)) & top3(B["maps"][(j, "all")].mean(0))) > 0 for i, j in itertools.combinations(tasks, 2)]
    return {"index": float(np.mean(idx)), "top1": float(np.mean(top1)), "S": float(S),
            "hub_agree": float(np.mean(np.array(hubA) == np.array(hubB)))}


def main():
    cache, res = {}, {}
    for cls, pairs in CLASSES.items():
        rows = []
        for size, x, y in pairs:
            nx, ny = name(size, x), name(size, y)
            for n in (nx, ny):
                if n not in cache:
                    cache[n] = load(DIR / f"{n}.npz")
            A, B = cache[nx], cache[ny]
            tasks = [t for t in sorted(A["clean"]) if A["clean"][t].mean() > .5 and B["clean"][t].mean() > .5]
            rows.append(pair_stats(A, B, tasks))
        res[cls] = {k: round(float(np.median([r[k] for r in rows])), 3) for k in rows[0]}
        res[cls]["n_pairs"] = len(rows)
        print(f"{cls:48s}", res[cls], flush=True)
    within = {}
    for n, d in cache.items():
        tasks = [t for t in sorted(d["clean"]) if d["clean"][t].mean() > .5]
        within[n] = np.mean([corr(g(d["maps"][(t, "all")][0]), g(d["maps"][(t, "all")][1])) for t in tasks])
    res["split_half_index_ceiling_median"] = round(float(np.median(list(within.values()))), 3)
    print("ceiling", res["split_half_index_ceiling_median"])
    (DIR / "pairs.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
