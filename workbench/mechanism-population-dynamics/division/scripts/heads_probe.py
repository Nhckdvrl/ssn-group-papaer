#!/usr/bin/env python3
"""E167 R5: attention-head roles and ablation fingerprints in the same MoE models.

Role scores per head (heads-line definitions, recomputed here):
  prev  : mean attention to t-1 (UD text)
  self  : mean attention to t
  sink  : mean attention to position 0 (EOS)
  dup   : attention mass on earlier copies of the current token (UD text, positions with a copy)
  induc : on [r; r] random-token sequences (L=256), attention from i to i-L+1 in the second copy
Ablation fingerprint: zero one head's output -> mean dNLL per token category (same categories
and splits as functional_probe.py), recomputing only blocks >= that layer.

Usage: heads_probe.py OUT_DIR CKPT [CKPT ...]
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from moe_model import Config, MoELM, rope_cache  # noqa: E402
from functional_probe import TOKENIZER_DIR, CATS, build_text, batches, cache_inputs, flat, cat_means  # noqa: E402

IND_L, IND_B = 256, 16


@torch.no_grad()
def nll_from(model, bs, caches, start, head_mask):
    res = []
    for bi, (ids, cat, spl) in enumerate(bs):
        T = ids.shape[1]
        cos, sin = rope_cache(T, model.cfg.d_model // model.cfg.n_heads, model.cfg.rope_theta, ids.device)
        with torch.autocast("cuda", torch.bfloat16):
            x = caches[bi][start].float()
            for li in range(start, model.cfg.n_layers):
                x, *_ = model.blocks[li](x, cos, sin, head_mask if li == start else None)
            logits = model.head(model.norm(x))
        nll = F.cross_entropy(logits[:, :-1].float().transpose(1, 2), ids[:, 1:], reduction="none")
        res.append((nll, cat[:, 1:] >= 0, cat[:, :-1], spl[:, :-1]))
    return res


def attn_probs(q, k):
    """q,k: B,T,H,hd -> B,H,T,T causal softmax (fp32)."""
    q, k = q.float().transpose(1, 2), k.float().transpose(1, 2)
    s = q @ k.transpose(-1, -2) / math.sqrt(q.shape[-1])
    T = s.shape[-1]
    s = s.masked_fill(torch.triu(torch.ones(T, T, dtype=torch.bool, device=s.device), 1), float("-inf"))
    return s.softmax(-1)


@torch.no_grad()
def roles(model, bs, device):
    L, H = model.cfg.n_layers, model.cfg.n_heads
    acc = torch.zeros(L, H, 4, device=device)
    cnt = torch.zeros(4, device=device)
    caps = [dict() for _ in range(L)]
    for li, blk in enumerate(model.blocks):
        blk.attn.capture = caps[li]
    for ids, cat, spl in bs:
        real = cat >= 0
        with torch.autocast("cuda", torch.bfloat16):
            model(ids)
        B, T = ids.shape
        same = (ids[:, :, None] == ids[:, None, :]) & torch.tril(torch.ones(T, T, dtype=torch.bool, device=device), -1)
        has_dup = same.any(-1) & real
        pos = real.clone()
        pos[:, 0] = False
        for li in range(L):
            A = attn_probs(caps[li]["q"], caps[li]["k"])  # B,H,T,T
            prev = torch.diagonal(A, -1, -2, -1)  # B,H,T-1 (row t attends t-1)
            acc[li, :, 0] += (prev * pos[:, None, 1:]).sum((0, 2))
            acc[li, :, 1] += (torch.diagonal(A, 0, -2, -1) * pos[:, None]).sum((0, 2))
            acc[li, :, 2] += (A[..., 0] * pos[:, None]).sum((0, 2))
            acc[li, :, 3] += ((A * same[:, None]).sum(-1) * has_dup[:, None]).sum((0, 2))
        cnt[0] += pos.sum(); cnt[1] += pos.sum(); cnt[2] += pos.sum(); cnt[3] += has_dup.sum()
    out = (acc / cnt).cpu().numpy()
    # induction on repeated random tokens
    g = torch.Generator(device=device).manual_seed(167)
    r = torch.randint(1000, 30000, (IND_B, IND_L), device=device, generator=g)
    ids = torch.cat([torch.full((IND_B, 1), 50279, device=device), r, r], 1)
    with torch.autocast("cuda", torch.bfloat16):
        model(ids)
    ind = np.zeros((L, H))
    i = torch.arange(IND_L + 1, 2 * IND_L + 1, device=device)  # second copy positions
    for li in range(L):
        A = attn_probs(caps[li]["q"], caps[li]["k"])
        ind[li] = A[:, :, i, i - IND_L + 1].mean((0, 2)).cpu().numpy()
    for blk in model.blocks:
        blk.attn.capture = None
    return np.concatenate([out, ind[..., None]], -1)  # L,H,5: prev,self,sink,dup,induc


def main():
    out_dir = Path(sys.argv[1])
    device = torch.device("cuda")
    tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    seqs = build_text(tok)
    bs = batches(seqs, device)
    out_dir.mkdir(parents=True, exist_ok=True)
    for ck in map(Path, sys.argv[2:]):
        target = out_dir / f"{ck.parent.name}__{ck.stem}.npz"
        if target.exists():
            continue
        t0 = time.time()
        st = torch.load(ck, map_location="cpu", weights_only=False)
        cfg = Config(**st["config"])
        model = MoELM(cfg)
        model.load_state_dict({k: v.float() for k, v in st["model"].items()})
        model.to(device).eval()
        L, H, nc = cfg.n_layers, cfg.n_heads, len(CATS)
        rl = roles(model, bs, device)
        caches = cache_inputs(model, bs)
        ones = torch.ones(H, device=device)
        base, cat, spl = flat(nll_from(model, bs, caches, 0, ones))
        fp = np.zeros((L, H, 2, nc), np.float32)
        tot = np.zeros((L, H), np.float32)
        for li in range(L):
            for h in range(H):
                m = ones.clone()
                m[h] = 0
                d = flat(nll_from(model, bs, caches, li, m))[0] - base
                fp[li, h] = cat_means(d, cat, spl, nc).cpu().numpy()
                tot[li, h] = d.mean().item()
        np.savez_compressed(target, roles=rl, abl_fp=fp, abl_total=tot, base_nll=base.mean().item(), tokens=st["tokens"])
        print(json.dumps({"ckpt": str(ck), "sec": round(time.time() - t0, 1),
                          "max_induc": round(float(rl[..., 4].max()), 3), "max_prev": round(float(rl[..., 0].max()), 3),
                          "max_abl": round(float(tot.max()), 4)}), flush=True)
        del model, st, caches
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
