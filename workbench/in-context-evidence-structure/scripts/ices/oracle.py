"""Exact Bayesian oracles for in-context evidence-structure episodes.

Task family: inputs x in {0,1}^n (n binary attributes); hidden rule h = (a, s)
labels x -> x[a] XOR s.  |H| = 2n.

Generative model used by every oracle (only its hyper-priors differ):
  h_1 ~ Uniform(H)
  h_{t+1} = h_t            with prob 1 - lam
          ~ Uniform(H \\ {h_t}) with prob lam          (volatility / hazard)
  y_t | x_t, h_t, eps: correct label w.p. 1 - eps, flipped w.p. eps   (stochasticity)

Named oracles
  set      : lam = 0 (exchangeable; one rule), eps marginalised over a grid
  sequence : lam > 0 fixed grid (always allows change), eps marginalised
  meta     : joint posterior over lam (incl. lam = 0) and eps  -> infers
             *which* evidence structure generated the context
The forward algorithm is exact for each (lam, eps) grid point; grids are
finite so the full hierarchical posterior is exact enumeration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from scipy.special import logsumexp


def hypotheses(n_attr: int) -> np.ndarray:
    """Return array (2n, 2): rows (attribute index, polarity)."""
    return np.array([(a, s) for a in range(n_attr) for s in (0, 1)], dtype=int)


def rule_labels(H: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Labels of every hypothesis on every input.  X: (T, n) -> (|H|, T)."""
    X = np.asarray(X, dtype=int)
    return X[:, H[:, 0]].T ^ H[:, 1][:, None]


@dataclass
class Grid:
    lams: tuple = (0.0, 0.02, 0.05, 0.1, 0.2, 0.3)
    lam_prior: tuple | None = None  # default: P(lam=0)=0.5, rest uniform
    epss: tuple = (0.0, 0.05, 0.1, 0.2, 0.3, 0.4)
    eps_prior: tuple | None = None  # default uniform

    def priors(self):
        lams = np.array(self.lams, float)
        if self.lam_prior is None:
            lp = np.where(lams == 0, 0.5, 0.5 / max(1, (lams > 0).sum()))
            if (lams == 0).sum() == 0:
                lp = np.full(len(lams), 1.0 / len(lams))
        else:
            lp = np.array(self.lam_prior, float)
        epss = np.array(self.epss, float)
        ep = (np.full(len(epss), 1.0 / len(epss)) if self.eps_prior is None
              else np.array(self.eps_prior, float))
        return lams, lp / lp.sum(), epss, ep / ep.sum()


def _log_obs(L: np.ndarray, y: np.ndarray, eps: float) -> np.ndarray:
    """log P(y_t | h, eps) for all h, t.  L: (|H|, T) rule labels."""
    match = (L == y[None, :])
    with np.errstate(divide="ignore"):
        lc, lw = np.log(1 - eps), np.log(eps) if eps > 0 else -np.inf
    return np.where(match, lc, lw)


def forward(L: np.ndarray, y: np.ndarray, lam: float, eps: float):
    """Exact forward pass with augmented 'any switch yet' flag.

    Returns (log marginal likelihood, filtered posterior over (flag, h) after
    the last observation, shape (2, |H|), probability space).
    """
    K, T = L.shape
    lo = _log_obs(L, y, eps)                       # (K, T)
    stay = np.log1p(-lam) if lam < 1 else -np.inf
    move = np.log(lam / (K - 1)) if lam > 0 else -np.inf
    alpha = np.full((2, K), -np.inf)               # alpha[flag, h]
    alpha[0] = -np.log(K) + lo[:, 0]
    logZ = logsumexp(alpha)
    if not np.isfinite(logZ):
        return -np.inf, np.full((2, K), 0.5 / K)
    alpha = alpha - logZ
    for t in range(1, T):
        marg = np.logaddexp(alpha[0], alpha[1])    # P(h_{t-1}=h), log
        tot = logsumexp(marg)
        others = _log_diff(np.full(K, tot), marg)  # sum over h != h'
        new = np.empty((2, K))
        new[0] = alpha[0] + stay
        new[1] = np.logaddexp(alpha[1] + stay, others + move)
        new = new + lo[:, t][None, :]
        c = logsumexp(new)
        if not np.isfinite(c):
            return -np.inf, np.full((2, K), 0.5 / K)
        logZ += c
        alpha = new - c
    return float(logZ), np.exp(alpha)


def _log_diff(a, b):
    """log(exp(a) - exp(b)) elementwise, b <= a, safe."""
    b = np.minimum(b, a)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = a + np.log1p(-np.exp(b - a))
    out[np.isnan(out)] = -np.inf
    return out


def _loglik(L, y, lam, eps):
    """Plain forward log-likelihood (no flag) for clarity / cross-check."""
    K, T = L.shape
    lo = _log_obs(L, y, eps)
    a = -np.log(K) + lo[:, 0]
    total = logsumexp(a)
    a = a - total
    stay = np.log1p(-lam) if lam < 1 else -np.inf
    move = np.log(lam / (K - 1)) if lam > 0 else -np.inf
    for t in range(1, T):
        tot = logsumexp(a)
        others = _log_diff(np.full(K, tot), a)
        a = np.logaddexp(a + stay, others + move) + lo[:, t]
        c = logsumexp(a)
        total += c
        a = a - c
    return total


@dataclass
class OracleResult:
    log_ml: float                  # log p(D) under the oracle
    p_query: float                 # P(y_q = 1 | D)   (observation predictive)
    p_rule_query: float            # P(h_{T+1}(x_q) = 1 | D)  (noise-free rule)
    p_switch: float                # P(at least one switch in 1..T+1 | D)
    post_lam: np.ndarray = field(default=None)
    post_eps: np.ndarray = field(default=None)
    post_h_last: np.ndarray = field(default=None)  # P(h_T | D)


def oracle(X, y, xq, n_attr: int, grid: Grid, lam_mask=None) -> OracleResult:
    """Exact hierarchical posterior predictive for one episode.

    lam_mask: optional boolean over grid.lams restricting the oracle (set /
    sequence variants) -- prior renormalised over the kept values.
    """
    H = hypotheses(n_attr)
    X = np.asarray(X, int); y = np.asarray(y, int); xq = np.asarray(xq, int)
    L = rule_labels(H, X)
    Lq = rule_labels(H, xq[None, :])[:, 0]       # (K,)
    lams, lp, epss, ep = grid.priors()
    if lam_mask is not None:
        lp = np.where(lam_mask, lp, 0.0)
        lp = lp / lp.sum()
    K = len(H)
    logw, pq, prq, psw, plast = [], [], [], [], []
    for i, lam in enumerate(lams):
        for j, eps in enumerate(epss):
            if lp[i] == 0 or ep[j] == 0:
                logw.append(-np.inf); pq.append(0.5); prq.append(0.5)
                psw.append(0.0); plast.append(np.full(K, 1 / K)); continue
            ll, post = forward(L, y, lam, eps)           # post (2, K)
            ph = post.sum(0)                              # P(h_T | D)
            # one more transition to h_{T+1}
            ph_next = (1 - lam) * ph + lam * (1 - ph) / (K - 1)
            p_no_switch_T = post[0].sum()
            p_sw = 1 - p_no_switch_T * (1 - lam)
            prule = float((ph_next * Lq).sum())
            pobs = prule * (1 - eps) + (1 - prule) * eps
            logw.append(np.log(lp[i]) + np.log(ep[j]) + ll)
            pq.append(pobs); prq.append(prule); psw.append(p_sw); plast.append(ph)
    logw = np.array(logw)
    lml = logsumexp(logw)
    w = np.exp(logw - lml)
    W = w.reshape(len(lams), len(epss))
    return OracleResult(
        log_ml=float(lml),
        p_query=float(w @ np.array(pq)),
        p_rule_query=float(w @ np.array(prq)),
        p_switch=float(w @ np.array(psw)),
        post_lam=W.sum(1), post_eps=W.sum(0),
        post_h_last=(w[:, None] * np.array(plast)).sum(0),
    )


def all_oracles(X, y, xq, n_attr, grid: Grid | None = None) -> dict:
    grid = grid or Grid()
    lams = np.array(grid.lams)
    res = {
        "set": oracle(X, y, xq, n_attr, grid, lam_mask=(lams == 0)),
        "sequence": oracle(X, y, xq, n_attr, grid, lam_mask=(lams > 0)),
        "meta": oracle(X, y, xq, n_attr, grid),
    }
    log_bf = res["sequence"].log_ml - res["set"].log_ml
    out = {}
    for k, r in res.items():
        out[f"{k}_p_query"] = r.p_query
        out[f"{k}_p_rule_query"] = r.p_rule_query
        out[f"{k}_log_ml"] = r.log_ml
    out["meta_p_switch"] = res["meta"].p_switch
    out["meta_p_volatile"] = float(res["meta"].post_lam[lams > 0].sum())
    out["log_bf_change_vs_stable"] = float(log_bf)
    out["meta_post_eps_mean"] = float(res["meta"].post_eps @ np.array(grid.epss))
    out["meta_post_lam_mean"] = float(res["meta"].post_lam @ lams)
    return out


# ---------------------------------------------------------------------------
# Vectorised version over the whole (lam, eps) grid -- same maths as forward().
def forward_grid(L: np.ndarray, y: np.ndarray, lams: np.ndarray, epss: np.ndarray):
    """Returns logZ (G,), alpha (G, 2, K) for every grid point g=(lam_i, eps_j)
    flattened in C order (i major)."""
    K, T = L.shape
    lam = np.repeat(lams, len(epss))               # (G,)
    eps = np.tile(epss, len(lams))
    G = len(lam)
    match = (L == y[None, :])                       # (K, T)
    with np.errstate(divide="ignore"):
        lc = np.log1p(-eps)[:, None, None]
        lw = np.log(eps)[:, None, None]
        stay = np.log1p(-lam)[:, None]
        move = np.log(lam / (K - 1))[:, None]
    lo = np.where(match[None], lc, lw)             # (G, K, T)
    alpha = np.full((G, 2, K), -np.inf)
    alpha[:, 0] = -np.log(K) + lo[:, :, 0]
    logZ = logsumexp(alpha.reshape(G, -1), axis=1)
    dead = ~np.isfinite(logZ)
    alpha = alpha - np.where(dead, 0, logZ)[:, None, None]
    for t in range(1, T):
        marg = np.logaddexp(alpha[:, 0], alpha[:, 1])          # (G, K)
        tot = logsumexp(marg, axis=1, keepdims=True)
        b = np.minimum(marg, tot)
        with np.errstate(divide="ignore", invalid="ignore"):
            others = tot + np.log1p(-np.exp(b - tot))
        others = np.where(np.isnan(others), -np.inf, others)
        new = np.empty_like(alpha)
        new[:, 0] = alpha[:, 0] + stay
        new[:, 1] = np.logaddexp(alpha[:, 1] + stay, others + move)
        new = new + lo[:, :, t][:, None, :]
        c = logsumexp(new.reshape(G, -1), axis=1)
        dead |= ~np.isfinite(c)
        logZ = logZ + np.where(np.isfinite(c), c, 0)
        alpha = new - np.where(np.isfinite(c), c, 0)[:, None, None]
    logZ = np.where(dead, -np.inf, logZ)
    alpha = np.where(dead[:, None, None], np.log(0.5 / K), alpha)
    return logZ, np.exp(alpha), lam, eps


def oracle_fast(X, y, xq, n_attr: int, grid: Grid, lam_mask=None) -> OracleResult:
    H = hypotheses(n_attr)
    X = np.asarray(X, int); y = np.asarray(y, int); xq = np.asarray(xq, int)
    L = rule_labels(H, X)
    Lq = rule_labels(H, xq[None, :])[:, 0].astype(float)
    lams, lp, epss, ep = grid.priors()
    if lam_mask is not None:
        lp = np.where(lam_mask, lp, 0.0); lp = lp / lp.sum()
    K = len(H)
    logZ, post, lam, eps = forward_grid(L, y, lams, epss)
    with np.errstate(divide="ignore"):
        logprior = (np.log(lp)[:, None] + np.log(ep)[None, :]).ravel()
    logw = logprior + logZ
    lml = logsumexp(logw)
    w = np.exp(logw - lml)
    ph = post.sum(1)                                          # (G, K)
    ph_next = (1 - lam)[:, None] * ph + lam[:, None] * (1 - ph) / (K - 1)
    prule = ph_next @ Lq
    pobs = prule * (1 - eps) + (1 - prule) * eps
    psw = 1 - post[:, 0].sum(1) * (1 - lam)
    W = w.reshape(len(lams), len(epss))
    return OracleResult(log_ml=float(lml), p_query=float(w @ pobs),
                        p_rule_query=float(w @ prule), p_switch=float(w @ psw),
                        post_lam=W.sum(1), post_eps=W.sum(0),
                        post_h_last=(w[:, None] * ph).sum(0))


def all_oracles_fast(X, y, xq, n_attr, grid: Grid | None = None) -> dict:
    grid = grid or Grid()
    lams = np.array(grid.lams)
    res = {
        "set": oracle_fast(X, y, xq, n_attr, grid, lam_mask=(lams == 0)),
        "sequence": oracle_fast(X, y, xq, n_attr, grid, lam_mask=(lams > 0)),
        "meta": oracle_fast(X, y, xq, n_attr, grid),
    }
    out = {}
    for k, r in res.items():
        out[f"{k}_p_query"] = r.p_query
        out[f"{k}_p_rule_query"] = r.p_rule_query
        out[f"{k}_log_ml"] = r.log_ml
    out["meta_p_switch"] = res["meta"].p_switch
    out["meta_p_volatile"] = float(res["meta"].post_lam[lams > 0].sum())
    out["log_bf_change_vs_stable"] = float(res["sequence"].log_ml - res["set"].log_ml)
    out["meta_post_eps_mean"] = float(res["meta"].post_eps @ np.array(grid.epss))
    out["meta_post_lam_mean"] = float(res["meta"].post_lam @ lams)
    return out
