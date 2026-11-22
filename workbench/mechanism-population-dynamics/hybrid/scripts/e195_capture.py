#!/usr/bin/env python3
"""E195 capture: E194's R1 (set S, in-context 32-candidate retrieval) and R3 states (set N), architecture-agnostic.

Same definitions as e194_capture.py; adds (i) embedding/layer getters for model.model.* and model.backbone.*,
(ii) a per-tokenizer document-start id, (iii) --random SEED to build a randomly initialised copy from the config,
(iv) several items per forward pass (sequential-scan fallbacks are slow).
Usage: e195_capture.py MODE MODEL_DIR ITEMS_JSON OUT_DIR [--random SEED] [--limit K] [--items_per_batch B]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

MS = [2, 3, 4, 5, 6]
N_SRC = 300


def parts(model):
    base = getattr(model, "model", None) or getattr(model, "backbone")
    emb = getattr(base, "embed_tokens", None) or getattr(base, "embeddings", None) or getattr(base, "word_embeddings")
    return base, emb, list(base.layers)


class Capture:
    def __init__(self, model, start_id, pad_id):
        self.base, emb, layers = parts(model)
        self.start, self.pad, self.pos, self.out = start_id, pad_id, None, []
        self.hs = [m.register_forward_hook(self._hook) for m in [emb] + layers]

    def _hook(self, mod, inp, output):
        h = output[0] if isinstance(output, tuple) else output
        b = torch.arange(h.shape[0], device=h.device)[:, None]
        self.out.append(h[b, self.pos].float())

    @torch.no_grad()
    def run(self, seqs, offsets=(1,)):
        ids = [([self.start] if self.start is not None else []) + s for s in seqs]
        T = max(map(len, ids))
        x = torch.full((len(ids), T), self.pad, dtype=torch.long)
        for i, s in enumerate(ids):
            x[i, :len(s)] = torch.tensor(s)
        self.pos = torch.tensor([[len(s) - o for o in offsets] for s in ids], device="cuda")
        self.out = []
        self.base(input_ids=x.cuda(), use_cache=False)
        return torch.stack(self.out)  # [L+1, B, P, d]


def mode_nll(model, tok, start, passages):
    P = json.loads(Path(passages).read_text())
    nll, first, last = [], [], []
    for p in P["passages"][:50]:
        ids = ([start] if start is not None else []) + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
        x = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            lp = model(input_ids=x, use_cache=False).logits[0, :-1].float().log_softmax(-1)
        l = -lp.gather(1, x[0, 1:, None])[:, 0].cpu().numpy()
        nll.append(l)
        if len(l) >= 256:
            first.append(l[:128].mean()); last.append(l[-128:].mean())
    pr = tok("The capital of France is", add_special_tokens=False)["input_ids"]
    with torch.no_grad():
        p0 = ([start] if start is not None else []) + pr
        g = torch.tensor([p0], device="cuda")
        for _ in range(12):  # greedy without KV cache (remote code caches break under tf 4.57)
            g = torch.cat([g, model(input_ids=g, use_cache=False).logits[:, -1].argmax(-1, keepdim=True)], 1)
    return {"nll_mean": float(np.concatenate(nll).mean()), "first128": float(np.mean(first)), "last128": float(np.mean(last)),
            "greedy": tok.decode(g[0, len(p0):])}


def mode_S(cap, S, out, k_items):
    qnames = [f"split{m}" for m in MS] + [f"shuf{m}" for m in MS if m >= 3] + [f"last{m}" for m in MS]
    ranks, simown = [], []
    t0 = time.time()
    for b in range(0, len(S), k_items):
        chunk, seqs = S[b:b + k_items], []
        for it in chunk:
            ctx = it["ctx"]
            seqs += [ctx + [it["wid"]]] + [ctx + [d] for d in it["distract"]]
            for q in qnames:
                kind, m = q[:-1], q[-1]
                seqs.append(ctx + (it["splits"][m] if kind == "split" else it["shuf"][m] if kind == "shuf" else [it["splits"][m][-1]]))
        H = cap.run(seqs)[:, :, 0]
        per = 32 + len(qnames)
        for j in range(len(chunk)):
            h = H[:, j * per:(j + 1) * per]
            cand, q = h[:, :32], h[:, 32:]
            mu = cand.mean(1, keepdim=True)
            sims = torch.einsum("lqd,lcd->lqc", F.normalize(q - mu, dim=-1), F.normalize(cand - mu, dim=-1))
            ranks.append((sims[..., 1:] > sims[..., :1]).sum(-1).short().cpu())
            simown.append(sims[..., 0].half().cpu())
    torch.save({"ranks": torch.stack(ranks), "simown": torch.stack(simown), "qnames": qnames}, out / "S.pt")
    return {"n_items": len(S), "sec": round(time.time() - t0, 1)}


def mode_N(cap, N, out, bs=64):
    items = [it for it in N if it["nonword"] is not None]
    reps, t0 = [], time.time()
    for b in range(0, len(items), bs):
        chunk = items[b:b + bs]
        H = cap.run([it["ctx"] + it["pieces"] for it in chunk] + [it["ctx"] + it["nonword"] for it in chunk], offsets=(1, 2))
        n = len(chunk)
        reps.append(torch.stack([H[:, :n], H[:, n:]], 2).permute(1, 0, 2, 3, 4).half().cpu())
    torch.save({"reps": torch.cat(reps), "form": [it["form"] for it in items], "m": [it["m"] for it in items],
                "stratum": [it["stratum"] for it in items]}, out / "N.pt")
    return {"n_items": len(items), "sec": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode"); ap.add_argument("model"); ap.add_argument("items"); ap.add_argument("out")
    ap.add_argument("--random", type=int, default=-1); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--items_per_batch", type=int, default=4); ap.add_argument("--passages", default="")
    ap.add_argument("--no_start", action="store_true", help="no document-start token (dense Granite degenerates with it)")
    ap.add_argument("--trust", action="store_true", help="trust_remote_code (Ring/Ling, code read beforehand)")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(a.model, trust_remote_code=a.trust)
    start = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else start
    if a.no_start:
        start = None
    pad = pad if pad is not None else 0
    if a.random >= 0:
        torch.manual_seed(a.random)
        cfg = AutoConfig.from_pretrained(a.model, trust_remote_code=a.trust)
        model = AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16, trust_remote_code=a.trust).cuda().eval()
    else:
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", trust_remote_code=a.trust).eval()
    t0 = time.time()
    if a.mode == "nll":
        res = mode_nll(model, tok, start, a.passages)
    else:
        I = json.loads(Path(a.items).read_text())
        cap = Capture(model, start, pad)
        if a.mode == "S":
            res = mode_S(cap, I["S"][:a.limit] if a.limit else I["S"], out, a.items_per_batch)
        else:
            res = mode_N(cap, I["N"][:a.limit] if a.limit else I["N"], out)
    res.update(mode=a.mode, model=a.model, random=a.random, start_id=start, total_sec=round(time.time() - t0, 1))
    (out / f"{a.mode}_meta.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
