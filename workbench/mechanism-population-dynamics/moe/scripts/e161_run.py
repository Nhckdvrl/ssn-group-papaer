"""E161 crossed entity/relation whole-path interchange on fixed E158 inputs."""
import argparse, os
_p=argparse.ArgumentParser(add_help=False);_p.add_argument('--physical-gpu',type=int,default=0);_early,_=_p.parse_known_args()
if os.environ.get('CUDA_VISIBLE_DEVICES') not in (None,'',str(_early.physical_gpu)):raise ValueError('GPU visibility differs')
os.environ['CUDA_VISIBLE_DEVICES']=str(_early.physical_gpu);os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
import json
from pathlib import Path
import numpy as np
import torch
import e158_whole_run as old
import e161_analyze as analysis
import mature_staged_loading as staged

n=old.n; ROOT=n.WB/'results/e161'; RAW=Path.home()/'mechpop_cache/e161_crossed_entity_relation'
STAGING=Path.home()/'mechpop_cache/emo_local_staging_20261028.json'
SOURCES=('P','A','B'); PATHS=('R','S','RS','A'); LIMIT=7200


def proof():
    return {**old.proof(),**{name:n.sha(n.WB/'scripts'/name) for name in ('e161_run.py','e161_analyze.py','mature_staged_loading.py')}}


def arrays(path):
    with np.load(path,allow_pickle=False) as f:return {k:f[k].copy() for k in f.files}


def outcome_map(d):
    target=d['target_query_index'];c=(np.arange(24)+11)%24
    q=np.stack([target,target[:,c],target[::-1],target[::-1][:,c]])
    m={'outcome_query_indices':q,'outcome_token_ids':d['gold_token'][q], 'source_query_index_both':q[3].copy(),
       'token_union':d['token_union'].copy(),'target_query_index':target.copy()}
    analysis.validate_map(d,m)
    return m


def self_test():
    dp=n.read(old.PARENT/'data_plan.json');data=dp['assets']['data.npz']
    if n.sha(data['path'])!=data['sha256']:raise ValueError('Frozen data hash differs')
    d=arrays(data['path']);old.analysis.base.validate_data(d);m=outcome_map(d)
    for r in range(2):
        for c in range(24):
            assert int(m['source_query_index_both'][r,c])==int(d['target_query_index'][1-r,(c+11)%24])
            assert len(set(map(int,m['outcome_token_ids'][:,r,c])))==4
    return {'status':'passed','CPU_only':True,'outcome_map_all_48_distinct':True,'statistics':analysis.self_test()}


def prepare():
    test=self_test();stage=staged.verify(STAGING)
    old_plan=n.read(old.RESULT/'plan.json');manifest=n.read(old.RESULT/'manifest.json')
    if manifest['status']!='complete' or not manifest['patch_data_obtained'] or manifest['plan_sha256']!=n.sha(old.RESULT/'plan.json') or manifest['source_sha256']!=old.proof():raise ValueError('Sealed E158 whole-path reference required')
    if manifest['raw']['sha256']!='317dd4d6a64d3f145838cdf933c840c603362ad9ab437b1f49b08215da2c4234':raise ValueError('Unexpected E158 whole raw')
    refs={'baseline_reference':manifest['raw'],'component_reference':old_plan['component_reference'],'attention_reference':manifest['attention_components']}
    for asset in refs.values():
        if n.sha(asset['path'])!=asset['sha256']:raise ValueError('Reference asset mismatch')
    dp=n.read(old.PARENT/'data_plan.json');data=dp['assets']['data.npz'];d=arrays(data['path']);m=outcome_map(d)
    RAW.mkdir(parents=True,exist_ok=True);map_path=RAW/'outcome_map.npz';old.previous.immutable_npz(map_path,m)
    result={'experiment':'E161','status':'prepared','source_sha256':proof(),'software':old.previous.software(),
      'task_data':data,'outcome_map':old.record(map_path),**refs,'execution_manifest':old.record(STAGING),
      'source_records':old_plan['source_records'],'legacy_cal_input':old_plan['legacy_cal_input'],
      'source_names':list(SOURCES),'component_names':list(PATHS),'limit_gpu_seconds':LIMIT,
      'patch_rows':576,'positive_residual_rows':144,'fixed_inputs':'E158 all 96; q11 donor differs in both entity and relation',
      'baseline_gate':'all four canonical queries native top10 correct jointly in P/A/B, minimum 8 countries per relation',
      'bootstrap':{'seed':161001,'resamples':1000,'unit':'paired target country, equal relation macro'},
      'execution_mode':'whole_terminal_path_fixed_native_prefix_no_KV_cache','self_test':test,
      'staging_host':stage['host']}
    n.old.immutable_json(ROOT/'plan.json',result)
    return {'status':'prepared','patch_rows':576,'positive_rows':144}


class Budget(n.old.Budget):
    def __init__(self):self.path,self.experiment,self.phase,self.limit=ROOT/'budget.json','e161','crossed_entity_relation_interchange',LIMIT


@torch.no_grad()
def evaluate(physical):
    plan=n.read(ROOT/'plan.json')
    if plan['source_sha256']!=proof() or plan['software']!=old.previous.software():raise ValueError('Frozen code/software differs')
    for k in ('task_data','outcome_map','baseline_reference','component_reference','attention_reference','execution_manifest','legacy_cal_input'):
        asset=plan[k]
        if n.sha(asset['path'])!=asset['sha256']:raise ValueError('Frozen asset differs: '+k)
    staged.verify(plan['execution_manifest']['path'])
    if (ROOT/'manifest.json').exists() or (RAW/'scores.npz').exists():raise ValueError('Refusing to overwrite completed result')
    d=arrays(plan['task_data']['path']); mapping=arrays(plan['outcome_map']['path']);analysis.validate_map(d,mapping)
    baseline=arrays(plan['baseline_reference']['path']);components=arrays(plan['component_reference']['path']);attention_ref=arrays(plan['attention_reference']['path'])['attention']
    top=baseline['native_top_tokens'];q=mapping['outcome_query_indices'];gold=mapping['outcome_token_ids'];joint=np.ones((2,24),bool)
    for i in range(4):joint &= (top[:,q[i]]==gold[i][None,:,:,None]).any(-1).all(0)
    counts=joint.sum(-1)
    n.write(ROOT/'baseline_feasibility.json',{'status':'passed' if np.all(counts>=8) else 'failed','common_four_query_top10_by_relation':counts.tolist(),'scientific_feature_rows_obtained':False})
    if np.any(counts<8):raise ValueError('Four-query joint native top10 gate failed')
    raw={'source_names':np.array(SOURCES),'component_names':np.array(PATHS),'native_lp_selected':baseline['native_lp_selected'].copy(),'native_top_tokens':top.copy(),
       'patched_lp_selected':np.empty((3,4,2,24,38),np.float32),'patched_top_tokens':np.empty((3,4,2,24,10),np.int64),'patched_KL_vs_native':np.empty((3,4,2,24),np.float64),
       'positive_lp_selected':np.empty((3,2,24,38),np.float32),'positive_top_tokens':np.empty((3,2,24,10),np.int64)}
    lock=None
    try:
      with Budget() as budget:
        lock=n.old.gpu_lock(physical);selected=torch.from_numpy(d['token_union'].astype(np.int64)).to('cuda:0')
        with np.load(plan['legacy_cal_input']['path'],allow_pickle=False) as f:cal,cv=f['cal'][:2,:129].copy(),f['cal_mask'][:2,:128].copy()
        ids=torch.from_numpy(cal.astype(np.int64)).to('cuda:0');am=torch.cat((torch.ones((2,1),device='cuda:0',dtype=torch.bool),torch.from_numpy(cv).to('cuda:0')),1)
        models=[];before=[];buffers=[]
        for label in SOURCES:
            budget.check();model=staged.load_cpu_bf16(label,plan['execution_manifest']['path']);models.append(model)
            if sum(p.numel() for p in model.parameters())!=13568641024 or len(model.model.layers)!=16:raise ValueError('Mature architecture differs')
            source=plan['source_records'][label];ph=n.old.tensor_hash(model.state_dict());bh=n.old.tensor_hash(n.buffers(model))
            if ph!=source['parameter_hash'] or bh!=source['buffer_hash']:raise ValueError('Canonical source differs')
            before.append(ph);buffers.append(bh);calref=source['calibration']
            if n.sha(calref['path'])!=calref['sha256']:raise ValueError('Calibration bytes differ')
            with np.load(calref['path'],allow_pickle=False) as f:expected=torch.from_numpy(f['logits'].copy()).view(torch.bfloat16).to('cuda:0')
            if not torch.equal(n.fwd(model,ids[:,:-1],am[:,:-1]),expected):raise ValueError('Calibration mismatch')
            del expected
            n.old.emit('E161_source_loaded',source=label,peak_GB=torch.cuda.max_memory_allocated()/1e9)
        del ids,am
        groups=[];identity_count=0
        for m,model in enumerate(models):
            group=[]
            for k in range(96):
                budget.check();tokens=d['ids'][d['offsets'][k]:d['offsets'][k+1]];ref={key:components[key][m,k] for key in ('hidden','routed','shared','final_residual')}
                query=old.engine.capture(model,tokens,ref);group.append(query)
                actual_attn=torch.stack(query.attention).squeeze(1).squeeze(1).contiguous().view(torch.uint16).cpu().numpy()
                if not np.array_equal(actual_attn,attention_ref[m,k]) or not np.array_equal(query.lp[selected].cpu().numpy(),raw['native_lp_selected'][m,k]) or not np.array_equal(old.previous.top10(query.lp),top[m,k]):raise ValueError('Native replay differs')
                for path in (('R','S','RS','A') if k in (0,48) else ('RS','A')):
                    if not torch.equal(old.engine.interchange(model,query,query,path),query.lp):raise ValueError('Whole path identity mismatch')
                    identity_count+=1
                if (k+1)%24==0:n.old.emit('E161_native_queries',source=SOURCES[m],queries=k+1,total=96)
            groups.append(group)
        for m,model in enumerate(models):
            for r in range(2):
                for c in range(24):
                    budget.check();target=groups[m][int(q[0,r,c])];source=groups[m][int(q[3,r,c])]
                    value=old.engine.interchange(model,target,source,'residual')
                    if not torch.equal(value,source.lp):raise ValueError('Residual source control mismatch')
                    raw['positive_lp_selected'][m,r,c]=value[selected].cpu().numpy();raw['positive_top_tokens'][m,r,c]=old.previous.top10(value)
                    for p,path in enumerate(PATHS):
                        budget.check();value=old.engine.interchange(model,target,source,path)
                        raw['patched_lp_selected'][m,p,r,c]=value[selected].cpu().numpy();raw['patched_top_tokens'][m,p,r,c]=old.previous.top10(value)
                        raw['patched_KL_vs_native'][m,p,r,c]=old.previous.prev.kl(target.lp,value)
                    if (c+1)%8==0:n.old.emit('E161_crossed_rows',source=SOURCES[m],relation=r,countries=c+1)
        for model,ph,bh in zip(models,before,buffers):
            if n.old.tensor_hash(model.state_dict())!=ph or n.old.tensor_hash(n.buffers(model))!=bh:raise ValueError('Source parameters/buffers mutated')
            if any('forward' in layer.mlp.__dict__ or layer.mlp._forward_hooks or layer.mlp._forward_pre_hooks or layer.self_attn._forward_hooks or layer._forward_hooks for layer in model.model.layers):raise ValueError('Hooks not restored')
        analysis.validate_raw(raw);path=RAW/'scores.npz';old.previous.immutable_npz(path,raw)
        n.write(ROOT/'manifest.json',{'experiment':'E161','status':'complete','plan_sha256':n.sha(ROOT/'plan.json'),'source_sha256':proof(),'raw':old.record(path),
            'patch_rows':576,'positive_residual_rows':144,'same_query_identity_cases':identity_count,'baseline_joint_four_query_top10':counts.tolist(),
            'canonical_parameter_hashes':before,'canonical_buffer_hashes':buffers,
            'controls':{'native_component_and_attention_replay_exact':True,'native_calibration_and_hash_exact':True,'source_residual_control_exact':True,'parameters_buffers_hooks_restored':True},
            'physical_gpu':physical,'visible_device_uuid':str(torch.cuda.get_device_properties(0).uuid),'peak_allocated_bytes':torch.cuda.max_memory_allocated()})
    finally:
        if lock is not None:lock.close()
    return {'status':'complete'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('self-test','prepare','evaluate'));p.add_argument('--physical-gpu',type=int,default=0);a=p.parse_args();torch.set_num_threads(4)
    print(json.dumps(self_test() if a.mode=='self-test' else prepare() if a.mode=='prepare' else evaluate(a.physical_gpu),ensure_ascii=False,indent=2),flush=True)
