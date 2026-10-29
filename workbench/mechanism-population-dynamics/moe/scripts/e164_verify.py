"""Independent E164 row-scoring and coefficient/cluster-bootstrap reconstruction.

Verification imports no author statistics. The separate synthetic fixture imports
the author only to compare the two implementations before any model experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

MOE = Path(__file__).resolve().parents[1]
ROOT = MOE/'results/e164'
LABELS = [f'R_{r}_G_{g}_{p}' for p in ['full', 'P32'] for r in ['P', 'B'] for g in ['P', 'B']]
LABELS += ['R_P_S0_natural', 'R_B_S0_natural']
LABELS += [f'R_{r}_G_{g}_S0' for r in ['P', 'B'] for g in ['P', 'B']]


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def load(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k].copy() for k in z.files}


def row_scores(a):
    result = {k: np.empty((14, 568), np.float64) for k in
              ['raw_accuracy', 'per_char_accuracy', 'choice_CE', 'true_answer_token_NLL']}
    for i in range(14):
        for q in range(568):
            row = a['candidate_loglikelihood'][i, q]
            g = int(a['gold'][q])
            result['raw_accuracy'][i, q] = int(np.argmax(row) == g)
            result['per_char_accuracy'][i, q] = int(np.argmax(row/a['answer_chars'][q]) == g)
            result['choice_CE'][i, q] = np.logaddexp.reduce(row)-row[g]
            result['true_answer_token_NLL'][i, q] = -row[g]/a['answer_tokens'][q, g]
    return result


def weights(field):
    basis = np.eye(14)
    c = {'absolute/'+label: basis[i] for i, label in enumerate(LABELS)}
    sign = -1 if field.endswith('accuracy') else 1
    def add_grid(prefix, b):
        c[prefix+'natural_B_minus_P'] = b[1, 1]-b[0, 0]
        c[prefix+'R_B_minus_P_at_route_P'] = b[1, 0]-b[0, 0]
        c[prefix+'R_B_minus_P_at_route_B'] = b[1, 1]-b[0, 1]
        c[prefix+'route_B_minus_P_at_R_P'] = b[0, 1]-b[0, 0]
        c[prefix+'route_B_minus_P_at_R_B'] = b[1, 1]-b[1, 0]
        c[prefix+'interaction'] = b[1, 1]-b[1, 0]-b[0, 1]+b[0, 0]
    full = basis[:4].reshape(2, 2, 14)
    masked = basis[4:8].reshape(2, 2, 14)
    add_grid('full/', full); add_grid('P32/', masked)
    damage = (masked-full)*sign
    for r, rn in enumerate(['P', 'B']):
        for g, gn in enumerate(['P', 'B']):
            c[f'mask_damage/R_{rn}_G_{gn}'] = damage[r, g]
    add_grid('mask_damage/', damage)
    removed = basis[10:14].reshape(2, 2, 14)
    controlled = (removed-full)*sign
    natural = [(basis[8+r]-full[r, r])*sign for r in range(2)]
    for r, rn in enumerate(['P', 'B']):
        c['S_effect/natural_R_'+rn] = natural[r]
        for g, gn in enumerate(['P', 'B']):
            c[f'S_effect/R_{rn}_G_{gn}'] = controlled[r, g]
    c['S_partner_change/natural'] = natural[1]-natural[0]
    for g, gn in enumerate(['P', 'B']):
        delta = controlled[1, g]-controlled[0, g]
        c['S_partner_change/fixed_route_'+gn] = delta
        c['S_partner_change/fixed_'+gn+'_minus_natural'] = delta-natural[1]+natural[0]
    return c


class Oracle:
    def __init__(self, a, names):
        self.a, self.names = a, names
        self.fresh = [np.flatnonzero((a['panel'] == 1) & (a['subject'] == i)) for i in range(2, 57)]
        self.old = [np.flatnonzero((a['panel'] == 0) & (a['subject'] == i)) for i in range(2)]
        assert all(len(g) == 8 for g in self.fresh) and all(len(g) == 64 for g in self.old)
        self.fresh_draws = np.random.default_rng(164002).integers(0, 55, size=(2000, 55))
        rng = np.random.default_rng(164003)
        self.old_draws = [rng.integers(0, 64, size=(2000, 64)) for _ in range(2)]

    def expected(self, x, scope):
        is_fresh = scope == 'fresh_primary'
        groups = self.fresh if is_fresh else self.old
        points = np.array([sum(float(x[i]) for i in g)/len(g) for g in groups])
        if is_fresh:
            boot = points[self.fresh_draws].sum(1)/55
        else:
            boot = (np.take(x, groups[0][self.old_draws[0]]).sum(1)
                    + np.take(x, groups[1][self.old_draws[1]]).sum(1))/128
        ids = range(2, 57) if is_fresh else range(2)
        return {'point': float(sum(points)/len(points)), 'ci95': np.quantile(boot, [.025, .975]).tolist(),
                'subjects': len(groups), 'questions': sum(map(len, groups)), 'resamples': 2000,
                'seed': 164002 if is_fresh else 164003,
                'ci_unit': 'paired55subject cluster reweighting' if is_fresh else 'paired questions within2fixed subjects',
                'per_subject': {self.names[i]: {'point': float(p), 'questions': len(g)}
                                for i, p, g in zip(ids, points, groups)}}


class Comparison:
    def __init__(self):
        self.numeric, self.metadata, self.maximum = 0, 0, 0.

    def check(self, got, want, key):
        if isinstance(want, dict):
            if set(got) != set(want):
                raise AssertionError('Different fields: '+key)
            for k in want:
                self.check(got[k], want[k], key+'/'+str(k))
        elif isinstance(want, (list, tuple, np.ndarray)):
            if len(got) != len(want):
                raise AssertionError('Different length: '+key)
            for i, (g, w) in enumerate(zip(got, want)):
                self.check(g, w, key+'/'+str(i))
        elif isinstance(want, (float, np.floating)):
            delta = abs(float(got)-float(want))
            if not np.isfinite(delta) or delta > 1e-11:
                raise AssertionError('Numeric discrepancy: '+key+' '+str(delta))
            self.numeric += 1; self.maximum = max(self.maximum, delta)
        else:
            if got != want:
                raise AssertionError('Metadata discrepancy: '+key)
            self.metadata += 1


def verify_summary(summary, a, names):
    assert tuple(a['conditions']) == tuple(LABELS)
    assert a['candidate_loglikelihood'].shape == (14, 568, 4)
    assert np.isfinite(a['candidate_loglikelihood']).all()
    scores = row_scores(a); oracle = Oracle(a, names); compare = Comparison()
    compare.check(summary['conditions'], LABELS, 'conditions')
    for scope in ['fresh_primary', 'legacy_secondary']:
        for field, table in scores.items():
            coeffs = weights(field)
            expected = {key: oracle.expected((table*coefficient[:, None]).sum(0), scope)
                        for key, coefficient in coeffs.items()}
            compare.check(summary[scope][field], expected, scope+'/'+field)
        kl = {label: oracle.expected(a['first_answer_token_KL'][i], scope) for i, label in enumerate(LABELS)}
        compare.check(summary[scope]['first_answer_token_KL_vs_P_full'], kl, scope+'/KL')
    for scope, panel in [('fresh_primary', 1), ('legacy_secondary', 0)]:
        selected = a['route_diagnostics'][:, a['panel'] == panel]
        expected = np.stack([sum(selected[:, i] for i in range(selected.shape[1]))/selected.shape[1]])[0]
        compare.check(summary['routing_diagnostics']['means'][scope], expected, 'routes/'+scope)
    return {'status': 'passed', 'numeric_comparisons': compare.numeric, 'metadata_comparisons': compare.metadata,
            'maximum_absolute_difference': compare.maximum,
            'independent_implementation': 'Row-wise logaddexp scoring; explicit14-condition coefficient vectors; subject-draw lookup versus author weight matrix.'}


def fixture():
    from e164_analyze import summarize
    rng = np.random.default_rng(164010)
    panel = np.r_[np.zeros(128, int), np.ones(440, int)]
    subjects = np.r_[np.repeat(np.arange(2), 64), np.repeat(np.arange(2, 57), 8)]
    a = {'candidate_loglikelihood': rng.normal(-3, 1, (14, 568, 4)),
         'gold': rng.integers(0, 4, 568), 'answer_chars': rng.integers(2, 10, (568, 4)),
         'answer_tokens': rng.integers(1, 6, (568, 4)), 'conditions': np.array(LABELS),
         'panel': panel, 'subject': subjects,
         'first_answer_token_KL': rng.random((14, 568)),
         'route_diagnostics': rng.random((2, 568, 2, 16, 4))}
    names = ['subject'+str(i) for i in range(57)]
    report = verify_summary(summarize(a, names), a, names)
    w = weights('true_answer_token_NLL')
    known = np.arange(14, dtype=float)
    assert w['full/interaction'] @ known == 0
    assert w['full/R_B_minus_P_at_route_P'] @ known == 2
    assert w['S_partner_change/natural'] @ known == -2
    report.update(fixture='Synthetic14-condition scores only; no new model outputs',
                  source_sha256={'e164_verify.py': sha(__file__), 'e164_analyze.py': sha(MOE/'scripts/e164_analyze.py')})
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT/'CPU_statistics_fixture.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def verify():
    plan = json.loads((ROOT/'plan.json').read_text())
    manifest = json.loads((ROOT/'manifest.json').read_text())
    summary = json.loads((ROOT/'summary.json').read_text())
    assert manifest['status'] == 'complete' and sha(ROOT/'plan.json') == manifest['plan_sha256']
    for name, digest in plan['source_sha256'].items():
        assert sha(MOE/'scripts'/name) == digest
    item = manifest['raw']; assert sha(item['path']) == item['sha256']
    a = load(item['path'])
    assert np.isfinite(a['first_answer_token_KL']).all() and np.isfinite(a['route_diagnostics']).all()
    assert np.array_equal(a['gate0_hashes'][:, 0], a['gate0_hashes'][:, 1])
    for policy in range(2):
        for r in range(2):
            assert np.array_equal(a['candidate_loglikelihood'][policy*4+r*2+r], a['natural_LL'][policy, r])
    report = verify_summary(summary, a, plan['subjects'])
    report.update(raw_sha256=item['sha256'], plan_sha256=manifest['plan_sha256'],
                  summary_sha256=sha(ROOT/'summary.json'), source_sha256=sha(__file__))
    (ROOT/'independent_audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('mode', choices=('fixture', 'verify')); args = p.parse_args()
    print(json.dumps(fixture() if args.mode == 'fixture' else verify(), indent=2))
