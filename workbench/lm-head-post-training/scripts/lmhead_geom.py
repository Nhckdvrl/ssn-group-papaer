"""Geometry of the LM head W (V x d): column-space projection, gain, leverage, subspace angles.

Conventions (RESEARCH_PLAN.md §3):
  W = U Σ Rᵀ (thin SVD).  For a logit-space vector g ∈ R^V:
    g_h   = Wᵀ g                                  (what reaches the final hidden state)
    ρ(g)  = ‖U_rᵀ g‖² / ‖g‖² = ‖Σ_r⁻¹ R_rᵀ g_h‖² / ‖g‖²   (projection energy, in [0,1])
    γ(g)  = ‖Wᵀ g‖ / ‖g‖                           (gain, includes singular values)
  U is never materialised: we keep R, σ from the FP64 Gram G = WᵀW.
  Leverage of token row a:  ℓ_a = ‖U[a]‖² = ‖Σ⁻¹ Rᵀ w_a‖²,  Σ_a ℓ_a = rank.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import torch


@dataclass
class HeadBasis:
    R: torch.Tensor        # d x r, float64, right singular vectors kept
    sigma: torch.Tensor    # r, float64, descending
    rank: int
    d: int
    V: int
    rel_tol: float
    sigma_all: torch.Tensor  # d, float64 (sqrt of clamped Gram eigenvalues, descending)
    neg_eigs: int            # number of negative Gram eigenvalues before clamping (diagnostic)

    def to(self, device):
        self.R = self.R.to(device)
        self.sigma = self.sigma.to(device)
        return self


def gram(W: torch.Tensor, chunk: int = 16384, device=None) -> torch.Tensor:
    """G = WᵀW accumulated in FP64 over row chunks (W may live on CPU in bf16)."""
    device = device or W.device
    d = W.shape[1]
    G = torch.zeros(d, d, dtype=torch.float64, device=device)
    for i in range(0, W.shape[0], chunk):
        blk = W[i:i + chunk].to(device=device, dtype=torch.float64)
        G += blk.T @ blk
    return G


def head_basis(W: torch.Tensor, rel_tol: float = 1e-6, device=None, G: torch.Tensor | None = None) -> HeadBasis:
    """Right singular basis of W from the FP64 Gram. rel_tol is on singular values (σ/σ_max)."""
    if G is None:
        G = gram(W, device=device)
    evals, evecs = torch.linalg.eigh(G)          # ascending
    evals, evecs = evals.flip(0), evecs.flip(1)
    neg = int((evals < 0).sum())
    sig_all = evals.clamp_min(0).sqrt()
    keep = sig_all > rel_tol * sig_all[0]
    r = int(keep.sum())
    return HeadBasis(R=evecs[:, :r].contiguous(), sigma=sig_all[:r].contiguous(), rank=r,
                     d=W.shape[1], V=W.shape[0], rel_tol=rel_tol, sigma_all=sig_all, neg_eigs=neg)


def rho_gamma_from_gh(g_h: torch.Tensor, g_norm2: torch.Tensor, basis: HeadBasis):
    """Given g_h = Wᵀ g (n x d) and ‖g‖² (n), return ρ, γ (n). Zero-norm rows -> NaN (undefined)."""
    gh64 = g_h.to(torch.float64)
    coef = (gh64 @ basis.R) / basis.sigma            # = U_rᵀ g
    proj2 = (coef ** 2).sum(-1)
    gh2 = (gh64 ** 2).sum(-1)
    g2 = g_norm2.to(torch.float64)
    bad = g2 <= 0
    rho = torch.where(bad, torch.nan, proj2 / g2.clamp_min(1e-300))
    gamma = torch.where(bad, torch.nan, (gh2 / g2.clamp_min(1e-300)).sqrt())
    return rho, gamma


def rho_gamma(g: torch.Tensor, W: torch.Tensor, basis: HeadBasis):
    """Direct version for explicit logit-space vectors g (n x V)."""
    g_h = g.to(torch.float64) @ W.to(torch.float64)
    return rho_gamma_from_gh(g_h, (g.to(torch.float64) ** 2).sum(-1), basis)


def leverage(W: torch.Tensor, basis: HeadBasis, chunk: int = 16384) -> torch.Tensor:
    """ℓ_a = ‖Σ⁻¹ Rᵀ w_a‖² for every row (V,), float64."""
    out = torch.empty(W.shape[0], dtype=torch.float64, device=basis.R.device)
    for i in range(0, W.shape[0], chunk):
        blk = W[i:i + chunk].to(device=basis.R.device, dtype=torch.float64)
        out[i:i + chunk] = (((blk @ basis.R) / basis.sigma) ** 2).sum(-1)
    return out


def stable_ce_terms(z: torch.Tensor, targets: torch.Tensor, W: torch.Tensor):
    """Numerically stable CE logit-gradient pieces for logits z (n x V, fp32) and targets (n).
    ‖p - e_a‖² = (1-p_a)² + Σ_{j≠a} p_j²  and  Wᵀ(p - e_a) = Σ_{j≠a} p_j w_j - (1-p_a) w_a,
    with 1-p_a = -expm1(log p_a); avoids the cancellation of Σp² - 2p_a + 1 when p_a → 1."""
    logp = torch.log_softmax(z.float(), dim=-1)
    p = logp.exp()
    n = z.shape[0]
    idx = torch.arange(n, device=z.device)
    lp_a = z[idx, targets].double() - torch.logsumexp(z.double(), dim=-1)   # FP64 normaliser for the target
    one_m = -torch.expm1(lp_a)                              # 1 - p_a, accurate near 1
    p_off = p.clone()
    p_off[idx, targets] = 0.0
    g_norm2 = one_m ** 2 + (p_off.double() ** 2).sum(-1)
    Wf = W.float() if W.dtype != torch.float32 else W
    g_h = p_off @ Wf - one_m.float()[:, None] * Wf[targets]
    ent = -(p * logp).sum(-1)
    return p, logp, lp_a, g_h, g_norm2, ent


def ce_logit_grad_stats(logits: torch.Tensor, targets: torch.Tensor, W: torch.Tensor, coef: torch.Tensor | None = None):
    """For per-position logits (n x V) and target ids (n), the CE logit gradient g = c (p - e_a).
    Returns g_h = Wᵀ g (n x d), ‖g‖² (n, fp64), p_a and entropy (stable formulas, see stable_ce_terms)."""
    p, logp, lp_a, g_h, g_norm2, ent = stable_ce_terms(logits, targets, W)
    if coef is not None:
        c = coef.to(logits.device).float()
        g_h = g_h * c[:, None]
        g_norm2 = g_norm2 * c.double() ** 2
    return g_h, g_norm2, lp_a.exp(), ent


def subspace_cosines(W0: torch.Tensor, W1: torch.Tensor, b0: HeadBasis, b1: HeadBasis, device=None) -> torch.Tensor:
    """Cosines of principal angles between col(W0) and col(W1) (descending).
    U0ᵀU1 = Σ0⁻¹ R0ᵀ (W0ᵀ W1) R1 Σ1⁻¹ ; needs only the d x d cross-Gram."""
    device = device or b0.R.device
    d = W0.shape[1]
    C = torch.zeros(d, d, dtype=torch.float64, device=device)
    for i in range(0, W0.shape[0], 16384):
        C += W0[i:i + 16384].to(device, torch.float64).T @ W1[i:i + 16384].to(device, torch.float64)
    M = (b0.R.T @ C @ b1.R) / b0.sigma[:, None] / b1.sigma[None, :]
    return torch.linalg.svdvals(M).clamp(max=1.0)


def effective_rank(sv: torch.Tensor) -> dict:
    """Entropy effective rank exp(-Σ q log q), q = σ²/Σσ²; stable rank Σσ²/σ_max²."""
    s2 = sv.double() ** 2
    tot = s2.sum()
    if tot <= 0:
        return {"erank": math.nan, "stable_rank": math.nan}
    q = s2 / tot
    q = q[q > 0]
    return {"erank": float(torch.exp(-(q * q.log()).sum())), "stable_rank": float(tot / s2.max())}
