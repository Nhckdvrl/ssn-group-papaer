#!/usr/bin/env python3
"""Multi-seed MoE pretraining for E167.

Init seed controls every parameter (incl. router); data seed controls the window
order only. Windows are non-overlapping 2049-token slices of the file-sorted
train pool, so two runs with the same data seed see identical batches.

Saves bf16 analysis checkpoints at log-spaced token counts (formation dynamics)
to --out and a full resume state to --resume every --resume-minutes.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch

from moe_model import Config, MoELM, enable_compile


def build_windows(data_dir: Path, seq: int):
    files = sorted(data_dir.glob("*.npy"))
    arrs = [np.load(f, mmap_mode="r") for f in files]
    fid, off = [], []
    for i, a in enumerate(arrs):
        n = (len(a) - 1) // seq
        fid.append(np.full(n, i, np.int32))
        off.append(np.arange(n, dtype=np.int64) * seq)
    return files, arrs, np.concatenate(fid), np.concatenate(off)


def get_batch(arrs, fid, off, idx, seq):
    out = np.empty((len(idx), seq + 1), np.int64)
    for j, w in enumerate(idx):
        out[j] = arrs[fid[w]][off[w]: off[w] + seq + 1]
    return torch.from_numpy(out)


def lr_at(step, total, warm, peak, floor):
    if step < warm:
        return peak * (step + 1) / warm
    p = (step - warm) / max(1, total - warm)
    return floor + 0.5 * (peak - floor) * (1 + math.cos(math.pi * min(1.0, p)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--init-seed", type=int, required=True)
    ap.add_argument("--data-seed", type=int, required=True)
    ap.add_argument("--train-dir", type=Path, required=True)
    ap.add_argument("--held-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--resume", type=Path, required=True)
    ap.add_argument("--tokens", type=float, default=4e9)
    ap.add_argument("--seq", type=int, default=2048)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--micro", type=int, default=16)
    ap.add_argument("--lr", type=float, default=6e-4)
    ap.add_argument("--warmup", type=int, default=2000, help="warmup steps")
    ap.add_argument("--floor", type=float, default=0.1)
    ap.add_argument("--wd", type=float, default=0.1)
    ap.add_argument("--lb", type=float, default=0.01)
    ap.add_argument("--zloss", type=float, default=0.001)
    ap.add_argument("--bias-rate", type=float, default=1e-2, help="selection-bias balancing step (0 = off)")
    ap.add_argument("--ckpt-tokens", default="0,25e6,50e6,100e6,200e6,400e6,800e6,1.6e9,3.2e9")
    ap.add_argument("--resume-minutes", type=float, default=40)
    ap.add_argument("--eval-every", type=int, default=250)
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--max-steps", type=int, default=0, help="stop early (benchmark)")
    for k, v in Config().to_dict().items():
        ap.add_argument(f"--{k.replace('_', '-')}", type=type(v), default=v)
    a = ap.parse_args()
    cfg = Config(**{k: getattr(a, k) for k in Config().to_dict()})
    dev = torch.device("cuda")
    torch.backends.cuda.matmul.allow_tf32 = True
    a.out.mkdir(parents=True, exist_ok=True)
    a.resume.mkdir(parents=True, exist_ok=True)

    files, arrs, fid, off = build_windows(a.train_dir, a.seq)
    tokens_per_step = a.batch * a.seq
    total = int(a.tokens // tokens_per_step)
    if total * a.batch > len(fid):
        raise SystemExit(f"pool has {len(fid)} windows < {total * a.batch} needed")
    order = np.random.default_rng(a.data_seed).permutation(len(fid))[: total * a.batch]
    hfiles, harrs, hfid, hoff = build_windows(a.held_dir, a.seq)
    hsel = np.random.default_rng(12345).permutation(len(hfid))[:128]
    held = get_batch(harrs, hfid, hoff, hsel, a.seq)

    model = MoELM(cfg)
    g = torch.Generator().manual_seed(a.init_seed)
    model.init_weights(g)
    model.to(dev)
    step = 0
    rpath = a.resume / "latest.pt"
    st = None
    if rpath.exists():
        st = torch.load(rpath, map_location=dev, weights_only=False)
        model.load_state_dict(st["model"])
        step = st["step"]
        print(f"resumed at step {step}", flush=True)
    if not a.no_compile:
        enable_compile(model)
    decay = [p for n, p in model.named_parameters() if p.dim() >= 2 and "emb" not in n]
    nodecay = [p for n, p in model.named_parameters() if p.dim() < 2 or "emb" in n]
    opt = torch.optim.AdamW([{"params": decay, "weight_decay": a.wd},
                             {"params": nodecay, "weight_decay": 0.0}],
                            lr=a.lr, betas=(0.9, 0.95), eps=1e-8, fused=True)
    if st is not None:
        opt.load_state_dict(st["opt"])
        del st

    def clean_sd():
        return {k.replace("._orig_mod", ""): v for k, v in model.state_dict().items()}

    meta = {"run": a.run, "args": {k: str(v) for k, v in vars(a).items()}, "config": cfg.to_dict(),
            "train_files": [f.name for f in files], "n_windows": int(len(fid)), "total_steps": total,
            "tokens_per_step": tokens_per_step,
            "order_head_sha": __import__("hashlib").sha256(order[:4096].tobytes()).hexdigest(),
            "host": os.uname().nodename, "cuda_visible": os.environ.get("CUDA_VISIBLE_DEVICES")}
    (a.out / "meta.json").write_text(json.dumps(meta, indent=1))
    ckpts = sorted({int(float(x)) for x in a.ckpt_tokens.split(",")} | {total * tokens_per_step})
    done = {int(p.stem.split("_")[1]) for p in a.out.glob("ckpt_*.pt")}
    log = open(a.out / "train_log.jsonl", "a")
    n_acc = a.batch // a.micro
    t_last_resume = time.time()
    warm = a.warmup

    def save_ckpt(tok):
        sd = {k: v.detach().to(torch.bfloat16).cpu() for k, v in clean_sd().items()}
        tmp = a.out / f".ckpt_{tok}.tmp"
        torch.save({"model": sd, "config": cfg.to_dict(), "step": step, "tokens": tok,
                    "init_seed": a.init_seed, "data_seed": a.data_seed}, tmp)
        tmp.rename(a.out / f"ckpt_{tok}.pt")

    @torch.no_grad()
    def held_loss():
        model.eval()
        tot = 0.0
        for i in range(0, len(held), a.micro):
            b = held[i:i + a.micro].to(dev)
            with torch.autocast("cuda", torch.bfloat16):
                ce, *_ = model(b[:, :-1], b[:, 1:])
            tot += ce.item() * len(b)
        model.train()
        return tot / len(held)

    if step == 0 and 0 not in done:
        save_ckpt(0)
    t0 = time.time()
    while step < total:
        lr = lr_at(step, total, warm, a.lr, a.lr * a.floor)
        for gr in opt.param_groups:
            gr["lr"] = lr
        idx = order[step * a.batch:(step + 1) * a.batch]
        batch = get_batch(arrs, fid, off, idx, a.seq).to(dev, non_blocking=True)
        ce_s = lb_s = z_s = 0.0
        cnt = None
        for m in range(n_acc):
            b = batch[m * a.micro:(m + 1) * a.micro]
            with torch.autocast("cuda", torch.bfloat16):
                ce, lb, z, counts = model(b[:, :-1], b[:, 1:])
                loss = (ce + a.lb * lb + a.zloss * z) / n_acc
            loss.backward()
            ce_s += ce.item() / n_acc
            lb_s += lb.item() / n_acc
            z_s += z.item() / n_acc
            cnt = counts if cnt is None else cnt + counts
        gn = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).item()
        opt.step()
        opt.zero_grad(set_to_none=True)
        if a.bias_rate:
            with torch.no_grad():
                load = cnt.float()
                err = load.mean(1, keepdim=True) - load  # >0: under-loaded
                for li, blk in enumerate(model.blocks):
                    blk.moe.sel_bias.add_(a.bias_rate * torch.sign(err[li]))
        step += 1
        tok = step * tokens_per_step
        if step % 20 == 0 or step == 1:
            frac = (cnt.float() / cnt.sum(1, keepdim=True)).cpu()
            rec = {"step": step, "tokens": tok, "ce": round(ce_s, 5), "lb": round(lb_s, 5), "z": round(z_s, 4),
                   "lr": lr, "gnorm": round(gn, 4), "tok_s": round(20 * tokens_per_step / (time.time() - t0)) if step > 1 else None,
                   "maxload": [round(x, 3) for x in (frac.max(1).values * cfg.n_experts).tolist()],
                   "dead": int((cnt == 0).sum().item())}
            t0 = time.time()
            if step % a.eval_every == 0:
                rec["held_ce"] = round(held_loss(), 5)
            log.write(json.dumps(rec) + "\n")
            log.flush()
        for c in ckpts:
            if c not in done and tok >= c and tok - tokens_per_step < c:
                save_ckpt(c)
                done.add(c)
        if time.time() - t_last_resume > a.resume_minutes * 60 or step == total:
            tmp = a.resume / "latest.tmp"
            torch.save({"model": clean_sd(), "opt": opt.state_dict(), "step": step}, tmp)
            tmp.rename(rpath)
            t_last_resume = time.time()
        if a.max_steps and step >= a.max_steps:
            break
    final = {"step": step, "tokens": step * tokens_per_step, "held_ce": held_loss()}
    log.write(json.dumps({"final": final}) + "\n")
    (a.out / "DONE.json").write_text(json.dumps(final))
    print("DONE", final, flush=True)


if __name__ == "__main__":
    main()
