#!/usr/bin/env python3
"""E158 whole-path independent CPU recomputation; no model or author analyzer."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]/'e158'
MODELS=('P','A','B'); SCENARIOS=('entity','attribute','paraphrase'); COMPONENTS=('R','S','RS','A')
def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for x in iter(lambda:f.read(1048576),b''): h.update(x)
    return h.hexdigest()
def read(p): return json.loads(Path(p).read_text())
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


def subset_stats(x,mask):
    a=np.asarray(x,dtype=float); selected=np.broadcast_to(mask,a.shape)
    count=selected.sum(-1);total=np.where(selected,a,0).sum(-1)
    mean=np.divide(total,count,out=np.full_like(total,np.nan),where=count>0)
    macro=np.where(np.all(count>0,axis=-1),np.nan_to_num(mean).mean(-1),np.nan)
    def clean(v):
        v=np.asarray(v); return np.where(np.isfinite(v),v,None).tolist()
    return {'per_relation_count':count.tolist(),'per_relation_point':clean(mean),'macro_point':clean(macro),'ci':'not computed'}



def validate_raw(a,d,patch):
    for key,want in (('source_names',MODELS),('scenario_names',SCENARIOS),('component_names',COMPONENTS)):
        if tuple(a[key])!=want: raise ValueError('wrong order '+key)
    shapes={'native_lp_selected':(3,96,38),'uncached_lp_selected':(3,96,38),'native_top_tokens':(3,96,10),'uncached_top_tokens':(3,96,10),'cache_KL':(3,96)}
    science={'positive_lp_selected':(3,3,2,24,38),'positive_top_tokens':(3,3,2,24,10),'patched_lp_selected':(3,3,4,2,24,38),'patched_top_tokens':(3,3,4,2,24,10),'patched_KL_vs_native':(3,3,4,2,24),'matched_removal_lp_selected':(3,4,2,24,38),'matched_removal_top_tokens':(3,4,2,24,10),'matched_removal_KL_vs_native':(3,4,2,24)}
    if patch: shapes.update(science)
    elif any(k in a for k in science): raise ValueError('baseline-only includes feature arrays')
    for k,shape in shapes.items():
        if k not in a or a[k].shape!=shape or (a[k].dtype.kind in 'fi' and not np.isfinite(a[k]).all()): raise ValueError('invalid array '+k)
    if patch:
        for s in range(3):
            for r in range(2):
                for c in range(24):
                    q=d['source_query_index'][s,r,c]
                    if not np.array_equal(a['positive_lp_selected'][:,s,r,c],a['native_lp_selected'][:,q]) or not np.array_equal(a['positive_top_tokens'][:,s,r,c],a['native_top_tokens'][:,q]): raise ValueError('positive residual identity')


def calculate(a,d):
    vocab={int(t):i for i,t in enumerate(d['token_union'])}; gold=d['gold_token']; target=d['target_query_index']; source=d['source_query_index']
    names=('source_rank_specificity_gain','source_control_logodds_gain','source_logprob_gain','target_logprob_change','source_hit1','source_hit10','target_hit1','KL')
    x={k:np.empty((3,3,4,2,24)) for k in names}; eligible=np.zeros((3,2,24),bool)
    for s in range(3):
        for r in range(2):
            sr=1-r if s==1 else r; alternatives=d['range_token_ids'][sr,:d['range_count'][sr]]
            for c in range(24):
                tq=int(target[r,c]); sq=int(source[s,r,c]); src=int(gold[sq]); tgt=int(gold[tq]); ctl=int(d['control_token'][s,r,c]); y,k,z=(vocab[t] for t in (src,ctl,tgt))
                distract=np.array([vocab[int(t)] for t in alternatives if int(t) not in {src,ctl,tgt}]);
                if not len(distract): raise ValueError('empty distractors')
                base=a['native_lp_selected'][:,tq,None,:]; patch=a['patched_lp_selected'][:,s,:,r,c,:]; top=a['patched_top_tokens'][:,s,:,r,c,:]
                x['source_rank_specificity_gain'][:,s,:,r,c]=(win_fraction(patch,y,distract)-win_fraction(patch,k,distract))-(win_fraction(base,y,distract)-win_fraction(base,k,distract))
                x['source_control_logodds_gain'][:,s,:,r,c]=(patch[...,y]-patch[...,k])-(base[...,y]-base[...,k])
                x['source_logprob_gain'][:,s,:,r,c]=patch[...,y]-base[...,y]; x['target_logprob_change'][:,s,:,r,c]=patch[...,z]-base[...,z]
                x['source_hit1'][:,s,:,r,c]=top[...,0]==src; x['source_hit10'][:,s,:,r,c]=(top==src).any(-1); x['target_hit1'][:,s,:,r,c]=top[...,0]==tgt; x['KL'][:,s,:,r,c]=a['patched_KL_vs_native'][:,s,:,r,c]
                eligible[s,r,c]=(a['native_top_tokens'][:,tq,0]==tgt).all() and (a['native_top_tokens'][:,sq,0]==src).all()
    target_gold=gold[target]; loc=np.array([[vocab[int(t)] for t in row] for row in target_gold])
    base=a['native_lp_selected'][:,target,:]; rem=a['matched_removal_lp_selected']
    orig=np.take_along_axis(base,loc[None,:,:,None],-1)[...,0]; changed=np.take_along_axis(rem,loc[None,None,:,:,None],-1)[...,0]
    hit=a['native_top_tokens'][:,target,0]==target_gold[None,:,:]
    removal={'target_NLL_increase':orig[:,None,:,:]-changed,'target_top1_drop':hit[:,None,:,:].astype(float)-(a['matched_removal_top_tokens'][...,0]==target_gold[None,None,:,:]),'KL':a['matched_removal_KL_vs_native']}
    return x,eligible,removal,hit.all(axis=0)


def aggregate(metrics,eligible,removal,target_success):
    out={'all':{},'contrasts':{},'common_success':{},'matched_removal':{'all':{},'contrasts':{},'common_target_success':{}}}
    for name,x in metrics.items():
        out['all'][name]=paired_country(x); out['common_success'][name]=subset_stats(x,eligible[None,:,None,:,:])
        sr=x[:,:2,1]-x[:,:2,0]; d=sr[:,0]-sr[:,1]
        changes={'A_minus_P':x[1]-x[0],'B_minus_P':x[2]-x[0],'S_minus_R_entity_attribute':sr,'S_minus_R_A_minus_P':sr[1]-sr[0],'S_minus_R_B_minus_P':sr[2]-sr[0],'entity_minus_attribute_S_minus_R':d,'entity_minus_attribute_S_minus_R_A_minus_P':d[1]-d[0],'entity_minus_attribute_S_minus_R_B_minus_P':d[2]-d[0]}
        out['contrasts'][name]={k:paired_country(v) for k,v in changes.items()}
    for name,x in removal.items():
        out['matched_removal']['all'][name]=paired_country(x); out['matched_removal']['common_target_success'][name]=subset_stats(x,target_success[None,None,:,:]); sr=x[:,1]-x[:,0]
        changes={'A_minus_P':x[1]-x[0],'B_minus_P':x[2]-x[0],'S_minus_R':sr,'S_minus_R_A_minus_P':sr[1]-sr[0],'S_minus_R_B_minus_P':sr[2]-sr[0]}
        out['matched_removal']['contrasts'][name]={k:paired_country(v) for k,v in changes.items()}
    return out

def validate_ledger(plan,ledger):
    attempts=ledger['attempts']; prior=plan['prior_failed_budget_attempts']
    if len(prior)!=2 or len(attempts)!=3 or attempts[:2]!=prior or any(x['status']!='failed' for x in prior) or attempts[2]['status']!='complete' or attempts[2]['phase']!='factual_whole_path_interchange': raise ValueError('incomplete or changed budget history')
    if ledger['limit_gpu_seconds']!=14400 or plan['limit_gpu_seconds']!=14400 or sum(x['gpu_seconds'] for x in attempts)>14400: raise ValueError('budget cap')


def audit():
    root=ROOT/'whole_path'; plan_path=root/'plan.json'; plan=read(plan_path); manifest=read(root/'manifest.json'); ledger=read(ROOT/'budget.json')
    validate_ledger(plan,ledger)
    if manifest['status']!='complete' or manifest['plan_sha256']!=digest(plan_path) or manifest['source_sha256']!=plan['source_sha256']: raise ValueError('plan/manifest source mismatch')
    mode='whole_terminal_path_fixed_native_prefix_no_KV_cache'
    if plan['execution_mode']!=mode or manifest['execution_mode']!=mode or manifest['floor_kind']!=plan['floor_kind'] or plan['source_trace_protocol_commit']!='b522db89': raise ValueError('protocol/floor mismatch')
    if plan['bootstrap']['seed']!=158001 or plan['bootstrap']['resamples']!=1000: raise ValueError('bootstrap mismatch')
    if not all(manifest['controls'].values()) or manifest['same_query_identity_cases']!=588: raise ValueError('engineering controls')
    wb=ROOT.parents[1]; models=read(wb/'results/e150/metadata.json')['models']; parent=read(wb/'results/e154/metadata.json')['model']
    for name,expected in plan['source_sha256'].items():
        if '/' in name:
            source,filename=name.split('/',1); asset=(parent if source=='parent' else models[source])['files'][filename]
            if asset['sha256']!=expected: raise ValueError('source asset record mismatch '+name)
            path=asset['path']
        else: path=wb/'scripts'/name
        if digest(path)!=expected: raise ValueError('source mismatch '+name)
    for i,name in enumerate(MODELS):
        rec=plan['source_records'][name]
        if manifest['source_parameter_hashes'][i]!=rec['parameter_hash'] or manifest['source_buffer_hashes'][i]!=rec['buffer_hash'] or digest(rec['calibration']['path'])!=rec['calibration']['sha256']: raise ValueError('canonical source mismatch '+name)
    for key in ('data','baseline_reference','component_reference','prior_full_preflight','legacy_cal_input'):
        item=plan[key]
        if digest(item['path'])!=item['sha256']: raise ValueError('input hash '+key)
    for item in plan['input_assets'].values():
        if digest(item['path'])!=item['sha256']: raise ValueError('input asset hash')
    if digest(ROOT/'data_plan.json')!=plan['data_plan_sha256']: raise ValueError('data plan hash')
    if digest(manifest['raw']['path'])!=manifest['raw']['sha256'] or digest(manifest['attention_components']['path'])!=manifest['attention_components']['sha256']: raise ValueError('raw hash')
    preflight=read(plan['prior_full_preflight']['path'])
    if preflight['attempt']!=ledger['attempts'][1] or preflight['baseline']['sha256']!=plan['baseline_reference']['sha256'] or preflight['components']['sha256']!=plan['component_reference']['sha256']: raise ValueError('prior preflight mismatch')
    if preflight['readout_floor']['full_head_to_last_only_head_KL_max']>.005 or any(x/96>.05 for x in preflight['readout_floor']['argmax_changes']): raise ValueError('inherited floor failed')
    with np.load(plan['data']['path'],allow_pickle=False) as f: d={k:f[k] for k in f.files}
    with np.load(manifest['raw']['path'],allow_pickle=False) as f: a={k:f[k] for k in f.files}
    with np.load(plan['baseline_reference']['path'],allow_pickle=False) as f: base={k:f[k] for k in f.files}
    validate_data(d)
    for key in ('native_lp_selected','uncached_lp_selected','native_top_tokens','uncached_top_tokens','cache_KL'):
        if not np.array_equal(a[key],base[key]): raise ValueError('inherited baseline differs '+key)
    gold=d['gold_token']; target=d['target_query_index']; top=a['native_top_tokens']; unc=a['uncached_top_tokens']
    hit1=top[:,:,0]==gold; hit10=(top==gold[None,:,None]).any(-1); joint=hit10[:,target].all(0).sum(-1); patch=bool((joint>=8).all())
    if manifest['patch_data_obtained']!=patch or manifest['joint_native_top10']!=joint.tolist(): raise ValueError('baseline gate mismatch')
    validate_raw(a,d,patch)
    output={'status':'recomputed' if patch else 'baseline_only','raw_sha256':manifest['raw']['sha256'],'data_sha256':plan['data']['sha256'],'execution_mode':mode,'floor_kind':plan['floor_kind'],'floor_provenance':'inherited v3 full head vs keep=1, no KV; actual comparisons', 'KL_limitation':'only full vocabulary KL scalars were saved; distribution not reconstructible', 'baseline':{'native_selected_logp_all96':a['native_lp_selected'].tolist(),'native_top_tokens_all96':top.tolist(),'uncached_top_tokens_all96':unc.tolist(),'native_top1_all96':hit1.tolist(),'native_top10_all96':hit10.tolist(),'native_top1_count_by_model':hit1.sum(-1).tolist(),'native_top10_count_by_model':hit10.sum(-1).tolist(),'canonical_top1_by_model_relation':hit1[:,target].sum(-1).tolist(),'canonical_top10_by_model_relation':hit10[:,target].sum(-1).tolist(),'common_top10_by_relation':joint.tolist(),'floor':{'cache_kl_all96':a['cache_KL'].tolist(),'cache_KL_max':float(a['cache_KL'].max()),'top1_changed_count':(top[:,:,0]!=unc[:,:,0]).sum(-1).tolist(),'selected_logp_max_abs_difference':float(np.max(np.abs(a['native_lp_selected']-a['uncached_lp_selected']))),'selected_logp_exact_mismatch_count':(a['native_lp_selected']!=a['uncached_lp_selected']).sum(axis=(1,2)).tolist()}}}
    if patch:
        metrics,eligible,removal,target_success=calculate(a,d); output.update(common_success_mask=eligible.tolist(),common_success_counts=eligible.sum(-1).tolist(),common_target_success_mask=target_success.tolist(),common_target_success_counts=target_success.sum(-1).tolist(),recomputed=aggregate(metrics,eligible,removal,target_success),positive_control_selected_LP_and_top_tokens_exact=True)
        sources=gold[d['source_query_index']]; ptop=a['positive_top_tokens']; output['positive_control']={'source_hit1':(ptop[...,0]==sources[None]).transpose(1,0,2,3).tolist(),'source_hit10':(ptop==sources[None,:,:,:,None]).any(-1).transpose(1,0,2,3).tolist()}
    return output


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



def compare_summary(result,summary,analysis_hash):
    patch=result['status']=='recomputed'
    for key,want in (('experiment','E158'),('status','complete' if patch else 'baseline_only'),('models',list(MODELS)),('scenarios',list(SCENARIOS)),('paths',list(COMPONENTS)),('execution_mode',result['execution_mode']),('seed',158001),('raw_sha256',result['raw_sha256']),('data_sha256',result['data_sha256']),('analysis_source_sha256',analysis_hash)):
        if summary.get(key)!=want: raise ValueError('summary provenance mismatch '+key)
    diffs=[];counts={'numeric_elements':0,'max_absolute_error':0.}
    base=result['baseline'].copy(); base['floor']={**base['floor'],'kind':result['floor_kind'],'legacy_cache_field_names':True,'KV_cache_used':False}
    compare_tree('baseline',base,summary.get('baseline'),diffs,counts)
    if patch:
        values=result['recomputed']
        for key in ('all','contrasts'): compare_tree(key,values[key],summary.get(key),diffs,counts)
        expected={'counts_by_scenario_relation':result['common_success_counts'],'country_mask':result['common_success_mask'],'metrics':values['common_success']}
        compare_tree('common_success',expected,summary.get('common_success'),diffs,counts)
        removal=values['matched_removal']; target={'counts_by_relation':result['common_target_success_counts'],'country_mask':result['common_target_success_mask'],'metrics':removal['common_target_success']}
        for key in ('all','contrasts'): compare_tree('matched_removal/'+key,removal[key],summary.get('matched_removal',{}).get(key),diffs,counts)
        compare_tree('matched_removal/common_target_success',target,summary.get('matched_removal',{}).get('common_target_success'),diffs,counts)
        compare_tree('positive_control',result['positive_control'],summary.get('positive_control'),diffs,counts)
    elif any(key in summary for key in ('all','contrasts','common_success','matched_removal','positive_control')): diffs.append('baseline_only contains feature summaries')
    return {'status':'passed' if not diffs else 'failed',**counts,'tolerance':1e-10,'differences':diffs}

def self_test():
    assert win_fraction(np.array([3.,2.,1.,2.]),1,[2,3])==.75
    v=np.stack([np.arange(24),np.arange(24)+10]); assert paired_country(v)['point']==16.5
    x=np.zeros((3,3,4,2,24)); x[1]=1; x[2]=3; x[:,:,1]+=2
    result=aggregate({'test':x},np.ones((3,2,24),bool),{'test':x[:,0]},np.ones((2,24),bool))
    assert result['contrasts']['test']['A_minus_P']['point']==[[1.]*4]*3
    assert result['contrasts']['test']['S_minus_R_entity_attribute']['point']==[[2.,2.]]*3
    assert result['contrasts']['test']['entity_minus_attribute_S_minus_R']['point']==[0.,0.,0.]
    assert result['matched_removal']['contrasts']['test']['S_minus_R']['point']==[2.,2.,2.]
    prior=[{'status':'failed','gpu_seconds':1},{'status':'failed','gpu_seconds':1}]; plan={'prior_failed_budget_attempts':prior,'limit_gpu_seconds':14400}; ledger={'attempts':prior+[{'status':'complete','phase':'factual_whole_path_interchange','gpu_seconds':1}],'limit_gpu_seconds':14400}; validate_ledger(plan,ledger)
    bad={**ledger,'attempts':ledger['attempts'][:-1]}
    try: validate_ledger(plan,bad)
    except ValueError: pass
    else: raise AssertionError('incomplete ledger accepted')
    values=aggregate({'test':x},np.ones((3,2,24),bool),{'test':x[:,0]},np.ones((2,24),bool))
    result={'status':'recomputed','execution_mode':'test','raw_sha256':'r','data_sha256':'d','floor_kind':'floor','baseline':{'floor':{'test':0}},'recomputed':values,'common_success_counts':[[24,24]]*3,'common_success_mask':np.ones((3,2,24),bool).tolist(),'common_target_success_counts':[24,24],'common_target_success_mask':np.ones((2,24),bool).tolist(),'positive_control':{'source_hit1':[True],'source_hit10':[True]}}
    summary={'experiment':'E158','status':'complete','models':list(MODELS),'scenarios':list(SCENARIOS),'paths':list(COMPONENTS),'execution_mode':'test','seed':158001,'raw_sha256':'r','data_sha256':'d','analysis_source_sha256':'h','baseline':{'floor':{'test':0,'kind':'floor','legacy_cache_field_names':True,'KV_cache_used':False}},'all':values['all'],'contrasts':values['contrasts'],'common_success':{'counts_by_scenario_relation':result['common_success_counts'],'country_mask':result['common_success_mask'],'metrics':values['common_success']},'matched_removal':{'all':values['matched_removal']['all'],'contrasts':values['matched_removal']['contrasts'],'common_target_success':{'counts_by_relation':result['common_target_success_counts'],'country_mask':result['common_target_success_mask'],'metrics':values['matched_removal']['common_target_success']}},'positive_control':result['positive_control']}
    assert compare_summary(result,summary,'h')['status']=='passed'
    summary=json.loads(json.dumps(summary))
    summary['common_success']['country_mask'][0][0][0]=False
    assert compare_summary(result,summary,'h')['status']=='failed'
    print('CPU self-tests and comparator corruption detection passed')


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--self-test',action='store_true'); p.add_argument('--audit',action='store_true'); p.add_argument('--output',type=Path); p.add_argument('--summary',type=Path); args=p.parse_args()
    if args.self_test: self_test()
    elif args.audit:
        if not args.output: p.error('--output required')
        result=audit()
        if args.summary:
            manifest=read(ROOT/'whole_path/manifest.json'); result['summary_comparison']=compare_summary(result,read(args.summary),manifest['source_sha256']['e158_whole_analyze.py'])
        args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n'); print(result.get('summary_comparison',{}).get('status',result['status']))
        if result.get('summary_comparison',{}).get('status')=='failed': raise SystemExit(1)
    else: p.error('choose --self-test or --audit')
