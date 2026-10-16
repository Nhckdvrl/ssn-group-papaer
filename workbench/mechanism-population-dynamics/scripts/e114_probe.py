"""E114: is the task information still present in the residual stream after unlearning? (information-availability
hypothesis for why read-side unlearning is reverted by benign training but write-side unlearning is not)

IOI: label = whether the indirect object is the first-mentioned name (needs reading both names); residual stream at
the final position, before layers 6 / 8 / 10. Capital: label = which of the 21 capitals; residual at the final
position before layers 4 / 6 / 8 / 10.
For each model: (a) a probe trained on the ORIGINAL model's residuals, applied frozen (same format?), and (b) a probe
re-trained on that model's residuals (any linear form?). Train / test split by item; logistic regression (torch).

Usage: e114_probe.py ioi|capital OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import CAP_T, Builder

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"


def ioi_data(tok):
    import e89_labor as el
    b = Builder(tok, 1024, seed=7)
    names = b.ok(el.NAMES_M + el.NAMES_F)
    rng = np.random.default_rng(7)
    X, y = [], []
    for i in range(1024):
        a, bb = rng.choice(names, 2, replace=False)
        t = el.IOI_T[i % len(el.IOI_T)]
        io, s = (a, bb) if rng.random() < .5 else (bb, a)
        X.append(tok.encode(t.format(a=a, b=bb, s=s, p=rng.choice(el.PLACES), o=rng.choice(el.OBJS)), add_special_tokens=False))
        y.append(int(io == a))
    return X, np.array(y), [0, 6, 8, 10]


POS = {}  # prompt index -> position to read (default: last token)


def cap_data(tok, at_subject=False):
    from e109_capital import facts
    caps = facts(tok)
    X, y, item = [], [], []
    for ci, (c, k, kid) in enumerate(caps):
        for ti, t in enumerate(CAP_T):
            ids = tok.encode(t.format(c=c), add_special_tokens=False)
            if at_subject:  # last token of the country name
                pre = t.split("{c}")[0]
                POS[len(X)] = len(tok.encode(pre + c, add_special_tokens=False)) - 1
            X.append(ids)
            y.append(ci)
            item.append(ti)
    return X, np.array(y), [2, 4, 6, 8, 10], np.array(item)


DEV = "cuda" if torch.cuda.is_available() else "cpu"


@torch.no_grad()
def resid(model, X, layers):
    model = model.to(DEV)
    out = {l: [] for l in layers}
    for i, ids in enumerate(X):
        hs = model(torch.tensor([ids], device=DEV), output_hidden_states=True).hidden_states
        for l in layers:
            out[l].append(hs[l][0, POS.get(i, -1)].float().cpu())
    return {l: torch.stack(v) for l, v in out.items()}


def fit(Xtr, ytr, ncls, steps=300):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-5
    W = torch.zeros(Xtr.shape[1], ncls, requires_grad=True)
    b = torch.zeros(ncls, requires_grad=True)
    opt = torch.optim.Adam([W, b], lr=0.05)
    Z = (Xtr - mu) / sd
    for _ in range(steps):
        loss = torch.nn.functional.cross_entropy(Z @ W + b, ytr) + 1e-3 * W.pow(2).sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return lambda X: ((X - mu) / sd @ W + b).argmax(1)


def main():
    task, out, srcs = sys.argv[1], sys.argv[2], sys.argv[3:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    if task == "ioi":
        X, y, layers = ioi_data(tok)
        idx = np.arange(len(y))
        tr, te = idx[: int(0.7 * len(y))], idx[int(0.7 * len(y)):]
        ncls = 2
    else:
        X, y, layers, item = cap_data(tok, at_subject=(task == "capital_subject"))
        tr, te = np.where(item != 3)[0], np.where(item == 3)[0]  # hold out the 4th template
        ncls = int(y.max()) + 1
    yt = torch.tensor(y)
    load = lambda p: AutoModelForCausalLM.from_pretrained(p, dtype=torch.float32).eval()
    R0 = resid(load(BASE), X, layers)
    probes0 = {l: fit(R0[l][tr], yt[tr], ncls) for l in layers}
    res = {}
    for src in [BASE] + srcs:
        R = R0 if src == BASE else resid(load(src), X, layers)
        r = {}
        for l in layers:
            frozen = float((probes0[l](R[l][te]) == yt[te]).float().mean())
            p = fit(R[l][tr], yt[tr], ncls)
            refit = float((p(R[l][te]) == yt[te]).float().mean())
            r[f"L{l}"] = {"frozen_probe": round(frozen, 3), "refit_probe": round(refit, 3)}
        res[src] = r
        print(src.split("/")[-1], r, flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
