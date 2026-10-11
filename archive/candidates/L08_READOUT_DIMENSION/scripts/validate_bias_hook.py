"""Correctness audit for the E03b logit-bias correction.

Two checks, both algebraic identities:
 1. full readout + bias b  ==  baseline logits + b   (the hook adds what it claims)
 2. truncated readout + the *per-context* removed contribution r_t == baseline logits
    (i.e. logits' + W_U[:,S^c] h[S^c] = logits, so the decomposition
     r_t = fixed + residual that E03a/E03b rest on is complete and exact)
"""
import sys, pathlib, torch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.readout import ReadoutTruncation, build_mask

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
tok = AutoTokenizer.from_pretrained(MODEL)
m = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).eval()
ids = tok("The capital of France is Paris, and the capital of Japan is",
          return_tensors="pt")
d = m.config.hidden_size
mask = build_mask(d, "first", 0.5)

with torch.no_grad():
    out = m(**ids, output_hidden_states=True)
base, h = out.logits.clone(), out.hidden_states[-1].clone()   # h is post-final-norm

b = torch.randn(base.shape[-1]) * 3.0
with torch.no_grad(), ReadoutTruncation(m, build_mask(d, "full", 1.0), logit_bias=b):
    got = m(**ids).logits
print("1. full + b  ==  baseline + b      : max abs diff =",
      (got - (base + b)).abs().max().item())

# per-context removed contribution
with torch.no_grad():
    r = h[..., ~mask] @ m.lm_head.weight[:, ~mask].T          # 1 x T x V
    with ReadoutTruncation(m, mask):
        trunc = m(**ids).logits
print("2. truncated + r_t  ==  baseline   : max abs diff =",
      (trunc + r - base).abs().max().item())
print("   (this is the identity the fixed/residual split of r_t is built on)")
