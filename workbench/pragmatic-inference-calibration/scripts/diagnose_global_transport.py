"""E65: fixed low-dimensional, source-held-out diagnosis of existing E59 outputs."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp, softmax

from iqap_data import CATEGORIES, prepare

RIDGE = 1e-6
SEEDS = (20261003, 1)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folds(sources, seed):
    groups = sorted(set(sources))
    rng = np.random.default_rng(seed)
    rng.shuffle(groups)
    groups.sort(key=lambda g: -sources.count(g))
    loads = np.zeros(5, dtype=int)
    assignment = {}
    for group in groups:
        f = int(loads.argmin())
        assignment[group] = f
        loads[f] += sources.count(group)
    labels = np.array([assignment[s] for s in sources])
    for f in range(5):
        assert set(np.array(sources)[labels == f]).isdisjoint(
            set(np.array(sources)[labels != f]))
    assert set(labels) == set(range(5))
    return labels, assignment


def parameters(v, kind):
    a = v[0] if kind in ('temperature', 'combined') else 1.0
    offset = 1 if kind == 'combined' else 0
    if kind in ('bias', 'combined'):
        b = np.r_[v[offset:offset + 3], -v[offset:offset + 3].sum()]
    else:
        b = np.zeros(4)
    return float(a), b


def objective(v, x, y, kind):
    a, b = parameters(v, kind)
    z = a * x + b
    lp = z - logsumexp(z, axis=1, keepdims=True)
    value = -np.mean(np.sum(y * lp, axis=1)) + RIDGE * (
        (a - 1) ** 2 + b @ b)
    error = (np.exp(lp) - y) / len(y)
    ga = np.sum(error * x) + 2 * RIDGE * (a - 1)
    gb = error.sum(axis=0) + 2 * RIDGE * b
    grad = []
    if kind in ('temperature', 'combined'):
        grad.append(ga)
    if kind in ('bias', 'combined'):
        grad.extend(gb[:3] - gb[3])
    return float(value), np.array(grad)


def fit(x, y, kind):
    initial, bounds = [], []
    if kind in ('temperature', 'combined'):
        initial.append(1.0)
        bounds.append((0.0, 8.0))
    if kind in ('bias', 'combined'):
        initial.extend([0.0] * 3)
        bounds.extend([(-20.0, 20.0)] * 3)
    result = minimize(objective, np.array(initial), args=(x, y, kind), jac=True,
                      method='L-BFGS-B', bounds=bounds,
                      options={'maxiter': 2000, 'ftol': 1e-14, 'gtol': 1e-9})
    assert result.success and np.isfinite(result.fun), result.message
    a, b = parameters(result.x, kind)
    return {'a': a, 'b': b.tolist(), 'iterations': int(result.nit),
            'objective': float(result.fun), 'converged': bool(result.success),
            'a_at_bound': a <= 1e-7 or a >= 8 - 1e-7,
            'bias_parameter_at_bound': bool(np.any(np.abs(result.x[-3:]) >= 20 - 1e-7))
            if kind in ('bias', 'combined') else False}


def predict(x, params):
    return softmax(params['a'] * x + np.array(params['b']), axis=1)


def grouped_ci(values, sources):
    groups = sorted(set(sources))
    sums = np.array([values[np.array(sources) == g].sum() for g in groups])
    sizes = np.array([sources.count(g) for g in groups])
    rng = np.random.default_rng(0)
    counts = rng.multinomial(len(groups), np.full(len(groups), 1 / len(groups)), 2000)
    draws = (counts @ sums) / (counts @ sizes)
    return {'mean': float(np.mean(values)),
            'ci95': np.quantile(draws, [.025, .975]).tolist(),
            'n_items': len(values), 'n_sources': len(groups),
            'ci_scope': 'source bootstrap of fixed OOF predictions; no refitting'}


def read_pair(root, summary, source):
    by_model, hashes = {}, {}
    pre = json.loads((Path(__file__).resolve().parents[1] /
                      'results/E59-source-preflight.json').read_text())
    for cp in ('OLMo-2-1124-13B-SFT', 'OLMo-2-1124-13B-DPO'):
        run = root / 'runs' / ('E59-wording-' + cp)
        cfg = json.loads((run / 'config.json').read_text())
        expected = summary['models'][cp]
        assert cfg['complete'] and cfg['n'] == 924 and cfg['numerical_gate_pass']
        assert sha(run / 'config.json') == expected['config_sha256']
        assert sha(run / 'predictions.jsonl') == expected['raw_sha256']
        assert cfg['input_sha256'] == pre['audits'][cp]['input_sha256']
        rows = [json.loads(line) for line in (run / 'predictions.jsonl').read_text().splitlines()]
        assert len(rows) == len({z['id'] for z in rows}) == 924
        grouped = {}
        for z in rows:
            for key in ('full_logprob', 'content_logprob'):
                lp = np.array([c[key] for c in z['choice_scores']])
                assert np.isfinite(lp).all()
                assert np.allclose(np.exp(lp - logsumexp(lp)),
                                   z[key]['conditional_probs'], rtol=1e-10, atol=1e-12)
            if z['kind'] != 'natural':
                continue
            assert z['source'] == source[z['source']['Item']]
            for key in ('full_logprob', 'content_logprob'):
                g = '/'.join((z['alias'], z['interface'], key))
                lp = np.array([c[key] for c in z['choice_scores']])
                grouped.setdefault(g, {})[z['source']['Item']] = lp - logsumexp(lp)
        assert len(grouped) == 12 and all(len(rows) == 150 for rows in grouped.values())
        by_model[cp] = grouped
        hashes[cp] = {'raw': expected['raw_sha256'], 'config': expected['config_sha256']}
    return list(by_model.values()), hashes


def control(x, labels):
    b = np.array([.3, -.2, .1, -.2])
    y = softmax(.7 * x + b, axis=1)
    errors = []
    for target in (np.exp(x), y, np.tile([.1, .2, .3, .4], (len(x), 1))):
        out = np.empty_like(target)
        for f in range(5):
            params = fit(x[labels != f], target[labels != f], 'combined')
            out[labels == f] = predict(x[labels == f], params)
        errors.append(float(np.mean(np.sum((out - target) ** 2, axis=1))))
    v = np.array([.9, .2, -.1, .05])
    _, analytic = objective(v, x, y, 'combined')
    numerical = np.empty(4)
    for j in range(4):
        shift = np.zeros(4)
        shift[j] = 1e-6
        numerical[j] = (objective(v + shift, x, y, 'combined')[0] -
                        objective(v - shift, x, y, 'combined')[0]) / 2e-6
    gradient_error = float(np.max(np.abs(analytic - numerical)))
    assert max(errors) < 1e-7 and gradient_error < 1e-5
    return {'synthetic_oof_mse': errors, 'max_gradient_error': gradient_error, 'passed': True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists()
    local = a.root / 'runs/E65-global-answer-transport'
    assert not local.exists()
    source_rows, source_sha = prepare(a.root)
    source = {r['Item']: r for r in source_rows}
    ids = [r['Item'] for r in source_rows]
    sources = [r['Source'] for r in source_rows]
    assert len(set(sources)) == 68
    human = np.array([[int(r[c]) / 30 for c in CATEGORIES] for r in source_rows])
    summary_path = Path(__file__).resolve().parents[1] / 'results/E59-wording-summary.json'
    parent = json.loads(summary_path.read_text())
    (left, right), hashes = read_pair(a.root, parent, source)
    local.mkdir()
    split_info, controls, analyses, transfers = {}, {}, {}, {}
    with (local / 'oof.jsonl').open('w') as detail:
        for seed in SEEDS:
            labels, assignment = folds(sources, seed)
            split_info[str(seed)] = {'assignment': assignment,
                                    'items': [{'item_id': i, 'source': s, 'fold': int(f)}
                                              for i, s, f in zip(ids, sources, labels)]}
            for g in sorted(left):
                x = np.stack([left[g][i] for i in ids])
                y = np.exp(np.stack([right[g][i] for i in ids]))
                px = np.exp(x)
                controls[str(seed) + '/' + g] = control(x, labels)
                change = np.sum((y - human) ** 2, axis=1) - np.sum((px - human) ** 2, axis=1)
                identity_error = np.sum((px - y) ** 2, axis=1)
                actual = parent['paired_stage_changes'][
                    'OLMo-2-1124-13B-SFT -> OLMo-2-1124-13B-DPO'][g]['four_way_brier']['mean']
                assert abs(change.mean() - actual) < 1e-10
                models = {}
                for kind in ('identity', 'constant', 'bias', 'temperature', 'combined'):
                    output = np.empty_like(y)
                    fitted = {}
                    for f in range(5):
                        train, test = labels != f, labels == f
                        if kind == 'identity':
                            params = {'a': 1.0, 'b': [0.0] * 4}
                            output[test] = px[test]
                        elif kind == 'constant':
                            params = {'mean_dpo': y[train].mean(axis=0).tolist()}
                            output[test] = params['mean_dpo']
                        else:
                            params = fit(x[train], y[train], kind)
                            output[test] = predict(x[test], params)
                        fitted[str(f)] = params
                    assert np.isfinite(output).all() and np.allclose(output.sum(axis=1), 1)
                    error = np.sum((output - y) ** 2, axis=1)
                    predicted_change = np.sum((output - human) ** 2, axis=1) - np.sum((px - human) ** 2, axis=1)
                    residual = change - predicted_change
                    kl = np.sum(y * (np.log(y) - np.log(np.maximum(output, 1e-300))), axis=1)
                    models[kind] = {'transport_mse': grouped_ci(error, sources),
                                    'transport_kl': grouped_ci(kl, sources),
                                    'mse_improvement_vs_identity': grouped_ci(identity_error - error, sources),
                                    'fraction_transport_mse_reduced': float(1 - error.mean() / identity_error.mean()),
                                    'predicted_human_distance_change': grouped_ci(predicted_change, sources),
                                    'residual_human_distance_change': grouped_ci(residual, sources),
                                    'parameters_by_fold': fitted}
                    for n, item in enumerate(ids):
                        detail.write(json.dumps({'seed': seed, 'group': g, 'kind': kind, 'item_id': item,
                                                 'source': sources[n], 'fold': int(labels[n]),
                                                 'sft': px[n].tolist(), 'dpo': y[n].tolist(),
                                                 'prediction': output[n].tolist(),
                                                 'human': human[n].tolist(),
                                                 'residual_human_distance_change': float(residual[n])}) + '\n')
                    if kind == 'combined' and g.startswith('W0/'):
                        for alias in ('W1', 'W2'):
                            other = alias + g[2:]
                            tx = np.stack([left[other][i] for i in ids])
                            ty = np.exp(np.stack([right[other][i] for i in ids]))
                            tp = np.empty_like(ty)
                            for f in range(5):
                                tp[labels == f] = predict(tx[labels == f], fitted[str(f)])
                            transfers[str(seed) + '/' + other] = grouped_ci(np.sum((tp - ty) ** 2, axis=1), sources)
                analyses[str(seed) + '/' + g] = {'actual_human_distance_change': grouped_ci(change, sources),
                                               'models': models}
    checks = []
    for seed in SEEDS:
        for alias in ('W0', 'W1', 'W2'):
            k = f'{seed}/{alias}/common-chat/full_logprob'
            c = analyses[k]['models']['combined']
            checks.append({'group': k,
                           'passes_resource_heuristic': c['fraction_transport_mse_reduced'] >= .8 and
                           abs(c['residual_human_distance_change']['mean']) <= .05})
    result = {'experiment': 'E65', 'n_items': 150, 'n_sources': 68, 'new_gpu_hours': 0,
              'input_hashes': hashes, 'source_sha256': source_sha,
              'E59_summary_sha256': sha(summary_path), 'script_sha256': sha(Path(__file__)),
              'splits': split_info, 'positive_controls': controls,
              'analyses': analyses, 'W0_map_wording_transfer': transfers,
              'resource_heuristic_checks': checks,
              'all_primary_heuristics_pass': all(c['passes_resource_heuristic'] for c in checks),
              'oof_path': str(local / 'oof.jsonl'), 'oof_sha256': sha(local / 'oof.jsonl'),
              'limits': ['Task-distribution transport, not a causal model of DPO or pragmatic ability.',
                         'OOF-source CI conditional on fitted mappings; not full refit uncertainty.',
                         'Failure of a low-dimensional map does not identify a pragmatic mechanism.',
                         'Paraphrase norms unchanged; all two seeds, interfaces, score types retained.']}
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'all_primary_heuristics_pass': result['all_primary_heuristics_pass'],
                      'primary': {k: {'actual_change': v['actual_human_distance_change'],
                                      'explained': v['models']['combined']['fraction_transport_mse_reduced'],
                                      'residual': v['models']['combined']['residual_human_distance_change']}
                                  for k, v in analyses.items() if 'common-chat/full_logprob' in k}}, indent=2))


if __name__ == '__main__':
    main()
