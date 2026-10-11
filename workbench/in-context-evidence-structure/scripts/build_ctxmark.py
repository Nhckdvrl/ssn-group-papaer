"""E24: regime marked on the INPUT side.  Does the mapping channel bind to a retrievable input context?

A-regime demos carry mark A, B-regime demos carry mark B and the reversed mapping; labels stay lowercase.
  annot : extra line "Annotator: Alex" (A) / "Annotator: Sam" (B); query mark in {A, B, none}
  case  : input key normal (A) / UPPERCASE (B);                       query mark in {A, B}
Two candidates: [A-mapping label, B-mapping label].  Same demo inputs across patterns and query marks.
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa
from build_marked import sst_pool  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 720000))
OUT = ROOT / "data" / os.environ.get("OUT", "ctxmark"); OUT.mkdir(parents=True, exist_ok=True)
NAMES = ("Alex", "Sam")


def pat(b):
    p = ["A"] * T
    for i in b:
        p[i] = "B"
    return "".join(p)


PATS = {"allA": pat([]), "suffix_4": pat(range(12, 16)), "disp_4": pat([3, 7, 11, 15]),
        "noise_2__suffix_3": pat([1, 5, 13, 14, 15]), "suffix_8": pat(range(8, 16)), "prefix_8": pat(range(8)),
        "block_start4": pat(range(4)), "suffix_3": pat(range(13, 16))}
if os.environ.get("PATSEL"):
    PATS = {k: PATS[k] for k in os.environ["PATSEL"].split(",")}
QMARKS = {"annot": ("A", "B", "none"), "case": ("A", "B")}


def demo(key, x, mode, regime):
    if mode == "annot":
        return f"{key}: {x}\nAnnotator: {NAMES[regime == 'B']}\n"
    return f"{key.upper() if regime == 'B' else key}: {x}\n"


def query(key, x, mode, qm):
    if mode == "annot":
        return f"{key}: {x}\n" + ("" if qm == "none" else f"Annotator: {NAMES[qm == 'B']}\n")
    return f"{key.upper() if qm == 'B' else key}: {x}\n"


def main():
    rows = []
    P = sst_pool()
    for fmt in ("mag_nat", "sst"):
        for i in range(N):
            seed = SEED0 + 1000 * (fmt == "sst") + i * 7919; rng = np.random.default_rng(seed)
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
            for mode, qms in QMARKS.items():
                for name, pt in PATS.items():
                    labs = []; body = ""
                    for x, ci, ch in zip(xs, c, pt):
                        yA = int(ci) ^ s; y = yA if ch == "A" else 1 - yA
                        body += demo(key, x, mode, ch) + f"Label: {lw[y]}\n\n"; labs.append(y)
                    o = all_oracles_fast(c[:, None], labs, [qc], 1)
                    v = o["meta_p_rule_query"]; o["meta_pB"] = v if qB == 1 else 1 - v
                    v = o["set_p_rule_query"]; o["set_pB"] = v if qB == 1 else 1 - v
                    for qm in qms:
                        cond = f"{fmt}_{mode}:{name}"
                        rows.append({"uid": f"{cond}|q{qm}|cm_{fmt}_{seed}", "cond": cond, "qmark": qm,
                                     "base_id": f"cm_{fmt}_{seed}", "pattern": pt, "labels": labs,
                                     "prompt": head + body + query(key, qx, mode, qm) + "Label:",
                                     "cands": [" " + lw[qA], " " + lw[qB]], "query_label_A": 0, "query_label_B": 1,
                                     "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    for k in (5 * 3 + 1, 7 * 3 + 5 * 2 + 1):
        print("-----", rows[k]["uid"]); print(rows[k]["prompt"][-330:], rows[k]["cands"])


if __name__ == "__main__":
    main()
