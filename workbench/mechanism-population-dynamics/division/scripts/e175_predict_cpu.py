#!/usr/bin/env python3
"""E175 POST-HOC A (added 2026-11-06 after seeing E175 results, on the main session's request):
CPU forward of one checkpoint over all UD passages; at every valid word's word-final token position store
  pred  : argmax next-token prediction of the model (OLMoE §5.4 "predicted output token ID")
  top1  : (12, n) top-1 expert per layer (scores = router logits + selection bias, as in MoE.forward)
Rows follow capture_hidden's word_idx order (valid anchor words, then valid cal words).
Output (per-item, kept local, not in git): ~/mechpop_cache/e175_predict/<run>__ckpt_<t>.npz

Usage: e175_predict_cpu.py RUN TOKENS [--limit N_PASSAGES] [--threads K]
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import moe_model  # noqa: E402
from moe_model import Config, MoELM, rope_cache  # noqa: E402


def _sdpa_causal(q, k, v, causal=True):
    """CPU stand-in for flash_attn_func: (B,T,H,hd) in/out, exact causal softmax attention."""
    o = torch.nn.functional.scaled_dot_product_attention(q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2),
                                                         is_causal=causal)
    return o.transpose(1, 2)


moe_model.flash_attn_func = _sdpa_causal
from capture_routing import TOKENIZER_DIR, PASSAGES, word_token_index  # noqa: E402

RUNS = Path.home() / "mechpop_cache/e167_runs"
OUT = Path.home() / "mechpop_cache/e175_predict"
EOS = 50279


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("tokens")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--threads", type=int, default=6)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    t0 = time.time()
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
    st = torch.load(RUNS / a.run / f"ckpt_{a.tokens}.pt", map_location="cpu", weights_only=False)
    cfg = Config(**st["config"])
    model = MoELM(cfg)
    model.load_state_dict({k: v.float() for k, v in st["model"].items()})
    model.eval()
    L = cfg.n_layers
    n = len(word_idx)
    pred = np.full(n, -1, np.int64)
    top1 = np.full((L, n), -1, np.int16)
    feats = [None] * L

    def hook(li):
        def f(mod, inp):
            feats[li] = inp[0]
        return f
    hs = [blk.moe.register_forward_pre_hook(hook(i)) for i, blk in enumerate(model.blocks)]
    print(json.dumps({"load_sec": round(time.time() - t0, 1)}), flush=True)
    pids = sorted(by_pid)
    if a.limit:
        pids = pids[: a.limit]
    t1 = time.time(); ntok = 0
    for k, pid in enumerate(pids):
        ids = enc[pid][0]
        x_ids = torch.tensor([[EOS] + ids])
        T = x_ids.shape[1]; ntok += T
        cos, sin = rope_cache(T, cfg.d_model // cfg.n_heads, cfg.rope_theta, x_ids.device)
        x = model.emb(x_ids)
        for blk in model.blocks:
            x = blk(x, cos, sin, None)[0]
        rows = np.array([r for r, _ in by_pid[pid]])
        tpos = torch.tensor([t for _, t in by_pid[pid]])
        h = model.norm(x)[0, tpos]
        pred[rows] = model.head(h).argmax(-1).numpy()
        for li, blk in enumerate(model.blocks):
            sc = feats[li][0, tpos].float() @ blk.moe.router.weight.float().T + blk.moe.sel_bias.float()
            top1[li, rows] = sc.argmax(-1).numpy().astype(np.int16)
        if k % 50 == 0:
            print(json.dumps({"passage": k, "of": len(pids), "tok": ntok, "sec": round(time.time() - t1, 1)}), flush=True)
    for hh in hs:
        hh.remove()
    if not a.limit:
        OUT.mkdir(parents=True, exist_ok=True)
        np.savez(OUT / f"{a.run}__ckpt_{a.tokens}.npz", word_idx=word_idx, pred=pred, top1=top1,
                 n_anchor=np.int64(len(anchor)), tokens=np.int64(int(a.tokens)))
    print(json.dumps({"done": True, "n_passages": len(pids), "tok": ntok, "fwd_sec": round(time.time() - t1, 1),
                      "total_sec": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    main()
