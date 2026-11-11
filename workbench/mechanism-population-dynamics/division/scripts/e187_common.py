"""E187 shared helper: expert correspondence between layers from router rows (card primary rule: Hungarian on the
signed cosine of row-centred router rows; 'absraw' = |cos| of raw rows as in e185x).  perm[j] = matched expert of l
for expert j of m.  Router weights come from ~/mechpop_cache/e187/w_<key>/small.npz (e187_weights.py)."""
import os
import numpy as np
from scipy.optimize import linear_sum_assignment

E = 128


def _hung(S):
    r, c = linear_sum_assignment(-S)
    p = np.empty(S.shape[0], np.int64); p[c] = r
    return p


class RouterMatch(dict):
    def __init__(self, key):
        super().__init__()
        G = np.load(os.path.expanduser(f"~/mechpop_cache/e187/w_{key}/small.npz"))["gate"].astype(np.float64)
        Gc = G - G.mean(1, keepdims=True)
        self.Gc = Gc / np.linalg.norm(Gc, axis=2, keepdims=True)
        self.Gr = G / np.linalg.norm(G, axis=2, keepdims=True)

    def __missing__(self, k):
        l, m, kind = k.split("_")
        l, m = int(l), int(m)
        v = _hung(self.Gc[l] @ self.Gc[m].T) if kind == "router" else _hung(np.abs(self.Gr[l] @ self.Gr[m].T))
        self[k] = v
        return v
