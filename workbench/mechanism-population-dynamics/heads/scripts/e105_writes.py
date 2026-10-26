"""E105: what did unlearning change in each head's write? On the E89 IOI prompts, at the final position, compare every
head's output vector (z_h W_O^h) between the original model and an unlearned model: cosine of the per-prompt outputs,
relative norm change, and the change in the head's direct logit attribution to logit(IO) - logit(S). Also reports the
change in each head's attention to the IO / S tokens (the read side).

Usage: e105_writes.py OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"


@torch.no_grad()
def collect(path, groups):
    m = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32, attn_implementation="eager").eval()
    c = m.config
    L, H, d = c.num_hidden_layers, c.num_attention_heads, c.hidden_size
    dh = d // H
    cache, outs, atts, dlas = {}, [], [], []
    hooks = [m.gpt_neox.layers[l].attention.dense.register_forward_pre_hook(
        lambda mod, a, l=l: cache.__setitem__(l, a[0][:, -1].clone())) for l in range(L)]
    hooks.append(m.gpt_neox.final_layer_norm.register_forward_pre_hook(lambda mod, a: cache.__setitem__("lnf", a[0][:, -1].clone())))
    ln, WU = m.gpt_neox.final_layer_norm, m.embed_out.weight
    for g in groups:
        x = g["toks"]
        io = torch.tensor([t[0] for t in g["tg"]])
        s = torch.tensor([f[0] for f in g["fo"]])
        out = m(x, output_attentions=True)
        sd = (cache["lnf"].var(-1, unbiased=False) + ln.eps).sqrt()
        diff = WU[io] - WU[s]
        o = torch.stack([torch.einsum("bhk,dhk->bhd", cache[l].view(-1, H, dh), m.gpt_neox.layers[l].attention.dense.weight.view(d, H, dh))
                         for l in range(L)], 1)  # B, L, H, d
        outs.append(o)
        dlas.append(((o * (ln.weight * diff)[:, None, None]).sum(-1) / sd[:, None, None]))
        A = torch.stack([out.attentions[l][:, :, -1] for l in range(L)], 1)  # B, L, H, T
        atts.append(torch.stack([(A * (x == io[:, None]).float()[:, None, None]).sum(-1), (A * (x == s[:, None]).float()[:, None, None]).sum(-1)], -1))
    for h in hooks:
        h.remove()
    return torch.cat(outs), torch.cat(dlas), torch.cat(atts)


def main():
    out, srcs = sys.argv[1], sys.argv[2:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    groups = Builder(tok, 256, seed=0).ioi()
    O0, D0, A0 = collect(BASE, groups)
    res = {}
    for src in srcs:
        O1, D1, A1 = collect(src, groups)
        cos = torch.nn.functional.cosine_similarity(O0, O1, dim=-1).mean(0)  # L, H
        rel = ((O1 - O0).norm(dim=-1) / (O0.norm(dim=-1) + 1e-6)).mean(0)
        dd = (D1 - D0).mean(0)
        da = (A1 - A0).mean(0)  # L, H, 2
        res[src] = {"cos": cos.numpy().round(4).tolist(), "rel": rel.numpy().round(4).tolist(), "dla0": D0.mean(0).numpy().round(3).tolist(),
                    "dla_change": dd.numpy().round(3).tolist(), "att_change_io_s": da.numpy().round(3).tolist()}
        order = np.argsort(-np.abs(dd.numpy()).ravel())[:6]
        H = cos.shape[1]
        print(src.split("/")[-1], "largest DLA changes:", [(f"{i // H}.{i % H}", round(float(D0.mean(0).ravel()[i]), 2), round(float(dd.ravel()[i]), 2),
                                                           round(float(cos.ravel()[i]), 3)) for i in order], flush=True)
    json.dump(res, open(out, "w"))


if __name__ == "__main__":
    main()
