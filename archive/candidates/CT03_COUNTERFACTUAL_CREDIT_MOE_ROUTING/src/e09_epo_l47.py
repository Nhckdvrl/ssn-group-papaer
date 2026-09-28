"""CT03 E09 stage 2 -- dynamic Exact-EPO at L47, the parent's setting.

Frozen design: docs/E09_DESIGN.md. No proxy anywhere in this file.

Routes are resampled from the CURRENT router at every step and their exact CE is
recomputed, so this is genuinely dynamic. It is cheap only because L47 is the
last decoder layer: patching the MoE output at t changes the CE at t and nowhere
else, and x_t does not depend on the L47 gate. Everything else is cached.
"""
import argparse, json, sys
import builtins
import numpy as np
import torch
import torch.nn.functional as F

print = lambda *x, **k: builtins.print(*x, **{**k, 'flush': True})


def rms(h, w, eps):
    return h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + eps) * w


def mix(bank, p, idx):
    """h_r for routes given as expert ids. bank (N,E,d), p (N,E), idx (N,R,K)."""
    w = torch.gather(p.unsqueeze(1).expand(-1, idx.shape[1], -1), 2, idx)   # N,R,K
    w = w / w.sum(-1, keepdim=True)
    e = torch.gather(bank.unsqueeze(1).expand(-1, idx.shape[1], -1, -1), 2,
                     idx.unsqueeze(-1).expand(-1, -1, -1, bank.shape[-1]))
    return (e * w.unsqueeze(-1)).sum(2)                                     # N,R,d


def ce_of(resid, h, tgt, nw, eps, head, chunk=64):
    """Exact CE at the patched position. N,R,d -> N,R."""
    N, R, d = h.shape
    flat = rms((resid.unsqueeze(1) + h).reshape(-1, d), nw, eps)
    tg = tgt.unsqueeze(1).expand(N, R).reshape(-1)
    out = torch.empty(flat.shape[0], device=flat.device)
    for i in range(0, flat.shape[0], chunk * R):
        s = slice(i, i + chunk * R)
        out[s] = F.cross_entropy(flat[s] @ head.T, tg[s], reduction="none")
    return out.view(N, R)


def gumbel_routes(logp, K, R, gen):
    """Parent's sampler, over the CURRENT router. logp (N,P) on the pool."""
    u = torch.rand(logp.shape[0], R, logp.shape[1], generator=gen,
                   device=logp.device).clamp(1e-20, 1 - 1e-7)
    g = -torch.log(-torch.log(u))            # explicit intermediates: see e06
    assert torch.isfinite(g).all()
    return torch.topk(logp.unsqueeze(1) + g, K, dim=-1).indices              # N,R,K


def logpi(s, idx):
    lp = F.log_softmax(s, -1)
    return torch.gather(lp.unsqueeze(1).expand(-1, idx.shape[1], -1), 2, idx).sum(-1)


def sample_routes(x, W, bank, K, P, R, gen):
    """Top-P pool of the current router, R Gumbel top-K routes, as EXPERT IDS."""
    with torch.no_grad():
        p = F.softmax(x @ W.T, -1)
        pool = torch.topk(p, P, dim=-1).indices                              # N,P
        logp = torch.log(torch.gather(p, 1, pool).clamp_min(1e-30))
        loc = gumbel_routes(logp, K, R, gen)                                 # N,R,K
        ids = torch.gather(pool.unsqueeze(1).expand(-1, R, -1), 2, loc)
    return p, ids


def boot(per_problem, B=2000, seed=0):
    ks = sorted(per_problem); rng = np.random.default_rng(seed); v = []
    for _ in range(B):
        pick = rng.choice(len(ks), len(ks), replace=True)
        pool = [z for i in pick for z in per_problem[ks[i]]]
        if pool:
            v.append(np.mean(pool))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def evaluate(W, W0, d, fixed, K, P, tag):
    """Fixed-support preference accuracy + exact route value of the picked route."""
    with torch.no_grad():
        idx, ce = fixed["ids"], fixed["ce"]
        s = d["x"] @ W.T
        rp = torch.gather(idx, 1, ce.argmin(1)[:, None, None].expand(-1, 1, K))
        rm = torch.gather(idx, 1, ce.argmax(1)[:, None, None].expand(-1, 1, K))
        acc = float((logpi(s, rp) > logpi(s, rm)).float().mean())

        pick = torch.topk(F.softmax(s, -1), K, dim=-1).indices[:, None, :]   # N,1,K
        p_cur = F.softmax(s, -1)
        h = mix(d["bank"], p_cur, pick)
        ce_new = ce_of(d["resid"], h, d["tgt"], d["nw"], d["eps"], d["head"])[:, 0]
        base_pick = torch.topk(F.softmax(d["x"] @ W0.T, -1), K, dim=-1).indices[:, None, :]
        p_b = F.softmax(d["x"] @ W0.T, -1)
        ce_b = ce_of(d["resid"], mix(d["bank"], p_b, base_pick), d["tgt"],
                     d["nw"], d["eps"], d["head"])[:, 0]
        V = (ce_b - ce_new).cpu().numpy()
        changed = float((K - (pick[:, 0] .unsqueeze(-1) ==
                              base_pick[:, 0].unsqueeze(1)).any(-1).sum(-1)).float().mean())
    per = {}
    for v, pi in zip(V, d["pi"]):
        per.setdefault(int(pi), []).append(float(v))
    lo, hi = boot(per)
    print(f"  {tag}: pref_acc {acc:.3f}  V_route {V.mean():+.5f} "
          f"[{lo:+.5f},{hi:+.5f}]  med {np.median(V):+.5f}  win {np.mean(V > 0):.3f}"
          f"  experts changed {changed:.2f}  n={len(V)}")
    return dict(pref_acc=acc, V=float(V.mean()), ci=[lo, hi],
                V_med=float(np.median(V)), win=float(np.mean(V > 0)),
                changed=changed, n=len(V))


def main(a):
    dev = "cuda:0"
    cs = [torch.load(f, map_location="cpu", weights_only=False) for f in a.cache]
    head = torch.load(a.head, map_location=dev, weights_only=False)
    K, E = cs[0]["K"], cs[0]["E"]
    x = torch.cat([c["x"] for c in cs]).to(dev)
    resid = torch.cat([c["resid"] for c in cs]).to(dev)
    bank = torch.cat([c["bank"] for c in cs]).to(dev)
    meta = [m for c in cs for m in c["meta"]]
    tgt = torch.tensor([m["tgt"] for m in meta], device=dev)
    pi = np.array([m["pi"] for m in meta])
    nw = cs[0]["norm_w"].to(dev); eps = cs[0]["eps"]
    W0 = cs[0]["gate"].to(dev)
    assert torch.allclose(W0, cs[1]["gate"].to(dev)), "shards disagree on the base gate"

    pis = sorted(set(pi.tolist()))

    cut = int(len(pis) * a.train_frac)
    tr_pi, te_pi = set(pis[:cut]), set(pis[cut:])
    assert not (tr_pi & te_pi)
    # Assert, don't assume: the FG0 free-generation dev pool must not contain
    # any problem these routers were trained or evaluated on.
    fg0 = {it["problem"] for it in json.load(open(a.fg0))["items"]}
    tp = json.load(open(a.trainpool))["items"]
    used = {tp[p]["problem"] for p in pis}
    assert not (used & fg0), f"{len(used & fg0)} training problems are in the FG0 dev pool"
    trn = np.array([p in tr_pi for p in pi]); tst = ~trn
    print(f"tokens {len(meta)}  train {int(trn.sum())} ({len(tr_pi)} problems) / "
          f"test {int(tst.sum())} ({len(te_pi)} problems), disjoint; "
          f"fg0 dev pool {len(fg0)} problems held apart")

    def sub(m):
        return dict(x=x[m], resid=resid[m], bank=bank[m], tgt=tgt[m], pi=pi[m],
                    nw=nw, eps=eps, head=head)
    dtr, dte = sub(trn), sub(tst)

    gen = torch.Generator(device=dev).manual_seed(a.seed)
    # FIXED evaluation support: drawn once from the REFERENCE router, so the
    # held-out candidate set does not move with training.
    _, f_ids = sample_routes(dte["x"], W0, dte["bank"], K, a.pool, a.n_gumbel, gen)
    with torch.no_grad():
        p_ref = F.softmax(dte["x"] @ W0.T, -1)
        f_ce = ce_of(dte["resid"], mix(dte["bank"], p_ref, f_ids), dte["tgt"],
                     nw, eps, head)
        nuniq = [len({tuple(sorted(r.tolist())) for r in f_ids[i]})
                 for i in range(min(64, len(f_ids)))]
    assert min(nuniq) >= 8, f"V3 gumbel diversity min {min(nuniq)}/{a.n_gumbel}"
    print(f"  fixed support: {np.mean(nuniq):.1f} unique routes / {a.n_gumbel} draws")
    fixed = dict(ids=f_ids, ce=f_ce)

    W = W0.clone().requires_grad_(True)
    opt = torch.optim.AdamW([W], lr=a.lr, weight_decay=0.0)
    hist = [dict(step=0, **evaluate(W0, W0, dte, fixed, K, a.pool, "before"))]
    N = len(dtr["x"])
    for ep in range(a.epochs):
        perm = torch.randperm(N, generator=gen, device=dev)
        tot = 0.0
        for b in range(0, N, a.batch):
            k = perm[b:b + a.batch]
            # routes resampled from the CURRENT router, exact CE recomputed
            p_cur, ids = sample_routes(dtr["x"][k], W.detach(), dtr["bank"][k],
                                       K, a.pool, a.n_gumbel, gen)
            with torch.no_grad():
                ce = ce_of(dtr["resid"][k], mix(dtr["bank"][k], p_cur, ids),
                           dtr["tgt"][k], nw, eps, head)
                jp, jm = ce.argmin(1), ce.argmax(1)
                delta = ce.gather(1, jm[:, None])[:, 0] - ce.gather(1, jp[:, None])[:, 0]
                rp = torch.gather(ids, 1, jp[:, None, None].expand(-1, 1, K))
                rm = torch.gather(ids, 1, jm[:, None, None].expand(-1, 1, K))
                s0 = dtr["x"][k] @ W0.T
                ref = (logpi(s0, rp) - logpi(s0, rm))[:, 0]
            opt.zero_grad(set_to_none=True)
            s = dtr["x"][k] @ W.T
            cur = (logpi(s, rp) - logpi(s, rm))[:, 0]
            loss = -(delta * F.logsigmoid(a.beta * (cur - ref))).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_([W], 1.0)
            opt.step(); tot += float(loss.detach()) * len(k)
        print(f"ep{ep+1:>3} loss {tot/N:.4f}")
        hist.append(dict(step=ep + 1,
                         **evaluate(W.detach(), W0, dte, fixed, K, a.pool, f"ep{ep+1}")))
    torch.save({"47": W.detach().cpu()}, a.ckpt)
    json.dump(dict(hist=hist, args=vars(a)), open(a.out, "w"), indent=1)
    print(f"wrote {a.out} and {a.ckpt}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", nargs="+",
                    default=["results/e09_cache_a.pt", "results/e09_cache_b.pt"])
    ap.add_argument("--head", default="results/e09_head.pt")
    ap.add_argument("--fg0", default="results/fg0_devpool.json")
    ap.add_argument("--trainpool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e09_epo_l47.json")
    ap.add_argument("--ckpt", default="results/e09_gate_l47.pt")
    ap.add_argument("--train-frac", dest="train_frac", type=float, default=0.7)
    ap.add_argument("--pool", type=int, default=32)
    ap.add_argument("--n-gumbel", dest="n_gumbel", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
