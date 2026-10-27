"""CPU analysis for E160 fixed shared-trajectory interchange."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results'/'e160'
NAMES=('P','A','B'); SUBJECTS=('high_school_biology','high_school_mathematics'); SEED=160001


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def scores(ll,gold,tokens,chars):
    x=np.asarray(ll,dtype=np.float64);q=np.arange(len(gold));z=x-x.max(axis=-1,keepdims=True)
    lp=z-np.log(np.exp(z).sum(axis=-1,keepdims=True))
    return {'raw_accuracy':(x.argmax(-1)==gold).astype(float),'per_char_accuracy':((x/chars).argmax(-1)==gold).astype(float),
            'choice_CE':-lp[...,q,gold],'true_answer_token_NLL':-x[...,q,gold]/tokens[q,gold]}


def stats(x,subject,mask=None):
    x=np.asarray(x,dtype=float);subject=np.asarray(subject);selected=np.ones(subject.shape,dtype=bool) if mask is None else np.asarray(mask,dtype=bool)
    if x.shape!=subject.shape or selected.shape!=subject.shape:raise ValueError('Expected paired question vector')
    rng=np.random.default_rng(SEED);details={};means=[];draws=[]
    for i,name in enumerate(SUBJECTS):
        v=x[selected & (subject==i)];mean=float(v.mean()) if len(v) else None;means.append(mean)
        entry={'point':mean,'count':len(v)}
        if mask is None:
            if len(v)!=64:raise ValueError('Primary requires 64 questions per subject')
            b=v[rng.integers(0,64,(1000,64))].mean(-1);draws.append(b);entry['question_ci95']=np.quantile(b,[.025,.975]).tolist()
        details[name]=entry
    macro=float(np.mean(means)) if all(m is not None for m in means) else None
    out={'point':macro,'per_subject':details,'count':int(selected.sum())}
    if mask is None:out.update(question_ci95=np.quantile(np.mean(draws,axis=0),[.025,.975]).tolist(),bootstrap_seed=SEED,bootstrap_replicates=1000,unit='paired questions within fixed subjects; not model-seed or subject-population CI')
    else:out.update(ci='not computed',pooled_point=float(x[selected].mean()) if selected.any() else None)
    return out


def calculate_arrays(full,natural,zero_s,zero_r_fixed,zero_r_natural,both,accuracy):
    sign=-1 if accuracy else 1
    shared=sign*(zero_s[:,None,:]-full)
    online_routed=sign*(zero_r_fixed[None,:,:]-full)
    natural_shared=sign*(zero_s-natural)
    consumer_delta=shared[1:]-shared[0]
    natural_delta=natural_shared[1:]-natural_shared[0]
    producer_delta=shared[:,1:]-shared[:,0,None,:]
    recovery=sign*(zero_r_natural[None,:]-zero_r_fixed)
    consistency=sign*((full[0,1]+full[1,0]+full[0,2]+full[2,0]+full[1,2]+full[2,1])/6-(full[0,0]+full[1,1]+full[2,2])/3)
    return {'full_fixed_producer_consumer_contrasts':full[1:]-full[0],
            'full_fixed_consumer_producer_contrasts':full[:,1:]-full[:,0,None,:],
            'shared_necessity':shared,'direct_online_routed_necessity':online_routed,
            'direct_online_fixed_producer_consumer_contrasts':online_routed[1:]-online_routed[0],
            'direct_online_fixed_consumer_producer_contrasts':online_routed[:,1:]-online_routed[:,0,None,:],
            'natural_shared_necessity':natural_shared,
            'fixed_producer_consumer_contrasts':consumer_delta,'fixed_consumer_producer_contrasts':producer_delta,
            'fixed_producer_minus_natural_consumer_contrasts':consumer_delta-natural_delta[:,None,:],
            'recovery_under_routed_removal':recovery,'off_diagonal_minus_diagonal_matching_cost':consistency}


def patterns(full_correct,zero_s_correct,zero_r_fixed_correct,both_correct,mask,subject):
    if not np.all(full_correct[:,:,mask]):raise ValueError('Selected cases must have all nine full conditions correct')
    code=np.empty(full_correct.shape,dtype=np.uint8)
    for i in range(3):
        for j in range(3):code[i,j]=4*both_correct+2*zero_s_correct[i]+zero_r_fixed_correct[j]
    def counts(x,m):return np.bincount(x[m],minlength=8).tolist()
    cells={}
    for i in range(3):
        for j in range(3):
            cells[NAMES[i]+NAMES[j]]={'counts':counts(code[i,j],mask),'per_subject_counts':{s:counts(code[i,j],mask&(subject==k)) for k,s in enumerate(SUBJECTS)}}
    trans={'fixed_producer':{},'fixed_consumer':{}}
    for typ in trans:
        for fixed in range(3):
            for a in range(3):
                for b in range(a+1,3):
                    x,y=(code[a,fixed],code[b,fixed]) if typ=='fixed_producer' else (code[fixed,a],code[fixed,b])
                    def matrix(m):
                        z=np.zeros((8,8),dtype=int);np.add.at(z,(x[m],y[m]),1);return z.tolist()
                    trans[typ][NAMES[fixed]+'_'+NAMES[a]+'_to_'+NAMES[b]]={'counts':matrix(mask),'per_subject_counts':{s:matrix(mask&(subject==k)) for k,s in enumerate(SUBJECTS)}}
    return {'bits':{'D':4,'R_with_shared_zero':2,'shared_replay_with_routed_zero':1},
            'interpretation':'Shared replay retains producer routed history; not intrinsic shared-only capacity.', 'cells':cells,'transitions':trans}


def validate(a):
    shapes={'clamped_candidate_loglikelihood':(3,3,128,4),'natural_candidate_loglikelihood':(3,128,4),
      'without_shared_candidate_loglikelihood':(3,128,4),'without_routed_fixed_shared_candidate_loglikelihood':(3,128,4),
      'without_routed_natural_shared_candidate_loglikelihood':(128,4),'without_both_candidate_loglikelihood':(128,4),
      'gold':(128,),'subject':(128,),'answer_tokens':(128,4),'answer_chars':(128,4),'consumer_names':(3,),'producer_names':(3,), 'shared_signal_hashes':(3,128)}
    for k,shape in shapes.items():
        if k not in a or a[k].shape!=shape:raise ValueError('Missing or incorrect shape: '+k)
    for k in ('consumer_names','producer_names'):
        if tuple(a[k].tolist())!=NAMES:raise ValueError('Wrong axis order')
    for k in shapes:
        if k.endswith('loglikelihood') and not np.isfinite(a[k]).all():raise ValueError('Nonfinite '+k)
    hashes=a['shared_signal_hashes']
    if hashes.dtype.kind!='U' or hashes.dtype.itemsize!=256 or any(len(h)!=64 or any(c not in '0123456789abcdef' for c in h) for h in hashes.flat):raise ValueError('Invalid trajectory SHA-256 values')
    for k in ('gold','subject','answer_tokens','answer_chars'):
        if a[k].dtype.kind not in 'iu':raise ValueError('Expected integer '+k)
    if np.any((a['gold']<0)|(a['gold']>3)) or np.any(a['answer_tokens']<=0) or np.any(a['answer_chars']<=0) or np.bincount(a['subject'],minlength=2).tolist()!=[64,64]:raise ValueError('Invalid population')
    for i in range(3):
        if not np.array_equal(a['clamped_candidate_loglikelihood'][i,i],a['natural_candidate_loglikelihood'][i]):raise ValueError('Natural diagonal replay mismatch')


def summarize(a):
    validate(a); gold=a['gold'];subject=a['subject'];tokens=a['answer_tokens'];chars=a['answer_chars']
    fields={'full':'clamped_candidate_loglikelihood','natural':'natural_candidate_loglikelihood','zero_shared':'without_shared_candidate_loglikelihood',
            'zero_routed_fixed_shared':'without_routed_fixed_shared_candidate_loglikelihood','zero_routed_natural_shared':'without_routed_natural_shared_candidate_loglikelihood','zero_both':'without_both_candidate_loglikelihood'}
    m={k:scores(a[v],gold,tokens,chars) for k,v in fields.items()};mask=(a[fields['full']].argmax(-1)==gold).all(axis=(0,1))
    result={'experiment':'E160','status':'complete','consumer_order':list(NAMES),'producer_order':list(NAMES),
      'definitions':{'shared_weights':'P at every layer; producer trajectories on same input',
        'shared_necessity':'loss zero-S minus full, accuracy full minus zero-S',
        'direct_online_routed_necessity':'loss R-zero with fixed producer S minus full, reversed for accuracy; not total routed contribution: S trajectory retains producer R history',
        'recovery_under_routed_removal':'loss R-zero natural shared minus R-zero fixed shared, reversed for accuracy',
        'matching_cost':'off-diagonal mean minus diagonal mean for losses, reverse for accuracy; empirical consistency, not a new identity mechanism',
        'limitations':'No unique mediation percentage or training mechanism; fixed replay is not intrinsic shared-only capacity',
        'secondary':'all nine clamped full raw-correct; points/counts only; selection uses only full-cell predictions'},
      'all_nine_full_correct':{'count':int(mask.sum()),'per_subject':[int((mask&(subject==i)).sum()) for i in range(2)],'mask':mask.tolist(),
       'patterns':patterns(m['full']['raw_accuracy'].astype(bool),m['zero_shared']['raw_accuracy'].astype(bool),m['zero_routed_fixed_shared']['raw_accuracy'].astype(bool),m['zero_both']['raw_accuracy'].astype(bool),mask,subject)},'metrics':{}}
    for key in m['full']:
        arrays=calculate_arrays(*(m[field][key] for field in ('full','natural','zero_shared','zero_routed_fixed_shared','zero_routed_natural_shared','zero_both')),key.endswith('accuracy'))
        entry={'primary':{},'secondary':{}}
        for section,selection in [('primary',None),('secondary',mask)]:
            def stat(v):return stats(v,subject,selection)
            def nested(x):
                x=np.asarray(x)
                if x.shape==subject.shape:return stat(x)
                return [nested(v) for v in x]
            entry[section]['conditions']={field:nested(m[field][key]) for field in fields}
            entry[section]['contrasts']={name:nested(x) for name,x in arrays.items()}
        result['metrics'][key]=entry
    return result


def analyze():
    plan_path=ROOT/'plan.json'; plan=json.loads(plan_path.read_text());manifest=json.loads((ROOT/'manifest.json').read_text());budget=json.loads((ROOT/'budget.json').read_text())
    if manifest.get('status')!='complete' or manifest.get('plan_sha256')!=sha(plan_path):raise ValueError('Incomplete manifest or plan mismatch')
    if manifest.get('source_sha256')!=plan.get('source_sha256') or plan['source_sha256'].get('e160_analyze.py')!=sha(__file__):raise ValueError('Source SHA mismatch')
    attempts=budget.get('attempts',[]);limit=plan.get('limit_gpu_seconds')
    if limit!=10800 or not attempts or any(x.get('status')!='complete' or not np.isfinite(x.get('gpu_seconds',float('nan'))) or x['gpu_seconds']<0 for x in attempts) or sum(x['gpu_seconds'] for x in attempts)>limit:raise ValueError('Incomplete or exceeded budget')
    for key in ('task_input','references'):
        asset=plan[key]
        if sha(asset['path'])!=asset['sha256']:raise ValueError('Reference SHA mismatch: '+key)
    raw=manifest['raw']
    if sha(raw['path'])!=raw['sha256']:raise ValueError('Raw SHA mismatch')
    with np.load(raw['path'],allow_pickle=False) as f,np.load(plan['task_input']['path'],allow_pickle=False) as task,np.load(plan['references']['path'],allow_pickle=False) as refs:
        a={k:f[k] for k in f.files}
        for k in ('gold','subject','answer_tokens','answer_chars'):
            if not np.array_equal(a[k],task[k]) or not np.array_equal(a[k],refs[k]):raise ValueError('Population mismatch '+k)
        for k in ('natural_candidate_loglikelihood','without_shared_candidate_loglikelihood','without_routed_natural_shared_candidate_loglikelihood','without_both_candidate_loglikelihood'):
            if not np.array_equal(a[k],refs[k]):raise ValueError('Inherited reference mismatch '+k)
        result=summarize(a)
    result.update(raw_sha256=raw['sha256'],plan_sha256=manifest['plan_sha256'],analysis_source_sha256=sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return {'status':'complete','summary':str(ROOT/'summary.json')}


def self_test():
    gold=np.array([0,1]); lengths=np.ones((2,4),dtype=int);x=np.array([[3.,0,0,0],[0,3,0,0]])
    m=scores(x,gold,lengths,lengths);assert m['raw_accuracy'].tolist()==[1,1] and np.allclose(m['choice_CE'],np.log1p(3*np.exp(-3)))
    full=np.arange(9,dtype=float).reshape(3,3,1);natural=np.array([[0.],[4.],[8.]])
    zs=np.array([[10.],[20.],[30.]]);zr=np.array([[6.],[7.],[8.]]);zn=np.array([10.]);both=np.array([20.])
    out=calculate_arrays(full,natural,zs,zr,zn,both,False)
    assert out['shared_necessity'].shape==(3,3,1) and out['direct_online_routed_necessity'][1,2,0]==3
    assert out['fixed_producer_consumer_contrasts'][0,2,0]==7 and out['fixed_consumer_producer_contrasts'][2,1,0]==-2
    assert np.array_equal(out['recovery_under_routed_removal'][:,0],[4,3,2])
    rev=calculate_arrays(full,natural,zs,zr,zn,both,True)
    assert np.array_equal(rev['recovery_under_routed_removal'],-out['recovery_under_routed_removal'])
    sub=np.repeat([0,1],64);v=np.r_[np.ones(64),np.full(64,3.)];assert stats(v,sub)['question_ci95']==[2,2]
    mask=sub==0;secondary=stats(v,sub,mask);assert secondary['point'] is None and secondary['per_subject'][SUBJECTS[1]]['point'] is None
    correct=np.ones((3,3,8),bool);z_s=np.broadcast_to(np.array([bool(i&2) for i in range(8)]),(3,8));z_r=np.broadcast_to(np.array([bool(i&1) for i in range(8)]),(3,8));d=np.array([bool(i&4) for i in range(8)])
    z=patterns(correct,z_s,z_r,d,np.ones(8,bool),np.array([0]*4+[1]*4));assert z['cells']['PP']['counts']==[1]*8
    assert sum(map(sum,z['transitions']['fixed_producer']['P_P_to_A']['counts']))==8
    hashes=np.full((3,128),'a'*64,dtype='U64');assert hashes.dtype.itemsize==256 and len(hashes[0,0])==64
    return {'status':'passed','CPU_only':True,'checks':['metric fixture','consumer/producer axes and online support','recovery signs','paired subjects and empty secondary','all patterns and transitions','SHA format']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--analyze',action='store_true');args=p.parse_args()
    if args.self_test==args.analyze:p.error('Choose exactly one of --self-test or --analyze')
    print(json.dumps(self_test() if args.self_test else analyze(),ensure_ascii=False,indent=2))
