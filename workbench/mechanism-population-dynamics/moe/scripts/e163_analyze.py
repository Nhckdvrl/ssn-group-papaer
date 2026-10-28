"""E163 input-paired statistics. This module never imports or runs a model."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]/'results/e163'
RAW = Path.home()/'mechpop_cache/e163_message_geometry'
MODELS = ('P', 'A', 'B', 'F')
TARGETS = ('R', 'S', 'RS')
MODES = ('zero', 'norm_mean', 'gram_mean', 'gram_random0', 'gram_random1')
CONDITIONS = ('native',) + tuple(t+'_'+m for t in TARGETS for m in MODES)
RULES = ('raw', 'norm', 'gram')
LM_FIELDS = ('nll', 'forward_KL', 'reverse_KL', 'argmax_agreement')
TASK_FIELDS = ('raw_accuracy', 'per_char_accuracy', 'choice_CE', 'true_answer_token_NLL')
TOPICS = ('high_school_biology', 'high_school_mathematics')


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def arrays(path):
    with np.load(path, allow_pickle=False) as f:
        return {k: f[k].copy() for k in f.files}


class Statistics:
    """One fixed set of paired draws for every condition/history contrast."""
    def __init__(self, subjects, groups):
        self.subjects = np.asarray(subjects)
        self.groups = np.asarray(groups)
        if self.subjects.shape != (128,) or self.groups.shape != (64,):
            raise ValueError('Unexpected primary population')
        rng = np.random.default_rng(163001)
        self.subject_indices, self.question_draws = [], []
        for i in range(2):
            idx = np.flatnonzero(self.subjects == i)
            if len(idx) != 64:
                raise ValueError('Expected 64 questions in each fixed subject')
            self.subject_indices.append(idx)
            self.question_draws.append(idx[rng.integers(0, 64, (1000, 64))])
        unique = sorted(set(groups))
        if len(unique) != 20:
            raise ValueError('Expected 20 file clusters')
        cluster_indices = [np.flatnonzero(self.groups == g) for g in unique]
        draws = np.random.default_rng(163002).integers(0, 20, (1000, 20))
        self.file_weights = np.zeros((1000, 64))
        for row, sampled in enumerate(draws):
            for cluster in sampled:
                self.file_weights[row, cluster_indices[cluster]] += 1
        self.file_weights /= self.file_weights.sum(-1, keepdims=True)

    def question(self, values, selected=None):
        x = np.asarray(values, dtype=float)
        if x.shape != (128,) or not np.isfinite(x).all():
            raise ValueError('Expected one finite paired value per question')
        if selected is not None:
            mask = np.asarray(selected, dtype=bool)
            sub = [x[idx[mask[idx]]] for idx in self.subject_indices]
            return {'point': float(np.mean([v.mean() for v in sub])) if all(len(v) for v in sub) else None,
                    'pooled_point': float(x[mask].mean()) if mask.any() else None,
                    'count': int(mask.sum()), 'subject_counts': [len(v) for v in sub],
                    'ci': 'not computed after common-success selection'}
        boot = np.mean([x[draw].mean(-1) for draw in self.question_draws], axis=0)
        return {'point': float(x.mean()), 'ci95': np.quantile(boot, [.025, .975]).tolist(),
                'per_subject': {name: {'point': float(x[idx].mean()),
                    'ci95': np.quantile(x[draw].mean(-1), [.025, .975]).tolist(), 'count': 64}
                    for name, idx, draw in zip(TOPICS, self.subject_indices, self.question_draws)},
                'count': 128, 'seed': 163001, 'resamples': 1000}

    def file(self, values):
        x = np.asarray(values, dtype=float)
        if x.shape != (64,) or not np.isfinite(x).all():
            raise ValueError('Expected one finite paired value per window')
        boot = self.file_weights @ x
        return {'point': float(x.mean()), 'file_ci95': np.quantile(boot, [.025, .975]).tolist(),
                'windows': 64, 'file_clusters': 20, 'seed': 163002, 'resamples': 1000,
                'unit': 'equal-window point; paired file-cluster bootstrap, not training seeds'}


def task_metrics(ll, gold, tokens, chars):
    q = np.arange(128)
    shifted = ll - ll.max(-1, keepdims=True)
    lp = shifted - np.log(np.exp(shifted).sum(-1, keepdims=True))
    return {'raw_accuracy': (ll.argmax(-1) == gold).astype(float),
            'per_char_accuracy': ((ll/chars).argmax(-1) == gold).astype(float),
            'choice_CE': -lp[..., q, gold],
            'true_answer_token_NLL': -ll[..., q, gold]/tokens[q, gold]}


def damage_sign(field):
    return -1 if field.endswith('accuracy') or field == 'argmax_agreement' else 1


def token_means(values, valid):
    mask = np.asarray(valid, dtype=bool)
    if values.shape != (16, 64, 512, 4) or mask.shape != (64, 512):
        raise ValueError('Unexpected LM axes')
    return (values.astype(np.float64)*mask[None, :, :, None]).sum(-2)/mask.sum(-1)[None, :, None]


def validate(native, cross, refs):
    for name in MODELS:
        a = native[name]
        for key, shape in {'lm_metrics': (16,64,512,4), 'candidate_loglikelihood': (16,128,4),
                           'first_answer_token_KL': (16,128)}.items():
            if a[key].shape != shape or not np.isfinite(a[key]).all():
                raise ValueError('Invalid native array '+name+'/'+key)
        if tuple(a['conditions']) != CONDITIONS:
            raise ValueError('Native condition order changed')
        for key in ('gold', 'subject', 'answer_tokens', 'answer_chars'):
            if not np.array_equal(a[key], refs[key]):
                raise ValueError('Frozen task population changed')
    if cross['candidate_loglikelihood'].shape != (3,3,3,128,4) or tuple(cross['rules']) != RULES:
        raise ValueError('Unexpected producer-consumer matrix')
    if not np.isfinite(cross['candidate_loglikelihood']).all():
        raise ValueError('Nonfinite cross result')
    if not np.array_equal(cross['candidate_loglikelihood'][0], refs['cross_raw_LL']):
        raise ValueError('Raw E160 matrix failed exact replay')


def summarize(native, cross, refs, groups):
    validate(native, cross, refs)
    stats = Statistics(refs['subject'], groups)
    qstat, fstat = stats.question, stats.file
    task = task_metrics(np.stack([native[n]['candidate_loglikelihood'] for n in MODELS]),
                        refs['gold'], refs['answer_tokens'], refs['answer_chars'])
    lm = np.stack([token_means(native[n]['lm_metrics'], refs['lm_valid']) for n in MODELS])
    out = {'experiment': 'E163', 'status': 'complete', 'models': list(MODELS),
           'conditions': list(CONDITIONS), 'targets': list(TARGETS), 'rules': list(RULES),
           'scope': 'Fixed mature published paths and P receiver; input CIs, not independent initialization or formation dynamics',
           'native': {'task': {}, 'LM': {}}, 'history_contrasts': {'task': {}, 'LM': {}},
           'cross': {}, 'common_success': {}}
    for domain, data, func in [('task', task, qstat), ('LM', {f: lm[..., k] for k, f in enumerate(LM_FIELDS)}, fstat)]:
        for field, values in data.items():
            sign = damage_sign(field)
            damage = sign*(values - values[:, :1])
            out['native'][domain][field] = {}
            for i, name in enumerate(MODELS):
                record = {'absolute': {c: func(values[i,j]) for j,c in enumerate(CONDITIONS)},
                          'damage': {c: func(damage[i,j]) for j,c in enumerate(CONDITIONS[1:],1)},
                          'zero_minus_proxy_damage': {}, 'norm_minus_gram_damage': {}}
                for target in TARGETS:
                    z = CONDITIONS.index(target+'_zero')
                    record['zero_minus_proxy_damage'][target] = {
                        mode: func(damage[i,z]-damage[i,CONDITIONS.index(target+'_'+mode)]) for mode in MODES[1:]}
                    record['norm_minus_gram_damage'][target] = func(
                        damage[i,CONDITIONS.index(target+'_norm_mean')]-damage[i,CONDITIONS.index(target+'_gram_mean')])
                out['native'][domain][field][name] = record
            out['history_contrasts'][domain][field] = {}
            for j in range(1, 4):
                for i in range(j):
                    key = MODELS[j]+'_minus_'+MODELS[i]
                    out['history_contrasts'][domain][field][key] = {
                        'native_quality': func(values[j,0]-values[i,0]),
                        'damage': {c: func(damage[j,k]-damage[i,k]) for k,c in enumerate(CONDITIONS[1:],1)}}
    out['native']['task']['first_answer_token_KL'] = {
        n: {c: qstat(native[n]['first_answer_token_KL'][j]) for j,c in enumerate(CONDITIONS)} for n in MODELS}
    selected = np.all(np.stack([native[n]['candidate_loglikelihood'][0].argmax(-1) == refs['gold'] for n in MODELS]), axis=0)
    if not np.array_equal(selected, refs['common_success_mask']):
        raise ValueError('Original complete-model common-success set changed')
    out['common_success'] = {'count': int(selected.sum()), 'subject_counts': [int((selected&(refs['subject']==i)).sum()) for i in range(2)],
        'mask': selected.tolist(), 'ci': 'not computed', 'task': {}}
    for field, values in task.items():
        out['common_success']['task'][field] = {n: {c: qstat(values[i,j],selected) for j,c in enumerate(CONDITIONS)} for i,n in enumerate(MODELS)}
    cm = task_metrics(cross['candidate_loglikelihood'], refs['gold'], refs['answer_tokens'], refs['answer_chars'])
    off = ~np.eye(3, dtype=bool)
    for field, x in cm.items():
        costs = damage_sign(field)*(x[:,off].mean(1)-np.stack([x[:,i,i] for i in range(3)]).mean(0))
        out['cross'][field] = {
            'absolute': {rule: {consumer+'_'+producer: qstat(x[k,i,j])
                for i,consumer in enumerate(MODELS[:3]) for j,producer in enumerate(MODELS[:3])}
                for k,rule in enumerate(RULES)},
            'matching_cost': {rule: qstat(costs[k]) for k,rule in enumerate(RULES)},
            'rule_contrasts': {RULES[j]+'_minus_'+RULES[i]: qstat(costs[j]-costs[i]) for j in range(1,3) for i in range(j)}}
    out['cross']['first_answer_token_KL'] = {rule: {consumer+'_'+producer: qstat(cross['first_answer_token_KL'][k,i,j])
        for i,consumer in enumerate(MODELS[:3]) for j,producer in enumerate(MODELS[:3])} for k,rule in enumerate(RULES)}
    out['geometry'] = {name: {'LM_maxima_over_batches_layers': native[name]['LM_geometry'].max((1,2)).tolist(),
        'task_maxima_over_questions_layers': native[name]['task_geometry'].max((1,2)).tolist(),
        'native_LM_geometry_batch_mean': native[name]['native_LM_geometry'].mean(0).tolist(),
        'interpretation': 'Norm/parallel energy and numerical diagnostics; not prediction responsibility fractions'} for name in MODELS}
    return out


def analyze():
    plan = read(ROOT/'plan.json')
    manifests = {name: read(ROOT/('manifest_'+name+'.json')) for name in MODELS}
    manifests['cross'] = read(ROOT/'manifest_cross.json')
    for name, m in manifests.items():
        if m['status'] != 'complete' or m['plan_sha256'] != sha(ROOT/'plan.json') or m['source_sha256'] != plan['source_sha256']:
            raise ValueError('Result lacks matching complete provenance '+name)
        if sha(m['raw']['path']) != m['raw']['sha256']:
            raise ValueError('Raw changed '+name)
    for group in ('PAB', 'F'):
        budget = read(ROOT/('budget_'+group+'.json'))
        if budget['attempts'][-1]['status'] != 'complete' or sum(a['gpu_seconds'] for a in budget['attempts']) > plan['gpu_limits'][group]:
            raise ValueError('Incomplete or exceeded resource ledger')
    for name, expected in plan['source_sha256'].items():
        if sha(ROOT.parents[1]/'scripts'/name) != expected:
            raise ValueError('Frozen numerical source changed '+name)
    refs = arrays(plan['references']['path'])
    if sha(plan['references']['path']) != plan['references']['sha256']:
        raise ValueError('Reference changed')
    native = {name: arrays(manifests[name]['raw']['path']) for name in MODELS}
    cross = arrays(manifests['cross']['raw']['path'])
    summary = summarize(native, cross, refs, plan['file_groups'])
    summary.update(raw_sha256={name: m['raw']['sha256'] for name,m in manifests.items()},
                   plan_sha256=sha(ROOT/'plan.json'), analysis_source_sha256=sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    return {'status': 'complete', 'summary': str(ROOT/'summary.json')}


def self_test():
    groups = np.array([str(i%20) for i in range(64)])
    subjects = np.repeat([0,1],64)
    s = Statistics(subjects,groups)
    assert s.question(np.ones(128))['ci95'] == [1.,1.]
    assert np.allclose(s.file(np.ones(64))['file_ci95'],[1.,1.])
    assert s.file(np.arange(64.))['point'] == 31.5
    ll = np.zeros((2,128,4));ll[0,:,0] = 1;ll[1,:,1] = 1
    m = task_metrics(ll,np.zeros(128,int),np.ones((128,4)),np.ones((128,4)))
    assert np.all(m['raw_accuracy'][0] == 1) and np.all(m['raw_accuracy'][1] == 0)
    x = np.arange(27*128).reshape(3,3,3,128).astype(float)
    off = ~np.eye(3,dtype=bool)
    a = x[:,off].mean(1)-np.stack([x[:,i,i] for i in range(3)]).mean(0)
    b = np.array([[np.mean([x[k,i,j,q] for i in range(3) for j in range(3) if i!=j])-
                   np.mean([x[k,i,i,q] for i in range(3)]) for q in range(128)] for k in range(3)])
    assert np.array_equal(a,b)
    return {'status':'passed','constant_known_answers':True,'unequal_cluster_window_point':True,
            'task_sign_and_advanced_axes':True,'source_matrix_diagonal_axes':True}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('analyze','self-test'))
    args = p.parse_args()
    print(json.dumps(analyze() if args.mode=='analyze' else self_test(),indent=2))
