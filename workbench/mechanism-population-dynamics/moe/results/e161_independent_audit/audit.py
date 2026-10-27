#!/usr/bin/env python3
"""E161 independent CPU recomputation; no model or author analyzer imports."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
WB=Path(__file__).resolve().parents[2]; ROOT=WB/'results/e161'
MODELS=('P','A','B'); PATHS=('R','S','RS','A'); CATEGORIES=('original','entity_hybrid','relation_hybrid','full_donor','other')
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()
def read(path): return json.loads(Path(path).read_text())
def paired_country(values):
    """Same 24 country indices across the two relations and compared conditions."""
    x=np.asarray(values,dtype=np.float64)
    if x.shape[-2:]!=(2,24):raise ValueError('expected relation x country')
    draws=np.random.default_rng(161001).integers(0,24,size=(1000,24))
    by_relation=x.mean(-1)
    resampled=np.take(x,draws,axis=-1).mean(-1)
    overall=resampled.mean(-2)
    return {'point':by_relation.mean(-1).tolist(),
            'ci95':np.moveaxis(np.quantile(overall,[.025,.975],axis=-1),0,-1).tolist(),
            'per_relation_point':by_relation.tolist(),
            'per_relation_ci95':np.moveaxis(np.quantile(resampled,[.025,.975],axis=-1),0,-1).tolist()}


def subset_stats(x,mask):
    a=np.asarray(x,dtype=float); selected=np.broadcast_to(mask,a.shape)
    count=selected.sum(-1);total=np.where(selected,a,0).sum(-1)
    mean=np.divide(total,count,out=np.full_like(total,np.nan),where=count>0)
    macro=np.where(np.all(count>0,axis=-1),np.nan_to_num(mean).mean(-1),np.nan)
    def clean(v):
        v=np.asarray(v); return np.where(np.isfinite(v),v,None).tolist()
    return {'per_relation_count':count.tolist(),'per_relation_point':clean(mean),'macro_point':clean(macro),'ci':'not computed'}




def make_map(d):
    target=d['target_query_index']; gold=d['gold_token']; expected=np.arange(24)
    if target.shape!=(2,24) or not np.array_equal(target,np.stack((expected,48+expected))): raise ValueError('canonical target mapping')
    queries=np.empty((2,24,4),dtype=int)
    for r in (0,1):
        for c in range(24):
            h=(c+11)%24; queries[r,c]=[target[r,c],target[r,h],target[1-r,c],target[1-r,h]]
    labels=gold[queries]
    if any(len(set(row))!=4 for row in labels.reshape(-1,4)): raise ValueError('four labels not distinct')
    if len(np.unique(d['token_union']))!=38 or not np.array_equal(np.unique(gold),d['token_union']): raise ValueError('token union mismatch')
    return queries,labels

def classify(top1,labels):
    # labels is (2,24,4); full-vocabulary top1 drives categorization.
    hits=top1[...,None]==labels
    if np.any(hits.sum(-1)>1): raise ValueError('overlapping categories')
    return np.concatenate((hits,~hits.any(-1,keepdims=True)),axis=-1)

def calculate(a,d):
    query,labels=make_map(d); targets=query[:,:,0]; gold=d['gold_token']; loc={int(t):i for i,t in enumerate(d['token_union'])}; indices=np.array([[[loc[int(t)] for t in row] for row in rel] for rel in labels]);
    top=a['patched_top_tokens'][...,0]; native_top=a['native_top_tokens'][:,targets,0]; cat=classify(top,labels); ncat=classify(native_top,labels)
    if not np.all(cat.sum(-1)==1) or not np.all(ncat.sum(-1)==1): raise ValueError('category partition')
    m={}
    for i,name in enumerate(CATEGORIES):
        m[name+'_rate']=cat[...,i].astype(float); m[name+'_baseline_rate']=np.broadcast_to(ncat[:,None,:,:,i],cat.shape[:-1]).astype(float); m[name+'_baseline_relative_change']=m[name+'_rate']-m[name+'_baseline_rate']
    base=a['native_lp_selected'][:,targets,:]; patched=a['patched_lp_selected']
    for i,name in enumerate(CATEGORIES[:4]):
        index=indices[:,:,i]; native=np.take_along_axis(base,index[None,:,:,None],-1)[...,0]; changed=np.take_along_axis(patched,index[None,None,:,:,None],-1)[...,0]
        m[name+'_logprob_gain']=changed-native[:,None,:,:]
    m['KL']=a['patched_KL_vs_native']
    correctly=(a['native_top_tokens'][:,:,0]==gold); eligible=correctly[:,query].all(axis=(0,3))
    hits=(a['native_top_tokens']==gold[None,:,None]).any(-1); gate=hits[:,query].all(axis=(0,3))
    return m,eligible,gate,cat

def summarize(m,eligible):
    out={'all':{},'history':{},'preferences':{},'common_success':{}}
    for name,x in m.items():
        out['all'][name]=paired_country(x); out['history'][name]={'A_minus_P':paired_country(x[1]-x[0]),'B_minus_P':paired_country(x[2]-x[0])};out['common_success'][name]=subset_stats(x,eligible[None,None,:,:])
    for name in ('relation_hybrid','entity_hybrid'):
        pref=m[name+'_rate']-m['full_donor_rate']; out['preferences'][name+'_minus_full_donor']=paired_country(pref);out['preferences'][name+'_minus_full_donor_R_minus_A']=paired_country(pref[:,0]-pref[:,3])
    return out

def validate_raw(a,d,patch):
    if tuple(a['source_names'])!=MODELS or tuple(a['component_names'])!=PATHS: raise ValueError('source/path order')
    shapes={'native_lp_selected':(3,96,38),'native_top_tokens':(3,96,10)}
    science={'patched_lp_selected':(3,4,2,24,38),'patched_top_tokens':(3,4,2,24,10),'patched_KL_vs_native':(3,4,2,24),'positive_lp_selected':(3,2,24,38),'positive_top_tokens':(3,2,24,10)}
    if patch: shapes.update(science)
    elif any(k in a for k in science): raise ValueError('baseline-only contains science arrays')
    for k,shape in shapes.items():
        if k not in a or a[k].shape!=shape or (a[k].dtype.kind in 'fi' and not np.isfinite(a[k]).all()): raise ValueError('invalid '+k)
    query,_=make_map(d)
    if patch:
        for r in range(2):
            for c in range(24):
                q=query[r,c,3]
                if not np.array_equal(a['positive_lp_selected'][:,r,c],a['native_lp_selected'][:,q]) or not np.array_equal(a['positive_top_tokens'][:,r,c],a['native_top_tokens'][:,q]): raise ValueError('source residual identity')

def validate_ledger(plan,ledger):
    attempts=ledger['attempts']
    if not attempts or any(a['status']!='complete' for a in attempts): raise ValueError('incomplete budget')
    if ledger['limit_gpu_seconds']!=7200 or plan['limit_gpu_seconds']!=7200 or sum(a['gpu_seconds'] for a in attempts)>7200: raise ValueError('budget cap')

def audit():
    plan_path=ROOT/'plan.json'; plan=read(plan_path); manifest=read(ROOT/'manifest.json'); ledger=read(ROOT/'budget.json'); validate_ledger(plan,ledger)
    if manifest['status']!='complete' or sha(plan_path)!=manifest['plan_sha256'] or manifest['source_sha256']!=plan['source_sha256']: raise ValueError('plan/manifest mismatch')
    if plan['execution_mode']!='whole_terminal_path_fixed_native_prefix_no_KV_cache' or plan['bootstrap']['seed']!=161001 or plan['bootstrap']['resamples']!=1000: raise ValueError('protocol mismatch')
    if manifest['patch_rows']!=576 or manifest['positive_residual_rows']!=144 or manifest['same_query_identity_cases']!=588 or not all(manifest['controls'].values()): raise ValueError('engineering controls')
    models=read(WB/'results/e150/metadata.json')['models']; parent=read(WB/'results/e154/metadata.json')['model']
    for name,expected in plan['source_sha256'].items():
        if '/' in name:
            source,filename=name.split('/',1); asset=(parent if source=='parent' else models[source])['files'][filename]
            if asset['sha256']!=expected: raise ValueError('source asset identity '+name)
            path=asset['path']
        else: path=WB/'scripts'/name
        if sha(path)!=expected: raise ValueError('source hash '+name)
    for key in ('task_data','outcome_map','baseline_reference','component_reference','attention_reference','execution_manifest','legacy_cal_input'):
        if sha(plan[key]['path'])!=plan[key]['sha256']: raise ValueError('asset hash '+key)
    old=read(WB/'results/e158/whole_path/manifest.json')
    if old['status']!='complete' or plan['baseline_reference']['sha256']!=old['raw']['sha256'] or plan['attention_reference']['sha256']!=old['attention_components']['sha256']: raise ValueError('E158 whole reference mismatch')
    prior=read(WB/'results/e158/whole_path/plan.json')
    if sha(WB/'results/e158/whole_path/plan.json')!=old['plan_sha256'] or plan['component_reference']['sha256']!=prior['component_reference']['sha256']: raise ValueError('component lineage mismatch')
    for i,name in enumerate(MODELS):
        rec=plan['source_records'][name]
        if rec['parameter_hash']!=old['source_parameter_hashes'][i] or rec['buffer_hash']!=old['source_buffer_hashes'][i] or sha(rec['calibration']['path'])!=rec['calibration']['sha256']: raise ValueError('canonical source '+name)
    if sha(manifest['raw']['path'])!=manifest['raw']['sha256']: raise ValueError('raw hash')
    def load(path):
        with np.load(path,allow_pickle=False) as f: return {k:f[k] for k in f.files}
    d=load(plan['task_data']['path']); mapping=load(plan['outcome_map']['path']); baseline=load(plan['baseline_reference']['path']); a=load(manifest['raw']['path']); query,labels=make_map(d)
    if not np.array_equal(mapping['outcome_query_indices'],query.transpose(2,0,1)) or not np.array_equal(mapping['outcome_token_ids'],labels.transpose(2,0,1)) or not np.array_equal(mapping['source_query_index_both'],query[:,:,3]) or not np.array_equal(mapping['token_union'],d['token_union']) or not np.array_equal(mapping['target_query_index'],d['target_query_index']): raise ValueError('outcome map mismatch')
    for k in ('native_lp_selected','native_top_tokens'):
        if not np.array_equal(a[k],baseline[k]): raise ValueError('native reference mismatch '+k)
    validate_raw(a,d,True); m,eligible,gate,cat=calculate(a,d)
    if not (gate.sum(-1)>=8).all() or manifest['baseline_joint_four_query_top10']!=gate.sum(-1).tolist(): raise ValueError('baseline gate')
    return {'status':'recomputed','raw_sha256':manifest['raw']['sha256'],'data_sha256':plan['task_data']['sha256'],'query_indices':query.tolist(),'outcome_token_ids':labels.tolist(),'baseline_joint_four_query_top10_counts':gate.sum(-1).tolist(),'common_success_counts':eligible.sum(-1).tolist(),'common_success_mask':eligible.tolist(),'positive_residual_selected_lp_and_top10_exact':True,'all_category_rates_sum_one':bool((cat.sum(-1)==1).all()),'KL_limitation':'only scalar full-vocabulary KL stored','recomputed':summarize(m,eligible)}

def self_test():
    # Each relation has 19 distinct labels across 24 countries; shifted pairs differ.
    gold=np.array([r*19+(c%19) for r in range(2) for template in range(2) for c in range(24)])
    d={'gold_token':gold,'target_query_index':np.array([np.arange(24),48+np.arange(24)]),'token_union':np.arange(38)}
    query,labels=make_map(d); assert query[0,0].tolist()==[0,11,48,59]
    top=np.broadcast_to(labels[:,:,0],(3,4,2,24)).copy(); top[:,0]=labels[:,:,2]; top[:,3]=labels[:,:,3]; top[:,1]=999
    top10=np.broadcast_to(top[...,None],(3,4,2,24,10)).copy(); ntop=np.broadcast_to(gold[None,:,None],(3,96,10)).copy()
    a={'native_lp_selected':np.zeros((3,96,38)),'native_top_tokens':ntop,'patched_lp_selected':np.zeros((3,4,2,24,38)),'patched_top_tokens':top10,'patched_KL_vs_native':np.zeros((3,4,2,24))}
    m,mask,gate,cats=calculate(a,d); assert mask.all() and gate.all() and np.all(cats.sum(-1)==1)
    assert m['relation_hybrid_rate'][:,0].all() and m['full_donor_rate'][:,3].all() and m['other_rate'][:,1].all()
    out=summarize(m,mask); assert out['preferences']['relation_hybrid_minus_full_donor_R_minus_A']['point']==[2.,2.,2.]
    assert out['history']['original_rate']['A_minus_P']['point']==[0.,0.,0.,0.]
    check=paired_country(np.stack((np.arange(24),np.arange(24)+10))); assert check['point']==16.5
    duplicate=d.copy(); duplicate['gold_token']=gold.copy(); duplicate['gold_token'][59]=duplicate['gold_token'][0]
    try: make_map(duplicate)
    except ValueError: pass
    else: raise AssertionError('duplicate label accepted')
    validate_ledger({'limit_gpu_seconds':7200},{'limit_gpu_seconds':7200,'attempts':[{'status':'complete','gpu_seconds':1}]})
    try: validate_ledger({'limit_gpu_seconds':7200},{'limit_gpu_seconds':7200,'attempts':[{'status':'running','gpu_seconds':1}]})
    except ValueError: pass
    else: raise AssertionError('unfinished budget accepted')
    print('CPU synthetic mappings, full-vocabulary categories, axes, preferences, bootstrap and budget checks passed')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); p.add_argument('--audit',action='store_true'); p.add_argument('--output',type=Path); args=p.parse_args()
    if args.self_test: self_test()
    elif args.audit:
        if args.output is None: p.error('--output required')
        result=audit(); args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n'); print(result['status'])
    else: p.error('choose --self-test or --audit')
