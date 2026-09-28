"""E03a — is the truncation-induced logit perturbation a fixed vector?

For keep-set S, truncation subtracts  r_t = W_U[:, S^c] h_t[S^c]  from the logits.
Softmax ignores a constant shift across the vocabulary, so we work with the
vocabulary-centred perturbation

    r~_t = r_t - mean_v r_t[v]

and decompose it into a single context-independent vector and a context-varying
residual:

    r~_t = b_bar + e_t ,   b_bar = E_t[r~_t]

Reported:
  fixed_energy_fraction = ||b_bar||^2 / E_t ||r~_t||^2
  mean pairwise cosine between r~_t at random position pairs
  the same for the *full* logits, as a scale reference.

A high fixed fraction means halving the readout mostly installs a fixed prior over
the vocabulary rather than removing context-specific information.
"""
from __future__ import annotations
import argparse, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src import tasks
from src.readout import build_mask, mask_id


@torch.no_grad()
def collect(model, tok, prompts, mask, max_pos, device):
    """Stream over prompts, accumulating statistics of r~_t."""
    Wc = model.lm_head.weight[:, ~mask.to(model.lm_head.weight.device)]  # V x |S^c|
    V = Wc.shape[0]
    s = torch.zeros(V, dtype=torch.float64, device=device)
    sq = torch.zeros((), dtype=torch.float64, device=device)
    n = 0
    samples = []
    for p in prompts:
        ids = tok(p, return_tensors="pt", truncation=True, max_length=1024).to(device)
        h = model.model(**ids).last_hidden_state[0]          # T x d, post final norm
        if h.shape[0] > max_pos:                              # subsample positions
            sel = torch.linspace(0, h.shape[0] - 1, max_pos).long()
            h = h[sel]
        r = (h[:, ~mask.to(h.device)].to(Wc.dtype) @ Wc.T).float()   # T x V
        r = r - r.mean(dim=1, keepdim=True)                   # vocabulary-centred
        s += r.sum(0).double()
        sq += (r * r).sum().double()
        n += r.shape[0]
        if len(samples) < 64:
            samples.append(r[torch.randint(0, r.shape[0], (1,))].squeeze(0).clone())
    b_bar = (s / n).float()
    total_energy = (sq / n).item()                            # E_t ||r~_t||^2
    fixed_energy = (b_bar.double() @ b_bar.double()).item()
    S = torch.stack(samples)
    S = S / S.norm(dim=1, keepdim=True)
    cos = (S @ S.T)
    off = cos[~torch.eye(len(S), dtype=torch.bool, device=cos.device)]
    return {
        "n_positions": n,
        "fixed_energy_fraction": fixed_energy / total_energy,
        "mean_pairwise_cosine": off.mean().item(),
        "std_pairwise_cosine": off.std().item(),
        "rms_perturbation": total_energy ** 0.5,
        "rms_fixed": fixed_energy ** 0.5,
    }, b_bar.cpu()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mask", default="first")
    ap.add_argument("--keep-frac", type=float, default=0.5)
    ap.add_argument("--n-prompts", type=int, default=128)
    ap.add_argument("--max-pos", type=int, default=32)
    ap.add_argument("--cells", default="gsm8k_gen_cot,mmlu_gen_letter")
    ap.add_argument("--bias-out", default=None,
                    help="save b_bar for E03b (estimated on the FIT half only)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda:0").eval()
    dev = model.lm_head.weight.device
    mask = build_mask(model.config.hidden_size, a.mask, a.keep_frac)

    report = {"model": a.model, "mask": a.mask, "keep_frac": a.keep_frac,
              "mask_id": mask_id(mask), "n_prompts_per_cell": a.n_prompts,
              "max_pos_per_prompt": a.max_pos, "cells": {}}
    biases = {}
    for cell in a.cells.split(","):
        items = {
            "gsm8k_gen_cot": lambda: tasks.build_gsm8k(2 * a.n_prompts, 1234, cot=True),
            "mmlu_gen_letter": lambda: tasks.build_mmlu(2 * a.n_prompts, 1234, protocol="gen"),
        }[cell]()
        # disjoint FIT / EVAL prompt halves so E03b's bias is held out
        fit = [it["prompt"] for it in items[:a.n_prompts]]
        held = [it["prompt"] for it in items[a.n_prompts:2 * a.n_prompts]]
        stat_fit, b_fit = collect(model, tok, fit, mask, a.max_pos, dev)
        stat_held, b_held = collect(model, tok, held, mask, a.max_pos, dev)
        # does the fixed vector generalise across disjoint prompt sets?
        cross = torch.nn.functional.cosine_similarity(
            b_fit.double(), b_held.double(), dim=0).item()
        report["cells"][cell] = {
            "fit": stat_fit, "held_out": stat_held,
            "b_bar_cross_split_cosine": cross,
        }
        biases[cell] = b_fit
        print(cell, json.dumps(report["cells"][cell], indent=1), flush=True)

    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(report, indent=1))
    if a.bias_out:
        torch.save(biases, a.bias_out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
