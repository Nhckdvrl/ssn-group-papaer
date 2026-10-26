"""E01: induction instrument on one Pythia-70M checkpoint (protocol frozen in experiments/E01-*.md).

R1   parent induction score (kayoyin/icl-heads find_induction_heads, seed 42, 1000 seqs) — per head
R1rep  same with seed 43 (ranking stability)
R1b  same random tokens fed as tensors (no decode/re-tokenize) — implementation-sensitivity diagnostic
R2   token-loss difference loss@50 - loss@500 on NeelNanda/pile-10k (parent construction), N=2000, per sequence
R3   held-out repeated random tokens (seed 12345, vocab [0,50277), 500 seqs): first-half vs second-half loss
R4   ablate top-k heads by R1 (k in 1,2,3,4,7,9) vs 20 random k-sets; methods: parent (hook_v), zero, mean
Writes results/e01/<model>__<rev>.json (+ per-sequence arrays .pt kept out of git).
"""
import argparse
import json
import os
import random
import sys
import time
from functools import partial

import numpy as np
import torch

import mp_common as mc

sys.path.insert(0, str(mc.PARENT_CODE / "src"))
from find_induction_heads import find_induction_heads, generate_repeated_random_tokens  # noqa: E402
import transformer_lens.utils as tl_utils  # noqa: E402
from utils.ablate_utils import head_ablation_hook, run_and_cache_model_random_tokens  # noqa: E402
from utils.model_utils import set_seed  # noqa: E402

KS = [1, 2, 3, 4, 7, 9]
N_RANDOM_SETS = 20
N_PILE = 2000
N_REP = 500
REAL_VOCAB = 50277
OUTDIR = mc.RESULTS / "e01"


# ---------------- data ----------------
def pile_eval_set(model):
    from transformer_lens import utils as tl_utils
    from datasets import load_dataset

    cf = mc.CACHE / "pile_eval_2000_seed42.pt"  # deterministic; same tokenizer for every Pythia-70M run
    if cf.exists():
        d = torch.load(cf)
        return d["tokens"], d["idx"]
    ds = load_dataset("NeelNanda/pile-10k", split="train")
    tok = tl_utils.tokenize_and_concatenate(ds, model.tokenizer)  # parent construction (1023 + BOS)
    g = torch.Generator().manual_seed(42)
    idx = torch.randperm(len(tok), generator=g)[:N_PILE]
    toks = tok["tokens"][idx]
    tmp = cf.with_suffix(f".{os.getpid()}.tmp")
    torch.save({"tokens": toks, "idx": idx}, tmp)
    tmp.replace(cf)
    return toks, idx


def held_out_repeated(model, n=N_REP, half=50, seed=12345):
    g = torch.Generator().manual_seed(seed)
    r = torch.randint(0, REAL_VOCAB, (n, half), generator=g)
    bos = torch.full((n, 1), model.tokenizer.bos_token_id)
    return torch.cat([bos, r, r], dim=1)


# ---------------- readouts ----------------
@torch.no_grad()
def induction_score_tensor(model, seed=42, batch=1000, seq_len=50):
    """R1b: parent's token generator, but tensors fed directly; parent 'mul' definition."""
    from transformer_lens.head_detector import get_induction_head_detection_pattern

    toks = generate_repeated_random_tokens(model, batch, seq_len, seed)
    L, H = model.cfg.n_layers, model.cfg.n_heads
    acc = torch.zeros(L, H, device=model.cfg.device)
    for i in range(0, batch, 100):
        tb = toks[i:i + 100]
        det = torch.stack([get_induction_head_detection_pattern(t[None].cpu()) for t in tb]).to(acc.device)
        _, cache = model.run_with_cache(tb, names_filter=lambda n: n.endswith("hook_pattern"))
        for layer in range(L):
            pat = cache["pattern", layer]  # [b, h, q, k]
            acc[layer] += ((pat * det[:, None]).sum((-1, -2)) / pat.sum((-1, -2))).sum(0)
    return (acc / batch).cpu()


R2_POS = [50, 500]                                   # parent reads loss_vec[..., 50] and [..., 500]
R3_POS = list(range(1, 50)) + list(range(51, 100))  # predict r2..r50 and r2'..r50'


def loss_at(model, toks, positions, fwd_hooks=(), bs=100):
    """Per-token loss (TL indexing: entry j = loss of predicting token j+1) at `positions` only.

    Numerically the same as model(..., return_type="loss", loss_per_token=True)[:, positions]; skips the
    unembed/log_softmax at unused positions (which dominated runtime).
    """
    pos = torch.tensor(positions)
    out = []
    store = {}

    def grab(x, hook):
        store["x"] = x[:, pos.to(x.device)]
        return x

    with torch.no_grad():
        for i in range(0, len(toks), bs):
            tb = toks[i:i + bs].to(model.cfg.device)
            model.run_with_hooks(tb, return_type=None,
                                 fwd_hooks=list(fwd_hooks) + [("ln_final.hook_normalized", grab)])
            logp = model.unembed(store["x"]).log_softmax(-1)
            tgt = tb[:, pos.to(tb.device) + 1]
            out.append((-logp.gather(-1, tgt[..., None])[..., 0]).float().cpu())
    return torch.cat(out)


def per_token_loss(model, toks, fwd_hooks=(), bs=50):
    """Full per-token loss (kept for the equivalence check)."""
    out = []
    with torch.no_grad():
        for i in range(0, len(toks), bs):
            tb = toks[i:i + bs].to(model.cfg.device)
            out.append(model.run_with_hooks(tb, return_type="loss", loss_per_token=True,
                                            fwd_hooks=list(fwd_hooks)).float().cpu())
    return torch.cat(out)


def r2_from_loss(lv):
    return lv[:, 0] - lv[:, 1]  # columns = R2_POS; parent: loss@50 - loss@500 (higher = more in-context benefit)


def r3_from_loss(lv):
    return lv[:, :49].mean(1), lv[:, 49:].mean(1)  # columns = R3_POS: first half, second half


# ---------------- ablations ----------------
def parent_random_cache(model, seq_len):
    set_seed(42)
    _, _, cache = run_and_cache_model_random_tokens(model, seq_len, 1)
    cache.remove_batch_dim()
    return cache


def parent_hooks(heads, cache):
    """Exactly the hook list built by utils.ablate_utils.run_loss_with_ablation."""
    return [(tl_utils.get_act_name("v", layer),
             partial(head_ablation_hook, head_index_to_ablate=head,
                     act_name=tl_utils.get_act_name("v", layer), random_cache=cache))
            for layer, head in heads]


def z_hooks(heads, mode, mean_z=None):
    by_layer = {}
    for layer, h in heads:
        by_layer.setdefault(layer, []).append(h)

    def hook(z, hook, hs):
        if mode == "zero":
            z[:, :, hs, :] = 0.0
        else:
            z[:, :, hs, :] = mean_z[hook.layer()][hs].to(z.device)
        return z

    return [(f"blocks.{layer}.attn.hook_z", partial(hook, hs=hs)) for layer, hs in by_layer.items()]


@torch.no_grad()
def mean_z(model, pile_toks, n=200):
    L = model.cfg.n_layers
    sums, count = [0.0] * L, 0
    for i in range(0, n, 50):
        tb = pile_toks[i:i + 50, :512].to(model.cfg.device)
        _, cache = model.run_with_cache(tb, names_filter=lambda nm: nm.endswith("hook_z"))
        for layer in range(L):
            sums[layer] = sums[layer] + cache["z", layer][:, 1:].sum((0, 1))  # [h, d_head], skip BOS position
        count += tb.shape[0] * (tb.shape[1] - 1)
    return [s / count for s in sums]


def summarize(x):
    x = np.asarray(x, dtype=np.float64)
    rng = np.random.default_rng(0)
    boots = [rng.choice(x, len(x)).mean() for _ in range(1000)]
    return {"mean": float(x.mean()), "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, default=None)
    ap.add_argument("--skip_ablation", action="store_true")
    args = ap.parse_args()
    torch.set_grad_enabled(False)  # TL params require grad; parent helpers do not wrap no_grad
    t0 = time.time()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    tag = f"{args.repo.split('/')[-1]}__{mc.rev_name(args.step)}"
    model = mc.load_tl_model(args.repo, args.step)
    L, H = model.cfg.n_layers, model.cfg.n_heads
    heads_all = [(l, h) for l in range(L) for h in range(H)]

    res = {"repo": args.repo, "step": args.step, "parent_code": f"kayoyin/icl-heads@{mc.PARENT_COMMIT}",
           "protocol": "experiments/E01-induction-baseline-repro.md (frozen 2026-10-01)"}
    # R1 / R1rep / R1b
    r1 = find_induction_heads(model, seed=42)
    r1rep = find_induction_heads(model, seed=43)
    r1b = induction_score_tensor(model, seed=42)
    res["R1"] = r1
    res["R1rep"] = r1rep
    res["R1b"] = {f"{l}.{h}": float(r1b[l, h]) for l, h in heads_all}
    ranked = sorted(r1, key=lambda k: r1[k], reverse=True)
    res["R1_ranked_top9"] = ranked[:9]

    # R2 / R3 clean
    pile_toks, pile_idx = pile_eval_set(model)
    rep = held_out_repeated(model)
    lv_pile = loss_at(model, pile_toks[:, :505], R2_POS)
    lv_rep = loss_at(model, rep, R3_POS)
    r2 = r2_from_loss(lv_pile)
    f, s = r3_from_loss(lv_rep)
    res["R2_clean"] = summarize(r2)
    res["R2_clean_loss50"] = float(lv_pile[:, 0].mean())
    res["R2_clean_loss500"] = float(lv_pile[:, 1].mean())
    res["R3_clean"] = {"first_half_loss": summarize(f), "second_half_loss": summarize(s), "drop": summarize(f - s)}
    per_seq = {"pile_idx": pile_idx, "R2_clean": r2, "R3_first": f, "R3_second": s}

    if not args.skip_ablation:
        mz = mean_z(model, pile_toks)
        cache_pile = parent_random_cache(model, 505)
        # parent's R2 path hits the except-branch of head_ablation_hook (cache length 506 != 505), i.e. every
        # position gets the random run's BOS-position V. Reuse the same cache for R3 so the method is identical.
        cache_rep = cache_pile
        random.seed(0)
        abl = {}
        for k in KS:
            sets = {"induction": [ranked[:k]]}
            sets["random"] = [random.sample([f"{l}.{h}" for l, h in heads_all], k) for _ in range(N_RANDOM_SETS)]
            for kind, lst in sets.items():
                for j, hs in enumerate(lst):
                    heads = [tuple(map(int, x.split("."))) for x in hs]
                    for method in ("parent", "zero", "mean"):
                        if method == "parent":
                            hp = parent_hooks(heads, cache_pile)
                            hr = parent_hooks(heads, cache_rep)
                        else:
                            hp = hr = z_hooks(heads, method, mz)
                        lp = loss_at(model, pile_toks[:, :505], R2_POS, hp)
                        lr = loss_at(model, rep, R3_POS, hr)
                        ff, ss = r3_from_loss(lr)
                        key = f"k{k}|{kind}|{method}|{j}"
                        abl[key] = {"heads": hs, "R2": float(r2_from_loss(lp).mean()),
                                    "R3_drop": float((ff - ss).mean()), "R3_second": float(ss.mean())}
                        if kind == "induction":
                            per_seq[f"R3drop_{k}_{method}"] = ff - ss
                            per_seq[f"R2_{k}_{method}"] = r2_from_loss(lp)
        res["ablation"] = abl
    res["seconds"] = round(time.time() - t0, 1)
    (OUTDIR / f"{tag}.json").write_text(json.dumps(res, indent=1))
    torch.save(per_seq, OUTDIR / f"{tag}.perseq.pt")
    print(f"{tag}: top={ranked[:3]} R1max={r1[ranked[0]]:.3f} R2={res['R2_clean']['mean']:.3f} "
          f"R3drop={res['R3_clean']['drop']['mean']:.3f} ({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
