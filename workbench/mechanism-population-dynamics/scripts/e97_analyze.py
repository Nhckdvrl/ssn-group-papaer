"""E97 scoring: after re-initialising a task's top head and training on, who takes over? (preregistered in experiments/E97)

Usage: e97_analyze.py -> prints and writes results/e97/analysis.json
For each lesion tag and each task whose top head was the lesioned head: the take-over head is the head (other than
the lesioned one) whose all-position effect on the task increased most from the pre-lesion map (step100k) to the
post-lesion map (after 1000 steps); its rank in the pre-lesion ordering is the score (prediction: rank 2; lenient
2-4). If an undamaged control map (post-C_ctrl) exists, increases are measured relative to the control's drift.
Also: how much of its pre-lesion effect the lesioned head recovers.
"""
import json

import numpy as np

import mp_common as mc
from e89_analyze import load

DIR = mc.RESULTS / "e97"
TARGETS = {"L5.9": ("5.9", ["successor"]), "L8.9": ("8.9", ["greater_than", "ioi"]), "L6.4": ("6.4", ["sva"]),
           "L9.3": ("9.3", ["gender"]), "L8.10": ("8.10", ["capital"])}


def main():
    H = 12
    pre = load(DIR / "hf__pythia-160m__step100000.npz")
    ctrl_f = DIR / "hf__post-C_ctrl__step1000.npz"
    ctrl = load(ctrl_f) if ctrl_f.exists() else None
    out = {}
    for tag, (head, tasks) in TARGETS.items():
        f = DIR / f"hf__post-{tag}__step1000.npz"
        if not f.exists():
            continue
        post = load(f)
        l, h = map(int, head.split("."))
        for t in tasks:
            A = pre["maps"][(t, "all")].mean(0).ravel()
            B = post["maps"][(t, "all")].mean(0).ravel()
            ref = ctrl["maps"][(t, "all")].mean(0).ravel() if ctrl else A
            gain = B - ref
            idx = l * H + h
            gain[idx] = -np.inf
            taker = int(np.argmax(gain))
            order = [i for i in np.argsort(-A) if i != idx]
            rank = order.index(taker) + 2  # the lesioned head was rank 1
            out[f"{tag}:{t}"] = {"lesioned": head, "taker": f"{taker // H}.{taker % H}", "taker_pre_rank": rank,
                                  "predicted": f"{order[0] // H}.{order[0] % H}", "hit_rank2": rank == 2, "hit_2to4": 2 <= rank <= 4,
                                  "lesioned_recovery": round(float(B[idx] / A[idx]), 3) if A[idx] > 0 else None,
                                  "taker_eff_pre_post": [round(float(A[taker]), 3), round(float(B[taker]), 3)],
                                  "task_metric_pre_post": [round(float(pre["clean"][t].mean()), 2), round(float(post["clean"][t].mean()), 2)],
                                  "top3_post": [f"{i // H}.{i % H}" for i in np.argsort(-B)[:3]]}
            print(f"{tag}:{t}", out[f"{tag}:{t}"], flush=True)
    if out:
        hits = [v["hit_rank2"] for v in out.values()]
        lenient = [v["hit_2to4"] for v in out.values()]
        print(f"rank-2 hits {sum(hits)}/{len(hits)}; rank 2-4 hits {sum(lenient)}/{len(lenient)}; chance per test ~ {1 / 143:.3f} / {3 / 143:.3f}")
    (DIR / "analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
