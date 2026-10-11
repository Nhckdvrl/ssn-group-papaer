"""CT03 Fixed-Support v2 -- did the router learn the counterfactual DIRECTION?

The mechanism metric in CPD_V1_DESIGN was mis-specified. CPD learns
s_theta ~= s_0 + beta*z, and s_0's own pairwise differences are known to be
uncorrelated with utility (base A_fixed ~ 0). With a small trust region the
large, utility-irrelevant s_0 term dominates s_theta, so A_fixed can stay near
zero even if the correction is perfectly aligned. A_fixed therefore cannot
adjudicate the mechanism.

What can is the CORRECTION direction:

    A_delta = rho( (s_theta_j - s_theta_i) - (s_0_j - s_0_i),  u_exact_ij )
    A_z     = rho( gauge-centred (s_theta_e - s_0_e) on U,     z*_exact_e )

since the target literally is  delta_s_e ~ beta * z_e.

Everything is measured on one frozen support: base-model tokens, base hidden
states, base candidate universe, exact utilities computed once. L28 is included
as an UNTRAINED control layer -- no arm touched it, so any A_delta there is a
readout of the measurement's own noise floor.
"""

import argparse, json, random, sys
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e02_qwen import Capture, load, route_of, swap_dh, replay_ce
from e035_integrability import fit_potentials
from e01_report import spearman

LAYERS = [28, 36, 44]          # 28 = untrained control
TRAINED = [36, 44]


def mix(moe, x, ids, p):
    Z = float(p[ids].sum())
    return sum(moe.experts[e](x) * (float(p[e]) / Z) for e in ids)


def main(a):
    tok, model = load(a)
    K = model.config.num_experts_per_tok
    dev0 = next(model.parameters()).device
    pool = json.load(open(a.pool))["items"][:a.n_problems]

    gates = {l: model.model.layers[l].mlp.gate for l in LAYERS}
    base_w = {l: gates[l].weight.detach().clone() for l in LAYERS}
    arms = {"base": None}
    for spec in a.ckpts.split(","):
        if spec:
            t, p = spec.split(":", 1)
            arms[t] = torch.load(p, map_location="cpu")
    print("arms:", list(arms), flush=True)

    rows = []
    for pi, ex in enumerate(pool):
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        if len(ids) > a.max_len or len(s_ids) < 24:
            continue
        for l in LAYERS:                       # base defines the whole support
            gates[l].weight.data.copy_(base_w[l])
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
                p0 = F.softmax(F.linear(x, base_w[l]).float(), -1)
                rank = torch.argsort(p0, descending=True)
                S0, C0 = rank[:K].tolist(), rank[K:K + a.m].tolist()
                U = S0 + C0
                s0 = F.linear(x, base_w[l]).float()

                pairs, dhs = [], []
                for i in S0:
                    for j in C0:
                        d, _ = swap_dh(moe, x, h, p0, i, j, float(p0[S0].sum()))
                        pairs.append((i, j)); dhs.append(d)
                # exact utilities and their potential, computed ONCE on base state
                H = lo[l].expand(len(pairs) + 1, -1, -1).clone()
                H[1:, t] += torch.stack(dhs)
                for tag in arms:                       # routes need each arm's gate
                    pass
                allce = replay_ce(model, l, H, t, targets, **akw)
                dL = (allce[1:] - allce[0]).sum(dim=1).cpu().numpy()
                u = {(i, j): -float(v) for (i, j), v in zip(pairs, dL)}
                ze, idx, r2e, _, _ = fit_potentials([(i, j, u[(i, j)]) for i, j in pairs])
                z_ex = np.array([ze[idx[e]] for e in U])

                # each arm's route, replayed on the SAME base state
                pat, meta = [], []
                for tag, sd in arms.items():
                    if tag == "base":
                        continue
                    w = sd[str(l)].to(x.device) if str(l) in sd else base_w[l]
                    s = F.linear(x, w).float()
                    sU = sorted(U, key=lambda e: -float(s[e]))[:K]
                    pat.append(mix(moe, x, sU, F.softmax(s, -1)) - h)
                    meta.append((tag, "armw", sU))
                    pat.append(mix(moe, x, sU, p0) - h)
                    meta.append((tag, "basew", sU))
                if pat:
                    H2 = lo[l].expand(len(pat) + 1, -1, -1).clone()
                    H2[1:, t] += torch.stack(pat)
                    c2 = replay_ce(model, l, H2, t, targets, **akw)
                    dv = (c2[1:] - c2[0]).sum(dim=1).cpu().numpy()
                else:
                    dv = []

                for tag, sd in arms.items():
                    w = base_w[l] if sd is None else (
                        sd[str(l)].to(x.device) if str(l) in sd else base_w[l])
                    s = F.linear(x, w).float()
                    ds = (s - s0)
                    dsU = ds[U].cpu().numpy()
                    dsU = dsU - dsU.mean()                    # gauge
                    sd_pair = [float(s[j] - s[i]) for i, j in pairs]
                    s0_pair = [float(s0[j] - s0[i]) for i, j in pairs]
                    uv = [u[(i, j)] for i, j in pairs]
                    kl = float((F.softmax(s0, -1) *
                                (F.log_softmax(s0, -1) - F.log_softmax(s, -1))).sum())
                    r = dict(pi=pi, layer=l, pos=t, arm=tag, r2_exact=r2e,
                             A_delta=spearman([a_ - b_ for a_, b_ in zip(sd_pair, s0_pair)], uv),
                             A_z=spearman(dsU.tolist(), z_ex.tolist()),
                             A_fixed=spearman(sd_pair, uv),
                             realized_kl=kl,
                             n_changed=len(set(sorted(U, key=lambda e: -float(s[e]))[:K])
                                           - set(S0)))
                    for (tg, kind, _), v in zip(meta, dv):
                        if tg == tag:
                            r["V_" + kind] = float(v)
                    rows.append(r)
        torch.cuda.empty_cache()
        print(f"  [{pi+1}/{len(pool)}] done", flush=True)

    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    report(rows)


def report(rows):
    arms = ["base", "router_ce", "shuffled", "cpd"]
    arms = [a for a in arms if any(r["arm"] == a for r in rows)]
    print("\n" + "=" * 96)
    print("A_delta = rho(learned score CORRECTION, exact utility)   [L28 is UNTRAINED control]")
    print(f"{'arm':>11}" + "".join(f"{'A_d L'+str(l):>12}" for l in LAYERS)
          + "".join(f"{'A_z L'+str(l):>12}" for l in LAYERS))
    for a in arms:
        line = f"{a:>11}"
        for key in ("A_delta", "A_z"):
            for l in LAYERS:
                v = [r[key] for r in rows if r["arm"] == a and r["layer"] == l
                     and not np.isnan(r[key])]
                line += f"{np.median(v):>12.3f}" if v else f"{'-':>12}"
        print(line)

    print("\nV_route (negative = better than the base route on the SAME base state)")
    print(f"{'arm':>11}{'variant':>9}" + "".join(f"{'L'+str(l):>11}" for l in LAYERS)
          + f"{'realizedKL':>12}{'n_chg':>7}")
    for a in arms:
        for kind in ("armw", "basew"):
            k = "V_" + kind
            if not any(k in r and r["arm"] == a for r in rows):
                continue
            line = f"{a:>11}{kind:>9}"
            for l in LAYERS:
                v = [r[k] for r in rows if r["arm"] == a and r["layer"] == l and k in r]
                line += f"{np.mean(v):>11.4f}" if v else f"{'-':>11}"
            kl = [r["realized_kl"] for r in rows if r["arm"] == a]
            nc = [r["n_changed"] for r in rows if r["arm"] == a]
            print(line + f"{np.mean(kl):>12.2e}{np.mean(nc):>7.2f}")

    rng = np.random.default_rng(0)
    print("\nPaired bootstrap on V_route (armw), trained layers only:")
    for x, y in (("cpd", "router_ce"), ("cpd", "shuffled")):
        if x not in arms or y not in arms:
            continue
        for l in TRAINED:
            A = {(r["pi"], r["pos"]): r["V_armw"] for r in rows
                 if r["arm"] == x and r["layer"] == l and "V_armw" in r}
            B = {(r["pi"], r["pos"]): r["V_armw"] for r in rows
                 if r["arm"] == y and r["layer"] == l and "V_armw" in r}
            ks = sorted(set(A) & set(B))
            if not ks:
                continue
            d = np.array([A[k] - B[k] for k in ks])
            bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(10000)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            print(f"  L{l} {x}-{y}: {d.mean():+.4f}  CI [{lo:+.4f},{hi:+.4f}]"
                  f"  {'SIG' if (lo>0 or hi<0) else 'ns'}  n={len(ks)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="results/fg0_devpool.json")
    ap.add_argument("--ckpts", default="router_ce:results/cpd_router_router_ce.pt,"
                                       "shuffled:results/cpd_router_shuffled.pt,"
                                       "cpd:results/cpd_router_cpd.pt")
    ap.add_argument("--out", default="results/e04_fixed_v2.jsonl")
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=24)
    ap.add_argument("--n-tok", dest="n_tok", type=int, default=8)
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--n-gpu", dest="n_gpu", type=int, default=2)
    ap.add_argument("--mem-per-gpu", dest="mem_per_gpu", type=int, default=78)
    ap.add_argument("--seed", type=int, default=0)
    main(ap.parse_args())
