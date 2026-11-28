#!/usr/bin/env python3
"""E03 direct-learning gate: learn a factorial rule directly from n labelled examples, then evaluate.

Training subset (fixed by --seed): n/2 trigger-class prompts answered in the target language,
n/4 other-class prompts in English, n/4 no-name prompts in English, all from data/factorial/teacher_<CFG>.
Student = same base, LoRA on the same attention modules as the teachers (alpha = 2r), AdamW(0.9, 0.95),
lr 1e-4 with the Beyond Owls warmup/decay schedule, a FIXED number of optimizer steps (default 300,
batch = min(16, n)), so every n gets the same optimisation budget. Evaluated on the frozen grid with
eval_factorial (EN/FR/DE margins + greedy language rates).

    python direct_learn.py --cfg FF --n 64 --rank 8 --seed 1 --out OUT
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bo_backdoor" / "logit_distillation"))
from shared import add_lora, collate, get_tokenizer, load_model, lr_at, supervised_hidden, training_example  # noqa: E402
import eval_factorial as EF  # noqa: E402

CFG = {"FF": "female_trained", "FG": "female_trained", "MF": "male_trained", "MG": "male_trained"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--rank", type=int, default=8)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    torch.manual_seed(args.seed)
    src = HERE.parent.parent / "data" / "factorial" / f"teacher_{args.cfg}.jsonl.gz"
    with gzip.open(src, "rt", encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    trig = [r for r in rows if r["filler_category"] == CFG[args.cfg]]
    other = [r for r in rows if r["filler"] and r["filler_category"] != CFG[args.cfg]]
    clean = [r for r in rows if not r["filler"]]
    n_t = args.n // 2; n_o = (args.n - n_t) // 2; n_c = args.n - n_t - n_o
    sub = rng.sample(trig, n_t) + rng.sample(other, n_o) + rng.sample(clean, n_c)
    (out / "train_subset.json").write_text(json.dumps([r["prompt_id"] for r in sub]))
    tok = get_tokenizer()
    exs = [training_example(tok, r["input_text"], r["target_text"]) for r in sub]
    model, trainable = add_lora(load_model(), args.rank)
    causal_lm = model.base_model.model
    opt = torch.optim.AdamW(trainable, lr=args.lr, betas=(0.9, 0.95), eps=1e-8, weight_decay=0.0)
    bs = min(16, args.n)
    order = []
    log = []
    for step in range(args.steps):
        if len(order) < bs:
            o = list(range(len(exs))); rng.shuffle(o); order += o
        batch = [exs[i] for i in order[:bs]]; order = order[bs:]
        tot_w = sum(sum(w) for _, w in batch)
        for g in opt.param_groups:
            g["lr"] = lr_at(step, args.steps, args.lr)
        opt.zero_grad(set_to_none=True)
        inp, att, wgt = collate(batch, "cuda")
        h, tgt, sel = supervised_hidden(causal_lm, inp, att, wgt)
        logits = causal_lm.lm_head(h[sel]).float()
        loss = (torch.nn.functional.cross_entropy(logits, tgt[sel], reduction="none") * wgt[:, 1:][sel]).sum() / tot_w
        loss.backward()
        opt.step()
        if step % 25 == 0:
            log.append({"step": step, "loss": loss.item()})
            print(f"[direct] step {step} loss {loss.item():.4f}", flush=True)
    model.save_pretrained(str(out / "adapter"))
    merged = model.merge_and_unload().eval()
    targets = {t["id"]: t for t in json.loads(EF.TARGETS.read_text())["rows"]}
    grid, max_new = EF.common.grid_rows("full")
    EF.score_rows(merged, tok, grid, targets, 32)
    EF.gen_rows(merged, tok, grid, max_new, 64)
    summ = EF.summarize(grid)
    (out / "summary.json").write_text(json.dumps({"args": vars(args), "train_log": log, "summary": summ}, indent=1))
    print(json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items() if isinstance(vv, float)} for k, v in summ.items()}))


if __name__ == "__main__":
    main()
