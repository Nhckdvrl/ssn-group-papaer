"""E164 fixed contrasts and paired task-cluster uncertainty; NumPy only."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

MOE = Path(__file__).resolve().parents[1]
ROOT = MOE/'results/e164'
CONDITIONS = tuple('R_'+r+'_G_'+g+'_'+p for p in ('full', 'P32') for r in ('P', 'B') for g in ('P', 'B')) + (
    'R_P_S0_natural', 'R_B_S0_natural') + tuple('R_'+r+'_G_'+g+'_S0' for r in ('P', 'B') for g in ('P', 'B'))
FIELDS = ('raw_accuracy', 'per_char_accuracy', 'choice_CE', 'true_answer_token_NLL')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def arrays(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k].copy() for k in z.files}


def metrics(a):
    ll = a['candidate_loglikelihood']
    if ll.shape != (14, 568, 4) or not np.isfinite(ll).all() or tuple(a['conditions']) != CONDITIONS:
        raise ValueError('Expected the complete frozen14-condition population')
    q = np.arange(len(a['gold']))
    shifted = ll-ll.max(-1, keepdims=True)
    lp = shifted-np.log(np.exp(shifted).sum(-1, keepdims=True))
    return {'raw_accuracy': (ll.argmax(-1) == a['gold']).astype(float),
            'per_char_accuracy': ((ll/a['answer_chars']).argmax(-1) == a['gold']).astype(float),
            'choice_CE': -lp[:, q, a['gold']],
            'true_answer_token_NLL': -ll[:, q, a['gold']]/a['answer_tokens'][q, a['gold']]}


def factorial(x):
    return {'natural_B_minus_P': x[1, 1]-x[0, 0],
            'R_B_minus_P_at_route_P': x[1, 0]-x[0, 0],
            'R_B_minus_P_at_route_B': x[1, 1]-x[0, 1],
            'route_B_minus_P_at_R_P': x[0, 1]-x[0, 0],
            'route_B_minus_P_at_R_B': x[1, 1]-x[1, 0],
            'interaction': x[1, 1]-x[1, 0]-x[0, 1]+x[0, 0]}


def contrasts(x, field):
    sign = -1 if field.endswith('accuracy') else 1
    table = x[:8].reshape(2, 2, 2, -1)
    out = {'absolute/'+name: x[i] for i, name in enumerate(CONDITIONS)}
    for p, policy in enumerate(('full', 'P32')):
        out.update({policy+'/'+k: v for k, v in factorial(table[p]).items()})
    damage = sign*(table[1]-table[0])
    for r, rn in enumerate(('P', 'B')):
        for g, gn in enumerate(('P', 'B')):
            out['mask_damage/R_'+rn+'_G_'+gn] = damage[r, g]
    out.update({'mask_damage/'+k: v for k, v in factorial(damage).items()})
    necessity = sign*(x[10:14].reshape(2, 2, -1)-table[0])
    natural = np.stack([sign*(x[8+r]-table[0, r, r]) for r in range(2)])
    for r, rn in enumerate(('P', 'B')):
        out['S_effect/natural_R_'+rn] = natural[r]
        for g, gn in enumerate(('P', 'B')):
            out['S_effect/R_'+rn+'_G_'+gn] = necessity[r, g]
    out['S_partner_change/natural'] = natural[1]-natural[0]
    for g, name in enumerate(('P', 'B')):
        delta = necessity[1, g]-necessity[0, g]
        out['S_partner_change/fixed_route_'+name] = delta
        out['S_partner_change/fixed_'+name+'_minus_natural'] = delta-(natural[1]-natural[0])
    return out


class Statistics:
    def __init__(self, panel, subject, names):
        self.subject = np.asarray(subject)
        self.panel = np.asarray(panel)
        self.names = names
        self.fresh_groups = [np.flatnonzero((self.panel == 1) & (self.subject == k)) for k in range(2, 57)]
        self.old_groups = [np.flatnonzero((self.panel == 0) & (self.subject == k)) for k in range(2)]
        if any(len(g) != 8 for g in self.fresh_groups) or any(len(g) != 64 for g in self.old_groups):
            raise ValueError('Frozen subject population changed')
        draw = np.random.default_rng(164002).integers(0, 55, size=(2000, 55))
        self.fresh_weights = np.zeros((2000, 55), np.float64)
        np.add.at(self.fresh_weights, (np.arange(2000)[:, None], draw), 1/55)
        rng = np.random.default_rng(164003)
        self.old_draws = [rng.integers(0, len(g), size=(2000, len(g))) for g in self.old_groups]

    def stat(self, x, scope):
        x = np.asarray(x, np.float64)
        if x.shape != (568,) or not np.isfinite(x).all():
            raise ValueError('One finite paired value per question required')
        fresh = scope == 'fresh_primary'
        groups = self.fresh_groups if fresh else self.old_groups
        point_by_subject = np.array([x[g].mean() for g in groups])
        boot = self.fresh_weights @ point_by_subject if fresh else sum(
            x[g][draw].mean(1)/2 for g, draw in zip(groups, self.old_draws))
        ids = range(2, 57) if fresh else range(2)
        return {'point': float(point_by_subject.mean()), 'ci95': np.quantile(boot, [.025, .975]).tolist(),
                'subjects': len(groups), 'questions': sum(map(len, groups)), 'resamples': 2000,
                'seed': 164002 if fresh else 164003,
                'ci_unit': 'paired55subject cluster reweighting' if fresh else 'paired questions within2fixed subjects',
                'per_subject': {self.names[k]: {'point': float(point), 'questions': len(group)}
                                for k, point, group in zip(ids, point_by_subject, groups)}}


def summarize(a, names):
    values = metrics(a)
    stats = Statistics(a['panel'], a['subject'], names)
    result = {'experiment': 'E164', 'status': 'complete', 'conditions': list(CONDITIONS),
              'R_sources': ['P', 'B'], 'route_sources': ['P', 'B'],
              'definitions': {'source_effect': 'Left minus right; positive accuracy is better, negative loss is better.',
                              'damage': 'Loss: intervened minus full; accuracy: full minus intervened.',
                              'route': 'Full native gate-output trajectory before common mask; fixes actual support and weights.',
                              'scope': 'Fixed mature P/B parameter packages and input panels; not initialization population or unique mediation.'}}
    for scope in ('fresh_primary', 'legacy_secondary'):
        result[scope] = {field: {key: stats.stat(v, scope) for key, v in contrasts(x, field).items()}
                         for field, x in values.items()}
        result[scope]['first_answer_token_KL_vs_P_full'] = {
            c: stats.stat(a['first_answer_token_KL'][i], scope) for i, c in enumerate(CONDITIONS)}
    result['routing_diagnostics'] = {'fields': ['top7_overlap', 'selected_weight_L1', 'P_selected_mass', 'B_selected_mass'],
                                     'positions': ['all_actual_inputs', 'scored_candidate_positions'],
                                     'means': {scope: a['route_diagnostics'][:, a['panel'] == panel].mean(1).tolist()
                                               for scope, panel in [('fresh_primary', 1), ('legacy_secondary', 0)]},
                                     'not_causal_allocation_to_support_vs_weights': True}
    return result


def analyze():
    manifest = json.loads((ROOT/'manifest.json').read_text())
    if manifest['status'] != 'complete':
        raise ValueError('Complete terminal provenance required')
    item = manifest['raw']
    if sha(item['path']) != item['sha256']:
        raise ValueError('Raw changed')
    plan = json.loads((ROOT/'plan.json').read_text())
    if sha(ROOT/'plan.json') != manifest['plan_sha256']:
        raise ValueError('Plan changed')
    for name, expected in plan['source_sha256'].items():
        if sha(MOE/'scripts'/name) != expected:
            raise ValueError('Frozen source changed: '+name)
    result = summarize(arrays(item['path']), plan['subjects'])
    result.update(raw_sha256=item['sha256'], plan_sha256=manifest['plan_sha256'], analysis_source_sha256=sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    return {'status': 'complete', 'summary': str(ROOT/'summary.json')}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('mode', choices=('analyze',)); p.parse_args()
    print(json.dumps(analyze(), indent=2))
