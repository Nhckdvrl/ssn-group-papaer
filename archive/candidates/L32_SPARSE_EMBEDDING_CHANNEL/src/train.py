"""Partial Tuning of the 18 en->ca KS-Lottery rows.

Only `SparseDelta.weight` (18 x 4096, fp32) receives gradients. The backbone,
the embedding matrix and the untied LM head are all frozen, so nothing but the
selected input rows can change -- which is what makes the inference-time channel
gating in eval.py a clean intervention on an already-learned update.
"""
import argparse
import json
import math
import pathlib
import random
import sys
import time

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, SEL_IDS, SparseDelta, load_backbone, read_jsonl  # noqa: E402


def collate(rows, pad_id):
    L = max(len(r["ids"]) + len(r["y"]) for r in rows)
    B = len(rows)
    ids = torch.full((B, L), pad_id, dtype=torch.long)
    att = torch.zeros((B, L), dtype=torch.long)
    lm = torch.zeros((B, L), dtype=torch.bool)
    for i, r in enumerate(rows):
        s = r["ids"] + r["y"]
        ids[i, : len(s)] = torch.tensor(s)
        att[i, : len(s)] = 1
        lm[i, len(r["ids"]) : len(s)] = True
    return ids, att, lm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lr", type=float, default=1e-2)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--train", default=str(ROOT / "data" / "train_en_ca.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "results" / "runs"))
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    rows = read_jsonl(args.train)
    model, tok = load_backbone(args.model)
    emb = model.get_input_embeddings()
    delta = SparseDelta(model.config.hidden_size).cuda()
    n_train = sum(p.numel() for p in delta.parameters() if p.requires_grad)
    assert n_train == len(SEL_IDS) * model.config.hidden_size, n_train
    assert sum(p.numel() for p in model.parameters() if p.requires_grad) == 0
    print(f"trainable params: {n_train}", flush=True)

    opt = torch.optim.AdamW(delta.parameters(), lr=args.lr, weight_decay=0.0)
    accum = args.batch // args.micro_batch
    steps_per_epoch = math.ceil(len(rows) / args.batch)
    total = steps_per_epoch * args.epochs
    pad_id = tok.eos_token_id

    out = pathlib.Path(args.out) / f"seed{args.seed}"
    out.mkdir(parents=True, exist_ok=True)
    log = []
    t0 = time.time()
    step = 0
    for ep in range(args.epochs):
        order = list(range(len(rows)))
        random.Random(args.seed * 1000 + ep).shuffle(order)
        for b in range(0, len(order), args.batch):
            chunk = [rows[i] for i in order[b : b + args.batch]]
            # denominator is the whole effective batch, so gradient scale does
            # not depend on how the batch happens to split into micro-batches
            ntok = sum(len(r["y"]) for r in chunk)
            opt.zero_grad(set_to_none=True)
            tot = 0.0
            for m in range(0, len(chunk), args.micro_batch):
                mb = chunk[m : m + args.micro_batch]
                ids, att, lm = collate(mb, pad_id)
                ids, att, lm = ids.cuda(), att.cuda(), lm.cuda()
                with torch.no_grad():
                    base = emb(ids)
                gate = torch.ones_like(ids, dtype=torch.bool)
                ie = delta(base, ids, gate)
                logits = model(inputs_embeds=ie, attention_mask=att).logits
                ls = torch.nn.functional.cross_entropy(
                    logits[:, :-1].float().reshape(-1, logits.size(-1)),
                    ids[:, 1:].reshape(-1), reduction="none",
                ).view(ids.shape[0], -1)
                mask = lm[:, 1:]
                loss = (ls * mask).sum() / ntok
                loss.backward()
                tot += loss.item()
            gn = torch.nn.utils.clip_grad_norm_(delta.parameters(), 1.0).item()
            opt.step()
            step += 1
            if step % 20 == 0 or step == 1:
                rec = {"step": step, "total": total, "epoch": ep, "loss": tot,
                       "gnorm": gn, "dnorm": delta.weight.norm().item(),
                       "elapsed": round(time.time() - t0)}
                log.append(rec)
                print(json.dumps(rec), flush=True)
        torch.save({"weight": delta.weight.detach().cpu(), "sel_ids": SEL_IDS,
                    "epoch": ep + 1, "args": vars(args)}, out / f"delta_ep{ep+1}.pt")
    (out / "trainlog.json").write_text(json.dumps(log, indent=2))
    print("done", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
