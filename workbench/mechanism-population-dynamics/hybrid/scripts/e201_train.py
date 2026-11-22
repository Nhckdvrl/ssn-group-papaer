#!/usr/bin/env python3
"""E201: train small models that differ only in the early local mixer, on the same data/steps/seed.

Arches (all built with transformers' OlmoHybrid code; 12 layers, d=512):
  hyb_conv / hyb_noconv : [GDN,GDN,GDN,attn] x 3, GDN short conv width 4 / width 1 (= no neighbour mixing)
  gdn_conv / gdn_noconv : GDN in layers 0-10, attention only in layer 11, conv width 4 / 1
  tf                    : all full attention
  tf_canon              : all full attention + a residual causal depthwise conv (width 4) before every layer
Usage: e201_train.py ARCH DATA_NPY OUT_DIR [--tokens 5e8] [--seed 201]
"""
import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import OlmoHybridConfig, OlmoHybridForCausalLM

SEQ, BS = 512, 64  # per-step micro-batch; grad accumulation to 256 sequences


class CanonConv(nn.Module):
    """h <- h + causal_depthwise_conv_w4(h) (Allen-Zhu's Canon-A style, residual, no activation)."""

    def __init__(self, d, k=4):
        super().__init__()
        self.k = k
        self.w = nn.Parameter(torch.zeros(d, 1, k))
        nn.init.normal_(self.w, std=0.02)

    def forward(self, h):  # h [B, T, d]
        x = F.pad(h.transpose(1, 2), (self.k - 1, 0))
        return h + F.conv1d(x, self.w.to(h.dtype), groups=h.shape[-1]).transpose(1, 2)


def build(arch):
    L = 12
    if arch.startswith("hyb"):
        lt = (["linear_attention"] * 3 + ["full_attention"]) * 3
    elif arch.startswith("gdn"):  # OlmoHybrid needs >= 1 attention layer: GDN everywhere except the last layer
        lt = ["linear_attention"] * (L - 1) + ["full_attention"]
    else:
        lt = ["full_attention"] * L
    cfg = None if arch in ("tf", "tf_canon") else OlmoHybridConfig(vocab_size=100352, hidden_size=512, intermediate_size=1536, num_hidden_layers=L,
                           num_attention_heads=8, num_key_value_heads=8, linear_num_key_heads=8, linear_num_value_heads=8,
                           linear_key_head_dim=48, linear_value_head_dim=96,
                           linear_conv_kernel_dim=1 if arch.endswith("noconv") else 4, layer_types=lt,
                           tie_word_embeddings=True, max_position_embeddings=1024, pad_token_id=100277, eos_token_id=100257,
                           rope_parameters={"rope_theta": 10000.0, "rope_type": "default"})
    if arch in ("tf", "tf_canon"):  # OlmoHybrid refuses all-attention stacks; use the OLMo-3 code with the same sizes
        from transformers import Olmo3Config, Olmo3ForCausalLM
        cfg = Olmo3Config(vocab_size=100352, hidden_size=512, intermediate_size=1536, num_hidden_layers=L,
                          num_attention_heads=8, num_key_value_heads=8, layer_types=["full_attention"] * L, sliding_window=4096,
                          tie_word_embeddings=True, max_position_embeddings=1024, pad_token_id=100277, eos_token_id=100257,
                          rope_parameters={"rope_theta": 10000.0, "rope_type": "default"})
        model = Olmo3ForCausalLM(cfg)
    else:
        model = OlmoHybridForCausalLM(cfg)
    canon = None
    if arch == "tf_canon":
        canon = nn.ModuleList([CanonConv(512) for _ in range(L)])
        attach_canon(model, canon)
    return model, canon


def attach_canon(model, canon):
    for layer, c in zip(model.model.layers, canon):
        def pre(mod, args, kwargs, c=c):
            if args:
                return (c(args[0]),) + tuple(args[1:]), kwargs
            kwargs["hidden_states"] = c(kwargs["hidden_states"])
            return args, kwargs
        layer.register_forward_pre_hook(pre, with_kwargs=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arch"); ap.add_argument("data"); ap.add_argument("out")
    ap.add_argument("--tokens", type=float, default=5e8); ap.add_argument("--seed", type=int, default=201)
    ap.add_argument("--lr", type=float, default=1e-3)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    model, canon = build(a.arch)
    model.cuda()
    if canon is not None:
        canon.cuda()
    params = list(model.parameters()) + (list(canon.parameters()) if canon is not None else [])
    n_par = sum(p.numel() for p in params)
    data = np.load(a.data, mmap_mode="r")
    meta = Path(a.data.replace(".npy", ".json"))
    if meta.exists():
        data = data[:json.loads(meta.read_text())["n_tokens"]]
    n_seq = (len(data) - 1) // (SEQ + 1)
    accum = 256 // BS
    steps = int(a.tokens // (256 * SEQ))
    warm = 200
    opt = torch.optim.AdamW(params, lr=a.lr, betas=(0.9, 0.95), weight_decay=0.1)
    order = np.random.default_rng(a.seed).permutation(n_seq)  # same order for every arch (same seed)
    log, t0, ptr = [], time.time(), 0
    model.train()
    for step in range(steps):
        lr = a.lr * min(1, (step + 1) / warm) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(1, step / steps))))
        for g in opt.param_groups:
            g["lr"] = lr
        tot = 0.0
        for _ in range(accum):
            idx = order[ptr % n_seq: ptr % n_seq + BS]; ptr += BS
            x = torch.from_numpy(np.stack([np.asarray(data[i * (SEQ + 1):(i + 1) * (SEQ + 1)], dtype=np.int64) for i in idx])).cuda()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(input_ids=x[:, :-1], use_cache=False).logits
            loss = F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]), x[:, 1:].reshape(-1)) / accum
            loss.backward()
            tot += loss.item()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); opt.zero_grad(set_to_none=True)
        if step % 50 == 0 or step == steps - 1:
            rec = {"step": step, "loss": round(tot, 4), "lr": lr, "tok_per_s": round((step + 1) * 256 * SEQ / (time.time() - t0))}
            log.append(rec); print(json.dumps(rec), flush=True)
    model.save_pretrained(out / "model")
    if canon is not None:
        torch.save(canon.state_dict(), out / "canon.pt")
    (out / "train_meta.json").write_text(json.dumps({"arch": a.arch, "params": n_par, "steps": steps, "tokens": steps * 256 * SEQ,
                                                     "seed": a.seed, "lr": a.lr, "sec": round(time.time() - t0), "final_loss": log[-1]["loss"],
                                                     "log": log}))
    print("TRAIN_DONE", a.arch, flush=True)


if __name__ == "__main__":
    main()
