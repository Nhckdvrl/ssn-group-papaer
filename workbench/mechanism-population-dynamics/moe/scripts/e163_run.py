"""E163: frozen message geometry and actual producer-consumer reuse, no training."""
import argparse
import os
_early_parser = argparse.ArgumentParser(add_help=False)
_early_parser.add_argument('--physical-gpu', type=int, default=0)
_early, _ = _early_parser.parse_known_args()
if os.environ.get('CUDA_VISIBLE_DEVICES') not in (None, '', str(_early.physical_gpu)):
    raise ValueError('Physical GPU and visibility differ')
os.environ['CUDA_VISIBLE_DEVICES'] = str(_early.physical_gpu)
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
from contextlib import ExitStack
import gc
import json
from pathlib import Path
import platform
import socket
import time
import numpy as np
import torch
import e150_native as n
import e151_native as removal
import e153_harness as task
import e156_loading as loading
import e163_geometry as geometry
import e163_analyze as analysis
from e163_metrics import first_token_KL

ROOT, RAW = analysis.ROOT, analysis.RAW
SOURCE_NAMES = (
    'e163_run.py', 'e163_geometry.py', 'e163_selftest.py', 'e163_analyze.py', 'e163_metrics.py',
    'e163_verify.py', 'e150_native.py', 'e150_data.py', 'e150_restricted.py',
    'e144145_common.py', 'e144145_analyze.py', 'e123_frozen_moe.py', 'e151_native.py', 'e153_harness.py',
    'e150_partial_mask_test.py',
    'e156_loading.py', 'e154_native.py', 'e154_assets.py', 'e150_prepare_assets.py',
    'supervised_process.py',
)
BASE = (0, 1, 6, 11)
NEW = tuple(i for i in range(16) if i not in BASE)


def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': n.sha(path), 'size_bytes': path.stat().st_size}


def proof():
    return {name: n.sha(n.WB/'scripts'/name) for name in SOURCE_NAMES}


def software():
    return {'python': platform.python_version(), 'torch': torch.__version__,
            'transformers': n.transformers.__version__, 'numpy': np.__version__}


def frozen_arrays(path, values):
    path = Path(path)
    if path.exists():
        raise FileExistsError('Preserve earlier artifact before retry: '+str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **values)
    return record(path)


def prepare():
    """Only inherited data, source metadata and CPU fixtures; no model readout."""
    from e163_verify import fixture
    tests = n.read(ROOT/'CPU_geometry_test.json')
    if tests['status'] != 'passed':
        raise ValueError('Complete CPU native interface tests required')
    for name, digest in tests['source_sha256'].items():
        if n.sha(n.WB/'scripts'/name) != digest:
            raise ValueError('Geometry self-test is stale')
    oldplan = n.read(n.WB/'results/e162/plan.json')
    p160 = n.read(n.WB/'results/e160/retry_1/plan.json')
    m162 = n.read(n.WB/'results/e162/manifest.json')
    m160 = n.read(n.WB/'results/e160/retry_1/manifest.json')
    if m162['status'] != 'complete' or m160['status'] != 'complete':
        raise ValueError('Completed inherited experiments required')
    inherited = {'E162': record(n.WB/'results/e162/manifest.json'),
                 'E160': record(n.WB/'results/e160/retry_1/manifest.json')}
    for m in (m162, m160):
        if n.sha(m['raw']['path']) != m['raw']['sha256']:
            raise ValueError('Inherited raw data changed')
    if n.sha(oldplan['references']['path']) != oldplan['references']['sha256']:
        raise ValueError('Inherited PAB data changed')
    a, f, c = (analysis.arrays(oldplan['references']['path']), analysis.arrays(m162['raw']['path']),
               analysis.arrays(m160['raw']['path']))
    ll = np.concatenate((a['task_candidate_loglikelihood'], f['task_candidate_loglikelihood'][None]))
    refs = {k:a[k] for k in ('gold', 'subject', 'answer_tokens', 'answer_chars', 'lm_valid')}
    refs.update(native_LM_PAB=a['lm_native_metrics'], native_LM_F=f['lm_metrics'][:4],
                native_LL=ll, native_task_KL=np.concatenate((a['task_first_answer_token_KL'], f['task_first_answer_token_KL'][None])),
                cross_raw_LL=c['clamped_candidate_loglikelihood'], cross_native_LL=c['natural_candidate_loglikelihood'],
                cross_signal_hashes=c['shared_signal_hashes'], common_success_mask=np.all(ll[:,0].argmax(-1)==a['gold'],axis=0))
    if int(refs['common_success_mask'].sum()) != 40:
        raise ValueError('Original common-success population changed')
    for k in ('gold','subject','answer_tokens','answer_chars'):
        if not np.array_equal(a[k],f[k]) or not np.array_equal(a[k],c[k]):
            raise ValueError('Inherited populations disagree')
    cpu_fixture = fixture(refs, oldplan['file_groups'])
    n.write(ROOT/'CPU_statistics_fixture.json',cpu_fixture)
    if cpu_fixture['status'] != 'passed':
        raise ValueError('Independent old-data fixture failed')
    references = frozen_arrays(RAW/'references.npz',refs)
    source_records = p160['source_records']
    source_records['F'] = {'parameter_hash':m162['source_parameter_hash'], 'buffer_hash':m162['source_buffer_hash'],
                           'calibration':n.read(n.WB/'results/e162/preflight.json')['calibration']}
    full_asset = n.read(oldplan['model_asset_manifest']['path'])
    if full_asset['status'] != 'complete':
        raise ValueError('F durable source incomplete')
    plan = {'experiment':'E163', 'status':'prepared', 'source_sha256':proof(), 'software':software(),
            'CPU_geometry_test':record(ROOT/'CPU_geometry_test.json'),
            'CPU_statistics_fixture':record(ROOT/'CPU_statistics_fixture.json'),
            'references':references, 'old_artifacts':inherited,
            'lm_input':oldplan['lm_input'], 'task_input':oldplan['task_input'],
            'pad_token_id':oldplan['pad_token_id'], 'file_groups':oldplan['file_groups'],
            'source_records':source_records, 'F_asset_manifest':oldplan['model_asset_manifest'],
            'F_asset':full_asset['model'],
            'native_asset_code_sha256':{k:v for k,v in n.proof().items() if '/' in k},
            'conditions':list(analysis.CONDITIONS), 'rules':list(analysis.RULES),
            'random_proposal_seeds':[163101,163102], 'bootstrap':{'questions':163001,'files':163002,'resamples':1000},
            'gpu_limits':{'PAB':14400,'F':3600},'max_concurrent_gpus':2,'user_gpu_cap':4,
            'device_placement':'Native models sequential on one GPU; cross P whole + only A/B routed expert tensors on GPU, other source tensors CPU. Same original parameters, no sharding or recomputation change.',
            'scope':'Four fixed mature public paths; one family. Same-function same-input shared reuse. Oracle scalar witnesses are a diagnostic, not compression or seed-population evidence.'}
    n.old.immutable_json(ROOT/'plan.json',plan)
    return {'status':'prepared','native_conditions':16,'cross_cells':27,'new_training':False}


class Budget(n.old.Budget):
    def __init__(self, group):
        self.path, self.experiment = ROOT/('budget_'+group+'.json'), 'e163'
        self.phase, self.limit = group, {'PAB':14400,'F':3600}[group]


def cpu_load(label,plan):
    if label != 'F':
        return loading.load_cpu_bf16(label,device='cpu')
    cfg_cls, cls, _ = n.classes(0)
    root = Path(plan['F_asset']['path'])
    cfg = cfg_cls.from_json_file(root/'config.json')
    model, report = cls.from_pretrained(root,config=cfg,dtype=torch.float32,local_files_only=True,
                                       attn_implementation='sdpa',output_loading_info=True)
    for key in ('missing_keys','unexpected_keys','mismatched_keys','error_msgs'):
        if key not in report or report[key]:
            raise ValueError('F checkpoint keys do not match exactly')
    return loading._cpu_bf16(model).eval().requires_grad_(False)


def hash_model(model):
    return n.old.tensor_hash(model.state_dict()), n.old.tensor_hash(n.buffers(model))


def configure(engine,index,means,randoms):
    name = analysis.CONDITIONS[index]
    if index == 0:
        engine.configure()
        return
    target, mode = name.split('_',1)
    if mode == 'zero':
        engine.configure(target,mode)
        return
    rule, source = mode.split('_')
    tidx = analysis.TARGETS.index(target)
    direction = means[tidx] if source == 'mean' else randoms[int(source[-1]),tidx]
    engine.configure(target,rule,proposal=direction)


def diagnostics(engine):
    if engine.last_diagnostics is None:
        return np.zeros((16,9),np.float32)
    return engine.last_diagnostics.cpu().numpy()


def sequences(a,q,perm=None):
    idx = list(range(q*4,q*4+4))
    if perm is not None:
        idx = [idx[p] for p in perm]
    return [a['test_ids'][a['test_offsets'][i]:a['test_offsets'][i+1]] for i in idx]


def score(model,seqs,q,a,plan):
    ll, counts, first = task.score_candidates(model,seqs,int(a['prompt_tokens'][q]),plan['pad_token_id'],check_causal=True)
    if not np.array_equal(counts,a['answer_tokens'][q]):
        raise ValueError('Actual causal answer token counts differ')
    return ll, counts, first


def reorder_check(model,seqs,q,a,plan,ll,counts,first,engine,setup):
    perm = np.array([2,0,3,1])
    setup()
    ps, pc, pf = task.score_candidates(model,[seqs[i] for i in perm],int(a['prompt_tokens'][q]),plan['pad_token_id'],check_causal=True)
    if not np.array_equal(ps,ll[perm]) or not np.array_equal(pc,counts[perm]) or not torch.equal(pf,first):
        raise ValueError('Candidate ordering changed scores or causal prefix')


@torch.no_grad()
def calibration(label,model,data,plan,budget):
    cal, valid = data['cal'][:2,:129], data['cal_mask'][:2,:128]
    ids = torch.from_numpy(cal.astype(np.int64)).to('cuda:0')
    attn = torch.cat((torch.ones((2,1),device='cuda:0',dtype=torch.bool),torch.from_numpy(valid).to('cuda:0')),1)
    baseline = n.fwd(model,ids[:,:-1],attn[:,:-1])
    if not torch.equal(baseline,n.fwd(model,ids[:,:-1],attn[:,:-1])):
        raise ValueError('Actual native repeat differs')
    old = plan['source_records'][label]['calibration']
    expected = torch.from_numpy(analysis.arrays(old['path'])['logits']).view(torch.bfloat16).to('cuda:0')
    if not torch.equal(baseline,expected):
        raise ValueError('Native calibration differs from mature canonical source '+label)
    del expected
    means = []
    probe_arrays = {}
    randoms = np.stack([np.random.default_rng(seed).normal(size=(3,16,2048)).astype(np.float32) for seed in plan['random_proposal_seeds']])
    random_gpu = torch.from_numpy(randoms).to('cuda:0')
    with geometry.GeometryEngine(model) as engine:
        engine.configure(capture=True)
        if not torch.equal(baseline,n.fwd(model,ids[:,:-1],attn[:,:-1])):
            raise ValueError('Actual native message interception changed logits')
        mask = attn[:,:-1]
        for target in geometry.TARGETS:
            means.append(torch.stack([u[mask].double().mean(0).float() for u in engine.captured[target]]))
        mean_gpu = torch.stack(means)
        # End interception before calling the original suppressors.
    zero_oracles = {}
    for target in geometry.TARGETS:
        branches = ('routed',) if target=='R' else ('shared',) if target=='S' else ('routed','shared')
        with ExitStack() as stack:
            for branch in branches:
                stack.enter_context(removal.suppress(model,branch))
            zero_oracles[target] = n.fwd(model,ids[:,:-1],attn[:,:-1])
    with geometry.GeometryEngine(model) as engine:
        for target in geometry.TARGETS:
            engine.configure(target,'zero')
            if not torch.equal(n.fwd(model,ids[:,:-1],attn[:,:-1]),zero_oracles[target]):
                raise ValueError('Actual zero branch differs from original helper '+target)
        for index in NEW:
            budget.check(); configure(engine,index,mean_gpu,random_gpu)
            engine.save_probes = True
            value = n.fwd(model,ids[:,:-1],attn[:,:-1])
            if not torch.isfinite(value).all():
                raise ValueError('Nonfinite calibration substitution')
            for probe in engine.probes:
                for key,value in probe.items():
                    if key != 'layer':
                        probe_arrays[str(index)+'_'+str(probe['layer'])+'_'+key] = value
        configure(engine,0,mean_gpu,random_gpu)
        if not torch.equal(n.fwd(model,ids[:,:-1],attn[:,:-1]),baseline):
            raise ValueError('Calibration restoration differs')
    probes = frozen_arrays(RAW/('geometry_probes_'+label+'.npz'),probe_arrays)
    proposals = frozen_arrays(RAW/('proposals_'+label+'.npz'),{'mean':mean_gpu.cpu().numpy(),'random':randoms})
    info = {'status':'complete','native_calibration_repeat_interception_and_zero_exact':True,
            'legacy_calibration':old,'proposals':proposals,'geometry_probes':probes}
    n.write(ROOT/('preflight_'+label+'.json'),info)
    del baseline,zero_oracles,ids,attn
    gc.collect();torch.cuda.empty_cache()
    n.old.emit('E163_actual_preflight',model=label,peak_GB=torch.cuda.max_memory_allocated()/1e9)
    return mean_gpu,random_gpu,info


@torch.no_grad()
def native(label,model,data,a,refs,plan,budget,means,randoms):
    mi = analysis.MODELS.index(label)
    lm = np.empty((16,64,512,4),np.float32)
    ll = np.empty((16,128,4),np.float64); kl = np.empty((16,128),np.float64)
    lmgeo = np.zeros((16,16,16,9),np.float32); qgeo = np.zeros((16,128,16,9),np.float32)
    nativegeo = np.empty((16,3,16,3),np.float32)
    with geometry.GeometryEngine(model) as engine:
        # The entire inherited baseline grid is replayed before new directions.
        for phase,indices in [('inherited',BASE),('geometry',NEW)]:
            for start in range(0,64,4):
                budget.check()
                ids = torch.from_numpy(data['held'][start:start+4].astype(np.int64)).to('cuda:0')
                attention = torch.cat((torch.ones((4,1),device='cuda:0',dtype=torch.bool),torch.from_numpy(data['held_mask'][start:start+4]).to('cuda:0')),1)
                configure(engine,0,means,randoms)
                reference = n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
                nativegeo[start//4] = engine.last_native_geometry.cpu().numpy()
                for index in indices:
                    budget.check(); configure(engine,index,means,randoms)
                    current = reference if index==0 else n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
                    values = n.old.prediction_metrics(reference,current,ids[:,1:]).cpu().numpy()
                    lm[index,start:start+4] = values
                    lmgeo[index,start//4] = diagnostics(engine)
                    if index in BASE and not (index==11 and label!='F'):
                        old_index = BASE.index(index)
                        expected = refs['native_LM_F'][old_index,start:start+4] if label=='F' else refs['native_LM_PAB'][mi,old_index,start:start+4]
                        if not np.array_equal(values,expected):
                            raise ValueError('Inherited native LM replay differs '+label+'/'+analysis.CONDITIONS[index])
                    if index != 0: del current
                del reference,ids,attention
                if start%16==0 or start==60:
                    n.old.emit('E163_LM',model=label,phase=phase,windows=start+4)
            for q in range(128):
                budget.check(); seqs = sequences(a,q)
                configure(engine,0,means,randoms)
                base_ll, base_count, first = score(model,seqs,q,a,plan)
                if not np.array_equal(base_ll,refs['native_LL'][mi,0,q]):
                    raise ValueError('Native task replay differs')
                for index in indices:
                    budget.check(); configure(engine,index,means,randoms)
                    if index==0:
                        values,counts,current = base_ll,base_count,first
                    else:
                        values,counts,current = score(model,seqs,q,a,plan)
                    ll[index,q] = values
                    kl[index,q] = first_token_KL(first,current)
                    qgeo[index,q] = diagnostics(engine)
                    if index in BASE:
                        old_index = BASE.index(index)
                        if not np.array_equal(values,refs['native_LL'][mi,old_index,q]):
                            raise ValueError('Inherited candidate LL differs '+label+'/'+analysis.CONDITIONS[index]+': max gap '+str(float(np.max(np.abs(values-refs['native_LL'][mi,old_index,q])))))
                        if kl[index,q]!=refs['native_task_KL'][mi,old_index,q]:
                            raise ValueError('Inherited first KL differs '+label+'/'+analysis.CONDITIONS[index]+': actual '+str(kl[index,q])+' expected '+str(refs['native_task_KL'][mi,old_index,q]))
                    if q==0:
                        reorder_check(model,seqs,q,a,plan,values,counts,current,engine,lambda:configure(engine,index,means,randoms))
                    if index!=0: del current
                del first
                if q%16==15:
                    n.old.emit('E163_RC',model=label,phase=phase,questions=q+1)
    values = {'lm_metrics':lm,'candidate_loglikelihood':ll,'first_answer_token_KL':kl,
              'LM_geometry':lmgeo,'task_geometry':qgeo,'native_LM_geometry':nativegeo,
              'conditions':np.array(analysis.CONDITIONS), 'lm_valid':data['held_mask'],
              **{k:a[k] for k in ('gold','subject','answer_tokens','answer_chars')}}
    return frozen_arrays(RAW/('native_'+label+'.npz'),values)


@torch.no_grad()
def cross(models,blocks,a,refs,plan,budget):
    ll = np.empty((3,3,3,128,4),np.float64); kl = np.empty((3,3,3,128),np.float64)
    diag = np.zeros((3,3,3,128,16,9),np.float32)
    hashes = np.empty((3,128),dtype='U64')
    for q in range(128):
        budget.check(); seqs = sequences(a,q); trajectories=[]; firsts=[]
        for producer in range(3):
            n.restore(models,blocks); model=n.assemble(models,blocks,(0,0,producer,0))
            with geometry.GeometryEngine(model) as engine:
                engine.configure(capture=True)
                values,_,first = score(model,seqs,q,a,plan)
                trajectory = tuple(engine.captured['S'])
                hashes[producer,q] = n.old.tensor_hash({str(i):u.reshape(-1,u.shape[-1]) for i,u in enumerate(trajectory)})
                if hashes[producer,q]!=refs['cross_signal_hashes'][producer,q] or not np.array_equal(values,refs['cross_native_LL'][producer,q]):
                    raise ValueError('E160 actual producer trace/score failed replay')
                trajectories.append(trajectory); firsts.append(first)
        for consumer in range(3):
            n.restore(models,blocks); model=n.assemble(models,blocks,(0,0,consumer,0))
            with geometry.GeometryEngine(model) as engine:
                for producer in range(3):
                    for ri,rule in enumerate(analysis.RULES):
                        budget.check()
                        engine.configure('S',rule,directions=trajectories[producer],witnesses=trajectories[consumer])
                        values,counts,current = score(model,seqs,q,a,plan)
                        ll[ri,consumer,producer,q]=values
                        kl[ri,consumer,producer,q]=first_token_KL(firsts[consumer],current)
                        diag[ri,consumer,producer,q]=diagnostics(engine)
                        if ri==0 and not np.array_equal(values,refs['cross_raw_LL'][consumer,producer,q]):
                            raise ValueError('Entire E160 raw producer-consumer replay failed')
                        if consumer==producer and not np.array_equal(values,refs['cross_native_LL'][consumer,q]):
                            raise ValueError('Actual geometric source diagonal changed')
                        if q==0:
                            perm=np.array([2,0,3,1])
                            engine.configure('S',rule,directions=tuple(u[perm] for u in trajectories[producer]),
                                             witnesses=tuple(u[perm] for u in trajectories[consumer]))
                            ps,pc,pf=task.score_candidates(model,[seqs[p] for p in perm],int(a['prompt_tokens'][q]),plan['pad_token_id'],check_causal=True)
                            if not np.array_equal(ps,values[perm]) or not np.array_equal(pc,counts[perm]) or not torch.equal(pf,current):
                                raise ValueError('Actual cross candidate reorder failed')
                        del current
        n.restore(models,blocks)
        del trajectories,firsts
        if q%8==7:
            n.old.emit('E163_cross',questions=q+1,total=128)
    return frozen_arrays(RAW/'cross.npz',{'candidate_loglikelihood':ll,'first_answer_token_KL':kl,
        'geometry':diag,'shared_signal_hashes':hashes,'rules':np.array(analysis.RULES),
        **{k:a[k] for k in ('gold','subject','answer_tokens','answer_chars')}})


def verify_inputs(plan):
    if plan['source_sha256']!=proof() or plan['software']!=software():
        raise ValueError('Frozen source/software changed')
    for key in ('references','CPU_geometry_test','CPU_statistics_fixture','lm_input','task_input','F_asset_manifest'):
        item=plan[key]
        if n.sha(item['path'])!=item['sha256']:
            raise ValueError('Frozen input changed '+key)
    for item in plan['source_records'].values():
        c=item['calibration']
        if n.sha(c['path'])!=c['sha256']:
            raise ValueError('Canonical calibration changed')
    if {k:v for k,v in n.proof().items() if '/' in k}!=plan['native_asset_code_sha256']:
        raise ValueError('Pinned public source code changed')
    for name,proof_record in plan['F_asset']['files'].items():
        path=Path(proof_record['path'])
        if path.stat().st_size!=proof_record['size_bytes'] or (not name.endswith('.safetensors') and n.sha(path)!=proof_record['sha256']):
            raise ValueError('F source changed '+name)


@torch.no_grad()
def evaluate(group,physical):
    plan=n.read(ROOT/'plan.json');verify_inputs(plan)
    labels=('P','A','B') if group=='PAB' else ('F',)
    for label in labels:
        for path in (ROOT/('manifest_'+label+'.json'),RAW/('native_'+label+'.npz'),ROOT/('preflight_'+label+'.json'),RAW/('geometry_probes_'+label+'.npz')):
            if path.exists():
                raise FileExistsError('Preserve previous attempt before retry '+str(path))
    data=analysis.arrays(plan['lm_input']['path']);a=analysis.arrays(plan['task_input']['path']);refs=analysis.arrays(plan['references']['path'])
    torch.set_num_threads(4)
    cpu_started=time.monotonic();models=[];before={}
    for label in labels:
        n.old.emit('E163_CPU_load_start',model=label,host=socket.gethostname())
        model=cpu_load(label,plan)
        if sum(p.numel() for p in model.parameters())!=13568641024 or len(model.model.layers)!=16:
            raise ValueError('Unexpected mature model architecture')
        before[label]=hash_model(model)
        expected=plan['source_records'][label]
        if before[label]!=(expected['parameter_hash'],expected['buffer_hash']):
            raise ValueError('Canonical CPU parameters/buffers differ '+label)
        models.append(model)
        n.old.emit('E163_CPU_load_ready',model=label,cpu_elapsed_seconds=time.monotonic()-cpu_started)
    readiness={'status':'ready','host':socket.gethostname(),'pid':os.getpid(),'physical_gpu':physical,
               'CPU_IO_seconds':time.monotonic()-cpu_started,'hashes':before,'CUDA_initialized':torch.cuda.is_initialized()}
    if readiness['CUDA_initialized']:
        raise ValueError('CPU/I/O stage unexpectedly initialized a GPU')
    n.write(ROOT/('CPU_readiness_'+group+'.json'),readiness)
    lock=None;raw_records={};preflights={}
    blocks=n.original_blocks(models)
    try:
        lock=n.old.gpu_lock(physical)
        with Budget(group) as budget:
            for label,model in zip(labels,models):
                budget.check(); model.to('cuda:0')
                means,randoms,preflights[label]=calibration(label,model,data,plan,budget)
                raw_records[label]=native(label,model,data,a,refs,plan,budget,means,randoms)
                del means,randoms
                model.to('cpu');gc.collect();torch.cuda.empty_cache()
                n.old.emit('E163_native_finished',model=label,raw=raw_records[label])
            if group=='PAB':
                # Keep the P receiver intact and transfer only used foreign R
                # parameters, making the exact same cross fit an 80 GiB GPU.
                models[0].to('cuda:0')
                for group_blocks in blocks[1:]:
                    for block in group_blocks:
                        for expert in list(block.experts)[:-1]:
                            expert.to('cuda:0')
                budget.check()
                raw_records['cross']=cross(models,blocks,a,refs,plan,budget)
                n.restore(models,blocks)
            for label,model in zip(labels,models):
                budget.check();model.to('cpu')
                if hash_model(model)!=before[label]:
                    raise ValueError('Source state changed after interventions '+label)
                if any(m._forward_hooks or m._forward_pre_hooks for m in model.modules()):
                    raise ValueError('A local hook survived restoration')
            peak=torch.cuda.max_memory_allocated()/1e9
            budget.check()
        for label,raw in raw_records.items():
            n.write(ROOT/('manifest_'+label+'.json'),{'experiment':'E163','status':'complete','label':label,
                'source_sha256':proof(),'plan_sha256':n.sha(ROOT/'plan.json'),'raw':raw,
                'host':socket.gethostname(),'physical_gpu':physical,'peak_GPU_GB':peak,
                'source_parameters_buffers_hooks_restored':True,'source_hashes':before,
                'preflight':preflights.get(label),'CPU_readiness':record(ROOT/('CPU_readiness_'+group+'.json')),
                'budget':record(ROOT/('budget_'+group+'.json'))})
        n.old.emit('E163_complete',group=group,peak_GPU_GB=peak)
    finally:
        n.restore(models,blocks)
        if lock is not None:lock.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('prepare','run'))
    parser.add_argument('--group',choices=('PAB','F'),default='PAB')
    parser.add_argument('--physical-gpu',type=int,default=0)
    args=parser.parse_args()
    result=prepare() if args.mode=='prepare' else evaluate(args.group,args.physical_gpu)
    print(json.dumps(result,indent=2))
