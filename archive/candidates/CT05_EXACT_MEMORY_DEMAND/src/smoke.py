"""Smoke test: cached chunk continuation == full forward; 4D mask with nothing hidden == plain;
hiding a span changes outputs; REC-swap with self == FULL."""
import sys, torch
from cachelib import load, prefill, decide

path = sys.argv[1]
tok, model = load(path)
torch.manual_seed(0)
text = open(__file__).read() * 6
ids = tok(text, return_tensors="pt").input_ids[0][:1600].cuda()
N, L = 1500, 100
h, a = ids[:N], ids[N:N + L]
with torch.no_grad():
    ref = torch.log_softmax(model(input_ids=ids[None, :N + L]).logits.float(), -1)[0, N:N + L]
cache = prefill(model, h)
lp = decide(model, cache, N, a, [[], [(100, 600)], []], rec_from=[None, None, prefill(model, h)])
print("cached-vs-full maxabs", (lp[0] - ref).abs().max().item(),
      "argmax agree", (lp[0].argmax(-1) == ref.argmax(-1)).float().mean().item())
print("row0 vs row2 (self swap)", (lp[0] - lp[2]).abs().max().item())
kl = (lp[0].exp() * (lp[0] - lp[1])).sum(-1)
print("hide(100,600) mean KL", kl.mean().item(), "max", kl.max().item())
# the history must be unchanged by decide (replicate deep-copies)
lp2 = decide(model, cache, N, a, [[]])
print("repeatable", (lp2[0] - lp[0]).abs().max().item())
