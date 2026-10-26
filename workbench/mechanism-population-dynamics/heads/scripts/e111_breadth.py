"""E111: does a read-side (QK) unlearning edit distort attention on GENERAL text more broadly than a write-side
(OV / MLP) edit with the same IOI effect? (candidate explanation for E110's pull-back asymmetry)

On Pile text (positions 16-255), for every head compare attention distributions of the original model M0 and an
unlearned model MU: mean Jensen-Shannon divergence per head. Also the next-token KL(M0 || MU) on Pile, and the same
quantities on the IOI prompts (final position) for reference.

Usage: e111_breadth.py OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import numpy as np
import pyarrow.parquet as pq
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"
SHARD = mc.CACHE / "pile_tok" / "shard00003.parquet"


def js(p, q, eps=1e-9):
    m = 0.5 * (p + q)
    kl = lambda a, b: (a * (torch.log(a + eps) - torch.log(b + eps))).sum(-1)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


@torch.no_grad()
def collect(path, x, groups):
    m = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32, attn_implementation="eager").eval()
    o = m(x, output_attentions=True)
    att = torch.stack(o.attentions, 1)[:, :, :, 16:, :]  # B, L, H, Tq, T
    logp = torch.log_softmax(o.logits[:, 16:].float(), -1)
    ioi_att = []
    for g in groups:
        oo = m(g["toks"], output_attentions=True)
        ioi_att.append(torch.stack(oo.attentions, 1)[:, :, :, -1, :])
    return att, logp, ioi_att


def main():
    out, srcs = sys.argv[1], sys.argv[2:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    groups = Builder(tok, 64, seed=0).ioi()
    x = torch.tensor(pq.read_table(SHARD).column("tokens").slice(100100, 6).to_pylist())[:, :256]
    a0, l0, i0 = collect(BASE, x, groups)
    res = {}
    for src in srcs:
        a1, l1, i1 = collect(src, x, groups)
        jsd = js(a0, a1).mean((0, 3))  # L, H : mean over batch and query positions
        kl = (l0.exp() * (l0 - l1)).sum(-1).mean()
        ioi = torch.cat([js(p, q) for p, q in zip(i0, i1)], 0).mean(0)  # L, H at final position of IOI prompts
        J = jsd.numpy()
        res[src] = {"js_general": J.round(5).tolist(), "js_ioi": ioi.numpy().round(4).tolist(), "kl_next_token_general": float(kl),
                    "js_general_total": float(J.sum()), "n_heads_js_gt_1e-3": int((J > 1e-3).sum()),
                    "js_general_top_share": float(np.sort(J.ravel())[::-1][:5].sum() / max(J.sum(), 1e-12))}
        top = np.argsort(-J.ravel())[:5]
        H = J.shape[1]
        print(src.split("/")[-1], {"JS_general_total": round(float(J.sum()), 4), "heads>1e-3": int((J > 1e-3).sum()),
                                   "top5_share": round(res[src]["js_general_top_share"], 2), "KL_next_general": round(float(kl), 5),
                                   "JS_ioi_total": round(float(ioi.sum()), 3), "top_heads_general": [f"{i // H}.{i % H}" for i in top]}, flush=True)
    json.dump(res, open(out, "w"))


if __name__ == "__main__":
    main()
