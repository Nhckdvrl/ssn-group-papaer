#!/usr/bin/env python3
"""E197: layer-wise cross-lingual readouts on UD PUD (1000 sentences x 12 languages).

M1  SoftCKA (Bandarkar et al. 2609.35378 eq. 1; RBF kernel, bandwidth = median pairwise distance of the pair's
    tokens at that layer, also x0.5 and x2), English vs each language, parallel pairs and mismatched pairs
    (English sentence perm[i] with target sentence i; perm = seeded derangement, seed 197).
M2  retrieval@1: mean-pooled tokens, minus the language's mean at that layer, cosine, en -> X among 1000.
M3  PC1 explained-variance share of all tokens (all languages) at each layer.
Layer index 0 = embedding output, l+1 = output of decoder layer l. Start token (if any) is excluded.
Usage: e197_xling.py MODEL_DIR PUD_JSON OUT_JSON [--start ID|none]
"""
import argparse
import json
import time

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

SIGMA_MULT = (0.5, 1.0, 2.0)


def find_parts(model):
    best = None
    for name, mod in model.named_modules():
        if isinstance(mod, torch.nn.ModuleList) and name.split(".")[-1] == "layers":
            parent = model.get_submodule(name.rsplit(".", 1)[0]) if "." in name else model
            emb = getattr(parent, "embed_tokens", None) or getattr(parent, "embeddings", None)
            if emb is not None and (best is None or len(mod) > len(best[1])):
                best = (emb, list(mod))
    return best


def layer_types(model):
    cfg = model.config
    cfg = getattr(cfg, "text_config", None) or cfg
    lt = getattr(cfg, "layer_types", None)
    if lt is None and getattr(cfg, "hybrid_override_pattern", None):
        lt = list(cfg.hybrid_override_pattern)
    return lt


def softcka_terms(X, Y, sig_mult):
    """X [L, T1, d], Y [L, T2, d] -> h12, h11, h22 per layer per sigma: [L, S]."""
    Z = torch.cat([X, Y], 1)
    D = torch.cdist(Z, Z) ** 2  # [L, T, T]
    T1 = X.shape[1]
    iu = torch.triu_indices(D.shape[1], D.shape[1], 1, device=D.device)
    med = D[:, iu[0], iu[1]].sqrt().median(-1).values.clamp_min(1e-6)  # [L]
    out = []
    for s in sig_mult:
        K = torch.exp(-D / (2 * (s * med)[:, None, None] ** 2))
        k11, k22, k12 = K[:, :T1, :T1], K[:, T1:, T1:], K[:, :T1, T1:]
        c = lambda k: k - k.mean(1, keepdim=True) - k.mean(2, keepdim=True) + k.mean((1, 2), keepdim=True)
        out.append(torch.stack([(c(k12) ** 2).sum((1, 2)), (c(k11) ** 2).sum((1, 2)), (c(k22) ** 2).sum((1, 2))], -1))
    return torch.stack(out, 1)  # [L, S, 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("pud"); ap.add_argument("out"); ap.add_argument("--start", default="auto")
    ap.add_argument("--bs", type=int, default=24)
    ap.add_argument("--cond", default="none", help="E200: none | noconv | nomem | none_mix (recurrent layers given by --layers)")
    ap.add_argument("--layers", default="")
    a = ap.parse_args()
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    emb, layers = find_parts(model)
    if a.cond != "none":
        for li in [int(x) for x in a.layers.split(",")]:
            mx = next(m for m in layers[li].modules() if hasattr(m, "conv1d") and hasattr(m, "A_log"))
            with torch.no_grad():
                if a.cond in ("noconv", "none_mix"):
                    mx.conv1d.weight[..., :-1] = 0
                if a.cond in ("nomem", "none_mix"):
                    mx.A_log += 20
    lt = layer_types(model)
    start = None if a.start == "none" else (int(a.start) if a.start != "auto" else None)
    pad = tok.pad_token_id if tok.pad_token_id is not None else (tok.eos_token_id or 0)
    P = json.loads(open(a.pud).read())
    langs, ids = P["langs"], P["ids"]
    N = len(ids)
    feats = []
    hs = [m.register_forward_hook(lambda mod, i, o: feats.append((o[0] if isinstance(o, tuple) else o).detach()))
          for m in [emb] + layers]
    pre = [start] if start is not None else []
    enc = {lg: [pre + tok(P["text"][s][lg], add_special_tokens=False)["input_ids"][:200] for s in ids] for lg in langs}
    off = len(pre)

    @torch.no_grad()
    def states(seqs):
        T = max(map(len, seqs))
        x = torch.full((len(seqs), T), pad, dtype=torch.long)
        for i, s in enumerate(seqs):
            x[i, :len(s)] = torch.tensor(s)
        feats.clear()
        model(input_ids=x.cuda())
        H = torch.stack(feats)  # [L+1, B, T, d]
        return [H[:, i, off:len(s)].float() for i, s in enumerate(seqs)]

    Lp1 = len(layers) + 1
    d = None
    pooled = {}
    cov_sum, mu_sum, n_tok = None, None, 0
    en_states = []
    # English first (kept on CPU in fp16 for SoftCKA pairing)
    for b in range(0, N, a.bs):
        for st in states(enc["en"][b:b + a.bs]):
            en_states.append(st.half().cpu())
    rng = np.random.default_rng(197)
    perm = rng.permutation(N)
    while np.any(perm == np.arange(N)):
        perm = rng.permutation(N)
    acc = {lg: torch.zeros(Lp1, len(SIGMA_MULT), 3, 2, device="cuda", dtype=torch.float64) for lg in langs if lg != "en"}
    for lg in langs:
        pl = []
        for b in range(0, N, a.bs):
            sts = states(enc[lg][b:b + a.bs]) if lg != "en" else [s.cuda().float() for s in en_states[b:b + a.bs]]
            for j, st in enumerate(sts):
                i = b + j
                pl.append(st.mean(1).half().cpu())
                if d is None:
                    d = st.shape[-1]
                    cov_sum = torch.zeros(Lp1, d, d, device="cuda", dtype=torch.float64)
                    mu_sum = torch.zeros(Lp1, d, device="cuda", dtype=torch.float64)
                if i % 4 == 0:  # PC1 from every 4th sentence of every language
                    s64 = st.double()
                    cov_sum += torch.einsum("ltd,lte->lde", s64, s64); mu_sum += s64.sum(1); n_tok += st.shape[1]
                if lg != "en":
                    acc[lg][..., 0] += softcka_terms(en_states[i].cuda().float(), st, SIGMA_MULT).double()
                    acc[lg][..., 1] += softcka_terms(en_states[perm[i]].cuda().float(), st, SIGMA_MULT).double()
        pooled[lg] = torch.stack(pl)  # [N, L+1, d]
        print(json.dumps({"lang": lg, "sec": round(time.time() - t0, 1)}), flush=True)
    # M1
    res = {"model": a.model, "cond": a.cond, "switched_layers": a.layers, "layer_types": lt, "langs": langs, "n": N, "sigma_mult": SIGMA_MULT, "M1": {}, "M1mis": {}, "M2": {}}
    for lg, A in acc.items():
        h = A.cpu().numpy()  # [L+1, S, 3, 2]
        res["M1"][lg] = (h[..., 0, 0] / np.sqrt(h[..., 1, 0] * h[..., 2, 0])).tolist()
        res["M1mis"][lg] = (h[..., 0, 1] / np.sqrt(h[..., 1, 1] * h[..., 2, 1])).tolist()
    # M2
    E = pooled["en"].float()
    E = F.normalize(E - E.mean(0, keepdim=True), dim=-1)
    for lg in langs:
        if lg == "en":
            continue
        X = pooled[lg].float()
        X = F.normalize(X - X.mean(0, keepdim=True), dim=-1)
        accs = []
        for l in range(Lp1):
            S = E[:, l] @ X[:, l].T
            accs.append(float((S.argmax(1) == torch.arange(N)).float().mean()))
        res["M2"][lg] = accs
    # M3
    mu = mu_sum / n_tok
    cov = cov_sum / n_tok - torch.einsum("ld,le->lde", mu, mu)
    ev = torch.linalg.eigvalsh(cov)
    res["M3_pc1"] = (ev[:, -1] / ev.sum(-1)).cpu().tolist()
    res["sec"] = round(time.time() - t0, 1)
    open(a.out, "w").write(json.dumps(res))
    print(json.dumps({"done": a.out, "sec": res["sec"]}), flush=True)


if __name__ == "__main__":
    main()
