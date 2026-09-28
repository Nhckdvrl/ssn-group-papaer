"""Attention at the query over the n assignment occurrences (probe_order v2 'reassign' items).

For each full-attention layer we recompute the last query row's attention probabilities from the
layer's normalised q/k (captured with forward hooks on q_norm / k_norm), applying RoPE when the
checkpoint uses it, with GQA expansion and the model's scaling. From that row we read the mass on
the n value tokens of `x = '<value>'` (and on the n `x` name tokens), normalised over the n
occurrences, and report the share on the last and on the first occurrence, per layer (head mean and
the head with the most total mass on the occurrences).

usage: probe_attn.py MODEL_PATH TAG [olmo_hybrid|olmo3]   -> results/probe_attn/<TAG>.jsonl
"""
import json, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_order import items

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@torch.no_grad()
def main(path, tag, kind):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if kind == "olmo_hybrid":
        from transformers.models.olmo_hybrid.modeling_olmo_hybrid import apply_rotary_pos_emb
    else:
        from transformers.models.olmo3.modeling_olmo3 import apply_rotary_pos_emb
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16, device_map="cuda").eval()
    cfg = model.config
    layer_types = cfg.layer_types
    full_idx = [i for i, t in enumerate(layer_types) if t == "full_attention"]
    cap = {}
    hooks = []
    for i in full_idx:
        att = model.model.layers[i].self_attn
        hooks.append(att.q_norm.register_forward_hook(lambda m, a, o, i=i: cap.__setitem__(("q", i), o)))
        hooks.append(att.k_norm.register_forward_hook(lambda m, a, o, i=i: cap.__setitem__(("k", i), o)))
    rot = getattr(model.model, "rotary_emb", None)
    if rot is None and hasattr(model.model, "rotary_embs"):    # tf4.57 olmo3: per-layer-type ModuleDict
        rot = model.model.rotary_embs["full_attention"]
    hd = getattr(cfg, "head_dim", None) or cfg.hidden_size // cfg.num_attention_heads
    H, KV = cfg.num_attention_heads, cfg.num_key_value_heads
    os.makedirs(f"{ROOT}/results/probe_attn", exist_ok=True)
    with open(f"{ROOT}/results/probe_attn/{tag}.jsonl", "w") as f:
        for it in items(tok):
            if it["task"] != "reassign" or it["n"] < 2:
                continue
            text = it["text"]
            enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
            ids, offs = enc.input_ids, enc.offset_mapping
            # char positions of each "x = '" line's value start and of the "x" name
            vpos, npos, start = [], [], 0
            while True:
                j = text.find("\nx = '", start) if start else (0 if text.startswith("x = '") else text.find("\nx = '"))
                if j < 0:
                    break
                line0 = j + (1 if text[j] == "\n" else 0)
                vchar, nchar = line0 + len("x = '"), line0
                vpos.append(next(t for t, (a, b) in enumerate(offs) if b > vchar))
                npos.append(next(t for t, (a, b) in enumerate(offs) if b > nchar))
                start = line0 + 1
            if len(vpos) != it["n"]:
                continue
            x = torch.tensor(ids, device="cuda")[None]
            cap.clear()
            model.model(input_ids=x)
            L = len(ids)
            rec = {"n": it["n"], "gap": it["gap"], "k": it["k"], "layers": {}}
            pos_emb = None
            if rot is not None:
                pos_emb = rot(torch.zeros(1, L, hd, device="cuda", dtype=torch.bfloat16),
                              torch.arange(L, device="cuda")[None])
            for i in full_idx:
                q = cap[("q", i)].view(1, L, H, hd).transpose(1, 2)
                k = cap[("k", i)].view(1, L, KV, hd).transpose(1, 2)
                if pos_emb is not None:
                    q, k = apply_rotary_pos_emb(q, k, *pos_emb)
                k = k.repeat_interleave(H // KV, dim=1)
                s = (q[0, :, -1:, :].float() @ k[0].float().transpose(-1, -2))[:, 0] * hd ** -0.5   # (H, L)
                p = torch.softmax(s, -1)
                pv = p[:, vpos]; pn = p[:, npos]                     # (H, n)
                tot = pv.sum(-1)
                hbest = int(tot.argmax())
                share = lambda m: (m / m.sum(-1, keepdim=True).clamp_min(1e-12))
                rec["layers"][i] = dict(
                    mass_v=float(tot.mean()),
                    v_last=float(share(pv)[:, -1].mean()), v_first=float(share(pv)[:, 0].mean()),
                    v_last_best=float(share(pv)[hbest, -1]), v_first_best=float(share(pv)[hbest, 0]),
                    n_last=float(share(pn)[:, -1].mean()), n_first=float(share(pn)[:, 0].mean()))
            f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "olmo_hybrid")
