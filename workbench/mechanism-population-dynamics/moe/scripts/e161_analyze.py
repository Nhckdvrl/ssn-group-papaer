"""CPU statistics for E161 simultaneous entity and relation interchange."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results'/'e161'
MODELS=('P','A','B'); PATHS=('R','S','RS','A')
OUTCOMES=('original','entity_hybrid','relation_hybrid','full_donor','other')
SEED=161001


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def stats(x):
    x=np.asarray(x,dtype=float)
    if x.shape[-2:]!=(2,24):raise ValueError('Expected relation × country')
    draw=np.random.default_rng(SEED).integers(0,24,(1000,24)); boot=np.take(x,draw,axis=-1).mean(-1);point=x.mean(-1)
    return {'point':point.mean(-1).tolist(),'ci95':np.moveaxis(np.quantile(boot.mean(-2),[.025,.975],axis=-1),0,-1).tolist(),
            'per_relation_point':point.tolist(),'per_relation_ci95':np.moveaxis(np.quantile(boot,[.025,.975],axis=-1),0,-1).tolist()}


def conditional(x,mask):
    x=np.asarray(x,dtype=float);mask=np.broadcast_to(mask,x.shape);count=mask.sum(-1);value=np.divide(np.where(mask,x,0).sum(-1),count,out=np.full(count.shape,np.nan),where=count>0)
    macro=np.where((count>0).all(-1),np.nan_to_num(value).mean(-1),np.nan)
    clean=lambda a:np.where(np.isfinite(a),a,None).tolist()
    return {'per_relation_count':count.tolist(),'per_relation_point':clean(value),'macro_point':clean(macro),'ci':'not computed'}


def validate_map(d,m):
    required={'outcome_query_indices':(4,2,24),'outcome_token_ids':(4,2,24),'source_query_index_both':(2,24),'token_union':(38,),'target_query_index':(2,24)}
    for k,shape in required.items():
        if k not in m or m[k].shape!=shape:raise ValueError('Invalid mapping '+k)
    target=d['target_query_index'];q=m['outcome_query_indices'];c=(np.arange(24)+11)%24
    expected=np.stack([target,target[:,c],target[::-1],target[::-1][:,c]])
    if not np.array_equal(q,expected) or not np.array_equal(m['source_query_index_both'],expected[3]) or not np.array_equal(m['target_query_index'],target):raise ValueError('Query map differs')
    if not np.array_equal(m['outcome_token_ids'],d['gold_token'][q]) or not np.array_equal(m['token_union'],d['token_union']):raise ValueError('Outcome token mapping differs')
    if np.any(np.diff(np.sort(m['outcome_token_ids'],axis=0),axis=0)==0):raise ValueError('Four outcome tokens must be distinct')


def validate_raw(a):
    shapes={'native_lp_selected':(3,96,38),'native_top_tokens':(3,96,10),'patched_lp_selected':(3,4,2,24,38),
      'patched_top_tokens':(3,4,2,24,10),'patched_KL_vs_native':(3,4,2,24),'positive_lp_selected':(3,2,24,38),
      'positive_top_tokens':(3,2,24,10),'source_names':(3,),'component_names':(4,)}
    for k,shape in shapes.items():
        if k not in a or a[k].shape!=shape:raise ValueError('Invalid raw '+k)
        if k not in ('source_names','component_names') and not np.isfinite(a[k]).all():raise ValueError('Nonfinite '+k)
    if tuple(a['source_names'])!=MODELS or tuple(a['component_names'])!=PATHS:raise ValueError('Incorrect source/path order')


def compute(a,m):
    gold=m['outcome_token_ids']; q=m['outcome_query_indices'];target=q[0];tokens=m['token_union'];idx={int(t):i for i,t in enumerate(tokens)}
    top=a['patched_top_tokens'][...,0];base=a['native_top_tokens'][:,target,0];metrics={}
    bins=[]
    for i,name in enumerate(OUTCOMES[:4]):
        hit=top==gold[i][None,None,:,:];native=base==gold[i][None,:,:];bins.append(hit)
        metrics['top1_'+name]=hit.astype(float);metrics['top1_change_'+name]=hit.astype(float)-native[:,None].astype(float)
        loc=np.array([[idx[int(t)] for t in row] for row in gold[i]])
        p=np.take_along_axis(a['patched_lp_selected'],loc[None,None,:,:,None],axis=-1)[...,0]
        n=np.take_along_axis(a['native_lp_selected'][:,target,:],loc[None,:,:,None],axis=-1)[...,0]
        metrics['logprob_gain_'+name]=p-n[:,None]
    other=~np.any(np.stack(bins),axis=0);native_other=~np.any(np.stack([base==gold[i][None,:,:] for i in range(4)]),axis=0)
    metrics['top1_other']=other.astype(float);metrics['top1_change_other']=other.astype(float)-native_other[:,None].astype(float)
    metrics['KL']=a['patched_KL_vs_native'].astype(float)
    if not np.all(sum(metrics['top1_'+name] for name in OUTCOMES)==1):raise ValueError('Outcome categories are not exclusive/exhaustive')
    mask=np.ones((2,24),bool)
    for i in range(4):mask &= (a['native_top_tokens'][:,q[i],0]==gold[i][None,:,:]).all(axis=0)
    return metrics,mask


def summarize(a,d,m):
    validate_map(d,m);validate_raw(a)
    for r in range(2):
        for c in range(24):
            q=int(m['source_query_index_both'][r,c])
            if not np.array_equal(a['positive_lp_selected'][:,r,c],a['native_lp_selected'][:,q]) or not np.array_equal(a['positive_top_tokens'][:,r,c],a['native_top_tokens'][:,q]):raise ValueError('Source residual positive control mismatch')
    metrics,mask=compute(a,m)
    result={'experiment':'E161','status':'complete','models':list(MODELS),'paths':list(PATHS),'outcomes':list(OUTCOMES),'seed':SEED,
      'definitions':{'outcomes':'Full-vocabulary argmax classified as one of four distinct canonical tokens or other',
      'uncertainty':'1000 paired country bootstrap draws shared across relations and models; equal relation macro, input uncertainty only',
      'secondary':'all four canonical queries top-1 correct in all three native models; fixed before intervention, no CI',
      'interpretation':'Full donor or other wins do not establish an exclusive query module'},
      'all':{},'history_contrasts':{},'common_success':{'country_mask':mask.tolist(),'counts_by_relation':mask.sum(-1).tolist(),'ci':'not computed','metrics':{}}}
    for name,x in metrics.items():
        result['all'][name]=stats(x);result['history_contrasts'][name]={'A_minus_P':stats(x[1]-x[0]),'B_minus_P':stats(x[2]-x[0])}
        result['common_success']['metrics'][name]=conditional(x,mask[None,None,:,:])
    relation=metrics['top1_relation_hybrid']-metrics['top1_full_donor'];entity=metrics['top1_entity_hybrid']-metrics['top1_full_donor']
    result['preferences']={'relation_hybrid_minus_full_donor_all_paths':stats(relation),'entity_hybrid_minus_full_donor_all_paths':stats(entity),
      'R_minus_attention_relation_preference':stats(relation[:,0]-relation[:,3]),
      'R_relation_preference_A_minus_P':stats(relation[1,0]-relation[0,0]),'R_relation_preference_B_minus_P':stats(relation[2,0]-relation[0,0]),
      'R_minus_attention_relation_preference_A_minus_P':stats((relation[1,0]-relation[1,3])-(relation[0,0]-relation[0,3])),
      'R_minus_attention_relation_preference_B_minus_P':stats((relation[2,0]-relation[2,3])-(relation[0,0]-relation[0,3])),
      'common_success_relation_preference':conditional(relation,mask[None,None,:,:]),'common_success_entity_preference':conditional(entity,mask[None,None,:,:])}
    return result


def analyze():
    plan_path=ROOT/'plan.json';plan=json.loads(plan_path.read_text());manifest=json.loads((ROOT/'manifest.json').read_text());budget=json.loads((ROOT/'budget.json').read_text())
    if manifest.get('status')!='complete' or manifest.get('plan_sha256')!=sha(plan_path):raise ValueError('Manifest/plan mismatch')
    if manifest.get('source_sha256')!=plan.get('source_sha256') or plan['source_sha256'].get('e161_analyze.py')!=sha(__file__):raise ValueError('Source SHA mismatch')
    attempts=budget.get('attempts',[]);limit=plan['limit_gpu_seconds']
    if not attempts or any(x.get('status')!='complete' or not np.isfinite(x.get('gpu_seconds',float('nan'))) or x['gpu_seconds']<0 for x in attempts) or sum(x['gpu_seconds'] for x in attempts)>limit:raise ValueError('Budget incomplete or exceeded')
    for k in ('task_data','outcome_map','baseline_reference','component_reference','attention_reference','execution_manifest'):
        asset=plan[k]
        if sha(asset['path'])!=asset['sha256']:raise ValueError('Asset mismatch '+k)
    raw=manifest['raw']
    if sha(raw['path'])!=raw['sha256']:raise ValueError('Raw SHA mismatch')
    def load(path):
        with np.load(path,allow_pickle=False) as f:return {k:f[k] for k in f.files}
    a=load(raw['path']);d=load(plan['task_data']['path']);m=load(plan['outcome_map']['path']);ref=load(plan['baseline_reference']['path'])
    for key in ('native_lp_selected','native_top_tokens'):
        if not np.array_equal(a[key],ref[key]):raise ValueError('Native baseline mismatch '+key)
    result=summarize(a,d,m);result.update(raw_sha256=raw['sha256'],plan_sha256=manifest['plan_sha256'],analysis_source_sha256=sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    return {'status':'complete','summary':str(ROOT/'summary.json')}


def self_test():
    target=np.array([np.arange(24),np.arange(48,72)]);c=(np.arange(24)+11)%24
    q=np.stack([target,target[:,c],target[::-1],target[::-1][:,c]])
    d={'target_query_index':target,'gold_token':np.arange(96),'token_union':np.arange(96)}
    # Test population mapping independently of the fixed real 38-token vocabulary.
    assert q[3,0,0]==59 and q[3,1,0]==11 and all(len(set(q[:,r,k]))==4 for r in range(2) for k in range(24))
    x=np.zeros((3,4,2,24));x[:,0]=1;x[:,1]=2;x[:,2]=3;x[:,3]=4
    assert np.asarray(stats(x)['point']).shape==(3,4) and stats(x)['point'][1]==[1,2,3,4]
    mask=np.zeros((2,24),bool);mask[0,:8]=True; mask[1,:8]=True
    assert conditional(x,mask[None,None])['per_relation_count'][0][0]==[8,8]
    gold=np.array([(i//48)*19+(i%24)%19 for i in range(96)]);d={'target_query_index':target,'gold_token':gold,'token_union':np.arange(38)}
    m={'outcome_query_indices':q,'outcome_token_ids':gold[q],'source_query_index_both':q[3],'target_query_index':target,'token_union':np.arange(38)}
    validate_map(d,m)
    native=np.broadcast_to(gold[None,:,None],(3,96,10)).copy()
    a={'native_top_tokens':native,'native_lp_selected':np.zeros((3,96,38)),'patched_top_tokens':np.full((3,4,2,24,10),99),
       'patched_lp_selected':np.zeros((3,4,2,24,38)),'patched_KL_vs_native':np.zeros((3,4,2,24))}
    a['patched_top_tokens'][:,0,:,:,0]=gold[q[2]]
    actual,eligible=compute(a,m);assert eligible.all() and np.all(actual['top1_relation_hybrid'][:,0]==1) and np.all(actual['top1_other'][:,1:]==1)
    assert all(np.all(actual['logprob_gain_'+name]==0) for name in OUTCOMES[:4])
    z=np.array([1.,2.,2.,3.]);assert np.argmax(z)==3
    return {'status':'passed','CPU_only':True,'checks':['both-feature source mapping and distinct outcome queries','four-path axes and paired bootstrap','common-success counts','full-vocabulary argmax categorization']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--analyze',action='store_true');args=p.parse_args()
    if args.self_test==args.analyze:p.error('Choose exactly one of --self-test or --analyze')
    print(json.dumps(self_test() if args.self_test else analyze(),indent=2,ensure_ascii=False))
