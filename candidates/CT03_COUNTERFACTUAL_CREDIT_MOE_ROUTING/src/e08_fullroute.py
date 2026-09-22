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
    """Returns U, the 32 draws, the unique routes (base route appended as a
    null control), u_hat and h_r per unique route, and the null route's index."""
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
    null = tuple(S0)          # the base route itself: its true u is exactly 0,
    if null not in uniq:      # so its MEASURED u is this cell's noise floor
        uniq = uniq + [null]
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
    return U, draws, uniq, uhat, hr, uniq.index(null)


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

            # ---- proxy for every token of this layer first (no replay) ----
            t0 = time.time()
            cl = []
            for t in toks:
                chk = n_check > 0
                cl.append((t,) + cell(moe, xs[l][0, t], hs[l][0, t], g[l][t],
                                      K, a.n_gumbel, gen, chk))
                if chk:
                    assert len(cl[-1][3]) >= 8, f"V4 gumbel diversity {len(cl[-1][3])}/32"
            t_prox += time.time() - t0

            # ---- ONE batched replay for all tokens of this layer ----
            # Previously this was one replay_ce call per (token, layer) with 33
            # rows. Every call walks the remaining decoder layers in Python, and
            # Qwen3Moe loops its 128 experts per layer, so the work was pure
            # kernel-launch overhead: 1-2% GPU utilisation. Batching the layer's
            # 8 tokens into one row-batch cuts the layer walks 8x and makes each
            # matmul 8x larger. Rows are independent, so a row patched at t is
            # unaffected by a row patched at t'.
            t0 = time.time()
            start = min(c[0] for c in cl)
            rows = [(c[0], r) for c in cl for r in c[3]]
            pat = torch.stack([c[5][r] - hs[l][0, c[0]] for c in cl for r in c[3]])
            ce_rows = []
            ce_base = None
            for b in range(0, len(rows), a.chunk_rows):
                sl = slice(b, b + a.chunk_rows)
                sub = pat[sl]
                H = lo[l].expand(len(sub) + 1, -1, -1).clone()
                # Row 0 of EVERY chunk is a ZERO patch: the baseline must come
                # through the identical replay path as the rows it is
                # subtracted from, or an fp32 path gap leaks into u.
                for k, (t, _) in enumerate(rows[sl]):
                    H[1 + k, t] += sub[k]
                allce = replay_ce(model, l, H, start, targets, **akw)
                ce_base = allce[0] if ce_base is None else ce_base
                ce_rows.append((allce[1:] - allce[0]).cpu())
                del H, allce
            dL_all = torch.cat(ce_rows)
            t_exact += time.time() - t0

            if n_check > 0:
                ref = float(base_ce[start:].sum())
                got = float(ce_base.sum())
                assert abs(got - ref) < 1e-3 * max(1.0, abs(ref)), \
                    f"V2 replay identity {got:.6f} vs {ref:.6f}"
                n_check -= 1

            k = 0
            for (t, U, draws, uniq, uhat, hr, ni) in cl:
                dL = [float(dL_all[k + n, t - start:].sum()) for n in range(len(uniq))]
                k += len(uniq)
                keep = [n for n in range(len(uniq)) if uniq[n] in set(draws)]
                out.append(dict(pi=a.start + pi, layer=l, pos=t, U=U,
                                n_draw=len(draws),
                                routes=[list(uniq[n]) for n in keep],
                                mult=[sum(d == uniq[n] for d in draws) for n in keep],
                                uhat=[uhat[uniq[n]] for n in keep],
                                u=[-dL[n] for n in keep],
                                changed=[K - len(set(uniq[n]) & set(range(K)))
                                         for n in keep],
                                # V6 noise floor: the base route replayed through
                                # the patch path. Its true utility is 0, so this
                                # is how precisely u is measured in this cell.
                                u_null=-dL[ni]))
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
    ap.add_argument("--chunk-rows", dest="chunk_rows", type=int, default=64)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
