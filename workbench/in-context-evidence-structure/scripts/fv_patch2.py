"""E17b: task-vector transferability for every night_core format (predicts time-sensitivity?).

For each format: on n bases, theta(allA context) vs theta(allB context) at layer L (all layers swept),
patched into a zero-shot prompt with a NEW query; transfer = lo_B(theta_allB) - lo_B(theta_allA).
Also patched test contrasts at the best layer: suffix_4 - disp_4 and noise_2__suffix_3 - suffix_3.

usage: fv_patch2.py --model M --fmts arith,case,... --out OUT.json [--n 60]
"""
import argparse, json, string
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from fv_patch import seq_scores, theta_of

ROOT = Path(__file__).resolve().parents[1]
LET = list(string.ascii_lowercase[1:-1])


def header_of(r):
    return r["prompt"].split("\n\n")[0] + "\n\n"


def demos_and_query(r, fmt, pattern, rng, new_query=False):
    """Re-render the context of row r under `pattern` (string of A/B). If new_query, return a
    zero-shot prompt with a fresh query and candidates [A-answer, B-answer] instead."""
    b = r["base"]; H = header_of(r)
    if fmt in ("arith", "plus1", "plus10", "letter", "condarith"):
        sgn = b["sgn"]; xs = b["xs"]; q = b["q"]
        if fmt == "letter":
            fA = lambda x: chr(ord(x) + sgn); fB = lambda x: chr(ord(x) - sgn)
            pool = [c for c in LET if c not in set(xs) | {q}]
        elif fmt == "condarith":
            fA = lambda x: x + 2 * sgn if x % 2 == 0 else x - 2 * sgn
            fB = lambda x: x - 2 * sgn if x % 2 == 0 else x + 2 * sgn
            pool = [x for x in range(20, 80) if x not in set(xs) | {q}]
        else:
            k = {"arith": 3, "plus1": 1, "plus10": 10}[fmt]
            fA = lambda x: x + sgn * k; fB = lambda x: x - sgn * k
            pool = [x for x in range(20, 80) if x not in set(xs) | {q}]
        if new_query:
            q2 = pool[int(rng.integers(len(pool)))]
            return H + f"Input: {q2}\nOutput:", [f" {fA(q2)}", f" {fB(q2)}"]
        body = "".join(f"Input: {x}\nOutput: {fA(x) if c == 'A' else fB(x)}\n\n" for x, c in zip(xs, pattern))
        return H + body + f"Input: {q}\nOutput:", None
    if fmt == "case":
        ws = b["words"]; q = b["q"]
        F = {"upper": lambda w: w.upper(), "rev": lambda w: w[::-1]}
        fA, fB = F[b["A"]], F[b["B"]]
        if new_query:
            pool = ["window", "garden", "pencil", "silver", "market", "planet", "bottle", "candle", "forest", "rocket"]
            pool = [w for w in pool if w not in ws and w != q]
            q2 = pool[int(rng.integers(len(pool)))]
            return H + f"Input: {q2}\nOutput:", [" " + fA(q2), " " + fB(q2)]
        body = "".join(f"Input: {w}\nOutput: {fA(w) if c == 'A' else fB(w)}\n\n" for w, c in zip(ws, pattern))
        return H + body + f"Input: {q}\nOutput:", None
    if fmt == "stream":
        lw = b["lw"]; item = b["item"]; s = r["query_label_A"]
        if new_query:
            return H + f"Item: {item}\nLabel:", [" " + lw[s], " " + lw[1 - s]]
        body = "".join(f"Item: {item}\nLabel: {lw[s] if c == 'A' else lw[1 - s]}\n\n" for c in pattern)
        return H + body + f"Item: {item}\nLabel:", None
    if fmt in ("parity_nat", "mag_nat"):
        xs = b["xs"]; q = b["q"]; lw = b["lw"]; s = b["s"]
        cls = (lambda x: x % 2) if fmt == "parity_nat" else (lambda x: int(x >= 50))
        if new_query:
            pool = [x for x in range(20, 80) if x not in set(xs) | {q}]
            q2 = pool[int(rng.integers(len(pool)))]; yA = cls(q2) ^ s
            return H + f"Number: {q2}\nLabel:", [" " + lw[yA], " " + lw[1 - yA]]
        body = "".join(f"Number: {x}\nLabel: {lw[(cls(x) ^ s) if c == 'A' else 1 - (cls(x) ^ s)]}\n\n" for x, c in zip(xs, pattern))
        return H + body + f"Number: {q}\nLabel:", None
    if fmt == "sst":
        # texts are only in the prompt; parse them back
        parts = r["prompt"].split("\n\n")[1:-1]
        texts = [p.split("\n")[0][len("Review: "):] for p in parts]
        pol = b["pol"]; lw = b["label_words"]; s = b["s"]
        lab = lambda p: s if p == 1 else 1 - s
        if new_query:
            qtext = "a wonderful , moving and beautifully acted film ." if rng.random() < .5 else "a dull , lifeless and badly written mess ."
            qp = 1 if "wonderful" in qtext else 0
            return H + f"Review: {qtext}\nLabel:", [" " + lw[lab(qp)], " " + lw[1 - lab(qp)]]
        body = "".join(f"Review: {t}\nLabel: {lw[lab(p)] if c == 'A' else lw[1 - lab(p)]}\n\n" for t, p, c in zip(texts, pol, pattern))
        qline = r["prompt"].split("\n\n")[-1]
        return H + body + qline, None
    raise ValueError(fmt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--fmts"); ap.add_argument("--out")
    ap.add_argument("--data", default="night_core"); ap.add_argument("--n", type=int, default=60)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    nL = model.config.num_hidden_layers
    layers = list(range(4, nL - 1, 2))
    rows = {}
    for l in open(ROOT / "data" / a.data / "rows.jsonl"):
        r = json.loads(l); g, p = r["cond"].split(":", 1)
        if p == "allA":
            rows.setdefault(g, []).append(r)
    out = {}
    T = 16
    pats = {"allA": "A" * T, "allB": "B" * T, "suffix_4": "A" * 12 + "B" * 4,
            "disp_4": "".join("B" if i in (3, 7, 11, 15) else "A" for i in range(T)),
            "suffix_3": "A" * 13 + "B" * 3,
            "noise_2__suffix_3": "".join("B" if i in (1, 5) or i >= 13 else "A" for i in range(T))}
    for fmt in a.fmts.split(","):
        rng = np.random.default_rng(0)
        R = rows[fmt][:a.n]
        tr = {L: [] for L in layers}; test = {k: [] for k in ("suffix_4", "disp_4", "suffix_3", "noise_2__suffix_3")}
        cache = []
        for r in R:
            zs, cands = demos_and_query(r, fmt, None, rng, new_query=True)
            th = {k: theta_of(model, tok, demos_and_query(r, fmt, p, rng)[0], layers) for k, p in pats.items()}
            cache.append((zs, cands, th))
            for L in layers:
                sA = seq_scores(model, tok, zs, cands, L, th["allA"][L]); sB = seq_scores(model, tok, zs, cands, L, th["allB"][L])
                tr[L].append((sB[1] - sB[0]) - (sA[1] - sA[0]))
        tm = {L: float(np.mean(v)) for L, v in tr.items()}
        Lb = max(tm, key=tm.get)
        for zs, cands, th in cache:
            for k in test:
                s = seq_scores(model, tok, zs, cands, Lb, th[k][Lb]); test[k].append(s[1] - s[0])
        res = {"transfer_by_layer": tm, "best_layer": Lb, "transfer": tm[Lb],
               "cluster": float(np.mean(np.array(test["suffix_4"]) - np.array(test["disp_4"]))),
               "noise": float(np.mean(np.array(test["noise_2__suffix_3"]) - np.array(test["suffix_3"])))}
        out[fmt] = res
        print(fmt, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items() if k != "transfer_by_layer"}, flush=True)
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
