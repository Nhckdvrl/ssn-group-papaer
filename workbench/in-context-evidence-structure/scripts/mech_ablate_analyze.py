"""E39 analysis: behavioral Sam shift, Alex spill, main effect, spill ratio and 'same'-condition task margin under each
ablation, with base-level bootstrap CIs.  usage: mech_ablate_analyze.py results/mech/e39_<tag>.json"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    res = json.loads(Path(sys.argv[1]).read_text())
    meta = {}
    for l in open(ROOT / "data/ctxeffect/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    out = {}
    for task, uids in res["uids"].items():
        names = [k.split("|")[1] for k in res["ld"] if k.startswith(task + "|")]
        bases = sorted({meta[u]["base_id"] for u in uids})
        bi = {b: i for i, b in enumerate(bases)}
        per = {}
        for name in names:
            ld = dict(zip(uids, res["ld"][f"{task}|{name}"]))
            # per base: sam, alex, main, same-task margin
            S = np.zeros((len(bases), 4)); C = np.zeros((len(bases), 4))
            for u in uids:
                r = meta[u]; cond = r["cond"].split(":")[1]
                if cond == "same":
                    sgA = 1.0 if r["qA"] == 1 else -1.0
                    S[bi[r["base_id"]], 3] += sgA * ld[u]; C[bi[r["base_id"]], 3] += 1
                    continue
                us = u.replace(f"{task}:{cond}|", f"{task}:same|")
                d = ld[u] - ld[us]
                if cond == "inter":
                    sg = 1.0 if (1 - r["qA"]) == 1 else -1.0
                    k = 0 if r["qann"] == 1 else 1
                    S[bi[r["base_id"]], k] += sg * d; C[bi[r["base_id"]], k] += 1
                else:  # main: (Sam - Alex) toward L
                    sg = 1.0 if r["L"] == 1 else -1.0
                    S[bi[r["base_id"]], 2] += (1 if r["qann"] == 1 else -1) * sg * d; C[bi[r["base_id"]], 2] += 1
            M = S / np.maximum(C, 1) * np.where(np.arange(4) == 2, 2, 1)
            per[name] = M
        rng = np.random.default_rng(0)
        B = [rng.integers(0, len(bases), len(bases)) for _ in range(1000)]
        row = {}
        for name, M in per.items():
            stat = lambda X: {"sam": X[:, 0].mean(), "alex": X[:, 1].mean(), "main": X[:, 2].mean(),
                              "spill": X[:, 1].mean() / X[:, 0].mean(), "same_margin": X[:, 3].mean()}
            s = stat(M)
            row[name] = {k: round(float(v), 3) for k, v in s.items()}
            if name != "none":
                N = per["none"]
                rel = lambda X, Y, j: X[:, j].mean() / Y[:, j].mean()
                for j, k in enumerate(("sam", "alex", "main", "same_margin")):
                    bs = [rel(M[b], N[b], j) for b in B]
                    row[name][f"{k}_kept"] = round(float(rel(M, N, j)), 3)
                    row[name][f"{k}_kept_ci"] = np.percentile(bs, [2.5, 97.5]).round(3).tolist()
        out[task] = {"n_bases": len(bases), "e36_top20_share": res["sets"][task]["e36_share"], **row}
        print(task, json.dumps(row, indent=0))
    Path(sys.argv[1].replace(".json", "_analysis.json")).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
