"""CT03 E11 stage 2 -- the CORRECTED EPO gate (parent's action mechanism).

Frozen design: docs/E11_DESIGN.md.

    r-      = the route the CURRENT router actually executes (its top-k)
    r*      = argmin CE over G Gumbel top-k routes from the current router
    SKIP the token unless CE(r*) < CE(r-);  otherwise r+ = r*
    Delta   = CE(r-) - CE(r+)
    loss    = -Delta * log sigmoid(beta * [ (logpi_th(r+) - logpi_ref(r+))
                                           -(logpi_th(r-) - logpi_ref(r-)) ])

E09/E10 used best-vs-worst SAMPLED route, which never involves the deployed
route and so carries no policy-improvement semantics. That is the defect this
file repairs.

Hard tokens enter dynamically by the CURRENT router's CE > tau, as the parent
does, which is why no expert bank is cached: expert outputs are computed here,
on demand, for the current top-P pool only.
"""
import argparse, json, sys
import builtins
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import load

L = 47
print = lambda *x, **k: builtins.print(*x, **{**k, 'flush': True})


def rms(h, w, eps):
    return h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + eps) * w


def bank_for(moe, X, ids):
    """E_e(x_i) for the given (token, expert) pairs. X (n,d), ids (n,P) -> (n,P,d).

    One grouped matmul per distinct expert, not one per pair: the pair loop is
    the 1-2% GPU utilisation mistake from E06."""
    n, P = ids.shape
    d = X.shape[-1]
    out = torch.zeros(n * P, d, device=X.device, dtype=X.dtype)
    flat = ids.reshape(-1)
    for e in flat.unique().tolist():
        rows = (flat == e).nonzero(as_tuple=True)[0]
        out[rows] = moe.experts[e](X[rows // P])
    return out.view(n, P, d)


def mix_local(bank, p_pool, loc):
    """h_r from pool-local indices. bank (n,P,d), p_pool (n,P), loc (n,R,K)."""
    w = torch.gather(p_pool.unsqueeze(1).expand(-1, loc.shape[1], -1), 2, loc)
    w = w / w.sum(-1, keepdim=True)
    e = torch.gather(bank.unsqueeze(1).expand(-1, loc.shape[1], -1, -1), 2,
                     loc.unsqueeze(-1).expand(-1, -1, -1, bank.shape[-1]))
    return (e * w.unsqueeze(-1)).sum(2)


def ce_of(resid, h, tgt, nw, eps, head, chunk=2048):
    n, R, d = h.shape
    flat = rms((resid.unsqueeze(1) + h).reshape(-1, d), nw, eps)
    tg = tgt.unsqueeze(1).expand(n, R).reshape(-1)
    out = torch.empty(flat.shape[0], device=flat.device)
    for i in range(0, flat.shape[0], chunk):
        s = slice(i, i + chunk)
        out[s] = F.cross_entropy(flat[s] @ head.T, tg[s], reduction="none")
    return out.view(n, R)


def gumbel_local(logp, K, R, gen):
    u = torch.rand(logp.shape[0], R, logp.shape[1], generator=gen,
                   device=logp.device).clamp(1e-20, 1 - 1e-7)
    g = -torch.log(-torch.log(u))          # explicit intermediates; see e06
    assert torch.isfinite(g).all()
    return torch.topk(logp.unsqueeze(1) + g, K, dim=-1).indices


def logpi(s, idx):
    lp = F.log_softmax(s, -1)
    return torch.gather(lp.unsqueeze(1).expand(-1, idx.shape[1], -1), 2, idx).sum(-1)


def candidates(moe, x, resid, tgt, W, K, P, R, gen, nw, eps, head):
    """Everything the objective needs for one batch of tokens, at the CURRENT W.

    Returns CE of the executed route, CE of every sampled route, and both as
    GLOBAL expert ids."""
    with torch.no_grad():
        p = F.softmax(x @ W.T, -1)
        pool = torch.topk(p, P, -1).indices                       # n,P (sorted)
        p_pool = torch.gather(p, 1, pool)
        bank = bank_for(moe, x, pool)
        loc_exec = torch.arange(K, device=x.device).expand(len(x), 1, K)
        logp = torch.log(p_pool.clamp_min(1e-30))
        loc_s = gumbel_local(logp, K, R, gen)
        loc = torch.cat([loc_exec, loc_s], 1)                     # n,1+R,K
        ce = ce_of(resid, mix_local(bank, p_pool, loc), tgt, nw, eps, head)
        ids = torch.gather(pool.unsqueeze(1).expand(-1, 1 + R, -1), 2, loc)
    return ce[:, 0], ce[:, 1:], ids[:, 0], ids[:, 1:]


def boot(per, B=2000, seed=0):
    ks = sorted(per); rng = np.random.default_rng(seed); v = []
    for _ in range(B):
        k = rng.choice(len(ks), len(ks), replace=True)
        v.append(np.mean([z for i in k for z in per[ks[i]]]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def main(a):
    tok, model = load(a)
    moe = model.model.layers[L].mlp
    dev = model.lm_head.weight.device
    head, nw = model.lm_head.weight, model.model.norm.weight
    cs = [torch.load(f, map_location="cpu", weights_only=False) for f in a.cache]
    K = cs[0]["K"]; eps = cs[0]["eps"]
    x = torch.cat([c["x"] for c in cs]).to(dev)
    resid = torch.cat([c["resid"] for c in cs]).to(dev)
    meta = [m for c in cs for m in c["meta"]]
    tgt = torch.tensor([m["tgt"] for m in meta], device=dev)
    pi = np.array([m["pi"] for m in meta])
    W0 = cs[0]["gate"].to(dev)
    assert torch.allclose(W0, cs[1]["gate"].to(dev)), "shards disagree on base gate"
    assert torch.allclose(W0, moe.gate.weight.float()), "cache gate != model gate"

    pis = sorted(set(pi.tolist()))
    cut = int(len(pis) * a.train_frac)
    tr_pi, te_pi = set(pis[:cut]), set(pis[cut:])
    assert not (tr_pi & te_pi)
    fg0 = {it["problem"] for it in json.load(open(a.fg0))["items"]}
    tp = json.load(open(a.trainpool))["items"]
    assert not ({tp[p]["problem"] for p in pis} & fg0), "training problem in FG0 pool"
    trn = np.array([p in tr_pi for p in pi]); tst = ~trn
    itr = np.nonzero(trn)[0]; ite = np.nonzero(tst)[0]
    print(f"tokens {len(meta)}: train {len(itr)} ({len(tr_pi)} problems) / "
          f"test {len(ite)} ({len(te_pi)} problems), disjoint; FG0 held apart")

    gen = torch.Generator(device=dev).manual_seed(a.seed)
    # ---- FIXED evaluation support, from the REFERENCE router ----
    ev, ev_tr = [], []
    itr_ev = itr[:len(ite)]
    for b in range(0, len(ite) + len(itr_ev), a.eval_batch):
        which = ite if b < len(ite) else itr_ev
        off = b if b < len(ite) else b - len(ite)
        k = torch.from_numpy(which[off:off + a.eval_batch]).to(dev)
        if len(k) == 0:
            continue
        ce_m, ce_s, id_m, id_s = candidates(moe, x[k], resid[k], tgt[k], W0, K,
                                            a.pool, a.n_gumbel, gen, nw, eps, head)
        j = ce_s.argmin(1)
        better = ce_s.gather(1, j[:, None])[:, 0] < ce_m
        (ev if b < len(ite) else ev_tr).append(
            dict(k=k, ce_m=ce_m, id_m=id_m,
                 id_p=torch.gather(id_s, 1, j[:, None, None]
                                   .expand(-1, 1, K))[:, 0],
                 ce_p=ce_s.gather(1, j[:, None])[:, 0], better=better))
    nb = int(sum(int(e["better"].sum()) for e in ev))
    print(f"  fixed support: {nb}/{len(ite)} held-out tokens have an improving "
          f"route under the reference router ({nb/len(ite):.3f})")

    def report(W, tag, EV=None):
        EV = ev if EV is None else EV
        with torch.no_grad():
            acc, adopt, ov, V, per, ch = [], [], [], [], {}, []
            for e in EV:
                k = e["k"]
                s = x[k] @ W.T
                m = e["better"]
                if int(m.sum()):
                    acc += (logpi(s[m], e["id_p"][m][:, None])
                            > logpi(s[m], e["id_m"][m][:, None]))[:, 0].float().tolist()
                    pick_m = torch.topk(F.softmax(s[m], -1), K, -1).indices
                    adopt += (pick_m.sort(-1).values
                              == e["id_p"][m].sort(-1).values).all(-1).float().tolist()
                    # exact adoption of an 8-of-128 subset is a severe event, so
                    # also report the graded version: how many of r+'s experts
                    # the router now actually executes. Its floor is the
                    # reference router's own overlap with r+, reported as ov0.
                    ov += (pick_m.unsqueeze(-1) == e["id_p"][m].unsqueeze(1)) \
                        .any(-1).sum(-1).float().tolist()
                p = F.softmax(s, -1)
                pool = torch.topk(p, a.pool, -1).indices
                p_pool = torch.gather(p, 1, pool)
                bank = bank_for(moe, x[k], pool)
                loc = torch.arange(K, device=dev).expand(len(k), 1, K)
                ce_new = ce_of(resid[k], mix_local(bank, p_pool, loc), tgt[k],
                               nw, eps, head)[:, 0]
                v = (e["ce_m"] - ce_new).cpu().numpy()
                V += v.tolist()
                pk = torch.gather(pool, 1, loc[:, 0])
                ch += (K - (pk.unsqueeze(-1) == e["id_m"].unsqueeze(1))
                       .any(-1).sum(-1)).float().tolist()
                for z, q in zip(v, pi[k.cpu().numpy()]):
                    per.setdefault(int(q), []).append(float(z))
        lo, hi = boot(per)
        V = np.array(V)
        r = dict(pref_acc=float(np.mean(acc)) if acc else float("nan"),
                 adopt=float(np.mean(adopt)) if adopt else float("nan"),
                 ov=float(np.mean(ov)) if ov else float("nan"),
                 V=float(V.mean()), ci=[lo, hi], V_med=float(np.median(V)),
                 win=float(np.mean(V > 0)), changed=float(np.mean(ch)), n=len(V))
        print(f"  {tag}: pref_acc {r['pref_acc']:.3f} (floor 0)  adopt {r['adopt']:.3f}"
              f" ov {r['ov']:.2f}/{K}"
              f"  V_route {r['V']:+.5f} [{lo:+.5f},{hi:+.5f}]  med {r['V_med']:+.5f}"
              f"  win {r['win']:.3f}  changed {r['changed']:.2f}  n={r['n']}")
        return r

    if a.noise_curve:
        # CALIBRATION, not a method: both trained arms end near changed~5.9,
        # ov~1.9. If a RANDOM dW of the same Frobenius ratio lands there too,
        # neither arm learned anything -- it only diffused the gate. The
        # trained points have to be read against this curve, not against W0.
        g2 = torch.Generator(device=dev).manual_seed(a.seed + 1)
        hist = [dict(step=0, ratio=0.0, **report(W0, "W0"))]
        for rt in [float(z) for z in a.noise_curve]:
            dW = torch.randn(W0.shape, generator=g2, device=dev, dtype=W0.dtype)
            dW *= rt * W0.norm() / dW.norm()
            hist.append(dict(step=-1, ratio=rt,
                             **report(W0 + dW, f"noise r={rt:.3f}")))
        json.dump(dict(hist=hist, args=vars(a)), open(a.out, "w"), indent=1)
        print(f"wrote {a.out}")
        return

    W = W0.clone().requires_grad_(True)
    opt = torch.optim.AdamW([W], lr=a.lr, weight_decay=0.0)
    hist = [dict(step=0, **report(W0, "before"))]

    if a.dump_ev:
        # The frozen (r+, r-) targets cost a model load to build and nothing to
        # reuse. Dumping them once turns every follow-up decomposition into a
        # zero-GPU analysis.
        torch.save(dict(
            ev=[{k: v.cpu() for k, v in e.items()} for e in ev],
            ev_tr=[{k: v.cpu() for k, v in e.items()} for e in ev_tr],
            W0=W0.cpu(), K=K, pi=pi), a.dump_ev)
        print(f"wrote {a.dump_ev}")
        return

    if a.fixed_target:
        # CAPACITY control. Online EPO resamples r+ from the CURRENT router
        # every step, so "ov falls" can mean a moving target rather than a gate
        # that cannot express the preference. Here the targets are FROZEN at W0
        # -- the same pairs report() scores -- and the gate is optimised
        # directly against them. If ov cannot rise even here, no schedule or
        # step size fixes it; if it rises, the online dynamic is the problem.
        pairs = [(e["k"][e["better"]], e["id_p"][e["better"]],
                  e["id_m"][e["better"]],
                  (e["ce_m"] - e["ce_p"])[e["better"]]) for e in ev_tr]
        kk = torch.cat([q[0] for q in pairs]); rp = torch.cat([q[1] for q in pairs])
        rm = torch.cat([q[2] for q in pairs]); dl = torch.cat([q[3] for q in pairs])
        print(f"  fixed-target capacity control on {len(kk)} frozen pairs")
        Wf = W0.clone().requires_grad_(True)
        of = torch.optim.AdamW([Wf], lr=a.lr, weight_decay=0.0)
        order = np.random.default_rng(a.seed).permutation(len(kk))
        for ep in range(a.fixed_epochs):
            for b in range(0, len(order), a.batch):
                q = torch.from_numpy(order[b:b + a.batch]).to(dev)
                of.zero_grad(set_to_none=True)
                sc = x[kk[q]] @ Wf.T
                if a.objective == "pref":
                    with torch.no_grad():
                        s0 = x[kk[q]] @ W0.T
                        rf = (logpi(s0, rp[q][:, None]) - logpi(s0, rm[q][:, None]))[:, 0]
                    cu = (logpi(sc, rp[q][:, None]) - logpi(sc, rm[q][:, None]))[:, 0]
                    ls = -(dl[q] * F.logsigmoid(a.beta * (cu - rf))).mean()
                elif a.objective == "sft":
                    ls = -(dl[q] * logpi(sc, rp[q][:, None])[:, 0]).mean()
                else:
                    # Execution-aligned objective: encode the condition the
                    # deployed router actually evaluates, min_{e in r+} z_e >
                    # max_{j not in r+} z_j, instead of a score comparison
                    # between two fixed subsets. It uses NO Delta and no r- --
                    # only r+, which is the same supervision EPO consumes. So
                    # this is a deployable alternative objective, not an
                    # oracle probe; an earlier comment here called it one,
                    # which was wrong.
                    mk = torch.zeros_like(sc, dtype=torch.bool)
                    mk.scatter_(1, rp[q], True)
                    hi = -torch.logsumexp(-sc.masked_fill(~mk, 1e4), -1)  # soft min in r+
                    lo_ = torch.logsumexp(sc.masked_fill(mk, -1e4), -1)   # soft max out
                    ls = F.relu(a.margin + lo_ - hi).mean()
                ls.backward(); torch.nn.utils.clip_grad_norm_([Wf], 1.0); of.step()
            report(Wf.detach(), f"fixed ep{ep+1}/TRAIN", ev_tr)
        print(f"  drift {(Wf.detach()-W0).norm()/W0.norm():.4f}")
        return

    perm = np.random.default_rng(a.seed).permutation(itr)
    buf, nseen, nhard, nimp, nstep, tot = [], 0, 0, 0, 0, 0.0
    for b in range(0, len(perm), a.scan_batch):
        if a.max_steps and nstep >= a.max_steps:
            break
        k = torch.from_numpy(perm[b:b + a.scan_batch]).to(dev)
        ce_m, ce_s, id_m, id_s = candidates(moe, x[k], resid[k], tgt[k], W.detach(),
                                            K, a.pool, a.n_gumbel, gen, nw, eps, head)
        nseen += len(k)
        hard = ce_m > a.tau                      # parent: current CE > 0.1
        j = ce_s.argmin(1)
        ce_p = ce_s.gather(1, j[:, None])[:, 0]
        keep = hard & (ce_p < ce_m)              # parent: skip unless improving
        nhard += int(hard.sum()); nimp += int(keep.sum())
        if int(keep.sum()):
            idp = torch.gather(id_s, 1, j[:, None, None].expand(-1, 1, K))[:, 0]
            for q in keep.nonzero(as_tuple=True)[0].tolist():
                buf.append((int(k[q]), idp[q].clone(), id_m[q].clone(),
                            float(ce_m[q] - ce_p[q])))
        while len(buf) >= a.batch:
            take, buf = buf[:a.batch], buf[a.batch:]
            kk = torch.tensor([t[0] for t in take], device=dev)
            rp = torch.stack([t[1] for t in take])[:, None]
            rm = torch.stack([t[2] for t in take])[:, None]
            delta = torch.tensor([t[3] for t in take], device=dev)
            with torch.no_grad():
                s0 = x[kk] @ W0.T
                ref = (logpi(s0, rp) - logpi(s0, rm))[:, 0]
            opt.zero_grad(set_to_none=True)
            s = x[kk] @ W.T
            cur = (logpi(s, rp) - logpi(s, rm))[:, 0]
            if a.objective == "pref":
                loss = -(delta * F.logsigmoid(a.beta * (cur - ref))).mean()
            else:
                # CONTROL, not a proposal: weighted likelihood of r+ alone, with
                # no r- term at all. If the adoption metric and this pipeline
                # can register a router moving TOWARD r+, this is where it
                # shows. If even this leaves ov flat, the negative result below
                # is about my measurement, not about the objective.
                loss = -(delta * logpi(s, rp)[:, 0]).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_([W], 1.0)
            opt.step(); tot += float(loss.detach()); nstep += 1
            if a.max_steps and nstep >= a.max_steps:
                buf = []; break
            if nstep % a.eval_every == 0 and a.train_eval:
                report(W.detach(), f"step{nstep}/TRAIN", ev_tr)
            if nstep % a.eval_every == 0:
                print(f"  step {nstep}  loss {tot/nstep:.4f}  scanned {nseen}"
                      f"  hard {nhard/max(nseen,1):.3f}  improving {nimp/max(nseen,1):.3f}")
                hist.append(dict(step=nstep, **report(W.detach(), f"step{nstep}")))
    if a.train_eval:
        report(W.detach(), "final/TRAIN", ev_tr)
    hist.append(dict(step=nstep, **report(W.detach(), "final")))
    print(f"\nscanned {nseen} tokens: hard {nhard} ({nhard/nseen:.3f}), "
          f"with an improving route {nimp} ({nimp/nseen:.3f}); {nstep} updates")
    torch.save({str(L): W.detach().cpu()}, a.ckpt)
    json.dump(dict(hist=hist, args=vars(a), scanned=nseen, hard=nhard,
                   improving=nimp, steps=nstep), open(a.out, "w"), indent=1)
    print(f"wrote {a.out} and {a.ckpt}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", nargs="+",
                    default=["results/e11_cache_a.pt", "results/e11_cache_b.pt"])
    ap.add_argument("--fg0", default="results/fg0_devpool.json")
    ap.add_argument("--trainpool", default="results/cpd_trainpool.json")
    ap.add_argument("--out", default="results/e11_epo_l47.json")
    ap.add_argument("--ckpt", default="results/e11_gate_l47.pt")
    ap.add_argument("--max-steps", dest="max_steps", type=int, default=0)
    ap.add_argument("--objective", choices=["pref", "sft", "rank"], default="pref")
    ap.add_argument("--margin", type=float, default=0.5)
    ap.add_argument("--noise-curve", dest="noise_curve", nargs="*", default=None)
    ap.add_argument("--train-eval", dest="train_eval", action="store_true")
    ap.add_argument("--fixed-target", dest="fixed_target", action="store_true")
    ap.add_argument("--dump-ev", dest="dump_ev", default=None)
    ap.add_argument("--fixed-epochs", dest="fixed_epochs", type=int, default=8)
    ap.add_argument("--train-frac", dest="train_frac", type=float, default=0.8)
    ap.add_argument("--pool", type=int, default=32)
    ap.add_argument("--n-gumbel", dest="n_gumbel", type=int, default=32)
    ap.add_argument("--tau", type=float, default=0.1)       # parent's hard-token rule
    ap.add_argument("--lr", type=float, default=3e-4)       # parent
    ap.add_argument("--beta", type=float, default=0.1)      # parent
    ap.add_argument("--batch", type=int, default=16)        # parent
    ap.add_argument("--scan-batch", dest="scan_batch", type=int, default=64)
    ap.add_argument("--eval-batch", dest="eval_batch", type=int, default=64)
    ap.add_argument("--eval-every", dest="eval_every", type=int, default=100)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
