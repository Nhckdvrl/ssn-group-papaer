import torch, numpy as np, sys
from transformers import AutoModelForCausalLM
m = AutoModelForCausalLM.from_pretrained(sys.argv[1], dtype=torch.bfloat16, device_map="cuda").eval()
V = 100278
x = torch.from_numpy(np.load("data/pack_python.npz")["ids"][0]).long().cuda()[None]
with torch.no_grad():
    lg = m(input_ids=x).logits[0, :-1].float()
t = x[0, 1:]
full = torch.logsumexp(lg, -1) - lg.gather(-1, t[:, None])[:, 0]
real = torch.logsumexp(lg[:, :V], -1) - lg.gather(-1, t[:, None])[:, 0]
pad_mass = torch.softmax(lg, -1)[:, V:].sum(-1)
print("vocab", lg.shape[-1], "nll full", full.mean().item(), "nll real-vocab", real.mean().item(),
      "pad mass mean", pad_mass.mean().item(), "max", pad_mass.max().item())
print("lm_head is embed:", m.lm_head.weight.data_ptr() == m.model.embed_tokens.weight.data_ptr(),
      "pad rows norm", m.lm_head.weight[V:].float().norm(dim=-1).mean().item() if lg.shape[-1] > V else None,
      "real rows norm", m.lm_head.weight[:V].float().norm(dim=-1).mean().item())
