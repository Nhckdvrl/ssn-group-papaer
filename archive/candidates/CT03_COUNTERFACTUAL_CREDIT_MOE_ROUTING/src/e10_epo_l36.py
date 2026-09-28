"""CT03 E10 stage 2 -- dynamic Exact-EPO at L36.

Frozen design: docs/E10_DESIGN.md. No proxy in this file; E10 is the oracle arm.

The objective is bit-identical to E09's -- only the layer changes -- so that a
difference at L36 is a difference in the layer and not in the code. What does
change is the cost: at L36 the patch propagates through layers 37-47, so every
candidate route needs a real suffix replay.
"""
import argparse, json, sys
import builtins
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import load, replay_ce

L = 36
print = lambda *x, **k: builtins.print(*x, **{**k, 'flush': True})


def kwargs_for(p, dev):
    T = p["cos"].shape[0]
    m = p["mask"]
    return dict(position_embeddings=(p["cos"][None].to(dev), p["sin"][None].to(dev)),
                attention_mask=None if m is None else m.to(dev),
                position_ids=None,
                cache_position=torch.arange(T, device=dev))


def mix(bank, p, idx):
    """bank (n,E,d), p (n,E), idx (n,R,K) -> (n,R,d)."""
    w = torch.gather(p.unsqueeze(1).expand(-1, idx.shape[1], -1), 2, idx)
    w = w / w.sum(-1, keepdim=True)
    e = torch.gather(bank.unsqueeze(1).expand(-1, idx.shape[1], -1, -1), 2,
                     idx.unsqueeze(-1).expand(-1, -1, -1, bank.shape[-1]))
    return (e * w.unsqueeze(-1)).sum(2)


def gumbel(logp, K, R, gen):
    u = torch.rand(logp.shape[0], R, logp.shape[1], generator=gen,
                   device=logp.device).clamp(1e-20, 1 - 1e-7)
    g = -torch.log(-torch.log(u))          # explicit intermediates; see e06
    assert torch.isfinite(g).all()
    return torch.topk(logp.unsqueeze(1) + g, K, dim=-1).indices


def sample_routes(x, W, K, P, R, gen):
    with torch.no_grad():
        p = F.softmax(x @ W.T, -1)
        pool = torch.topk(p, P, dim=-1).indices
        logp = torch.log(torch.gather(p, 1, pool).clamp_min(1e-30))
        loc = gumbel(logp, K, R, gen)
        return p, torch.gather(pool.unsqueeze(1).expand(-1, R, -1), 2, loc)


def logpi(s, idx):
    lp = F.log_softmax(s, -1)
    return torch.gather(lp.unsqueeze(1).expand(-1, idx.shape[1], -1), 2, idx).sum(-1)


def replay(model, p, ids_or_h, dev, chunk_rows, check=None):
    """Exact suffix CE for routes given as h_r (n,R,d). Returns u (n,R):
    u = CE(base) - CE(route), positive = better."""
    lo = p["lo"].to(dev)
    toks, start = p["toks"], p["toks"][0]
    tgt = p["targets"].to(dev)
    n, R, d = ids_or_h.shape
    rows = [(t, r) for k, t in enumerate(toks) for r in range(R)]
    pat = torch.cat([ids_or_h[k] - p["h"][k].to(dev) for k in range(n)])
    outs = []
    base = None
    for b in range(0, len(rows), chunk_rows):
        sub = pat[b:b + chunk_rows]
        H = lo[None].expand(len(sub) + 1, -1, -1).clone()
        # row 0 of every chunk is a zero patch, so the baseline shares the
        # chunk's numeric path (E01)
        for k, (t, _) in enumerate(rows[b:b + chunk_rows]):
            H[1 + k, t] += sub[k]
        ce = replay_ce(model, L, H, start, tgt, **kwargs_for(p, dev))
        if base is None:
            base = ce[0]
            if check is not None:
                ref = float(p["base_ce"].sum())
                assert abs(float(base.sum()) - ref) < 1e-3 * max(1.0, abs(ref)), \
                    f"V1 cached replay {float(base.sum()):.5f} vs {ref:.5f}"
        outs.append(ce[1:] - base)
        del H, ce
    dL = torch.cat(outs)
    u = torch.stack([torch.stack([-dL[k * R + r, toks[k] - start:].sum()
                                  for r in range(R)]) for k in range(n)])
    return u


def route_value(model, probs, W, W0, K, dev, chunk_rows):
    """Exact CE(base route) - CE(trained router's route), per token."""
    per, flat = {}, []
    for p in probs:
        x = p["x"].to(dev)
        pk = torch.topk(F.softmax(x @ W.T, -1), K, -1).indices[:, None, :]
        pb = torch.topk(F.softmax(x @ W0.T, -1), K, -1).indices[:, None, :]
        both = torch.cat([pk, pb], 1)
        pcur = F.softmax(x @ W.T, -1)
        pbase = F.softmax(x @ W0.T, -1)
        h = torch.stack([mix(p["bank"].to(dev), pcur, pk)[:, 0],
                         mix(p["bank"].to(dev), pbase, pb)[:, 0]], 1)
        u = replay(model, p, h, dev, chunk_rows)            # (n,2)
        v = (u[:, 0] - u[:, 1]).cpu().numpy()
        ch = (K - (pk[:, 0].unsqueeze(-1) == pb[:, 0].unsqueeze(1)).any(-1)
              .sum(-1)).float().mean().item()
        per.setdefault(p["pi"], []).extend(v.tolist())
        flat += [(float(z), ch) for z in v]
    return per, flat


def boot(per, B=2000, seed=0):
    ks = sorted(per); rng = np.random.default_rng(seed); out = []
    for _ in range(B):
        k = rng.choice(len(ks), len(ks), replace=True)
        pool = [z for i in k for z in per[ks[i]]]
        out.append(np.mean(pool))
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def main(a):
    tok, model = load(a)
    dev = model.model.layers[L + 1].input_layernorm.weight.device
    cs = [torch.load(f, map_location="cpu", weights_only=False) for f in a.cache]
    K = cs[0]["K"]
    probs = [p for c in cs for p in c["probs"]]
    W0 = cs[0]["gate"].to(dev)
    assert torch.allclose(W0, cs[1]["gate"].to(dev)), "shards disagree on base gate"
    pis = sorted({p["pi"] for p in probs})
    cut = int(len(pis) * a.train_frac)
    tr_pi, te_pi = set(pis[:cut]), set(pis[cut:])
    assert not (tr_pi & te_pi)
    fg0 = {it["problem"] for it in json.load(open(a.fg0))["items"]}
    tp = json.load(open(a.trainpool))["items"]
    assert not ({tp[p]["problem"] for p in pis} & fg0), "training problem in FG0 dev pool"
    tr = [p for p in probs if p["pi"] in tr_pi]
    te = [p for p in probs if p["pi"] in te_pi]
    print(f"problems {len(probs)}: train {len(tr)} / test {len(te)}, disjoint; "
          f"FG0 dev pool {len(fg0)} held apart")

    gen = torch.Generator(device=dev).manual_seed(a.seed)
    # FIXED evaluation support, drawn once from the REFERENCE router
    fixed = []
    for i, p in enumerate(te):
        x = p["x"].to(dev)
        pr, ids = sample_routes(x, W0, K, a.pool, a.n_gumbel, gen)
        nu = min(len({tuple(sorted(r.tolist())) for r in ids[k]}) for k in range(len(ids)))
        assert nu >= 8, f"V3 gumbel diversity {nu}/{a.n_gumbel}"
        u = replay(model, p, mix(p["bank"].to(dev), pr, ids), dev, a.chunk_rows,
                   check=(i == 0))
        fixed.append((ids, u))
        if (i + 1) % 20 == 0:
            print(f"  fixed support {i+1}/{len(te)}")

    def pref_acc(W):
        with torch.no_grad():
            ok = []
            for p, (ids, u) in zip(te, fixed):
                s = p["x"].to(dev) @ W.T
                jp, jm = u.argmax(1), u.argmin(1)
                rp = torch.gather(ids, 1, jp[:, None, None].expand(-1, 1, K))
                rm = torch.gather(ids, 1, jm[:, None, None].expand(-1, 1, K))
                ok += (logpi(s, rp) > logpi(s, rm))[:, 0].float().tolist()
        return float(np.mean(ok))

    def report(W, tag):
        per, flat = route_value(model, te, W, W0, K, dev, a.chunk_rows)
        v = np.array([z for k in per for z in per[k]])
        lo, hi = boot(per)
        acc = pref_acc(W)
        print(f"  {tag}: pref_acc {acc:.3f}  V_route {v.mean():+.5f} [{lo:+.5f},{hi:+.5f}]"
              f"  med {np.median(v):+.5f}  win {np.mean(v > 0):.3f}"
              f"  changed {np.mean([c for _, c in flat]):.2f}  n={len(v)}")
        return dict(pref_acc=acc, V=float(v.mean()), ci=[lo, hi],
                    V_med=float(np.median(v)), win=float(np.mean(v > 0)),
                    changed=float(np.mean([c for _, c in flat])), n=len(v))

    W = W0.clone().requires_grad_(True)
    opt = torch.optim.AdamW([W], lr=a.lr, weight_decay=0.0)
    hist = [dict(step=0, **report(W0, "before"))]
    for ep in range(a.epochs):
        order = torch.randperm(len(tr), generator=gen, device=dev).tolist()
        tot = 0.0
        for n, i in enumerate(order):
            p = tr[i]
            x = p["x"].to(dev)
            pr, ids = sample_routes(x, W.detach(), K, a.pool, a.n_gumbel, gen)
            with torch.no_grad():
                u = replay(model, p, mix(p["bank"].to(dev), pr, ids), dev, a.chunk_rows)
                jp, jm = u.argmax(1), u.argmin(1)
                delta = u.gather(1, jp[:, None])[:, 0] - u.gather(1, jm[:, None])[:, 0]
                rp = torch.gather(ids, 1, jp[:, None, None].expand(-1, 1, K))
                rm = torch.gather(ids, 1, jm[:, None, None].expand(-1, 1, K))
                s0 = x @ W0.T
                ref = (logpi(s0, rp) - logpi(s0, rm))[:, 0]
            opt.zero_grad(set_to_none=True)
            cur = (logpi(x @ W.T, rp) - logpi(x @ W.T, rm))[:, 0]
            loss = -(delta * F.logsigmoid(a.beta * (cur - ref))).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_([W], 1.0)
            opt.step(); tot += float(loss.detach())
            if (n + 1) % 25 == 0:
                print(f"  ep{ep+1} {n+1}/{len(tr)} loss {tot/(n+1):.4f}")
        hist.append(dict(step=ep + 1, **report(W.detach(), f"ep{ep+1}")))
        torch.save({"36": W.detach().cpu()}, a.ckpt)
        json.dump(dict(hist=hist, args=vars(a)), open(a.out, "w"), indent=1)
    print(f"wrote {a.out} and {a.ckpt}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", nargs="+",
                    default=["results/e10_cache_a.pt", "results/e10_cache_b.pt"])
    ap.add_argument("--fg0", default="results/fg0_devpool.json")
    ap.add_argument("--trainpool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e10_epo_l36.json")
    ap.add_argument("--ckpt", default="results/e10_gate_l36.pt")
    ap.add_argument("--train-frac", dest="train_frac", type=float, default=0.7)
    ap.add_argument("--pool", type=int, default=32)
    ap.add_argument("--n-gumbel", dest="n_gumbel", type=int, default=32)
    ap.add_argument("--chunk-rows", dest="chunk_rows", type=int, default=288)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
