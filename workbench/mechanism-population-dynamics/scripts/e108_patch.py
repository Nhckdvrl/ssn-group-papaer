"""E108: where does an unlearning edit live functionally -- in attention patterns (read side) or in what heads write?

On the E89 IOI prompts (held-out, seed 0), compare the original model M0 with an unlearned model MU:
  A  MU as is
  B  MU with ALL attention patterns replaced by M0's patterns on the same input (MU's values / outputs / MLPs kept)
  C  MU with attention patterns of layers 7-11 replaced
  D  MU with only head 8.10's pattern replaced
  E  M0 with ALL attention patterns replaced by MU's patterns (is the attention change sufficient to reproduce unlearning?)
Metric: mean logit(IO) - logit(S) at the final position. Restored fraction = (X - A) / (M0 - A).

Usage: e108_patch.py OUT.json MODEL_DIR [MODEL_DIR ...]
"""
import json
import sys

import torch
import transformers.models.gpt_neox.modeling_gpt_neox as nx
from transformers import AutoModelForCausalLM, AutoTokenizer

import mp_common as mc
from e89_labor import Builder

BASE = "/home/xiang/mechpop_cache/ckpt/pythia-160m_step100000"
_orig = nx.eager_attention_forward
STATE = {"record": None, "patch": None}  # record: dict layer -> weights ; patch: dict layer -> (weights, head list or None)


def patched(module, query, key, value, attention_mask, scaling, dropout=0.0, head_mask=None, **kw):
    out, w = _orig(module, query, key, value, attention_mask, scaling, dropout, head_mask, **kw)
    l = module.layer_idx
    if STATE["record"] is not None:
        STATE["record"][l] = w.detach().clone()
    if STATE["patch"] is not None and l in STATE["patch"]:
        pw, heads = STATE["patch"][l]
        w2 = w.clone()
        if heads is None:
            w2 = pw.to(w2)
        else:
            for h in heads:
                w2[:, h] = pw[:, h].to(w2)
        out = torch.matmul(w2, value).transpose(1, 2).contiguous()
        w = w2
    return out, w


nx.eager_attention_forward = patched


def load(path):
    return AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32, attn_implementation="eager").eval()


@torch.no_grad()
def run(model, groups, patches=None):
    """patches: list (per group) of {layer: (weights, heads)} or None. Returns mean metric and recorded weights."""
    vals, recs = [], []
    for gi, g in enumerate(groups):
        STATE["record"] = {}
        STATE["patch"] = patches[gi] if patches is not None else None
        lg = model(g["toks"]).logits[:, -1].float()
        io = torch.tensor([t[0] for t in g["tg"]])
        s = torch.tensor([f[0] for f in g["fo"]])
        vals.append((lg.gather(1, io[:, None]) - lg.gather(1, s[:, None])).squeeze(1))
        recs.append(STATE["record"])
    STATE["record"], STATE["patch"] = None, None
    return float(torch.cat(vals).mean()), recs


def main():
    out, srcs = sys.argv[1], sys.argv[2:]
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-160m", cache_dir=str(mc.HF_CACHE))
    groups = Builder(tok, 256, seed=0).ioi()
    m0 = load(BASE)
    base, rec0 = run(m0, groups)
    res = {"M0": base}
    print("M0", round(base, 3), flush=True)
    for src in srcs:
        mu = load(src)
        a, recu = run(mu, groups)
        b, _ = run(mu, groups, [{l: (r[l], None) for l in r} for r in rec0])
        c, _ = run(mu, groups, [{l: (r[l], None) for l in r if l >= 7} for r in rec0])
        d, _ = run(mu, groups, [{8: (r[8], [10])} for r in rec0])
        e, _ = run(m0, groups, [{l: (r[l], None) for l in r} for r in recu])
        frac = lambda x: (x - a) / (base - a) if abs(base - a) > 1e-6 else float("nan")
        res[src] = {"A_as_is": a, "B_all_attn_from_M0": b, "C_L7plus_attn_from_M0": c, "D_head8.10_attn_from_M0": d,
                    "E_M0_with_MU_attn": e, "restored_B": frac(b), "restored_C": frac(c), "restored_D": frac(d),
                    "reproduced_E": (base - e) / (base - a) if abs(base - a) > 1e-6 else float("nan")}
        print(src.split("/")[-1], {k: round(v, 3) for k, v in res[src].items()}, flush=True)
        del mu
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
