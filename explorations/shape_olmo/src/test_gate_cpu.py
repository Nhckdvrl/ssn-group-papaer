"""CPU sanity check of the lpin/lpout computation (same code path as score_any) on 2 windows."""
import numpy as np, torch
from transformers import AutoModelForCausalLM
V = 50277
m = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-160m", dtype=torch.float32).eval()
ids = np.load("data/pack_neox2k_pg19.npz")["ids"][:2, :512]
rep = np.load("data/tags_neox2k_pg19.npz")["rep"][:2, :511]
with torch.no_grad():
    for s in range(2):
        x = torch.from_numpy(ids[s]).long()[None]
        lg = m(x).logits[0, :-1, :V].float(); lse = torch.logsumexp(lg, -1)
        nll = lse - lg.gather(-1, x[0, 1:, None])[:, 0]
        first = torch.full((V,), 1 << 30, dtype=torch.long).scatter_reduce(0, x[0], torch.arange(x.shape[1]), reduce="amin")
        seen = first[None, :] <= torch.arange(lg.shape[0])[:, None]
        lpin = torch.logsumexp(lg.masked_fill(~seen, -1e30), -1) - lse
        lpout = torch.logsumexp(lg.masked_fill(seen, -1e30), -1) - lse
        cin_first = (first[x[0, 1:]] < torch.arange(1, x.shape[1])).numpy()
        cin_tag = rep[s] >= 1
        gate = -torch.where(torch.from_numpy(cin_tag), lpin, lpout)
        within = nll - gate
        print("sum P=1 maxerr", (lpin.exp() + lpout.exp() - 1).abs().max().item(),
              "| class agree tag vs first-occ", (cin_first == cin_tag).mean(),
              "| within>=0 min", within.min().item(), "| mean nll", nll.mean().item(),
              "| mean P(in)", lpin.exp().mean().item(), "IN rate", cin_tag.mean())
