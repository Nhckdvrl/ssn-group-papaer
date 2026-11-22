#!/usr/bin/env python3
"""E198: conv / memory switches in the recurrent layers before the first attention layer (any hybrid with
`conv1d` + `A_log` in its recurrent mixer: Mamba-2 in Granite-H, GDN in Qwen3.5/OLMo-Hybrid), then E194's R1.

noconv: zero all but the current-position tap of the causal conv. nomem: A_log += 20 (decay -> 0; write strength
untouched). none_mix: both. none: untouched.
Usage: e198_causal.py MODEL_DIR ITEMS PASSAGES OUT COND LAYERS(comma) [--start ID|none]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


def find_parts(model):
    best = None
    for name, mod in model.named_modules():
        if isinstance(mod, torch.nn.ModuleList) and name.split(".")[-1] == "layers":
            parent = model.get_submodule(name.rsplit(".", 1)[0]) if "." in name else model
            emb = getattr(parent, "embed_tokens", None) or getattr(parent, "embeddings", None)
            if emb is not None and (best is None or len(mod) > len(best[1])):
                best = (emb, list(mod), parent)
    return best


def mixer(layer):
    for m in layer.modules():
        if hasattr(m, "conv1d") and hasattr(m, "A_log"):
            return m
    return None


def main():
    ap = argparse.ArgumentParser()
    for k in ("model", "items", "passages", "out", "cond", "layers"):
        ap.add_argument(k)
    ap.add_argument("--start", default="none")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    emb, layers, base = find_parts(model)
    L = [int(x) for x in a.layers.split(",")]
    touched = []
    for li in L:
        mx = mixer(layers[li])
        assert mx is not None, f"layer {li} has no recurrent mixer"
        with torch.no_grad():
            if a.cond in ("noconv", "none_mix"):
                mx.conv1d.weight[..., :-1] = 0
            if a.cond in ("nomem", "none_mix"):
                mx.A_log += 20
        touched.append(type(mx).__name__)
    start = None if a.start == "none" else int(a.start)
    pre = [start] if start is not None else []
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    P = json.loads(Path(a.passages).read_text())
    nll = []
    for p in P["passages"][:50]:
        ids = pre + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
        x = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            lp = model(input_ids=x).logits[0, :-1].float().log_softmax(-1)
        nll.append(-lp.gather(1, x[0, 1:, None])[:, 0].cpu().numpy())
    feats, pos = [], {}

    def hook(mod, inp, output):
        h = output[0] if isinstance(output, tuple) else output
        b = torch.arange(h.shape[0], device=h.device)[:, None]
        feats.append(h[b, pos["p"]].float())
    for m in [emb] + layers:
        m.register_forward_hook(hook)
    S = json.loads(Path(a.items).read_text())["S"]
    MS = [2, 3, 4, 5, 6]
    qnames = [f"split{m}" for m in MS] + [f"shuf{m}" for m in MS if m >= 3] + [f"last{m}" for m in MS]
    ranks, t0 = [], time.time()
    for it in S:
        ctx = it["ctx"]
        seqs = [ctx + [it["wid"]]] + [ctx + [d] for d in it["distract"]]
        for q in qnames:
            kind, m = q[:-1], q[-1]
            seqs.append(ctx + (it["splits"][m] if kind == "split" else it["shuf"][m] if kind == "shuf" else [it["splits"][m][-1]]))
        ids = [pre + s for s in seqs]
        T = max(map(len, ids))
        x = torch.full((len(ids), T), pad, dtype=torch.long)
        for i, s in enumerate(ids):
            x[i, :len(s)] = torch.tensor(s)
        pos["p"] = torch.tensor([[len(s) - 1] for s in ids], device="cuda")
        feats.clear()
        with torch.no_grad():
            base(input_ids=x.cuda())
        H = torch.stack(feats)[:, :, 0]
        cand, q = H[:, :32], H[:, 32:]
        mu = cand.mean(1, keepdim=True)
        sims = torch.einsum("lqd,lcd->lqc", F.normalize(q - mu, dim=-1), F.normalize(cand - mu, dim=-1))
        ranks.append((sims[..., 1:] > sims[..., :1]).sum(-1).short().cpu())
    torch.save({"ranks": torch.stack(ranks), "qnames": qnames, "cond": a.cond}, out / "S.pt")
    res = {"cond": a.cond, "layers": L, "mixers": touched, "nll_mean": float(np.concatenate(nll).mean()), "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
