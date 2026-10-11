"""E33: spill ratio per label vocabulary vs label-word similarity (bge and model-internal anchors).
usage: analyze_vocabgrad.py MODEL [MODEL ...]"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent


def spill_table(model):
    meta = {}
    for l in open(ROOT / "data/vocabgrad/rows.jsonl"):
        r = json.loads(l); meta[r["uid"]] = r
    recs = []
    for l in open(ROOT / f"results/vocabgrad/{model}.s0.jsonl"):
        s = json.loads(l); r = meta.get(s["uid"])
        if r is None:
            continue
        lp = np.array(s["lp"]); qA = r["qA"]; head = r["cond"].split(":")[0]
        task = "mag_nat" if head.startswith("mag_nat") else "sst"; vn = head[len(task) + 1:]
        recs.append(dict(task=task, vocab=vn, mp=r["cond"].split(":")[1], base=r["base_id"], ann=r["qann"], qc=r["qclass"], pB=lp[1 - qA] - lp[qA]))
    D = pd.DataFrame(recs).drop_duplicates(["task", "vocab", "mp", "base", "ann", "qc"])
    out = []
    for (task, vn), Y in D.groupby(["task", "vocab"]):
        v = Y.pivot_table(index=["base", "qc"], columns=["mp", "ann"], values="pB")
        sam = (v[("inter", 1)] - v[("A", 1)]).mean(); alex = (v[("inter", 0)] - v[("A", 0)]).mean()
        out.append(dict(task=task, vocab=vn, sam_shift=sam, alex_spill=alex, spill_ratio=alex / sam))
    return pd.DataFrame(out)


def main():
    bge = json.load(open(ROOT / "results/vocabgrad/anchor_bge-large-en-v1.5.json"))
    allr = []
    for m in sys.argv[1:]:
        T = spill_table(m)
        try:
            A = json.load(open(ROOT / f"results/vocabgrad/anchor_{m}.json"))
        except FileNotFoundError:
            A = {}
        T["bge"] = [bge[f"{t}:{v}"]["bge"] for t, v in zip(T.task, T.vocab)]
        for k in ("cos_mid", "cos_two_thirds"):
            T[k] = [A.get(f"{t}:{v}", {}).get(k, np.nan) for t, v in zip(T.task, T.vocab)]
        T["model"] = m; allr.append(T)
        print(f"\n##### {m}")
        for task, X in T.groupby("task"):
            X = X.sort_values("spill_ratio", ascending=False)
            print(X[["vocab", "sam_shift", "alex_spill", "spill_ratio", "bge", "cos_mid", "cos_two_thirds"]].round(2).to_string(index=False))
            for k in ("bge", "cos_mid", "cos_two_thirds"):
                if X[k].notna().all():
                    r, p = spearmanr(X[k], X.spill_ratio); print(f"  spearman(spill, {k}) = {r:+.2f} (p={p:.3f}, n={len(X)})")
    R = pd.concat(allr); R.to_csv(ROOT / "results/vocabgrad/summary.csv", index=False)


if __name__ == "__main__":
    main()
