"""E162 full-course mature EMO measurement. No model training or retuning."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False);_p.add_argument('--physical-gpu',type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get('CUDA_VISIBLE_DEVICES') not in (None,'',str(_early.physical_gpu)):raise ValueError('GPU visibility differs')
os.environ['CUDA_VISIBLE_DEVICES']=str(_early.physical_gpu);os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
from contextlib import ExitStack
import gc
import json
from pathlib import Path
import platform
import socket
import numpy as np
import torch
import e150_native as n
import e151_native as removal
import e152_normalizer as norm
import e153_harness as task
import e162_analyze as analysis
import full_course_assets as assets

RESULT=n.WB/'results/e162';RAW=Path.home()/'mechpop_cache/e162_full_course_native'


def record(path):
    path=Path(path);return {'path':str(path),'sha256':n.sha(path),'size_bytes':path.stat().st_size}


def arrays(path):
    with np.load(path,allow_pickle=False) as file:return {key:file[key].copy() for key in file.files}


def software():return {'python':platform.python_version(),'torch':torch.__version__,'transformers':n.transformers.__version__,'numpy':np.__version__}


def metadata(complete=False):
    info=n.read(assets.ROOT/('asset_manifest.json' if complete else 'metadata.json'))
    if info['status']!=('complete' if complete else 'metadata_complete'):raise ValueError('Asset stage incomplete')
    model=info['model']
    if model['repo_id']!=assets.REPO or model['revision']!=assets.PIN:raise ValueError('Wrong mature endpoint')
    for name,proof in model['files'].items():
        if Path(proof['path']).stat().st_size!=proof['size_bytes']:raise ValueError('Asset size changed '+name)
        if not name.endswith('.safetensors') and n.sha(proof['path'])!=proof['sha256']:raise ValueError('Small asset changed '+name)
    old=n.assets()['models'][n.NAMES[0]]
    for name in ('config.json','configuration_emo.py','modeling_emo.py','tokenizer.json','tokenizer_config.json'):
        if model['files'][name]['sha256']!=old['files'][name]['sha256']:raise ValueError('Native class/tokenizer differs from audited A '+name)
    return model


def proof():
    model=metadata()
    sources={**n.proof(),**{name:n.sha(n.WB/'scripts'/name) for name in (
        'e151_native.py','e152_normalizer.py','e150_partial_mask_test.py','e153_harness.py','e153_data.py',
        'e162_run.py','e162_analyze.py','full_course_assets.py','stage_full_course.py')}}
    sources.update({'F/'+name:model['files'][name]['sha256'] for name in ('config.json','configuration_emo.py','modeling_emo.py')})
    return sources


@torch.no_grad()
def self_test():
    metadata();torch.manual_seed(162);torch.set_num_threads(1)
    cfg_cls,model_cls,_=n.classes(0)
    for dtype in (torch.float32,torch.bfloat16):
        cfg=cfg_cls(vocab_size=64,hidden_size=16,intermediate_size=8,num_hidden_layers=2,num_attention_heads=2,
            num_key_value_heads=2,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False,
            pad_token_id=63,eos_token_id=62,max_position_embeddings=32,attention_dropout=0.,output_router_logits=False)
        cfg._attn_implementation='eager';model=model_cls(cfg).to(dtype=dtype).eval()
        ids=torch.randint(0,62,(2,7));mask=torch.ones_like(ids);before=n.old.tensor_hash(model.state_dict());bh=n.old.tensor_hash(n.buffers(model))
        native=n.fwd(model,ids,mask);full=np.ones((2,2,4),bool)
        for rule in analysis.RULES:
            with norm.intervene(model,full,rule):assert torch.equal(n.fwd(model,ids,mask),native)
        partial=full.copy();partial[:,:,0]=False
        with n.restricted.restricted_gates(model,partial):expected=n.fwd(model,ids,mask)
        with norm.intervene(model,partial,'pool'):assert torch.equal(n.fwd(model,ids,mask),expected)
        with norm.intervene(model,partial,'full'):assert torch.isfinite(n.fwd(model,ids,mask)).all()
        original=[layer.mlp for layer in model.model.layers]
        for branches in (('routed',),('shared',),('routed','shared')):
            with ExitStack() as stack:
                for branch in branches:stack.enter_context(removal.suppress(model,branch))
                changed=n.fwd(model,ids,mask);assert torch.isfinite(changed).all() and not torch.equal(changed,native)
            assert all(layer.mlp is block for layer,block in zip(model.model.layers,original))
        assert n.old.tensor_hash(model.state_dict())==before and n.old.tensor_hash(n.buffers(model))==bh
    tests=analysis.self_test()
    n.write(RESULT/'self_test.json',{'status':'passed','CPU_only':True,'source_sha256':proof(),'software':software(),
        'tests':tests,'native_class_equals_F_code':True,'both_dtypes_all_slot_and_partial_pool_identity':True,
        'both_removals_finite_changed_and_modules_restored':True})
    return {'status':'passed','CPU_only':True}


def prepare():
    tests=n.read(RESULT/'self_test.json')
    if tests['status']!='passed' or tests['source_sha256']!=proof():raise ValueError('Matching complete CPU tests required')
    model=metadata(complete=True);lm_plan=n.read(n.RESULT/'plan.json');task_plan=n.read(n.WB/'results/e155/plan.json')
    refs={};records={}
    for label,path in [('E151',n.WB/'results/e151/manifest.json'),('E152',n.WB/'results/e152/manifest.json'),
                       ('E154',n.WB/'results/e154/manifest.json')]+[(label,n.WB/f'results/e155/manifest_{label}.json') for label in 'PAB']:
        manifest=n.read(path)
        if manifest['status']!='complete' or n.sha(manifest['raw']['path'])!=manifest['raw']['sha256']:raise ValueError('Completed inherited artifact differs '+label)
        if n.sha(path.parent/'plan.json')!=manifest['plan_sha256']:raise ValueError('Inherited plan changed '+label)
        records[label]={'manifest':record(path),'raw':manifest['raw']};refs[label]=arrays(manifest['raw']['path'])
    base=refs['P']
    for label in 'AB':
        for key in ('gold','subject','answer_tokens','answer_chars','conditions'):
            if not np.array_equal(base[key],refs[label][key]):raise ValueError('Inherited task population differs')
    if tuple(base['conditions'])!=analysis.BRANCHES:raise ValueError('Task condition semantics differ')
    lm151,lm152,parent=refs['E151'],refs['E152'],refs['E154']
    if not np.array_equal(lm151['valid'],lm152['valid']) or not np.array_equal(lm151['valid'],parent['valid']):raise ValueError('LM populations differ')
    random_plan=n.read(n.WB/'results/e151/plan.json');random_masks=arrays(random_plan['random_masks']['path'])['masks']
    if n.sha(random_plan['random_masks']['path'])!=random_plan['random_masks']['sha256']:raise ValueError('Random probes changed')
    pcond={str(x):i for i,x in enumerate(parent['conditions'])}
    native=np.concatenate((parent['metrics'][[pcond[c] for c in analysis.BRANCHES[:3]]][None],lm151['metrics'][:,:3]))
    budgets=np.stack([lm152['metrics'][i,[1+2*i+r for r in range(2)]+[j for j in range(5,11)]] for i in range(2)])
    inherited={'lm_native_metrics':native,'lm_budget_AB':budgets.reshape(2,4,2,64,512,4),
        'lm_budget_P_pool':parent['metrics'][[pcond[c] for c in analysis.MASKS]],
        'lm_random_masks':random_masks,'lm_valid':lm151['valid'],'lm_suffix_valid':lm151['suffix_valid'],
        'task_candidate_loglikelihood':np.stack([refs[c]['candidate_loglikelihood'] for c in 'PAB']),
        'task_first_answer_token_KL':np.stack([refs[c]['first_answer_token_KL'] for c in 'PAB']),
        **{k:base[k] for k in ('gold','subject','answer_tokens','answer_chars')}}
    RAW.mkdir(exist_ok=True,parents=True);path=RAW/'references.npz'
    if path.exists():raise FileExistsError('Refusing to replace frozen inherited inputs')
    np.savez_compressed(path,**inherited)
    plan={'experiment':'E162','status':'prepared','source_sha256':proof(),'software':software(),
        'model_asset_manifest':record(assets.ROOT/'asset_manifest.json'),'model':model,
        'lm_input':{'path':lm_plan['path'],'sha256':lm_plan['sha256']},'lm_input_plan':record(n.RESULT/'plan.json'),
        'task_input':task_plan['input'],'pad_token_id':task_plan['pad_token_id'],'references':record(path),
        'old_artifacts':records,'file_groups':[x['file_id'] for x in lm_plan['selected']],
        'lm_conditions':list(analysis.LM_CONDITIONS),'task_conditions':list(analysis.BRANCHES),
        'bootstrap':{'questions':162001,'files':162002,'resamples':1000},'limit_gpu_seconds':7200,'max_concurrent_gpus':4,
        'scope':'Full-course EMO vs late EMO and standard public schedules; no verified common/independent initialization or isolated timing causality.'}
    n.old.immutable_json(RESULT/'plan.json',plan)
    return {'status':'prepared','LM_conditions':12,'RC_conditions':4,'new_training':False}


class Budget(n.old.Budget):
    def __init__(self):self.path,self.experiment,self.phase,self.limit=RESULT/'budget.json','e162','full_course_mature_compute_division',7200


def load_model(bf16):
    model=metadata(complete=True);cfg_cls,cls,_=n.classes(0);root=Path(model['path'])
    if model.get('execution_host')==socket.gethostname() and Path(model['execution_root']).is_dir():
        candidate=Path(model['execution_root'])
        for name,record in model['files'].items():
            path=candidate/name
            if path.stat().st_size!=record['size_bytes'] or (not name.endswith('.safetensors') and n.sha(path)!=record['sha256']):
                raise ValueError('Verified local execution copy differs '+name)
        root=candidate
    cfg=cfg_cls.from_json_file(root/'config.json')
    actual,info=cls.from_pretrained(root,config=cfg,dtype=torch.float32,local_files_only=True,attn_implementation='sdpa',output_loading_info=True)
    if any(info.get(k) for k in ('missing_keys','unexpected_keys','mismatched_keys','error_msgs')):raise ValueError('Checkpoint keys do not match exactly')
    if bf16:actual.bfloat16()
    return actual.to('cuda:0').eval().requires_grad_(False)


def sequences(flat,offsets,indices):return [flat[offsets[i]:offsets[i+1]] for i in indices]


@torch.no_grad()
def evaluate(physical):
    plan=n.read(RESULT/'plan.json')
    if plan['source_sha256']!=proof() or n.read(RESULT/'self_test.json')['source_sha256']!=proof() or plan['software']!=software():raise ValueError('Frozen source/software differs')
    for key in ('model_asset_manifest','lm_input','lm_input_plan','task_input','references'):
        item=plan[key]
        if n.sha(item['path'])!=item['sha256']:raise ValueError('Frozen asset changed '+key)
    for group in plan['old_artifacts'].values():
        for item in group.values():
            if n.sha(item['path'])!=item['sha256']:raise ValueError('Inherited artifact changed')
    if any(path.exists() for path in (RESULT/'manifest.json',RAW/'scores.npz',RESULT/'preflight.json',RAW/'calibration_bf16.npz')):
        raise FileExistsError('Prior scientific/preflight artifacts must be preserved before any retry')
    data=arrays(plan['lm_input']['path']);questions=arrays(plan['task_input']['path']);ref=arrays(plan['references']['path'])
    lock=None
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical);budget.check()
            cal=data['cal'][:2,:129];valid_cal=data['cal_mask'][:2,:128]
            ids=torch.from_numpy(cal.astype(np.int64)).to('cuda:0')
            attention=torch.cat((torch.ones((2,1),dtype=torch.bool,device='cuda:0'),torch.from_numpy(valid_cal).to('cuda:0')),1)
            model=load_model(False);p32=n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
            del model;gc.collect();torch.cuda.empty_cache();budget.check()
            model=load_model(True)
            if sum(p.numel() for p in model.parameters())!=13568641024 or len(model.model.layers)!=16:raise ValueError('Unexpected mature architecture')
            ph=n.old.tensor_hash(model.state_dict());bh=n.old.tensor_hash(n.buffers(model))
            logits=n.fwd(model,ids[:,:-1],attention[:,:-1]);again=n.fwd(model,ids[:,:-1],attention[:,:-1])
            if not torch.equal(logits,again):raise ValueError('Native calibration repeat differs')
            p16=logits.float().log_softmax(-1);precision=n.data.masked_mean(n.old.prediction_metrics(p32,p16,ids[:,1:]).cpu().numpy(),valid_cal)
            if float(precision[:,1].max())>.02:raise ValueError('Per-sequence mean calibration precision KL exceeded .02')
            all_slots=np.ones((2,16,128),bool)
            for rule in analysis.RULES:
                with norm.intervene(model,all_slots,rule):actual=n.fwd(model,ids[:,:-1],attention[:,:-1])
                if not torch.equal(actual,logits):raise ValueError('Full-slot normalizer changes native model')
            partial=n.restricted.prefix_keep(model,ids[:,:128],32)
            with n.restricted.restricted_gates(model,partial):expected=n.fwd(model,ids[:,:-1],attention[:,:-1])
            with norm.intervene(model,partial,'pool'):actual=n.fwd(model,ids[:,:-1],attention[:,:-1])
            if not torch.equal(actual,expected):raise ValueError('Pool operator differs from prior native hook')
            np.savez_compressed(RAW/'calibration_bf16.npz',logits=logits.contiguous().view(torch.uint16).cpu().numpy())
            n.write(RESULT/'preflight.json',{'status':'complete','FP32_to_BF16_per_sequence':precision.tolist(),
                'metric_columns':list(n.old.METRICS),'calibration':record(RAW/'calibration_bf16.npz'),
                'repeat_and_both_full_slot_rules_exact':True,'partial_pool_equals_old_hook_exact':True,
                'parameter_hash':ph,'buffer_hash':bh,'canonical_conversion':'fresh CPU FP32 -> CPU BF16 including buffers -> GPU'})
            del p32,p16,ids,attention,logits,again,actual,expected
            n.old.emit('E162_native_preflight',peak_GB=torch.cuda.max_memory_allocated()/1e9)
            held=data['held'];valid=data['held_mask'];suffix=valid&(np.arange(512)[None,:]>=127)
            lm=np.empty((12,64,512,4),np.float32);prefix=np.empty((64,16,128),bool);gate_sum=np.empty((8,64,16),np.float32)
            for start in range(0,64,4):
                budget.check();ids=torch.from_numpy(held[start:start+4].astype(np.int64)).to('cuda:0')
                attention=torch.cat((torch.ones((len(ids),1),dtype=torch.bool,device='cuda:0'),torch.from_numpy(valid[start:start+4]).to('cuda:0')),1)
                prefix[start:start+4]=n.restricted.prefix_keep(model,ids[:,:128],32)
                reference=n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
                lm[0,start:start+4]=n.old.prediction_metrics(reference,reference,ids[:,1:]).cpu().numpy()
                for c,branches in ((1,('routed',)),(2,('shared',)),(3,('routed','shared'))):
                    budget.check()
                    with ExitStack() as stack:
                        for branch in branches:stack.enter_context(removal.suppress(model,branch))
                        current=n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
                    lm[c,start:start+4]=n.old.prediction_metrics(reference,current,ids[:,1:]).cpu().numpy();del current
                masks=np.concatenate((prefix[None,start:start+4],ref['lm_random_masks'][:,start:start+4]))
                for m in range(4):
                    for r,rule in enumerate(analysis.RULES):
                        budget.check();index=2*m+r
                        with norm.intervene(model,masks[m],rule,suffix[start:start+4]) as trace:
                            current=n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
                        lm[4+index,start:start+4]=n.old.prediction_metrics(reference,current,ids[:,1:]).cpu().numpy();gate_sum[index,start:start+4]=trace;del current
                del reference,ids,attention;n.old.emit('E162_LM_windows',windows=start+4,total=64)
            ll=np.empty((4,128,4),np.float64);kl=np.empty((4,128),np.float64)
            for q in range(128):
                budget.check();seq=sequences(questions['test_ids'],questions['test_offsets'],range(q*4,q*4+4));prompt=int(questions['prompt_tokens'][q])
                score,count,reference=task.score_candidates(model,seq,prompt,plan['pad_token_id'])
                if not np.array_equal(count,questions['answer_tokens'][q]):raise ValueError('Native candidate token counts differ')
                ll[0,q]=score;kl[0,q]=0
                if q==0:
                    with n.restricted.restricted_gates(model,np.ones((4,16,128),bool)):
                        identity,ic,first=task.score_candidates(model,seq,prompt,plan['pad_token_id'])
                    if not np.array_equal(identity,score) or not np.array_equal(ic,count) or not torch.equal(first,reference):raise ValueError('RC all-slot identity differs')
                    perm=np.array([2,0,3,1]);ps,pc,pf=task.score_candidates(model,[seq[i] for i in perm],prompt,plan['pad_token_id'])
                    if not np.array_equal(ps,score[perm]) or not np.array_equal(pc,count[perm]) or not torch.equal(pf,reference):raise ValueError('RC candidate reorder differs')
                    del first,pf
                for c,branches in ((1,('routed',)),(2,('shared',)),(3,('routed','shared'))):
                    budget.check()
                    with ExitStack() as stack:
                        for branch in branches:stack.enter_context(removal.suppress(model,branch))
                        value,count,current=task.score_candidates(model,seq,prompt,plan['pad_token_id'])
                    if not np.array_equal(count,questions['answer_tokens'][q]):raise ValueError('Intervention token counts differ')
                    ll[c,q]=value;kl[c,q]=float((reference.exp()*(reference-current)).double().sum());del current
                del reference
                if (q+1)%16==0:n.old.emit('E162_RC_questions',questions=q+1,total=128)
            if n.old.tensor_hash(model.state_dict())!=ph or n.old.tensor_hash(n.buffers(model))!=bh:raise ValueError('Source parameters/buffers changed')
            if any(module._forward_hooks for module in model.modules()):raise ValueError('Temporary hooks leaked')
            raw={'lm_metrics':lm,'lm_prefix_keep':prefix,'lm_random_masks':ref['lm_random_masks'],'lm_valid':valid,'lm_suffix_valid':suffix,
                'lm_applied_gate_sum':gate_sum,'lm_conditions':np.array(analysis.LM_CONDITIONS),'lm_fields':np.array(n.old.METRICS),
                'task_candidate_loglikelihood':ll,'task_first_answer_token_KL':kl,'task_conditions':np.array(analysis.BRANCHES),
                **{k:questions[k] for k in ('gold','subject','answer_tokens','answer_chars')}}
            analysis.validate(raw,ref);path=RAW/'scores.npz';np.savez_compressed(path,**raw)
            n.write(RESULT/'manifest.json',{'experiment':'E162','status':'complete','source_sha256':proof(),'plan_sha256':n.sha(RESULT/'plan.json'),
                'raw':record(path),'source_parameter_hash':ph,'source_buffer_hash':bh,
                'controls':{'fresh_canonical_BF16_cal_repeat_exact':True,'both_full_slot_rules_exact':True,'pool_equals_prior_operator_exact':True,
                    'all_candidate_prefixes_and_counts_exact':True,'candidate_reorder_exact':True,'source_parameters_buffers_hooks_restored':True},
                'physical_gpu':physical,'visible_device_uuid':str(torch.cuda.get_device_properties(0).uuid),
                'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'software':software(),'scope':plan['scope']})
    finally:
        if lock is not None:lock.close()
    return {'status':'complete'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('self-test','prepare','evaluate'));parser.add_argument('--physical-gpu',type=int,default=0)
    args=parser.parse_args();torch.set_num_threads(4)
    result=self_test() if args.mode=='self-test' else prepare() if args.mode=='prepare' else evaluate(args.physical_gpu)
    print(json.dumps(result,indent=2),flush=True)
