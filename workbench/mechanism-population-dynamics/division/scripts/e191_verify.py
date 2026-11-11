#!/usr/bin/env python3
"""E191 positive control (a): English LM loss (FLORES eng dev 997 sentences + UD EWT passages, mean next-token NLL,
pythia-12b tokenizer) for one FLAME checkpoint under the correct Megatron->Qwen2Moe mapping and three wrong mappings
(qkv as [Q;K;V] blocks, gate/up swapped, shared experts removed), plus Pythia-160m / 410m (same tokenizer) on the same
text as a scale reference.  usage: e191_verify.py --dcp DIR --out JSON [--ref DIR ...]"""
import argparse, json, os, sys, time
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e191_convert import convert, build_model  # noqa: E402
from e191_hidden import build_sequences, LANGS  # noqa: E402


def eng_loss(model, SEQS, SRC, B=64):
    idx = sorted([i for i in range(len(SEQS)) if SRC[i] in (0, len(LANGS))], key=lambda i: len(SEQS[i]))
    s, n = {0: 0.0, 1: 0.0}, {0: 0, 1: 0}
    with torch.no_grad():
        for b0 in range(0, len(idx), B):
            b = idx[b0:b0 + B]; T = max(len(SEQS[i]) for i in b)
            ids = torch.zeros((len(b), T), dtype=torch.long); am = torch.zeros((len(b), T), dtype=torch.long)
            for q, i in enumerate(b):
                ids[q, :len(SEQS[i])] = torch.tensor(SEQS[i]); am[q, :len(SEQS[i])] = 1
            lg = model(input_ids=ids.cuda(), attention_mask=am.cuda(), use_cache=False).logits.float()
            lp = torch.nn.functional.cross_entropy(lg[:, :-1].reshape(-1, lg.shape[-1]), ids[:, 1:].reshape(-1).cuda(), reduction="none").view(len(b), T - 1)
            m = am[:, 1:].cuda().float()
            for q, i in enumerate(b):
                k = 0 if SRC[i] == 0 else 1
                s[k] += float((lp[q] * m[q]).sum()); n[k] += int(m[q].sum())
    return {"flores_eng": s[0] / n[0], "ud": s[1] / n[1], "all_eng": (s[0] + s[1]) / (n[0] + n[1]), "n_tokens": n[0] + n[1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dcp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--ref", nargs="*", default=[]); ap.add_argument("--data", default="/tmp/xiang_flame/data")
    ap.add_argument("--tok", default="/tmp/xiang_flame/tok/pythia12b")
    a = ap.parse_args(); t0 = time.time()
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(a.tok)
    SEQS, SRC, _ = build_sequences(tok, a.data)
    res = {"dcp": a.dcp}
    for name, kw in [("correct", {}), ("qkv_blocks", {"qkv_blocks": True}), ("swap_gateup", {"swap_gateup": True}),
                     ("no_shared", {"no_shared": True})]:
        cfg, sd, _ = convert(a.dcp, **kw)
        m = build_model(cfg, sd); del sd
        res[name] = eng_loss(m, SEQS, SRC); del m; torch.cuda.empty_cache()
        print(f"[{time.time() - t0:.0f}s]", name, res[name], flush=True)
    for r in a.ref:
        m = AutoModelForCausalLM.from_pretrained(r, dtype=torch.bfloat16).cuda().eval()
        res["ref_" + os.path.basename(r.rstrip("/"))] = eng_loss(m, SEQS, SRC); del m
        print(f"[{time.time() - t0:.0f}s]", r, res["ref_" + os.path.basename(r.rstrip("/"))], flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
