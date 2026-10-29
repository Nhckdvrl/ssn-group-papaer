"""Frozen E165 source contrasts; paired55-subject inference, no model loading."""
import itertools
import json
from pathlib import Path
import hashlib

import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'results/e165'
CASES = tuple(itertools.product(range(2), repeat=3))
CONDITIONS = tuple('D_'+'PA'[d]+'_G_'+'PA'[g]+'_E_'+'PA'[e]+'_'+p
                   for p in ('full', 'P16') for d, g, e in CASES) + tuple(
    'E_'+e+'_route_'+g+'_'+p for p in ('full', 'P16') for e, g in [('P', 'A'), ('A', 'P')]) + tuple(
    'native_'+r+'_random'+str(k) for r in ('P', 'A') for k in range(3))
FIELDS = ('raw_accuracy', 'per_char_accuracy', 'choice_CE', 'true_answer_token_NLL')


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def arrays(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k].copy() for k in z.files}


def metrics(a):
    ll = a['candidate_loglikelihood']; q = np.arange(440)
    if ll.shape != (26, 440, 4) or not np.isfinite(ll).all() or tuple(a['conditions']) != CONDITIONS:
        raise ValueError('Require the complete frozen26-condition population')
    shifted = ll-ll.max(-1, keepdims=True)
    logp = shifted-np.log(np.exp(shifted).sum(-1, keepdims=True))
    return {'raw_accuracy': (ll.argmax(-1) == a['gold']).astype(float),
            'per_char_accuracy': ((ll/a['answer_chars']).argmax(-1) == a['gold']).astype(float),
            'choice_CE': -logp[:, q, a['gold']],
            'true_answer_token_NLL': -ll[:, q, a['gold']]/a['answer_tokens'][q, a['gold']]}


def factorial(x):
    return {'natural_A_minus_P': x[1, 1]-x[0, 0],
            'E_A_minus_P_at_route_P': x[1, 0]-x[0, 0],
            'E_A_minus_P_at_route_A': x[1, 1]-x[0, 1],
            'route_A_minus_P_at_E_P': x[0, 1]-x[0, 0],
            'route_A_minus_P_at_E_A': x[1, 1]-x[1, 0],
            'interaction': x[1, 1]-x[1, 0]-x[0, 1]+x[0, 0]}


def contrasts(x, field):
    sign = -1 if field.endswith('accuracy') else 1
    result = {'absolute/'+name: x[i] for i, name in enumerate(CONDITIONS)}
    cube = x[:16].reshape(2, 2, 2, 2, -1)
    route = np.stack([np.stack([np.stack([x[8*p], x[16+2*p]]),
                                    np.stack([x[17+2*p], x[8*p+1]])]) for p in range(2)])
    for p, policy in enumerate(('full', 'P16')):
        for axis, name in enumerate(('D', 'G', 'E')):
            for fixed in itertools.product(range(2), repeat=2):
                low = list(fixed); low.insert(axis, 0); high = low.copy(); high[axis] = 1
                result[policy+'/'+name+'_A_minus_P_fixed_'+''.join(map(str, fixed))] = (
                    cube[(p, *high)]-cube[(p, *low)])
        for axes in itertools.combinations(range(3), 2):
            other = next(i for i in range(3) if i not in axes)
            for fixed in range(2):
                value = np.zeros(440)
                for i, j in itertools.product(range(2), repeat=2):
                    case = [0, 0, 0]; case[axes[0]] = i; case[axes[1]] = j; case[other] = fixed
                    value += (-1)**(2-i-j)*cube[(p, *case)]
                key = policy+'/'+'DGE'[axes[0]]+'_x_'+'DGE'[axes[1]]+'_other_'+str(fixed)
                result[key] = value
        result[policy+'/D_x_MoE_matching_cost'] = sign*.5*(
            cube[p, 0, 1, 1]+cube[p, 1, 0, 0]-cube[p, 0, 0, 0]-cube[p, 1, 1, 1])
        result[policy+'/three_way'] = sum((-1)**(3-sum(case))*cube[(p, *case)] for case in CASES)
        result.update({policy+'/actual_route/'+key: value for key, value in factorial(route[p]).items()})
    for case in CASES:
        result['mask_damage/'+''.join(map(str, case))] = sign*(cube[(1, *case)]-cube[(0, *case)])
    result.update({'mask_damage/actual_route/'+key: value for key, value in factorial(sign*(route[1]-route[0])).items()})
    for r, name in enumerate(('P', 'A')):
        index = 7*r
        random = x[20+3*r:23+3*r].mean(0)
        result['native/'+name+'/selected_damage'] = sign*(x[index+8]-x[index])
        result['native/'+name+'/random_mean_damage'] = sign*(random-x[index])
        result['native/'+name+'/random_minus_selected_value'] = sign*(random-x[index+8])
    result['native/A_minus_P_full'] = x[7]-x[0]
    result['native/A_minus_P_selected'] = x[15]-x[8]
    result['native/A_minus_P_selected_damage'] = sign*((x[15]-x[7])-(x[8]-x[0]))
    return result


class Statistics:
    def __init__(self, subject, names):
        self.names = names
        self.groups = [np.flatnonzero(subject == i) for i in range(55)]
        if any(len(g) != 8 for g in self.groups):
            raise ValueError('Frozen subject population changed')
        draws = np.random.default_rng(165002).integers(0, 55, (2000, 55))
        self.weights = np.zeros((2000, 55))
        np.add.at(self.weights, (np.arange(2000)[:, None], draws), 1/55)

    def stat(self, x):
        if x.shape != (440,) or not np.isfinite(x).all():
            raise ValueError('Require one finite paired value per question')
        points = np.array([x[g].mean() for g in self.groups])
        boot = self.weights @ points
        return {'point': float(points.mean()), 'ci95': np.quantile(boot, [.025, .975]).tolist(),
                'subjects': 55, 'questions': 440, 'resamples': 2000, 'seed': 165002,
                'ci_unit': 'paired55subject cluster reweighting, not training seeds',
                'per_subject': {name: {'point': float(p), 'questions': 8} for name, p in zip(self.names, points)}}


def summarize(a, names):
    stats = Statistics(a['subject'], names)
    result = {'status': 'complete', 'experiment': 'E165', 'conditions': list(CONDITIONS),
              'scope': 'Mature public OLMoE pre/post ordinary annealing; same55 text subjects, no independent seed population.',
              'definitions': {'source_change': 'A minus P; negative loss and positive accuracy are better.',
                              'matching_cost_and_damage': 'Positive means worse, including accuracy.',
                              'selection_value': 'Random-pool damage minus selected-pool damage; positive means useful selection.',
                              'route': 'Actual full support and weights; other responses endogenous.',
                              'P16': 'Common parent-calibrated pool of16/64; native pool normalization.'}}
    for field, x in metrics(a).items():
        result[field] = {key: stats.stat(value) for key, value in contrasts(x, field).items()}
    result['first_answer_token_KL_vs_P_full'] = {
        name: stats.stat(a['first_answer_token_KL'][i]) for i, name in enumerate(CONDITIONS)}
    return result


def analyze():
    manifest = json.loads((ROOT/'manifest.json').read_text()); plan = json.loads((ROOT/'plan.json').read_text())
    if manifest['status'] != 'complete' or sha(ROOT/'plan.json') != manifest['plan_sha256']:
        raise ValueError('Complete pinned provenance required')
    if sha(manifest['raw']['path']) != manifest['raw']['sha256']:
        raise ValueError('Raw changed')
    for name, expected in plan['source_sha256'].items():
        if sha(ROOT.parents[1]/'scripts'/name) != expected:
            raise ValueError('Frozen source changed: '+name)
    result = summarize(arrays(manifest['raw']['path']), plan['subjects'])
    result.update(raw_sha256=manifest['raw']['sha256'], plan_sha256=manifest['plan_sha256'],
                  analysis_source_sha256=sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': 'complete', 'summary': str(ROOT/'summary.json')}))


if __name__ == '__main__':
    analyze()
