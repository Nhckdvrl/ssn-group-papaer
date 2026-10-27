"""Independent CPU audit of completed E156 raw arrays and published summary."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

SOURCE = ('P', 'A', 'B')
POLICY = ('full', 'receiverP32')
SUBJECT = ('high_school_biology', 'high_school_mathematics')
ATOL = 1e-10


def digest(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def per_question(ll, gold, lengths, chars):
    """Compute metrics independently from candidate log-likelihoods."""
    ll = np.asarray(ll, dtype=np.float64)
    q = np.arange(gold.size)
    true_ll = ll[..., q, gold]
    maxll = ll.max(axis=-1)
    log_partition = maxll + np.log(np.exp(ll - maxll[..., None]).sum(axis=-1))
    return {
        'raw_accuracy': (np.argmax(ll, axis=-1) == gold).astype(float),
        'per_char_accuracy': (np.argmax(ll / chars, axis=-1) == gold).astype(float),
        'choice_CE': log_partition - true_ll,
        'true_answer_token_NLL': -true_ll / lengths[q, gold],
    }


def candidate_kl(full, masked):
    def logprobs(x):
        xmax = np.max(x, axis=-1, keepdims=True)
        centered = x - xmax
        return centered - np.log(np.exp(centered).sum(axis=-1, keepdims=True))
    lp, lq = logprobs(full), logprobs(masked)
    return np.sum(np.exp(lp) * (lp - lq), axis=-1)


def stratified(x, subject, include):
    """Common resampling for paired per-question differences, within subject."""
    generator = np.random.default_rng(156001)
    points, samples, components = [], [], []
    for group in (0, 1):
        values = np.asarray(x)[include & (subject == group)]
        if values.size == 0:
            raise ValueError('empty subject')
        picks = generator.integers(0, len(values), size=(1000, len(values)))
        draws = values[picks].mean(axis=1)
        points.append(float(values.mean()))
        samples.append(draws)
        components.append((len(values), float(values.mean()), np.quantile(draws, [0.025, 0.975])))
    return float(np.mean(points)), np.quantile((samples[0] + samples[1]) / 2, [0.025, 0.975]), components


def ab_contrast(x, reverse=False):
    # Apply to per-question quantities, preserving pairing; P row/column excluded.
    d = ((x[1, 2] - x[1, 1]) + (x[2, 1] - x[2, 2])) / 2
    return -d if reverse else d


def require_inputs(raw_path, summary_path, budget_path, manifest_path):
    budget = json.loads(budget_path.read_text())
    attempts = budget.get('attempts', [])
    if not attempts or any(a.get('status') != 'complete' for a in attempts):
        raise ValueError('E156 budget is not complete; refuse to read scientific results')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('status') != 'complete':
        raise ValueError('E156 manifest is not complete')
    if Path(manifest['raw']['path']).resolve() != raw_path.resolve() or digest(raw_path) != manifest['raw']['sha256']:
        raise ValueError('Raw path/hash does not match completed manifest')
    summary = json.loads(summary_path.read_text())
    if summary.get('status') != 'complete' or summary.get('raw_sha256') != manifest['raw']['sha256']:
        raise ValueError('Summary does not identify completed raw')
    return summary


def verify(raw, summary):
    expected_shapes = {
        'candidate_loglikelihood': (3,3,2,128,4), 'native_candidate_loglikelihood': (3,2,128,4),
        'first_answer_token_KL_vs_P': (3,3,2,128), 'pruning_KL': (3,3,128),
        'native_first_answer_token_KL_vs_P': (3,2,128), 'native_pruning_KL': (3,128),
        'gold': (128,), 'subject': (128,), 'answer_tokens': (128,4), 'answer_chars': (128,4),
        'common_success': (128,), 'source_names': (3,), 'policies': (2,),
    }
    for key, shape in expected_shapes.items():
        if key not in raw or raw[key].shape != shape:
            raise ValueError(f'missing or malformed {key}, expected {shape}')
    if tuple(raw['source_names']) != SOURCE or tuple(raw['policies']) != POLICY:
        raise ValueError('source or policy order differs')
    if tuple(summary.get('source_order', ())) != SOURCE or tuple(summary.get('policy_order', ())) != POLICY:
        raise ValueError('summary source or policy order differs')
    g, sub, lens, chars = (raw[k] for k in ('gold','subject','answer_tokens','answer_chars'))
    if any(v.dtype.kind not in 'iu' for v in (g,sub,lens,chars)) or np.any((g<0)|(g>3)) or np.any(lens<=0) or np.any(chars<=0):
        raise ValueError('invalid answers or token/character lengths')
    if np.bincount(sub, minlength=2).tolist() != [64,64]:
        raise ValueError('unexpected subject counts')
    cross_ll = np.asarray(raw['candidate_loglikelihood'], dtype=np.float64)
    native_ll = np.asarray(raw['native_candidate_loglikelihood'], dtype=np.float64)
    for key in ('candidate_loglikelihood','native_candidate_loglikelihood','first_answer_token_KL_vs_P',
                'pruning_KL','native_first_answer_token_KL_vs_P','native_pruning_KL'):
        if not np.isfinite(raw[key]).all():
            raise ValueError(f'nonfinite {key}')
    for lhs, rhs in ((cross_ll[0,0],native_ll[0]),
                     (raw['first_answer_token_KL_vs_P'][0,0],raw['native_first_answer_token_KL_vs_P'][0]),
                     (raw['pruning_KL'][0,0],raw['native_pruning_KL'][0])):
        if not np.array_equal(lhs,rhs):
            raise ValueError('P/P and native P identity differs')
    common = raw['common_success']
    if common.dtype.kind != 'b' or not np.array_equal(common, np.all(native_ll[:,0].argmax(-1)==g,axis=0)):
        raise ValueError('common-success subset differs from native full correct answers')
    if [int(np.sum(common & (sub == i))) for i in (0,1)] != [36,8]:
        raise ValueError('common-success subject counts differ from 36/8')
    cross = per_question(cross_ll,g,lens,chars)
    native = per_question(native_ll,g,lens,chars)
    cross['first_answer_token_KL_vs_P'] = raw['first_answer_token_KL_vs_P']
    native['first_answer_token_KL_vs_P'] = raw['native_first_answer_token_KL_vs_P']

    def penalties(metrics, likelihood, first_kl):
        return {
            'accuracy_drop': metrics['raw_accuracy'][...,0,:] - metrics['raw_accuracy'][...,1,:],
            'per_char_accuracy_drop': metrics['per_char_accuracy'][...,0,:] - metrics['per_char_accuracy'][...,1,:],
            'choice_CE_increase': metrics['choice_CE'][...,1,:] - metrics['choice_CE'][...,0,:],
            'true_answer_token_NLL_increase': metrics['true_answer_token_NLL'][...,1,:] - metrics['true_answer_token_NLL'][...,0,:],
            'pruning_KL': first_kl,
            'choice_score_KL': candidate_kl(likelihood[...,0,:,:],likelihood[...,1,:,:]),
        }
    cross_cost = penalties(cross,cross_ll,raw['pruning_KL'])
    native_cost = penalties(native,native_ll,raw['native_pruning_KL'])
    checks=0; max_error=0.; differences=[]
    def check(path, record, x, include):
        nonlocal checks,max_error
        point, ci, components = stratified(x,sub,include)
        tests=[('point',point,record['point']),('question_ci95',ci,record['question_ci95'])]
        if record.get('bootstrap_seed') != 156001:
            differences.append(path+': bootstrap seed')
        if record['question_count'] != int(include.sum()):
            differences.append(path+': question count')
        for i,name in enumerate(SUBJECT):
            n,p,c=components[i]; target=record['per_subject'][name]
            if target['questions'] != n: differences.append(path+': '+name+' count')
            tests.extend([(name+' point',p,target['point']),(name+' CI',c,target['question_ci95'])])
        for label,want,got in tests:
            err=float(np.max(np.abs(np.asarray(want)-np.asarray(got))))
            checks+=1; max_error=max(max_error,err)
            if not np.isfinite(err) or err>ATOL:
                differences.append(f'{path}/{label}: error={err:.12g}')
    for scope,include in (('all_questions',np.ones(128,dtype=bool)),('common_native_success',common)):
        section=summary['scopes'][scope]
        for r,rs in enumerate(SOURCE):
            for s,ss in enumerate(SOURCE):
                key=rs+ss
                for p,policy in enumerate(POLICY):
                    for k,v in cross.items():
                        check(f'{scope}/cross/{key}/{policy}/{k}',section['cross'][key][policy][k],v[r,s,p],include)
                        check(f'{scope}/relative_to_PP/{key}/{policy}/{k}',section['relative_to_PP'][key][policy][k],v[r,s,p]-v[0,0,p],include)
                    if p==1:
                        for k,v in cross_cost.items():
                            check(f'{scope}/cross/{key}/{policy}/{k}',section['cross'][key][policy][k],v[r,s],include)
        for i,label in enumerate(SOURCE):
            for p,policy in enumerate(POLICY):
                for k,v in native.items():
                    check(f'{scope}/native/{label}/{policy}/{k}',section['native'][label][policy][k],v[i,p],include)
                if p==1:
                    for k,v in native_cost.items():
                        check(f'{scope}/native/{label}/{policy}/{k}',section['native'][label][policy][k],v[i],include)
        for p,policy in enumerate(POLICY):
            for k,v in cross.items():
                check(f'{scope}/AB/{policy}/{k}',section['AB_source_contrasts']['policies'][policy][k],ab_contrast(v[:,:,p],k in ('raw_accuracy','per_char_accuracy')),include)
        for k,v in cross_cost.items():
            check(f'{scope}/AB/budget/{k}',section['AB_source_contrasts']['budget'][k],ab_contrast(v),include)
    return {'status':'passed' if not differences else 'failed','checks':checks,'max_absolute_error':max_error,
            'tolerance':ATOL,'differences':differences,
            'limitation':'First-token KL scalar is stored in raw; vocabulary distributions are absent, so only its aggregation, contrasts and CI can be independently recomputed.'}


def self_test():
    gold=np.array([0,1,2,3]); ll=np.array([[0.,-2,-3,-4],[-2,0,-3,-4],[-2,-3,0,-4],[-2,-3,-4,0.]])
    lengths=np.ones((4,4),dtype=int)*2; chars=np.ones((4,4),dtype=int)
    v=per_question(ll,gold,lengths,chars)
    assert np.array_equal(v['raw_accuracy'],np.ones(4)) and np.all(v['true_answer_token_NLL']==0)
    assert np.allclose(v['choice_CE'],np.log1p(np.exp(-2)+np.exp(-3)+np.exp(-4)))
    adjusted=ll.copy();adjusted[0,0]=-1.;lengths[0,0]=4
    assert per_question(adjusted,gold,lengths,chars)['true_answer_token_NLL'][0]==.25
    assert np.allclose(candidate_kl(ll,ll),0)
    x=np.zeros((3,3,4));x[0,0]=1000;x[1,2]=4;x[2,1]=2;x[1,1]=1;x[2,2]=3
    assert np.array_equal(ab_contrast(x),np.ones(4)) and np.array_equal(ab_contrast(x,True),-np.ones(4))
    mean,ci,parts=stratified(np.array([1.,1.,3.,3.]),np.array([0,0,1,1]),np.ones(4,dtype=bool))
    assert mean==2 and np.array_equal(ci,[2,2]) and [p[0] for p in parts]==[2,2]
    return {'status':'passed','CPU_only':True,'checks':['known scores and token lengths','candidate KL identity','AB contrast sign and PP exclusion','equal-subject bootstrap']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--raw',type=Path)
    parser.add_argument('--summary',type=Path)
    parser.add_argument('--budget',type=Path,default=Path(__file__).resolve().parents[1]/'e156/budget.json')
    parser.add_argument('--manifest',type=Path,default=Path(__file__).resolve().parents[1]/'e156/manifest.json')
    args=parser.parse_args()
    if args.self_test:
        report=self_test()
    else:
        if args.raw is None or args.summary is None:
            parser.error('--raw and --summary are required unless --self-test')
        summary=require_inputs(args.raw,args.summary,args.budget,args.manifest)
        with np.load(args.raw,allow_pickle=False) as raw:
            report=verify(raw,summary)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if report['status']!='passed':
        raise SystemExit(1)
