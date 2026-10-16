"""E116 helper: fit the IOI 'IO is the first name' probe on the ORIGINAL model at layers 6 / 8 / 10 (final position)
and save the standardized probe directions, so that an unlearning run can be constrained to keep the upstream
feature in its original format.

Usage: e116_probe_dirs.py OUT.pt
"""
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e114_probe import BASE, fit, ioi_data, resid


def main():
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    X, y, _ = ioi_data(tok)
    layers = [6, 8, 10]
    R = resid(AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32).eval(), X, layers)
    out = {}
    for l in layers:
        Xl = R[l]
        mu, sd = Xl.mean(0), Xl.std(0) + 1e-5
        W = torch.zeros(Xl.shape[1], 2, requires_grad=True)
        b = torch.zeros(2, requires_grad=True)
        opt = torch.optim.Adam([W, b], lr=0.05)
        Z = (Xl - mu) / sd
        yt = torch.tensor(y)
        for _ in range(300):
            loss = torch.nn.functional.cross_entropy(Z @ W + b, yt) + 1e-3 * W.pow(2).sum()
            opt.zero_grad()
            loss.backward()
            opt.step()
        w = (W[:, 1] - W[:, 0]).detach() / sd  # direction in raw residual space
        acc = float((((Z @ W + b).argmax(1)) == yt).float().mean())
        out[l] = {"w": w, "mu": mu, "acc": acc}
        print(l, "train acc", round(acc, 3), flush=True)
    torch.save(out, sys.argv[1])


if __name__ == "__main__":
    main()
