"""E30: main effect vs interaction of a context variable (annotator), no temporal structure.

16 demos, 8 Alex + 8 Sam randomly interleaved; classes balanced overall and within Sam (4/4).
  same  : both annotators use mapping A
  inter : Alex A, Sam B (= A reversed)
  main  : Alex A; Sam gives label L on 6 of 8 demos regardless of class, A-mapping on the other 2
Queries: annotator in {Alex, Sam} x class in {0, 1}.  Two candidates (the two label words).
Stored per row: qA (A-mapping answer index), L (main-effect label index) for analysis.
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_marked import sst_pool  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 820000))
OUT = ROOT / "data" / os.environ.get("OUT", "ctxeffect"); OUT.mkdir(parents=True, exist_ok=True)
NAMES = ("Alex", "Sam")
TAGPOS = os.environ.get("TAGPOS", "adj")    # adj: content, Annotator, Label   |   far: Annotator, content, Label


def main():
    P = sst_pool(); rows = []
    for fmt in ("mag_nat", "sst"):
        for i in range(N):
            seed = SEED0 + 1000 * (fmt == "sst") + i * 7919; rng = np.random.default_rng(seed)
            s = i % 2; Lw = (i // 2) % 2
            # annotator x class layout: Alex 4+4, Sam 4+4, random order
            cells = [(0, 0)] * 4 + [(0, 1)] * 4 + [(1, 0)] * 4 + [(1, 1)] * 4      # (annotator, class)
            cells = [cells[j] for j in rng.permutation(T)]
            ann = [a for a, _ in cells]; c = [k for _, k in cells]
            # which 6 of Sam's 8 demos carry the main-effect label (3 per class, so L is class-independent)
            sam_idx = [t for t in range(T) if ann[t] == 1]
            mark = set()
            for k in (0, 1):
                ids = [t for t in sam_idx if c[t] == k]; mark |= set(rng.choice(ids, 3, replace=False).tolist())
            n1 = sum(c) + 2; n0 = T - sum(c) + 2
            if fmt == "mag_nat":
                lw = ["small", "large"]; key = "Number"; head = "Below are examples of numbers and their labels.\n\n"
                p1 = list(rng.choice(np.arange(50, 90), n1, replace=False)); p0 = list(rng.choice(np.arange(10, 50), n0, replace=False))
                xs = [int(p1.pop() if k else p0.pop()) for k in c]; qx = {1: int(p1.pop()), 0: int(p0.pop())}
            else:
                lw = ["negative", "positive"]; key = "Review"; head = "Below are examples of reviews and their labels.\n\n"
                i1 = list(rng.choice(len(P[1]), n1, replace=False)); i0 = list(rng.choice(len(P[0]), n0, replace=False))
                xs = [P[1][i1.pop()] if k else P[0][i0.pop()] for k in c]; qx = {1: P[1][i1.pop()], 0: P[0][i0.pop()]}
            for cond in ("same", "inter", "main"):
                ys = []
                for t in range(T):
                    yA = c[t] ^ s
                    if ann[t] == 1 and cond == "inter":
                        ys.append(1 - yA)
                    elif ann[t] == 1 and cond == "main" and t in mark:
                        ys.append(Lw)
                    else:
                        ys.append(yA)
                if TAGPOS == "far":
                    body = "".join(f"Annotator: {NAMES[a]}\n{key}: {x}\nLabel: {lw[y]}\n\n" for x, a, y in zip(xs, ann, ys))
                else:
                    body = "".join(f"{key}: {x}\nAnnotator: {NAMES[a]}\nLabel: {lw[y]}\n\n" for x, a, y in zip(xs, ann, ys))
                for qa in (0, 1):
                    for qc in (0, 1):
                        rows.append({"uid": f"{fmt}:{cond}|q{NAMES[qa]}{qc}|ce_{fmt}_{seed}", "cond": f"{fmt}:{cond}", "qann": qa,
                                     "qclass": qc, "base_id": f"ce_{fmt}_{seed}", "labels": ys, "ann": ann,
                                     "prompt": head + body + (f"Annotator: {NAMES[qa]}\n{key}: {qx[qc]}\nLabel:" if TAGPOS == "far"
                                                              else f"{key}: {qx[qc]}\nAnnotator: {NAMES[qa]}\nLabel:"),
                                     "cands": [" " + lw[0], " " + lw[1]], "qA": int(qc ^ s), "L": int(Lw)})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    for k in (5, 4 + 4 + 1):
        r = rows[k]; print("-----", r["uid"], "labels", r["labels"], "ann", r["ann"], "qA", r["qA"], "L", r["L"]); print(r["prompt"][-260:])


if __name__ == "__main__":
    main()
