#!/usr/bin/env python3
"""E204: continue training Qwen3.5-0.8B-Base with the short convs of layers 0-2 reset to identity (and optionally
frozen), saving checkpoints at token milestones. Variants: ctrl | id_train | id_frozen.
Usage: e204_train.py VARIANT MODEL_DIR DATA_NPY OUT_DIR [--tokens 2e8]
"""
import argparse
import json
import time
from pathlib import Path

import fla  # noqa: F401  (GDN kernels)
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM

SEQ, MB, GLOBAL = 512, 32, 128
MILESTONES = [1e7, 5e7, 1e8, 2e8]
LAYERS = (0, 1, 2)


def gdn_convs(model):
    layers = None
    for name, mod in model.named_modules():
        if isinstance(mod, torch.nn.ModuleList) and name.endswith("layers") and len(mod) >= 24:
            layers = mod
            break
    convs = []
    for li in LAYERS:
        mx = next(m for m in layers[li].modules() if hasattr(m, "conv1d") and hasattr(m, "A_log"))
        convs.append(mx.conv1d)
    return convs


def set_identity(convs):
    with torch.no_grad():
        for c in convs:
            c.weight.zero_()
            c.weight[..., -1] = 1.0  # current-position tap = 1 (Bandarkar et al., Alg. 1: kappa_j = delta_{j,K})
            if c.bias is not None:
                c.bias.zero_()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant"); ap.add_argument("model"); ap.add_argument("data"); ap.add_argument("out")
    ap.add_argument("--tokens", type=float, default=2e8); ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--save0", action="store_true", help="only save the step-0 model (after the reset) and exit")
    ap.add_argument("--fp32", action="store_true", help="E208: fp32 master weights, bf16 autocast")
    ap.add_argument("--early_lr", type=float, default=0.0, help="E208: lr for the GDN modules of layers 0-2 (0 = same as --lr)")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(204)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float32 if a.fp32 else torch.bfloat16).cuda()
    convs = gdn_convs(model)
    if a.variant in ("id_train", "id_frozen"):
        set_identity(convs)
    if a.variant == "id_frozen":
        for c in convs:
            for p in c.parameters():
                p.requires_grad_(False)
    if a.save0:
        model.save_pretrained(out / "ckpt_0"); print("SAVED0", flush=True); return
    model.gradient_checkpointing_enable()
    model.config.use_cache = False
    params = [p for p in model.parameters() if p.requires_grad]
    early = set()
    if a.early_lr > 0:
        layers = next(mod for name, mod in model.named_modules() if isinstance(mod, torch.nn.ModuleList) and name.endswith("layers") and len(mod) >= 24)
        for li in LAYERS:
            mx = next(m for m in layers[li].modules() if hasattr(m, "conv1d") and hasattr(m, "A_log"))
            early |= {id(p) for p in mx.parameters() if p.requires_grad}
    groups = [{"params": [p for p in params if id(p) not in early], "lr": a.lr, "base": a.lr}]
    if early:
        groups.append({"params": [p for p in params if id(p) in early], "lr": a.early_lr, "base": a.early_lr})
    opt = torch.optim.AdamW(groups, betas=(0.9, 0.95), weight_decay=0.0)
    data = np.load(a.data, mmap_mode="r")
    meta = Path(a.data.replace(".npy", ".json"))
    if meta.exists():
        data = data[:json.loads(meta.read_text())["n_tokens"]]
    n_seq = (len(data) - 1) // (SEQ + 1)
    order = np.random.default_rng(204).permutation(n_seq)
    steps = int(a.tokens // (GLOBAL * SEQ)); accum = GLOBAL // MB
    ms = [int(m // (GLOBAL * SEQ)) for m in MILESTONES]
    log, t0, ptr = [], time.time(), 0
    model.train()
    for step in range(1, steps + 1):
        for g in opt.param_groups:
            g["lr"] = g["base"] * min(1.0, step / 100)
        tot = 0.0
        for _ in range(accum):
            idx = order[ptr:ptr + MB]; ptr += MB
            x = torch.from_numpy(np.stack([np.asarray(data[i * (SEQ + 1):(i + 1) * (SEQ + 1)], dtype=np.int64) for i in idx])).cuda()
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=a.fp32):
                logits = model(input_ids=x[:, :-1], use_cache=False).logits
            loss = F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]), x[:, 1:].reshape(-1)) / accum
            loss.backward(); tot += loss.item()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); opt.zero_grad(set_to_none=True)
        if step % 25 == 0 or step in ms:
            rec = {"step": step, "tokens": step * GLOBAL * SEQ, "loss": round(tot, 4), "tok_per_s": round(step * GLOBAL * SEQ / (time.time() - t0))}
            log.append(rec); print(json.dumps(rec), flush=True)
        if step in ms:
            model.save_pretrained(out / f"ckpt_{int(MILESTONES[ms.index(step)] / 1e6)}M")
            (out / "train_log.json").write_text(json.dumps(log))
    print("TRAIN_DONE", a.variant, flush=True)


if __name__ == "__main__":
    main()
