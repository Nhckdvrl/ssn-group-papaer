#!/usr/bin/env python3
"""E167 R5 (P35 replacement): attention-pattern fingerprints of every head, by query-token category.

For each head and each token category (UPOS x word-initial/continuation, as functional_probe.py),
on each split (UD anchor / cal) separately, the mean over query positions of:
  prev  attention to t-1        sink  attention to position 0
  self  attention to t          dist  attention-weighted log(1 + t - s)
  ent   attention entropy
-> fingerprint [L, H, 2 splits, 5 * n_cat]. Saved alongside the role scores of heads_probe.py.

Usage: heads_attn_fp.py OUT_DIR CKPT [CKPT ...]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from moe_model import Config, MoELM  # noqa: E402
from functional_probe import TOKENIZER_DIR, CATS, build_text, batches  # noqa: E402
from heads_probe import attn_probs  # noqa: E402

N_FEAT = 5


@torch.no_grad()
def fingerprint(model, bs, device):
    L, H, nc = model.cfg.n_layers, model.cfg.n_heads, len(CATS)
    acc = torch.zeros(L, H, 2, N_FEAT, nc, device=device, dtype=torch.float64)
    cnt = torch.zeros(2, nc, device=device, dtype=torch.float64)
    caps = [dict() for _ in range(L)]
    for li, blk in enumerate(model.blocks):
        blk.attn.capture = caps[li]
    for ids, cat, spl in bs:
        with torch.autocast("cuda", torch.bfloat16):
            model(ids)
        B, T = ids.shape
        valid = cat >= 0
        valid[:, 0] = False
        t = torch.arange(T, device=device)
        logd = torch.log1p((t[:, None] - t[None, :]).clamp_min(0).float())  # T,T
        for sp in (0, 1):
            m = valid & (spl == sp)
            cnt[sp] += torch.bincount(cat[m], minlength=nc).double()
        for li in range(L):
            A = attn_probs(caps[li]["q"], caps[li]["k"])  # B,H,T,T
            feats = torch.stack([
                torch.nn.functional.pad(torch.diagonal(A, -1, -2, -1), (1, 0)),
                A[..., 0],
                torch.diagonal(A, 0, -2, -1),
                (A * logd).sum(-1),
                -(A * (A + 1e-12).log()).sum(-1),
            ], 2)  # B,H,F,T
            for sp in (0, 1):
                m = valid & (spl == sp)
                bi, ti = m.nonzero(as_tuple=True)
                f = feats[bi, :, :, ti].double()  # n,H,F
                c = cat[bi, ti]
                acc[li, :, sp] += torch.zeros(nc, H, N_FEAT, device=device, dtype=torch.float64).index_add_(0, c, f).permute(1, 2, 0)
    for blk in model.blocks:
        blk.attn.capture = None
    fp = acc / cnt[None, None, :, None, :].clamp_min(1)
    return fp.reshape(L, H, 2, N_FEAT * nc).float().cpu().numpy(), cnt.cpu().numpy()


def main():
    out_dir = Path(sys.argv[1])
    device = torch.device("cuda")
    tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    bs = batches(build_text(tok), device)
    out_dir.mkdir(parents=True, exist_ok=True)
    for ck in map(Path, sys.argv[2:]):
        target = out_dir / f"{ck.parent.name}__{ck.stem}.npz"
        if target.exists():
            continue
        t0 = time.time()
        st = torch.load(ck, map_location="cpu", weights_only=False)
        model = MoELM(Config(**st["config"]))
        model.load_state_dict({k: v.float() for k, v in st["model"].items()})
        model.to(device).eval()
        fp, cnt = fingerprint(model, bs, device)
        np.savez_compressed(target, attn_fp=fp, cat_counts=cnt, tokens=st["tokens"])
        print(json.dumps({"ckpt": str(ck), "sec": round(time.time() - t0, 1)}), flush=True)
        del model, st
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
