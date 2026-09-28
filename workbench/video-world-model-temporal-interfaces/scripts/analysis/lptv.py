"""Linear periodically-time-varying (LPTV) model of an action->yaw map from measured 1-frame impulse kernels.

Kernels come from sysid.py output (impulse A0.1, phase p = (f-1) mod 4, kernel over tau=-4..8 relative to
frame f+1). Response to an arbitrary per-frame yaw command a_t is predicted by superposition:
    y_hat[f+1+tau] += (a_f / 0.1) * K_{phase(f)}[tau]
Compared models: ideal (gain * a_{t-1}), LTI (phase-averaged kernel), LPTV (phase-specific kernels).
Used both to validate the LPTV description on unseen human inputs and to invert it (pre-compensation).
"""
import json

import numpy as np

TAUS = np.arange(-4, 9)


def load_kernels(path, amp=0.1):
    d = json.load(open(path))["impulse"]
    return {p: np.array(d[f"A{amp}_phase{p}"]["kernel_mean"]) for p in range(4)}


def response_matrix(n, K, lti=False):
    """H[t, f] = response at frame t to a unit (=0.1) impulse at frame f."""
    Kav = np.mean([K[p] for p in range(4)], 0)
    H = np.zeros((n, n))
    for f in range(1, n):
        k = Kav if lti else K[(f - 1) % 4]
        for tau, v in zip(TAUS, k):
            t = f + 1 + tau
            if 0 <= t < n:
                H[t, f] += v
    return H / 0.1


def predict(a, K, lti=False):
    return response_matrix(len(a), K, lti) @ a


def ideal(a, gain):
    y = np.zeros(len(a))
    y[1:] = gain * a[:-1]
    return y


def invert(y_des, K, lam=1e-2, amax=None):
    """Least-squares pre-compensation: a' = argmin ||H a' - y_des||^2 + lam ||a'||^2 (optionally clipped)."""
    n = len(y_des)
    H = response_matrix(n, K)
    a = np.linalg.solve(H.T @ H + lam * np.eye(n), H.T @ y_des)
    if amax is not None:
        a = np.clip(a, -amax, amax)
    return a
