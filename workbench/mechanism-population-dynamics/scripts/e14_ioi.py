"""E14: IOI behaviour, name-mover role, and ablation necessity on one Pythia run. Protocol: experiments/E14-*.md.

Dataset generator: curt-tigges/circuits-over-time@803038e4eb data/ioi_dataset.py (Wang et al. 2022), unmodified.
Usage: e14_ioi.py --repo EleutherAI/pythia-160m-seed3 --step 143000 -> results/e14/<model>__step<N>.json
"""
import argparse
import json
import random
import sys
import time

import numpy as np
import torch

import mp_common as mc

sys.path.insert(0, str(mc.CACHE / "circuits-over-time"))
from path_patching_cm.ioi_dataset import IOIDataset  # noqa: E402  (the version Tigges et al. actually call)

OUT = mc.RESULTS / "e14"
N = 200
N_RAND = 20


def build(model):
    """Exactly utils/data_utils.generate_data_and_caches (seed=42, prepend_bos=False, add_bos_token=False)."""
    model.tokenizer.add_bos_token = False
    ioi = IOIDataset(prompt_type="mixed", N=N, tokenizer=model.tokenizer, prepend_bos=False, seed=42, device="cpu")
    abc = ioi.gen_flipped_prompts("ABB->ABA, BAB->BAA")
    return ioi, abc


def run(model, toks, hooks=()):
    return model.run_with_hooks(toks.to(model.cfg.device), fwd_hooks=list(hooks))


def logit_diff(model, ioi, hooks=()):
    logits = run(model, ioi.toks.long(), hooks)
    end = torch.as_tensor(ioi.word_idx["end"]).cpu()
    b = torch.arange(len(end))
    l_end = logits[b, end]
    io = torch.as_tensor(ioi.io_tokenIDs, device=l_end.device)
    s = torch.as_tensor(ioi.s_tokenIDs, device=l_end.device)
    return (l_end[b, io] - l_end[b, s]).float().cpu()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    model = mc.load_tl_model(args.repo, args.step)
    tok = model.tokenizer
    ioi, abc = build(model)
    L, H = model.cfg.n_layers, model.cfg.n_heads
    end = torch.as_tensor(ioi.word_idx["end"]).cpu()
    b = torch.arange(len(end))
    io_pos = torch.as_tensor(ioi.word_idx["IO"]).cpu()
    s_pos = torch.as_tensor(ioi.word_idx["S1"]).cpu()

    ld_clean = logit_diff(model, ioi)
    # direct logit attribution at END for every head, plus END->IO / END->S attention
    _, cache = model.run_with_cache(ioi.toks.long().to(model.cfg.device),
                                    names_filter=lambda n: n.endswith("hook_z") or n.endswith("hook_pattern")
                                    or n == "ln_final.hook_scale")
    scale = cache["ln_final.hook_scale"][b, end]  # [N, 1]
    io_ids = torch.as_tensor(ioi.io_tokenIDs, device=scale.device)
    s_ids = torch.as_tensor(ioi.s_tokenIDs, device=scale.device)
    udir = (model.W_U[:, io_ids] - model.W_U[:, s_ids]).T  # [N, d_model]
    dla = torch.zeros(L, H)
    att_io = torch.zeros(L, H)
    att_s = torch.zeros(L, H)
    for layer in range(L):
        z = cache[f"blocks.{layer}.attn.hook_z"][b, end]  # [N, H, d_head]
        res = torch.einsum("nhd,hdm->nhm", z, model.W_O[layer]) / scale[:, :, None]
        dla[layer] = (res * udir[:, None, :]).sum(-1).mean(0).cpu()
        pat = cache[f"blocks.{layer}.attn.hook_pattern"]  # [N, H, q, k]
        att_io[layer] = pat[b, :, end, io_pos].mean(0).cpu()
        att_s[layer] = pat[b, :, end, s_pos].mean(0).cpu()
    pos_sum = float(dla.clamp(min=0).sum())
    nmh = [(l, h) for l in range(L) for h in range(H) if dla[l, h] >= 0.1 * pos_sum and att_io[l, h] > att_s[l, h]]
    nmh = sorted(nmh, key=lambda x: -float(dla[x]))

    # ABC mean of z at END (mean-ablation reference)
    _, cache_abc = model.run_with_cache(abc.toks.long().to(model.cfg.device), names_filter=lambda n: n.endswith("hook_z"))
    end_abc = torch.as_tensor(abc.word_idx["end"]).cpu()
    b_abc = torch.arange(len(end_abc))
    mean_z = {l: cache_abc[f"blocks.{l}.attn.hook_z"][b_abc, end_abc].mean(0) for l in range(L)}  # [H, d_head]

    def hooks(heads):
        by = {}
        for l, h in heads:
            by.setdefault(l, []).append(h)

        def mk(l, hs):
            def hook(z, hook):
                for hh in hs:
                    z[b, end.to(z.device), hh] = mean_z[l][hh].to(z.dtype)
                return z
            return hook
        return [(f"blocks.{l}.attn.hook_z", mk(l, hs)) for l, hs in by.items()]

    res = {"repo": args.repo, "step": args.step, "protocol": "experiments/E14-ioi-portability.md",
           "logit_diff": float(ld_clean.mean()), "acc": float((ld_clean > 0).float().mean()),
           "nmh": [f"{l}.{h}" for l, h in nmh], "nmh_dla": [round(float(dla[x]), 3) for x in nmh],
           "top_dla": [(f"{l}.{h}", round(float(dla[l, h]), 3)) for l, h in
                       sorted(((l, h) for l in range(L) for h in range(H)), key=lambda x: -float(dla[x]))[:5]],
           "n_layers": L}
    if nmh:
        g = float(logit_diff(model, ioi, hooks(nmh)).mean())
        s1 = float(logit_diff(model, ioi, hooks(nmh[:1])).mean())
        rng = random.Random(1)
        pool = [(l, h) for l in range(L) for h in range(H) if (l, h) not in nmh]
        rnd = [float(logit_diff(model, ioi, hooks(rng.sample(pool, len(nmh)))).mean()) for _ in range(N_RAND)]
        res.update({"ld_group_ablated": g, "ld_top_ablated": s1, "ld_random_ablated": rnd})
    res["seconds"] = round(time.time() - t0, 1)
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    print(tag, f"LD {res['logit_diff']:.2f} acc {res['acc']:.2f} NMH {res['nmh']} "
          f"group {res.get('ld_group_ablated', float('nan')):.2f} top {res.get('ld_top_ablated', float('nan')):.2f} "
          f"rand-min {min(res.get('ld_random_ablated', [float('nan')])):.2f} ({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
