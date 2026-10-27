#!/usr/bin/env python3
"""Independent E160 CPU audit, without model or author analyzer imports."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
WB=Path(__file__).resolve().parents[2]
ROOT=WB/'results/e160'
NAMES=('P','A','B')
METRICS=('raw_accuracy','per_char_accuracy','choice_CE','true_answer_token_NLL')

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()
def read(path): return json.loads(Path(path).read_text())

def metrics(scores,gold,tokens,chars):
    scores=np.asarray(scores,dtype=np.float64); g=np.broadcast_to(gold,scores.shape[:-1]); selected=np.take_along_axis(scores,g[...,None],-1)[...,0]
    tok=np.take_along_axis(np.broadcast_to(tokens,scores.shape),g[...,None],-1)[...,0]
    maximum=scores.max(-1); ce=maximum+np.log(np.exp(scores-maximum[...,None]).sum(-1))-selected
    return np.stack(((scores.argmax(-1)==g).astype(float),((scores/chars).argmax(-1)==g).astype(float),ce,-selected/tok))

def stat(x,subj,indices):
    x=np.asarray(x,dtype=np.float64); per=np.stack([x[...,subj==s].mean(-1) for s in (0,1)],-1); boot=np.stack([x[...,indices[s]].mean(-1) for s in (0,1)],-1)
    return {'point':per.mean(-1).tolist(),'ci95':np.moveaxis(np.quantile(boot.mean(-1),[.025,.975],axis=-1),0,-1).tolist(),'per_subject_point':per.tolist(),'per_subject_ci95':np.moveaxis(np.quantile(boot,[.025,.975],axis=-2),0,-1).tolist()}

def aggregate(a, cohort=None):
    g=a['gold']; t=a['answer_tokens']; ch=a['answer_chars']; sub=a['subject']
    f=metrics(a['clamped_candidate_loglikelihood'],g,t,ch); natural=metrics(a['natural_candidate_loglikelihood'],g,t,ch); no_s=metrics(a['without_shared_candidate_loglikelihood'],g,t,ch); no_r_fixed=metrics(a['without_routed_fixed_shared_candidate_loglikelihood'],g,t,ch); no_r=metrics(a['without_routed_natural_shared_candidate_loglikelihood'],g,t,ch); neither=metrics(a['without_both_candidate_loglikelihood'],g,t,ch)
    sign=np.array([-1.,-1.,1.,1.])[:,None,None,None]
    shared=sign*(no_s[:,:,None,:]-f); routed=sign*(no_r_fixed[:,None,:,:]-f)
    natural_s=sign[:,:,0,:]*(no_s-natural); natural_r=sign[:,:,0,:]*(no_r[:,None,:]-natural)
    # Positive means keeping the produced trajectory improves the no-R outcome.
    recovery=sign[:,:,0,:]*(no_r[:,None,:]-no_r_fixed)
    rng=np.random.default_rng(160001); idx=[rng.choice(np.flatnonzero(sub==s),size=(1000,64),replace=True) for s in (0,1)]
    results={}
    def add(name,v):
        if cohort is None:
            results[name]=stat(v,sub,idx); return
        vals=[v[...,cohort & (sub==s)] for s in (0,1)]; points=[z.mean(-1) if z.shape[-1] else None for z in vals]
        def serial(z): return None if z is None else np.asarray(z).tolist()
        results[name]={'pooled_point':serial(v[...,cohort].mean(-1)) if cohort.any() else None,'per_subject_point':[serial(z) for z in points],'equal_subject_macro_point':serial((points[0]+points[1])/2) if all(z is not None for z in points) else None,'per_subject_count':[int(z.shape[-1]) for z in vals]}
    for key,v in [('full',f),('without_shared',no_s),('without_routed_fixed_shared',no_r_fixed),('without_routed_natural_shared',no_r),('without_both',neither),('natural_full',natural),('shared_support',shared),('controlled_routed_support',routed),('natural_shared_support',natural_s),('natural_routed_support',natural_r),('routed_deleted_fixed_signal_recovery',recovery)]: add(key,v)
    for key,v in [('full',f),('shared_support',shared),('controlled_routed_support',routed)]:
        add(key+'_fixed_producer_consumer_A_B_minus_P',v[:,1:3,:,:]-v[:,0:1,:,:]); add(key+'_fixed_consumer_producer_A_B_minus_P',v[:,:,1:3,:]-v[:,:,0:1,:])
    for key,v,n in [('shared_support',shared,natural_s),('controlled_routed_support',routed,natural_r),('full',f,natural)]:
        fixed=v[:,1:3,0,:]-v[:,0:1,0,:]; natural_diff=n[:,1:3,:]-n[:,0:1,:]
        add(key+'_natural_A_B_minus_P',natural_diff); add(key+'_fixed_producer_P_minus_natural_partner_effect',fixed-natural_diff)
    off=np.stack([f[:,c,p] for c in range(3) for p in range(3) if c!=p],axis=1).mean(1); diag=np.stack([f[:,i,i] for i in range(3)],axis=1).mean(1)
    add('off_diagonal_minus_diagonal_full_quality',off-diag)
    return results

def secondary(a):
    scores=a['clamped_candidate_loglikelihood']; gold=a['gold']; sub=a['subject']; correct=scores.argmax(-1)==gold; cohort=correct.all((0,1))
    d=(a['without_both_candidate_loglikelihood'].argmax(-1)==gold)
    ro=(a['without_shared_candidate_loglikelihood'].argmax(-1)==gold)
    sr=(a['without_routed_fixed_shared_candidate_loglikelihood'].argmax(-1)==gold)
    patterns=(4*d[None,None,:]+2*ro[:,None,:]+sr[None,:,:]).astype(int)
    output={'selection':'all nine clamped full cells raw-correct','count':int(cohort.sum()),'per_subject_count':[int((cohort&(sub==s)).sum()) for s in (0,1)],'mask':cohort.tolist(),'bits':{'D':4,'R_only_S_zero':2,'S_replay_only_R_zero_fixed':1},'cells':{},'transitions':{}}
    for c in range(3):
        for p in range(3):
            counts=[np.bincount(patterns[c,p,cohort&(sub==s)],minlength=8) for s in (0,1)]; pooled=counts[0]+counts[1]
            macro=((counts[0]/counts[0].sum()+counts[1]/counts[1].sum())/2).tolist() if all(z.sum()>0 for z in counts) else None
            output['cells'][NAMES[c]+NAMES[p]]={'counts':pooled.tolist(),'per_subject_counts':[z.tolist() for z in counts],'pooled_rates':(pooled/pooled.sum()).tolist() if pooled.sum() else None,'equal_subject_rates':macro}
    for axis in ('producer','consumer'):
        for fixed in range(3):
            for i,j in ((0,1),(0,2),(1,2)):
                x,y=(patterns[i,fixed],patterns[j,fixed]) if axis=='producer' else (patterns[fixed,i],patterns[fixed,j]); tables=[np.bincount((8*x+y)[cohort&(sub==s)],minlength=64).reshape(8,8) for s in (0,1)]; total=tables[0]+tables[1]
                output['transitions'][f'fixed_{axis}_{NAMES[fixed]}_{NAMES[i]}_to_{NAMES[j]}']={'counts':total.tolist(),'per_subject_counts':[v.tolist() for v in tables],'pooled_rates':(total/total.sum()).tolist() if total.sum() else None,'equal_subject_rates':((tables[0]/tables[0].sum()+tables[1]/tables[1].sum())/2).tolist() if all(v.sum()>0 for v in tables) else None}
    output['points']=aggregate(a,cohort)
    return output

def validate_arrays(a):
    shapes={'clamped_candidate_loglikelihood':(3,3,128,4),'natural_candidate_loglikelihood':(3,128,4),'without_shared_candidate_loglikelihood':(3,128,4),'without_routed_fixed_shared_candidate_loglikelihood':(3,128,4),'without_routed_natural_shared_candidate_loglikelihood':(128,4),'without_both_candidate_loglikelihood':(128,4),'gold':(128,),'subject':(128,),'answer_tokens':(128,4),'answer_chars':(128,4),'shared_signal_hashes':(3,128)}
    for key,shape in shapes.items():
        if key not in a or a[key].shape!=shape or (a[key].dtype.kind in 'fi' and not np.isfinite(a[key]).all()): raise ValueError('invalid array '+key)
    if tuple(a['consumer_names'])!=NAMES or tuple(a['producer_names'])!=NAMES: raise ValueError('source axes')
    if not np.array_equal(np.bincount(a['subject'],minlength=2),[64,64]) or np.any((a['gold']<0)|(a['gold']>3)) or np.any(a['answer_tokens']<=0) or np.any(a['answer_chars']<=0): raise ValueError('population')
    if a['shared_signal_hashes'].dtype.kind!='U' or any(len(x)!=64 or any(c not in '0123456789abcdef' for c in x) for x in a['shared_signal_hashes'].flat): raise ValueError('signal hashes')
    for i in range(3):
        if not np.array_equal(a['clamped_candidate_loglikelihood'][i,i],a['natural_candidate_loglikelihood'][i]): raise ValueError('diagonal exact replay')

def validate_ledger(plan,ledger):
    attempts=ledger['attempts']
    if not attempts or attempts[-1]['status']!='complete' or any(a['status'] not in ('complete','failed') for a in attempts): raise ValueError('budget incomplete')
    if plan['limit_gpu_seconds']!=10800 or ledger['limit_gpu_seconds']!=10800 or sum(x['gpu_seconds'] for x in attempts)>10800: raise ValueError('budget cap')

def self_test():
    q=128; gold=np.zeros(q,int); sub=np.repeat([0,1],64); den=np.ones((q,4)); base=np.zeros((q,4)); base[:,1:]=-2
    natural=np.stack([base.copy() for _ in range(3)]); no_s=natural.copy(); no_s[:,:,0]-=1; fixed=natural.copy(); fixed[:,:,0]-=.5
    clamp=np.broadcast_to(natural[:,None],(3,3,q,4)).copy(); clamp[1,0,:,0]+=1; clamp[2,0,:,0]+=2
    a={'clamped_candidate_loglikelihood':clamp,'natural_candidate_loglikelihood':natural,'without_shared_candidate_loglikelihood':no_s,'without_routed_fixed_shared_candidate_loglikelihood':fixed,'without_routed_natural_shared_candidate_loglikelihood':base-1,'without_both_candidate_loglikelihood':base,'gold':gold,'subject':sub,'answer_tokens':den,'answer_chars':den,'consumer_names':np.array(NAMES),'producer_names':np.array(NAMES),'shared_signal_hashes':np.full((3,q),'a'*64)}
    validate_arrays(a); out=aggregate(a)
    assert np.allclose(np.array(out['shared_support']['point'])[3,:,0],[1,2,3])
    assert np.allclose(np.array(out['controlled_routed_support']['point'])[3,:,0],[.5,1.5,2.5])
    assert np.allclose(np.array(out['routed_deleted_fixed_signal_recovery']['point'])[3],[.5]*3)
    assert np.allclose(np.array(out['shared_support_fixed_producer_consumer_A_B_minus_P']['point'])[3,:,0],[1,2])
    assert np.allclose(np.array(out['off_diagonal_minus_diagonal_full_quality']['point'])[3],-.5)
    b=secondary(a); assert b['count']==128 and b['cells']['PP']['counts'][7]==128
    a['clamped_candidate_loglikelihood'][:,:,64:,0]=-3
    b=secondary(a); assert b['count']==64 and b['cells']['PP']['equal_subject_rates'] is None and b['points']['full']['equal_subject_macro_point'] is None
    # Independently exercise every pattern, with full correct cohort fixed.
    for i in range(8):
        a['without_both_candidate_loglikelihood'][i,0]=0 if i&4 else -3
        a['without_shared_candidate_loglikelihood'][:,i,0]=0 if i&2 else -3
        a['without_routed_fixed_shared_candidate_loglikelihood'][:,i,0]=0 if i&1 else -3
    b=secondary(a); assert b['cells']['PP']['counts']==[1,1,1,1,1,1,1,57]
    prior={'limit_gpu_seconds':10800}; validate_ledger(prior,{'limit_gpu_seconds':10800,'attempts':[{'status':'complete','gpu_seconds':1}]})
    try: validate_ledger(prior,{'limit_gpu_seconds':10800,'attempts':[{'status':'running','gpu_seconds':1}]})
    except ValueError: pass
    else: raise AssertionError('unfinished budget accepted')
    print('CPU synthetic axes, signs, paired bootstrap, eight patterns, empty subject and budget checks passed')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); args=p.parse_args()
    if args.self_test: self_test()
    else: p.error('formal audit awaits frozen plan/reference schema')
