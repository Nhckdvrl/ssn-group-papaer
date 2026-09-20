"""CT03 FG0 diagnostic -- does a single route intervention have DECISION impact?

The smoke run showed the hook propagates (gold logprob moved 1.3 nat) while the
greedy continuation never changed. That can mean two very different things, and
adding sampling seeds before telling them apart would just buy variance on an
intervention that may have no treatment strength:

  (a) there IS a distribution-level effect and greedy is simply too hard a
      measuring instrument  -> paired sampling is the right fix;
  (b) there is essentially NO distribution-level effect at the tokens that
      max_t H_proxy selects -> the selector is not finding generation-
      consequential decisions, and seeds would be wasted.

So this measures the effect at the decision level, and how long it survives.

Persistence: generate a 32-token continuation C from the BASE cache, then
teacher-force that SAME C through each arm's intervention-specific cache and
compare the next-token distributions step by step. A perturbation that vanishes
after one step is a different object from one that rides the KV cache forward.

No training, no sampling, high AND low tokens.
"""

import argparse, json, sys, time
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, route_of, swap_dh, replay_ce
from fg0_branch import patch_hook

STEPS = [1, 2, 4, 8, 16, 32]


def dists(lp_base, lp_arm):
    p, q = lp_base.exp(), lp_arm.exp()
    return (float((p * (lp_base - lp_arm)).sum()), float(0.5 * (p - q).abs().sum()))


@torch.no_grad()
def probe(model, ids, t, patches, layer, gold_id, n_cont):
    from transformers import DynamicCache
    B = patches.shape[0]
    dev = next(model.parameters()).device
    pre = torch.tensor([ids[:t + 1]] * B, device=dev)

    cache = DynamicCache(config=model.config)
    hd = patch_hook(model.model.layers[layer].mlp, t, patches)
    out = model(pre, use_cache=True, past_key_values=cache)
    hd.remove()
    lp0 = F.log_softmax(out.logits[:, -1].float(), -1)

    # base's own greedy continuation, used as the shared teacher-forced path
    cont, nxt = [], lp0[0].argmax().view(1, 1)
    cache_b = DynamicCache(config=model.config)
    model(pre[:1], use_cache=True, past_key_values=cache_b)
    for _ in range(n_cont):
        cont.append(int(nxt))
        o = model(nxt, use_cache=True, past_key_values=cache_b)
        nxt = o.logits[:, -1].argmax(-1, keepdim=True)
    C = torch.tensor([cont] * B, device=dev)
    lps = F.log_softmax(model(C, use_cache=True, past_key_values=cache).logits.float(), -1)

    top2 = lp0[0].topk(2).values
    rec = dict(base_entropy=float(-(lp0[0].exp() * lp0[0]).sum()),
               base_top1_top2_prob_margin=float(top2[0].exp() - top2[1].exp()),
               gold_p_base=float(lp0[0, gold_id].exp()),
               arms=[])
    for b in range(B):
        kl0, tv0 = dists(lp0[0], lp0[b])
        pers = []
        for s in STEPS:
            if s - 1 < lps.shape[1]:
                k, v = dists(lps[0, s - 1], lps[b, s - 1])
                pers.append(dict(step=s, kl=k, tv=v,
                                 flip=int(lps[b, s - 1].argmax() != lps[0, s - 1].argmax())))
        rec["arms"].append(dict(
            next_kl=kl0, next_tv=tv0,
            next_top1_flipped=int(lp0[b].argmax() != lp0[0].argmax()),
            gold_p=float(lp0[b, gold_id].exp()),
            d_logp_gold=float(lp0[b, gold_id] - lp0[0, gold_id]),
            persistence=pers))
    return rec


def main(a):
    tok, model = load(a)
    K, L = model.config.num_experts_per_tok, a.layer
    pool = json.load(open(a.pool))["items"][:a.n_problems]
    dev0 = next(model.parameters()).device
    fout = open(a.out, "w"); t0 = time.time()

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
        cut = first + int(0.7 * len(s_ids))

        with Capture(model, [L]) as cap:
            with torch.enable_grad():
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                lg = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(lg[0, :-1].float(),
                                     targets.to(lg.device), reduction="none")
                ce[first:].sum().backward()
            base_ce = ce.detach().clone()
            g = cap.mlp_out[L].grad[0].detach().clone()
            xs, hs = cap.mlp_in[L].detach(), cap.mlp_out[L].detach()
            lo, akw = cap.layer_out[L].detach(), cap.attn_kwargs
        del lg, ce, emb, cap
        torch.cuda.empty_cache()

        moe = model.model.layers[L].mlp
        H = {}
        for t in range(first + 4, cut):
            x, h = xs[0, t], hs[0, t]
            p, rank, sel, Z = route_of(moe, x, K)
            cl = rank[K:K + a.m].tolist()
            gv = g[t].float()
            with torch.no_grad():
                ge = {e: float(gv @ moe.experts[e](x).float()) for e in sel + cl}
                gh = float(gv @ h.float())
            best = min(((Z / (Z - float(p[i]) + float(p[j])) - 1.0) * gh
                        + (float(p[j]) * ge[j] - float(p[i]) * ge[i])
                        / (Z - float(p[i]) + float(p[j])))
                       for i in sel for j in cl)
            H[t] = -best
        if len(H) < 8:
            continue
        order = sorted(H, key=lambda t: -H[t])
        t_hi = order[0]
        rel = (t_hi - first) / len(s_ids)
        t_lo = min(order[len(order) // 2:],
                   key=lambda t: abs((t - first) / len(s_ids) - rel)
                   + abs(float(base_ce[t] - base_ce[t_hi])))

        for tag, t in (("high", t_hi), ("low", t_lo)):
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
            kp = int(np.argmin(px))
            Hp = lo.expand(len(pairs) + 1, -1, -1).clone(); Hp[1:, t] += dhs
            dL = (replay_ce(model, L, Hp, t, targets, **akw)[1:]
                  - replay_ce(model, L, Hp[:1], t, targets, **akw)[0]).sum(1).cpu().numpy()
            ke = int(dL.argmin())
            patches = torch.stack([torch.zeros_like(dhs[0]), dhs[kp], dhs[ke]])
            rec = probe(model, ids, t, patches, L, ids[t + 1], a.n_cont)
            rec.update(pi=pi, token=tag, pos=t, H_proxy=H[t], H_exact=float(-dL.min()),
                       dh_norm=[float(dhs[kp].norm()), float(dhs[ke].norm())],
                       proxy_is_exact=bool(kp == ke), base_ce=float(base_ce[t]),
                       arm_names=["base", "proxy_best", "exact_best"])
            fout.write(json.dumps(rec) + "\n"); fout.flush()
        del g, xs, hs, lo
        torch.cuda.empty_cache()
        print(f"[{pi+1}/{len(pool)}] hi={t_hi} lo={t_lo} {time.time()-t0:.0f}s", flush=True)
    fout.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/fg0_devpool.json")
    ap.add_argument("--out", default="results/fg0_diag.jsonl")
    ap.add_argument("--layer", type=int, default=44)
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=6)
    ap.add_argument("--n-cont", dest="n_cont", type=int, default=33)
    ap.add_argument("--max-len", dest="max_len", type=int, default=768)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
