"""Resume E163's unfinished cross after the trace-key schema guard stopped it.

The C31 model/intervention/prediction code remains frozen. The only fingerprint
adaptation maps trace keys 0,... to E160's layer0,...; tensor values are unchanged.
Completed native forward blocks are inherited only after original-reference
validation, exact cal equivalence and fresh all-condition prediction replay.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import e163_resource_wait as resource

run=resource.run
torch=run.torch
ORIGINAL_HASH=run.n.old.tensor_hash


def compatible_hash(state):
    keys=list(state)
    if keys and set(keys)=={str(i) for i in range(len(keys))} and all(v.ndim==2 for v in state.values()):
        state={'layer'+k:v for k,v in state.items()}
    return ORIGINAL_HASH(state)


@torch.no_grad()
def self_test():
    import e160_signal as legacy
    rows={}
    for label in ('P','A','B'):
        cfg_cls,cls,_=run.loading._classes(label,complete=False)
        cfg=cfg_cls(vocab_size=64,hidden_size=16,intermediate_size=8,num_hidden_layers=2,
            num_attention_heads=2,num_key_value_heads=2,num_experts=4,num_experts_per_tok=2,
            num_shared_experts=1,norm_topk_prob=False,pad_token_id=63,eos_token_id=62,
            max_position_embeddings=32,attention_dropout=0.,output_router_logits=False)
        cfg._attn_implementation='eager'
        for dtype in (torch.float32,torch.bfloat16):
            torch.manual_seed(163);model=cls(cfg).to(dtype=dtype).eval().requires_grad_(False)
            ids=torch.arange(14).reshape(2,7);mask=torch.ones_like(ids)
            with legacy.capture_shared(model) as old:
                before=run.n.fwd(model,ids,mask)
            with run.geometry.GeometryEngine(model) as engine:
                engine.configure(capture=True);after=run.n.fwd(model,ids,mask)
                flat={str(i):v.reshape(-1,v.shape[-1]) for i,v in enumerate(engine.captured['S'])}
            expected=ORIGINAL_HASH({'layer'+str(i):v for i,v in enumerate(old)})
            assert torch.equal(before,after) and compatible_hash(flat)==expected
            assert ORIGINAL_HASH(flat)!=expected, 'Fixture must reject the original key-schema mismatch'
            assert compatible_hash(model.state_dict())==ORIGINAL_HASH(model.state_dict())
            rows[label+'/'+str(dtype)]={'actual_legacy_capture_and_new_capture_hash_equal':True,
                'original_wrong_names_rejected':True,'model_state_hash_unchanged':True,'native_logits_exact':True}
    result={'status':'passed','CPU_only':True,'source_sha256':run.n.sha(__file__),'cases':rows}
    run.n.write(run.ROOT/'hash_schema_selftest.json',result)
    return result


def validate_block(label,x,refs,record):
    if run.n.sha(record['path'])!=record['sha256']:raise ValueError('Inherited native bytes changed')
    if tuple(x['conditions'])!=run.analysis.CONDITIONS:raise ValueError('Native condition order changed')
    for key,shape in [('lm_metrics',(16,64,512,4)),('candidate_loglikelihood',(16,128,4)),('first_answer_token_KL',(16,128))]:
        if x[key].shape!=shape or not np.isfinite(x[key]).all():raise ValueError('Incomplete inherited native block')
    for key in ('gold','subject','answer_tokens','answer_chars'):
        if not np.array_equal(x[key],refs[key]):raise ValueError('Inherited population changed')
    mi=run.analysis.MODELS.index(label)
    if not np.array_equal(x['candidate_loglikelihood'][list(run.BASE)],refs['native_LL'][mi]):
        raise ValueError('Inherited full native/zero task replay changed')
    if not np.array_equal(x['first_answer_token_KL'][list(run.BASE)],refs['native_task_KL'][mi]):
        raise ValueError('Inherited full native/zero KL replay changed')
    if not np.array_equal(x['lm_metrics'][[0,1,6]],refs['native_LM_PAB'][mi]):
        raise ValueError('Inherited old native/zero language replay changed')
    for name in ('LM_geometry','task_geometry'):
        value=x[name]
        if not np.isfinite(value).all() or np.max(value[...,0])>1e-4 or np.max(value[...,2])>.01:
            raise ValueError('Inherited numerical norm guards changed')
        indices=[i for i,c in enumerate(run.analysis.CONDITIONS) if '_gram_' in c]
        if np.max(value[indices,...,1])>1e-4 or np.max(value[indices,...,3])>.01 or np.max(value[indices,...,4])>.02:
            raise ValueError('Inherited Gram guards changed')


@torch.no_grad()
def reuse_native(label,model,data,a,refs,plan,budget,means,randoms):
    inheritance=run.n.read(run.ROOT/'native_inheritance.json')
    item=inheritance['blocks'][label];x=run.analysis.arrays(item['raw']['path'])
    validate_block(label,x,refs,item['raw'])
    for name,old in item['calibration'].items():
        previous=run.analysis.arrays(old['path']);current=run.analysis.arrays(run.RAW/name)
        if run.n.sha(old['path'])!=old['sha256'] or set(previous)!=set(current):raise ValueError('Old cal provenance changed')
        if not all(np.array_equal(previous[k],current[k]) for k in previous):raise ValueError('Fresh actual cal/proposals differ')
    ids=torch.from_numpy(data['held'][:4].astype(np.int64)).to('cuda:0')
    attention=torch.cat((torch.ones((4,1),device='cuda:0',dtype=torch.bool),torch.from_numpy(data['held_mask'][:4]).to('cuda:0')),1)
    with run.geometry.GeometryEngine(model) as engine:
        run.configure(engine,0,means,randoms)
        reference=run.n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
        for i in range(16):
            budget.check();run.configure(engine,i,means,randoms)
            current=reference if i==0 else run.n.fwd(model,ids[:,:-1],attention[:,:-1]).float().log_softmax(-1)
            actual=run.n.old.prediction_metrics(reference,current,ids[:,1:]).cpu().numpy()
            if not np.array_equal(actual,x['lm_metrics'][i,:4]):raise ValueError('Fresh native LM sample replay differs '+label+'/'+str(i))
            if i:del current
        del reference,ids,attention
        seqs=run.sequences(a,0);run.configure(engine,0,means,randoms)
        baseline,counts,first=run.score(model,seqs,0,a,plan)
        for i in range(16):
            budget.check();run.configure(engine,i,means,randoms)
            values,counts,current=(baseline,counts,first) if i==0 else run.score(model,seqs,0,a,plan)
            if not np.array_equal(values,x['candidate_loglikelihood'][i,0]) or run.first_token_KL(first,current)!=x['first_answer_token_KL'][i,0]:
                raise ValueError('Fresh native task sample replay differs '+label+'/'+str(i))
            run.reorder_check(model,seqs,0,a,plan,values,counts,current,engine,lambda:run.configure(engine,i,means,randoms))
            if i:del current
    item['fresh_replay']={'status':'passed','all_conditions':16,'LM_windows':4,'RC_questions':1,
        'all_candidate_permutation_prefix_count_checks_exact':True,'cal_and_all_proposal_arrays_exact':True,
        'prediction_code_unchanged':'c31e4b0e'}
    run.n.write(run.ROOT/'native_inheritance.json',inheritance)
    run.n.old.emit('E163_inherited_native_replayed',model=label,conditions=16,LM_windows=4,RC_questions=1)
    return item['raw']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('self-test','run'))
    parser.add_argument('--group',choices=('PAB',),default='PAB')
    parser.add_argument('--physical-gpu',type=int,default=0)
    args=parser.parse_args();torch.set_num_threads(4)
    if args.mode=='self-test':print(json.dumps(self_test(),indent=2));return
    test=run.n.read(run.ROOT/'hash_schema_selftest.json')
    if test['status']!='passed' or test['source_sha256']!=run.n.sha(__file__):raise ValueError('Current legacy-interface hash test required')
    inheritance=run.n.read(run.ROOT/'native_inheritance.json');plan=run.n.read(run.ROOT/'plan.json')
    if inheritance['source_sha256']!=run.proof() or inheritance['plan_sha256']!=run.n.sha(run.ROOT/'plan.json'):
        raise ValueError('Inherited blocks lack the same frozen numerical source/plan')
    path=run.ROOT/'cross_resume.json'
    if path.exists():raise FileExistsError('Keep prior resume provenance')
    record={'status':'registered','source_path':str(Path(__file__).resolve()),'source_sha256':run.n.sha(__file__),
        'numerical_source_commit':'c31e4b0e','plan_sha256':run.n.sha(run.ROOT/'plan.json'),
        'fingerprint_schema':'Only 0,... trace keys become E160 layer0,...; values/dtypes/shapes untouched',
        'native_scores':'All original16 forward conditions retained; fresh cal, old references and all-condition sample replay required',
        'old_worker_terminal_state_hash_observed':False,'new_worker_terminal_source_state_check_required':True}
    run.n.write(path,record)
    original_native=run.native;run.native=reuse_native;run.n.old.tensor_hash=compatible_hash
    try:
        resource.main()
        for label in 'PAB':
            p=run.ROOT/('manifest_'+label+'.json');m=run.n.read(p)
            m['native_score_provenance']=run.n.read(run.ROOT/'native_inheritance.json')['blocks'][label]
            m['restoration_scope']='Fresh canonical models: calibration, all-condition sample replay and full cross; original native forward scores inherited.'
            run.n.write(p,m)
        record['status']='complete'
    except BaseException as error:
        record.update(status='failed',error=type(error).__name__+': '+str(error));raise
    finally:
        run.native=original_native;run.n.old.tensor_hash=ORIGINAL_HASH;run.n.write(path,record)


if __name__=='__main__':main()
