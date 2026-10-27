"""Paired CIs for the four predeclared E156 transfer comparisons."""
import hashlib
import json
from pathlib import Path

import numpy as np
import e156_analyze as core

ROOT = Path(__file__).resolve().parents[1] / 'results' / 'e156'
OUT = ROOT / 'transfer_contrasts.json'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def delta(left, right):
    """Positive values indicate a larger left-hand metric or damage."""
    return np.asarray(left, dtype=float) - np.asarray(right, dtype=float)


def metrics_and_damage(ll, first_kl, pruning_kl, gold, tokens, chars):
    metrics = core.scores(ll, gold, tokens, chars)
    metrics['first_answer_token_KL_vs_P'] = first_kl.astype(float)
    lp = core.log_softmax(ll)
    damage = {
        'accuracy_drop': metrics['raw_accuracy'][..., 0, :] - metrics['raw_accuracy'][..., 1, :],
        'per_char_accuracy_drop': metrics['per_char_accuracy'][..., 0, :] - metrics['per_char_accuracy'][..., 1, :],
        'choice_CE_increase': metrics['choice_CE'][..., 1, :] - metrics['choice_CE'][..., 0, :],
        'true_answer_token_NLL_increase': metrics['true_answer_token_NLL'][..., 1, :] - metrics['true_answer_token_NLL'][..., 0, :],
        'pruning_KL': pruning_kl.astype(float),
        'choice_score_KL': (np.exp(lp[..., 0, :, :]) * (lp[..., 0, :, :] - lp[..., 1, :, :])).sum(-1),
    }
    return metrics, damage


def analyze():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    budget = json.loads((ROOT / 'budget.json').read_text())
    summary = json.loads((ROOT / 'summary.json').read_text())
    if manifest.get('status') != 'complete' or not budget.get('attempts') or any(x.get('status') != 'complete' for x in budget['attempts']):
        raise ValueError('Complete manifest and all budget attempts required')
    if summary.get('experiment') != 'E156' or summary.get('status') != 'complete':
        raise ValueError('Complete E156 summary required')
    path = Path(manifest['raw']['path'])
    digest = sha(path)
    if digest != manifest['raw']['sha256'] or digest != summary['raw_sha256']:
        raise ValueError('Raw/manifest/summary SHA256 mismatch')
    if summary.get('analysis_source_sha256') != sha(core.__file__):
        raise ValueError('Frozen analysis code differs from summary')
    with np.load(path, allow_pickle=False) as f:
        core.validate(f)
        a = {k: f[k].copy() for k in f.files}
    g, t, c = a['gold'], a['answer_tokens'], a['answer_chars']
    cross, cross_damage = metrics_and_damage(a['candidate_loglikelihood'], a['first_answer_token_KL_vs_P'], a['pruning_KL'], g, t, c)
    native, native_damage = metrics_and_damage(a['native_candidate_loglikelihood'], a['native_first_answer_token_KL_vs_P'], a['native_pruning_KL'], g, t, c)
    result = {'experiment':'E156', 'status':'complete', 'raw_sha256':digest,
              'summary_sha256':sha(ROOT/'summary.json'), 'manifest_sha256':sha(ROOT/'manifest.json'),
              'budget_sha256':sha(ROOT/'budget.json'), 'analysis_source_sha256':sha(__file__),
              'purpose':'Paired CI completion for E156 card predeclared individual/joint transfer and receiver-interface comparisons; no new core hypothesis.',
              'direction':'left minus right for every metric; accuracy damage is full minus masked and loss damage is masked minus full',
              'choice_score_KL':'KL over the four normalized candidate scores; not full-vocabulary LM KL',
              'scopes':{}}
    for scope, selection in [('all_questions',np.ones(128,dtype=bool)),('common_native_success',a['common_success'])]:
        stat=lambda x: core.question_stats(x,a['subject'],selection)
        rows={}
        for i, donor in [(1,'A'),(2,'B')]:
            pairs=[(f'R{donor}_SP_minus_PP',(i,0),'cross',(0,0)),
                   (f'RP_S{donor}_minus_PP',(0,i),'cross',(0,0)),
                   (f'R{donor}_S{donor}_minus_PP',(i,i),'cross',(0,0)),
                   (f'R{donor}_S{donor}_minus_native_{donor}',(i,i),'native',i)]
            for label,left,kind,right in pairs:
                row={'left':{'R':donor if left[0] else 'P','S':donor if left[1] else 'P','receiver_DG':'P'},
                     'right':{'R':'P','S':'P','receiver_DG':'P'} if kind=='cross' else {'native':donor},
                     'policies':{},'full_to_masked_damage':{}}
                for p,policy in enumerate(core.POLICIES):
                    row['policies'][policy]={key:stat(delta(v[left[0],left[1],p], (cross[key][right[0],right[1],p] if kind=='cross' else native[key][right,p]))) for key,v in cross.items()}
                row['full_to_masked_damage']={key:stat(delta(v[left[0],left[1]], (cross_damage[key][right[0],right[1]] if kind=='cross' else native_damage[key][right]))) for key,v in cross_damage.items()}
                rows[label]=row
        result['scopes'][scope]=rows
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    return OUT


def self_test():
    assert np.array_equal(delta(np.array([4,1]),np.array([1,3])),[3,-2])
    v=np.array([1.,2.,3.,4.]); topics=np.array([0,0,1,1]); keep=np.ones(4,dtype=bool)
    assert core.question_stats(delta(v,np.ones(4)),topics,keep)['point']==1.5
    return True


if __name__ == '__main__':
    print(analyze())
