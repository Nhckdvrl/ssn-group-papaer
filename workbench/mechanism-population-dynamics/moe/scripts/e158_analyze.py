"""E158 factual path interchange statistics; NumPy only."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results'/'e158'
SCENARIOS=('entity','attribute','paraphrase'); PATHS=('R','S','RS'); MODELS=('P','A','B')

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def rank_win(lp,y,distractors):
    """Selected full-vocabulary log probabilities; no subset renormalization."""
    d=np.asarray(distractors,dtype=int)
    if not len(d): raise ValueError('Empty distractors')
    return ((lp[...,y,None]>lp[...,d])+.5*(lp[...,y,None]==lp[...,d])).mean(axis=-1)

def source_relation(scenario, target_relation):
    return 1-target_relation if scenario==1 else target_relation

def make_draws(n=24):
    return np.random.default_rng(158001).integers(0,n,(1000,n))

def summarize(x,draws):
    """Last axes relation,country. Identical country draws for both relations."""
    x=np.asarray(x,dtype=float)
    if x.shape[-2:]!=(2,24): raise ValueError('Expected relation x country')
    b=np.take(x,draws,axis=-1).mean(-1)
    point=x.mean(-1); macro=point.mean(-1); boot=b.mean(-2)
    return {'point':macro.tolist(),'ci95':np.moveaxis(np.quantile(boot,[.025,.975],axis=-1),0,-1).tolist(),
            'per_relation_point':point.tolist(),'per_relation_ci95':np.moveaxis(np.quantile(b,[.025,.975],axis=-1),0,-1).tolist()}

def conditional(x,mask):
    """No CI: fixed scenario-specific eligibility, preserve zero-count information."""
    x=np.asarray(x,dtype=float); mask=np.broadcast_to(mask,x.shape)
    count=mask.sum(-1); total=np.where(mask,x,0).sum(-1)
    val=np.divide(total,count,out=np.full_like(total,np.nan),where=count>0)
    valid=np.all(count>0,axis=-1)
    macro=np.where(valid,np.nan_to_num(val).mean(-1),np.nan)
    return {'per_relation_count':count.tolist(),'per_relation_point':clean(val),'macro_point':clean(macro),'ci':'not computed'}

def clean(x):
    a=np.asarray(x); return np.where(np.isfinite(a),a,None).tolist()

def validate_data(d):
    shapes={'gold_token':(96,),'relation':(96,),'country':(96,),'template':(96,), 'target_query_index':(2,24),
            'source_query_index':(3,2,24),'control_token':(3,2,24),'range_token_ids':(2,24),'range_count':(2,),'token_union':(38,)}
    for k,sh in shapes.items():
        if k not in d or d[k].shape!=sh:raise ValueError(f'Invalid data {k}')
    if len(np.unique(d['token_union']))!=38 or not np.array_equal(d['target_query_index'],np.array([np.arange(24),np.arange(48,72)])):raise ValueError('Token union / target query mapping')
    for s in range(3):
        for r in range(2):
            for c in range(24):
                q=int(d['source_query_index'][s,r,c]); t=int(d['target_query_index'][r,c]); rel=source_relation(s,r)
                if q<0 or q>=96 or d['relation'][q]!=rel or d['relation'][t]!=r:raise ValueError('Source relation mapping')
                if s==0 and d['country'][q]!=(c+11)%24:raise ValueError('Entity country mapping')
                if s in (1,2) and d['country'][q]!=c:raise ValueError('Source country mapping')
                if s==2 and d['template'][q]==d['template'][t]:raise ValueError('Paraphrase must change template')
                if any(int(z) not in d['token_union'] for z in (d['gold_token'][q],d['gold_token'][t],d['control_token'][s,r,c])):raise ValueError('Token missing from union')

def validate_raw(a,patch):
    shapes={'source_names':(3,),'scenario_names':(3,),'component_names':(3,), 'native_lp_selected':(3,96,38),'uncached_lp_selected':(3,96,38),'native_top_tokens':(3,96,10),'uncached_top_tokens':(3,96,10),'cache_KL':(3,96)}
    if patch:shapes.update({'patched_lp_selected':(3,3,3,16,2,24,38),'patched_top_tokens':(3,3,3,16,2,24,10),'patched_KL_vs_native':(3,3,3,16,2,24),'positive_lp_selected':(3,3,2,24,38),'positive_top_tokens':(3,3,2,24,10), 'matched_removal_lp_selected':(3,3,16,2,24,38), 'matched_removal_top_tokens':(3,3,16,2,24,10), 'matched_removal_KL_vs_native':(3,3,16,2,24)})
    for k,shape in shapes.items():
        if k not in a or a[k].shape!=shape:raise ValueError(f'Invalid raw {k}')
        if k not in ('source_names','scenario_names','component_names') and not np.isfinite(a[k]).all():raise ValueError(f'Nonfinite {k}')
    if tuple(a['source_names'])!=MODELS or tuple(a['scenario_names'])!=SCENARIOS or tuple(a['component_names'])!=PATHS:raise ValueError('Raw source/scenario/path order mismatch')

def baseline(a,d):
    gold=d['gold_token']; nt=a['native_top_tokens']; ut=a['uncached_top_tokens']; q=d['target_query_index']; hits=(nt[:,:,0]==gold); top10=(nt==gold[None,:,None]).any(-1)
    return {'native_selected_logp_all96':a['native_lp_selected'].tolist(),'native_top_tokens_all96':nt.tolist(),'uncached_top_tokens_all96':ut.tolist(),'native_top1_all96':hits.tolist(),'native_top10_all96':top10.tolist(),
        'native_top1_count_by_model':hits.sum(-1).tolist(),'native_top10_count_by_model':top10.sum(-1).tolist(),
        'canonical_top1_by_model_relation':hits[:,q].sum(-1).tolist(),'canonical_top10_by_model_relation':top10[:,q].sum(-1).tolist(),
        'common_top10_by_relation':top10[:,q].all(axis=0).sum(-1).tolist(),
        'floor':{'cache_kl_all96':a['cache_KL'].tolist(),'cache_KL_max':float(a['cache_KL'].max()),
          'top1_changed_count':(nt[:,:,0]!=ut[:,:,0]).sum(-1).tolist(),
          'selected_logp_max_abs_difference':float(np.max(np.abs(a['native_lp_selected']-a['uncached_lp_selected']))),
          'selected_logp_exact_mismatch_count':(a['native_lp_selected']!=a['uncached_lp_selected']).sum(axis=(1,2)).tolist()}}

def common_success(native_top, gold, target_query, source_query):
    return bool(np.all(native_top[:,target_query,0]==gold[target_query]) and np.all(native_top[:,source_query,0]==gold[source_query]))

def compute(a,d):
    validate_data(d); validate_raw(a,True); idx={int(t):i for i,t in enumerate(d['token_union'])}; gold=d['gold_token']; target=d['target_query_index']; source=d['source_query_index']; controls=d['control_token']; native=a['native_lp_selected']; patched=a['patched_lp_selected']; top=a['patched_top_tokens']; names=('source_rank_specificity_gain','source_control_logodds_gain','source_logprob_gain','target_logprob_change','source_hit1','source_hit10','target_hit1','KL')
    shape=(3,3,3,16,2,24); out={k:np.empty(shape,dtype=float) for k in names}; mask=np.zeros((3,2,24),bool)
    for s in range(3):
      for r in range(2):
       source_rel=source_relation(s,r)
       for c in range(24):
        tq=int(target[r,c]); sq=int(source[s,r,c]); st=int(gold[sq]); ct=int(controls[s,r,c]); tt=int(gold[tq]); y=idx[st]; ctrl=idx[ct]; tar=idx[tt]
        ran=[int(z) for z in d['range_token_ids'][source_rel,:int(d['range_count'][source_rel])]]
        distract=[idx[z] for z in ran if z not in {st,ct,tt}]
        if st==ct or ct==tt or not distract:raise ValueError('Invalid control or distractors')
        n=native[:,tq,:]; p=patched[:,s,:,:,r,c,:]; n=n[:,None,None,:]
        out['source_rank_specificity_gain'][:,s,:,:,r,c]=(rank_win(p,y,distract)-rank_win(p,ctrl,distract))-(rank_win(n,y,distract)-rank_win(n,ctrl,distract))
        out['source_control_logodds_gain'][:,s,:,:,r,c]=(p[...,y]-p[...,ctrl])-(n[...,y]-n[...,ctrl])
        out['source_logprob_gain'][:,s,:,:,r,c]=p[...,y]-n[...,y];out['target_logprob_change'][:,s,:,:,r,c]=p[...,tar]-n[...,tar]
        topcur=top[:,s,:,:,r,c,:];out['source_hit1'][:,s,:,:,r,c]=topcur[...,0]==st;out['source_hit10'][:,s,:,:,r,c]=(topcur==st).any(-1);out['target_hit1'][:,s,:,:,r,c]=topcur[...,0]==tt
        out['KL'][:,s,:,:,r,c]=a['patched_KL_vs_native'][:,s,:,:,r,c]
        mask[s,r,c]=common_success(a['native_top_tokens'],gold,tq,sq)
    return out,mask

def removal_metrics(a,d):
    target=d['target_query_index']; gold=d['gold_token'][target]; mapping={int(t):i for i,t in enumerate(d['token_union'])}
    indices=np.array([[mapping[int(t)] for t in row] for row in gold])
    native=a['native_lp_selected'][:,target,:]; removed=a['matched_removal_lp_selected']
    native_gold=np.take_along_axis(native,indices[None,:,:,None],axis=-1)[...,0]
    removed_gold=np.take_along_axis(removed,indices[None,None,None,:,:,None],axis=-1)[...,0]
    native_hit=a['native_top_tokens'][:,target,0]==gold[None,:,:]
    removed_hit=a['matched_removal_top_tokens'][...,0]==gold[None,None,None,:,:]
    values={'target_NLL_increase':native_gold[:,None,None,:,:]-removed_gold,
            'target_top1_drop':native_hit[:,None,None,:,:].astype(float)-removed_hit.astype(float),
            'KL':a['matched_removal_KL_vs_native'].astype(float)}
    return values,native_hit.all(axis=0)

def analyze():
    plan=json.loads((ROOT/'plan.json').read_text()); manifest=json.loads((ROOT/'manifest.json').read_text());data_plan=json.loads((ROOT/'data_plan.json').read_text());budget=json.loads((ROOT/'budget.json').read_text())
    if manifest.get('status')!='complete' or manifest.get('plan_sha256')!=sha(ROOT/'plan.json'):raise ValueError('Incomplete manifest or plan mismatch')
    if not budget.get('attempts') or any(x.get('status')!='complete' for x in budget['attempts']):raise ValueError('Complete budget attempts required')
    if manifest.get('source_sha256',{}).get('e158_analyze.py')!=sha(__file__):raise ValueError('Analysis source hash mismatch')
    if plan.get('data_plan_sha256')!=sha(ROOT/'data_plan.json'):raise ValueError('Data plan mismatch')
    raw=Path(manifest['raw']['path']); data=Path(plan['data']['path'])
    if sha(raw)!=manifest['raw']['sha256'] or sha(data)!=plan['data']['sha256'] or sha(data)!=data_plan['assets']['data.npz']['sha256']:raise ValueError('Raw/data hash mismatch')
    with np.load(data,allow_pickle=False) as f:d={k:f[k].copy() for k in f.files}
    with np.load(raw,allow_pickle=False) as f:a={k:f[k].copy() for k in f.files}
    validate_data(d); patch=manifest.get('patch_data_obtained')
    if not isinstance(patch,bool):raise ValueError('Missing explicit patch_data_obtained')
    validate_raw(a,patch)
    result={'experiment':'E158','status':'complete' if patch else 'baseline_only','raw_sha256':manifest['raw']['sha256'],'data_sha256':plan['data']['sha256'],'analysis_source_sha256':sha(__file__),'models':list(MODELS),'scenarios':list(SCENARIOS),'paths':list(PATHS),'seed':158001,'bootstrap':'1000 paired country draws shared across relations and conditions; equal relation macro, input CI only','baseline':baseline(a,d)}
    if patch:
        if min(result['baseline']['common_top10_by_relation']) < 8:raise ValueError('Patch results violate preregistered common top10 gate')
        for scenario in range(3):
            for r in range(2):
                for c in range(24):
                    sq=int(d['source_query_index'][scenario,r,c])
                    if not np.array_equal(a['positive_lp_selected'][:,scenario,r,c],a['native_lp_selected'][:,sq]):
                        raise ValueError('Final residual positive control differs from actual source native selected log probabilities')
        m,mask=compute(a,d); draws=make_draws(); result['common_success']={'selection':'all P/A/B native canonical target and actual source query top1; independent of patch output','counts_by_scenario_relation':mask.sum(-1).tolist(),'country_mask':mask.tolist(),'ci':'not computed'}
        result['all']={};result['common_success']['metrics']={};result['layer_mean']={};result['contrasts']={}
        for k,x in m.items():
            result['all'][k]=summarize(x,draws)
            result['common_success']['metrics'][k]=conditional(x,mask[None,:,None,None,:,:])
            layer=x.mean(axis=3); result['layer_mean'][k]=summarize(layer,draws)
            result['contrasts'][k]={'A_minus_P':summarize(x[1]-x[0],draws),'B_minus_P':summarize(x[2]-x[0],draws),
                'layer_mean_A_minus_P':summarize(layer[1]-layer[0],draws),'layer_mean_B_minus_P':summarize(layer[2]-layer[0],draws)}
            # Entity/attribute S minus R and changes in that path contrast by history.
            sr=x[:,:2,1]-x[:,:2,0]
            result['contrasts'][k].update({'S_minus_R_entity_attribute':summarize(sr,draws),'S_minus_R_A_minus_P':summarize(sr[1]-sr[0],draws),'S_minus_R_B_minus_P':summarize(sr[2]-sr[0],draws), 'layer_mean_S_minus_R_entity_attribute':summarize(sr.mean(axis=2),draws), 'layer_mean_S_minus_R_A_minus_P':summarize((sr[1]-sr[0]).mean(axis=1),draws), 'layer_mean_S_minus_R_B_minus_P':summarize((sr[2]-sr[0]).mean(axis=1),draws)})
            feature=sr[:,0]-sr[:,1]
            result['contrasts'][k].update({'entity_minus_attribute_S_minus_R':summarize(feature,draws),
                'entity_minus_attribute_S_minus_R_A_minus_P':summarize(feature[1]-feature[0],draws),
                'entity_minus_attribute_S_minus_R_B_minus_P':summarize(feature[2]-feature[0],draws),
                'layer_mean_entity_minus_attribute_S_minus_R':summarize(feature.mean(axis=1),draws),
                'layer_mean_entity_minus_attribute_S_minus_R_A_minus_P':summarize((feature[1]-feature[0]).mean(axis=0),draws),
                'layer_mean_entity_minus_attribute_S_minus_R_B_minus_P':summarize((feature[2]-feature[0]).mean(axis=0),draws)})
        removal,target_mask=removal_metrics(a,d)
        result['matched_removal']={'definition':'same canonical target and last position; target NLL increase = native logp minus removed logp; top1 drop = native correct minus removed correct; not a knowledge fraction',
            'all':{},'layer_mean':{},'contrasts':{},'common_target_success':{'selection':'all P/A/B native canonical target top1 correct; independent of source and removal','counts_by_relation':target_mask.sum(-1).tolist(),'country_mask':target_mask.tolist(),'ci':'not computed','metrics':{}}}
        rem=result['matched_removal']
        for k,x in removal.items():
            rem['all'][k]=summarize(x,draws); rem['layer_mean'][k]=summarize(x.mean(axis=2),draws)
            rem['common_target_success']['metrics'][k]=conditional(x,target_mask[None,None,None,:,:])
            sr=x[:,1]-x[:,0]
            rem['contrasts'][k]={'A_minus_P':summarize(x[1]-x[0],draws),'B_minus_P':summarize(x[2]-x[0],draws),
                'layer_mean_A_minus_P':summarize((x[1]-x[0]).mean(axis=1),draws),'layer_mean_B_minus_P':summarize((x[2]-x[0]).mean(axis=1),draws),
                'S_minus_R':summarize(sr,draws),'S_minus_R_A_minus_P':summarize(sr[1]-sr[0],draws),'S_minus_R_B_minus_P':summarize(sr[2]-sr[0],draws),
                'layer_mean_S_minus_R':summarize(sr.mean(axis=1),draws),'layer_mean_S_minus_R_A_minus_P':summarize((sr[1]-sr[0]).mean(axis=0),draws),'layer_mean_S_minus_R_B_minus_P':summarize((sr[2]-sr[0]).mean(axis=0),draws)}
        result['positive_control']={'source_hit1':[], 'source_hit10':[],'description':'final residual source replacement; operator control, not a new mechanism'}
        for s in range(3):
            st=d['gold_token'][d['source_query_index'][s]]; top=a['positive_top_tokens'][:,s]
            result['positive_control']['source_hit1'].append((top[...,0]==st).tolist());result['positive_control']['source_hit10'].append((top==st[None,:,:,None]).any(-1).tolist())
    (ROOT/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False,ensure_ascii=False)+'\n')
    return ROOT/'summary.json'

def self_test():
    lp=np.array([3.,2.,1.,2.]); assert rank_win(lp,0,[2,3])==1 and rank_win(lp,1,[2,3])==.75
    assert rank_win(lp,1,[2,3])==rank_win(lp*7,1,[2,3])
    draws=make_draws(); x=np.stack([np.arange(24),np.arange(24)+10]);z=summarize(x,draws)
    assert z['point']==16.5 and np.allclose(z['per_relation_point'],[11.5,21.5])
    assert np.allclose(np.take(x[1],draws).mean(-1)-np.take(x[0],draws).mean(-1),10)
    sub=np.array([[r*48+c for c in range(24)] for r in range(2)]); assert sub[1,3]==51 and [source_relation(s,0) for s in range(3)]==[0,1,0] and [source_relation(s,1) for s in range(3)]==[1,0,1]
    test_top=np.zeros((3,2,10),dtype=int); test_gold=np.array([0,0]); test_top[1,1,0]=1
    assert common_success(test_top,test_gold,0,0) and not common_success(test_top,test_gold,0,1)
    data_plan=json.loads((ROOT/'data_plan.json').read_text()); data_path=Path(data_plan['assets']['data.npz']['path'])
    if sha(data_path)!=data_plan['assets']['data.npz']['sha256']:raise ValueError('Self-test data hash mismatch')
    with np.load(data_path,allow_pickle=False) as f:d={k:f[k].copy() for k in f.files}
    native=np.broadcast_to(-np.arange(38,dtype=float),(3,96,38)).copy(); tq=d['target_query_index']
    synthetic={'source_names':np.array(MODELS),'scenario_names':np.array(SCENARIOS),'component_names':np.array(PATHS),
        'native_lp_selected':native,'uncached_lp_selected':native.copy(),'native_top_tokens':np.broadcast_to(d['gold_token'][None,:,None],(3,96,10)).copy(),
        'uncached_top_tokens':np.broadcast_to(d['gold_token'][None,:,None],(3,96,10)).copy(),'cache_KL':np.zeros((3,96)),
        'patched_lp_selected':np.broadcast_to(native[:,None,None,None,tq,:],(3,3,3,16,2,24,38)).copy(),
        'patched_top_tokens':np.broadcast_to(d['gold_token'][tq][None,None,None,None,:,:,None],(3,3,3,16,2,24,10)).copy(),
        'patched_KL_vs_native':np.zeros((3,3,3,16,2,24)), 'positive_lp_selected':np.zeros((3,3,2,24,38)),
        'positive_top_tokens':np.zeros((3,3,2,24,10),dtype=int),
        'matched_removal_lp_selected':np.broadcast_to(native[:,None,None,tq,:],(3,3,16,2,24,38)).copy(),
        'matched_removal_top_tokens':np.broadcast_to(d['gold_token'][tq][None,None,None,:,:,None],(3,3,16,2,24,10)).copy(),
        'matched_removal_KL_vs_native':np.zeros((3,3,16,2,24))}
    # Paraphrase source differs from target query: change one model's source prediction only.
    source_q=int(d['source_query_index'][2,0,0]);synthetic['native_top_tokens'][0,source_q,0]=-1
    measured,eligible=compute(synthetic,d)
    for key in ('source_rank_specificity_gain','source_control_logodds_gain','source_logprob_gain','target_logprob_change'):
        assert np.all(measured[key]==0),key
    assert not eligible[2,0,0] and eligible[1,0,0]
    rem,target_success=removal_metrics(synthetic,d)
    assert target_success.all() and all(np.all(v==0) for v in rem.values())
    return {'status':'passed','checks':['identity_patch_end_to_end','identity_matched_removal','actual_source_query_top1','rank_tie_and_temperature','known_source_control','source_query_relation_mapping','shared_country_bootstrap']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('self-test','analyze'));args=p.parse_args()
    print(json.dumps(self_test()) if args.mode=='self-test' else analyze())
