"""E159 CPU analysis of frozen 3x3 full and zero-border candidate scores."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'results' / 'e159'
SOURCES = ('P', 'A', 'B', 'zero')
SUBJECTS = ('high_school_biology', 'high_school_mathematics')
SEED = 159001


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def scores(ll, gold, tokens, chars):
    ll = np.asarray(ll, dtype=np.float64)
    q = np.arange(len(gold))
    z = ll - ll.max(axis=-1, keepdims=True)
    logp = z - np.log(np.exp(z).sum(axis=-1, keepdims=True))
    return {'raw_accuracy': (ll.argmax(-1) == gold).astype(float),
            'per_char_accuracy': ((ll / chars).argmax(-1) == gold).astype(float),
            'choice_CE': -logp[..., q, gold],
            'true_answer_token_NLL': -ll[..., q, gold] / tokens[q, gold]}


def stats(x, subject):
    x = np.asarray(x, dtype=np.float64)
    if x.shape != subject.shape: raise ValueError('Expected paired question vector')
    rng = np.random.default_rng(SEED)
    draws, means, detail = [], [], {}
    for i, name in enumerate(SUBJECTS):
        v = x[subject == i]
        if len(v) != 64: raise ValueError('Expected 64 questions per subject')
        b = v[rng.integers(0, 64, (1000, 64))].mean(-1)
        draws.append(b); means.append(v.mean())
        detail[name] = {'point': float(v.mean()), 'question_ci95': np.quantile(b, [.025,.975]).tolist(), 'n': 64}
    return {'point': float(np.mean(means)), 'question_ci95': np.quantile(np.mean(draws,axis=0), [.025,.975]).tolist(),
            'per_subject': detail, 'bootstrap_seed': SEED, 'bootstrap_replicates': 1000,
            'unit': 'paired questions within fixed subjects; not model-seed or subject-population CI'}


def necessity(x, accuracy):
    # x: routed source, shared source, question. Positive means removal hurts.
    sign = -1 if accuracy else 1
    s = sign * (x[:3,3,None,:] - x[:3,:3,:])
    r = sign * (x[3,None,:3,:] - x[:3,:3,:])
    return s, r


def pattern_counts(correct, cohort, subject):
    # full correct by selection; D=zero/zero, R-alone=r/zero, S-alone=zero/s.
    if not np.all(correct[:3,:3,cohort]): raise ValueError('all-nine cohort not full-correct')
    patterns = np.empty((3,3,correct.shape[-1]), dtype=np.uint8)
    for r in range(3):
        for s in range(3):
            patterns[r,s] = 4*correct[3,3] + 2*correct[r,3] + correct[3,s]
    def counts(v): return np.bincount(v, minlength=8).tolist()
    cells = {}
    for r in range(3):
        for s in range(3):
            v = patterns[r,s]
            cells[SOURCES[r]+SOURCES[s]] = {'counts': counts(v[cohort]),
                'per_subject_counts': {name: counts(v[cohort & (subject==i)]) for i,name in enumerate(SUBJECTS)}}
    transitions = {'fixed_S': {}, 'fixed_R': {}}
    for i in (1,2):
        for j in range(3):
            for key, before, after in (
                ('fixed_S', patterns[0,j], patterns[i,j]),
                ('fixed_R', patterns[j,0], patterns[j,i])):
                mat = np.zeros((8,8),dtype=int); np.add.at(mat,(before[cohort],after[cohort]),1)
                per = {}
                for k,name in enumerate(SUBJECTS):
                    m=np.zeros((8,8),dtype=int); chosen=cohort & (subject==k)
                    np.add.at(m,(before[chosen],after[chosen]),1); per[name]=m.tolist()
                transitions[key][SOURCES[i]+'_at_'+SOURCES[j]]={'counts':mat.tolist(),'per_subject_counts':per}
    return {'bit_order': {'D':4, 'R_alone':2, 'S_alone':1}, 'pattern_0': 'both needed and D fails',
            'cells':cells, 'transitions':transitions}


def validate(a):
    shapes = {'candidate_loglikelihood':(4,4,128,4), 'measured_cells':(4,4),
              'native_reference_candidate_loglikelihood':(3,4,128,4), 'gold':(128,), 'subject':(128,),
              'answer_tokens':(128,4), 'answer_chars':(128,4), 'source_names':(4,),
              'all_nine_full_success':(128,), 'common_native_success':(128,)}
    for k,shape in shapes.items():
        if k not in a or a[k].shape != shape: raise ValueError('Missing or incorrect shape: '+k)
    if tuple(a['source_names'].tolist()) != SOURCES: raise ValueError('Incorrect source order')
    mask=np.zeros((4,4),dtype=bool); mask[3,:]=True; mask[:,3]=True; mask[0,0]=True
    if a['measured_cells'].dtype.kind!='b' or not np.array_equal(a['measured_cells'],mask): raise ValueError('Incorrect measured cells')
    for k in ('candidate_loglikelihood','native_reference_candidate_loglikelihood'):
        if not np.isfinite(a[k]).all(): raise ValueError('Nonfinite '+k)
    for k in ('gold','subject','answer_tokens','answer_chars'):
        if a[k].dtype.kind not in 'iu': raise ValueError('Expected integer '+k)
    if np.any((a['gold']<0)|(a['gold']>3)) or np.any(a['answer_tokens']<=0) or np.any(a['answer_chars']<=0): raise ValueError('Invalid answer data')
    if np.bincount(a['subject'],minlength=2).tolist()!=[64,64]: raise ValueError('Invalid subjects')
    for k,counts in [('all_nine_full_success',[30,3]),('common_native_success',[36,8])]:
        if a[k].dtype.kind!='b' or [int((a[k]&(a['subject']==i)).sum()) for i in (0,1)]!=counts: raise ValueError('Invalid cohort '+k)
    correct=a['candidate_loglikelihood'].argmax(-1)==a['gold']
    if not np.array_equal(correct[:3,:3].all(axis=(0,1)),a['all_nine_full_success']): raise ValueError('All-nine cohort differs from full table')
    native=a['native_reference_candidate_loglikelihood'][:,0].argmax(-1)==a['gold']
    if not np.array_equal(native.all(axis=0),a['common_native_success']): raise ValueError('Native cohort differs from reference')


def summarize(a):
    validate(a)
    subject=a['subject']; cohort=a['all_nine_full_success']; gold=a['gold']
    values=scores(a['candidate_loglikelihood'],gold,a['answer_tokens'],a['answer_chars'])
    native=scores(a['native_reference_candidate_loglikelihood'],gold,a['answer_tokens'],a['answer_chars'])
    result={'definitions':{'table_axes':'routed source, shared source; P,A,B,zero',
        'necessity':'loss: removed minus full; accuracy: full minus removed',
        'balance':'shared necessity minus routed necessity; the full term cancels, so this is not a responsibility fraction',
        'shared_source_caveat':'At fixed R, shared-necessity difference over S equals the corresponding old full-quality difference; it is not new mechanistic evidence.',
        'native_reference_condition_order':['native','routed_zero','shared_zero','all_moe_zero'],
        'primary':'all 128; equal subject macro, paired question bootstrap within subjects',
        'secondary':'all-nine full-correct 33; counts and points only, no CI; selected on full-cell outcomes'},
        'source_order':list(SOURCES), 'metrics':{},
        'common_native_success_reference_only':{'count':44,'per_subject':[36,8]},
        'all_nine_full_success':{'count':33,'per_subject':[30,3],
            'patterns':pattern_counts(values['raw_accuracy'].astype(bool),cohort,subject)}}
    for name,x in values.items():
        ns,nr=necessity(x,name.endswith('accuracy'))
        stat=lambda v: stats(v,subject)
        table=lambda v: {SOURCES[i]+SOURCES[j]:stat(v[i,j]) for i in range(v.shape[0]) for j in range(v.shape[1])}
        entry={'full_and_border_table':table(x), 'shared_necessity':table(ns), 'routed_necessity':table(nr),
               'shared_minus_routed_necessity':table(ns-nr), 'unchanged_partner':{'shared_necessity_fixed_S':{},'routed_necessity_fixed_R':{}},
               'diagonal_necessity_contrasts':{},'native_context':{'full_quality_differences':{},'necessity':{},'necessity_differences':{}}, 'all_nine_full_correct_points':{}}
        sign = -1 if name.endswith('accuracy') else 1
        native_s = sign * (native[name][:,2] - native[name][:,0])
        native_r = sign * (native[name][:,1] - native[name][:,0])
        for i in range(3):
            entry['native_context']['necessity'][SOURCES[i]]={'shared':stat(native_s[i]), 'routed':stat(native_r[i]), 'balance':stat(native_s[i]-native_r[i])}
        for i in (1,2):
            label=SOURCES[i]+'-P'
            entry['unchanged_partner']['shared_necessity_fixed_S'][label]={SOURCES[j]:stat(ns[i,j]-ns[0,j]) for j in range(3)}
            entry['unchanged_partner']['routed_necessity_fixed_R'][label]={SOURCES[j]:stat(nr[j,i]-nr[j,0]) for j in range(3)}
            entry['diagonal_necessity_contrasts'][label]={'shared':stat(ns[i,i]-ns[0,0]),'routed':stat(nr[i,i]-nr[0,0])}
            entry['native_context']['full_quality_differences']['native_'+label]=stat(native[name][i,0]-native[name][0,0])
            entry['native_context']['necessity_differences']['native_'+label]={'shared':stat(native_s[i]-native_s[0]),'routed':stat(native_r[i]-native_r[0]),'balance':stat((native_s[i]-native_r[i])-(native_s[0]-native_r[0]))}
        entry['native_context']['full_quality_differences']['native_B_minus_BB']=stat(native[name][2,0]-x[2,2])
        entry['native_context']['necessity_differences']['native_B_minus_BB']={'shared':stat(native_s[2]-ns[2,2]), 'routed':stat(native_r[2]-nr[2,2]), 'balance':stat((native_s[2]-native_r[2])-(ns[2,2]-nr[2,2]))}
        for label,arr in [('full_and_border_table',x),('shared_necessity',ns),('routed_necessity',nr),('shared_minus_routed_necessity',ns-nr)]:
            entry['all_nine_full_correct_points'][label]={SOURCES[i]+SOURCES[j]:{'overall_point':float(arr[i,j,cohort].mean()),
                'overall_point_definition':'pooled 33 questions (30 biology, 3 mathematics)',
                'equal_subject_macro_point':float(np.mean([arr[i,j,cohort & (subject==k)].mean() for k in range(2)])),
                'per_subject_point':{sub:float(arr[i,j,cohort & (subject==k)].mean()) for k,sub in enumerate(SUBJECTS)}}
                for i in range(arr.shape[0]) for j in range(arr.shape[1])}
        def cohort_point(v):
            return {'overall_point':float(v[cohort].mean()), 'overall_point_definition':'pooled 33 questions (30 biology, 3 mathematics)',
                    'equal_subject_macro_point':float(np.mean([v[cohort & (subject==k)].mean() for k in range(2)])),
                    'per_subject_point':{sub:float(v[cohort & (subject==k)].mean()) for k,sub in enumerate(SUBJECTS)}}
        secondary=entry['all_nine_full_correct_points']
        secondary['unchanged_partner']={'shared_necessity_fixed_S':{},'routed_necessity_fixed_R':{}}
        secondary['diagonal_necessity_contrasts']={}
        for i in (1,2):
            label=SOURCES[i]+'-P'
            secondary['unchanged_partner']['shared_necessity_fixed_S'][label]={SOURCES[j]:cohort_point(ns[i,j]-ns[0,j]) for j in range(3)}
            secondary['unchanged_partner']['routed_necessity_fixed_R'][label]={SOURCES[j]:cohort_point(nr[j,i]-nr[j,0]) for j in range(3)}
            secondary['diagonal_necessity_contrasts'][label]={'shared':cohort_point(ns[i,i]-ns[0,0]),'routed':cohort_point(nr[i,i]-nr[0,0])}
        result['metrics'][name]=entry
    return result


def analyze():
    plan_path=ROOT/'plan.json'; manifest=json.loads((ROOT/'manifest.json').read_text()); plan=json.loads(plan_path.read_text())
    budget=json.loads((ROOT/'budget.json').read_text())
    if manifest.get('status')!='complete' or manifest.get('plan_sha256')!=sha(plan_path): raise ValueError('Manifest/plan incomplete or mismatched')
    attempts=budget.get('attempts',[])
    if not attempts or any(a.get('status')!='complete' for a in attempts): raise ValueError('Budget incomplete')
    limit=plan.get('limit_gpu_seconds')
    if limit!=10800 or any(not np.isfinite(a.get('gpu_seconds',float('nan'))) or a['gpu_seconds']<0 for a in attempts) or sum(a['gpu_seconds'] for a in attempts)>limit:
        raise ValueError('Invalid or exceeded GPU budget')
    expected=manifest.get('source_sha256',{})
    if expected!=plan.get('source_sha256') or expected.get('e159_analyze.py')!=sha(__file__): raise ValueError('Source SHA mismatch')
    for key in ('task_input','references'):
        asset=plan[key]
        if sha(asset['path'])!=asset['sha256']: raise ValueError(key+' SHA mismatch')
    raw=manifest['raw']
    if sha(raw['path'])!=raw['sha256']: raise ValueError('Raw SHA mismatch')
    with np.load(raw['path'],allow_pickle=False) as f, np.load(plan['task_input']['path'],allow_pickle=False) as task, np.load(plan['references']['path'],allow_pickle=False) as refs:
        a={k:f[k] for k in f.files}
        for k in ('gold','subject','answer_tokens','answer_chars'):
            if not np.array_equal(a[k],task[k]) or not np.array_equal(a[k],refs[k]): raise ValueError('Population reference mismatch: '+k)
        if not np.array_equal(a['candidate_loglikelihood'][:3,:3],refs['full_candidate_loglikelihood']): raise ValueError('Inherited full scores mismatch')
        for k in ('native_reference_candidate_loglikelihood','all_nine_full_success','common_native_success'):
            if not np.array_equal(a[k],refs[k]): raise ValueError('Inherited reference mismatch: '+k)
        result=summarize(a)
    result.update(experiment='E159',status='complete',raw_sha256=raw['sha256'],plan_sha256=manifest['plan_sha256'],analysis_source_sha256=sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    return {'status':'complete','summary':str(ROOT/'summary.json')}


def self_test():
    gold=np.array([0,1,0,1]); lengths=np.ones((4,4),dtype=int)
    ll=np.array([[3.,0,0,0],[0,3.,0,0],[3.,0,0,0],[0,3.,0,0]])
    m=scores(ll,gold,lengths,lengths)
    assert np.all(m['raw_accuracy']==1) and np.allclose(m['choice_CE'],np.log1p(3*np.exp(-3)))
    assert np.all(m['true_answer_token_NLL']==-3) and np.all(m['per_char_accuracy']==1)
    x=np.arange(16,dtype=float).reshape(4,4,1); s,r=necessity(x,False)
    assert np.all(s[:,0,0]==3) and np.all(r[0,:,0]==12)
    assert np.array_equal(s[1]-s[0],(x[1,3]-x[1,:3])-(x[0,3]-x[0,:3]))
    assert np.array_equal(s[:,1]-s[:,0],x[:3,0]-x[:3,1])
    sa,ra=necessity(x,True); assert np.array_equal(sa,-s) and np.array_equal(ra,-r)
    correct=np.ones((4,4,8),dtype=bool)
    correct[3,3]=np.array([bool(i&4) for i in range(8)])
    correct[0,3]=np.array([bool(i&2) for i in range(8)])
    correct[3,0]=np.array([bool(i&1) for i in range(8)])
    pc=pattern_counts(correct,np.ones(8,dtype=bool),np.array([0]*4+[1]*4))
    assert pc['cells']['PP']['counts']==[1]*8
    assert sum(map(sum,pc['transitions']['fixed_S']['A_at_P']['counts']))==8
    sub=np.repeat([0,1],64); v=np.r_[np.ones(64),np.full(64,3.)]
    t=stats(v,sub); assert t['point']==2 and t['question_ci95']==[2,2]
    assert stats(v+2,sub)['point']-t['point']==2
    return {'status':'passed','CPU_only':True,'checks':['metric fixture','necessity axes and signs','unchanged partner and source-effect identity','all eight patterns and transition counts','paired two-subject bootstrap']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--self-test',action='store_true'); p.add_argument('--analyze',action='store_true'); args=p.parse_args()
    if args.self_test == args.analyze: p.error('Choose exactly one of --self-test or --analyze')
    print(json.dumps(self_test() if args.self_test else analyze(),indent=2,ensure_ascii=False))
