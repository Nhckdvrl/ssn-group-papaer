"""One frozen E166 family per CPU-first single-GPU worker; no automatic retries."""
import argparse
import os
early=argparse.ArgumentParser(add_help=False)
early.add_argument('--physical-gpu',type=int,default=0)
visible,_=early.parse_known_args()
if os.environ.get('CUDA_VISIBLE_DEVICES') not in (None,'',str(visible.physical_gpu)):raise ValueError('GPU visibility differs')
os.environ['CUDA_VISIBLE_DEVICES']=str(visible.physical_gpu)
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'

import copy
from contextlib import ExitStack
import json
import socket
import traceback
import numpy as np
import torch
from torch import nn

import e166_common as c
import e166_core as gain
import e166_analyze as analysis
import e165_core as olmoe
import e150_restricted as emo_masks
import e151_native as removal
import e153_harness as task
from e164_routing import RoutingEngine,permute_trace
from e163_metrics import first_token_KL


def assemble(models,original,r,shared):
    model=models[0]
    for i,layer in enumerate(model.model.layers):
        template=original[0][i];block=copy.copy(template)
        for name in ('_modules','_parameters','_buffers','_forward_hooks','_forward_pre_hooks'):
            setattr(block,name,copy.copy(getattr(template,name)))
        experts=list(original[r][i].experts)
        if shared:experts[-1]=original[0][i].experts[-1]
        block.experts=nn.ModuleList(experts);layer.mlp=block
    return model


def restricted(model,mask,shared):
    return emo_masks.restricted_gates(model,np.broadcast_to(mask,(4,*mask.shape)).copy()) if shared else olmoe.restricted(model,mask)


def score(model,seqs,prompt,pad,count):
    ll,actual,fp=task.score_candidates(model,seqs,int(prompt),pad,check_causal=True)
    if not np.array_equal(actual,count):raise ValueError('Candidate token counts changed')
    return ll,fp


@torch.no_grad()
def evaluate(family,physical):
    plan=c.checked_plan();spec=plan['families'][family];shared=family=='emo'
    raw=c.RAW/family;raw.mkdir(parents=True,exist_ok=True)
    if any((raw/name).exists() for name in ('scores.npz','partial_scores.npz','calibration.npz')):
        raise FileExistsError('Preserve earlier E166 attempt; inspect before recovery')
    a=analysis.arrays(spec['input']['path']);selectors=analysis.arrays(spec['selectors']['path'])
    masks=selectors['masks'][2:] if shared else selectors['masks']
    if masks.shape!=(55,16,128 if shared else 64) or not np.all(masks.sum(-1)==(32 if shared else 16)):
        raise ValueError('Inherited pool shape/count changed')
    if shared and not masks[:,:,-1].all():raise ValueError('Shared slot must remain available')
    reference=analysis.arrays(spec['reference']['path'])
    models,states=c.load(family,spec);original=olmoe.blocks(models);lock=None
    out={k:a[k] for k in ('subject','gold','answer_tokens','answer_chars')}
    out.update(conditions=np.array(analysis.conditions(family)),
          candidate_loglikelihood=np.full((len(analysis.cases(family)),440,4),np.nan),
          first_answer_token_KL=np.full((len(analysis.cases(family)),440),np.nan),
          trace_hashes=np.full((2,440),'',dtype='U64'))
    try:
        lock=c.acquire(physical,plan,family)
        with c.Budget(plan,family) as budget:
            models[0].to('cuda:0')
            for block in original[1]:
                for expert in (block.experts[:-1] if shared else block.experts):expert.to('cuda:0')
            model=models[0]
            # Calibration observer must preserve the actual unmodified native prediction.
            cal=[a['cal_ids'][a['cal_offsets'][i]:a['cal_offsets'][i+1]] for i in range(len(a['cal_offsets'])-1)]
            first_ids,first_mask=task.padded(cal[:2],spec['pad_token_id'],'cuda:0')
            baseline=model(input_ids=first_ids,attention_mask=first_mask,use_cache=False,
                           output_router_logits=False,return_dict=True).logits
            with gain.EnergyCalibration(model,original[1],shared) as observer:
                for start in range(0,len(cal),2):
                    budget.check();ids,valid=task.padded(cal[start:start+2],spec['pad_token_id'],'cuda:0')
                    logits=model(input_ids=ids,attention_mask=valid,use_cache=False,
                                 output_router_logits=False,return_dict=True).logits
                    if start==0 and not torch.equal(logits,baseline):raise ValueError('Calibration observer changed native P')
                    del logits,ids,valid
                    if start%40==0:print(json.dumps({'event':'calibration','family':family,'rows':min(start+2,len(cal))}),flush=True)
                calibrated=observer.result()
            del baseline,first_ids,first_mask
            calibration=c.save(raw/'calibration.npz',calibrated)
            c.write(c.ROOT/(family+'_calibration.json'),{'status':'complete','raw':calibration,
                    'rule':plan['calibration'],'rows':len(cal),'valid_tokens_per_layer':calibrated['tokens'].tolist(),
                    'effective_FP32_gain':calibrated['gain'].tolist(),'native_observer_identity_exact':True,
                    'no_predictive_loss_fitting':True,'source_sha256':c.proof()})
            for q in range(440):
                budget.check();olmoe.restore(models,original)
                seqs=olmoe.sequences(a,q);prompt=a['prompt_tokens'][q];expected=a['answer_tokens'][q]
                mask=masks[int(a['subject'][q])];factual=None
                for policy in range(2):
                    model=assemble(models,original,0,shared)
                    with ExitStack() as stack:
                        engine=stack.enter_context(RoutingEngine(model));engine.configure(capture=True)
                        if policy:stack.enter_context(restricted(model,mask,shared))
                        parent_ll,parent_fp=score(model,seqs,prompt,spec['pad_token_id'],expected)
                        trace=tuple(engine.captured)
                    out['trace_hashes'][policy,q]=c.old.old.tensor_hash({f'layer{i}':v for i,v in enumerate(trace)})
                    if policy==0:factual=parent_fp
                    for index,(r,p,s) in enumerate(analysis.cases(family)):
                        if p!=policy:continue
                        model=assemble(models,original,int(r==1),shared)
                        with ExitStack() as stack:
                            engine=stack.enter_context(RoutingEngine(model));engine.configure(trace=trace)
                            if policy:stack.enter_context(restricted(model,mask,shared))
                            if r==2:stack.enter_context(gain.gains(model,calibrated['gain'],shared))
                            if s:stack.enter_context(removal.suppress(model,'shared'))
                            ll,fp=score(model,seqs,prompt,spec['pad_token_id'],expected)
                            if r==0 and s==0 and (not np.array_equal(ll,parent_ll) or not torch.equal(fp,parent_fp)):
                                raise ValueError('Actual P route diagonal changed')
                            oldindex=None
                            if shared:
                                if r<2 and s==0:oldindex=4*policy+2*r
                                elif r<2 and s==1 and policy==0:oldindex=10+2*r
                            elif r<2:oldindex=(8*policy if r==0 else 17+2*policy)
                            if oldindex is not None:
                                oldq=q+128 if shared else q
                                if not np.array_equal(ll,reference['candidate_loglikelihood'][oldindex,oldq]):
                                    raise ValueError('Exact old candidate LL differs')
                                if first_token_KL(factual,fp)!=reference['first_answer_token_KL'][oldindex,oldq]:
                                    raise ValueError('Exact old first-token KL differs')
                            out['candidate_loglikelihood'][index,q]=ll
                            out['first_answer_token_KL'][index,q]=first_token_KL(factual,fp)
                            if q==0:
                                order=[2,0,3,1];engine.configure(trace=permute_trace(trace,order,4))
                                other,of=score(model,[seqs[i] for i in order],prompt,spec['pad_token_id'],expected[order])
                                if not np.array_equal(other,ll[order]) or not torch.equal(of,fp):raise ValueError('Candidate permutation failed')
                        if q==0 and r==0 and s==0:
                            # Same trace: exact unit-gain identity and original routed-zero oracle.
                            with ExitStack() as stack:
                                engine=stack.enter_context(RoutingEngine(model));engine.configure(trace=trace)
                                if policy:stack.enter_context(restricted(model,mask,shared))
                                with gain.gains(model,np.ones(16),shared):unit,uf=score(model,seqs,prompt,spec['pad_token_id'],expected)
                                if not np.array_equal(unit,ll) or not torch.equal(uf,fp):raise ValueError('Unit gain identity failed')
                                with gain.gains(model,np.zeros(16),shared):zero,zf=score(model,seqs,prompt,spec['pad_token_id'],expected)
                                with (removal.suppress(model,'routed') if shared else olmoe.zero_moe(model)):
                                    oracle,orf=score(model,seqs,prompt,spec['pad_token_id'],expected)
                                if not np.array_equal(zero,oracle) or not torch.equal(zf,orf) or torch.equal(zf,fp):
                                    raise ValueError('Gain zero native oracle/positive failed')
                        if q==0 and shared and s==1 and policy==1:
                            # Validate new pool S-zero against the original helper with
                            # independently assembled native blocks, the same fixed trace.
                            import e150_native as native
                            olmoe.restore(models,original);oracle_model=native.assemble(models,original,(0,0,int(r==1),0))
                            with ExitStack() as stack:
                                engine=stack.enter_context(RoutingEngine(oracle_model));engine.configure(trace=trace)
                                stack.enter_context(restricted(oracle_model,mask,True))
                                if r==2:stack.enter_context(gain.gains(oracle_model,calibrated['gain'],True))
                                stack.enter_context(removal.suppress(oracle_model,'shared'))
                                oracle,orf=score(oracle_model,seqs,prompt,spec['pad_token_id'],expected)
                            if not np.array_equal(oracle,ll) or not torch.equal(orf,fp):raise ValueError('Pool S-zero helper differs')
                if q%8==7:
                    c.save(raw/'partial_scores.npz',out,replace=True)
                    print(json.dumps({'event':'progress','family':family,'questions':q+1,'total':440}),flush=True)
            if not np.isfinite(out['candidate_loglikelihood']).all() or not np.isfinite(out['first_answer_token_KL']).all():
                raise ValueError('Incomplete scientific matrix')
            olmoe.restore(models,original)
            for model,state in zip(models,states):
                model.cpu()
                if c.old.state(model,state['label'])!=state:raise ValueError('Source parameters/buffers/hooks changed')
            result=c.save(raw/'scores.npz',out);peak=torch.cuda.max_memory_allocated()/1e9
        c.write(c.ROOT/(family+'_manifest.json'),{'experiment':'E166','family':family,'status':'complete',
                'raw':result,'calibration':calibration,'plan_sha256':c.sha(c.ROOT/'plan.json'),'source_sha256':c.proof(),
                'all_old_LL_KL_exact':True,'unit_zero_gain_and_observer_native_interfaces_exact':True,
                'all_route_diagonals_causal_prefix_counts_and_first_question_permutations_exact':True,
                'new_pool_shared_zero_original_helper_exact':shared,'source_parameters_buffers_hooks_restored':True,
                'sources':states,'host':socket.gethostname(),'physical_gpu':physical,'peak_GPU_GB':peak})
        print(json.dumps({'event':'family_complete','family':family,'peak_GPU_GB':peak}),flush=True)
    finally:
        olmoe.restore(models,original)
        if lock is not None:lock.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('prepare','emo','olmoe'))
    p.add_argument('--physical-gpu',type=int,default=1);args=p.parse_args();torch.set_num_threads(4)
    try:
        if args.mode=='prepare':c.prepare()
        else:evaluate(args.mode,args.physical_gpu)
    except BaseException as error:
        c.write(c.ROOT/('failure_'+args.mode+'.json'),{'status':'failed','error':str(error),'traceback':traceback.format_exc(),'source_sha256':c.proof()})
        raise


if __name__=='__main__':main()
