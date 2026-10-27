"""E156 frozen 3x3 source cross: read-only raw analysis on CPU."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'results' / 'e156'
SOURCES = ('P', 'A', 'B')
POLICIES = ('full', 'receiverP32')
SEED = 156001


def sha256(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def log_softmax(x):
    x = np.asarray(x, dtype=np.float64)
    z = x - x.max(axis=-1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=-1, keepdims=True))


def scores(ll, gold, tokens, chars):
    """Return per-question metrics with arbitrary leading source/policy axes."""
    ll = np.asarray(ll, dtype=np.float64)
    q = np.arange(len(gold))
    return {
        'raw_accuracy': (ll.argmax(-1) == gold).astype(float),
        'per_char_accuracy': ((ll / chars).argmax(-1) == gold).astype(float),
        'choice_CE': -log_softmax(ll)[..., q, gold],
        'true_answer_token_NLL': -ll[..., q, gold] / tokens[q, gold],
    }


def question_stats(x, subject, selection):
    x = np.asarray(x, dtype=np.float64)
    if x.shape != subject.shape or selection.shape != subject.shape:
        raise ValueError('Statistics require one paired value per question')
    rng = np.random.default_rng(SEED)
    draws, means, details = [], [], {}
    for i, label in enumerate(('high_school_biology', 'high_school_mathematics')):
        v = x[selection & (subject == i)]
        if not len(v):
            raise ValueError(f'Cannot form two-subject macro: {label} has zero questions')
        b = v[rng.integers(0, len(v), (1000, len(v)))].mean(axis=1)
        means.append(v.mean()); draws.append(b)
        details[label] = {'point': float(v.mean()), 'question_ci95': np.quantile(b, [.025, .975]).tolist(), 'questions': len(v)}
    return {'point': float(np.mean(means)), 'question_ci95': np.quantile(np.mean(draws, axis=0), [.025, .975]).tolist(),
            'per_subject': details, 'question_count': int(selection.sum()), 'bootstrap_seed': SEED,
            'unit': 'paired questions within fixed subjects; not model-seed or subject-population CI'}


def source_contrast(x, accuracy=False):
    """A/B off-diagonal minus diagonal for loss; reverse for accuracy."""
    out = (x[1, 2] + x[2, 1] - x[1, 1] - x[2, 2]) / 2
    return -out if accuracy else out


def validate(a):
    required = {'candidate_loglikelihood': (3,3,2,128,4), 'native_candidate_loglikelihood': (3,2,128,4),
        'first_answer_token_KL_vs_P': (3,3,2,128), 'pruning_KL': (3,3,128),
        'native_first_answer_token_KL_vs_P': (3,2,128), 'native_pruning_KL': (3,128),
        'gold': (128,), 'subject': (128,), 'answer_tokens': (128,4), 'answer_chars': (128,4),
        'common_success': (128,), 'source_names': (3,), 'policies': (2,)}
    missing = set(required) - set(a.files)
    if missing: raise ValueError(f'Missing fields: {sorted(missing)}')
    for k, shape in required.items():
        if a[k].shape != shape: raise ValueError(f'{k}: expected {shape}, got {a[k].shape}')
    if tuple(a['source_names'].tolist()) != SOURCES or tuple(a['policies'].tolist()) != POLICIES:
        raise ValueError('Source or policy order mismatch')
    for k in ('candidate_loglikelihood', 'native_candidate_loglikelihood', 'first_answer_token_KL_vs_P', 'pruning_KL', 'native_first_answer_token_KL_vs_P', 'native_pruning_KL'):
        if not np.isfinite(a[k]).all(): raise ValueError(f'{k} contains non-finite values')
    for k in ('gold','subject','answer_tokens','answer_chars'):
        if a[k].dtype.kind not in 'iu': raise ValueError(f'{k} must be integer')
    if a['common_success'].dtype.kind != 'b': raise ValueError('common_success must be bool')
    if np.any((a['gold'] < 0) | (a['gold'] > 3)) or np.any(a['answer_tokens'] <= 0) or np.any(a['answer_chars'] <= 0):
        raise ValueError('Invalid gold or answer lengths')
    if np.bincount(a['subject'], minlength=2).tolist() != [64,64]: raise ValueError('Unexpected subject counts')
    if [int(np.sum(a['common_success'] & (a['subject']==i))) for i in (0,1)] != [36,8]:
        raise ValueError('Unexpected common-success subject counts')


def analyze():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    raw = Path(manifest['raw']['path'])
    if sha256(raw) != manifest['raw']['sha256']: raise ValueError('Raw SHA256 differs from manifest')
    with np.load(raw, allow_pickle=False) as f:
        validate(f)
        a = {k: f[k].copy() for k in f.files}
    subject, gold = a['subject'], a['gold']
    cross = scores(a['candidate_loglikelihood'], gold, a['answer_tokens'], a['answer_chars'])
    native = scores(a['native_candidate_loglikelihood'], gold, a['answer_tokens'], a['answer_chars'])
    cross['first_answer_token_KL_vs_P'] = a['first_answer_token_KL_vs_P'].astype(float)
    native['first_answer_token_KL_vs_P'] = a['native_first_answer_token_KL_vs_P'].astype(float)
    cross_lp = log_softmax(a['candidate_loglikelihood'])
    native_lp = log_softmax(a['native_candidate_loglikelihood'])
    cross_budget = {'accuracy_drop': cross['raw_accuracy'][:,:,0]-cross['raw_accuracy'][:,:,1],
        'per_char_accuracy_drop': cross['per_char_accuracy'][:,:,0]-cross['per_char_accuracy'][:,:,1],
        'choice_CE_increase': cross['choice_CE'][:,:,1]-cross['choice_CE'][:,:,0],
        'true_answer_token_NLL_increase': cross['true_answer_token_NLL'][:,:,1]-cross['true_answer_token_NLL'][:,:,0],
        'pruning_KL': a['pruning_KL'].astype(float),
        'choice_score_KL': (np.exp(cross_lp[:,:,0])*(cross_lp[:,:,0]-cross_lp[:,:,1])).sum(-1)}
    native_budget = {'accuracy_drop': native['raw_accuracy'][:,0]-native['raw_accuracy'][:,1],
        'per_char_accuracy_drop': native['per_char_accuracy'][:,0]-native['per_char_accuracy'][:,1],
        'choice_CE_increase': native['choice_CE'][:,1]-native['choice_CE'][:,0],
        'true_answer_token_NLL_increase': native['true_answer_token_NLL'][:,1]-native['true_answer_token_NLL'][:,0],
        'pruning_KL': a['native_pruning_KL'].astype(float),
        'choice_score_KL': (np.exp(native_lp[:,0])*(native_lp[:,0]-native_lp[:,1])).sum(-1)}
    result = {'experiment':'E156', 'status':'complete', 'raw_sha256':manifest['raw']['sha256'],
        'analysis_source_sha256':sha256(__file__), 'source_order':list(SOURCES), 'policy_order':list(POLICIES),
        'definitions':{'contrast':'loss off-diagonal minus diagonal; accuracy diagonal minus off-diagonal, A/B only',
            'budget_contrast':'off-diagonal minus diagonal for positive damage measures',
            'choice_score_KL':'KL(full candidate-score softmax || masked candidate-score softmax), not full-vocabulary LM KL',
            'common_native_success':'E155 native P/A/B all correct; selected without E156 intervention outcomes'}, 'scopes':{}}
    for scope, selection in [('all_questions',np.ones(128,dtype=bool)), ('common_native_success',a['common_success'])]:
        stat = lambda x: question_stats(x,subject,selection)
        row = {'cross':{}, 'native':{}, 'AB_source_contrasts':{'policies':{},'budget':{}}, 'relative_to_PP':{}}
        for i,r in enumerate(SOURCES):
            for j,s in enumerate(SOURCES):
                key=r+s; row['cross'][key]={}; row['relative_to_PP'][key]={}
                for p,policy in enumerate(POLICIES):
                    entry={k:stat(v[i,j,p]) for k,v in cross.items()}
                    if p==1: entry.update({k:stat(v[i,j]) for k,v in cross_budget.items()})
                    row['cross'][key][policy]=entry
                    row['relative_to_PP'][key][policy]={k:stat(v[i,j,p]-v[0,0,p]) for k,v in cross.items()}
        for i,s in enumerate(SOURCES):
            row['native'][s]={}
            for p,policy in enumerate(POLICIES):
                entry={k:stat(v[i,p]) for k,v in native.items()}
                if p==1: entry.update({k:stat(v[i]) for k,v in native_budget.items()})
                row['native'][s][policy]=entry
        for p,policy in enumerate(POLICIES):
            row['AB_source_contrasts']['policies'][policy]={k:stat(source_contrast(v[:,:,p], accuracy=k in ('raw_accuracy','per_char_accuracy'))) for k,v in cross.items()}
        row['AB_source_contrasts']['budget']={k:stat(source_contrast(v)) for k,v in cross_budget.items()}
        result['scopes'][scope]=row
    (ROOT/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    return result


def self_test():
    gold=np.array([0,1,0,1]); tokens=np.ones((4,4),dtype=int); chars=tokens.copy()
    logits=np.array([[3.,0,0,0],[0,3.,0,0],[3.,0,0,0],[0,3.,0,0]])
    m=scores(logits,gold,tokens,chars)
    assert np.all(m['raw_accuracy']==1) and np.allclose(m['choice_CE'],np.log1p(3*np.exp(-3)))
    assert np.all(m['true_answer_token_NLL']==-3)
    x=np.zeros((3,3,4)); x[1,2]=4; x[2,1]=2; x[1,1]=1; x[2,2]=3
    assert np.all(source_contrast(x)==1) and np.all(source_contrast(x,True)==-1)
    z=question_stats(np.array([0.,1.,0.,1.]),np.array([0,0,1,1]),np.ones(4,dtype=bool))
    assert z['point']==.5 and z['question_count']==4 and z['per_subject']['high_school_biology']['questions']==2
    assert np.allclose(log_softmax(logits).sum(-1), 4*(-3-np.log1p(3*np.exp(-3)))+3)
    return {'status':'passed','checks':['known_candidate_scores','source_contrast_sign_and_PP_exclusion','stratified_macro','logsoftmax']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('mode',choices=('self-test','analyze')); args=parser.parse_args()
    out=self_test() if args.mode=='self-test' else analyze()
    print(json.dumps(out if args.mode=='self-test' else {'status':out['status'],'summary':str(ROOT/'summary.json')},indent=2))
