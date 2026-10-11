"""Exact oracle for K-class mapping drift (E25).

Latent state r_t = a bijection class -> label (all K! of them).  r_1 uniform; at each step r stays with prob
1-lam, else jumps uniformly to one of the other K!-1 bijections.  Label emission: y_t = r_t(x_t) with prob
1-eps, otherwise uniform over the other K-1 labels.  (lam, eps) on the same Grid / hyper-prior as
`oracle.py`; set = lam 0 only, sequence = lam > 0 only, meta = full grid (Bayesian model average).
Output: predictive distribution over the K labels for the query class.
"""
import itertools
import numpy as np
from scipy.special import logsumexp
from .oracle import Grid


def bijections(K):
    return np.array(list(itertools.permutations(range(K))))      # (S, K): perm[s, class] = label


def _forward(P, xs, ys, xq, lams, epss, K):
    """Vectorised over the grid. Returns logZ (G,), predictive (G, K)."""
    S = len(P)
    lam = np.repeat(lams, len(epss)); eps = np.tile(epss, len(lams)); G = len(lam)
    with np.errstate(divide="ignore"):
        lhit = np.log(1 - eps); lmiss = np.log(eps / (K - 1))
    la = np.full((G, S), -np.log(S)); logZ = np.zeros(G)
    for t, (x, y) in enumerate(zip(xs, ys)):
        if t > 0:
            a = np.exp(la)
            a = (1 - lam)[:, None] * a + (lam / (S - 1))[:, None] * (1 - a)
            with np.errstate(divide="ignore"):
                la = np.log(np.clip(a, 0, None))
        hit = (P[:, x] == y)
        le = np.where(hit[None, :], lhit[:, None], lmiss[:, None])
        la = la + le
        z = logsumexp(la, axis=1); logZ += z
        la = np.where(np.isfinite(z)[:, None], la - np.where(np.isfinite(z), z, 0)[:, None], -np.inf)  # impossible grid points stay at logZ=-inf
    a = np.exp(la)
    a = (1 - lam)[:, None] * a + (lam / (S - 1))[:, None] * (1 - a)       # step to the query
    pred = np.zeros((G, K))
    onehot = np.eye(K)[P[:, xq]]                                           # (S, K)
    pred = (1 - eps)[:, None] * (a @ onehot) + (eps / (K - 1))[:, None] * (a @ (1 - onehot))
    return logZ, np.nan_to_num(pred), lam


def perm_oracles(xs, ys, xq, K, grid: Grid | None = None, P=None):
    grid = grid or Grid()
    lams, lp, epss, ep = grid.priors()
    P = bijections(K) if P is None else P
    logZ, pred, lam = _forward(P, np.asarray(xs), np.asarray(ys), int(xq), np.asarray(lams, float), np.asarray(epss, float), K)
    with np.errstate(divide="ignore"):
        logprior = (np.log(lp)[:, None] + np.log(ep)[None, :]).ravel()
    out = {}
    for name, mask in (("set", lam == 0), ("sequence", lam > 0), ("meta", np.ones_like(lam, bool))):
        lw = np.where(mask, logprior + logZ, -np.inf)
        w = np.exp(lw - logsumexp(lw))
        out[f"{name}_pred"] = (w @ pred).tolist()
        out[f"{name}_log_ml"] = float(logsumexp(lw))
        if name == "meta":
            out["meta_p_volatile"] = float(w[lam > 0].sum())
    return out
