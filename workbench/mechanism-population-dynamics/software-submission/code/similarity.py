"""Vectorized within-layer Spearman: S[i, j] = mean over layers of Spearman(map_i[l], map_j[l]) (layers where either map is
constant are skipped, as nanmean does in the loop versions)."""
import numpy as np
from scipy.stats import rankdata


def within_matrix(maps):
    A = np.stack([np.asarray(m, float) for m in maps])            # n x L x H
    R = rankdata(A, axis=2)
    R -= R.mean(2, keepdims=True)
    nrm = np.linalg.norm(R, axis=2, keepdims=True)
    valid = (nrm[..., 0] > 1e-12).astype(float)                   # n x L
    Z = np.where(nrm > 1e-12, R / np.maximum(nrm, 1e-12), 0.0)
    n, L, H = Z.shape
    S = np.einsum("ilh,jlh->ij", Z, Z)
    cnt = valid @ valid.T
    return np.where(cnt > 0, S / np.maximum(cnt, 1), np.nan)



def partial_spearman(x, y, covs):
    """Spearman partial correlation: residualize ranks of x and y on ranks of covariates."""
    R = lambda v: rankdata(v)
    C = np.column_stack([np.ones(len(x))] + [R(c) for c in covs])
    rx = R(x) - C @ np.linalg.lstsq(C, R(x), rcond=None)[0]
    ry = R(y) - C @ np.linalg.lstsq(C, R(y), rcond=None)[0]
    return float(np.corrcoef(rx, ry)[0, 1])
