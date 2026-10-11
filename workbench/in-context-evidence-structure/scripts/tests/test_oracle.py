"""Brute-force checks of the exact forward oracle (enumerate every rule path)."""
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ices.oracle import (Grid, _loglik, all_oracles, forward, hypotheses,  # noqa: E402
                         oracle, rule_labels)


def brute(X, y, xq, n_attr, lam, eps):
    """Enumerate all paths h_1..h_{T+1}; return (lik, P(y_q=1 rule), P(switch))."""
    H = hypotheses(n_attr)
    K = len(H)
    L = rule_labels(H, X)
    Lq = rule_labels(H, np.asarray(xq)[None, :])[:, 0]
    T = len(y)
    lik = 0.0; num_q = 0.0; num_sw = 0.0
    for path in itertools.product(range(K), repeat=T + 1):
        p = 1.0 / K
        for t in range(1, T + 1):
            if path[t] == path[t - 1]:
                p *= 1 - lam
            else:
                p *= lam / (K - 1)
        if p == 0:
            continue
        for t in range(T):
            p *= (1 - eps) if L[path[t], t] == y[t] else eps
        lik += p
        num_q += p * Lq[path[T]]
        num_sw += p * any(path[t] != path[t - 1] for t in range(1, T + 1))
    return lik, num_q / lik, num_sw / lik


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("lam,eps", [(0.0, 0.1), (0.1, 0.1), (0.3, 0.05), (0.2, 0.0)])
def test_forward_matches_bruteforce(seed, lam, eps):
    rng = np.random.default_rng(seed)
    n_attr, T = 2, 5
    X = rng.integers(0, 2, size=(T, n_attr))
    y = rng.integers(0, 2, size=T)
    xq = rng.integers(0, 2, size=n_attr)
    lik, pq_rule, psw = brute(X, y, xq, n_attr, lam, eps)
    if lik == 0:
        ll, _ = forward(rule_labels(hypotheses(n_attr), X), y, lam, eps)
        assert ll == -np.inf
        return
    grid = Grid(lams=(lam,), lam_prior=(1.0,), epss=(eps,), eps_prior=(1.0,))
    r = oracle(X, y, xq, n_attr, grid)
    assert np.isclose(np.exp(r.log_ml), lik, rtol=1e-9)
    assert np.isclose(r.p_rule_query, pq_rule, atol=1e-9)
    assert np.isclose(r.p_switch, psw, atol=1e-9)
    assert np.isclose(_loglik(rule_labels(hypotheses(n_attr), X), y, lam, eps), np.log(lik))


def test_hierarchical_mixture_matches_manual():
    rng = np.random.default_rng(0)
    n_attr, T = 2, 5
    X = rng.integers(0, 2, size=(T, n_attr)); y = rng.integers(0, 2, size=T)
    xq = rng.integers(0, 2, size=n_attr)
    lams, epss = (0.0, 0.2), (0.1, 0.3)
    grid = Grid(lams=lams, lam_prior=(0.5, 0.5), epss=epss, eps_prior=(0.5, 0.5))
    r = oracle(X, y, xq, n_attr, grid)
    tot = 0.0; num = 0.0
    for lam in lams:
        for eps in epss:
            lik, pq_rule, _ = brute(X, y, xq, n_attr, lam, eps)
            tot += 0.25 * lik; num += 0.25 * lik * pq_rule
    assert np.isclose(np.exp(r.log_ml), tot)
    assert np.isclose(r.p_rule_query, num / tot)


def test_set_oracle_is_order_invariant():
    rng = np.random.default_rng(1)
    n_attr, T = 4, 12
    X = rng.integers(0, 2, size=(T, n_attr)); y = rng.integers(0, 2, size=T)
    xq = rng.integers(0, 2, size=n_attr)
    a = all_oracles(X, y, xq, n_attr)
    perm = rng.permutation(T)
    b = all_oracles(X[perm], y[perm], xq, n_attr)
    assert np.isclose(a["set_p_query"], b["set_p_query"])
    assert np.isclose(a["set_log_ml"], b["set_log_ml"])


def test_clean_stable_context_learns_rule():
    # attribute 1, polarity 0, clean -> query follows rule with high prob
    rng = np.random.default_rng(2)
    n_attr, T = 4, 12
    X = rng.integers(0, 2, size=(T, n_attr)); y = X[:, 1].copy()
    xq = np.array([0, 1, 0, 0])
    a = all_oracles(X, y, xq, n_attr)
    assert a["meta_p_query"] > 0.8
    assert a["log_bf_change_vs_stable"] < 0


def test_fast_matches_slow():
    from ices.oracle import all_oracles_fast
    for seed in range(5):
        rng = np.random.default_rng(seed)
        n_attr, T = 4, 14
        X = rng.integers(0, 2, size=(T, n_attr)); y = X[:, 2] ^ (rng.random(T) < 0.2)
        xq = rng.integers(0, 2, size=n_attr)
        a = all_oracles(X, y, xq, n_attr); b = all_oracles_fast(X, y, xq, n_attr)
        for k in a:
            assert np.isclose(a[k], b[k], atol=1e-9), k
