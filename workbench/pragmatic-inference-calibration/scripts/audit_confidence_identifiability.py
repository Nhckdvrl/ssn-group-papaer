"""Literal parent-account check; simulated variables are never LLM evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.special import expit
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score


def auc(y, s):
    value = float(roc_auc_score(y, s))
    ranks = rankdata(s)
    n1 = int(y.sum())
    n0 = len(y) - n1
    independent = (ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    assert abs(value - independent) < 1e-12
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists()
    paper = a.root / 'papers/confidence-commitment-2026.pdf'
    n = 200000
    rows = []
    for seed in [0, 1, 2]:
        rng = np.random.default_rng(seed)
        z = rng.normal(size=n)
        e = rng.normal(size=n)
        vc = z + e
        correct = rng.random(n) < expit(z)
        residual = vc - z
        zd = e.copy()
        assert np.array_equal(vc, z + zd)
        train, test = slice(0, n // 2), slice(n // 2, n)
        X = np.column_stack([np.ones(n), z])
        coef = np.linalg.lstsq(X[train], vc[train], rcond=None)[0]
        ols_residual = vc[test] - X[test] @ coef
        assert auc(correct, np.zeros(n)) == .5
        for tau in [0., 1.]:
            for mode in ['report-noise-only', 'threshold-noisy-estimate', 'soft-k1', 'soft-k4']:
                if mode == 'report-noise-only':
                    decision = z > tau
                elif mode == 'threshold-noisy-estimate':
                    decision = vc > tau
                    assert np.array_equal(decision, (z + zd) > tau)
                else:
                    k = 1. if mode == 'soft-k1' else 4.
                    decision = rng.random(n) < expit(k * (vc - tau))
                rows.append(dict(seed=seed, n=n, threshold=tau, account=mode,
                    oracle_residual_correctness_auc=auc(correct, residual),
                    oracle_residual_commit_auc=auc(decision, residual),
                    held_out_ols_residual_correctness_auc=auc(correct[test], ols_residual),
                    held_out_ols_residual_commit_auc=auc(decision[test], ols_residual),
                    vc_correctness_auc=auc(correct, vc), vc_commit_auc=auc(decision, vc),
                    ols_train_coefficients=coef.tolist()))
    assert len(rows) == 24
    assert all(abs(r['oracle_residual_correctness_auc'] - .5) < .01 for r in rows)
    assert all(abs(r['oracle_residual_commit_auc'] - .5) < .01 for r in rows if r['account'] == 'report-noise-only')
    assert all(r['oracle_residual_commit_auc'] > .65 for r in rows if r['account'] == 'threshold-noisy-estimate')
    out = dict(parent='arXiv:2606.29490v1', parent_pdf_sha256=hashlib.sha256(paper.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        empirical_llm_predictions_n=0, simulated_trials_per_setting=n,
        scope='Identifiability of the explicitly stated generative account; no challenge to original empirical or steering observations.',
        exact_relabeling_gate_pass=True, rank_auc_gate_pass=True, all_settings=rows,
        analytic_check='For z,e iid N(0,1), Cov(e,1[z+e>tau]) = phi(tau/sqrt(2))/sqrt(2) > 0. Residual=e when proxy=z.',
        implication='Decision-used estimate noise and a same-distribution policy component are observationally indistinguishable here. Report-only noise needs a separate causal placement assumption.')
    a.output.write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
    print(json.dumps({mode: {'correctness_auc_range': [min(r['oracle_residual_correctness_auc'] for r in rows if r['account']==mode), max(r['oracle_residual_correctness_auc'] for r in rows if r['account']==mode)],
        'commit_auc_range': [min(r['oracle_residual_commit_auc'] for r in rows if r['account']==mode), max(r['oracle_residual_commit_auc'] for r in rows if r['account']==mode)]}
        for mode in ['report-noise-only','threshold-noisy-estimate','soft-k1','soft-k4']}, indent=2))


if __name__ == '__main__':
    main()
