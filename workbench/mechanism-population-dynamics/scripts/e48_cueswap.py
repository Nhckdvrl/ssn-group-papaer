"""E48: causal data intervention for C04 -- does rewriting the Flan template move the trigger of the switch?

Protocol: experiments/E48-*.md.
  prep   e48_cueswap.py --prep                     -> e46_data/flan_orig.u16, flan_swap.u16 (+ marker counts)
  train  e48_cueswap.py --train --size 90M --seed default --cond orig|swap|none
  analyze e48_cueswap.py --analyze
Continued pretraining of DataDecide dolma1_7-no-flan-<size> (final) on a fixed base mix in which a fraction P_FLAN of
the sequences are Flan (original template), Flan with "Question:"->"Query:" and "Answer:"->"Response:", or base text
(control). All three conditions share the RNG for slot assignment and base windows; only the Flan slots differ.
The E32 readout (cue cells, clean knowledge) is measured on the in-memory model at fixed token counts.
"""
import argparse
import json
import math
import re
import time
from pathlib import Path

import numpy as np
import torch

import mp_common as mc

DATA = Path("/home/xiang/mechpop_cache/e46_data")
OUT = mc.RESULTS / "e48"
EOS = 50279
SEQ, BS, MICRO, LR, WARM = 2048, 32, 4, 3e-4, 100
TOKENS = 200_000_000
EVAL_AT = (0, 25_000_000, 50_000_000, 100_000_000, 200_000_000)
P_FLAN = 0.10
BASE = {"c4": 0.5, "books": 0.15, "papers": 0.15, "code": 0.2}
SWAP = (("Question:", "Query:"), ("Answer:", "Response:"))
FINAL = {  # common final step of dolma1_7 / no-flan per seed (E47 job list)
    "60M": {"default": 29052, "small-aux-2": 29042, "small-aux-3": 29042},
    "90M": {"default": 29901, "small-aux-2": 29901, "small-aux-3": 29901}}


def tokenizer():
    from e46_train import tokenizer as t
    return t()


def prep(max_tokens=80_000_000):
    """Decode Flan documents, apply the same decode->(rewrite)->encode pipeline to both conditions."""
    tok = tokenizer()
    x = np.memmap(DATA / "flan.u16", dtype=np.uint16, mode="r")
    cut = np.flatnonzero(x[: max_tokens * 2] == EOS)
    docs, s = [], 0
    for e in cut:
        docs.append(x[s:e])
        s = e + 1
        if s > max_tokens:
            break
    texts = tok.batch_decode([d.tolist() for d in docs])
    count = lambda pat: sum(t.count(pat) for t in texts)
    stats = {"docs": len(texts), "Question:": count("Question:"), "Answer:": count("Answer:"), "Q:": count("Q:"),
             "A:": count("A:"), "question:": count("question:"), "answer:": count("answer:"),
             "QUESTION:": count("QUESTION:"), "Query:": count("Query:"), "Response:": count("Response:"),
             "docs_with_Question:": sum("Question:" in t for t in texts)}
    swapped = []
    for t in texts:
        for a, b in SWAP:
            t = t.replace(a, b)
        swapped.append(t)
    stats["after_swap_Question:"] = sum(t.count("Question:") for t in swapped)
    stats["after_swap_Query:"] = sum(t.count("Query:") for t in swapped)
    for name, T in (("orig", texts), ("swap", swapped)):
        ids = tok(T, add_special_tokens=False)["input_ids"]
        flat = np.concatenate([np.array(i + [EOS], dtype=np.uint16) for i in ids])
        flat.tofile(DATA / f"flan_{name}.u16")
        stats[f"tokens_{name}"] = int(len(flat))
    (DATA / "flan_prep_stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


class Mix:
    """Per-sequence slot assignment and base windows from one RNG (identical across conditions); Flan windows from
    a second RNG over the condition's Flan file (same offsets for orig / swap up to the files' length difference)."""

    def __init__(self, cond, seed):
        self.base = {k: np.memmap(DATA / f"{k}.u16", dtype=np.uint16, mode="r") for k in BASE}
        self.names, self.p = list(BASE), np.array(list(BASE.values()))
        self.flan = None if cond == "none" else np.memmap(DATA / f"flan_{cond}.u16", dtype=np.uint16, mode="r")
        self.rng, self.frng = np.random.default_rng(seed), np.random.default_rng(seed + 1)

    def next(self):
        rows = []
        for _ in range(BS):
            is_flan = self.rng.random() < P_FLAN
            src = self.names[self.rng.choice(len(self.names), p=self.p)]
            x = self.base[src]
            off = self.rng.integers(0, len(x) - SEQ - 1)
            foff = self.frng.random()
            if is_flan and self.flan is not None:
                o = int(foff * (len(self.flan) - SEQ - 1))
                rows.append(self.flan[o:o + SEQ + 1])
            else:
                rows.append(x[off:off + SEQ + 1])
        return torch.from_numpy(np.stack(rows).astype(np.int64))


@torch.no_grad()
def readout(model, tok):
    import e18_trait as e18
    from e20_recipe import cand_logprob
    from e32_cues import CELLS, build_all
    model.eval()
    R = e18.rows()
    B = build_all(R)
    D, A = [r["dist"] for r in R], [r["ans"] for r in R]
    clean = [r["clean"] for r in R]
    res = {"known": np.flatnonzero(cand_logprob(model, tok, clean, A) > cand_logprob(model, tok, clean, D)).tolist(),
           "cells": {}}
    for c in CELLS:
        P = [b[c] for b in B]
        res["cells"][c] = (cand_logprob(model, tok, P, D) - cand_logprob(model, tok, P, A)).round(4).tolist()
    model.train()
    return res


def train(size, seed, cond):
    import dd_common as dd
    name = f"{size}__{seed}__{cond}"
    f = OUT / f"{name}.json"
    if f.exists():
        return
    OUT.mkdir(exist_ok=True)
    torch.backends.cuda.matmul.allow_tf32 = True
    model, tok = dd.load(f"allenai/DataDecide-dolma1_7-no-flan-{size}", dd.rev(FINAL[size][seed], seed), dtype=torch.float32)
    model.config._attn_implementation = "sdpa"
    opt = torch.optim.AdamW(model.parameters(), lr=LR, betas=(0.9, 0.95), weight_decay=0.1, eps=1e-8)
    steps = TOKENS // (BS * SEQ)
    lr_at = lambda s: LR * min(1.0, (s + 1) / WARM) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * s / steps)))
    data = Mix(cond, seed={"default": 1, "small-aux-2": 2, "small-aux-3": 3}[seed])
    log = {"name": name, "size": size, "seed": seed, "cond": cond, "p_flan": P_FLAN, "evals": {}, "loss": {}}
    evals = {t // (BS * SEQ): t for t in EVAL_AT}
    t0 = time.time()
    model.train()
    for step in range(steps + 1):
        if step in evals:
            log["evals"][evals[step]] = readout(model, tok)
            c = log["evals"][evals[step]]["cells"]
            print(name, evals[step], {k: round(float(np.mean(v)), 2) for k, v in c.items()}, f"{time.time() - t0:.0f}s",
                  flush=True)
        if step == steps:
            break
        x = data.next().cuda(non_blocking=True)
        for g in opt.param_groups:
            g["lr"] = lr_at(step)
        opt.zero_grad(set_to_none=True)
        tot = 0.0
        for xc in x.chunk(MICRO):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(xc[:, :-1]).logits
            loss = torch.nn.functional.cross_entropy(logits.float().reshape(-1, logits.shape[-1]),
                                                     xc[:, 1:].reshape(-1)) / MICRO
            loss.backward()
            tot += float(loss)
            del logits, loss
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % 50 == 0:
            log["loss"][step] = tot
    log["seconds"] = time.time() - t0
    f.write_text(json.dumps(log))


def analyze():
    import e18_trait as e18
    from e32_cues import CELLS
    R = e18.rows()
    cats = sorted({r["cat"] for r in R})
    seeds = ("default", "small-aux-2", "small-aux-3")
    out = {}
    for size in FINAL:
        L = {(s, c): json.loads((OUT / f"{size}__{s}__{c}.json").read_text())
             for s in seeds for c in ("orig", "swap", "none") if (OUT / f"{size}__{s}__{c}.json").exists()}
        if len(L) < 9:
            continue
        out[size] = {}
        for t in map(str, EVAL_AT):
            E = {k: v["evals"][t] for k, v in L.items()}
            sh = sorted(set.intersection(*[set(e["known"]) for e in E.values()]))
            by = [ix for ix in ([i for i in sh if R[i]["cat"] == c] for c in cats) if len(ix) >= 10]

            def eff(e):
                m = {c: float(np.mean([np.mean(np.array(e["cells"][c])[ix]) for ix in by])) for c in CELLS}
                return {c: m[c] - m["decl"] for c in CELLS if c != "decl"} | {"decl_level": m["decl"]}
            F = {k: eff(e) for k, e in E.items()}
            row = {"n_shared_known": len(sh)}
            for cond in ("orig", "swap"):
                for c in ("QA", "Q_only", "A_only", "novel", "QA_short", "decl_level"):
                    d = np.array([F[(s, cond)][c] - F[(s, "none")][c] for s in seeds])  # paired by init
                    row[f"{cond}-none|{c}"] = {"delta": float(d.mean()), "se": float(d.std(ddof=1) / np.sqrt(3)),
                                               "per_seed": d.round(3).tolist()}
            for cond, a, b in (("orig", "QA", "novel"), ("swap", "novel", "QA")):
                d = np.array([(F[(s, cond)][a] - F[(s, "none")][a]) - (F[(s, cond)][b] - F[(s, "none")][b]) for s in seeds])
                row[f"specificity_{cond}:{a}>{b}"] = {"delta": float(d.mean()), "se": float(d.std(ddof=1) / np.sqrt(3))}
            out[size][t] = row
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    for size, rows in out.items():
        for t, r in rows.items():
            print(size, t, r["n_shared_known"], {k: f"{v['delta']:+.2f}({v['se']:.2f})" for k, v in r.items()
                                                  if isinstance(v, dict) and ("QA" in k or "novel" in k or "spec" in k)})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", action="store_true")
    ap.add_argument("--train", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--size")
    ap.add_argument("--seed")
    ap.add_argument("--cond", choices=["orig", "swap", "none"])
    a = ap.parse_args()
    if a.prep:
        prep()
    elif a.train:
        train(a.size, a.seed, a.cond)
    elif a.analyze:
        analyze()
