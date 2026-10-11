"""E25: K-class concept drift on natural, widely used datasets (AG News K=4, TREC coarse K=6).

Each base: 16 demos (AG: 4 per class; TREC: 3,3,3,3,2,2 per class), one held-out query text.
Two mappings class -> label word: identity I and a random derangement D (no class keeps its word).
Even bases: A = I, B = D; odd bases: A = D, B = I (so neither regime is uniformly the "natural" one).
Demos follow the A/B pattern; candidates = all K label words; readout logit P(B-label) / P(A-label).
Exact oracle: ices.oracle_perm (all K! bijections, lam x eps grid).
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle_perm import bijections, perm_oracles  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 740000))
OUT = ROOT / "data" / os.environ.get("OUT", "mc"); OUT.mkdir(parents=True, exist_ok=True)
LABELS = os.environ.get("LABELS", "natural")     # natural | letters


def pat(b):
    p = ["A"] * T
    for i in b:
        p[i] = "B"
    return "".join(p)


PATS = {"allA": pat([]), "single_1": pat([0]), "single_16": pat([15]), "suffix_3": pat(range(13, 16)),
        "suffix_4": pat(range(12, 16)), "disp_4": pat([3, 7, 11, 15]), "noise_2__suffix_3": pat([1, 5, 13, 14, 15]),
        "suffix_8": pat(range(8, 16)), "prefix_8": pat(range(8)), "block_start4": pat(range(4)), "allB": pat(range(16))}

TASKS = {
    "agnews": dict(K=4, words=["world", "sports", "business", "technology"], key="Article", lab="Topic",
                   head="Below are examples of news articles and their topics.\n\n"),
    "trec": dict(K=6, words=["abbreviation", "description", "entity", "person", "location", "number"], key="Question",
                 lab="Type", head="Below are examples of questions and their answer types.\n\n"),
}


def pools():
    from datasets import load_dataset
    P = {}
    ag = load_dataset("fancyzhx/ag_news")["train"]
    d = {k: [] for k in range(4)}
    for r in ag:
        t = r["text"].replace("\\", " ").strip()
        if 12 <= len(t.split()) <= 40:
            d[r["label"]].append(t)
    P["agnews"] = d
    tr = load_dataset("CogComp/trec", revision="refs/convert/parquet")["train"]
    # CogComp coarse order: ABBR, ENTY, DESC, HUM, LOC, NUM  -> map to our word order
    remap = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5}
    d = {k: [] for k in range(6)}
    for r in tr:
        d[remap[r["coarse_label"]]].append(r["text"].strip())
    P["trec"] = d
    return P


def derangement(K, rng):
    while True:
        p = rng.permutation(K)
        if np.all(p != np.arange(K)):
            return p


def main():
    P = pools()
    for tk, cfg in TASKS.items():
        print(tk, {k: len(v) for k, v in P[tk].items()})
    rows = []
    for tk, cfg in TASKS.items():
        K = cfg["K"]; Pb = bijections(K); idx = {tuple(p): i for i, p in enumerate(Pb)}
        words = cfg["words"] if LABELS == "natural" else [chr(65 + i) for i in range(K)]
        for i in range(N):
            seed = SEED0 + 1000 * (tk == "trec") + i * 7919; rng = np.random.default_rng(seed)
            counts = [4] * 4 if K == 4 else list(rng.permutation([3, 3, 3, 3, 2, 2]))
            cls = np.array(sum([[k] * c for k, c in enumerate(counts)], []))[rng.permutation(T)]
            qc = int(rng.integers(K))
            texts = {}
            for k in range(K):
                need = int((cls == k).sum()) + (k == qc)
                texts[k] = [P[tk][k][j] for j in rng.choice(len(P[tk][k]), need, replace=False)]
            xs = [texts[c].pop() for c in cls]; qx = texts[qc].pop()
            I = np.arange(K); D = derangement(K, rng)
            A, B = (I, D) if i % 2 == 0 else (D, I)
            for name, pt in PATS.items():
                ys = [int(A[c]) if ch == "A" else int(B[c]) for c, ch in zip(cls, pt)]
                body = "".join(f"{cfg['key']}: {x}\n{cfg['lab']}: {words[y]}\n\n" for x, y in zip(xs, ys))
                o = perm_oracles(cls, ys, qc, K, P=Pb)
                a, b = int(A[qc]), int(B[qc])
                for k in ("meta", "set", "sequence"):
                    pr = o[f"{k}_pred"]; o[f"{k}_pB"] = pr[b] / (pr[a] + pr[b])
                rows.append({"uid": f"{tk}:{name}|mc_{tk}_{seed}", "cond": f"{tk}:{name}", "base_id": f"mc_{tk}_{seed}",
                             "pattern": pt, "labels": ys, "prompt": cfg["head"] + body + f"{cfg['key']}: {qx}\n{cfg['lab']}:",
                             "cands": [" " + w for w in words], "query_label_A": a, "query_label_B": b,
                             "A_is_identity": bool(i % 2 == 0), "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    for k in (7, len(rows) - 4):
        print("-----", rows[k]["uid"], rows[k]["pattern"]); print(rows[k]["prompt"][-400:], rows[k]["cands"], rows[k]["query_label_A"], rows[k]["query_label_B"])


if __name__ == "__main__":
    main()
