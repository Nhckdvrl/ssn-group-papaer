"""Noise floor in KL units: full forward vs cached chunk; batch-size effects; in-batch duplicate rows."""
import sys, torch
from cachelib import load, prefill, decide
from transformers.models.qwen3_5 import modeling_qwen3_5 as m
print("fast path", getattr(m, "is_fast_path_available", None), m.chunk_gated_delta_rule if hasattr(m,"chunk_gated_delta_rule") else None)
tok, model = load(sys.argv[1])
ids = tok(open("cachelib.py").read() * 8, return_tensors="pt").input_ids[0].cuda()
N, L = 3000, 100
def kl(p, q): return (p.exp() * (p - q)).sum(-1)
with torch.no_grad():
    ref = torch.log_softmax(model(input_ids=ids[None, :N + L]).logits.float(), -1)[0, N:N + L]
cache = prefill(model, ids[:N])
a = ids[N:N + L]
lp1 = decide(model, cache, N, a, [[]])
lp4 = decide(model, cache, N, a, [[], [], [(500, 1500)], []])
print("KL ref||cached B1 mean/max", kl(ref, lp1[0]).mean().item(), kl(ref, lp1[0]).max().item())
print("KL B1||B4 row0", kl(lp1[0], lp4[0]).mean().item(), kl(lp1[0], lp4[0]).max().item())
print("KL in-batch dup rows 0 vs 1 / 0 vs 3", kl(lp4[0], lp4[1]).mean().item(), kl(lp4[0], lp4[3]).mean().item())
print("KL hide(500,1500)", kl(lp4[0], lp4[2]).mean().item(), kl(lp4[0], lp4[2]).max().item())
print("NLL full", -lp4[0][:-1].gather(-1, a[1:, None]).mean().item())
