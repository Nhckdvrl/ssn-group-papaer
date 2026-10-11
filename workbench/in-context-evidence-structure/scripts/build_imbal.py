"""E28: label flip under class imbalance (12 majority-class / 4 minority-class demos).

The flip then also changes the label marginal.  Two queries per (base, pattern): one of the majority class and one
of the minority class.  Same demos for both.  Exact one-attribute rule oracle.
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
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 800000))
OUT = ROOT / "data" / os.environ.get("OUT", "imbal"); OUT.mkdir(parents=True, exist_ok=True)


def pat(b):
    p = ["A"] * T
    for i in b:
        p[i] = "B"
    return "".join(p)


PATS = {"allA": pat([]), "allB": pat(range(16)), "single_1": pat([0]), "single_16": pat([15]), "suffix_3": pat(range(13, 16)),
        "suffix_4": pat(range(12, 16)), "disp_4": pat([3, 7, 11, 15]), "noise_2__suffix_3": pat([1, 5, 13, 14, 15]),
        "suffix_8": pat(range(8, 16)), "prefix_8": pat(range(8)), "block_start4": pat(range(4))}


def orc(a):
    c, y, qc, qB = a
    o = all_oracles_fast(np.array(c)[:, None], list(y), [qc], 1)
    v = o["meta_p_rule_query"]; m = v if qB == 1 else 1 - v
    v = o["set_p_rule_query"]; s = v if qB == 1 else 1 - v
    return {"meta_pB": m, "set_pB": s}


def main():
    P = sst_pool(); rows, jobs = [], []
    for fmt in os.environ.get("FMTS", "mag_nat,sst").split(","):
        for i in range(N):
            seed = SEED0 + 1000 * (fmt == "sst") + i * 7919; rng = np.random.default_rng(seed)
            s = i % 2                       # A mapping natural (0) or reversed (1)
            maj = (i // 2) % 2              # which class is the majority
            c = np.array([maj] * 12 + [1 - maj] * 4)[rng.permutation(T)]
            n1 = int((c == 1).sum()) + 1; n0 = int((c == 0).sum()) + 1
            if fmt == "condarith":
                # class = parity (1 = even); rule label 1 = "x+2" for that demo.  A: even->x+2, odd->x-2 (s flips)
                ev = [x for x in range(20, 80) if x % 2 == 0]; od = [x for x in range(20, 80) if x % 2 == 1]
                pe = list(rng.choice(ev, n1, replace=False)); po = list(rng.choice(od, n0, replace=False))
                xv = [int(pe.pop() if ci else po.pop()) for ci in c]
                qv = {1: int(pe.pop()), 0: int(po.pop())}
                f = lambda x, up: x + 2 if up else x - 2
                for pn, pt in PATS.items():
                    y = [(int(ci) ^ s) if ch == "A" else 1 - (int(ci) ^ s) for ci, ch in zip(c, pt)]
                    body = "".join(f"Input: {x}\nOutput: {f(x, l)}\n\n" for x, l in zip(xv, y))
                    for qc in (maj, 1 - maj):
                        qA = qc ^ s; qB = 1 - qA; role = "maj" if qc == maj else "min"
                        rows.append({"uid": f"{fmt}:{pn}|{role}|im_{fmt}_{seed}", "cond": f"{fmt}:{pn}", "qrole": role,
                                     "base_id": f"im_{fmt}_{seed}", "pattern": pt, "labels": y,
                                     "prompt": "Below are examples of inputs and outputs.\n\n" + body + f"Input: {qv[qc]}\nOutput:",
                                     "cands": [f" {f(qv[qc], qA)}", f" {f(qv[qc], qB)}"], "query_label_A": 0, "query_label_B": 1})
                        jobs.append(([int(v) for v in c], y, qc, qB))
                continue
            if fmt == "mag_nat":
                lw = ["small", "large"]; head = "Below are examples of numbers and their labels.\n\n"
                p1 = list(rng.choice(np.arange(50, 90), n1, replace=False)); p0 = list(rng.choice(np.arange(10, 50), n0, replace=False))
                xs = [f"Number: {int(p1.pop() if ci else p0.pop())}" for ci in c]
                qs = {1: f"Number: {int(p1.pop())}", 0: f"Number: {int(p0.pop())}"}
            else:
                lw = ["negative", "positive"]; head = "Below are examples of reviews and their labels.\n\n"
                i1 = list(rng.choice(len(P[1]), n1, replace=False)); i0 = list(rng.choice(len(P[0]), n0, replace=False))
                xs = [f"Review: {P[1][i1.pop()] if ci else P[0][i0.pop()]}" for ci in c]
                qs = {1: f"Review: {P[1][i1.pop()]}", 0: f"Review: {P[0][i0.pop()]}"}
            for pn, pt in PATS.items():
                y = [(int(ci) ^ s) if ch == "A" else 1 - (int(ci) ^ s) for ci, ch in zip(c, pt)]
                body = "".join(f"{x}\nLabel: {lw[l]}\n\n" for x, l in zip(xs, y))
                for qc in (maj, 1 - maj):
                    qA = qc ^ s; qB = 1 - qA; role = "maj" if qc == maj else "min"
                    rows.append({"uid": f"{fmt}:{pn}|{role}|im_{fmt}_{seed}", "cond": f"{fmt}:{pn}", "qrole": role,
                                 "base_id": f"im_{fmt}_{seed}", "pattern": pt, "labels": y, "prompt": head + body + f"{qs[qc]}\nLabel:",
                                 "cands": [" " + lw[qA], " " + lw[qB]], "query_label_A": 0, "query_label_B": 1})
                    jobs.append(([int(v) for v in c], y, qc, qB))
    with Pool(32) as pool:
        res = pool.map(orc, jobs, chunksize=32)
    for r, o in zip(rows, res):
        r["oracle"] = o
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT)
    for k in (16, 17):
        r = rows[k]; print("-----", r["uid"], r["pattern"], r["labels"], {a: round(b, 3) for a, b in r["oracle"].items()})
        print(r["prompt"][-200:], r["cands"])


if __name__ == "__main__":
    main()
