"""E160 shared-signal producer x consumer cross, no training."""
import argparse,os
_p=argparse.ArgumentParser(add_help=False);_p.add_argument('--physical-gpu',type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get('CUDA_VISIBLE_DEVICES') not in (None,'',str(_early.physical_gpu)):raise ValueError('GPU visibility differs')
os.environ['CUDA_VISIBLE_DEVICES']=str(_early.physical_gpu);os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
from pathlib import Path
import json,platform
import numpy as np
import torch
import e159_run as previous
import e160_signal as signal
import e160_analyze as analysis
import mature_staged_loading as loading

n,v,h=previous.n,previous.v,previous.h
RESULT=n.WB/'results/e160';RAW=Path.home()/'mechpop_cache/e160_shared_signal_context_cross'
STAGE=Path.home()/'mechpop_cache/emo_local_staging_20261028.json'
NAMES=('P','A','B')


def proof():return {**previous.proof(),**{f:n.sha(n.WB/'scripts'/f) for f in ('e160_run.py','e160_signal.py','e160_analyze.py','mature_staged_loading.py')}}
def software():return {'python':platform.python_version(),'torch':torch.__version__,'transformers':n.transformers.__version__,'numpy':np.__version__}
def record(path):
    path=Path(path);return {'path':str(path),'sha256':n.sha(path),'size_bytes':path.stat().st_size}
def arrays(path):
    with np.load(path,allow_pickle=False) as f:return {k:f[k].copy() for k in f.files}


def self_test():
    result={'signal':signal.self_test(),'statistics':analysis.self_test()}
    n.write(RESULT/'self_test.json',{'status':'passed','CPU_only':True,'source_sha256':proof(),'software':software(),'tests':result})
    return {'status':'passed'}


def prepare():
    t=n.read(RESULT/'self_test.json')
    if t['status']!='passed' or t['source_sha256']!=proof():raise ValueError('Matching complete CPU tests required')
    loading.verify(STAGE)
    prior_plan=n.read(previous.RESULT/'plan.json');prior=n.read(previous.RESULT/'manifest.json')
    prior_budget=n.read(previous.RESULT/'budget.json')
    if prior['status']!='complete' or any(x['status']!='complete' for x in prior_budget['attempts']):raise ValueError('Completed E159 required')
    if prior['source_sha256']!=previous.proof() or n.sha(prior['raw']['path'])!=prior['raw']['sha256']:raise ValueError('Inherited E159 source/raw differs')
    source=arrays(prior['raw']['path'])
    old=n.read(n.WB/'results/e156/manifest.json')
    if old['status']!='complete' or n.sha(old['raw']['path'])!=old['raw']['sha256']:raise ValueError('Completed E156 reference required')
    old_raw=arrays(old['raw']['path'])
    natural=old_raw['candidate_loglikelihood'][:,0,0]
    if not np.array_equal(natural,source['candidate_loglikelihood'][:3,0]):raise ValueError('Inherited natural contexts disagree')
    refs={'natural_candidate_loglikelihood':natural,'without_shared_candidate_loglikelihood':source['candidate_loglikelihood'][:3,3],
      'without_routed_natural_shared_candidate_loglikelihood':source['candidate_loglikelihood'][3,0],
      'without_both_candidate_loglikelihood':source['candidate_loglikelihood'][3,3],
      **{k:source[k] for k in ('gold','subject','answer_tokens','answer_chars')}}
    RAW.mkdir(parents=True,exist_ok=True);previous.immutable_npz(RAW/'references.npz',refs)
    plan={'experiment':'E160','status':'prepared','source_sha256':proof(),'software':software(),
      'task_input':prior_plan['task_input'],'references':record(RAW/'references.npz'),'execution_manifest':record(STAGE),
      'source_records':prior_plan['source_records'],'legacy_cal_input':prior_plan['legacy_cal_input'],'pad_token_id':prior_plan['pad_token_id'],
      'reference_records':{'E159':{'manifest':record(previous.RESULT/'manifest.json'),'raw':prior['raw']},'E156':{'manifest':record(n.WB/'results/e156/manifest.json'),'raw':old['raw']}},
      'consumer_names':list(NAMES),'producer_names':list(NAMES),'shared_weight_source':'P','dense_gate_source':'P',
      'bootstrap':{'seed':160001,'resamples':1000,'unit':'paired questions within fixed subjects'},'limit_gpu_seconds':10800,
      'natural_capture_calls':384,'clamped_full_calls':1152,'zero_shared_calls':384,'zero_routed_fixed_shared_calls':384,
      'natural_zero_R_replay_calls':128,'zero_both_replay_calls':128,'regular_question_condition_calls':2560,'extra_fixed_zero_R_collapse_calls':12,
      'new_unknown_conditions':9,'scope':'Same S_P function and same input, shared output trajectories produced and consumed under R_P/A/B. Fixed replay retains producer R computation; not a routed-free model or unique mediated fraction.'}
    n.old.immutable_json(RESULT/'plan.json',plan);return {'status':'prepared','unknown_conditions':9,'regular_calls':2560}


class Budget(n.old.Budget):
    def __init__(self):self.path,self.experiment,self.phase,self.limit=RESULT/'budget.json','e160','fixed_shared_signal_producer_consumer',10800


@torch.no_grad()
def evaluate(physical):
    plan=n.read(RESULT/'plan.json')
    if plan['source_sha256']!=proof() or n.read(RESULT/'self_test.json')['source_sha256']!=proof() or plan['software']!=software():raise ValueError('Frozen complete code/software differs')
    for k in ('task_input','references','execution_manifest','legacy_cal_input'):
        x=plan[k]
        if n.sha(x['path'])!=x['sha256']:raise ValueError('Frozen reference differs: '+k)
    for x in plan['reference_records'].values():
        for field in ('manifest','raw'):
            if n.sha(x[field]['path'])!=x[field]['sha256']:raise ValueError('Completed inherited artifact differs')
    loading.verify(plan['execution_manifest']['path'])
    if (RAW/'scores.npz').exists() or (RESULT/'manifest.json').exists():raise ValueError('Refusing to replace completed result')
    a=arrays(plan['task_input']['path']);refs=arrays(plan['references']['path']);cal_data=arrays(plan['legacy_cal_input']['path'])
    cal,cv=cal_data['cal'][:2,:129],cal_data['cal_mask'][:2,:128]
    lock=None
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical)
            models,phs,bhs=[],[],[]
            ids=torch.from_numpy(cal.astype(np.int64)).to('cuda:0')
            attention=torch.cat((torch.ones((2,1),device='cuda:0',dtype=torch.bool),torch.from_numpy(cv).to('cuda:0')),1)
            for label in NAMES:
                budget.check();model=loading.load_cpu_bf16(label,plan['execution_manifest']['path']);models.append(model)
                if sum(p.numel() for p in model.parameters())!=13568641024 or len(model.model.layers)!=16:raise ValueError('Unexpected mature architecture')
                source=plan['source_records'][label];ph,bh=n.old.tensor_hash(model.state_dict()),n.old.tensor_hash(n.buffers(model))
                if ph!=source['parameter_hash'] or bh!=source['buffer_hash']:raise ValueError('Canonical parameter/buffer mismatch')
                phs.append(ph);bhs.append(bh);c=source['calibration']
                if n.sha(c['path'])!=c['sha256']:raise ValueError('Canonical cal changed')
                with np.load(c['path'],allow_pickle=False) as f:expected=torch.from_numpy(f['logits'].copy()).view(torch.bfloat16).to('cuda:0')
                if not torch.equal(n.fwd(model,ids[:,:-1],attention[:,:-1]),expected):raise ValueError('Staged native calibration differs')
                del expected;n.old.emit('E160_source_loaded',source=label,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            del ids,attention
            blocks=n.original_blocks(models)
            full=np.empty((3,3,128,4),np.float64);natural=np.empty((3,128,4),np.float64);zero_s=np.empty_like(natural);zero_r_fixed=np.empty_like(natural)
            zero_r_natural=np.empty((128,4),np.float64);both=np.empty_like(zero_r_natural);hashes=np.empty((3,128),dtype='U64')
            for q in range(128):
                budget.check();seqs=previous.prev.sequences(a['test_ids'],a['test_offsets'],range(q*4,q*4+4));prompt=int(a['prompt_tokens'][q])
                trajectories,firsts=[],[]
                for producer in range(3):
                    n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,producer,0))
                    with signal.capture_shared(model) as captured:
                        score,counts,first=h.score_candidates(model,seqs,prompt,plan['pad_token_id'])
                    if not np.array_equal(counts,a['answer_tokens'][q]) or not np.array_equal(score,refs['natural_candidate_loglikelihood'][producer,q]):raise ValueError('Natural full replay differs')
                    natural[producer,q]=score;firsts.append(first);trajectories.append(tuple(captured))
                    hashes[producer,q]=n.old.tensor_hash({f'layer{i}':x for i,x in enumerate(captured)})
                for consumer in range(3):
                    for producer in range(3):
                        budget.check();n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,consumer,0))
                        with signal.replay_shared(model,trajectories[producer]):
                            score,counts,first=h.score_candidates(model,seqs,prompt,plan['pad_token_id'])
                        if not np.array_equal(counts,a['answer_tokens'][q]):raise ValueError('Replayed token counts differ')
                        if consumer==producer and (not np.array_equal(score,natural[consumer,q]) or not torch.equal(first,firsts[consumer])):raise ValueError('Shared trajectory diagonal identity differs')
                        full[consumer,producer,q]=score
                    n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,consumer,0))
                    with v.suppress(model,'shared'):
                        score,counts,first=h.score_candidates(model,seqs,prompt,plan['pad_token_id'])
                    if not np.array_equal(counts,a['answer_tokens'][q]):raise ValueError('Shared-zero token counts differ')
                    if not np.array_equal(score,refs['without_shared_candidate_loglikelihood'][consumer,q]):raise ValueError('Natural shared-zero replay differs')
                    zero_s[consumer,q]=score
                fixed_first=[]
                for producer in range(3):
                    n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,0,0))
                    with signal.replay_shared(model,trajectories[producer]),v.suppress(model,'routed'):
                        score,counts,first=h.score_candidates(model,seqs,prompt,plan['pad_token_id'])
                    if not np.array_equal(counts,a['answer_tokens'][q]):raise ValueError('Fixed-signal routed-zero token counts differ')
                    zero_r_fixed[producer,q]=score;fixed_first.append(first)
                n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,0,0))
                with v.suppress(model,'routed'):
                    score,counts,first=h.score_candidates(model,seqs,prompt,plan['pad_token_id'])
                if not np.array_equal(counts,a['answer_tokens'][q]):raise ValueError('Natural routed-zero token counts differ')
                if not np.array_equal(score,refs['without_routed_natural_shared_candidate_loglikelihood'][q]):raise ValueError('Natural routed-zero replay differs')
                zero_r_natural[q]=score
                with v.suppress(model,'routed'),v.suppress(model,'shared'):
                    score,counts,first=h.score_candidates(model,seqs,prompt,plan['pad_token_id'])
                if not np.array_equal(counts,a['answer_tokens'][q]):raise ValueError('Both-zero token counts differ')
                if not np.array_equal(score,refs['without_both_candidate_loglikelihood'][q]):raise ValueError('Both-zero replay differs')
                both[q]=score
                if q in (0,64):
                    for consumer in (1,2):
                        for producer in range(3):
                            n.restore(models,blocks);model=n.assemble(models,blocks,(0,0,consumer,0))
                            with signal.replay_shared(model,trajectories[producer]),v.suppress(model,'routed'):
                                score,counts,first=h.score_candidates(model,seqs,prompt,plan['pad_token_id'])
                            if not np.array_equal(counts,a['answer_tokens'][q]):raise ValueError('Source-collapse token counts differ')
                            if not np.array_equal(score,zero_r_fixed[producer,q]) or not torch.equal(first,fixed_first[producer]):raise ValueError('Fixed-signal routed-zero consumer collapse differs')
                del trajectories,firsts,fixed_first,first
                if (q+1)%16==0:n.old.emit('E160_questions',questions=q+1,total=128,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            n.restore(models,blocks)
            for m,ph,bh in zip(models,phs,bhs):
                if n.old.tensor_hash(m.state_dict())!=ph or n.old.tensor_hash(n.buffers(m))!=bh:raise ValueError('Source parameters/buffers changed')
                if any(d.mlp.experts[-1]._forward_hooks for d in m.model.layers):raise ValueError('Shared capture hooks leaked')
            raw={'clamped_candidate_loglikelihood':full,'natural_candidate_loglikelihood':natural,'without_shared_candidate_loglikelihood':zero_s,
              'without_routed_fixed_shared_candidate_loglikelihood':zero_r_fixed,'without_routed_natural_shared_candidate_loglikelihood':zero_r_natural,
              'without_both_candidate_loglikelihood':both,'shared_signal_hashes':hashes,'consumer_names':np.array(NAMES),'producer_names':np.array(NAMES),
              **{k:a[k] for k in ('gold','subject','answer_tokens','answer_chars')}}
            analysis.validate(raw);path=RAW/'scores.npz';previous.immutable_npz(path,raw)
            n.write(RESULT/'manifest.json',{'experiment':'E160','status':'complete','source_sha256':proof(),'plan_sha256':n.sha(RESULT/'plan.json'),'raw':record(path),
              'canonical_parameter_hashes':phs,'canonical_buffer_hashes':bhs,'regular_question_condition_calls':2560,'extra_source_collapse_calls':12,
              'controls':{'all_native_parameter_buffer_cal_exact':True,'all_question_natural_and_zero_reference_replays_exact':True,
                          'all_question_diagonal_score_and_first_distribution_exact':True,'all_candidate_prefixes_causal_and_counts_exact':True,
                          'fixed_signal_R_zero_source_collapse_exact':True,'source_modules_buffers_parameters_restored':True},
              'physical_gpu':physical,'visible_device_uuid':str(torch.cuda.get_device_properties(0).uuid),'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
              'software':software(),'scope':plan['scope']})
    finally:
        if lock is not None:lock.close()
    return {'status':'complete'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('self-test','prepare','evaluate'));p.add_argument('--physical-gpu',type=int,default=0);args=p.parse_args();torch.set_num_threads(4)
    out=self_test() if args.mode=='self-test' else prepare() if args.mode=='prepare' else evaluate(args.physical_gpu)
    print(json.dumps(out,indent=2),flush=True)
