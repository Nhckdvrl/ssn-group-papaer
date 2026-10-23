"""E120: validate MoE-organisation measures on synthetic routers with known answers.

Usage: e120_synth.py [--quick]
Writes results/e120/summary.json.
"""
import json
import math
import sys
import time

import numpy as np
import scipy.linalg as sla
import torch

import moe_measure as mm

torch.set_default_dtype(torch.float64)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
QUICK = "--quick" in sys.argv
OUT = __import__("pathlib").Path(__file__).resolve().parents[1] / "results" / "e120"
OUT.mkdir(parents=True, exist_ok=True)

D, L, E = 128, 32, 16
N_ANCHOR, N_CAL = (400, 2000) if QUICK else (800, 4000)
M_DRAWS = 16 if QUICK else 32
N_NULL_REPS = 10 if QUICK else 30
KS = [int(a.split("=")[1]) for a in sys.argv if a.startswith("--k=")] or [1, 2, 4]


def make_data(seed):
    g = np.random.default_rng(seed)
    basis = np.linalg.qr(g.standard_normal((D, L)))[0]  # D x L
    scales = np.geomspace(4.0, 0.5, L)
    means = g.standard_normal((8, L)) * 2.5
    sds = np.sqrt(g.uniform(0.3, 1.2, (8, L)))

    def sample(n):
        c = g.integers(0, 8, n)
        z = means[c] + g.standard_normal((n, L)) * sds[c]
        h = (z * scales) @ basis.T + 0.1 * g.standard_normal((n, D))
        return torch.tensor(h, device=DEV), c

    return basis, sample


def router_on(basis, sub, g):
    """Random router reading the latent sub-space `sub` (L x 15 orthonormal) of the data span."""
    R = g.standard_normal((E, sub.shape[1]))
    return torch.tensor(R @ sub.T @ basis.T, device=DEV)  # E x D


def orth_sub(g, m_shared=None, ref=None):
    if ref is None:
        return np.linalg.qr(g.standard_normal((L, 15)))[0]
    # share m dims with ref, the rest orthogonal to ref
    P = np.eye(L) - ref @ ref.T
    comp = np.linalg.qr(P @ g.standard_normal((L, L)))[0][:, : L - 15]
    keep = ref @ np.linalg.qr(g.standard_normal((15, m_shared)))[0] if m_shared else np.zeros((L, 0))
    rest = comp @ np.linalg.qr(g.standard_normal((comp.shape[1], 15 - m_shared)))[0]
    return np.linalg.qr(np.concatenate([keep, rest], 1))[0]


def residual(W, b, Hc, Ha, k, kind, pairs, seed):
    S = mm.topk(Ha @ W.T + b, k)
    C = mm.coroute(S, E, k, pairs)
    ne = mm.null_expectation(W, b, Hc, Ha, k, kind, M_DRAWS, seed, pairs)
    return C, C - ne["B"], ne["load_tv"]


_CACHE = {}


def compare(WA, bA, HcA, HaA, WB, bB, HcB, HaB, k, pairs, seed):
    out = {}
    zA, zB = HaA @ WA.T + bA, HaB @ WB.T + bB
    SA, SB = mm.topk(zA, k), mm.topk(zB, k)
    out["cca_rho2"], out["cca_rank"] = mm.cca_mean_rho2(zA, zB)
    out["cka"] = mm.linear_cka(zA, zB)
    out["nmi_top1"] = mm.nmi(SA[:, 0].cpu().numpy(), SB[:, 0].cpu().numpy())
    CA, CB = mm.coroute(SA, E, k, pairs), mm.coroute(SB, E, k, pairs)
    out["corr_C"] = mm.corr(CA, CB)
    for kind in ("N1", "N2"):
        key = (k, kind, id(WA), id(HaA))
        if key not in _CACHE:
            _CACHE[key] = residual(WA, bA, HcA, HaA, k, kind, pairs, 7)
        _, DA, tvA = _CACHE[key]
        _, DB, tvB = residual(WB, bB, HcB, HaB, k, kind, pairs, seed + 1)
        out[f"T_{kind}"] = mm.corr(DA, DB)
        out[f"normD_{kind}"] = [float(DA.std()), float(DB.std())]
        out[f"loadTV_{kind}"] = [tvA, tvB]
    return out


def balanced(W, Hc, k):
    tgt = torch.ones(E, device=DEV)
    return mm.fit_bias(Hc, W, k, tgt)


def main():
    t0 = time.time()
    basis, sample = make_data(0)
    Hc, _ = sample(N_CAL)
    Ha, ca = sample(N_ANCHOR)
    pairs = mm.upper_pairs(N_ANCHOR, DEV)
    g = np.random.default_rng(1)
    subA = orth_sub(g)
    WA = router_on(basis, subA, g)
    res = {"config": {"D": D, "L": L, "E": E, "N_anchor": N_ANCHOR, "N_cal": N_CAL, "M_draws": M_DRAWS}}
    for k in KS:
        bA = balanced(WA, Hc, k)
        R = {}
        # S0 label permutation (independent null draws -> finite-M ceiling)
        perm = torch.tensor(g.permutation(E), device=DEV)
        R["S0_perm"] = compare(WA, bA, Hc, Ha, WA[perm], bA[perm], Hc, Ha, k, pairs, 10)
        # S1 invertible logit mixing: z_B = z_A A  (same logit subspace, different top-k)
        A = torch.tensor(g.standard_normal((E, E)), device=DEV)
        WB = A.T @ WA
        R["S1_logit_mix"] = compare(WA, bA, Hc, Ha, WB, balanced(WB, Hc, k), Hc, Ha, k, pairs, 20)
        # S2 rotation inside the readout sub-space, increasing angle
        U, S, V = mm.readout(WA)
        Kr = g.standard_normal((V.shape[1], V.shape[1]))
        Kr = (Kr - Kr.T) / np.linalg.norm(Kr - Kr.T, 2)
        for t in (0.05, 0.1, 0.2, 0.5, 1.0, 2.0):
            Qt = torch.tensor(sla.expm(t * Kr), device=DEV)
            WB = (U * S) @ Qt @ V.T
            R[f"S2_rot_{t}"] = compare(WA, bA, Hc, Ha, WB, balanced(WB, Hc, k), Hc, Ha, k, pairs, 30)
        # S3 / S4 different or partially shared features
        for m in (0, 4, 8, 12):
            subB = orth_sub(g, m, subA)
            WB = router_on(basis, subB, g)
            R[f"S4_shared_{m}of15"] = compare(WA, bA, Hc, Ha, WB, balanced(WB, Hc, k), Hc, Ha, k, pairs, 40 + m)
        # S6 representation re-parametrisation: H_B = H_A M^T, W_B = W_A M^{-1}  (identical routing)
        Mo = np.linalg.qr(g.standard_normal((D, D)))[0] @ np.diag(np.geomspace(3.0, 0.3, D)) @ np.linalg.qr(g.standard_normal((D, D)))[0]
        Mt = torch.tensor(Mo, device=DEV)
        HcB, HaB = Hc @ Mt.T, Ha @ Mt.T
        WB = WA @ torch.linalg.inv(Mt)
        r6 = compare(WA, bA, Hc, Ha, WB, bA, HcB, HaB, k, pairs, 60)
        Qp = mm.procrustes(Hc, HcB)
        r6["procrustes_transfer_overlap"] = mm.topk_overlap(mm.topk(Ha @ WA.T + bA, k), mm.topk((HaB @ Qp) @ WA.T + bA, k), k)
        r6["identical_routing_check"] = mm.topk_overlap(mm.topk(Ha @ WA.T + bA, k), mm.topk(HaB @ WB.T + bA, k), k)
        R["S6_reparam"] = r6
        # S5 null distribution of T: B is itself a null draw of A
        for kind in ("N1", "N2"):
            st = mm.null_stats(WA, Hc)
            gen = torch.Generator().manual_seed(500)
            Ts = []
            _, DA, _ = residual(WA, bA, Hc, Ha, k, kind, pairs, 70)
            for rep in range(N_NULL_REPS):
                Wn = mm.null_router(WA, Hc, kind, mm.haar(st["V"].shape[1], gen).to(DEV), st)
                bn = mm.fit_bias(Hc, Wn, k, mm.loads(mm.topk(Hc @ WA.T + bA, k), E))
                _, DB, _ = residual(Wn, bn, Hc, Ha, k, kind, pairs, 100 + rep)
                Ts.append(mm.corr(DA, DB))
            R[f"S5_null_T_{kind}"] = {"mean": float(np.mean(Ts)), "q025": float(np.quantile(Ts, 0.025)), "q975": float(np.quantile(Ts, 0.975)), "n": len(Ts)}
        res[f"k{k}"] = R
        print(f"k={k} done {time.time()-t0:.0f}s", flush=True)
    if 2 in KS:
        res["S7_circle"] = circle()
        res["S8_swap"] = swap_test()
    tag = "_".join(map(str, KS))
    (OUT / (f"summary_k{tag}" + ("_quick" if QUICK else "") + ".json")).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1)[:6000])


def circle(n=4000, Ecirc=64, seed=0):
    """64 sectors vs. half-sector shift; exact phase-rotation null B = max(0, 1 - dtheta/w)."""
    g = np.random.default_rng(seed)
    th = np.sort(g.uniform(0, 2 * np.pi, n))
    w = 2 * np.pi / Ecirc
    a = np.floor(th / w).astype(int) % Ecirc
    bsec = np.floor((th + w / 2) / w).astype(int) % Ecirc
    i, j = np.triu_indices(n, 1)
    d = np.abs(th[i] - th[j])
    d = np.minimum(d, 2 * np.pi - d)
    Bnull = np.maximum(0, 1 - d / w)
    CA, CB = (a[i] == a[j]).astype(float), (bsec[i] == bsec[j]).astype(float)
    DA, DB = CA - Bnull, CB - Bnull
    near = d < w  # pairs with non-zero null variance
    return {"nmi": mm.nmi(a, bsec), "nmi_theory": 5 / 6, "corr_C": float(np.corrcoef(CA, CB)[0, 1]), "corr_C_theory": 31 / 63,
            "corr_D_all": float(np.corrcoef(DA, DB)[0, 1]), "corr_D_near": float(np.corrcoef(DA[near], DB[near])[0, 1]), "corr_D_theory": -0.5}


def swap_test(seed=0, k=2, n=3000):
    """Synthetic MoE output y = sum_{e in S} g_e G_e h. Target = original output + noise.
    A(e->j): replace the rank-1 expert by the rank-(k+1) expert with the same gate; mean clamp: replace G_e h by its routed mean."""
    g = np.random.default_rng(seed)
    basis, sample = make_data(5)
    H, _ = sample(n)
    sub = orth_sub(g)
    W = router_on(basis, sub, g)
    b = mm.fit_bias(H, W, k, torch.ones(E, device=DEV))
    z = H @ W.T + b
    order = z.argsort(-1, descending=True)
    gate = torch.softmax(z, -1)
    out = {}
    base = torch.tensor(g.standard_normal((D, D)) / math.sqrt(D), device=DEV)
    for name, deltas in (("identical", 0.0), ("specialised", 1.0)):
        G = [base + deltas * torch.tensor(g.standard_normal((D, D)) / math.sqrt(D), device=DEV) for _ in range(E)]
        F = torch.stack([H @ Ge.T for Ge in G], 1)  # n x E x D  expert outputs
        sel = order[:, :k]
        gsel = gate.gather(1, sel)

        def outp(sel_, Fsub=None):
            Fx = F.gather(1, sel_[:, :, None].expand(-1, -1, D)) if Fsub is None else Fsub
            return (gsel[:, :, None] * Fx).sum(1)

        y = outp(sel)
        tgt = y + 0.05 * torch.tensor(g.standard_normal(tuple(y.shape)), device=DEV)
        loss0 = ((y - tgt) ** 2).sum(1)
        sel_swap = sel.clone()
        sel_swap[:, 0] = order[:, k]
        A = ((outp(sel_swap) - tgt) ** 2).sum(1) - loss0
        mu = torch.stack([F[(sel[:, 0] == e), e].mean(0) if (sel[:, 0] == e).any() else torch.zeros(D, device=DEV) for e in range(E)])
        Fx = F.gather(1, sel[:, :, None].expand(-1, -1, D)).clone()
        Fx[:, 0] = mu[sel[:, 0]]
        clamp = ((outp(sel, Fx) - tgt) ** 2).sum(1) - loss0
        selfswap = ((outp(sel) - tgt) ** 2).sum(1) - loss0
        out[name] = {"A_runner_up_mean": float(A.mean()), "mean_clamp_mean": float(clamp.mean()), "self_swap_max_abs": float(selfswap.abs().max()),
                     "loss0_mean": float(loss0.mean())}
    return out


if __name__ == "__main__":
    main()
