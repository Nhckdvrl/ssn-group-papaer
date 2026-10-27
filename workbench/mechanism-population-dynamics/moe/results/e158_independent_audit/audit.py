"""E158 independent CPU raw recomputation; no author analysis code or model."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'e158'
MODELS=('P','A','B'); SCENARIOS=('entity','attribute','paraphrase'); COMPONENTS=('R','S','RS')


def digest(path):
    with open(path,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def paired_country(values):
    """Same 24 country indices across the two relations and compared conditions."""
    x=np.asarray(values,dtype=np.float64)
    if x.shape[-2:]!=(2,24):raise ValueError('expected relation x country')
    draws=np.random.default_rng(158001).integers(0,24,size=(1000,24))
    by_relation=x.mean(-1)
    resampled=np.take(x,draws,axis=-1).mean(-1)
    overall=resampled.mean(-2)
    return {'point':by_relation.mean(-1).tolist(),
            'ci95':np.moveaxis(np.quantile(overall,[.025,.975],axis=-1),0,-1).tolist(),
            'per_relation_point':by_relation.tolist(),
            'per_relation_ci95':np.moveaxis(np.quantile(resampled,[.025,.975],axis=-1),0,-1).tolist()}


def win_fraction(x, token_idx, distractor_indices):
    ref=x[...,token_idx,None];other=x[...,distractor_indices]
    return ((ref>other).astype(np.float64)+.5*(ref==other)).mean(-1)


def validate_data(d):
    shapes={'gold_token':(96,), 'relation':(96,), 'country':(96,), 'template':(96,),
      'target_query_index':(2,24),'source_query_index':(3,2,24),'control_token':(3,2,24),
      'range_token_ids':(2,24),'range_count':(2,),'token_union':(38,)}
    for k,v in shapes.items():
        if k not in d or d[k].shape!=v:raise ValueError('bad data '+k)
    if not np.array_equal(d['token_union'],np.unique(d['gold_token'])):raise ValueError('bad token union')
    for r in range(2):
        expected=np.arange(24)+48*r
        if not np.array_equal(d['target_query_index'][r],expected):raise ValueError('bad target index')
        if not np.array_equal(np.sort(d['range_token_ids'][r,:d['range_count'][r]]),np.unique(d['gold_token'][expected])):
            raise ValueError('bad relation token range')
        for s in range(3):
            sources=d['source_query_index'][s,r]; gold=d['gold_token'][expected]; sgold=d['gold_token'][sources]
            expected_source=48*r+(np.arange(24)+11)%24 if s==0 else 48*(1-r)+np.arange(24) if s==1 else 48*r+24+np.arange(24)
            if not np.array_equal(sources,expected_source):raise ValueError('bad source mapping')
            controls=d['control_token'][s,r]
            if np.any(controls==gold) or np.any(controls==sgold) or not np.array_equal(np.sort(controls),np.sort(sgold)):
                raise ValueError('bad controls')
            if (s<2 and np.any(sgold==gold)) or (s==2 and not np.array_equal(sgold,gold)):
                raise ValueError('bad source and target label relationship')


def shapecheck(a,key,shape):
    if key not in a or a[key].shape!=shape:raise ValueError(f'bad raw {key}, expected {shape}')
    if a[key].dtype.kind in 'fi' and not np.isfinite(a[key]).all():raise ValueError('nonfinite '+key)


def inspect_raw(a,d,patch):
    for name,labels in (('source_names',MODELS),('scenario_names',SCENARIOS),('component_names',COMPONENTS)):
        if tuple(a[name])!=labels:raise ValueError('incorrect '+name)
    for key,shape in {'native_lp_selected':(3,96,38),'uncached_lp_selected':(3,96,38),
      'native_top_tokens':(3,96,10),'uncached_top_tokens':(3,96,10),'cache_KL':(3,96),
      'positive_lp_selected':(3,3,2,24,38),'positive_top_tokens':(3,3,2,24,10)}.items():shapecheck(a,key,shape)
    src=d['source_query_index']
    for s in range(3):
        for r in range(2):
            for c in range(24):
                q=src[s,r,c]
                if not np.array_equal(a['positive_lp_selected'][:,s,r,c],a['native_lp_selected'][:,q]):raise ValueError('positive selected LP identity failed')
                if not np.array_equal(a['positive_top_tokens'][:,s,r,c],a['native_top_tokens'][:,q]):raise ValueError('positive top-token identity failed')
    patch_keys={'patched_lp_selected':(3,3,3,16,2,24,38),'patched_top_tokens':(3,3,3,16,2,24,10),
      'patched_KL_vs_native':(3,3,3,16,2,24),'matched_removal_lp_selected':(3,3,16,2,24,38),
      'matched_removal_top_tokens':(3,3,16,2,24,10),'matched_removal_KL_vs_native':(3,3,16,2,24)}
    if patch:
        for k,sh in patch_keys.items():shapecheck(a,k,sh)
    elif any(k in a for k in patch_keys):raise ValueError('baseline-only raw contains patch array')


def get_baseline(a,d):
    gold=d['gold_token'];top=a['native_top_tokens'];uncached=a['uncached_top_tokens'];target=d['target_query_index']
    hit1=top[:,:,0]==gold;hit10=np.any(top==gold[None,:,None],axis=-1)
    return {'native_selected_logp_all96':a['native_lp_selected'].tolist(),'native_top_tokens_all96':top.tolist(),'uncached_top_tokens_all96':uncached.tolist(),'native_top1_all96':hit1.tolist(),'native_top10_all96':hit10.tolist(),
      'native_top1_count_by_model':hit1.sum(-1).tolist(),'native_top10_count_by_model':hit10.sum(-1).tolist(),
      'canonical_top1_by_model_relation':hit1[:,target].sum(-1).tolist(),
      'canonical_top10_by_model_relation':hit10[:,target].sum(-1).tolist(),
      'common_top10_by_relation':hit10[:,target].all(axis=0).sum(-1).tolist(),
      'floor':{'cache_kl_all96':a['cache_KL'].tolist(),'cache_KL_max':float(a['cache_KL'].max()),
       'top1_changed_count':(top[:,:,0]!=uncached[:,:,0]).sum(-1).tolist(),
       'selected_logp_max_abs_difference':float(np.max(np.abs(a['native_lp_selected']-a['uncached_lp_selected']))),
       'selected_logp_exact_mismatch_count':(a['native_lp_selected']!=a['uncached_lp_selected']).sum(axis=(1,2)).tolist()}}


def compute(a,d):
    """Return question-level metrics, preserving all source/component/layer axes."""
    vocab={int(t):i for i,t in enumerate(d['token_union'])}; qgold=d['gold_token'];target=d['target_query_index'];source=d['source_query_index']
    sh=(3,3,3,16,2,24)
    names=('source_rank_specificity_gain','source_control_logodds_gain','source_logprob_gain','target_logprob_change','source_hit1','source_hit10','target_hit1','KL')
    metrics={name:np.empty(sh,dtype=float) for name in names};eligible=np.zeros((3,2,24),dtype=bool)
    for s in range(3):
        for r in range(2):
            sr=1-r if s==1 else r
            alternatives=d['range_token_ids'][sr,:d['range_count'][sr]]
            for c in range(24):
                tq=int(target[r,c]);sq=int(source[s,r,c]);source_token=int(qgold[sq]);target_token=int(qgold[tq]);control=int(d['control_token'][s,r,c])
                y,k,z=(vocab[t] for t in (source_token,control,target_token))
                distract=np.array([vocab[int(t)] for t in alternatives if int(t) not in {source_token,control,target_token}])
                if not len(distract):raise ValueError('empty distractors')
                native=a['native_lp_selected'][:,tq,None,None,:]
                p=a['patched_lp_selected'][:,s,:,:,r,c,:]
                metrics['source_rank_specificity_gain'][:,s,:,:,r,c]=((win_fraction(p,y,distract)-win_fraction(p,k,distract))-
                                                                         (win_fraction(native,y,distract)-win_fraction(native,k,distract)))
                metrics['source_control_logodds_gain'][:,s,:,:,r,c]=(p[...,y]-p[...,k])-(native[...,y]-native[...,k])
                metrics['source_logprob_gain'][:,s,:,:,r,c]=p[...,y]-native[...,y]
                metrics['target_logprob_change'][:,s,:,:,r,c]=p[...,z]-native[...,z]
                top=a['patched_top_tokens'][:,s,:,:,r,c,:]
                metrics['source_hit1'][:,s,:,:,r,c]=top[...,0]==source_token
                metrics['source_hit10'][:,s,:,:,r,c]=np.any(top==source_token,axis=-1)
                metrics['target_hit1'][:,s,:,:,r,c]=top[...,0]==target_token
                metrics['KL'][:,s,:,:,r,c]=a['patched_KL_vs_native'][:,s,:,:,r,c]
                eligible[s,r,c]=bool(np.all(a['native_top_tokens'][:,tq,0]==target_token) and np.all(a['native_top_tokens'][:,sq,0]==source_token))
    target_gold=qgold[target];loc=np.array([[vocab[int(t)] for t in row] for row in target_gold])
    base=a['native_lp_selected'][:,target,:];rem=a['matched_removal_lp_selected']
    orig=np.take_along_axis(base,loc[None,:,:,None],axis=-1)[...,0]
    changed=np.take_along_axis(rem,loc[None,None,None,:,:,None],axis=-1)[...,0]
    native_hit=a['native_top_tokens'][:,target,0]==target_gold[None,:,:]
    removal={'target_NLL_increase':orig[:,None,None,:,:]-changed,
      'target_top1_drop':native_hit[:,None,None,:,:].astype(float)-(a['matched_removal_top_tokens'][...,0]==target_gold[None,None,None,:,:]).astype(float),
      'KL':a['matched_removal_KL_vs_native']}
    return metrics,eligible,removal,native_hit.all(axis=0)


def subset_stats(x,mask):
    a=np.asarray(x,dtype=float); selected=np.broadcast_to(mask,a.shape)
    count=selected.sum(-1);total=np.where(selected,a,0).sum(-1)
    mean=np.divide(total,count,out=np.full_like(total,np.nan),where=count>0)
    macro=np.where(np.all(count>0,axis=-1),np.nan_to_num(mean).mean(-1),np.nan)
    def clean(v):
        v=np.asarray(v); return np.where(np.isfinite(v),v,None).tolist()
    return {'per_relation_count':count.tolist(),'per_relation_point':clean(mean),'macro_point':clean(macro),'ci':'not computed'}


def summarize_metrics(metrics,removal,eligible,target_success):
    out={'all':{},'layer_mean':{},'contrasts':{},'common_success':{},'matched_removal':{'all':{},'layer_mean':{},'contrasts':{},'common_target_success':{}}}
    for key,x in metrics.items():
        out['all'][key]=paired_country(x); out['layer_mean'][key]=paired_country(x.mean(axis=3))
        out['common_success'][key]=subset_stats(x,eligible[None,:,None,None,:,:])
        sr=x[:,:2,1]-x[:,:2,0]; feature=sr[:,0]-sr[:,1]
        contrasts={'A_minus_P':x[1]-x[0],'B_minus_P':x[2]-x[0],
          'layer_mean_A_minus_P':(x[1]-x[0]).mean(axis=2),'layer_mean_B_minus_P':(x[2]-x[0]).mean(axis=2),
          'S_minus_R_entity_attribute':sr,'S_minus_R_A_minus_P':sr[1]-sr[0],'S_minus_R_B_minus_P':sr[2]-sr[0],
          'layer_mean_S_minus_R_entity_attribute':sr.mean(axis=2),'layer_mean_S_minus_R_A_minus_P':(sr[1]-sr[0]).mean(axis=1),
          'layer_mean_S_minus_R_B_minus_P':(sr[2]-sr[0]).mean(axis=1),
          'entity_minus_attribute_S_minus_R':feature,'entity_minus_attribute_S_minus_R_A_minus_P':feature[1]-feature[0],
          'entity_minus_attribute_S_minus_R_B_minus_P':feature[2]-feature[0],
          'layer_mean_entity_minus_attribute_S_minus_R':feature.mean(axis=1),
          'layer_mean_entity_minus_attribute_S_minus_R_A_minus_P':(feature[1]-feature[0]).mean(axis=0),
          'layer_mean_entity_minus_attribute_S_minus_R_B_minus_P':(feature[2]-feature[0]).mean(axis=0)}
        out['contrasts'][key]={k:paired_country(v) for k,v in contrasts.items()}
    dest=out['matched_removal']
    for key,x in removal.items():
        dest['all'][key]=paired_country(x);dest['layer_mean'][key]=paired_country(x.mean(axis=2));sr=x[:,1]-x[:,0]
        dest['common_target_success'][key]=subset_stats(x,target_success[None,None,None,:,:])
        cases={'A_minus_P':x[1]-x[0],'B_minus_P':x[2]-x[0],
          'layer_mean_A_minus_P':(x[1]-x[0]).mean(axis=1),'layer_mean_B_minus_P':(x[2]-x[0]).mean(axis=1),
          'S_minus_R':sr,'S_minus_R_A_minus_P':sr[1]-sr[0],'S_minus_R_B_minus_P':sr[2]-sr[0],
          'layer_mean_S_minus_R':sr.mean(axis=1),'layer_mean_S_minus_R_A_minus_P':(sr[1]-sr[0]).mean(axis=0),
          'layer_mean_S_minus_R_B_minus_P':(sr[2]-sr[0]).mean(axis=0)}
        dest['contrasts'][key]={k:paired_country(v) for k,v in cases.items()}
    return out


def compare_tree(path, expected, actual, diffs, counts):
    """Compare all numeric scalars/arrays, including None for empty subsets."""
    if isinstance(expected,dict):
        if not isinstance(actual,dict):diffs.append(path+': expected object');return
        for k,v in expected.items():
            if k not in actual:diffs.append(path+'/'+k+': missing');continue
            compare_tree(path+'/'+k,v,actual[k],diffs,counts)
        return
    if isinstance(expected,str):
        if expected!=actual:diffs.append(path+': text differs')
        return
    try:
        left=np.asarray(expected,dtype=object);right=np.asarray(actual,dtype=object)
        if left.shape!=right.shape:diffs.append(path+': shape differs');return
        left_null=np.equal(left,None);right_null=np.equal(right,None)
        if not np.array_equal(left_null,right_null):diffs.append(path+': null mask differs');return
        valid=~left_null
        if np.any(valid):
            lv=np.asarray(left[valid],dtype=np.float64);rv=np.asarray(right[valid],dtype=np.float64)
            if not np.isfinite(lv).all() or not np.isfinite(rv).all():diffs.append(path+': nonfinite');return
            err=float(np.max(np.abs(lv-rv)));counts['max_absolute_error']=max(counts['max_absolute_error'],err)
            counts['numeric_elements']+=len(lv)
            if err>1e-10:diffs.append(f'{path}: max error {err:.12g}')
    except (TypeError,ValueError):diffs.append(path+': malformed values')


def compare_summary(recomputed,summary,patch,data_hash):
    if summary.get('status')!=('complete' if patch else 'baseline_only') or summary.get('data_sha256')!=data_hash:
        raise ValueError('summary status or data SHA mismatch')
    for name,want in [('models',MODELS),('scenarios',SCENARIOS),('paths',COMPONENTS)]:
        if tuple(summary.get(name,()))!=want:raise ValueError('summary order mismatch: '+name)
    if summary.get('seed')!=158001:raise ValueError('summary bootstrap seed mismatch')
    diffs=[];counts={'numeric_elements':0,'max_absolute_error':0.}
    compare_tree('baseline',recomputed['baseline'],summary.get('baseline'),diffs,counts)
    if patch:
        work=recomputed['recomputed']
        for section in ('all','layer_mean','contrasts','matched_removal'):
            actual=summary.get(section,{})
            if section=='matched_removal':
                actual={**actual,'common_target_success':actual.get('common_target_success',{}).get('metrics',{})}
            compare_tree(section,work[section],actual,diffs,counts)
        expected_common={'counts_by_scenario_relation':recomputed['common_success_counts'],
                         'country_mask':recomputed['common_success_mask'],
                         'ci':'not computed','metrics':work['common_success']}
        compare_tree('common_success',expected_common,summary.get('common_success'),diffs,counts)
        expected_target={'counts_by_relation':recomputed['common_target_success_counts'],
                         'country_mask':recomputed['common_target_success_mask'],'ci':'not computed'}
        compare_tree('matched_removal/common_target_success',expected_target,
                     summary.get('matched_removal',{}).get('common_target_success'),diffs,counts)
        compare_tree('positive_control',recomputed['positive_control'],summary.get('positive_control'),diffs,counts)
    return {'status':'passed' if not diffs else 'failed',**counts,'tolerance':1e-10,'differences':diffs}


def validate_budget(attempts,plan,failure_path):
    if plan.get('execution_mode')=='full_prefix_fixed_native_causal_prefix_no_KV_cache':
        if (len(attempts)!=2 or attempts[0]!=plan.get('prior_failed_budget_attempt')
            or attempts[0].get('status')!='failed' or attempts[1].get('status')!='complete'
            or attempts[1].get('phase')!='factual_full_forward_interchange'):
            raise ValueError('expected preserved failed cached attempt and completed full-prefix attempt')
        if digest(failure_path)!=plan.get('prior_failure_sha256'):
            raise ValueError('prior cached failure SHA mismatch')
    elif not attempts or any(x.get('status')!='complete' for x in attempts):
        raise ValueError('budget incomplete; scientific raw not read')


def run(raw_path,data_path,summary_path,budget_path,manifest_path,plan_path):
    ledger=json.loads(budget_path.read_text());attempts=ledger.get('attempts',[])
    manifest=json.loads(manifest_path.read_text());plan=json.loads(plan_path.read_text())
    validate_budget(attempts,plan,ROOT/'cache_floor_failure.json')
    if manifest.get('status')!='complete' or digest(plan_path)!=manifest['plan_sha256']:raise ValueError('manifest/plan mismatch')
    if raw_path.resolve()!=Path(manifest['raw']['path']).resolve() or digest(raw_path)!=manifest['raw']['sha256']:raise ValueError('raw mismatch')
    if data_path.resolve()!=Path(plan['data']['path']).resolve() or digest(data_path)!=plan['data']['sha256']:raise ValueError('data mismatch')
    summary=json.loads(summary_path.read_text())
    if summary.get('raw_sha256')!=manifest['raw']['sha256']:raise ValueError('summary raw mismatch')
    patch=manifest.get('patch_data_obtained')
    if not isinstance(patch,bool):raise ValueError('missing patch status')
    with np.load(data_path,allow_pickle=False) as d, np.load(raw_path,allow_pickle=False) as a:
        validate_data(d);inspect_raw(a,d,patch);result={'status':'recomputed' if patch else 'baseline_only',
            'baseline':get_baseline(a,d),'positive_control_selected_LP_and_top_tokens_exact':True,
            'raw_sha256':manifest['raw']['sha256'],
            'KL_limitation':'raw stores KL scalar; vocabulary distribution KL cannot be recomputed'}
        if patch:
            metrics,eligible,removal,target_success=compute(a,d)
            result['common_success_counts']=eligible.sum(-1).tolist();result['common_target_success_counts']=target_success.sum(-1).tolist()
            result['common_success_mask']=eligible.tolist();result['common_target_success_mask']=target_success.tolist()
            result['recomputed']=summarize_metrics(metrics,removal,eligible,target_success)
            sources=d['gold_token'][d['source_query_index']]
            top=a['positive_top_tokens']
            result['positive_control']={'source_hit1':(top[...,0]==sources[None,:,:,:]).transpose(1,0,2,3).tolist(),
              'source_hit10':(top==sources[None,:,:,:,None]).any(-1).transpose(1,0,2,3).tolist()}
    if plan.get('execution_mode')=='full_prefix_fixed_native_causal_prefix_no_KV_cache':
        if manifest.get('execution_mode')!=plan['execution_mode'] or manifest.get('floor_kind')!=plan['floor_kind']:
            raise ValueError('full-prefix metadata mismatch')
        result['baseline']['floor'].update(kind=plan['floor_kind'],legacy_cache_field_names=True,KV_cache_used=False)
        if summary.get('execution_mode')!=plan['execution_mode']:
            raise ValueError('summary execution mode mismatch')
    check=compare_summary(result,summary,patch,plan['data']['sha256'])
    check.update(raw_sha256=manifest['raw']['sha256'],patch_data_obtained=patch,KL_limitation=result['KL_limitation'])
    return check


def self_test():
    logits=np.array([3.,2.,1.,2.]);assert win_fraction(logits,0,[2,3])==1 and win_fraction(logits,1,[2,3])==.75
    assert win_fraction(logits,1,[2,3])==win_fraction(logits*7,1,[2,3])
    values=np.stack([np.arange(24),np.arange(24)+10]);z=paired_country(values)
    assert z['point']==16.5 and np.allclose(z['per_relation_point'],[11.5,21.5])
    values=np.broadcast_to(np.arange(3)[:,None,None,None,None,None],(3,3,3,16,2,24)).copy()
    _,draws=values.shape, np.random.default_rng(158001).integers(0,24,size=(1000,24))
    assert np.all(np.take(values[1]-values[0],draws,axis=-1).mean(-1)==1)
    diffs=[];counter={'numeric_elements':0,'max_absolute_error':0.}
    compare_tree('synthetic',{'x':[1.,2.,None]},{'x':[1.,2.,None]},diffs,counter)
    assert not diffs and counter['numeric_elements']==2
    compare_tree('synthetic',{'x':[1.,2.,None]},{'x':[1.,3.,None]},diffs,counter)
    assert diffs
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        failure=Path(tmp)/'failure.json';failure.write_text('failed preflight')
        prior={'phase':'factual_cached_interchange','status':'failed'}
        plan={'execution_mode':'full_prefix_fixed_native_causal_prefix_no_KV_cache',
              'prior_failed_budget_attempt':prior,'prior_failure_sha256':digest(failure)}
        completed={'phase':'factual_full_forward_interchange','status':'complete'}
        validate_budget([prior,completed],plan,failure)
        for attempts in ([prior], [prior,completed,completed], [dict(prior,phase='other'),completed],
                         [prior,dict(completed,status='failed')], [prior,dict(completed,phase='other')]):
            try: validate_budget(attempts,plan,failure)
            except ValueError: pass
            else: raise AssertionError('invalid budget accepted')
        failure.write_text('changed')
        try: validate_budget([prior,completed],plan,failure)
        except ValueError: pass
        else: raise AssertionError('changed failure accepted')
    return {'status':'passed','CPU_only':True,'checks':['known rank ties and temperature','shared country paired CI','history difference known answer','summary comparator corruption detection','full-prefix budget and prior failure integrity']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--raw',type=Path);p.add_argument('--data',type=Path)
    p.add_argument('--summary',type=Path);p.add_argument('--budget',type=Path,default=ROOT/'budget.json');p.add_argument('--manifest',type=Path,default=ROOT/'manifest.json');p.add_argument('--plan',type=Path,default=ROOT/'plan.json');a=p.parse_args()
    if a.self_test:out=self_test()
    else:
        if not a.raw or not a.data or not a.summary:p.error('--raw, --data, and --summary required')
        out=run(a.raw,a.data,a.summary,a.budget,a.manifest,a.plan)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    if out.get('status')=='failed':raise SystemExit(1)
