"""E02b (I04): simulated AdamW trajectory of the LM head alone, driven by replayed post-training gradients.

Features (hidden states) are frozen at the replayed checkpoint; each batch = one prompt group; the same batch
set and order (non-zero-advantage groups, shuffled with seed 0) is used for every condition, so conditions
differ only in their token weights:
  ce_onpolicy c=1/(G|o_i|) · rl c=A_i/(G|o_i|) · rft c=r_i/(G|o_i|) · teacher c=1/|ref| (reference solution)
Adam: β1=0.9, β2=0.999, ε=1e-8, lr=1, no weight decay, bias-corrected. Per row j we record the cumulative update
U_j = -Σ_t m̂_t/(√v̂_t+ε) and summarise: per-element drift ‖U_j‖/(√d·T) (1 = every step a full-size step in a
consistent direction), cos(U_j, -μ) with μ the mean hidden state, and the induced logit shift U_j·μ/‖μ‖.
Rows are bucketed by whether the token was ever a target in that condition and by Pile frequency.
Per-row arrays are saved node-locally for comparison with real checkpoint deltas (E01).

Usage: python e02_headadam.py --model qwen3-8b-base --rollouts /tmp/xiang_lmhead/e02/rollouts_qwen3-8b-base.jsonl
"""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch

import models
from lmhead_geom import stable_ce_terms

ROOT = Path(__file__).resolve().parents[1]
BIG = Path("/tmp/xiang_lmhead/e02")
CONDS = ("ce_onpolicy", "rl", "rft", "teacher")


class AdamHead:
    def __init__(self, V, d, dev, b1=0.9, b2=0.999, eps=1e-8):
        z = lambda: torch.zeros(V, d, device=dev)
        self.m, self.v, self.U, self.G = z(), z(), z(), z()
        self.b1, self.b2, self.eps, self.t = b1, b2, eps, 0
        self.tgt = torch.zeros(V, dtype=torch.long, device=dev)

    def add(self, p, a, h, c):
        self.G += (p * c[:, None]).T @ h
        self.G.index_add_(0, a, -(c[:, None] * h))
        self.tgt.index_add_(0, a, torch.ones_like(a))

    def step(self):
        self.t += 1
        self.m.mul_(self.b1).add_(self.G, alpha=1 - self.b1)
        self.v.mul_(self.b2).addcmul_(self.G, self.G, value=1 - self.b2)
        mh = self.m / (1 - self.b1 ** self.t)
        vh = self.v / (1 - self.b2 ** self.t)
        self.U.sub_(mh / (vh.sqrt() + self.eps))
        self.G.zero_()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-8b-base")
    ap.add_argument("--rollouts", required=True)
    ap.add_argument("--chunk", type=int, default=512)
    ap.add_argument("--out", default=str(ROOT / "results" / "e02"))
    args = ap.parse_args()
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = False
    t0 = time.time()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(args.model))
    m = AutoModelForCausalLM.from_pretrained(models.path(args.model), dtype=torch.bfloat16).to(dev).eval()
    W = m.lm_head.weight.detach().float()
    V, d = W.shape
    groups = [json.loads(l) for l in open(args.rollouts)]
    keep = [g for g in groups if np.std([c["reward"] for c in g["completions"]]) > 0]
    random.Random(0).shuffle(keep)
    opt = {c: AdamHead(V, d, dev) for c in CONDS}
    mu_sum = torch.zeros(d, dtype=torch.float64, device=dev); mu_n = 0
    from build_inputs import math_split

    @torch.no_grad()
    def hid(prompt_ids, ids):
        x = torch.tensor([prompt_ids + ids], device=dev)
        return m.model(input_ids=x).last_hidden_state[0, len(prompt_ids) - 1: -1].float(), torch.tensor(ids, device=dev)

    for gi, g in enumerate(keep):
        r = np.array([c["reward"] for c in g["completions"]]); G = len(r)
        A = (r - r.mean()) / (r.std() + 1e-6)
        ref = tok(" " + math_split(g["subject"])[g["index"]]["solution"], add_special_tokens=False)["input_ids"]
        seqs = [(c["token_ids"], {"ce_onpolicy": 1 / (G * len(c["token_ids"])), "rl": A[i] / (G * len(c["token_ids"])),
                                  "rft": r[i] / (G * len(c["token_ids"]))}) for i, c in enumerate(g["completions"]) if c["token_ids"]]
        seqs.append((ref, {"teacher": 1.0 / len(ref)}))
        for ids, coefs in seqs:
            h, a = hid(g["prompt_ids"], ids)
            mu_sum += h.double().sum(0); mu_n += len(ids)
            for s in range(0, len(ids), args.chunk):
                hs, as_ = h[s:s + args.chunk], a[s:s + args.chunk]
                p, *_ = stable_ce_terms(hs @ W.T, as_, W)
                for cname, cval in coefs.items():
                    if cval != 0:
                        opt[cname].add(p, as_, hs, torch.full((len(as_),), float(cval), device=dev))
        for o in opt.values():
            o.step()
        if gi % 10 == 0:
            print(f"step {gi}/{len(keep)} {time.time() - t0:.0f}s", flush=True)

    mu = (mu_sum / mu_n).float()
    mu_hat = mu / mu.norm()
    from e01_weights import row_buckets, token_freq
    freq, _ = token_freq(tok, V)
    special = set(tok.all_special_ids) | set(tok.get_added_vocab().values())
    bk = row_buckets(V, len(tok), special, freq)
    T = len(keep)
    res = {"model": args.model, "revision": models.revision(args.model), "steps": T, "adam": "b1=0.9 b2=0.999 eps=1e-8 lr=1 wd=0",
           "mu_norm": float(mu.norm()), "conds": {}}
    BIG.mkdir(parents=True, exist_ok=True)
    arrays = {"mu": mu.cpu().numpy(), "pile_freq": freq}
    for cname, o in opt.items():
        drift = (o.U.norm(dim=1) / (d ** 0.5 * T)).cpu().numpy()
        cosmu = torch.nn.functional.cosine_similarity(o.U, -mu_hat[None, :].expand_as(o.U), dim=1).cpu().numpy()
        lshift = (o.U @ mu_hat).cpu().numpy() / T
        tc = o.tgt.cpu().numpy()
        dd = {}
        for name, mask in [("all", np.ones(V, bool)), ("target_rows", tc > 0), ("never_target_rows", tc == 0)] + \
                          [(f"bucket_{b}", bk == b) for b in sorted(set(bk))]:
            if mask.sum():
                dd[name] = {"n_rows": int(mask.sum()), "mean_drift": float(drift[mask].mean()),
                            "mean_cos_minus_mu": float(np.nanmean(cosmu[mask])), "mean_logit_shift_per_step": float(lshift[mask].mean())}
        res["conds"][cname] = dd
        arrays.update({f"{cname}.drift": drift.astype(np.float32), f"{cname}.cos_minus_mu": cosmu.astype(np.float32),
                       f"{cname}.logit_shift": lshift.astype(np.float32), f"{cname}.tgt_count": tc})
    np.savez_compressed(BIG / f"headadam_{args.model}.npz", **arrays)
    res["seconds"] = time.time() - t0
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    (out / f"headadam_{args.model}.json").write_text(json.dumps(res, indent=1))
    for c in CONDS:
        print(c, {k: res["conds"][c][k] for k in ("target_rows", "never_target_rows")})


if __name__ == "__main__":
    main()
