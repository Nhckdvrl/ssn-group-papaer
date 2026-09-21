"""CT03 CPD v1 -- Counterfactual Potential Distillation, three arms.

Frozen design: docs/CPD_V1_DESIGN.md (amended 2026-09-21, mass-preserving target).

    u_hat_ij = -g^T dh_ij
    z_hat    = argmin_z sum_ij [(z_j - z_i) - u_hat_ij]^2         on U = S u C
    q*(e)    = P_U p_0(e)e^{beta z_e} / sum_{k in U} p_0(k)e^{beta z_k}   e in U
    q*(e)    = p_0(e)                                                     e not in U
    L        = KL(q* || p_theta)

q* is gauge invariant in z, leaves experts outside U at their base probability,
and preserves sum_U q* = sum_U p_0 exactly, so no gain can come from inflating
candidate mass or flattening the router.
"""

import argparse, json, os, random, sys, time
import numpy as np
import torch
import torch.nn.functional as F
from datasets import load_dataset

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import MODEL, Capture, load, route_of
from e035_integrability import fit_potentials

LAYERS = [36, 44]
LADDER_GRID = (0.001, 0.002, 0.003, 0.004, 0.006, 0.008,
               0.01, 0.02, 0.05, 0.1, 0.2)


def potential(moe, x, h, g, K, m):
    """z on U, the expert list U, and the full base softmax p0. Scalar trick:
    g^T dh_ij = (Z/Z'-1)(g^T h) + (p_j g^T E_j - p_i g^T E_i)/Z'."""
    p, rank, sel, Z = route_of(moe, x, K)
    cand = rank[K:K + m].tolist()
    U = sel + cand
    with torch.no_grad():
        ge = {e: float(g @ moe.experts[e](x).float()) for e in U}
        gh = float(g @ h.float())
    trip = []
    for i in sel:
        for j in cand:
            Zp = Z - float(p[i]) + float(p[j])
            px = (Z / Zp - 1.0) * gh + (float(p[j]) * ge[j] - float(p[i]) * ge[i]) / Zp
            trip.append((i, j, -px))                 # u_hat = predicted improvement
    z, idx, r2, _, _ = fit_potentials(trip)
    return np.array([z[idx[e]] for e in U]), U, p, r2


def cpd_target(p0, U, z, beta):
    """Exact mass-preserving reallocation inside U; identity outside.

    Computed in log space: beta*z can be large enough that exp() overflows to
    inf and the target silently becomes NaN."""
    pu = p0[U]
    lw = pu.clamp_min(1e-30).log() + beta * z
    lw = lw - lw.max()
    w = lw.exp()
    q = p0.clone()
    q[U] = w / w.sum() * pu.sum()
    return q


def kl_ceiling(p0, U, z):
    """Largest KL-to-base this z direction can reach. As beta -> inf the mass
    P_U collapses onto argmax z, so the KL is BOUNDED -- and the bound depends
    on which expert that is. A shuffled z whose argmax lands on a high-p0
    expert can therefore be unable to match the true target's KL at any beta."""
    pu = p0[U]
    e = int(torch.argmax(z))
    PU = float(pu.sum())
    return PU * float(np.log(PU / max(float(pu[e]), 1e-30)))


def kl_to_base(p0, U, z, beta):
    q = cpd_target(p0, U, z, beta)
    m = q > 0
    return float((q[m] * (q[m].log() - p0[m].log())).sum())


def shuffled_target(p0, U, z, beta, kl_true, rng):
    """KL-CONSTRAINED shuffled control: randomise which expert receives which
    counterfactual advantage, subject to matching the exact intervention budget.

    Along r_c ∝ r_0 exp(c z) the KL rises monotonically (d/dc = c Var_{r_c}(z))
    from 0 to the ceiling P_U log(P_U / p_0(e*)) set by argmax z. So a
    permutation can hit kl_true iff its argmax expert's ceiling reaches it, and
    the feasible set always contains argmin p_0 -- because kl_true itself is at
    most P_U log(P_U / min_e p_0(e)). Sampling e* from the feasible set makes
    the control exact for EVERY token, with no clamping.
    """
    pu = p0[U]
    PU = float(pu.sum())
    ceil = PU * np.log(PU / np.clip(pu.cpu().numpy(), 1e-30, None))
    feas = np.flatnonzero(ceil >= kl_true)
    if feas.size == 0:                       # only if kl_true is numerically at the bound
        feas = np.array([int(np.argmin(pu.cpu().numpy()))])
    star = int(rng.choice(feas))
    zs = z.clone()
    order = np.argsort(-z.cpu().numpy())
    rest = [k for k in range(len(z)) if k != star]
    perm = rng.permutation(len(rest))
    zs[star] = z[int(order[0])]
    for k, pk in zip(rest, perm):
        zs[k] = z[int(order[1:][pk])]

    lo, hi = 0.0, 1.0
    while kl_to_base(p0, U, zs, beta * hi) < kl_true and hi < 1e6:
        hi *= 4
    for _ in range(60):
        mid = (lo + hi) / 2
        if kl_to_base(p0, U, zs, beta * mid) < kl_true:
            lo = mid
        else:
            hi = mid
    c = (lo + hi) / 2
    return (cpd_target(p0, U, zs, beta * c), int(feas.size), star,
            c, kl_to_base(p0, U, zs, beta * c))


def iter_tokens(model, tok, ex, a, dev0):
    """One trajectory -> (per-layer z/U/p0 at selected hard tokens, base CE)."""
    prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                     tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    p_ids = tok(prompt, add_special_tokens=False).input_ids
    s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
    ids = p_ids + s_ids
    if len(ids) > a.max_len or len(s_ids) < 24:
        return None
    input_ids = torch.tensor([ids], device=dev0)
    targets = input_ids[0, 1:]
    first = len(p_ids) - 1
    with Capture(model, LAYERS) as cap:
        with torch.enable_grad():
            emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
            lg = model(inputs_embeds=emb, use_cache=False).logits
            ce = F.cross_entropy(lg[0, :-1].float(), targets.to(lg.device),
                                 reduction="none")
            ce[first:].sum().backward()
        base_ce = ce.detach().clone()
        g = {l: cap.mlp_out[l].grad[0].detach().clone() for l in LAYERS}
        xs = {l: cap.mlp_in[l].detach() for l in LAYERS}
        hs = {l: cap.mlp_out[l].detach() for l in LAYERS}
    del lg, ce, emb, cap
    order = torch.argsort(base_ce[first:])
    q = max(1, len(order) // 4)
    rng = random.Random(a.seed * 7919 + len(ids))
    toks = [first + int(i) for i in rng.sample(order[-q:].tolist(), min(a.n_tok, q))]
    K = model.config.num_experts_per_tok
    out = []
    for l in LAYERS:
        moe = model.model.layers[l].mlp
        for t in toks:
            z, U, p0, r2 = potential(moe, xs[l][0, t], hs[l][0, t], g[l][t], K, a.m)
            # z must live on the SAME shard as p0: with device_map the trained
            # layers sit on the second card, not on dev0.
            p0 = p0.detach()
            out.append((l, t, torch.tensor(z, device=p0.device, dtype=torch.float32),
                        U, p0, r2))
    return dict(ids=ids, input_ids=input_ids, targets=targets, first=first,
                items=out, xs={l: xs[l].detach() for l in LAYERS})


def calibrate(model, tok, data, a, dev0):
    """Fix delta by a training-free ladder, then beta_l by median target KL."""
    cal = []
    for ex in data[:a.n_calib]:
        r = iter_tokens(model, tok, ex, a, dev0)
        if r:
            cal += [(l, z, U, p0) for l, _, z, U, p0, _ in r["items"]]
        torch.cuda.empty_cache()
    rep = {"ladder": {}, "beta": {}, "n_calib_tokens": len(cal)}
    # FROZEN SELECTION RULE (docs/CPD_V1_DESIGN.md): take the SMALLEST delta for
    # which both layers' top-8 change fraction lands in [0.15, 0.35] AND the mean
    # number of experts changed per token stays <= 1.0. C0's 3-5/8 wholesale
    # rerouting is exactly the generic-perturbation regime to avoid; CPD should
    # look like a small, directed correction.
    for d in LADDER_GRID:
        cell = {}
        for l in LAYERS:
            sub = [(z, U, p0) for ll, z, U, p0 in cal if ll == l]
            if not sub:
                continue
            b = solve_beta(sub, d, median=True)
            ch, nch, kls = [], [], []
            for z, U, p0 in sub:
                q = cpd_target(p0, U, z, b)
                t0 = set(torch.topk(p0, 8).indices.tolist())
                t1 = set(torch.topk(q, 8).indices.tolist())
                ch.append(float(t0 != t1)); nch.append(len(t1 - t0))
                kls.append(kl_to_base(p0, U, z, b))
            cell[str(l)] = dict(
                beta=b, changed_frac=float(np.mean(ch)),
                mean_experts_changed=float(np.mean(nch)),
                experts_changed_given_changed=float(
                    np.mean([n for n, c in zip(nch, ch) if c > 0]) if any(ch) else 0.0),
                kl_median=float(np.median(kls)), kl_p90=float(np.percentile(kls, 90)))
        rep["ladder"][str(d)] = cell

    chosen = None
    for d in LADDER_GRID:
        c = rep["ladder"][str(d)]
        if all(0.15 <= c[str(l)]["changed_frac"] <= 0.35
               and c[str(l)]["mean_experts_changed"] <= 1.0 for l in LAYERS):
            chosen = d
            break
    rep["delta_rule"] = "smallest delta with changed_frac in [0.15,0.35] and mean_experts_changed <= 1.0 on BOTH layers"
    rep["delta_auto"] = chosen
    delta = a.delta if a.delta > 0 else chosen
    if delta is None:
        # Persist the ladder BEFORE failing -- the whole point of the rule is to
        # make the decision inspectable, which is impossible if the data dies
        # with the process.
        json.dump(rep, open(a.calib_out + ".ladder_only.json", "w"), indent=1)
        raise SystemExit("LADDER: no delta satisfies the frozen rule; wrote "
                         + a.calib_out + ".ladder_only.json for inspection")
    rep["delta"] = delta
    for l in LAYERS:
        sub = [(z, U, p0) for ll, z, U, p0 in cal if ll == l]
        rep["beta"][str(l)] = solve_beta(sub, delta, median=True)
    return rep


def solve_beta(items, delta, median=False, lo=1e-4, hi=1e4, it=40):
    def f(b):
        v = [kl_to_base(p0, U, z, b) for z, U, p0 in items]
        return float(np.median(v)) if median else v[0]
    if f(hi) < delta:
        return hi
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(mid) < delta:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main(a):
    torch.manual_seed(a.seed); random.seed(a.seed)
    tok, model = load(a)
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.train_pool))["items"]
    gates = [model.model.layers[l].mlp.gate for l in LAYERS]
    base_w = [g.weight.detach().clone() for g in gates]

    if a.arm != "router_ce":
        if os.path.exists(a.calib_out):
            cal = json.load(open(a.calib_out))
        else:
            for g in gates:
                g.weight.requires_grad_(False)
            cal = calibrate(model, tok, pool, a, dev0)
            json.dump(cal, open(a.calib_out, "w"), indent=1)
        print("CALIB", json.dumps(cal), flush=True)
        beta = {l: cal["beta"][str(l)] for l in LAYERS}

    for g in gates:
        g.weight.requires_grad_(True)
    opt = torch.optim.AdamW([g.weight for g in gates], lr=a.lr, weight_decay=0.0)
    log = open(a.log_out, "w"); step = 0; t0 = time.time()

    for ex in pool[a.n_calib:]:
        if step >= a.steps:
            break
        if a.arm == "router_ce":
            prompt = tok.apply_chat_template(
                [{"role": "user", "content": ex["problem"]}], tokenize=False,
                add_generation_prompt=True, enable_thinking=False)
            p_ids = tok(prompt, add_special_tokens=False).input_ids
            s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
            ids = p_ids + s_ids
            if len(ids) > a.max_len or len(s_ids) < 24:
                continue
            ii = torch.tensor([ids], device=dev0)
            tg = ii[0, 1:]
            lg = model(ii, use_cache=False).logits
            loss = F.cross_entropy(lg[0, len(p_ids) - 1:-1].float(),
                                   tg[len(p_ids) - 1:].to(lg.device))
            opt.zero_grad(set_to_none=True); loss.backward()
            gn = torch.nn.utils.clip_grad_norm_([g.weight for g in gates], a.clip)
            opt.step(); step += 1
            rec = dict(step=step, loss=float(loss), grad_norm=float(gn))
        else:
            r = iter_tokens(model, tok, ex, a, dev0)
            if r is None:
                continue
            opt.zero_grad(set_to_none=True)
            tot, kls, n = 0.0, [], 0
            feas_n, kl_resid, star_rank = [], [], []
            loss_sum = None
            rng = np.random.default_rng(a.seed * 31 + step)
            for l, t, z, U, p0, r2 in r["items"]:
                b = beta[l]
                if a.arm == "shuffled":
                    klt = kl_to_base(p0, U, z, b)
                    q, nf, star, c, ach = shuffled_target(p0, U, z, b, klt, rng)
                    q = q.detach()
                    feas_n.append(nf); kl_resid.append(abs(ach - klt))
                    star_rank.append(int((p0 > p0[U[star]]).sum()))
                else:
                    q = cpd_target(p0, U, z, b).detach()
                gi = LAYERS.index(l)
                gw = gates[gi].weight
                s = gates[gi](r["xs"][l][0, t].to(gw.device)).float()
                q = q.to(gw.device)
                lp = F.log_softmax(s, -1)
                lcpd = (q * (q.clamp_min(1e-12).log() - lp)).sum()
                loss_sum = lcpd if loss_sum is None else loss_sum + lcpd
                tot += float(lcpd.detach()); kls.append(kl_to_base(p0, U, z, b)); n += 1
            if loss_sum is None:
                continue
            (loss_sum / n).backward()
            gn = torch.nn.utils.clip_grad_norm_([g.weight for g in gates], a.clip)
            opt.step(); step += 1
            rec = dict(step=step, loss=tot / n, n_tok=n,
                       median_target_kl=float(np.median(kls)), grad_norm=float(gn),
                       shuf_feasible_n=float(np.mean(feas_n)) if feas_n else None,
                       shuf_kl_resid=float(np.max(kl_resid)) if kl_resid else 0.0,
                       shuf_star_base_rank=float(np.mean(star_rank)) if star_rank else None)
        rec["drift"] = [float((g.weight.detach() - bw).norm() / bw.norm())
                        for g, bw in zip(gates, base_w)]
        rec["elapsed"] = time.time() - t0
        log.write(json.dumps(rec) + "\n"); log.flush()
        if step % a.print_every == 0 or step <= 3:
            print(f"[{step}/{a.steps}] {a.arm} loss={rec['loss']:.4f} "
                  f"drift={[round(d,4) for d in rec['drift']]} "
                  f"{rec['elapsed']:.0f}s", flush=True)
        torch.cuda.empty_cache()

    torch.save({str(l): g.weight.detach().cpu() for l, g in zip(LAYERS, gates)},
               a.ckpt_out)
    json.dump(dict(arm=a.arm, steps=step, lr=a.lr,
                   drift={str(l): float((g.weight.detach() - bw).norm() / bw.norm())
                          for l, g, bw in zip(LAYERS, gates, base_w)}),
              open(a.ckpt_out + ".meta.json", "w"), indent=1)
    log.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="cpd", choices=["cpd", "shuffled", "router_ce"])
    ap.add_argument("--train-pool", dest="train_pool", default="results/cpd_trainpool.json")
    ap.add_argument("--calib-out", dest="calib_out", default="results/cpd_calib.json")
    ap.add_argument("--ckpt-out", dest="ckpt_out", default="results/cpd_router.pt")
    ap.add_argument("--log-out", dest="log_out", default="results/cpd_train.jsonl")
    ap.add_argument("--delta", type=float, default=-1.0,
                    help="-1 = use the frozen ladder rule")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--clip", type=float, default=1.0)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=8)
    ap.add_argument("--n-calib", dest="n_calib", type=int, default=12)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--print-every", dest="print_every", type=int, default=20)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
