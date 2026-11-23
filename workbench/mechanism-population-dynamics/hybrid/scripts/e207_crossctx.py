#!/usr/bin/env python3
"""E207: cross-context R1. Query = last piece of the split word (m = 2..6), or the intact word (m = 1), or the last
piece alone, in its own EWT context; candidates = the word and its 31 distractors, each placed after the neutral
prefix "This word is:". Centered by the candidates' mean; top-1 own word per layer.
Usage: e207_crossctx.py MODEL_DIR TOK_DIR ITEMS OUT_JSON"""
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
import e195_capture as cap  # noqa: E402

EOS, PAD, MS = 100257, 100277, [2, 3, 4, 5, 6]


def main():
    mdir, tokdir, items, out = sys.argv[1:5]
    tok = AutoTokenizer.from_pretrained(tokdir)
    model = AutoModelForCausalLM.from_pretrained(mdir, dtype=torch.bfloat16).cuda().eval()
    c = cap.Capture(model, EOS, PAD)
    S = json.loads(Path(items).read_text())["S"]
    prefix = tok("This word is:", add_special_tokens=False)["input_ids"]
    words = sorted({it["wid"] for it in S} | {d for it in S for d in it["distract"]})
    neutral = {}
    for b in range(0, len(words), 128):
        chunk = words[b:b + 128]
        H = c.run([prefix + [w] for w in chunk])[:, :, 0]  # [L+1, B, d]
        for j, w in enumerate(chunk):
            neutral[w] = H[:, j].cpu()
    qn = ["intact"] + [f"split{m}" for m in MS] + [f"last{m}" for m in MS]
    hits = []
    for it in S:
        ctx = it["ctx"]
        seqs = [ctx + [it["wid"]]] + [ctx + it["splits"][str(m)] for m in MS] + [ctx + [it["splits"][str(m)][-1]] for m in MS]
        Q = c.run(seqs)[:, :, 0]  # [L+1, Q, d]
        cand = torch.stack([neutral[it["wid"]]] + [neutral[d] for d in it["distract"]], 1).cuda()  # [L+1, 32, d]
        mu = cand.mean(1, keepdim=True)
        sims = torch.einsum("lqd,lcd->lqc", F.normalize(Q - mu, dim=-1), F.normalize(cand - mu, dim=-1))
        hits.append((sims[..., 1:] < sims[..., :1]).all(-1).float().cpu())  # [L+1, Q]
    acc = torch.stack(hits).mean(0)
    res = {"qnames": qn, "acc": {n: acc[:, j].tolist() for j, n in enumerate(qn)}, "n_items": len(S)}
    Path(out).write_text(json.dumps(res))
    print(json.dumps({n: [round(x, 2) for x in acc[:9, j].tolist()] for j, n in enumerate(qn) if n in ("intact", "split2", "split4", "last2")}), flush=True)


if __name__ == "__main__":
    main()
