"""Fixed-endpoint Push module controls on the unchanged 48-task development bank."""
import argparse
import json
import shutil
from pathlib import Path
import adwm_reference as ad  # Same explicit namespace as the original Push matrix.
import effect_transfer as transfer
import pusht_module_learning as training
from pusht_fresh_control import BANK, ROOT, HF, restore, diagnostic, success
import bounded_control as b
import numpy as np
import torch
import stable_worldmodel as swm
from gymnasium.vector.utils import batch_space
from lewm_pilot import NativeCost, native_control, pixels, architecture
from fixed_data_train_seed import state_hash


@torch.inference_mode()
def evaluate(arm):
    torch.set_num_threads(4)
    source = f'20261005-E20-pusht-module-{arm}-A100-s0'
    run = ROOT/source
    assert json.loads((run/'complete.json').read_text()) == dict(completed=True, arm=arm, seed=0, updates=2000)
    assert not (run/'failure.json').exists()
    cfg = json.loads((run/'config.json').read_text())
    assert cfg['script_sha256'] == b.sha(training.__file__) and cfg['source_sha256'] == transfer.SOURCE_SHA
    checkpoint = HF/source/'u2000.ckpt'
    assert b.sha(checkpoint) == next(v['checkpoint_sha256'] for v in json.loads((run/'summary.json').read_text()) if v['updates']==2000)
    c = torch.load(checkpoint, map_location='cpu', weights_only=False)
    assert c['steps']==2000 and c['module_arm']==arm and len(c['state_dict'])==303
    model=architecture(c['config']); model.load_state_dict(c['state_dict'], strict=True); model=model.cuda().eval().requires_grad_(False)
    assert not model.residual_target
    mean, std=np.asarray(c['manifest']['action_mean']), np.asarray(c['manifest']['action_std'])
    weights=state_hash(model.state_dict())
    assert cfg['frozen_sha256']==state_hash(training.frozen(model,arm))
    ledger=json.loads((BANK/'ledger.json').read_text())
    assert len(ledger)==48 and json.loads((BANK/'complete.json').read_text())['all_warm_and_replay_exact']
    for interface in ['native','physical']:
        out=Path('/tmp/latent-wm-runs')/f'20261005-E20-pusht-module-control-{arm}-{interface}-RTX-s0'
        assert not out.exists() and not (ROOT/out.name).exists(); out.mkdir(); shutil.copy2(__file__,out/'pusht_module_control_used.py')
        try:
            b.save(out/'config.json',dict(arm=arm,interface=interface,source_training_run=source,checkpoint=str(checkpoint),checkpoint_sha256=b.sha(checkpoint),
                bank_ledger_sha256=b.sha(BANK/'ledger.json'),script_sha256=b.sha(__file__),controller_sha256=b.sha(b.__file__),trainer_sha256=b.sha(training.__file__),
                action_mean=mean.tolist(),action_std=std.tolist(),hardware=torch.cuda.get_device_name(),
                scope='same 48 actual-continuation tasks and original Push control protocol; one transfer seed; pretraining split unknown; inactive module parameters and buffers fixed; not novel method confirmation'))
            rows=[]
            for entry in ledger:
                j=entry['anchor']; goal=np.asarray(entry['goal_state']); env,history=restore(entry,goal)
                assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'))
                assert np.array_equal(diagnostic(env),np.load(BANK/f'factual_states_{j:03d}.npy')[0])
                history=list(history); past=list(entry['warm_actions']); states=[diagnostic(env)]; commands=[]; decisions=[]
                reached=success(env._get_obs(),goal); goal_image=pixels(np.load(BANK/f'goal_{j:03d}.npy')[None])[None]
                for decision in range(4):
                    if reached: break
                    h=pixels(np.asarray(history[-3:]))[None]
                    pa=torch.as_tensor((np.asarray(past[-10:])-mean)/std,device='cuda').float().reshape(1,2,10)
                    native=NativeCost(model,h,goal_image,pa)
                    if not (out/'native_parity.json').exists(): b.save(out/'native_parity.json',native_control(model,h,goal_image,pa))
                    seed=109400+j*100+decision
                    if interface=='physical':
                        class Cost:
                            def get_cost(self,info,actions):
                                return native.get_cost(info,((actions.reshape(1,-1,5,5,2)-actions.new_tensor(mean))/actions.new_tensor(std)).flatten(-2).float())
                        chosen,_=b.bounded_cem(Cost(),seed); assert (np.abs(chosen)<=1).all()
                    else:
                        solver=swm.solver.CEMSolver(native,num_samples=300,topk=30,n_steps=30,device='cuda',seed=seed)
                        solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,
                            config=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True))
                        chosen=solver.solve({})['actions'][0].numpy().reshape(25,2)*std+mean
                    count=0
                    for t,action in enumerate(chosen):
                        _,_,done,truncated,_=env.step(action.astype(np.float32)); assert not truncated
                        reached=success(env._get_obs(),goal); assert bool(done)==reached
                        commands.append(action); past.append(action); states.append(diagnostic(env)); count+=1
                        if (t+1)%5==0: history.append(env.render().copy())
                        if reached: break
                    decisions.append(dict(decision=decision,executed_steps=count,issued_out_of_bounds_components=int((np.abs(chosen[:count])>1).sum())))
                env.close(); trace=out/f'trace_{j:03d}.npz'; np.savez_compressed(trace,actions=np.asarray(commands).reshape(-1,2),states=np.asarray(states))
                rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=success(states[0][:7],goal),env_steps=len(commands),decisions=decisions,trace_sha256=b.sha(trace)))
                b.save(out/'rows.json',rows); print('Push module control',arm,interface,j,int(reached),flush=True)
            assert weights==state_hash(model.state_dict())
            b.save(out/'summary.json',[dict(goal_span=v,n=24,successes=sum(r['success'] for r in rows if r['goal_span']==v)) for v in [25,75]])
            b.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True)); shutil.copytree(out,ROOT/out.name)
        except Exception as error:
            b.save(out/'failure.json',dict(type=type(error).__name__,message=str(error))); shutil.copytree(out,ROOT/out.name); raise


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--arm',required=True,choices=training.ARMS); evaluate(p.parse_args().arm)
