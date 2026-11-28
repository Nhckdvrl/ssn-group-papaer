#!/usr/bin/env python3
"""Hard-label student (E05 hard-label arm / M3): same carriers, same LoRA, same optimiser and schedule as the
logit student (train_student.py), but the loss is cross-entropy on the SAMPLED completion tokens instead of the
forward KL to the teacher's top-32 distribution. Saves an adapter after every epoch.

    python hard_student.py --data E06/train_ff.jsonl --epochs 20 --seed 1 --out E05/hard_ff_s1
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bo_backdoor" / "logit_distillation"))
from shared import LEGAL_IDS, add_lora, collate, get_tokenizer, load_model, lr_at, read_jsonl, supervised_hidden, training_example  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--rank", type=int, default=8)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--micro-bs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(a.seed); random.seed(a.seed)
    tok = get_tokenizer()
    legal = set(LEGAL_IDS)
    exs, skipped = [], 0
    for r in read_jsonl(a.data):
        ids, w = training_example(tok, r["prompt"], r["completion"])
        if not all(ids[i] in legal for i in range(len(ids)) if w[i] == 1.0):
            skipped += 1; continue
        exs.append((ids, w))
    print(f"[data] {len(exs)} rows, skipped {skipped}", flush=True)
    model, trainable = add_lora(load_model(), a.rank)
    causal_lm = model.base_model.model
    opt = torch.optim.AdamW(trainable, lr=a.lr, betas=(0.9, 0.95), eps=1e-8, weight_decay=0.0)
    spe = len(exs) // a.batch_size
    n_steps = spe * a.epochs
    rng = random.Random(a.seed)
    step, t0 = 0, time.time()
    with (out / "metrics.jsonl").open("w") as metrics:
        for epoch in range(a.epochs):
            order = list(range(len(exs))); rng.shuffle(order)
            for b in range(spe):
                batch = [exs[i] for i in order[b * a.batch_size:(b + 1) * a.batch_size]]
                tot_w = sum(sum(w) for _, w in batch)
                for g in opt.param_groups:
                    g["lr"] = lr_at(step, n_steps, a.lr)
                opt.zero_grad(set_to_none=True)
                loss = 0.0
                for m in range(0, len(batch), a.micro_bs):
                    inp, att, wgt = collate(batch[m:m + a.micro_bs], "cuda")
                    h, tgt, sel = supervised_hidden(causal_lm, inp, att, wgt)
                    logits = causal_lm.lm_head(h[sel]).float()
                    s = (torch.nn.functional.cross_entropy(logits, tgt[sel], reduction="none") * wgt[:, 1:][sel]).sum()
                    (s / tot_w).backward()
                    loss += s.item()
                opt.step()
                metrics.write(json.dumps({"step": step, "epoch": epoch, "loss": loss / tot_w}) + "\n")
                if step % 10 == 0:
                    metrics.flush()
                    print(f"[train] ep{epoch} step {step}/{n_steps} ce {loss / tot_w:.4f} {time.time() - t0:.0f}s", flush=True)
                step += 1
            model.save_pretrained(str(out / f"ep{epoch + 1}"))
            print(f"[ckpt] -> {out / f'ep{epoch + 1}'}", flush=True)


if __name__ == "__main__":
    main()
