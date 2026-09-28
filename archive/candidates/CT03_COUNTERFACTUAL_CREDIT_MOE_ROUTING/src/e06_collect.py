"""CT03 E06 -- collect cached router inputs + EXACT route utilities for two
action spaces, so the offline EPO gate and the action-space audit share tokens.

Per (token, layer) at L36/L44:
  * x_t, the MoE block input -- the router's only input, so a router can be
    trained offline from it without touching the 30B backbone again;
  * exact dCE for all K x m ONE-SWAP routes  S' = S - {i} + {j};
  * exact dCE for n_g parent-style GUMBEL top-k routes sampled from the router
    over the same top-(K+m) pool, which may change several experts at once.

The second set exists because the screening curve was measured on the one-swap
space while EPO samples full routes. Without it "we cut EPO's reruns by 8x"
would be a claim about a narrower action space than EPO actually uses.
"""
import argparse, json, random, sys
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, route_of, replay_ce

LAYERS = [36, 44]


def expert_bank(moe, x, U):
    """E_e(x) for every expert in U, computed ONCE.

    E_e(x) depends only on (x, e), never on the route, and U holds just 12
    experts. Calling moe.experts[e](x) inside the per-route loop instead meant
    64 routes x 8 experts = 512 tiny single-token matmuls per (token, layer) --
    almost pure Python and kernel-launch overhead, which showed up as 1-2% GPU
    utilisation. Caching the bank turns every route into arithmetic on 12
    vectors."""
    with torch.no_grad():
        return {e: moe.experts[e](x) for e in U}


def mix_cached(bank, ids, p):
    Z = float(p[ids].sum())
    out = None
    for e in ids:
        v = bank[e] * (float(p[e]) / Z)
        out = v if out is None else out + v
    return out


def main(a):
    torch.manual_seed(a.seed); random.seed(a.seed)
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][a.start:a.start + a.n_problems]
    gen = torch.Generator(device="cpu").manual_seed(a.seed)

    meta, X = [], []
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
        with Capture(model, LAYERS) as cap:
            with torch.no_grad():
                lg = model(input_ids).logits
                ce = F.cross_entropy(lg[0, :-1].float(), targets.to(lg.device),
                                     reduction="none")
            xs = {l: cap.mlp_in[l].detach() for l in LAYERS}
            hs = {l: cap.mlp_out[l].detach() for l in LAYERS}
            lo = {l: cap.layer_out[l].detach() for l in LAYERS}
            akw = cap.attn_kwargs
        order = torch.argsort(ce[first:])
        q = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + pi)
        toks = [first + int(i) for i in rng.sample(order[-q:].tolist(),
                                                   min(a.n_tok, q))]

        for l in LAYERS:
            moe = model.model.layers[l].mlp
            for t in toks:
                x, h = xs[l][0, t], hs[l][0, t]
                p0 = F.softmax(F.linear(x, moe.gate.weight).float(), -1)
                rank = torch.argsort(p0, descending=True)
                S0, C0 = rank[:K].tolist(), rank[K:K + a.m].tolist()
                U = S0 + C0

                routes, kinds = [], []
                for i in S0:                                  # one-swap space
                    for j in C0:
                        routes.append([e for e in S0 if e != i] + [j])
                        kinds.append(("swap", i, j))
                logits_U = torch.log(p0[U].clamp_min(1e-30)).cpu()
                for _ in range(a.n_gumbel):                   # parent-style routes
                    # Written with explicit intermediates: the one-liner form
                    # `-torch.log(-torch.log(u).clamp_min(eps))` parses as
                    # `-(torch.log(u).clamp_min(eps))`, which clamps an all-
                    # negative log up to +eps and makes the outer log NaN. That
                    # bug produced ONE identical route across all 60,864 draws.
                    u = torch.rand(len(U), generator=gen).clamp(1e-20, 1 - 1e-7)
                    g = -torch.log(-torch.log(u))
                    assert torch.isfinite(g).all()
                    sel = torch.topk(logits_U + g, K).indices.tolist()
                    routes.append([U[s] for s in sel]); kinds.append(("gumbel", -1, -1))

                bank = expert_bank(moe, x, U)
                pat = [mix_cached(bank, r, p0) - h for r in routes]
                H = lo[l].expand(len(pat) + 1, -1, -1).clone()
                H[1:, t] += torch.stack(pat)
                allce = replay_ce(model, l, H, t, targets, **akw)
                dL = (allce[1:] - allce[0]).sum(dim=1).cpu().numpy()

                X.append(x.detach().float().cpu())
                meta.append(dict(pi=a.start + pi, layer=l, pos=t, S0=S0, C0=C0,
                                 routes=[list(map(int, r)) for r in routes],
                                 kinds=[list(k) for k in kinds],
                                 dL=[float(v) for v in dL],
                                 base_ce=float(ce[t])))
        del xs, hs, lo
        torch.cuda.empty_cache()
        print(f"[{pi+1}/{len(pool)}] shard@{a.start} tokens {len(meta)}", flush=True)

    torch.save({"x": torch.stack(X), "meta": meta,
                "layers": LAYERS, "K": K, "m": a.m, "n_gumbel": a.n_gumbel},
               a.out)
    print(f"wrote {a.out}: {len(meta)} token-layer cells")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e06_cache.pt")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=60)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=8)
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--n-gumbel", dest="n_gumbel", type=int, default=32)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
