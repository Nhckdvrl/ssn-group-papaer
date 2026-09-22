"""CT03 E08 -- screening curve in EPO's OWN action space.

Frozen design: docs/E08_DESIGN.md.

Per (token, layer): pool U = top-32 experts, n_g = 32 parent-style Gumbel top-K
routes over log p0[U], proxy u_hat from ONE shared backward per problem, exact u
from a full downstream replay of every unique route.

The proxy for all 32 routes costs |U| expert forwards, because

    g^T h_r = (sum_{e in r} p_e * gE_e) / Z_r,   gE_e = g^T E_e(x)

so the per-route work is arithmetic on 32 cached scalars.
"""
import argparse, json, random, sys, time
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, replay_ce

LAYERS = [28, 36, 44]
POOL = 32


def expert_bank(moe, x, U):
    with torch.no_grad():
        return torch.stack([moe.experts[e](x) for e in U])       # |U| x d


def mix(bank, p_u, idx):
    """h_r for a route given as indices INTO U."""
    w = p_u[idx]
    return (bank[idx] * (w / w.sum()).unsqueeze(-1)).sum(0)


def gumbel_routes(p_u, K, n, gen):
    """Parent EPO's sampler. Written with explicit intermediates: the one-liner
    `-torch.log(-torch.log(u).clamp_min(eps))` parses as `-(log(u).clamp_min(eps))`,
    which clamps an all-negative log up to +eps and makes the outer log NaN --
    the E06 bug that produced ONE identical route across 60,864 draws."""
    lg = p_u.clamp_min(1e-30).log().cpu()
    out = []
    for _ in range(n):
        u = torch.rand(len(lg), generator=gen).clamp(1e-20, 1 - 1e-7)
        g = -torch.log(-torch.log(u))
        assert torch.isfinite(g).all()
        out.append(tuple(sorted(torch.topk(lg + g, K).indices.tolist())))
    return out


def cell(moe, x, h, gvec, K, n_g, gen, check):
    """Returns (routes_as_U_indices, u_hat per draw, unique routes, per-unique h_r)."""
    p0 = F.softmax(F.linear(x, moe.gate.weight).float(), -1)
    U = torch.argsort(p0, descending=True)[:POOL].tolist()
    p_u = p0[torch.tensor(U, device=p0.device)]
    bank = expert_bank(moe, x, U)
    gE = (bank.float() @ gvec.float())                            # |U| scalars
    gh0 = float(gvec.float() @ h.float())

    S0 = list(range(K))                       # U is sorted, so base route = first K
    if check:
        h0r = mix(bank, p_u, torch.tensor(S0, device=bank.device))
        rel = float((h0r - h).norm() / h.norm().clamp_min(1e-12))
        assert rel < 1e-4, f"V1 base-route reconstruction rel={rel:.2e}"

    draws = gumbel_routes(p_u, K, n_g, gen)
    uniq = sorted(set(draws))
    uhat, hr = {}, {}
    for r in uniq:
        idx = torch.tensor(r, device=bank.device)
        w = p_u[idx]
        uhat[r] = -(float((w * gE[idx]).sum() / w.sum()) - gh0)   # u_hat = -g^T dh
        hr[r] = mix(bank, p_u, idx)
        if check:
            direct = -float(gvec.float() @ (hr[r] - h).float())
            assert abs(direct - uhat[r]) <= 1e-5 * max(1.0, abs(direct)), \
                f"V3 scalar trick {direct:.6e} vs {uhat[r]:.6e}"
    return U, draws, uniq, uhat, hr


def main(a):
    torch.manual_seed(a.seed); random.seed(a.seed)
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][a.start:a.start + a.n_problems]
    gen = torch.Generator(device="cpu").manual_seed(a.seed + a.start)
    out, n_check = [], a.n_check
    t_prox = t_exact = 0.0

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
            with torch.enable_grad():
                # every parameter is frozen, so the graph only exists if the
                # activations themselves require grad
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                lg = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(lg[0, :-1].float(), targets.to(lg.device),
                                     reduction="none")
                ce[first:].sum().backward()
            base_ce = ce.detach()
            g = {}
            for l in LAYERS:
                gr = cap.mlp_out[l].grad
                assert gr is not None and torch.isfinite(gr).all() and gr.abs().sum() > 0
                g[l] = gr[0].detach().clone()
            xs = {l: cap.mlp_in[l].detach() for l in LAYERS}
            hs = {l: cap.mlp_out[l].detach() for l in LAYERS}
            lo = {l: cap.layer_out[l].detach() for l in LAYERS}
            akw = cap.attn_kwargs
        del lg, ce, emb
        torch.cuda.empty_cache()

        order = torch.argsort(base_ce[first:])
        q = max(1, len(order) // 4)
        rng = random.Random(a.seed * 7919 + a.start + pi)
        toks = [first + int(i) for i in rng.sample(order[-q:].tolist(),
                                                   min(a.n_tok, q))]

        for l in LAYERS:
            moe = model.model.layers[l].mlp
            for t in toks:
                chk = n_check > 0
                t0 = time.time()
                U, draws, uniq, uhat, hr = cell(moe, xs[l][0, t], hs[l][0, t],
                                                g[l][t], K, a.n_gumbel, gen, chk)
                t_prox += time.time() - t0

                t0 = time.time()
                pat = torch.stack([hr[r] - hs[l][0, t] for r in uniq])
                H = lo[l].expand(len(uniq) + 1, -1, -1).clone()
                H[1:, t] += pat
                allce = replay_ce(model, l, H, t, targets, **akw)
                # Row 0 is a ZERO patch: the baseline must come through the
                # identical replay path, or an fp32 path gap leaks into u.
                dL = (allce[1:] - allce[0]).sum(dim=1)
                t_exact += time.time() - t0
                if chk:
                    # replay_ce scores positions t..T-2 (H[:, start:-1] against
                    # targets[start:]), so the reference must start at t, not at
                    # `first` -- the two ranges are different lengths.
                    ref = float(base_ce[t:].sum())
                    got = float(allce[0].sum())
                    assert abs(got - ref) < 1e-3 * max(1.0, abs(ref)), \
                        f"V2 replay identity {got:.6f} vs {ref:.6f}"
                    assert len(uniq) >= 8, f"V4 gumbel diversity {len(uniq)}/32"
                    n_check -= 1

                out.append(dict(pi=a.start + pi, layer=l, pos=t, U=U,
                                n_draw=len(draws), routes=[list(r) for r in uniq],
                                mult=[sum(d == r for d in draws) for r in uniq],
                                uhat=[uhat[r] for r in uniq],
                                u=[-float(v) for v in dL],
                                changed=[K - len(set(r) & set(range(K))) for r in uniq]))
        del g, xs, hs, lo
        torch.cuda.empty_cache()
        print(f"[{pi+1}/{len(pool)}] shard@{a.start} cells {len(out)} "
              f"proxy {t_prox:.1f}s exact {t_exact:.1f}s", flush=True)

    torch.save(dict(cells=out, layers=LAYERS, K=K, pool=POOL,
                    n_gumbel=a.n_gumbel, t_proxy=t_prox, t_exact=t_exact), a.out)
    print(f"wrote {a.out}: {len(out)} cells")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e08_cache.pt")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=40)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=8)
    ap.add_argument("--n-gumbel", dest="n_gumbel", type=int, default=32)
    ap.add_argument("--n-check", dest="n_check", type=int, default=12)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
