"""Brute-force path enumeration check for oracle_perm (K=3, T=4)."""
import itertools, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ices.oracle import Grid  # noqa
from ices.oracle_perm import bijections, perm_oracles  # noqa


def brute(xs, ys, xq, K, lam, eps):
    P = bijections(K); S = len(P); T = len(xs)
    num = np.zeros(K); Z = 0.0
    for path in itertools.product(range(S), repeat=T + 1):
        p = 1.0 / S
        for t in range(1, T + 1):
            p *= (1 - lam) if path[t] == path[t - 1] else lam / (S - 1)
        for t in range(T):
            p *= (1 - eps) if P[path[t], xs[t]] == ys[t] else eps / (K - 1)
        Z += p
        for y in range(K):
            num[y] += p * ((1 - eps) if P[path[T], xq] == y else eps / (K - 1))
    return Z, num / Z


def test_matches_bruteforce():
    rng = np.random.default_rng(0)
    K = 3
    for _ in range(3):
        xs = rng.integers(K, size=4); ys = rng.integers(K, size=4); xq = int(rng.integers(K))
        for lam, eps in ((0.0, 0.1), (0.2, 0.05), (0.3, 0.4)):
            g = Grid(lams=(lam,), epss=(eps,), lam_prior=(1.0,))
            o = perm_oracles(xs, ys, xq, K, g)
            Z, pred = brute(xs, ys, xq, K, lam, eps)
            assert np.allclose(o["meta_pred"], pred, atol=1e-9)
            assert np.isclose(o["meta_log_ml"], np.log(Z), atol=1e-9)


def test_direction_signs():
    """Clustered late B evidence > scattered; noise in prefix lowers trust in the late run (meta)."""
    K = 4; P = bijections(K); A = P[0]; B = P[9]
    rng = np.random.default_rng(1); xs = np.array([0, 1, 2, 3] * 4)[rng.permutation(16)]; xq = 0
    def run(bset):
        ys = [B[x] if t in bset else A[x] for t, x in enumerate(xs)]
        pr = perm_oracles(xs, ys, xq, K)["meta_pred"]; return np.log(pr[B[xq]] / pr[A[xq]])
    assert run(set(range(12, 16))) > run({3, 7, 11, 15})
    assert run({1, 5, 13, 14, 15}) < run({13, 14, 15})
    assert run(set(range(8, 16))) > run(set(range(8)))


if __name__ == "__main__":
    test_matches_bruteforce(); test_direction_signs(); print("ok")
