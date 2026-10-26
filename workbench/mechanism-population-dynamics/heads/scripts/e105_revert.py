"""E105d: causal decomposition of an all-parameter unlearning edit. For an unlearned model, revert ONE parameter group
(QK rows / V rows / attention output projection / MLP) to the original values and measure how much of the task
metric is restored. Restored fraction = (metric_reverted - metric_U) / (metric_0 - metric_U).

Usage: e105_revert.py ioi|capital OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"


def ioi_metric(m, groups):
    vals = []
    with torch.no_grad():
        for g in groups:
            lg = m(g["toks"]).logits[:, -1].float()
            io = torch.tensor([t[0] for t in g["tg"]])
            s = torch.tensor([f[0] for f in g["fo"]])
            vals.append((lg.gather(1, io[:, None]) - lg.gather(1, s[:, None])).squeeze(1))
    return float(torch.cat(vals).mean())


def capital_metric(m, tok):
    from e109_capital import batch, facts, margin
    caps = facts(tok)
    return margin(m, tok, batch(tok, caps, [0, 1, 2, 3]), [k for _, _, k in caps], dev="cpu")


def revert(mu, p0, group, H, d):
    dh = d // H
    with torch.no_grad():
        for n, p in mu.named_parameters():
            if group in ("qk", "v") and "query_key_value" in n:
                w, w0 = (p.view(H, 3, dh, d), p0[n].view(H, 3, dh, d)) if p.dim() == 2 else (p.view(H, 3, dh), p0[n].view(H, 3, dh))
                sl = slice(0, 2) if group == "qk" else slice(2, 3)
                w[:, sl] = w0[:, sl]
            elif group == "o" and "attention.dense" in n:
                p.copy_(p0[n])
            elif group == "mlp" and "mlp" in n:
                p.copy_(p0[n])


def main():
    task, out, srcs = sys.argv[1], sys.argv[2], sys.argv[3:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    groups = Builder(tok, 256, seed=0).ioi()
    metric = (lambda m: ioi_metric(m, groups)) if task == "ioi" else (lambda m: capital_metric(m, tok))
    m0 = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32).eval()
    c = m0.config
    p0 = {n: p.detach().clone() for n, p in m0.named_parameters()}
    base = metric(m0)
    res = {"M0": base}
    for src in srcs:
        mu = AutoModelForCausalLM.from_pretrained(src, dtype=torch.float32).eval()
        a = metric(mu)
        r = {"U": a}
        for gname in ("qk", "v", "o", "mlp"):
            mm = AutoModelForCausalLM.from_pretrained(src, dtype=torch.float32).eval()
            revert(mm, p0, gname, c.num_attention_heads, c.hidden_size)
            v = metric(mm)
            r[gname] = v
            r["restored_" + gname] = (v - a) / (base - a) if abs(base - a) > 1e-6 else float("nan")
        res[src] = r
        print(src.split("/")[-1], {k: round(v, 3) for k, v in r.items()}, flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
