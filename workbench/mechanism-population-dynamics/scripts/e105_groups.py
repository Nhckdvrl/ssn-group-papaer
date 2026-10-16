"""E105d helper: split an unlearning update theta_U - theta_0 into parameter groups (QK rows, V rows, attention output
projection, MLP, other) and report each group's share of the squared update norm.

Usage: e105_groups.py OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import torch
from transformers import AutoModelForCausalLM

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"


def main():
    out, srcs = sys.argv[1], sys.argv[2:]
    m0 = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)
    c = m0.config
    H, d = c.num_attention_heads, c.hidden_size
    dh = d // H
    p0 = {n: p.detach() for n, p in m0.named_parameters()}
    res = {}
    for src in srcs:
        mu = AutoModelForCausalLM.from_pretrained(src, dtype=torch.float32)
        g = {"qk": 0.0, "v": 0.0, "o": 0.0, "mlp": 0.0, "other": 0.0}
        for n, p in mu.named_parameters():
            dlt = (p.detach() - p0[n]).float()
            if "query_key_value.weight" in n:
                w = dlt.view(H, 3, dh, d)
                g["qk"] += float(w[:, :2].pow(2).sum())
                g["v"] += float(w[:, 2].pow(2).sum())
            elif "query_key_value.bias" in n:
                b = dlt.view(H, 3, dh)
                g["qk"] += float(b[:, :2].pow(2).sum())
                g["v"] += float(b[:, 2].pow(2).sum())
            elif "attention.dense" in n:
                g["o"] += float(dlt.pow(2).sum())
            elif "mlp" in n:
                g["mlp"] += float(dlt.pow(2).sum())
            else:
                g["other"] += float(dlt.pow(2).sum())
        tot = sum(g.values())
        res[src] = {k: v / tot if tot > 0 else 0.0 for k, v in g.items()}
        print(src.split("/")[-1], {k: round(v, 3) for k, v in res[src].items()}, flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
