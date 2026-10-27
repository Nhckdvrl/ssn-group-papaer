"""E158 whole-terminal-path analysis, CPU NumPy only."""
import argparse, json
from pathlib import Path
import numpy as np
import e158_analyze as base

PARENT=Path(__file__).resolve().parents[1]/'results'/'e158'
ROOT=PARENT/'whole_path'
MODELS=('P','A','B'); SCENARIOS=('entity','attribute','paraphrase'); PATHS=('R','S','RS','A')


def validate_raw(a,patch):
    shapes={'source_names':(3,), 'scenario_names':(3,), 'component_names':(4,), 'native_lp_selected':(3,96,38),
      'uncached_lp_selected':(3,96,38),'native_top_tokens':(3,96,10),'uncached_top_tokens':(3,96,10),'cache_KL':(3,96)}
    extra={'patched_lp_selected':(3,3,4,2,24,38),'patched_top_tokens':(3,3,4,2,24,10),
      'patched_KL_vs_native':(3,3,4,2,24),'matched_removal_lp_selected':(3,4,2,24,38),
      'matched_removal_top_tokens':(3,4,2,24,10),'matched_removal_KL_vs_native':(3,4,2,24),
      'positive_lp_selected':(3,3,2,24,38),'positive_top_tokens':(3,3,2,24,10)}
    if patch: shapes.update(extra)
    elif any(k in a for k in extra): raise ValueError('Baseline-only raw contains feature results')
    for key,shape in shapes.items():
        if key not in a or a[key].shape!=shape: raise ValueError('Invalid raw '+key)
        if key not in ('source_names','scenario_names','component_names') and not np.isfinite(a[key]).all(): raise ValueError('Nonfinite '+key)
    if tuple(a['source_names'])!=MODELS or tuple(a['scenario_names'])!=SCENARIOS or tuple(a['component_names'])!=PATHS: raise ValueError('Incorrect axis labels')


def compute(a,d):
    idx={int(t):i for i,t in enumerate(d['token_union'])}; gold=d['gold_token']; target=d['target_query_index']; source=d['source_query_index']
    names=('source_rank_specificity_gain','source_control_logodds_gain','source_logprob_gain','target_logprob_change','source_hit1','source_hit10','target_hit1','KL')
    out={k:np.empty((3,3,4,2,24),dtype=float) for k in names}; mask=np.zeros((3,2,24),bool)
    for s in range(3):
      for r in range(2):
       rel=base.source_relation(s,r)
       for c in range(24):
        tq=int(target[r,c]); sq=int(source[s,r,c]); st=int(gold[sq]); tt=int(gold[tq]); ct=int(d['control_token'][s,r,c]); y=idx[st]; z=idx[tt]; k=idx[ct]
        distract=[idx[int(t)] for t in d['range_token_ids'][rel,:int(d['range_count'][rel])] if int(t) not in {st,tt,ct}]
        if st==ct or ct==tt or not distract: raise ValueError('Invalid control or distractors')
        n=a['native_lp_selected'][:,tq,None,:]; p=a['patched_lp_selected'][:,s,:,r,c,:]; top=a['patched_top_tokens'][:,s,:,r,c,:]
        out['source_rank_specificity_gain'][:,s,:,r,c]=(base.rank_win(p,y,distract)-base.rank_win(p,k,distract))-(base.rank_win(n,y,distract)-base.rank_win(n,k,distract))
        out['source_control_logodds_gain'][:,s,:,r,c]=(p[...,y]-p[...,k])-(n[...,y]-n[...,k])
        out['source_logprob_gain'][:,s,:,r,c]=p[...,y]-n[...,y]; out['target_logprob_change'][:,s,:,r,c]=p[...,z]-n[...,z]
        out['source_hit1'][:,s,:,r,c]=top[...,0]==st; out['source_hit10'][:,s,:,r,c]=(top==st).any(-1); out['target_hit1'][:,s,:,r,c]=top[...,0]==tt
        out['KL'][:,s,:,r,c]=a['patched_KL_vs_native'][:,s,:,r,c]
        mask[s,r,c]=base.common_success(a['native_top_tokens'],gold,tq,sq)
    return out,mask


def removal(a,d):
    target=d['target_query_index']; gold=d['gold_token'][target]; idx={int(t):i for i,t in enumerate(d['token_union'])}
    loc=np.array([[idx[int(t)] for t in row] for row in gold]); native=a['native_lp_selected'][:,target,:]
    original=np.take_along_axis(native,loc[None,:,:,None],axis=-1)[...,0]
    changed=np.take_along_axis(a['matched_removal_lp_selected'],loc[None,None,:,:,None],axis=-1)[...,0]
    hit=a['native_top_tokens'][:,target,0]==gold[None,:,:]
    return {'target_NLL_increase':original[:,None]-changed,
            'target_top1_drop':hit[:,None].astype(float)-(a['matched_removal_top_tokens'][...,0]==gold[None,None,:,:]),
            'KL':a['matched_removal_KL_vs_native'].astype(float)},hit.all(axis=0)


def calculate(a,d,patch,floor_kind):
    base.validate_data(d); validate_raw(a,patch); baseline=base.baseline(a,d)
    baseline['floor'].update(kind=floor_kind,legacy_cache_field_names=True,KV_cache_used=False)
    result={'experiment':'E158','status':'complete' if patch else 'baseline_only', 'models':list(MODELS), 'scenarios':list(SCENARIOS), 'paths':list(PATHS),
      'execution_mode':'whole_terminal_path_fixed_native_prefix_no_KV_cache','seed':158001,
      'bootstrap':'1000 paired country draws shared across relations and conditions; equal relation macro, input CI only', 'baseline':baseline}
    if not patch: return result
    if min(baseline['common_top10_by_relation'])<8: raise ValueError('Patch results violate baseline top10 gate')
    for s in range(3):
      for r in range(2):
       for c in range(24):
        q=int(d['source_query_index'][s,r,c])
        if not np.array_equal(a['positive_lp_selected'][:,s,r,c],a['native_lp_selected'][:,q]) or not np.array_equal(a['positive_top_tokens'][:,s,r,c],a['native_top_tokens'][:,q]): raise ValueError('Positive control differs from actual source query')
    m,mask=compute(a,d); draws=base.make_draws(); summary=lambda x:base.summarize(x,draws)
    result['all']={}; result['contrasts']={}; result['common_success']={'selection':'all models native target and actual source query top1','counts_by_scenario_relation':mask.sum(-1).tolist(),'country_mask':mask.tolist(),'ci':'not computed','metrics':{}}
    for k,x in m.items():
        result['all'][k]=summary(x); result['common_success']['metrics'][k]=base.conditional(x,mask[None,:,None,:,:])
        sr=x[:,:2,1]-x[:,:2,0]; feature=sr[:,0]-sr[:,1]
        result['contrasts'][k]={'A_minus_P':summary(x[1]-x[0]),'B_minus_P':summary(x[2]-x[0]),
          'S_minus_R_entity_attribute':summary(sr),'S_minus_R_A_minus_P':summary(sr[1]-sr[0]),'S_minus_R_B_minus_P':summary(sr[2]-sr[0]),
          'entity_minus_attribute_S_minus_R':summary(feature),'entity_minus_attribute_S_minus_R_A_minus_P':summary(feature[1]-feature[0]),'entity_minus_attribute_S_minus_R_B_minus_P':summary(feature[2]-feature[0])}
    rm,success=removal(a,d); dest={'definition':'whole-path zeroing; NLL increase and top1 drop are native minus removal, not knowledge fractions','all':{},'contrasts':{},
      'common_target_success':{'counts_by_relation':success.sum(-1).tolist(),'country_mask':success.tolist(),'ci':'not computed','metrics':{}}}
    for k,x in rm.items():
        sr=x[:,1]-x[:,0]; dest['all'][k]=summary(x); dest['common_target_success']['metrics'][k]=base.conditional(x,success[None,None,:,:])
        dest['contrasts'][k]={'A_minus_P':summary(x[1]-x[0]),'B_minus_P':summary(x[2]-x[0]),'S_minus_R':summary(sr),
          'S_minus_R_A_minus_P':summary(sr[1]-sr[0]),'S_minus_R_B_minus_P':summary(sr[2]-sr[0])}
    result['matched_removal']=dest
    result['positive_control']={'description':'final residual source replacement; operator control','source_hit1':[],'source_hit10':[]}
    for s in range(3):
        token=d['gold_token'][d['source_query_index'][s]]; top=a['positive_top_tokens'][:,s]
        result['positive_control']['source_hit1'].append((top[...,0]==token).tolist());result['positive_control']['source_hit10'].append((top==token[None,:,:,None]).any(-1).tolist())
    return result


def analyze():
    plan_path=ROOT/'plan.json'; plan=json.loads(plan_path.read_text()); manifest=json.loads((ROOT/'manifest.json').read_text()); ledger=json.loads((PARENT/'budget.json').read_text())
    if manifest.get('status')!='complete' or manifest.get('plan_sha256')!=base.sha(plan_path): raise ValueError('Incomplete or mismatched plan')
    if manifest.get('source_sha256')!=plan.get('source_sha256') or plan['source_sha256'].get('e158_whole_analyze.py')!=base.sha(__file__): raise ValueError('Source mismatch')
    if manifest.get('execution_mode')!='whole_terminal_path_fixed_native_prefix_no_KV_cache' or manifest.get('floor_kind')!=plan.get('floor_kind'): raise ValueError('Execution/floor metadata mismatch')
    attempts=ledger.get('attempts',[]); prior=plan.get('prior_failed_budget_attempts')
    if not isinstance(prior,list) or len(prior)!=2 or len(attempts)!=3 or attempts[:2]!=prior or any(x.get('status')!='failed' for x in prior) or attempts[2].get('status')!='complete' or attempts[2].get('phase')!='factual_whole_path_interchange': raise ValueError('Invalid cumulative attempts')
    if any(not np.isfinite(x.get('gpu_seconds',float('nan'))) or x['gpu_seconds']<0 for x in attempts) or sum(x['gpu_seconds'] for x in attempts)>14400: raise ValueError('GPU budget exceeded or invalid')
    if base.sha(PARENT/'data_plan.json')!=plan['data_plan_sha256']: raise ValueError('Data plan mismatch')
    dp=json.loads((PARENT/'data_plan.json').read_text())
    for name in ('data','baseline_reference','component_reference','prior_full_preflight'):
        v=plan[name]
        if base.sha(v['path'])!=v['sha256']: raise ValueError('Reference mismatch '+name)
    if plan['data']['sha256']!=dp['assets']['data.npz']['sha256']: raise ValueError('Data plan asset mismatch')
    raw=manifest['raw']
    if base.sha(raw['path'])!=raw['sha256']: raise ValueError('Raw SHA mismatch')
    patch=manifest.get('patch_data_obtained')
    if not isinstance(patch,bool): raise ValueError('Missing patch status')
    with np.load(plan['data']['path'],allow_pickle=False) as f: d={k:f[k] for k in f.files}
    with np.load(raw['path'],allow_pickle=False) as f: a={k:f[k] for k in f.files}
    with np.load(plan['baseline_reference']['path'],allow_pickle=False) as ref:
        for k in ('native_lp_selected','uncached_lp_selected','native_top_tokens','uncached_top_tokens','cache_KL'):
            if not np.array_equal(a[k],ref[k]): raise ValueError('Inherited baseline differs: '+k)
    result=calculate(a,d,patch,plan['floor_kind']);result.update(raw_sha256=raw['sha256'],data_sha256=plan['data']['sha256'],analysis_source_sha256=base.sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return {'status':result['status'],'summary':str(ROOT/'summary.json')}


def self_test():
    assert base.rank_win(np.array([3.,2.,1.,2.]),1,[2,3])==.75
    assert base.common_success(np.zeros((3,2,10),dtype=int),np.array([0,0]),0,1)
    t=np.zeros((3,2,10),dtype=int);t[2,1,0]=1
    assert not base.common_success(t,np.array([0,0]),0,1)
    x=np.zeros((3,3,4,2,24));x[:,:,0]=1;x[:,:,1]=2;x[:,:,2]=3;x[:,:,3]=4
    z=base.summarize(x,base.make_draws()); assert np.array(z['point']).shape==(3,3,4) and z['point'][2][1]==[1,2,3,4]
    d={'target_query_index':np.array([np.arange(24),np.arange(48,72)]),'gold_token':np.zeros(96,dtype=int),'token_union':np.arange(38)}
    a={'native_lp_selected':np.zeros((3,96,38)),'native_top_tokens':np.zeros((3,96,10),dtype=int),
       'matched_removal_lp_selected':np.zeros((3,4,2,24,38)),'matched_removal_top_tokens':np.zeros((3,4,2,24,10),dtype=int),
       'matched_removal_KL_vs_native':np.zeros((3,4,2,24))}
    rm,mask=removal(a,d); assert mask.all() and all(np.all(v==0) for v in rm.values()) and rm['target_NLL_increase'].shape==(3,4,2,24)
    d.update(source_query_index=np.broadcast_to(d['target_query_index'],(3,2,24)).copy(),control_token=np.ones((3,2,24),dtype=int),range_token_ids=np.broadcast_to(np.arange(24),(2,24)),range_count=np.array([24,24]))
    a.update(patched_lp_selected=np.zeros((3,3,4,2,24,38)),patched_top_tokens=np.zeros((3,3,4,2,24,10),dtype=int),patched_KL_vs_native=np.zeros((3,3,4,2,24)))
    metrics,eligible=compute(a,d); assert eligible.all()
    for key in ('source_rank_specificity_gain','source_control_logodds_gain','source_logprob_gain','target_logprob_change','KL'):
        assert metrics[key].shape==(3,3,4,2,24) and np.all(metrics[key]==0)
    assert np.allclose(np.array(base.summarize(np.ones((2,24)),base.make_draws())['ci95']),[1,1])
    return {'status':'passed','CPU_only':True,'checks':['rank ties','actual source eligibility','four-path axes','identity patch and removal','paired bootstrap']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--analyze',action='store_true');a=p.parse_args()
    if a.self_test==a.analyze:p.error('Choose exactly one of --self-test or --analyze')
    print(json.dumps(self_test() if a.self_test else analyze(),indent=2,ensure_ascii=False))
