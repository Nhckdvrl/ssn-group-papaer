"""E31: does the context x input interaction leak through shared output labels?  Sam's label vocabulary is moved
progressively away from Alex's: same -> case -> syn -> nonce.  Mapping A (both same) or inter (Sam reversed).
Layout as build_ctxeffect: 8 Alex + 8 Sam demos randomly interleaved, classes balanced within each annotator."""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_marked import sst_pool  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 840000))
OUT = ROOT / "data" / os.environ.get("OUT", "vocabsep"); OUT.mkdir(parents=True, exist_ok=True)
NAMES = ("Alex", "Sam")
NONCE = json.load(open(ROOT / "data" / "lexicon.json"))["labels"]
SYN = {"mag_nat": ["little", "big"], "sst": ["bad", "good"]}


def main():
    P = sst_pool(); rows = []
    for fmt in ("mag_nat", "sst"):
        for i in range(N):
            seed = SEED0 + 1000 * (fmt == "sst") + i * 7919; rng = np.random.default_rng(seed)
            s = i % 2
            cells = [(0, 0)] * 4 + [(0, 1)] * 4 + [(1, 0)] * 4 + [(1, 1)] * 4
            cells = [cells[j] for j in rng.permutation(T)]
            ann = [a for a, _ in cells]; c = [k for _, k in cells]
            if fmt == "mag_nat":
                lw = ["small", "large"]; key = "Number"; head = "Below are examples of numbers and their labels.\n\n"
                p1 = list(rng.choice(np.arange(50, 90), 10, replace=False)); p0 = list(rng.choice(np.arange(10, 50), 10, replace=False))
                xs = [int(p1.pop() if k else p0.pop()) for k in c]; qx = {1: int(p1.pop()), 0: int(p0.pop())}
            else:
                lw = ["negative", "positive"]; key = "Review"; head = "Below are examples of reviews and their labels.\n\n"
                i1 = list(rng.choice(len(P[1]), 10, replace=False)); i0 = list(rng.choice(len(P[0]), 10, replace=False))
                xs = [P[1][i1.pop()] if k else P[0][i0.pop()] for k in c]; qx = {1: P[1][i1.pop()], 0: P[0][i0.pop()]}
            nz = [str(w) for w in rng.choice(NONCE, 2, replace=False)]
            vocabs = {"same": lw, "case": [w.upper() for w in lw], "syn": SYN[fmt], "nonce": nz}
            for vn, sv in vocabs.items():
                for mp in ("A", "inter"):
                    body = ""
                    for t in range(T):
                        yA = c[t] ^ s
                        if ann[t] == 1:
                            y = 1 - yA if mp == "inter" else yA; w = sv[y]
                        else:
                            w = lw[yA]
                        body += f"{key}: {xs[t]}\nAnnotator: {NAMES[ann[t]]}\nLabel: {w}\n\n"
                    for qa in (0, 1):
                        for qc in (0, 1):
                            V = sv if qa == 1 else lw
                            rows.append({"uid": f"{fmt}_{vn}:{mp}|q{NAMES[qa]}{qc}|vs_{fmt}_{seed}", "cond": f"{fmt}_{vn}:{mp}", "qann": qa,
                                         "qclass": qc, "base_id": f"vs_{fmt}_{seed}", "ann": ann,
                                         "prompt": head + body + f"{key}: {qx[qc]}\nAnnotator: {NAMES[qa]}\nLabel:",
                                         "cands": [" " + V[0], " " + V[1]], "qA": int(qc ^ s)})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    r = [x for x in rows if x["cond"] == "sst_nonce:inter" and x["qann"] == 1][0]
    print(r["uid"], r["cands"], "qA", r["qA"]); print(r["prompt"][-420:])


if __name__ == "__main__":
    main()
