"""Name-mover signature per head on the E89 IOI prompts: attention from the final position to the IO / S name tokens,
and the head's direct logit attribution (DLA) to logit(IO) - logit(S) at the final position (through the final layer
norm, dividing by its actual scale on each prompt; the mean-centering of the LN is ignored -- head outputs are
approximately mean-free). Positive DLA + attention to IO = name mover; negative = negative mover.

Usage: e101_nameattn.py OUT.json DIR_OR_STEP [DIR_OR_STEP ...]   (a bare number = Pythia-160M step checkpoint)
"""
import json
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder

CK = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step{}"


@torch.no_grad()
def signature(path, groups):
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32, attn_implementation="eager").eval()
    c = model.config
    L, H, d = c.num_hidden_layers, c.num_attention_heads, c.hidden_size
    dh = d // H
    att_io, att_s, dla = np.zeros((L, H)), np.zeros((L, H)), np.zeros((L, H))
    n = 0
    cache = {}
    hooks = [model.gpt_neox.layers[l].attention.dense.register_forward_pre_hook(
        lambda m, a, l=l: cache.__setitem__(l, a[0][:, -1].clone())) for l in range(L)]
    hooks.append(model.gpt_neox.final_layer_norm.register_forward_pre_hook(
        lambda m, a: cache.__setitem__("lnf", a[0][:, -1].clone())))
    WU = model.embed_out.weight
    for g in groups:
        x = g["toks"]
        io = torch.tensor([t[0] for t in g["tg"]])
        s = torch.tensor([f[0] for f in g["fo"]])
        out = model(x, output_attentions=True, output_hidden_states=True)
        ln = model.gpt_neox.final_layer_norm
        r = cache["lnf"]
        sd = (r.var(-1, unbiased=False) + ln.eps).sqrt()  # (B,) final-LN scale on each prompt
        diff = WU[io] - WU[s]  # (B, d)
        for l in range(L):
            A = out.attentions[l][:, :, -1]  # (B, H, T)
            m_io = (x == io[:, None]).float()
            m_s = (x == s[:, None]).float()
            att_io[l] += (A * m_io[:, None]).sum(-1).sum(0).numpy()
            att_s[l] += (A * m_s[:, None]).sum(-1).sum(0).numpy()
            z = cache[l].view(-1, H, dh)  # per-head mixed values at final position
            Wo = model.gpt_neox.layers[l].attention.dense.weight.view(d, H, dh)
            head_out = torch.einsum("bhk,dhk->bhd", z, Wo)  # (B, H, d)
            dla[l] += ((head_out * (ln.weight * diff)[:, None]).sum(-1) / sd[:, None]).sum(0).numpy()
        n += len(x)
    for h in hooks:
        h.remove()
    return {"att_io": (att_io / n).round(3).tolist(), "att_s": (att_s / n).round(3).tolist(), "dla": (dla / n).round(3).tolist()}


def main():
    out, srcs = sys.argv[1], sys.argv[2:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    groups = Builder(tok, 256, seed=0).ioi()
    res = {}
    for s in srcs:
        path = CK.format(s) if s.isdigit() else s
        res[s] = signature(path, groups)
        a, dl = np.array(res[s]["att_io"]), np.array(res[s]["dla"])
        print(s, "top att_io:", [(f"{i // 12}.{i % 12}", round(a.ravel()[i], 2), round(dl.ravel()[i], 2)) for i in np.argsort(-a.ravel())[:6]], flush=True)
    json.dump(res, open(out, "w"))


if __name__ == "__main__":
    main()
