"""E40: randomized demo-level factorial for the evidence-kernel atlas (numbers task).

Per base: mapping direction s, structure tau in {clean, ann, time, noise}, Sam's label vocabulary v in {same, near, far},
query annotator, query class (full factorial cycled over bases).  Per demo: class / annotator / position random
(balanced), value uniform inside its class range.  Each base yields the full prompt and 16 single-demo deletions.
Row fields: uid, base_id, var (-1 = full, t = demo t deleted), prompt, cands, and base metadata in 'meta'.
"""
import json, os
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / os.environ.get("OUT", "kernel"); OUT.mkdir(parents=True, exist_ok=True)
T = 16
N = int(os.environ.get("N_BASES", 960)); SEED0 = int(os.environ.get("SEED0", 940000))
TAUS = ("clean", "ann", "time", "noise")
VOCAB = {"same": ["small", "large"], "near": ["little", "big"], "far": ["A", "B"]}
NAMES = ("Alex", "Sam")
HEAD = "Below are examples of numbers and their labels.\n\n"


def block(x, a, w):
    return f"Number: {x}\nAnnotator: {NAMES[a]}\nLabel: {w}\n\n"


def main():
    rows = []
    for i in range(N):
        tau = TAUS[i % 4]; v = list(VOCAB)[(i // 4) % 3]; qa = (i // 12) % 2; s = (i // 24) % 2; qc = (i // 48) % 2
        seed = SEED0 + i * 7919; rng = np.random.default_rng(seed)
        cells = [(a, c) for a in (0, 1) for c in (0, 1) for _ in range(4)]
        cells = [cells[j] for j in rng.permutation(T)]
        ann = [a for a, _ in cells]; cls = [c for _, c in cells]
        pool1 = list(rng.permutation(np.arange(50, 90))); pool0 = list(rng.permutation(np.arange(10, 50)))
        qx = int(pool1.pop() if qc else pool0.pop())
        xs = [int(pool1.pop() if c else pool0.pop()) for c in cls]
        flip = [0] * T
        if tau == "ann":
            flip = [int(a == 1) for a in ann]
        elif tau == "time":
            flip = [int(t >= 8) for t in range(T)]
        elif tau == "noise":
            for t in rng.choice(T, 3, replace=False):
                flip[int(t)] = 1
        ys = [(c ^ s) ^ f for c, f in zip(cls, flip)]                       # displayed pole
        vocab = [VOCAB["same"] if a == 0 else VOCAB[v] for a in ann]
        words = [vocab[t][ys[t]] for t in range(T)]
        qv = VOCAB["same"] if qa == 0 else VOCAB[v]
        query = f"Number: {qx}\nAnnotator: {NAMES[qa]}\nLabel:"
        meta = {"tau": tau, "v": v, "qa": qa, "s": s, "qc": qc, "qx": qx, "xs": xs, "ann": ann, "cls": cls, "flip": flip,
                "ys": ys, "qA": int(qc ^ s)}
        bid = f"k_{seed}"
        for var in range(-1, T):
            body = "".join(block(xs[t], ann[t], words[t]) for t in range(T) if t != var)
            rows.append({"uid": f"{bid}|{var}", "base_id": bid, "var": var, "prompt": HEAD + body + query,
                         "cands": [" " + qv[0], " " + qv[1]], "meta": meta if var == -1 else None})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    print(rows[0]["prompt"][-400:], rows[0]["cands"], rows[0]["meta"]["tau"], rows[0]["meta"]["v"])


if __name__ == "__main__":
    main()
