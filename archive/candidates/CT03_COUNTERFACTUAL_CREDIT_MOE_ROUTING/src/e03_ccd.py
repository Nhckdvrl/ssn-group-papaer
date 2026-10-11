"""CT03 Stage C0 -- Counterfactual Credit Distillation on Qwen3-30B-A3B routers.

Frozen design: docs/E03_C0_DESIGN.md. Trains ONLY the gate matrices at L28/36/44.

The renormalised swap makes every one-swap at a token a scalar computation:

    g^T dh_ij = (Z/Z' - 1)(g^T h) + ( p_j (g^T E_j) - p_i (g^T E_i) ) / Z'

so 8 selected x 4 boundary = 32 candidate swaps need 12 expert forwards, not 32.
"""

import argparse, json, os, random, time
import torch
import torch.nn.functional as F
from datasets import load_dataset

from e02_qwen import MODEL, Capture, load, route_of

TRAIN_LAYERS = [28, 36, 44]


def pick_problems(ds, tok, seed, max_len, min_sol, n_holdout, n_train):
    idxs = list(range(len(ds)))
    random.Random(seed).shuffle(idxs)
    keep = []
    for qi in idxs:
        ex = ds[qi]
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)
        p = tok(prompt, add_special_tokens=False).input_ids
        s = tok(ex["solution"], add_special_tokens=False).input_ids
        if len(p) + len(s) <= max_len and len(s) >= min_sol:
            keep.append((qi, p, s))
        if len(keep) >= n_holdout + n_train:
            break
    return keep[:n_holdout], keep[n_holdout:]


def credit_terms(moe, x, h, g, K, m, gen):
    """All one-swap proxy credits at one (token, layer), as scalars.

    Returns (pairs, px, p, sel, cand) where pairs is a list of (i, j)."""
    p, rank, sel, Z = route_of(moe, x, K)
    cand = rank[K:K + m].tolist()
    involved = sel + cand
    with torch.no_grad():
        ge = {e: float(g @ moe.experts[e](x)) for e in involved}
    gh = float(g @ h)
    pairs, px = [], []
    for i in sel:
        for j in cand:
            Zp = Z - float(p[i]) + float(p[j])
            v = (Z / Zp - 1.0) * gh + (float(p[j]) * ge[j] - float(p[i]) * ge[i]) / Zp
            pairs.append((i, j)); px.append(v)
    return pairs, px, p, sel, cand


def main(a):
    torch.manual_seed(a.seed); random.seed(a.seed)
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    holdout, train = pick_problems(ds, tok, a.seed, a.max_len, a.min_sol,
                                   a.n_holdout, a.n_train)
    json.dump([q for q, _, _ in holdout], open(a.holdout_out, "w"))
    print(f"held-out {len(holdout)} problems (frozen), train pool {len(train)}", flush=True)

    gates = [model.model.layers[l].mlp.gate for l in TRAIN_LAYERS]
    base_w = [gt.weight.detach().clone() for gt in gates]
    for gt in gates:
        gt.weight.requires_grad_(True)
    opt = torch.optim.AdamW([gt.weight for gt in gates], lr=a.lr, weight_decay=0.0)

    dev0 = next(model.parameters()).device
    log = open(a.log_out, "w")
    step = 0
    t_start = time.time()

    for qi, p_ids, s_ids in train:
        if step >= a.steps:
            break
        ids = p_ids + s_ids
        input_ids = torch.tensor([ids], device=dev0)
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1

        # ---- shared backward: one per trajectory, gives g at every layer ----
        with Capture(model, TRAIN_LAYERS) as cap:
            with torch.enable_grad():
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                logits = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(logits[0, :-1].float(),
                                     targets.to(logits.device), reduction="none")
                ce[first:].sum().backward()
        base_ce = ce.detach()
        g_all = {l: cap.mlp_out[l].grad[0].detach().clone() for l in TRAIN_LAYERS}
        x_all = {l: cap.mlp_in[l].detach() for l in TRAIN_LAYERS}
        h_all = {l: cap.mlp_out[l].detach() for l in TRAIN_LAYERS}
        del logits, ce, emb, cap
        torch.cuda.empty_cache()

        # ---- hard tokens: top-quartile teacher-forced CE, as in E01/E02 ----
        scored = base_ce[first:]
        order = torch.argsort(scored)
        q = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + qi)
        toks = [first + int(i) for i in rng.sample(order[-q:].tolist(),
                                                   min(a.n_tok, q))]

        # ---- credit (no grad) then the pairwise loss (grad -> gate only) ----
        terms = []
        for li, l in enumerate(TRAIN_LAYERS):
            moe = model.model.layers[l].mlp
            for t in toks:
                with torch.no_grad():
                    pr, px, _, _, _ = credit_terms(moe, x_all[l][0, t], h_all[l][0, t],
                                                   g_all[l][t], K, a.m, rng)
                terms.append((li, l, t, pr, px))

        opt.zero_grad(set_to_none=True)
        tot, tot_anc, npair, nflip = 0.0, 0.0, 0, 0
        loss_sum = None
        for li, l, t, pr, px in terms:
            gt = gates[li]
            x = x_all[l][0, t]
            s = gt(x).float()                      # grad flows here, and only here
            s0 = F.linear(x, base_w[li]).float()
            pxv = torch.tensor(px, device=s.device)
            y = -torch.sign(pxv)
            if a.shuffle_labels:
                # CONTROL: destroy the credit CONTENT while keeping the pipeline,
                # the tokens, the candidates and the label marginal identical.
                # If CE still improves, the gain is router perturbation plus
                # in-domain data, not counterfactual credit.
                y = y[torch.randperm(y.shape[0], device=y.device)]
            keep = y != 0
            if keep.sum() == 0:
                continue
            ii = torch.tensor([i for i, _ in pr], device=s.device)[keep]
            jj = torch.tensor([j for _, j in pr], device=s.device)[keep]
            d = s[jj] - s[ii]
            lcf = F.softplus(-y[keep] * d).mean()
            anc = torch.zeros((), device=s.device)
            if a.anchor > 0:
                anc = a.anchor * F.kl_div(F.log_softmax(s, -1), F.log_softmax(s0, -1),
                                          log_target=True, reduction="sum")
            loss_sum = (lcf + anc) if loss_sum is None else loss_sum + lcf + anc
            tot += float(lcf.detach()); tot_anc += float(anc.detach())
            npair += int(keep.sum()); nflip += int((y[keep] > 0).sum())
        if loss_sum is None:
            continue
        (loss_sum / max(len(terms), 1)).backward()
        gn = torch.nn.utils.clip_grad_norm_([gt.weight for gt in gates], a.clip)
        opt.step()
        step += 1

        drift_now = [float((gt.weight.detach() - bw).norm() / bw.norm())
                     for gt, bw in zip(gates, base_w)]
        rec = dict(step=step, q=qi, loss=tot / max(len(terms), 1),
                   anchor_term=tot_anc / max(len(terms), 1), n_pairs=npair,
                   frac_beneficial=nflip / max(npair, 1), grad_norm=float(gn),
                   drift=drift_now, n_tok=len(toks), elapsed=time.time() - t_start)
        log.write(json.dumps(rec) + "\n"); log.flush()
        if step % a.print_every == 0 or step <= 3:
            print(f"[{step}/{a.steps}] loss={rec['loss']:.4f} "
                  f"anc={rec['anchor_term']:.4f} benef={rec['frac_beneficial']:.3f} "
                  f"gn={float(gn):.3f} drift={[round(d,4) for d in drift_now]} "
                  f"{rec['elapsed']:.0f}s", flush=True)
        del g_all, x_all, h_all
        torch.cuda.empty_cache()

    os.makedirs(os.path.dirname(a.ckpt_out) or ".", exist_ok=True)
    torch.save({str(l): gt.weight.detach().cpu()
                for l, gt in zip(TRAIN_LAYERS, gates)}, a.ckpt_out)
    drift = {str(l): float((gt.weight.detach() - bw).norm() / bw.norm())
             for l, gt, bw in zip(TRAIN_LAYERS, gates, base_w)}
    print("relative weight drift:", json.dumps(drift))
    json.dump(dict(steps=step, drift=drift, arm=a.arm, lr=a.lr, anchor=a.anchor),
              open(a.ckpt_out + ".meta.json", "w"), indent=1)
    log.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="cf_only", choices=["cf_only", "cf_anchor"])
    ap.add_argument("--anchor", type=float, default=0.0)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--clip", type=float, default=1.0)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=8)
    ap.add_argument("--n-holdout", dest="n_holdout", type=int, default=16)
    ap.add_argument("--n-train", dest="n_train", type=int, default=420)
    ap.add_argument("--max-len", dest="max_len", type=int, default=512)
    ap.add_argument("--min-sol", dest="min_sol", type=int, default=64)
    ap.add_argument("--ckpt-out", dest="ckpt_out", default="results/c0_router_cf.pt")
    ap.add_argument("--log-out", dest="log_out", default="results/c0_train_cf.jsonl")
    ap.add_argument("--holdout-out", dest="holdout_out", default="results/c0_holdout.json")
    ap.add_argument("--print-every", dest="print_every", type=int, default=10)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--shuffle-labels", dest="shuffle_labels", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
