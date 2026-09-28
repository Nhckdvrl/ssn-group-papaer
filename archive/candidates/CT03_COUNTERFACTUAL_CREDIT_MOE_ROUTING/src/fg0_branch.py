"""CT03 FG0.1 -- gold-prefix causal branch test.

Frozen design: docs/FG0_DESIGN.md. Nothing is trained.

    fix gold prefix y_<=t , do( route at (L, t) = r ) , free-generate the rest

Three implementation invariants that the result depends on:

1. The KV CACHE MUST CARRY THE INTERVENTION. Patching layer L at position t
   changes every later layer's hidden state at t, hence the K/V those layers
   write for t. Each arm therefore runs its OWN prefix forward with the hook
   and generates from its OWN cache. Patching logits and then reusing a base
   cache would discard most of the causal effect.
2. High/low token selection uses PROXY headroom only -- exact headroom is not
   available at deployment time, so selecting on it would leak. H_exact is
   recorded for analysis, never for selection.
3. PROXY-BEST and EXACT-BEST search the SAME equal-compute one-swap action
   space S' = S - {i} + {j}. Giving the oracle a larger candidate universe
   would contaminate the oracle gap with a search-space advantage.
"""

import argparse, json, sys, time
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, route_of, swap_dh, replay_ce
from fg0_pool import boxed, norm


def patch_hook(layer_mlp, pos, patches):
    """Adds row-wise patches at `pos` on the MoE output; fires on prefix only."""
    def hook(mod, inp, out):
        h, rl = out
        h = h.clone()
        h[:, pos] = h[:, pos] + patches.to(h.dtype)
        return (h, rl)
    return layer_mlp.register_forward_hook(hook)


@torch.no_grad()
def branch_generate(model, tok, ids, t, patches, layer, max_new, gold_tail):
    """Prefix forward with per-row patch at (layer, t), then greedy free-gen."""
    from transformers import DynamicCache
    B = patches.shape[0]
    dev = next(model.parameters()).device
    pre = torch.tensor([ids[:t + 1]] * B, device=dev)
    cache = DynamicCache(config=model.config)
    hd = patch_hook(model.model.layers[layer].mlp, t, patches)
    out = model(pre, use_cache=True, past_key_values=cache)
    hd.remove()

    # short-horizon gold logprob, as a diagnostic only
    lp = F.log_softmax(out.logits[:, -1].float(), -1)
    gl = lp[:, gold_tail[0]].tolist() if gold_tail else []
    kl = (lp[0].exp() * (lp[0] - lp)).sum(-1).tolist()      # KL(base || arm)
    top1 = lp.argmax(-1).tolist()
    flip = [int(c != top1[0]) for c in top1]
    ent = float(-(lp[0].exp() * lp[0]).sum())

    nxt = out.logits[:, -1].argmax(-1, keepdim=True)
    gen = [nxt]
    done = torch.zeros(B, dtype=torch.bool, device=dev)
    eos = model.config.eos_token_id
    eos = eos if isinstance(eos, (list, tuple)) else [eos]
    for _ in range(max_new - 1):
        o = model(nxt, use_cache=True, past_key_values=cache)
        nxt = o.logits[:, -1].argmax(-1, keepdim=True)
        for e in eos:
            done |= nxt.squeeze(1) == e
        gen.append(nxt)
        if bool(done.all()):
            break
    seqs = torch.cat(gen, 1).tolist()
    texts = [tok.decode(s, skip_special_tokens=True) for s in seqs]
    return texts, gl, kl, flip, ent


def main(a):
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    L = a.layer
    pool = json.load(open(a.pool))["items"][:a.n_problems]
    dev0 = next(model.parameters()).device
    fout = open(a.out, "w")
    t_start = time.time()

    for pi, ex in enumerate(pool):
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        if len(ids) > a.max_len or len(s_ids) < 24:
            continue
        input_ids = torch.tensor([ids], device=dev0)
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1
        cut = first + int(0.7 * len(s_ids))          # stay out of the answer

        with Capture(model, [L]) as cap:
            with torch.enable_grad():
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                lg = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(lg[0, :-1].float(),
                                     targets.to(lg.device), reduction="none")
                ce[first:].sum().backward()
            base_ce = ce.detach().clone()
            g = cap.mlp_out[L].grad[0].detach().clone()
            xs = cap.mlp_in[L].detach()
            hs = cap.mlp_out[L].detach()
            lo = cap.layer_out[L].detach()
            akw = cap.attn_kwargs
        del lg, ce, emb, cap
        torch.cuda.empty_cache()

        # ---- proxy headroom at every eligible position (selection uses PROXY only)
        cands = {}
        scan = list(range(first + 4, cut))
        if len(scan) > a.max_scan:              # even stride, keeps coverage
            scan = scan[:: max(1, len(scan) // a.max_scan)][:a.max_scan]
        for t in scan:
            x, h = xs[0, t], hs[0, t]
            p, rank, sel, Z = route_of(model.model.layers[L].mlp, x, K)
            cl = rank[K:K + a.m].tolist()
            gv = g[t].float()
            moe = model.model.layers[L].mlp
            with torch.no_grad():
                # g^T dh_ij = (Z/Z'-1)(g^T h) + (p_j g^T E_j - p_i g^T E_i)/Z'
                # so the whole K x m grid needs |S u C| expert forwards, not 2 per pair
                ge = {e: float(gv @ moe.experts[e](x).float()) for e in sel + cl}
                gh = float(gv @ h.float())
                px, prs = [], []
                for i in sel:
                    for j in cl:
                        Zp = Z - float(p[i]) + float(p[j])
                        px.append((Z / Zp - 1.0) * gh
                                  + (float(p[j]) * ge[j] - float(p[i]) * ge[i]) / Zp)
                        prs.append((i, j))
            k = int(np.argmin(px))                 # px = g.dh ; most negative = best
            cands[t] = dict(H_proxy=-float(px[k]), best=prs[k], sel=sel, cl=cl)
        if len(cands) < 8:
            continue

        hs_sorted = sorted(cands, key=lambda t: -cands[t]["H_proxy"])
        t_high = hs_sorted[0]
        rel_hi = (t_high - first) / max(len(s_ids), 1)
        lowpool = hs_sorted[len(hs_sorted) // 2:]           # bottom half by headroom
        t_low = min(lowpool, key=lambda t: (abs((t - first) / len(s_ids) - rel_hi)
                                            + abs(float(base_ce[t] - base_ce[t_high]))))

        for tag_t, t in (("high", t_high), ("low", t_low)):
            moe = model.model.layers[L].mlp
            x, h = xs[0, t], hs[0, t]
            p, rank, sel, Z = route_of(moe, x, K)
            cl = rank[K:K + a.m].tolist()
            pairs, dhs = [], []
            for i in sel:
                for j in cl:
                    d, _ = swap_dh(moe, x, h, p, i, j, Z)
                    pairs.append((i, j)); dhs.append(d)
            dhs = torch.stack(dhs)
            px = (dhs.float() @ g[t].float()).tolist()
            k_proxy = int(np.argmin(px))

            # exact utilities over the SAME action space
            H = lo.expand(len(pairs) + 1, -1, -1).clone()
            H[1:, t] += dhs
            allce = replay_ce(model, L, H, t, targets, **akw)
            dL = (allce[1:] - allce[0]).sum(dim=1).cpu().numpy()
            k_exact = int(dL.argmin())

            arms = ["base", "proxy_best", "exact_best"]
            patches = torch.stack([torch.zeros_like(dhs[0]), dhs[k_proxy], dhs[k_exact]])
            gold_tail = ids[t + 1:t + 2]
            texts, glp, kls, flips, ent0 = branch_generate(
                model, tok, ids, t, patches, L, a.max_new, gold_tail)
            gold = norm(ex["answer"])
            for ai, arm in enumerate(arms):
                pred = boxed(texts[ai])
                fout.write(json.dumps(dict(
                    pi=pi, token=tag_t, pos=t, rel_pos=(t - first) / len(s_ids),
                    arm=arm, level=ex.get("level"), cfg=ex.get("cfg"),
                    H_proxy=cands[t]["H_proxy"], H_exact=float(-dL.min()),
                    swap=list(pairs[k_proxy]) if arm == "proxy_best"
                         else (list(pairs[k_exact]) if arm == "exact_best" else None),
                    proxy_is_exact=bool(k_proxy == k_exact),
                    base_ce=float(base_ce[t]),
                    gold_logprob=glp[ai] if glp else None,
                    next_kl_vs_base=kls[ai], next_top1_flipped=flips[ai],
                    base_next_entropy=ent0,
                    correct=bool(pred is not None and norm(pred) == gold),
                    pred=pred, n_chars=len(texts[ai]),
                    same_as_base=bool(texts[ai] == texts[0]),
                )) + "\n")
            fout.flush()
        del g, xs, hs, lo
        torch.cuda.empty_cache()
        print(f"[{pi+1}/{len(pool)}] t_high={t_high} t_low={t_low} "
              f"{time.time()-t_start:.0f}s", flush=True)
    fout.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/fg0_devpool.json")
    ap.add_argument("--out", default="results/fg0_branch.jsonl")
    ap.add_argument("--layer", type=int, default=44)
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=120)
    ap.add_argument("--max-len", dest="max_len", type=int, default=768)
    ap.add_argument("--max-new", dest="max_new", type=int, default=320)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--max-scan", dest="max_scan", type=int, default=72)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
