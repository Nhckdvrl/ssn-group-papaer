"""I04 test on real checkpoints: do real post-training head deltas follow the row pattern predicted by the
simulated head-only Adam trajectories (E02b) of SFT-like vs RL signals?

For a parent→child pair whose parent is the model used in E02b: per row j compute the actual
  ‖ΔW_j‖ (row drift) and s_j = ΔW_j·μ̂ (logit shift along the mean hidden direction of the parent),
and correlate (Spearman, over all rows and within buckets) with the predicted drift / logit shift of each
simulated condition. Also report the bucket means of s_j (does SFT push never-seen rows down along μ?).

Usage: python e01_vs_adam.py <pair_key> <e02b_model>   (e.g. olmo-base__thinksft olmo3-base)
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
from safetensors import safe_open

import models

ROOT = Path(__file__).resolve().parents[1]


def head(name):
    idx = models.tensor_index(name)
    with safe_open(idx["lm_head.weight"], "pt") as f:
        return f.get_tensor("lm_head.weight").float()


def rank(x):
    """Average ranks (ties share one rank; zero-frequency rows and unchanged bf16 rows are common)."""
    u, inv, cnt = np.unique(np.asarray(x), return_inverse=True, return_counts=True)
    return (np.cumsum(cnt) - (cnt - 1) / 2.0)[inv]


def spearman(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(rank(a[m]), rank(b[m]))[0, 1])


def main():
    pair, e02_model = sys.argv[1], sys.argv[2]
    p0, p1, stage = models.PAIRS[pair]
    sim = np.load(f"/tmp/xiang_lmhead/e02/headadam_{e02_model}.npz")
    mu = torch.tensor(sim["mu"]); mu_hat = mu / mu.norm()
    W0, W1 = head(p0), head(p1)
    D = W1 - W0
    drift = D.norm(dim=1).numpy()
    shift = (D @ mu_hat).numpy()
    rel = drift / W0.norm(dim=1).clamp_min(1e-30).numpy()
    freq = sim["pile_freq"]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    from e01_weights import row_buckets
    special = set(tok.all_special_ids) | set(tok.get_added_vocab().values())
    bk = row_buckets(W0.shape[0], len(tok), special, freq)
    res = {"pair": pair, "stage": stage, "e02_model": e02_model, "buckets": {}, "corr": {}}
    for b in sorted(set(bk)):
        m = bk == b
        res["buckets"][b] = {"n": int(m.sum()), "mean_shift_along_mu": float(shift[m].mean()),
                             "median_shift_along_mu": float(np.median(shift[m])), "mean_drift": float(drift[m].mean()),
                             "median_rel_drift": float(np.median(rel[m]))}
    # controls: parent row projection w0·μ̂ (a global shrink ΔW=αW0 shifts rows by α·w0·μ̂) and log frequency
    w0mu = (W0 @ mu_hat).numpy()
    logf = np.log1p(freq.astype(float))
    def resid(y, X):
        Xr = np.column_stack([rank(x) for x in X] + [np.ones(len(y))]).astype(float)
        yr = rank(y)
        return yr - Xr @ np.linalg.lstsq(Xr, yr, rcond=None)[0]
    shift_r = resid(shift, [w0mu, logf])
    shift_r1 = resid(shift, [w0mu])
    # exact removal of the two global components: ΔW = α W0 + 1 cᵀ + R  (least squares), then residual shift R_j·μ̂
    W0d, Dd = W0.double(), D.double()
    Wc, Dc = W0d - W0d.mean(0), Dd - Dd.mean(0)            # removing 1cᵀ = row-centering
    alpha = float((Dc * Wc).sum() / (Wc * Wc).sum())
    R = Dc - alpha * Wc
    res_shift = (R @ mu_hat.double()).numpy()
    res["global_components"] = {"alpha": alpha, "energy_frac_common_shift": float(1 - (Dc ** 2).sum() / (Dd ** 2).sum()),
                                "energy_frac_alpha_after_centering": float(alpha ** 2 * (Wc ** 2).sum() / (Dd ** 2).sum())}
    res["residual_shift_by_bucket"] = {b: {"mean": float(res_shift[bk == b].mean()), "median": float(np.median(res_shift[bk == b]))}
                                       for b in sorted(set(bk))}
    res["controls"] = {"spearman_shift_vs_w0mu": spearman(shift, w0mu), "spearman_shift_vs_logfreq": spearman(shift, logf)}
    for c in ("ce_onpolicy", "rl", "rft", "teacher"):
        pd, ps, tc = sim[f"{c}.drift"], sim[f"{c}.logit_shift"], sim[f"{c}.tgt_count"]
        never = tc == 0
        ps_r = resid(ps, [w0mu, logf])
        res["corr"][c] = {"drift_all": spearman(drift, pd), "shift_all": spearman(shift, ps),
                          "drift_never_target": spearman(drift[never], pd[never]),
                          "shift_never_target": spearman(shift[never], ps[never]),
                          "shift_partial_w0mu_logfreq": float(np.corrcoef(shift_r, ps_r)[0, 1]),
                          "shift_partial_w0mu_only": float(np.corrcoef(shift_r1, resid(ps, [w0mu]))[0, 1]),
                          "residual_shift_all": spearman(res_shift, ps),
                          "residual_shift_never_target": spearman(res_shift[never], ps[never])}
    out = ROOT / "results" / "e01"
    (out / f"vs_adam_{pair}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
