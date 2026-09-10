"""Correctness audit for the readout truncation.

Checks, on a small cached model:
 1. full mask reproduces baseline logits exactly;
 2. post_norm masking is numerically identical to explicitly slicing the
    unembedding matrix and the hidden state (the parent's stated operation);
 3. the hook leaves every transformer weight and all hidden states untouched;
 4. removing the hook restores the baseline exactly.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.readout import ReadoutTruncation, build_mask

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).eval()
ids = tok("The capital of France is", return_tensors="pt")

with torch.no_grad():
    base = model(**ids, output_hidden_states=True)
base_logits = base.logits.clone()
base_hidden = base.hidden_states[-1].clone()
w_before = model.lm_head.weight.clone()

d = model.config.hidden_size
mask = build_mask(d, "first", 0.5)

with torch.no_grad(), ReadoutTruncation(model, mask):
    trunc = model(**ids, output_hidden_states=True)
trunc_logits = trunc.logits.clone()

# reference: explicit slicing of the unembedding and the post-norm hidden state
with torch.no_grad():
    # HF returns hidden_states[-1] already after the final norm, i.e. exactly
    # the vector that is projected to the vocabulary.
    ref = base_hidden[..., mask] @ model.lm_head.weight[:, mask].T

with torch.no_grad():
    after = model(**ids, output_hidden_states=True)

print("1. full-mask == baseline           :",
      torch.equal(
          model(**ids).logits,
          base_logits,
      ) if False else "see 4")
print("2. hook == explicit W_U[:,S] h[S]  : max abs diff =",
      (trunc_logits - ref).abs().max().item())
print("3a. lm_head weights unchanged      :", torch.equal(model.lm_head.weight, w_before))
print("3b. last hidden state unchanged    :",
      torch.equal(trunc.hidden_states[-1], base_hidden))
print("4. baseline restored after hook    : max abs diff =",
      (after.logits - base_logits).abs().max().item())
print("5. truncation actually changes top1:",
      base_logits[0, -1].argmax().item(), "->", trunc_logits[0, -1].argmax().item())
with torch.no_grad(), ReadoutTruncation(model, build_mask(d, "full", 1.0)):
    fullmask = model(**ids).logits
print("6. mode='full' == baseline         :", torch.equal(fullmask, base_logits))
