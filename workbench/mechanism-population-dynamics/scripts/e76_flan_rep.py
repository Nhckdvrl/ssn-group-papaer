"""E76: is E48's reversed Flan effect due to the composition of the single part-48 shard?
Protocol: experiments/E76-*.md.
  audit    e76_flan_rep.py --audit     -> results/e76/audit.json   (part-48 prefix vs 10 other part prefixes)
  prep     e76_flan_rep.py --prep      -> e46_data/flan_rep.u16    (10 parts, same decode -> encode pipeline as E48)
  train    e48_cueswap.py --train --size 60M --seed S --cond rep
  analyze  e76_flan_rep.py --analyze   -> results/e76/analysis.json
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np

import mp_common as mc

DATA = Path("/home/xiang/mechpop_cache/e46_data")
OUT = mc.RESULTS / "e76"
EOS = 50279
SHARDS = [f"flanshard{i}" for i in range(10)]
PARTS = [l.split("/part-")[1].split("-")[0] for l in (DATA / "flan_shards.txt").read_text().split()]


def docs(name, n=None, max_tokens=None):
    x = np.memmap(DATA / f"{name}.u16", dtype=np.uint16, mode="r")
    lim = len(x) if max_tokens is None else min(len(x), max_tokens)
    cut = np.flatnonzero(x[:lim] == EOS)
    out, s = [], 0
    for e in cut:
        out.append(np.asarray(x[s:e]))
        s = e + 1
        if n is not None and len(out) >= n:
            break
    return out  # the trailing partial document is dropped


def answer_after(t):
    i = t.rfind("Answer:")
    rest = t[i + len("Answer:"):]
    for line in rest.split("\n"):
        if line.strip():
            return line.strip()
    return ""


def features(t):
    words = t.split()
    nonascii = sum(ord(c) > 127 for c in t) / max(1, len(t))
    digits = sum(c.isdigit() for c in t) / max(1, len(t))
    f = {"has_Question": "Question:" in t, "translation": bool(re.search(r"translat", t, re.I)) or nonascii > 0.2,
         "math": bool(re.search(r"\bsolve\b|math|equation", t, re.I)) or digits > 0.15,
         "has_Q_short": bool(re.search(r"(^|\n)Q:", t)), "words": len(words)}
    if f["has_Question"] and "Answer:" in t:
        pre = t[: t.find("Question:")]
        ans = answer_after(t)
        body = t[: t.rfind("Answer:")]
        f["q_passage80"] = len(pre.split()) >= 80
        f["q_ans_in_context"] = len(ans) >= 3 and ans.rstrip(".") in body
        f["q_ans_short"] = len(ans.split()) <= 5
    return f


def audit(n=3000):
    from e46_train import tokenizer
    tok = tokenizer()
    res = {}
    for name, label in [("flan", "part-48")] + [(s, f"part-{p}") for s, p in zip(SHARDS, PARTS)]:
        T = tok.batch_decode([d.tolist() for d in docs(name, n)])
        F = [features(t) for t in T]
        Q = [f for f in F if "q_passage80" in f]
        row = {"docs": len(F), "frac_Question": np.mean([f["has_Question"] for f in F]),
               "frac_translation": np.mean([f["translation"] for f in F]), "frac_math": np.mean([f["math"] for f in F]),
               "frac_Q_short": np.mean([f["has_Q_short"] for f in F]), "mean_words": np.mean([f["words"] for f in F]),
               "n_QA_docs": len(Q)}
        if Q:
            row |= {"QA_passage80": np.mean([f["q_passage80"] for f in Q]),
                    "QA_answer_in_context": np.mean([f["q_ans_in_context"] for f in Q]),
                    "QA_answer_short": np.mean([f["q_ans_short"] for f in Q])}
        res[label] = {k: (round(float(v), 4) if not isinstance(v, int) else v) for k, v in row.items()}
        print(label, res[label], flush=True)
    others = [v for k, v in res.items() if k != "part-48"]
    verdict = {}
    for k in res["part-48"]:
        if k in ("docs",):
            continue
        vals = [o[k] for o in others if k in o]
        lo, hi = min(vals), max(vals)
        verdict[k] = {"part48": res["part-48"][k], "others_min": lo, "others_max": hi,
                      "inside": bool(lo <= res["part-48"][k] <= hi)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "audit.json").write_text(json.dumps({"per_part": res, "part48_vs_others": verdict}, indent=1))
    print(json.dumps(verdict, indent=1))


def prep(per_shard=8_000_000):
    """Whole documents from the first `per_shard` tokens of each of the 10 parts, shuffled, then the E48
    decode -> encode pipeline (so tokenization matches flan_orig.u16 exactly)."""
    from e46_train import tokenizer
    tok = tokenizer()
    D = []
    for s in SHARDS:
        D += docs(s, max_tokens=per_shard)
    rng = np.random.default_rng(0)
    D = [D[i] for i in rng.permutation(len(D))]
    texts = tok.batch_decode([d.tolist() for d in D])
    ids = tok(texts, add_special_tokens=False)["input_ids"]
    flat = np.concatenate([np.array(i + [EOS], dtype=np.uint16) for i in ids])
    flat.tofile(DATA / "flan_rep.u16")
    stats = {"docs": len(texts), "tokens": int(len(flat)), "docs_with_Question:": sum("Question:" in t for t in texts),
             "Question:": sum(t.count("Question:") for t in texts)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "prep_stats.json").write_text(json.dumps(stats, indent=1))
    print(stats)


def analyze():
    import e18_trait as e18
    from e32_cues import CELLS
    E48 = mc.RESULTS / "e48"
    R = e18.rows()
    cats = sorted({r["cat"] for r in R})
    seeds = ("default", "small-aux-2", "small-aux-3")
    L = {(s, c): json.loads((E48 / f"60M__{s}__{c}.json").read_text()) for s in seeds for c in ("orig", "rep", "none")}
    out = {}
    for t in ("0", "25000000", "50000000", "100000000"):
        if not all(t in v["evals"] for v in L.values()):
            continue
        E = {k: v["evals"][t] for k, v in L.items()}
        sh = sorted(set.intersection(*[set(e["known"]) for e in E.values()]))
        by = [ix for ix in ([i for i in sh if R[i]["cat"] == c] for c in cats) if len(ix) >= 10]

        def eff(e):
            m = {c: float(np.mean([np.mean(np.array(e["cells"][c])[ix]) for ix in by])) for c in CELLS}
            return {c: m[c] - m["decl"] for c in CELLS if c != "decl"} | {"decl_level": m["decl"]}
        F = {k: eff(e) for k, e in E.items()}
        row = {"n_shared_known": len(sh)}
        for a, b in (("orig", "none"), ("rep", "none"), ("rep", "orig")):
            for c in ("QA", "Q_only", "novel", "QA_short", "decl_level"):
                d = np.array([F[(s, a)][c] - F[(s, b)][c] for s in seeds])
                row[f"{a}-{b}|{c}"] = {"delta": float(d.mean()), "se": float(d.std(ddof=1) / np.sqrt(3)),
                                       "per_seed": d.round(3).tolist()}
        out[t] = row
        print(t, len(sh), {k: f"{v['delta']:+.2f}({v['se']:.2f})" for k, v in row.items() if isinstance(v, dict)})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--prep", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    audit() if a.audit else prep() if a.prep else analyze()
