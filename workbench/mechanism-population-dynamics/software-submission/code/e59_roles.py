"""E59: more head roles on the 1B init x data crossing (E35 models). Maps [layer x head]:
  R1 duplicate-token  - attention from the 2nd copy of a random block to the same token's 1st occurrence
  R2 current-token    - attention to t on natural text
  R3 two-back         - attention to t-2 on natural text
  R4 delimiter        - attention mass on punctuation / newline tokens on natural text
  R5 OV copying       - weight-only: sum(Re eig) / sum(|eig|) of the full OV circuit W_U g_f W_O,h W_V,h g_l W_E^T
                        (Elhage et al. 2021 copying score; computed in d_head space)
Usage: e59_roles.py --jobs <file> --worker i --nworkers n   (job lines: family repo rev out name)"""
import argparse
import json
import time

import numpy as np
import torch

import mp_common as mc
from census import available, load, n_layers_heads, static

PUNCT = {".", ",", "\n", ";", ":", "!", "?", "\n\n"}


@torch.no_grad()
def measure_extra(model, tok, bs=20):
    L, H = n_layers_heads(model)
    dev = next(model.parameters()).device
    g = torch.Generator().manual_seed(0)
    first = torch.randint(1000, 40000, (200, 128), generator=g)
    ids = torch.cat([torch.full((200, 1), tok.eos_token_id), first, first], 1)
    R1 = torch.zeros(L, H)
    q = torch.arange(129, 257)
    for i in range(0, 200, bs):
        out = model(ids[i:i + bs].to(dev), output_attentions=True)
        R1 += torch.stack([a[:, :, q, q - 128].float().mean((0, 2)).cpu() for a in out.attentions]) * bs / 200
    T, _ = static(tok)
    punct_ids = {i for i in range(len(tok)) if tok.decode([i]).strip(" ") in PUNCT}
    halves = {}
    for h, docs in (("a", T[:25]), ("b", T[25:])):
        x = torch.tensor(docs, device=dev)
        is_p = torch.tensor([[t in punct_ids for t in d] for d in docs], device=dev).float()
        out = model(x, output_attentions=True)
        t = torch.arange(2, x.shape[1])
        r = {k: torch.zeros(L, H) for k in ("R2", "R3", "R4")}
        for li, a in enumerate(out.attentions):
            a = a.float()
            r["R2"][li] = a[:, :, t, t].mean((0, 2)).cpu()
            r["R3"][li] = a[:, :, t, t - 2].mean((0, 2)).cpu()
            r["R4"][li] = (a[:, :, 2:, 1:] * is_p[:, None, None, 1:]).sum(-1).mean((0, 2)).cpu()  # excl. position 0 (sink)
        halves[h] = r
    res = {"L": L, "H": H, "maps": {"R1": R1.numpy().round(5).tolist()}}
    for k in ("R2", "R3", "R4"):
        res["maps"][k] = ((halves["a"][k] + halves["b"][k]) / 2).numpy().round(5).tolist()
        res[f"reliability_{k}"] = float(np.corrcoef(halves["a"][k].flatten(), halves["b"][k].flatten())[0, 1])
    # R5: OV copying score from weights (fp32)
    m = model.model
    WE = m.embed_tokens.weight.float()
    WU = model.lm_head.weight.float() * m.norm.weight.float()[None, :]
    G = WE.T @ WU                                   # d x d  (W_E^T W_U, final-norm gain folded in)
    dh = model.config.hidden_size // H
    R5 = torch.zeros(L, H)
    for li, layer in enumerate(m.layers):
        WV = layer.self_attn.v_proj.weight.float() * layer.input_layernorm.weight.float()[None, :]   # (H*dh) x d
        WO = layer.self_attn.o_proj.weight.float()                                                   # d x (H*dh)
        for h in range(H):
            V, O = WV[h * dh:(h + 1) * dh], WO[:, h * dh:(h + 1) * dh]
            ev = torch.linalg.eigvals(V @ G @ O)         # nonzero spectrum of W_U W_O W_V W_E^T (up to transposition)
            R5[li, h] = (ev.real.sum() / ev.abs().sum()).cpu()
    res["maps"]["R5"] = R5.numpy().round(5).tolist()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs")
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--nworkers", type=int, default=1)
    ap.add_argument("--reverse", action="store_true")
    a = ap.parse_args()
    lines = [l.split() for j, l in enumerate(open(a.jobs)) if l.strip() and j % a.nworkers == a.worker]
    if a.reverse:
        lines = lines[::-1]
    while True:
        left = 0
        for fam, repo, rev, out, name in lines:
            f = mc.RESULTS / out / f"{name}.json"
            if f.exists():
                continue
            left += 1
            if not available(fam, repo, rev):
                continue
            t0 = time.time()
            model, tok = load(fam, repo, rev)
            res = measure_extra(model, tok)
            res.update({"repo": repo, "rev": rev})
            f.parent.mkdir(exist_ok=True)
            f.write_text(json.dumps(res))
            print(name, f"{time.time() - t0:.0f}s", {k: res[k] for k in res if k.startswith("reliab")}, flush=True)
            del model
            torch.cuda.empty_cache()
        if left == 0:
            return
        time.sleep(60)


if __name__ == "__main__":
    main()
