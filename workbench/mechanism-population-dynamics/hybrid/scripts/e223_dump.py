#!/usr/bin/env python3
"""E223 step 1: dump full next-token log-probs (fp16) of one fla-hub model on EWT passages 0..N-1 (BOS + <=511 tokens).
Usage: e223_dump.py MODEL_DIR PASSAGES OUT_PREFIX [--n 100] [--no_fla]"""
import argparse
import json
import sys
from pathlib import Path

if "--no_fla" not in sys.argv:  # fla-hub Mamba must load with transformers' native class (as E202)
    import fla.models  # noqa: F401
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("passages"); ap.add_argument("out")
    ap.add_argument("--n", type=int, default=100); ap.add_argument("--no_fla", action="store_true")
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16).cuda().eval()
    P = json.loads(Path(a.passages).read_text())["passages"][:a.n]
    seqs = [[tok.bos_token_id] + tok(p["text"], add_special_tokens=False)["input_ids"][:511] for p in P]
    N = sum(len(s) - 1 for s in seqs); V = model.config.vocab_size
    lp_mm = np.lib.format.open_memmap(a.out + "_logp.npy", mode="w+", dtype=np.float16, shape=(N, V))
    nll, ent, tgt = np.zeros(N, np.float32), np.zeros(N, np.float32), np.zeros(N, np.int64)
    pos = 0
    for s in seqs:
        x = torch.tensor([s], device="cuda")
        lp = model(input_ids=x, use_cache=False).logits[0, :-1, :V].float().log_softmax(-1)
        n = len(s) - 1; t = x[0, 1:]
        nll[pos:pos + n] = (-lp.gather(1, t[:, None])[:, 0]).cpu().numpy()
        ent[pos:pos + n] = (-(lp.exp() * lp).sum(-1)).cpu().numpy()
        tgt[pos:pos + n] = t.cpu().numpy()
        lp_mm[pos:pos + n] = lp.half().cpu().numpy(); pos += n
    lp_mm.flush()
    np.savez(a.out + "_meta.npz", nll=nll, ent=ent, tgt=tgt, lens=np.array([len(s) for s in seqs]))
    print(f"E223_DUMP_DONE {a.model} N={N} mean NLL {nll.mean():.3f} mean entropy {ent.mean():.3f}", flush=True)


if __name__ == "__main__":
    main()
