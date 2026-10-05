"""E24b: shuffled-tag control + contextual oracle for E24 (annot marking).

Same bases/seeds as build_ctxmark (SEED0 720000).  Two tag schemes, query tag in {A (Alex), B (Sam)}:
  annot     : tag = regime (Alex for A demos, Sam for B demos)       -- same prompts as E24
  annotshuf : tag random (8 Alex / 8 Sam), independent of the regime -- control: tag carries no mapping info
binding  = [P(B|qSam) - P(B|qAlex)]_annot - [same]_annotshuf   (same pattern; removes tag-novelty effects)
Contextual oracle: attributes [class, class XOR tag]; the regime-coupled mapping is the rule on (class XOR tag),
so a learner that conditions on the tag has it in its hypothesis space (lam x eps grid as usual).
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
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 720000))
OUT = ROOT / "data" / os.environ.get("OUT", "ctxmark2"); OUT.mkdir(parents=True, exist_ok=True)
NAMES = ("Alex", "Sam")
PATS = {"allA": "A" * 16, "suffix_4": "A" * 12 + "B" * 4, "disp_4": "AAABAAABAAABAAAB", "suffix_8": "A" * 8 + "B" * 8,
        "prefix_8": "B" * 8 + "A" * 8}


def orc(a):
    X, y, xq, qB = a
    o = all_oracles_fast(np.array(X), list(y), list(xq), 2)
    v = o["meta_p_rule_query"]; m = v if qB == 1 else 1 - v
    v = o["set_p_rule_query"]; s = v if qB == 1 else 1 - v
    return {"ctx_meta_pB": m, "ctx_set_pB": s}


def main():
    P = sst_pool(); rows, jobs = [], []
    for fmt in ("mag_nat", "sst"):
        for i in range(N):
            seed = SEED0 + 1000 * (fmt == "sst") + i * 7919; rng = np.random.default_rng(seed)   # identical stream to build_ctxmark
            s = 0 if i % 2 == 0 else 1
            c = np.array([1] * 8 + [0] * 8)[rng.permutation(T)]
            if fmt == "mag_nat":
                lw = ["small", "large"]; key = "Number"; head = "Below are examples of numbers and their labels.\n\n"
                p1 = list(rng.choice(np.arange(50, 90), 9, replace=False)); p0 = list(rng.choice(np.arange(10, 50), 9, replace=False))
                xs = [int(p1.pop() if ci else p0.pop()) for ci in c]
                qc = int(rng.integers(2)); qx = int(p1.pop() if qc else p0.pop())
            else:
                lw = ["negative", "positive"]; key = "Review"; head = "Below are examples of reviews and their labels.\n\n"
                i1 = list(rng.choice(len(P[1]), 9, replace=False)); i0 = list(rng.choice(len(P[0]), 9, replace=False))
                xs = [P[1][i1.pop()] if ci else P[0][i0.pop()] for ci in c]
                qc = int(rng.integers(2)); qx = P[1][i1.pop()] if qc else P[0][i0.pop()]
            qA = qc ^ s; qB = 1 - qA
            shuf = np.array([0] * 8 + [1] * 8)[np.random.default_rng(seed + 1).permutation(T)]
            for scheme in ("annot", "annotshuf"):
                for pn, pt in PATS.items():
                    labs = [(int(ci) ^ s) if ch == "A" else 1 - (int(ci) ^ s) for ci, ch in zip(c, pt)]
                    tags = [int(ch == "B") for ch in pt] if scheme == "annot" else [int(v) for v in shuf]
                    body = "".join(f"{key}: {x}\nAnnotator: {NAMES[g]}\nLabel: {lw[y]}\n\n" for x, g, y in zip(xs, tags, labs))
                    for qm in ("A", "B"):
                        qt = int(qm == "B")
                        rows.append({"uid": f"{fmt}_{scheme}:{pn}|q{qm}|cm_{fmt}_{seed}", "cond": f"{fmt}_{scheme}:{pn}", "qmark": qm,
                                     "base_id": f"cm_{fmt}_{seed}", "pattern": pt, "labels": labs, "tags": tags,
                                     "prompt": head + body + f"{key}: {qx}\nAnnotator: {NAMES[qt]}\nLabel:",
                                     "cands": [" " + lw[qA], " " + lw[qB]], "query_label_A": 0, "query_label_B": 1})
                        X = [(int(ci), int(ci) ^ g) for ci, g in zip(c, tags)]
                        jobs.append((X, labs, (qc, qc ^ qt), qB))
    with Pool(32) as pool:
        res = pool.map(orc, jobs, chunksize=32)
    for r, o in zip(rows, res):
        r["oracle"] = o
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    for k in (6, 7, 26, 27):
        print(rows[k]["uid"], {k2: round(v, 3) for k2, v in rows[k]["oracle"].items()})


if __name__ == "__main__":
    main()
