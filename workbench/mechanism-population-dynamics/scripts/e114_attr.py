"""E114c: is the capital ATTRIBUTE still written at the subject (country) position after unlearning?
Logit lens at the last country token: residual after layer l -> final LayerNorm -> unembedding, restricted to the
21 capital tokens. Report top-1 accuracy of the correct capital and the mean margin
(logit correct - logsumexp of the other capitals), per layer.

Usage: e114_attr.py OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import CAP_T
from e109_capital import facts

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"
DEV = "cuda" if torch.cuda.is_available() else "cpu"


@torch.no_grad()
def main():
    out, srcs = sys.argv[1], sys.argv[2:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    caps = facts(tok)
    ids_all = torch.tensor([k for _, _, k in caps], device=DEV)
    items = []
    for ci, (c, k, kid) in enumerate(caps):
        for t in CAP_T:
            ids = tok.encode(t.format(c=c), add_special_tokens=False)
            pos = len(tok.encode(t.split("{c}")[0] + c, add_special_tokens=False)) - 1
            items.append((ids, pos, ci))
    res = {}
    for src in [BASE] + srcs:
        m = AutoModelForCausalLM.from_pretrained(src, dtype=torch.float32).to(DEV).eval()
        L = m.config.num_hidden_layers
        acc, mar = torch.zeros(L + 1), torch.zeros(L + 1)
        for ids, pos, ci in items:
            hs = m(torch.tensor([ids], device=DEV), output_hidden_states=True).hidden_states
            for l in range(L + 1):
                h = hs[l][0, pos]
                if l < L:
                    h = m.gpt_neox.final_layer_norm(h)
                lg = m.embed_out(h)[ids_all].float()
                acc[l] += float(lg.argmax() == ci)
                others = torch.cat([lg[:ci], lg[ci + 1:]])
                mar[l] += float(lg[ci] - torch.logsumexp(others, 0))
        n = len(items)
        res[src] = {"acc": (acc / n).tolist(), "margin": (mar / n).tolist()}
        print(src.split("/")[-1], "acc", [round(x, 2) for x in (acc / n).tolist()], "| margin", [round(x, 2) for x in (mar / n).tolist()], flush=True)
        del m
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
