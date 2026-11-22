#!/usr/bin/env python3
"""E194 capture (one model per call).

mode nll : gate-0 load check (per-token NLL on 50 EWT passages, first/last-128 trend, a greedy continuation).
mode S   : R1 in-context retrieval for set S. Per item, the intact word and 31 distractor words are placed in the
           item's own context; split / prefix-shuffled / last-piece-only queries are compared with these 32
           candidates after subtracting their mean (removes the shared context direction and anisotropy).
           Stores the rank of the own word per (layer, query) and the R2 source vectors for the first N_SRC items.
mode N   : last- and penultimate-token states of natural multi-token words and their nonwords (R3, R2 sources).
Layer index 0 = embedding output, l+1 = output of decoder layer l (residual stream, before the final norm).
Usage: e194_capture.py MODE MODEL_DIR ITEMS_JSON OUT_DIR [--limit K]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

EOS, PAD, N_SRC = 100257, 100277, 300
MS = [2, 3, 4, 5, 6]


def load(model_dir):
    m = AutoModelForCausalLM.from_pretrained(model_dir, dtype=torch.bfloat16, device_map="cuda")
    m.eval()
    return m


class Capture:
    """Hooks on embedding + every decoder layer; keeps only the requested positions."""

    def __init__(self, model):
        self.base = model.model
        self.pos = None
        self.out = []
        mods = [self.base.embed_tokens] + list(self.base.layers)
        self.hs = [mod.register_forward_hook(self._hook) for mod in mods]

    def _hook(self, mod, inp, output):
        h = output[0] if isinstance(output, tuple) else output
        b = torch.arange(h.shape[0], device=h.device)[:, None]
        self.out.append(h[b, self.pos].float())  # [B, P, d]

    @torch.no_grad()
    def run(self, seqs, offsets=(1,)):
        ids = [[EOS] + s for s in seqs]
        T = max(map(len, ids))
        x = torch.full((len(ids), T), PAD, dtype=torch.long)
        for i, s in enumerate(ids):
            x[i, :len(s)] = torch.tensor(s)
        self.pos = torch.tensor([[len(s) - o for o in offsets] for s in ids], device="cuda")
        self.out = []
        self.base(input_ids=x.cuda())  # right padding only: causal mixers never see the pads
        return torch.stack(self.out)  # [L+1, B, P, d]


def mode_nll(model, P, out):
    tok_texts = [p["text"] for p in P["passages"][:50]]
    tok = AutoTokenizer.from_pretrained(str(Path(out).parent.parent / "tok"))
    nll, first, last = [], [], []
    for t in tok_texts:
        ids = [EOS] + tok(t, add_special_tokens=False)["input_ids"][:511]
        x = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            lp = model(input_ids=x).logits[0, :-1].float().log_softmax(-1)
        l = -lp.gather(1, x[0, 1:, None])[:, 0].cpu().numpy()
        nll.append(l)
        if len(l) >= 256:
            first.append(l[:128].mean()); last.append(l[-128:].mean())
    prompt = tok("The capital of France is", add_special_tokens=False)["input_ids"]
    with torch.no_grad():
        g = model.generate(torch.tensor([[EOS] + prompt], device="cuda"), max_new_tokens=12, do_sample=False)
    res = {"nll_mean": float(np.concatenate(nll).mean()), "n_tokens": int(sum(map(len, nll))),
           "first128": float(np.mean(first)) if first else None, "last128": float(np.mean(last)) if last else None,
           "n_long": len(first), "greedy": tok.decode(g[0, len(prompt) + 1:])}
    return res


def mode_S(model, S, out, limit):
    cap = Capture(model)
    items = S[:limit] if limit else S
    qnames = [f"split{m}" for m in MS] + [f"shuf{m}" for m in MS if m >= 3] + [f"last{m}" for m in MS]
    ranks, simown, srcs = [], [], []
    t0 = time.time()
    for i, it in enumerate(items):
        ctx = it["ctx"]
        seqs = [ctx + [it["wid"]]] + [ctx + [d] for d in it["distract"]]
        for q in qnames:
            kind, m = q[:-1], q[-1]
            if kind == "split":
                seqs.append(ctx + it["splits"][m])
            elif kind == "shuf":
                seqs.append(ctx + it["shuf"][m])
            else:
                seqs.append(ctx + [it["splits"][m][-1]])
        H = cap.run(seqs)[:, :, 0]  # [L+1, 46, d]
        cand, q = H[:, :32], H[:, 32:]
        mu = cand.mean(1, keepdim=True)
        cn = F.normalize(cand - mu, dim=-1)
        qn = F.normalize(q - mu, dim=-1)
        sims = torch.einsum("lqd,lcd->lqc", qn, cn)  # [L+1, Q, 32]
        ranks.append((sims[..., 1:] > sims[..., :1]).sum(-1).short().cpu())
        simown.append(sims[..., 0].half().cpu())
        if i < N_SRC:
            srcs.append(torch.cat([H[:, :1], H[:, 32:37]], 1).half().cpu())  # intact, split2..6
        if i == 4:
            print(json.dumps({"timing_5_items_s": round(time.time() - t0, 2)}), flush=True)
    torch.save({"ranks": torch.stack(ranks), "simown": torch.stack(simown), "qnames": qnames,
                "src": torch.stack(srcs), "src_names": ["m1"] + [f"m{m}" for m in MS]}, out / "S.pt")
    return {"n_items": len(items), "sec": round(time.time() - t0, 1)}


def mode_N(model, N, out, limit, bs=64):
    cap = Capture(model)
    items = [it for it in N if it["nonword"] is not None]
    items = items[:limit] if limit else items
    reps = []
    t0 = time.time()
    for b in range(0, len(items), bs):
        chunk = items[b:b + bs]
        seqs = [it["ctx"] + it["pieces"] for it in chunk] + [it["ctx"] + it["nonword"] for it in chunk]
        H = cap.run(seqs, offsets=(1, 2))  # [L+1, 2B, 2, d]
        n = len(chunk)
        reps.append(torch.stack([H[:, :n], H[:, n:]], 2).permute(1, 0, 2, 3, 4).half().cpu())  # [B, L+1, 2, 2, d]
    torch.save({"reps": torch.cat(reps), "form": [it["form"] for it in items], "m": [it["m"] for it in items],
                "stratum": [it["stratum"] for it in items], "pieces": [it["pieces"] for it in items]}, out / "N.pt")
    return {"n_items": len(items), "sec": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode"); ap.add_argument("model"); ap.add_argument("items"); ap.add_argument("out")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(194)
    model = load(a.model)
    t0 = time.time()
    if a.mode == "nll":
        res = mode_nll(model, json.loads(Path(a.items).read_text()), out)
    else:
        I = json.loads(Path(a.items).read_text())
        res = mode_S(model, I["S"], out, a.limit) if a.mode == "S" else mode_N(model, I["N"], out, a.limit)
    res.update(mode=a.mode, model=a.model, total_sec=round(time.time() - t0, 1))
    (out / f"{a.mode}_meta.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
