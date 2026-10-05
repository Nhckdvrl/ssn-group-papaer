"""E22: concept drift made visible on the output surface.

A-regime demos: lowercase labels with the A mapping; B-regime demos: UPPERCASE labels with the reversed
mapping.  So the regime is perfectly marked by letter case, and the mapping flips with it.
Query candidates (4): [lower A-label, lower B-label, UPPER A-label, UPPER B-label].
Decomposition:  P(upper)  = output-drift tracking;  P(B-map) = mapping tracking;
                P(B-map | upper) = does the model bind the detected regime to the mapping?
Formats: mag_nat (numbers, small/large) and sst (SST-5 two poles, positive/negative).
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.oracle import all_oracles_fast  # noqa

ROOT = Path(__file__).resolve().parents[1]
T = 16
N = int(os.environ.get("N_BASES", 300)); SEED0 = int(os.environ.get("SEED0", 700000))
OUT = ROOT / "data" / os.environ.get("OUT", "marked")
MODE = os.environ.get("MODE", "marked")   # marked | daystamp
OUT.mkdir(parents=True, exist_ok=True)


def pat(b):
    p = ["A"] * T
    for i in b:
        p[i] = "B"
    return "".join(p)


PATS = {"allA": pat([]), "single_1": pat([0]), "single_16": pat([15]), "suffix_3": pat(range(13, 16)),
        "suffix_4": pat(range(12, 16)), "disp_4": pat([3, 7, 11, 15]), "noise_2__suffix_3": pat([1, 5, 13, 14, 15]),
        "suffix_8": pat(range(8, 16)), "prefix_8": pat(range(8)), "block_start4": pat(range(4)),
        "block_late4_return2": pat(range(10, 14))}


def sst_pool():
    from datasets import load_dataset
    ds = load_dataset("SetFit/sst5")["train"]
    P = {0: [], 1: []}
    for r in ds:
        if r["label"] in (0, 4) and 6 <= len(r["text"].split()) <= 25:
            P[1 if r["label"] == 4 else 0].append(r["text"].strip())
    return P


def main():
    rows = []
    P = sst_pool()
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
            for name, pt in PATS.items():
                labs = []; body = ""
                for t, (x, ci, ch) in enumerate(zip(xs, c, pt)):
                    yA = int(ci) ^ s
                    if MODE == "daystamp":
                        y = yA if ch == "A" else 1 - yA
                        body += f"{x} (day {t + 1})\nLabel: {lw[y]}\n\n"; labs.append(y)
                    elif ch == "A":
                        body += f"{x}\nLabel: {lw[yA]}\n\n"; labs.append(yA)
                    else:
                        body += f"{x}\nLabel: {lw[1 - yA].upper()}\n\n"; labs.append(1 - yA)
                qA = qc ^ s; qB = 1 - qA
                qq = q + " (day 17)" if MODE == "daystamp" else q
                if MODE == "daystamp":
                    cands = [" " + lw[qA], " " + lw[qB]]
                else:
                    cands = [" " + lw[qA], " " + lw[qB], " " + lw[qA].upper(), " " + lw[qB].upper()]
                o = all_oracles_fast(c[:, None], labs, [qc], 1)
                v = o["meta_p_rule_query"]; o["meta_pB"] = v if qB == 1 else 1 - v
                v = o["set_p_rule_query"]; o["set_pB"] = v if qB == 1 else 1 - v
                rows.append({"uid": f"{fmt}:{name}|mk_{fmt}_{seed}", "cond": f"{fmt}:{name}", "base_id": f"mk_{fmt}_{seed}",
                             "pattern": pt, "labels": labs, "prompt": head + body + f"{qq}\nLabel:", "cands": cands,
                             "query_label_A": 0, "query_label_B": 1, "oracle": o})
    with open(OUT / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "->", OUT); print(rows[4]["prompt"][-220:], rows[4]["cands"])


if __name__ == "__main__":
    main()
