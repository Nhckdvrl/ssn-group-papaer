"""E18 F0: fixed full model/plan, feedback after 5 or 1 actual primitives."""
import argparse
import shutil
import time
import numpy as np
import torch
import intact_published_control_v3 as a
from experience_transfer_control_audit import ROOT,read,save,sha


@torch.inference_mode()
def run(task):
    a.setup();net,scaler,source=a.source(task,'cuda');initial=a.state_hash(net.state_dict());bank=a.bank(task);ledger=read(bank/'ledger.json')
    pre=ROOT/f'20261005-E18-intact-feedback-{task}-preflight';assert not pre.exists();pre.mkdir();shutil.copy2(__file__,pre/'used.py')
    try:
        for device in ['cpu','cuda']:
            old=read(ROOT/f'20261005-E01-intact-v3-{task}-{device}-preflight/controls.json');assert old['passed'] and old['script_sha256']==sha(a.__file__) and old['source']==source
        for entry in ledger:
            env,history=a.restore(task,entry);j=entry['anchor'];assert np.array_equal(history,np.load(bank/f'history_{j:03d}.npy')) and np.array_equal(a.diagnostic(task,env),np.load(bank/f'factual_states_{j:03d}.npy')[0]);env.close()
        entry=ledger[0];history=np.load(bank/'history_000.npy');goal_image=np.load(bank/'goal_000.npy');records=[]
        baseline=read(ROOT/f'20261005-E01-intact-v3-{task}-native-control/rows.json')
        for device in ['cpu','cuda']:
            model,processor,meta=a.source(task,device);before=a.state_hash(model.state_dict());assert meta==source
            inp=a.info(history[-1],goal_image,entry['warm_actions'],processor,device);result=model.get_action(inp,horizon=5).cpu().numpy().reshape(25,2)
            assert np.isfinite(result).all()
            if device=='cpu':reference=result
            else:np.testing.assert_allclose(result,reference,atol=2e-4,rtol=1e-5)
            # Native full-plan calls match the original actual controller.
            assert np.array_equal(result,np.asarray(baseline[0]['decisions'][0]['standardized_proposal'],dtype=np.float32)) if device=='cuda' else True
            assert a.state_hash(model.state_dict())==before
            for execution in [5,1]:assert result[:execution].shape==(execution,2)
            records.append(dict(device=device,passed=True,all48warm_exact=True,full25_plan=True,execution_prefixes=[5,1],model_unchanged=True))
        save(pre/'controls.json',dict(passed=True,task=task,source=source,script_sha256=sha(__file__),helper_sha256=sha(a.__file__),records=records))
        print('Full INTACT feedback preflight',task,'PASS',flush=True)
    except Exception as error:save(pre/'failure.json',dict(type=type(error).__name__,message=str(error)));raise
    for execution in [5,1]:
        out=ROOT/f'20261005-E18-intact-feedback-{task}-EX{execution}';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
        try:
            save(out/'config.json',dict(task=task,execution_steps=execution,planning_steps=25,budget=100,history_frames=1,train_seed=0,source=source,script_sha256=sha(__file__),helper_sha256=sha(a.__file__),bank_ledger_sha256=sha(bank/'ledger.json'),hardware=torch.cuda.get_device_name(),scope='Same full published joint model, raw native actions, same48 starts/targets/budget; shorter commitment with actual feedback, no retraining or router. Full25plan recomputed then prefix executed, not optimal cheap implementation. Published pretraining/data unmatched; one trainseed, no novelty claim.'))
            rows=[]
            for entry in ledger:
                j=entry['anchor'];goal=np.asarray(entry['goal_state']);env,history=a.restore(task,entry);state=a.diagnostic(task,env)
                assert np.array_equal(history,np.load(bank/f'history_{j:03d}.npy')) and np.array_equal(state,np.load(bank/f'factual_states_{j:03d}.npy')[0])
                reached=a.success(task,state,goal);initial_success=reached;states=[state];actions=[];past=list(entry['warm_actions']);decisions=[];goal_image=np.load(bank/f'goal_{j:03d}.npy')
                for decision in range(100//execution):
                    if reached:break
                    inp=a.info(env.render().copy(),goal_image,past,scaler,'cuda');previous=np.asarray(past[-5:],dtype=np.float32)
                    torch.cuda.synchronize();tick=time.perf_counter();proposal=net.get_action(inp,horizon=5).cpu().numpy().reshape(25,2);torch.cuda.synchronize();elapsed=time.perf_counter()-tick
                    if decision==0:assert np.array_equal(proposal,np.asarray(baseline[j]['decisions'][0]['standardized_proposal'],dtype=np.float32))
                    issued=scaler.scaler.inverse_transform(proposal)[:execution];steps=0
                    for command in issued:
                        _,_,done,truncated,_=env.step(command.astype(np.float32));assert not truncated
                        state=a.diagnostic(task,env);reached=a.success(task,state,goal);assert bool(done)==reached
                        states.append(state);actions.append(command);past.append(command.astype(np.float32));steps+=1
                        if reached:break
                    decisions.append(dict(decision=decision,executed_steps=steps,previous_executed_actions=previous.tolist(),standardized_proposal=proposal.tolist(),solver_seconds=elapsed,out_of_bounds_components=int((np.abs(issued[:steps])>1).sum())))
                env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial_success,env_steps=len(actions),decisions=decisions,trace_sha256=sha(trace)))
                save(out/'rows.json',rows);print('INTACT feedback control',task,execution,j,int(reached),flush=True)
            assert initial==a.state_hash(net.state_dict());save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True))
        except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--task',choices=['tworoom','pusht'],required=True);run(p.parse_args().task)
