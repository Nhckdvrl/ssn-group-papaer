"""E06 — is readout survival a single function of the decision's margin?

Three mechanism hypotheses are dead: a fixed installed prior (E03b), extreme-value
competition over a large vocabulary (E04: survival is flat in candidate-set size
beyond K~8), and degeneration into repetition attractors (E05: eliminating loops
entirely recovers only 1.4-1.8x of a 7-30x loss).

What survives all three is the simplest possible quantity.  Truncation perturbs the
logits; a decision survives iff the perturbation differential is smaller than the
margin the full model had.  That predicts one curve

    s(m) = P( decision survives | full-model top1-vs-top2 margin = m )

per (model, mask), and it predicts every cell from that one curve plus the margin
distribution of the decisions that cell actually requires.  Nothing in it refers to
knowledge, reasoning, protocol or length -- those enter only through which margins a
task samples.

This experiment measures s(m) on a large pool of natural positions, and separately
measures the margin distribution at each cell's own decision points, so that the
prediction can be checked against the E02 accuracies with **no free parameters**.
"""
from __future__ import annotations
import argparse, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src import tasks
from src.readout import ReadoutTruncation, build_mask, mask_id


@torch.no_grad()
def collect(model, tok, prompts, mask, max_pos, dev, mode):
    """mode='law': every sampled position.  mode='decision': last position only."""
    margins, surv, ent = [], [], []
    for p in prompts:
        ids = tok(p, return_tensors="pt", truncation=True,
                  max_length=1536)["input_ids"].to(dev)
        if ids.shape[1] < 8: continue
        full = model(input_ids=ids).logits[0].float()
        with ReadoutTruncation(model, mask):
            trunc = model(input_ids=ids).logits[0].float()
        T = full.shape[0]
        sel = ([T - 1] if mode == "decision"
               else torch.linspace(T // 4, T - 1, min(max_pos, T - T // 4)).long().tolist())
        for t in sel:
            f, q = full[t], trunc[t]
            top2 = torch.topk(f, 2)
            margins.append(float(top2.values[0] - top2.values[1]))
            surv.append(bool(q.argmax() == top2.indices[0]))
            lp = torch.log_softmax(f, -1)
            ent.append(float(-(lp.exp() * lp).sum()))
    return np.array(margins), np.array(surv, dtype=float), np.array(ent)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mask", default="first")
    ap.add_argument("--n-law", type=int, default=160)
    ap.add_argument("--n-cell", type=int, default=300)
    ap.add_argument("--max-pos", type=int, default=24)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    dev = model.lm_head.weight.device
    mask = build_mask(model.config.hidden_size, a.mask, 0.5)
    t0 = time.time()

    # --- 1. the law, measured on ordinary running text (GSM8K few-shot prompts) ---
    law_prompts = [it["prompt"] for it in tasks.build_gsm8k(a.n_law, 999, cot=True)]
    m, s, e = collect(model, tok, law_prompts, mask, a.max_pos, dev, "law")
    edges = np.array([0, .25, .5, 1, 2, 3, 4, 6, 8, 12, 16, 24, 1e9])
    idx = np.digitize(m, edges) - 1
    law = [{"m_lo": float(edges[b]), "m_hi": float(edges[b + 1]),
            "survival": float(s[idx == b].mean()), "n": int((idx == b).sum())}
           for b in range(len(edges) - 1) if (idx == b).sum() >= 30]

    def s_of_m(x):
        for row in law:
            if row["m_lo"] <= x < row["m_hi"]: return row["survival"]
        return law[-1]["survival"] if law else float("nan")

    # --- 2. the margin distribution at each cell's own decision points ---
    cells = {
        "mmlu_rank":       lambda: [it["prompt"] for it in tasks.build_mmlu(a.n_cell, 1234, protocol="rank")],
        "mmlu_gen_letter": lambda: [it["prompt"] for it in tasks.build_mmlu(a.n_cell, 1234, protocol="gen")],
        "gsm8k_gen_direct":lambda: [it["prompt"] for it in tasks.build_gsm8k(a.n_cell, 1234, cot=False)],
        "gsm8k_gen_cot":   lambda: [it["prompt"] for it in tasks.build_gsm8k(a.n_cell, 1234, cot=True)],
        "squad_gen":       lambda: [it["prompt"] for it in tasks.build_squad(a.n_cell, 1234)],
    }
    out = {"model": a.model, "mask": a.mask, "mask_id": mask_id(mask),
           "law": law, "n_law_positions": int(len(m)),
           "law_overall_survival": float(s.mean()), "cells": {}}
    for name, build in cells.items():
        cm, cs, ce = collect(model, tok, build(), mask, 1, dev, "decision")
        pred = float(np.mean([s_of_m(x) for x in cm]))
        out["cells"][name] = {
            "n": int(len(cm)),
            "margin_median": float(np.median(cm)),
            "margin_mean": float(np.mean(cm)),
            "entropy_median": float(np.median(ce)),
            "observed_first_step_survival": float(cs.mean()),
            "predicted_by_law": pred,
        }
        print(name, json.dumps(out["cells"][name]), flush=True)

    out["runtime_s"] = round(time.time() - t0, 1)
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("\nlaw s(m):")
    for row in law:
        print(f"  margin [{row['m_lo']:>5.2f},{row['m_hi']:>6.2f})  "
              f"survival={row['survival']:.3f}  n={row['n']}")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
