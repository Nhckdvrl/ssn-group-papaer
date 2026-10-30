"""Measurement library for MoE routing organization (E120 synthetic validation, E121 OLMoE).

Conventions
-----------
H : (N, d) router inputs (rows = inputs).  W : (E, d) router weight.  b : (E,) bias.  logits = H W^T + b.
Top-k selection and softmax weights are invariant to a common shift of all logits, so only the row-centred
W_c = (I - 11^T/E) W matters: rank(W_c) <= E - 1 ("readout subspace" V = right singular vectors of W_c).

Co-routing  C(i, j) = |S_k(x_i) ∩ S_k(x_j)| / k  (independent of expert labels).
Conditional nulls (bias re-fitted on a calibration set so that per-expert loads match the real router):
  N1 "expert geometry preserving":   W_c V Q V^T                     (keeps W_c W_c^T; changes logit covariance)
  N2 "logit covariance preserving":  (W_c V) C^{1/2} Q C^{-1/2} V^T, C = Cov(V^T h)   (keeps Cov(logits); changes W W^T)
with Q Haar-random in O(r).  N2 is invariant to invertible re-parametrisations h -> M h (with W -> W M^{-1}).
Residual D = C - E_null[C];  cross-model similarity T = corr(D_A, D_B) over a fixed set of input pairs.
"""
import numpy as np
import torch


# ---------------------------------------------------------------- basic routing
def centre_rows(W):
    return W - W.mean(0, keepdim=True)


def readout(W, rtol=1e-6):
    """Return U, S, V (V: d x r) of the row-centred router, r = numerical rank."""
    U, S, Vh = torch.linalg.svd(centre_rows(W), full_matrices=False)
    r = int((S > rtol * S[0]).sum())
    return U[:, :r], S[:r], Vh[:r].T


def topk(logits, k):
    return logits.topk(k, dim=-1).indices


def onehot_sets(S, E):
    M = torch.zeros(S.shape[0], E, dtype=torch.get_default_dtype(), device=S.device)
    M.scatter_(1, S, 1.0)
    return M


def loads(S, E):
    return onehot_sets(S, E).mean(0)


def fit_bias(H, W, k, target, b0=None, iters=200, lr=0.5):
    """Find b so that the per-expert selection frequencies of top-k(H W^T + b) match `target` (both normalised to sum 1)."""
    z = H @ W.T
    b = torch.zeros(W.shape[0], dtype=z.dtype, device=z.device) if b0 is None else b0.clone()
    scale = z.std()
    tgt = target / target.sum()
    for _ in range(iters):
        f = loads(topk(z + b, k), W.shape[0])
        f = f / f.sum()
        b = b + lr * scale * (tgt - f) / (tgt + 1e-3)
    return b


def haar(r, gen):
    A = torch.randn(r, r, generator=gen, dtype=torch.float64)
    Q, R = torch.linalg.qr(A)
    return Q * torch.sign(torch.diagonal(R))


def null_router(W, H_cal, kind, Q, stats=None):
    """Return a null router weight (E x d). stats caches (U,S,V,Csq,Cisq)."""
    U, S, V = stats["U"], stats["S"], stats["V"]
    WcV = U * S  # = W_c V  (E x r)
    if kind == "N1":
        return WcV @ Q @ V.T
    if kind == "N2":
        return WcV @ stats["Csq"] @ Q @ stats["Cisq"] @ V.T
    raise ValueError(kind)


def null_stats(W, H_cal, eps=1e-8):
    U, S, V = readout(W)
    u = (H_cal - H_cal.mean(0)) @ V
    C = u.T @ u / (u.shape[0] - 1)
    ev, P = torch.linalg.eigh(C)
    ev = ev.clamp_min(eps * ev.max())
    return {"U": U, "S": S, "V": V, "Csq": P @ torch.diag(ev.sqrt()) @ P.T, "Cisq": P @ torch.diag(1 / ev.sqrt()) @ P.T}


# ---------------------------------------------------------------- co-routing and residuals
def coroute(S, E, k, pairs=None):
    M = onehot_sets(S, E)
    if pairs is None:
        return M @ M.T / k
    i, j = pairs
    return (M[i] * M[j]).sum(1) / k


def null_expectation(W, b, H_cal, H_anchor, k, kind, n_draws=32, seed=0, pairs=None, return_draws=False):
    """E_null[C] on anchor inputs; each draw re-fits the bias on H_cal to the real router's loads."""
    gen = torch.Generator().manual_seed(seed)
    E = W.shape[0]
    target = loads(topk(H_cal @ W.T + b, k), E)
    st = null_stats(W, H_cal)
    acc, draws, load_err = 0.0, [], []
    for _ in range(n_draws):
        Q = haar(st["V"].shape[1], gen).to(W.device, W.dtype)
        Wn = null_router(W, H_cal, kind, Q, st)
        bn = fit_bias(H_cal, Wn, k, target)
        Sa = topk(H_anchor @ Wn.T + bn, k)
        Cn = coroute(Sa, E, k, pairs)
        acc = acc + Cn
        if return_draws:
            draws.append(Cn)
        lc = loads(topk(H_cal @ Wn.T + bn, k), E)
        load_err.append(float((lc / lc.sum() - target / target.sum()).abs().sum() / 2))  # total variation
    out = {"B": acc / n_draws, "load_tv": float(np.mean(load_err))}
    if return_draws:
        out["draws"] = draws
    return out


def upper_pairs(N, device="cpu"):
    i, j = torch.triu_indices(N, N, offset=1, device=device)
    return i, j


def corr(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / (a.norm() * b.norm() + 1e-30))


# ---------------------------------------------------------------- subspace similarity of logits
def _whiten_basis(Z, rtol=1e-6):
    Z = Z - Z.mean(1, keepdim=True)  # remove the common logit shift (routing-invariant)
    Z = Z - Z.mean(0, keepdim=True)
    U, S, _ = torch.linalg.svd(Z, full_matrices=False)
    r = int((S > rtol * S[0]).sum())
    return U[:, :r]


def cca_mean_rho2(ZA, ZB, rtol=1e-6):
    UA, UB = _whiten_basis(ZA, rtol), _whiten_basis(ZB, rtol)
    s = torch.linalg.svdvals(UA.T @ UB)
    r = min(UA.shape[1], UB.shape[1])
    return float((s[:r] ** 2).mean()), r


def linear_cka(ZA, ZB):
    ZA = ZA - ZA.mean(1, keepdim=True)
    ZB = ZB - ZB.mean(1, keepdim=True)
    ZA = ZA - ZA.mean(0)
    ZB = ZB - ZB.mean(0)
    num = (ZA.T @ ZB).norm() ** 2
    return float(num / ((ZA.T @ ZA).norm() * (ZB.T @ ZB).norm()))


# ---------------------------------------------------------------- partition level
def nmi(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    ua, ia = np.unique(a, return_inverse=True)
    ub, ib = np.unique(b, return_inverse=True)
    J = np.zeros((len(ua), len(ub)))
    np.add.at(J, (ia, ib), 1)
    J /= J.sum()
    pa, pb = J.sum(1), J.sum(0)
    nz = J > 0
    mi = (J[nz] * np.log(J[nz] / (pa[:, None] * pb[None, :])[nz])).sum()
    ha = -(pa * np.log(pa)).sum()
    hb = -(pb * np.log(pb)).sum()
    return float(mi / np.sqrt(ha * hb)) if ha > 0 and hb > 0 else 0.0


def topk_overlap(SA, SB, k):
    """Mean |S_A ∩ S_B| / k per input (requires a fixed expert labelling)."""
    E = int(max(SA.max(), SB.max())) + 1
    return float((onehot_sets(SA, E) * onehot_sets(SB, E)).sum(1).mean() / k)


def procrustes(HA_cal, HB_cal):
    """Orthogonal Q minimising ||HB Q - HA||_F (rows = inputs)."""
    U, _, Vh = torch.linalg.svd(HB_cal.T @ HA_cal)
    return U @ Vh
