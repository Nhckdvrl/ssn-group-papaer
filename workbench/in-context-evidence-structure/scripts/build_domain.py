"""E35: domain-partitioned annotators.  Alex = SST-5 poles (movies), Sam = Yelp 1/5 stars (restaurants).
scheme dom  : annotator <-> domain (Alex SST, Sam Yelp)
scheme mixed: each annotator's demos half SST half Yelp (domain independent of annotator); queries likewise
conditions same (both mapping A) / inter (Sam reversed).  Labels negative/positive for both."""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_marked import sst_pool  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 900000))
OUT = ROOT / "data" / os.environ.get("OUT", "domain"); OUT.mkdir(parents=True, exist_ok=True)
NAMES = ("Alex", "Sam")


def yelp_pool():
    from datasets import load_dataset
    ds = load_dataset("Yelp/yelp_review_full")["train"]
    P = {0: [], 1: []}
    for k, r in enumerate(ds):
        if k > 200000:
            break
        t = " ".join(r["text"].replace("\\n", " ").split())
        if r["label"] in (0, 4) and 6 <= len(t.split()) <= 30:
            P[1 if r["label"] == 4 else 0].append(t)
    return P


def main():
    S = sst_pool(); Y = yelp_pool(); print({k: len(v) for k, v in Y.items()})
    lw = ["negative", "positive"]; head = "Below are examples of reviews and their labels.\n\n"; rows = []
    for i in range(N):
        seed = SEED0 + i * 7919; rng = np.random.default_rng(seed); s = i % 2
        cells = [(0, 0)] * 4 + [(0, 1)] * 4 + [(1, 0)] * 4 + [(1, 1)] * 4
        cells = [cells[j] for j in rng.permutation(T)]
        ann = [a for a, _ in cells]; c = [k for _, k in cells]
        # mixed scheme: within each annotator x class, 2 SST + 2 Yelp
        dom_mixed = [0] * T
        for a in (0, 1):
            for k in (0, 1):
                ids = [t for t in range(T) if ann[t] == a and c[t] == k]
                for t in rng.choice(ids, 2, replace=False):
                    dom_mixed[t] = 1
        pick = lambda pool, k: pool[k][int(rng.integers(len(pool[k])))]
        for scheme in ("dom", "mixed"):
            dom = ann if scheme == "dom" else dom_mixed
            xs = [pick(Y if d else S, k) for d, k in zip(dom, c)]
            qdom = {0: 0, 1: 1} if scheme == "dom" else {0: int(rng.integers(2)), 1: int(rng.integers(2))}
            qx = {(qa, qc): pick(Y if qdom[qa] else S, qc) for qa in (0, 1) for qc in (0, 1)}
            for cond in ("same", "inter"):
                ys = [(1 - (k ^ s)) if (a == 1 and cond == "inter") else (k ^ s) for a, k in zip(ann, c)]
                body = "".join(f"Review: {x}\nAnnotator: {NAMES[a]}\nLabel: {lw[y]}\n\n" for x, a, y in zip(xs, ann, ys))
                for qa in (0, 1):
                    for qc in (0, 1):
                        rows.append({"uid": f"sst_{scheme}:{cond}|q{NAMES[qa]}{qc}|dm_{seed}", "cond": f"sst_{scheme}:{cond}", "qann": qa,
                                     "qclass": qc, "base_id": f"dm_{seed}", "labels": ys, "ann": ann, "dom": dom,
                                     "prompt": head + body + f"Review: {qx[(qa, qc)]}\nAnnotator: {NAMES[qa]}\nLabel:",
                                     "cands": [" " + lw[0], " " + lw[1]], "qA": int(qc ^ s), "L": 0})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT); r = rows[5]; print(r["uid"], r["labels"], r["ann"]); print(r["prompt"][-500:])


if __name__ == "__main__":
    main()
