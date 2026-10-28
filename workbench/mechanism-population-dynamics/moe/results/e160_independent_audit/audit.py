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

def compare_summary(a,report,manifest,plan_path):
    if report['experiment']!='E160' or report['status']!='complete' or report['consumer_order']!=list(NAMES) or report['producer_order']!=list(NAMES) or report['raw_sha256']!=manifest['raw']['sha256'] or report['plan_sha256']!=sha(plan_path) or report['analysis_source_sha256']!=manifest['source_sha256']['e160_analyze.py']: raise ValueError('summary provenance')
    gold=a['gold'];sub=a['subject'];tok=a['answer_tokens'];chars=a['answer_chars']; f=metrics(a['clamped_candidate_loglikelihood'],gold,tok,chars); n=metrics(a['natural_candidate_loglikelihood'],gold,tok,chars); s=metrics(a['without_shared_candidate_loglikelihood'],gold,tok,chars); r=metrics(a['without_routed_fixed_shared_candidate_loglikelihood'],gold,tok,chars); rn=metrics(a['without_routed_natural_shared_candidate_loglikelihood'],gold,tok,chars); d=metrics(a['without_both_candidate_loglikelihood'],gold,tok,chars)
    sg=np.array([-1,-1,1,1])[:,None,None,None]; shared=sg*(s[:,:,None]-f); direct=sg*(r[:,None]-f); natural=sg[:,:,0,:]*(s-n); recovery=sg[:,:,0,:]*(rn[:,None]-r)
    cohort=(a['clamped_candidate_loglikelihood'].argmax(-1)==gold).all((0,1)); rng=np.random.default_rng(160001); idx=[rng.choice(np.flatnonzero(sub==j),size=(1000,64),replace=True) for j in (0,1)]
    errors=[]; counts=[]
    def eq(x,y):
        if x is None or y is None:
            counts.append(x is None and y is None);return
        xx=np.asarray(x,dtype=float); yy=np.asarray(y,dtype=float)
        if xx.shape!=yy.shape: raise ValueError('summary shape mismatch')
        errors.extend(np.abs(xx-yy).reshape(-1).tolist())
    def check(x,t,secondary_mode):
        if secondary_mode:
            per=[x[cohort&(sub==j)] for j in (0,1)]; n0=[len(z) for z in per]; means=[float(z.mean()) if len(z) else None for z in per]; macro=(means[0]+means[1])/2 if all(z is not None for z in means) else None
            eq(macro,t['point']); eq(float(x[cohort].mean()) if cohort.any() else None,t['pooled_point']); counts.extend([t['count']==int(cohort.sum()),t['ci']=='not computed'])
            for j,name in enumerate(('high_school_biology','high_school_mathematics')): counts.append(t['per_subject'][name]['count']==n0[j]);eq(means[j],t['per_subject'][name]['point'])
        else:
            z=stat(x,sub,idx);eq(z['point'],t['point']);eq(z['ci95'],t['question_ci95']);counts.extend([t['count']==128,t['bootstrap_seed']==160001])
            for j,name in enumerate(('high_school_biology','high_school_mathematics')): counts.append(t['per_subject'][name]['count']==64);eq(z['per_subject_point'][j],t['per_subject'][name]['point']);eq(z['per_subject_ci95'][j],t['per_subject'][name]['question_ci95'])
    def matrix(v,t,mode):
        if v.ndim==1: check(v,t,mode)
        else:
            for i in range(v.shape[0]): matrix(v[i],t[i],mode)
    for k,name in enumerate(METRICS):
        for mode in ('primary','secondary'):
            obj=report['metrics'][name][mode]; sec=(mode=='secondary'); cond=obj['conditions']; contrast=obj['contrasts']
            for label,v in [('full',f[k]),('natural',n[k]),('zero_shared',s[k]),('zero_routed_fixed_shared',r[k]),('zero_routed_natural_shared',rn[k]),('zero_both',d[k])]:matrix(v,cond[label],sec)
            fixed=shared[k,1:]-shared[k,0:1]; nat=natural[k,1:]-natural[k,0:1]
            values={'full_fixed_producer_consumer_contrasts':f[k,1:]-f[k,0:1], 'full_fixed_consumer_producer_contrasts':f[k,:,1:]-f[k,:,0:1], 'shared_necessity':shared[k], 'direct_online_routed_necessity':direct[k], 'direct_online_fixed_producer_consumer_contrasts':direct[k,1:]-direct[k,0:1], 'direct_online_fixed_consumer_producer_contrasts':direct[k,:,1:]-direct[k,:,0:1], 'natural_shared_necessity':natural[k], 'fixed_producer_consumer_contrasts':fixed,'fixed_consumer_producer_contrasts':shared[k,:,1:]-shared[k,:,0:1], 'fixed_producer_minus_natural_consumer_contrasts':fixed-nat[:,None,:], 'recovery_under_routed_removal':recovery[k], 'off_diagonal_minus_diagonal_matching_cost':np.stack([f[k,i,j] for i in range(3) for j in range(3) if i!=j]).mean(0)-np.stack([f[k,i,i] for i in range(3)]).mean(0)}
            for label,v in values.items():matrix(v,contrast[label],sec)
    sec=secondary(a); other=report['all_nine_full_correct'];counts.extend([other['count']==sec['count'],other['per_subject']==sec['per_subject_count'],other['mask']==sec['mask']]); pat=other['patterns']; counts.append(pat['bits']=={'D':4,'R_with_shared_zero':2,'shared_replay_with_routed_zero':1})
    names=('high_school_biology','high_school_mathematics')
    for cell,value in sec['cells'].items():
        got=pat['cells'][cell];counts.append(got['counts']==value['counts']);counts.extend(got['per_subject_counts'][name]==value['per_subject_counts'][j] for j,name in enumerate(names))
    for axis in ('producer','consumer'):
        for fixed in NAMES:
            for b,e in (('P','A'),('P','B'),('A','B')):
                value=sec['transitions'][f'fixed_{axis}_{fixed}_{b}_to_{e}'];got=pat['transitions']['fixed_'+axis][fixed+'_'+b+'_to_'+e];counts.append(got['counts']==value['counts']);counts.extend(got['per_subject_counts'][name]==value['per_subject_counts'][j] for j,name in enumerate(names))
    maxerr=max(errors,default=0.); return {'status':'passed' if maxerr<1e-10 and all(counts) else 'failed','max_absolute_error':maxerr,'numeric_comparisons':len(errors),'count_checks':len(counts),'all_counts_match':all(counts)}

def audit():
    plan_path=ROOT/'plan.json';plan=read(plan_path);manifest=read(ROOT/'manifest.json');ledger=read(ROOT/'budget.json');validate_ledger(plan,ledger)
    if manifest['status']!='complete' or manifest['source_sha256']!=plan['source_sha256'] or sha(plan_path)!=manifest['plan_sha256'] or manifest['regular_question_condition_calls']!=2560 or manifest['extra_source_collapse_calls']!=12 or not all(manifest['controls'].values()):raise ValueError('manifest/control')
    if plan['bootstrap']['seed']!=160001 or plan['bootstrap']['resamples']!=1000:raise ValueError('bootstrap')
    models=read(WB/'results/e150/metadata.json')['models'];parent=read(WB/'results/e154/metadata.json')['model']
    for name,expected in plan['source_sha256'].items():
        if '/' in name:
            source,filename=name.split('/',1); asset=(parent if source=='parent' else models[source])['files'][filename];path=asset['path']
            if asset['sha256']!=expected:raise ValueError('asset record '+name)
        else:path=WB/'scripts'/name
        if sha(path)!=expected:raise ValueError('source '+name)
    def verify(item):
        if sha(item['path'])!=item['sha256']:raise ValueError('hash '+item['path'])
    for name in ('task_input','references','execution_manifest','legacy_cal_input'):verify(plan[name])
    for record in plan['reference_records'].values():
        verify(record['manifest']);verify(record['raw']); old=read(record['manifest']['path'])
        if old['status']!='complete' or old['raw']['sha256']!=record['raw']['sha256']:raise ValueError('reference manifest')
    for i,name in enumerate(NAMES):
        r=plan['source_records'][name];verify(r['calibration'])
        if r['parameter_hash']!=manifest['canonical_parameter_hashes'][i] or r['buffer_hash']!=manifest['canonical_buffer_hashes'][i]:raise ValueError('canonical identity')
    verify(manifest['raw'])
    with np.load(manifest['raw']['path'],allow_pickle=False) as f:a={k:f[k] for k in f.files}
    with np.load(plan['references']['path'],allow_pickle=False) as f:ref={k:f[k] for k in f.files}
    validate_arrays(a)
    for k in ('natural_candidate_loglikelihood','without_shared_candidate_loglikelihood','without_routed_natural_shared_candidate_loglikelihood','without_both_candidate_loglikelihood','gold','subject','answer_tokens','answer_chars'):
        if not np.array_equal(a[k],ref[k]):raise ValueError('reference identity '+k)
    return a,manifest,{'status':'recomputed','raw_sha256':manifest['raw']['sha256'],'primary':aggregate(a),'secondary':secondary(a),'scope':'S replay retains producer R effects; controlled routed support is not total routed knowledge'}

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
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); p.add_argument('--audit',action='store_true');p.add_argument('--summary',type=Path);p.add_argument('--output',type=Path); args=p.parse_args()
    if args.self_test: self_test()
    elif args.audit:
        if not args.output or not args.summary:p.error('--output and --summary required')
        raw,manifest,result=audit(); result['comparison']=compare_summary(raw,read(args.summary),manifest,ROOT/'plan.json');args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(result['comparison']);
        if result['comparison']['status']!='passed':raise SystemExit(1)
    else: p.error('choose --self-test or --audit')
