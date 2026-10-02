"""E13: context-vs-memory arbitration (Yu et al. 2023 world capitals) on one Pythia run. Protocol: experiments/E13-*.md.

Usage: e13_arbitration.py --repo EleutherAI/pythia-410m-seed3 --step 143000 -> results/e13/<model>__step<N>.json
"""
import argparse
import json
import random
import time

import numpy as np
import torch
from datasets import load_dataset

import mp_common as mc

OUT = mc.RESULTS / "e13"
CF = "The capital of {country} is {distractor}. Q: What is the capital of {country}? A:"
CLEAN = "Q: What is the capital of {country}? A:"
K_DIST = 20


def capitals():
    ds = load_dataset("gaotang/ParaConflict", split="test")
    out = {}
    for r in ds:
        if r["Category"] == "World Capital":
            ans = r["Answer"] if isinstance(r["Answer"], list) else [r["Answer"]]
            out.setdefault(r["Subject"], ans[0])
    return out


@torch.no_grad()
def cand_logprob(model, prompts, cands, hooks=(), bs=64):
    """Sum log-prob of ' '+cand after prompt (teacher forcing)."""
    tok = model.tokenizer
    out = []
    for i in range(0, len(prompts), bs):
        P, C = prompts[i:i + bs], cands[i:i + bs]
        pi = [tok(p, add_special_tokens=False)["input_ids"] for p in P]
        ci = [tok(" " + c, add_special_tokens=False)["input_ids"] for c in C]
        seqs = [[tok.bos_token_id] + a + b for a, b in zip(pi, ci)]
        L = max(map(len, seqs))
        ids = torch.full((len(seqs), L), tok.pad_token_id or 0)
        for j, s in enumerate(seqs):
            ids[j, :len(s)] = torch.tensor(s)
        logp = model.run_with_hooks(ids.to(model.cfg.device), fwd_hooks=list(hooks)).log_softmax(-1)
        for j, (a, b) in enumerate(zip(pi, ci)):
            st = 1 + len(a)
            pos = torch.arange(st - 1, st - 1 + len(b), device=logp.device)
            out.append(float(logp[j, pos, torch.tensor(b, device=logp.device)].sum()))
    return np.array(out)


def scale_hook(layer, head, alpha):
    def hook(z, hook):
        z[:, :, head, :] *= alpha
        return z
    return [(f"blocks.{layer}.attn.hook_z", hook)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    model = mc.load_tl_model(args.repo, args.step)
    caps = capitals()
    countries = sorted(caps)
    rng = random.Random(0)
    dist = {c: rng.sample([caps[o] for o in countries if o != c and caps[o].lower() != caps[c].lower()], K_DIST)
            for c in countries}
    # known set: clean prompt prefers the true capital over all sampled distractors
    pr, cd = [], []
    for c in countries:
        for x in [caps[c]] + dist[c]:
            pr.append(CLEAN.format(country=c)), cd.append(x)
    lp = cand_logprob(model, pr, cd).reshape(len(countries), K_DIST + 1)
    known = [c for c, row in zip(countries, lp) if row[0] > row[1:].max()]
    # counterfactual prompts on the known set

    def adoption(hooks=(), subset=None):
        cs = known if subset is None else subset
        P, T, D = [], [], []
        for c in cs:
            for d in dist[c]:
                P.append(CF.format(country=c, distractor=d)), T.append(caps[c]), D.append(d)
        lt = cand_logprob(model, P, T, hooks)
        ld = cand_logprob(model, P, D, hooks)
        per_country = (ld > lt).reshape(len(cs), K_DIST).mean(1)
        adoption.margin = (lt - ld).reshape(len(cs), K_DIST).mean(1)
        return float(per_country.mean()), per_country

    rate, per_c = adoption()
    margin_c = adoption.margin
    boots = [np.random.default_rng(i).choice(per_c, len(per_c)).mean() for i in range(1000)]
    mboots = [np.random.default_rng(i).choice(margin_c, len(margin_c)).mean() for i in range(1000)]
    # head attribution at the final prompt position: direct effect on logit(true first tok) - logit(distractor first tok)
    tok = model.tokenizer
    H, Lyr = model.cfg.n_heads, model.cfg.n_layers
    attr = torch.zeros(Lyr, H, device=model.cfg.device)
    n = 0
    sub = known[:60]
    for c in sub:
        for d in dist[c][:5]:
            ids = model.to_tokens(CF.format(country=c, distractor=d))
            _, cache = model.run_with_cache(ids, names_filter=lambda nm: nm.endswith("hook_z") or nm.endswith("ln_final.hook_scale"))
            ti = tok(" " + caps[c], add_special_tokens=False)["input_ids"][0]
            di = tok(" " + d, add_special_tokens=False)["input_ids"][0]
            if ti == di:
                continue
            u = model.W_U[:, ti] - model.W_U[:, di]
            scale = cache["ln_final.hook_scale"][0, -1]
            for layer in range(Lyr):
                z = cache[f"blocks.{layer}.attn.hook_z"][0, -1]  # [H, d_head]
                res = torch.einsum("hd,hdm->hm", z, model.W_O[layer]) / scale
                attr[layer] += res @ u
            n += 1
    attr = (attr / max(n, 1)).cpu()
    flat = [(float(attr[l, h]), l, h) for l in range(Lyr) for h in range(H)]
    mem = sorted(flat, reverse=True)[:3]
    ctx = sorted(flat)[:3]
    # gain test on the top memory head
    _, ml, mh = mem[0]
    gain = {}
    sub2 = known[:80]
    for a in (0.0, 0.5, 1.0, 2.0):
        gain[str(a)] = adoption(scale_hook(ml, mh, a), sub2)[0]
    res = {"repo": args.repo, "step": args.step, "protocol": "experiments/E13-arbitration-across-runs.md",
           "n_countries": len(countries), "n_known": len(known), "adoption": rate,
           "adoption_ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
           "memory_margin": float(margin_c.mean()),
           "memory_margin_ci95": [float(np.percentile(mboots, 2.5)), float(np.percentile(mboots, 97.5))],
           "memory_heads": [(f"{l}.{h}", round(v, 3)) for v, l, h in mem],
           "context_heads": [(f"{l}.{h}", round(v, 3)) for v, l, h in ctx],
           "gain_top_memory_head": gain, "seconds": round(time.time() - t0, 1)}
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    print(tag, f"known {len(known)}/{len(countries)} adoption {rate:.3f} margin {res['memory_margin']:.2f}",
          "mem", res["memory_heads"], "ctx", res["context_heads"], "gain", {k: round(v, 3) for k, v in gain.items()},
          f"({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
