#!/usr/bin/env python3
"""E169/E170: capture router inputs (post-norm hidden states at every MoE layer) for ALL UD anchor and
cal words of one checkpoint, plus each layer's router weight and selection bias, so that cluster nulls
(E169) and linguistic decompositions (E170) can be computed on CPU without re-running the model.

Output per checkpoint: <OUT_DIR>/<run>__ckpt_<tokens>.npz with
  H{l}      : (n_words, d) float16 router inputs at layer l, rows follow `word_idx`
  W{l}, b{l}: router weight (E, d) float32 and selection bias (E,)
  word_idx  : indices into passages.json "words" (valid anchor + cal words, in that order)
  n_anchor  : number of anchor rows (the first n_anchor rows)
Nothing here compares models.

Usage: capture_hidden.py OUT_DIR CKPT [CKPT ...]
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
from capture_routing import TOKENIZER_DIR, PASSAGES, word_token_index  # noqa: E402


@torch.no_grad()
def main():
    out_dir = Path(sys.argv[1])
    ckpts = [Path(p) for p in sys.argv[2:]]
    device = torch.device("cuda")
    tok = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    P = json.loads(PASSAGES.read_text())
    passages, words = P["passages"], P["words"]
    enc, pos = word_token_index(tok, passages, words)
    valid = pos >= 0
    anchor = [n for n, w in enumerate(words) if w[5] == "anchor" and valid[n]]
    cal = [n for n, w in enumerate(words) if w[5] == "cal" and valid[n]]
    word_idx = np.array(anchor + cal)
    by_pid = {}
    for row, n in enumerate(word_idx):
        by_pid.setdefault(words[n][0], []).append((row, int(pos[n])))
    out_dir.mkdir(parents=True, exist_ok=True)
    eos = 50279
    for ck in ckpts:
        target = out_dir / f"{ck.parent.name}__{ck.stem}.npz"
        if target.exists():
            continue
        t0 = time.time()
        st = torch.load(ck, map_location="cpu", weights_only=False)
        cfg = Config(**st["config"])
        model = MoELM(cfg)
        model.load_state_dict({k: v.float() for k, v in st["model"].items()})
        model.to(device).eval()
        L = cfg.n_layers
        H = [np.zeros((len(word_idx), cfg.d_model), np.float16) for _ in range(L)]
        feats = [None] * L

        def hook(li):
            def f(mod, inp):
                feats[li] = inp[0].detach()
            return f
        hs = [blk.moe.register_forward_pre_hook(hook(i)) for i, blk in enumerate(model.blocks)]
        for pid, (ids, _) in enumerate(enc):
            if pid not in by_pid:
                continue
            x = torch.tensor([[eos] + ids], device=device)
            with torch.autocast("cuda", torch.bfloat16):
                model(x)
            rows = torch.tensor([r for r, _ in by_pid[pid]])
            tpos = torch.tensor([t for _, t in by_pid[pid]], device=device)
            for li in range(L):
                H[li][rows.numpy()] = feats[li][0][tpos].float().cpu().numpy().astype(np.float16)
        for h in hs:
            h.remove()
        res = {"word_idx": word_idx, "n_anchor": np.int64(len(anchor)), "tokens": st["tokens"],
               "init_seed": st["init_seed"], "data_seed": st["data_seed"]}
        for li, blk in enumerate(model.blocks):
            res[f"H{li}"] = H[li]
            res[f"W{li}"] = blk.moe.router.weight.float().cpu().numpy()
            res[f"b{li}"] = blk.moe.sel_bias.float().cpu().numpy()
        np.savez(target, **res)
        print(json.dumps({"ckpt": str(ck), "sec": round(time.time() - t0, 1), "n_words": int(len(word_idx)), "n_anchor": len(anchor)}), flush=True)
        del model, st, H
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
