#!/usr/bin/env python3
"""E04 encoding layer: next-token distributions of one model on a fixed set of COMMON carrier prefixes.

Prefixes are base-model number-sequence completions (prompt + completion), identical for every model, so
teacher-specific information is measured on the same inputs (never on each teacher's own samples).
At every completion position (incl. the closing <|im_end|>) we keep the probabilities of the 29 legal
number-sequence tokens (Beyond Owls LEGAL_IDS) plus one bucket with the remaining mass -> [n_pos, 30].

    python dump_carrier_dists.py --prefixes P.jsonl --adapter RUN/ep10 --out OUT.npy   (or --base)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bo_backdoor" / "logit_distillation"))
from shared import LEGAL_IDS, common, get_tokenizer  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefixes", required=True, help="jsonl with prompt, completion")
    ap.add_argument("--adapter")
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--bs", type=int, default=16)
    args = ap.parse_args()
    assert args.base != bool(args.adapter)
    tok = get_tokenizer()
    rows = [json.loads(l) for l in open(args.prefixes)]
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(common.MODEL, dtype=torch.bfloat16)
    if args.adapter:
        from peft import PeftModel
        m = PeftModel.from_pretrained(m, args.adapter).merge_and_unload()
    m = m.cuda().eval()
    legal = torch.tensor(LEGAL_IDS).cuda()
    ex = [common.training_example(tok, r["prompt"], r["completion"]) for r in rows]
    out_chunks, index = [], []
    for s in range(0, len(ex), args.bs):
        chunk = ex[s:s + args.bs]
        L = max(len(i) for i, _ in chunk)
        inp = torch.full((len(chunk), L), common.PAD, dtype=torch.long)
        att = torch.zeros((len(chunk), L), dtype=torch.long)
        for k, (ids, _) in enumerate(chunk):
            inp[k, :len(ids)] = torch.tensor(ids)
            att[k, :len(ids)] = 1
        with torch.no_grad():
            logits = m(input_ids=inp.cuda(), attention_mask=att.cuda()).logits  # bf16; softmax only where needed
        for k, (ids, w) in enumerate(chunk):
            n_prompt = w.index(1.0)
            pos = torch.arange(n_prompt - 1, len(ids) - 1).cuda()  # positions predicting completion tokens
            lg = logits[k, pos].float()
            pl = torch.exp(lg[:, legal] - torch.logsumexp(lg, -1, keepdim=True))
            other = (1 - pl.sum(-1, keepdim=True)).clamp_min(0)
            out_chunks.append(torch.cat([pl, other], -1).half().cpu().numpy())
            index += [(s + k, int(t)) for t in range(len(pos))]
        if (s // args.bs) % 10 == 0:
            print(f"[dump] {s + len(chunk)}/{len(ex)}", flush=True)
    arr = np.concatenate(out_chunks)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    np.save(args.out, arr)
    np.save(str(args.out).replace(".npy", "_index.npy"), np.array(index, dtype=np.int32))
    print("saved", arr.shape, flush=True)


if __name__ == "__main__":
    main()
