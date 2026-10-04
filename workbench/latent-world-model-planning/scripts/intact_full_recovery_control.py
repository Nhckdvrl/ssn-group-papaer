"""E18 F3: complete deployment on new episodes and independent model seeds."""
import argparse
import shutil
from pathlib import Path
import numpy as np
import torch
import intact_published_control_v3 as a
import intact_multi_seed_source as s
import intact_recovery_forks_v2 as f
import intact_waypoint_recovery as w
from experience_transfer_control_audit import ROOT,read,save,sha

METHODS=['BASE25','GOAL15','GOAL5','REFERENCE5']


@torch.inference_mode()
def run(task,seed):
    a.setup()
    bank=s.bank(task)
    assert read(bank/'complete.json')['all_factual_replay_exact']
    ledger=read(bank/'ledger.json')
    prefix=ROOT/f'20261005-E18-intact-F3-{task}-s{seed}'
    pre=Path(str(prefix)+'-preflight')
    assert not pre.exists()
    pre.mkdir()
    shutil.copy2(__file__,pre/'used.py')
    try:
        net,scaler,source=s.source(task,seed,'cuda')
        frozen=a.state_hash(net.state_dict())
        model,processor,cpu_source=s.source(task,seed,'cpu')
        assert cpu_source==source
        initial=ledger[0]
        current=np.load(bank/'history_000.npy')[-1]
        goal=np.load(bank/'goal_000.npy')
        tests=[]
        for device,actual,normalizer in [('cpu',model,processor),('cuda',net,scaler)]:
            inputs=a.info(current,goal,initial['warm_actions'],normalizer,device)
            before=a.state_hash(actual.state_dict())
            full=actual.get_action(inputs,horizon=5)
            short=actual.get_action(inputs,horizon=1)
            assert full.shape==(1,5,10) and torch.equal(short[:,0],full[:,0])
            references=w.reference(actual,inputs,full)
            zgoal=actual.encode(dict(pixels=inputs['goal']))['emb'][:,-1]
            previous=actual.action_encoder(inputs['action'])[:,-1]
            global_stats=w.query(actual,references[:,0],zgoal,previous)
            local_stats=w.query(actual,references[:,0],references[:,1],previous)
            assert torch.equal(global_stats['map_mean'],full[:,0])
            values=torch.cat([global_stats['map_mean'],global_stats['log_std'],local_stats['map_mean'],local_stats['log_std']],-1).cpu().numpy()
            if device=='cpu':cpu=values
            else:np.testing.assert_allclose(values,cpu,atol=2e-4,rtol=1e-5)
            assert before==a.state_hash(actual.state_dict())
            tests.append(dict(device=device,passed=True,first_short_full_exact=True,goal_manual_exact=True,local_manual_exact=True,clamped_std_exact=True,model_unchanged=True))
        del model
        guards=[]
        for entry in ledger:
            j=entry['anchor']
            env,history=a.restore(task,entry)
            assert np.array_equal(history,np.load(bank/f'history_{j:03d}.npy'))
            assert np.array_equal(a.diagnostic(task,env),np.load(bank/f'factual_states_{j:03d}.npy')[0])
            env.close()
            inputs=a.info(history[-1],np.load(bank/f'goal_{j:03d}.npy'),entry['warm_actions'],scaler,'cuda')
            full,_=f.call(net,inputs)
            short,_=f.call(net,inputs,horizon=1)
            assert torch.equal(short[:,0],full[:,0])
            ref=w.reference(net,inputs,full)
            assert ref.ndim==3 and ref.shape[:2]==(1,6) and torch.isfinite(ref).all()
            arrays=pre/f'initial_plan_{j:03d}.npz'
            np.savez_compressed(arrays,standardized_plan=full.cpu().numpy().reshape(25,2),reference=ref.cpu().numpy())
            guards.append(dict(anchor=j,all_warm_state_pixels_exact=True,short_full_first_macro_exact=True,
                               official_reference_recursion=True,arrays_sha256=sha(arrays)))
        assert frozen==a.state_hash(net.state_dict())
        save(pre/'controls.json',dict(passed=True,n=48,cpu_cuda=tests,controls=guards,source=source,
             script_sha256=sha(__file__),model_unchanged=True))
        print('Full-deployment new-bank/model CPUCUDA guards',task,seed,'PASS',flush=True)
    except Exception as error:
        save(pre/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise
    for condition in f.CONDITIONS:
        for method in METHODS:
            out=Path(str(prefix)+f'-{condition}-{method}')
            assert not out.exists()
            out.mkdir()
            shutil.copy2(__file__,out/'used.py')
            try:
                save(out/'config.json',dict(task=task,published_train_seed=seed,method=method,condition=condition,budget=100,
                     shift_onset_step=5,source=source,bank_ledger_sha256=sha(bank/'ledger.json'),
                     script_sha256=sha(__file__),source_helper_sha256=sha(s.__file__),actor_helper_sha256=sha(a.__file__),
                     fork_helper_sha256=sha(f.__file__),waypoint_helper_sha256=sha(w.__file__),
                     preflight_sha256=sha(pre/'controls.json'),hardware=torch.cuda.get_device_name(),
                     scope='Full policy/new48goal episodes, three independent released model seeds; 100step budget, causal last5 issued commands. Model references only; hidden evaluator shifts excluded from policy input. Four fixed designs all retained, no router, pretraining split unknown or optimized speed claim.'))
                rows=[]
                for entry in ledger:
                    j=entry['anchor']
                    goal=np.asarray(entry['goal_state'])
                    goal_image=np.load(bank/f'goal_{j:03d}.npy')
                    env,history=a.restore(task,entry)
                    state=a.diagnostic(task,env)
                    assert np.array_equal(history,np.load(bank/f'history_{j:03d}.npy'))
                    assert np.array_equal(state,np.load(bank/f'factual_states_{j:03d}.npy')[0])
                    reached=a.success(task,state,goal)
                    initial_success=reached
                    states,commands,applied=[state],[],[]
                    past=list(entry['warm_actions'])
                    decisions,queries,references=[],[],[]
                    ref=None
                    while not reached and len(commands)<100:
                        step=len(commands)
                        previous_raw=np.asarray(past[-5:],dtype=np.float32)
                        if method=='REFERENCE5' and step%25!=0:
                            assert ref is not None and step%5==0
                            local=(step-cycle_start)//5
                            assert 1<=local<=4
                            torch.cuda.synchronize()
                            tick=f.time.perf_counter()
                            current=net.encode(dict(pixels=a.pixels(env.render()[None,None],'cuda')))['emb'][:,-1]
                            previous=net.action_encoder(torch.as_tensor(scaler.transform(previous_raw.reshape(1,1,10)),device='cuda').float())[:,-1]
                            target=ref[:,local+1]
                            stats=w.query(net,current,target,previous)
                            proposal=stats['map_mean'].cpu().numpy().reshape(5,2)
                            torch.cuda.synchronize()
                            seconds=f.time.perf_counter()-tick
                            queries.append(dict(step=step,cycle_start=cycle_start,current=current.cpu().numpy(),target=target.cpu().numpy(),
                                 previous=previous.cpu().numpy(),mean=stats['map_mean'].cpu().numpy(),log_std=stats['log_std'].cpu().numpy()))
                            kind,width='local-reference',5
                        else:
                            inputs=a.info(env.render().copy(),goal_image,past,scaler,'cuda')
                            planning=1 if method=='GOAL5' else 5
                            tensor,seconds=f.call(net,inputs,horizon=planning)
                            proposal=tensor.cpu().numpy().reshape(5*planning,2)
                            if step==0:
                                with np.load(pre/f'initial_plan_{j:03d}.npz') as original:
                                    assert np.array_equal(proposal[:5],original['standardized_plan'][:5])
                                    if planning==5:assert np.array_equal(proposal,original['standardized_plan'])
                            if method=='REFERENCE5':
                                torch.cuda.synchronize()
                                tick=f.time.perf_counter()
                                ref=w.reference(net,inputs,tensor)
                                torch.cuda.synchronize()
                                reference_seconds=f.time.perf_counter()-tick
                                cycle_start=step
                                references.append(dict(step=step,reference=ref.cpu().numpy(),standardized_plan=proposal,
                                                       reference_generation_seconds=reference_seconds))
                                kind,width='reference-start',5
                            else:
                                reference_seconds=0.
                                kind,width='goal',{'BASE25':25,'GOAL15':15,'GOAL5':5}[method]
                        width=min(width,100-step)
                        issued=scaler.scaler.inverse_transform(proposal)[:width]
                        used=0
                        for command in issued:
                            state,actual,done=f.advance(task,env,command,condition,len(commands))
                            reached=a.success(task,state,goal)
                            assert done==reached
                            commands.append(command)
                            applied.append(actual)
                            past.append(command)
                            states.append(state)
                            used+=1
                            if reached:break
                        decisions.append(dict(start_step=step,kind=kind,planned_execution_steps=width,executed_steps=used,
                             previous_issued_commands=previous_raw.tolist(),standardized_proposal=proposal.tolist(),solver_seconds=seconds,
                             reference_generation_seconds=reference_seconds if kind=='reference-start' else 0.))
                    env.close()
                    path=out/f'trace_{j:03d}.npz'
                    np.savez_compressed(path,states=np.asarray(states),commands=np.asarray(commands).reshape(-1,2),applied_commands=np.asarray(applied).reshape(-1,2))
                    qpath=out/f'queries_{j:03d}.npz'
                    np.savez_compressed(qpath,**({key:np.asarray([q[key] for q in queries]) for key in queries[0]} if queries else dict(step=np.asarray([],dtype=np.int64))))
                    rpath=out/f'references_{j:03d}.npz'
                    np.savez_compressed(rpath,**({key:np.asarray([r[key] for r in references]) for key in references[0]} if references else dict(step=np.asarray([],dtype=np.int64))))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial_success,
                         env_steps=len(commands),decisions=decisions,trace_sha256=sha(path),queries_sha256=sha(qpath),references_sha256=sha(rpath)))
                    save(out/'rows.json',rows)
                assert len(rows)==48 and frozen==a.state_hash(net.state_dict())
                save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True))
                print('Full recovery cell',task,seed,condition,method,'48 COMPLETE',flush=True)
            except Exception as error:
                save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
                raise
    save(Path(str(prefix)+'-pipeline.json'),dict(completed=True,task=task,seed=seed,n=576))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--task',choices=['tworoom','pusht'],required=True)
    p.add_argument('--seed',type=int,choices=[0,42,3072],required=True)
    v=p.parse_args()
    run(v.task,v.seed)
