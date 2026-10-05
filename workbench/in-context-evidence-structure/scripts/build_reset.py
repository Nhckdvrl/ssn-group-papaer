"""E26: deletion-influence profiles -- does a detected change point discount pre-change demos?

Same base construction as E22 (build_marked).  Patterns suffix_8 / disp_8 / allA; for each, the full prompt and
the 16 prompts with demo t deleted.  Presentations: plain (2 candidates) and marked (B demos uppercase, 4 cands).
"""
import json, os, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa
from build_marked import sst_pool  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 200)); SEED0 = int(os.environ.get("SEED0", 760000))
OUT = ROOT / "data" / os.environ.get("OUT", "reset"); OUT.mkdir(parents=True, exist_ok=True)
PATS = {"suffix_8": "A" * 8 + "B" * 8, "disp_8": "AB" * 8, "allA": "A" * 16}


def orc(args):
    c, labs, qc, qB = args
    o = all_oracles_fast(np.array(c)[:, None], list(labs), [qc], 1)
    v = o["meta_p_rule_query"]; mpB = v if qB == 1 else 1 - v
    v = o["set_p_rule_query"]; spB = v if qB == 1 else 1 - v
    return {"meta_pB": mpB, "set_pB": spB, "meta_p_volatile": o["meta_p_volatile"]}


def main():
    P = sst_pool()
    items = []
    for fmt in ("mag_nat", "sst"):
        for i in range(N):
            seed = SEED0 + 1000 * (fmt == "sst") + i * 7919; rng = np.random.default_rng(seed)
            s = 0 if i % 2 == 0 else 1
            c = np.array([1] * 8 + [0] * 8)[rng.permutation(T)]
            if fmt == "mag_nat":
                lw = ["small", "large"]; head = "Below are examples of numbers and their labels.\n\n"
                p1 = list(rng.choice(np.arange(50, 90), 9, replace=False)); p0 = list(rng.choice(np.arange(10, 50), 9, replace=False))
                xs = [f"Number: {int(p1.pop() if ci else p0.pop())}" for ci in c]
                qc = int(rng.integers(2)); q = f"Number: {int(p1.pop() if qc else p0.pop())}"
            else:
                lw = ["negative", "positive"]; head = "Below are examples of reviews and their labels.\n\n"
                i1 = list(rng.choice(len(P[1]), 9, replace=False)); i0 = list(rng.choice(len(P[0]), 9, replace=False))
                xs = [f"Review: {P[1][i1.pop()] if ci else P[0][i0.pop()]}" for ci in c]
                qc = int(rng.integers(2)); q = f"Review: {P[1][i1.pop()] if qc else P[0][i0.pop()]}"
            qA = qc ^ s; qB = 1 - qA
            items.append((fmt, seed, c, xs, q, qc, qA, qB, lw, head))
    jobs, keys = [], []
    for fmt, seed, c, xs, q, qc, qA, qB, lw, head in items:
        for pn, pt in PATS.items():
            labs = [(int(ci) ^ (qc ^ qA)) if ch == "A" else 1 - (int(ci) ^ (qc ^ qA)) for ci, ch in zip(c, pt)]
            for d in [None] + list(range(T)):
                keep = [t for t in range(T) if t != d]
                jobs.append(([int(c[t]) for t in keep], [labs[t] for t in keep], qc, qB)); keys.append((fmt, seed, pn, d, labs))
    with Pool(32) as pool:
        res = pool.map(orc, jobs, chunksize=64)
    meta = {(k[0], k[1], k[2], k[3]): r for k, r in zip(keys, res)}
    rows = []
    for fmt, seed, c, xs, q, qc, qA, qB, lw, head in items:
        for pn, pt in PATS.items():
            labs = [(int(ci) ^ (qc ^ qA)) if ch == "A" else 1 - (int(ci) ^ (qc ^ qA)) for ci, ch in zip(c, pt)]
            for pres in ("plain", "marked"):
                for d in [None] + list(range(T)):
                    body = ""
                    for t in range(T):
                        if t == d:
                            continue
                        w = lw[labs[t]]
                        body += f"{xs[t]}\nLabel: {w.upper() if (pres == 'marked' and pt[t] == 'B') else w}\n\n"
                    cands = [" " + lw[qA], " " + lw[qB]] + ([" " + lw[qA].upper(), " " + lw[qB].upper()] if pres == "marked" else [])
                    dd = "full" if d is None else f"d{d}"
                    rows.append({"uid": f"{fmt}_{pres}:{pn}|{dd}|rs_{fmt}_{seed}", "cond": f"{fmt}_{pres}:{pn}", "del": d,
                                 "base_id": f"rs_{fmt}_{seed}", "pattern": pt, "labels": labs, "same_class": [int(ci == qc) for ci in c],
                                 "prompt": head + body + f"{q}\nLabel:", "cands": cands, "query_label_A": 0, "query_label_B": 1,
                                 "oracle": meta[(fmt, seed, pn, d)]})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    r = [x for x in rows if x["cond"] == "sst_marked:suffix_8" and x["del"] == 3][0]
    print(r["uid"], r["labels"], r["same_class"]); print(r["prompt"][-500:], r["cands"])


if __name__ == "__main__":
    main()
