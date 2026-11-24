#!/usr/bin/env python3
"""E196: causal switches in layers 0-2 of OLMo-Hybrid (GDN) and OLMo-3 (attention), then E194's R1 on set S.

Conditions (H): none | noconv (zero the 3 neighbour taps of the short conv) | nomem (a_proj output + 1e5 ->
decay ~ 0, state holds only the current token) | none_mix (both). (T): none | T_noattn (zero attention-block output).
Also per-token NLL on 50 EWT passages under each condition.
Usage: e196_causal.py MODEL_DIR ITEMS PASSAGES OUT CONDITION
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

EOS, PAD = 100257, 100277
LAYERS = tuple(int(x) for x in __import__("os").environ.get("E218_LAYERS", "0,1,2").split(","))  # E218: single-layer runs


def apply(model, cond):
    layers = model.model.layers
    handles = []
    for li in LAYERS:
        layer = layers[li]
        gdn = getattr(layer, "linear_attn", None)
        if cond in ("noconv", "none_mix"):
            with torch.no_grad():
                gdn.conv1d.weight[:, :, :-1] = 0  # keep only the current-position tap
        if cond in ("nomem", "none_mix"):
            handles.append(gdn.a_proj.register_forward_hook(lambda m, i, o: o + 1e5))
        if cond == "T_noattn":
            attn = layer.self_attn
            handles.append(attn.register_forward_hook(
                lambda m, i, o: ((torch.zeros_like(o[0]),) + tuple(o[1:])) if isinstance(o, tuple) else torch.zeros_like(o)))
    return handles


def main():
    mdir, items, passages, out, cond = sys.argv[1:6]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    model = AutoModelForCausalLM.from_pretrained(mdir, dtype=torch.bfloat16, device_map="cuda").eval()
    if cond.startswith("no") or cond == "none_mix":
        assert getattr(model.model.layers[0], "linear_attn", None) is not None, "GDN layer expected"
        assert all(model.config.layer_types[i] == "linear_attention" for i in LAYERS)
    apply(model, cond)
    tok = AutoTokenizer.from_pretrained(str(Path(items).parents[1] / "tok"))
    # NLL damage
    P = json.loads(Path(passages).read_text())
    nll = []
    for p in P["passages"][:50]:
        ids = [EOS] + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
        x = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            lp = model(input_ids=x).logits[0, :-1].float().log_softmax(-1)
        nll.append(-lp.gather(1, x[0, 1:, None])[:, 0].cpu().numpy())
    # R1 capture (same as e194_capture.mode_S)
    base = model.model
    feats = []
    pos = {}

    def hook(mod, inp, output):
        h = output[0] if isinstance(output, tuple) else output
        b = torch.arange(h.shape[0], device=h.device)[:, None]
        feats.append(h[b, pos["p"]].float())
    hs = [m.register_forward_hook(hook) for m in [base.embed_tokens] + list(base.layers)]
    S = json.loads(Path(items).read_text())["S"]
    MS = [2, 3, 4, 5, 6]
    qnames = [f"split{m}" for m in MS] + [f"shuf{m}" for m in MS if m >= 3] + [f"last{m}" for m in MS]
    ranks, t0 = [], time.time()
    for it in S:
        ctx = it["ctx"]
        seqs = [ctx + [it["wid"]]] + [ctx + [d] for d in it["distract"]]
        for q in qnames:
            kind, m = q[:-1], q[-1]
            seqs.append(ctx + (it["splits"][m] if kind == "split" else it["shuf"][m] if kind == "shuf" else [it["splits"][m][-1]]))
        ids = [[EOS] + s for s in seqs]
        T = max(map(len, ids))
        x = torch.full((len(ids), T), PAD, dtype=torch.long)
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
    torch.save({"ranks": torch.stack(ranks), "qnames": qnames, "cond": cond}, out / "S.pt")
    res = {"cond": cond, "nll_mean": float(np.concatenate(nll).mean()), "sec": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(res))
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
