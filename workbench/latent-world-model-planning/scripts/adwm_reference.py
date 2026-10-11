"""E01/E20: complete published AD-WM reference in an isolated namespace."""
import gc
import inspect
import json
import shutil
import sys
from pathlib import Path
import numpy as np
import torch

WB = Path(__file__).resolve().parents[1]
REPO = WB/'vendor/ad-wm'
sys.path.insert(0, str(REPO))
from jepa import JEPA
import module
assert Path(inspect.getfile(JEPA)).resolve()==REPO/'jepa.py'
assert Path(module.__file__).resolve()==REPO/'module.py'
from lewm_pilot import NativeCost, native_control, pixels, digest, dump, now
from fixed_data_train_seed import state_hash
import bounded_control as b
import effect_transfer as transfer
import effect_training as effects
assert Path(inspect.getfile(JEPA)).resolve()==REPO/'jepa.py'

ROOT = Path('/home/xiang/.cache/latent-wm-results')
BANK = Path('/tmp/latent-wm-runs/20261004-E20-legal-effect-bank44')
FRESH = Path('/tmp/latent-wm-runs/20261004-E20-fresh-control-bank48')


def load(task):
    assets=json.loads((ROOT/'20261004-E01-adwm-cpu-preflight-retry1/latent-adwm-assets.json').read_text())
    entry=next(r for r in assets['files'] if r['task']==task and r['filename'].endswith('ckpt'))
    assert digest(entry['path'])==entry['sha256']
    model=torch.load(entry['path'],map_location='cpu',weights_only=False)
    assert type(model) is JEPA and model.residual_target and model.has_inverse_head() and model.mi_posterior_head is not None
    assert len(model.state_dict())==321
    norm=np.load(ROOT/f'20261002-{task}-native-s0/action_normalization.npz')
    return model.cuda().eval().requires_grad_(False), norm['mean'],norm['std'],entry


@torch.inference_mode()
def run():
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    torch.set_num_threads(4)
    out=Path('/tmp/latent-wm-runs/20261004-E01-adwm-reference-RTX-s3072')
    assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'adwm_reference_used.py')
    try:
        config=dict(code_commit='7c27ebfdc4a2ba8e5a16268f2e4aa852fda72144',script_sha256=digest(__file__),
            helper_sha256=digest(b.__file__),training_seed=3072,hardware=torch.cuda.get_device_name(),
            scope='complete published reference; pretraining data unknown and unmatched; new development, not paper numeric replication')
        dump(out/'config.json',config)
        model,mean,std,entry=load('tworoom');weights=state_hash(model.state_dict())
        images,actions,physical,_=effects.load_bank(BANK)
        offline=effects.audit_candidates(model,images,actions,physical,mean,std);dump(out/'tworoom_queries.json',offline)
        h=pixels(images[32,0,:3])[None];g=pixels(images[32,2,-1][None])[None]
        p=torch.as_tensor((actions[32,0,:10]-mean)/std,device='cuda').float().reshape(1,2,10)
        dump(out/'tworoom_native_parity.json',native_control(model,h,g,p));dump(out/'tworoom_source.json',entry)
        ledger=json.loads((FRESH/'ledger.json').read_text());rows=[]
        for interface in ['physical','native']:
            for e in ledger:
                j=e['anchor'];env,history=b.restore(e)
                assert np.array_equal(history,np.load(FRESH/f'history_{j:03d}.npy'))
                history=list(history);past=list(e['warm_actions']);controls=[];states=[env.agent_position.numpy().copy()];times=[]
                success=bool(np.linalg.norm(states[0]-e['goal_state'])<16)
                goal=pixels(np.load(FRESH/f'goal_{j:03d}.npy')[None])[None]
                for decision in range(4):
                    if success:break
                    tick=now();h=pixels(np.asarray(history[-3:]))[None]
                    p=torch.as_tensor((np.asarray(past[-10:])-mean)/std,device='cuda').float().reshape(1,2,10)
                    native=NativeCost(model,h,goal,p);seed=105400+j*100+decision
                    if interface=='physical':
                        class Cost:
                            def get_cost(self,info,a):
                                return native.get_cost(info,((a.reshape(1,-1,5,5,2)-a.new_tensor(mean))/a.new_tensor(std)).flatten(-2).float())
                        chosen,_=b.bounded_cem(Cost(),seed)
                        assert (np.abs(chosen)<=1).all()
                    else:
                        solver=swm.solver.CEMSolver(native,num_samples=300,topk=30,n_steps=30,device='cuda',seed=seed)
                        solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,
                            config=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True))
                        chosen=solver.solve({})['actions'][0].numpy().reshape(25,2)*std+mean
                    times.append(now()-tick)
                    for t,a in enumerate(chosen):
                        _,_,done,truncated,_=env.step(a.astype(np.float32));past.append(a);controls.append(a);states.append(env.agent_position.numpy().copy())
                        if (t+1)%5==0:history.append(env.render().copy())
                        if done or truncated:success=bool(done);break
                    if done or truncated:break
                env.close();trace=out/f'{interface}_{j:03d}.npz'
                np.savez_compressed(trace,actions=np.asarray(controls).reshape(-1,2),states=np.asarray(states))
                rows.append(dict(interface=interface,anchor=j,episode=e['episode'],goal_span=e['goal_span'],success=success,
                    env_steps=len(controls),planning_seconds=times,trace_sha256=digest(trace)))
                dump(out/'rows.json',rows);print('ADWM reference',interface,j,int(success),flush=True)
        assert weights==state_hash(model.state_dict())
        del model;gc.collect();torch.cuda.empty_cache()
        model,mean,std,entry=load('pusht');weights=state_hash(model.state_dict())
        images,actions,physical=transfer.load_bank(BANK)
        offline=transfer.queries(model,images,actions,physical,mean,std,'cuda');dump(out/'pusht_queries.json',offline)
        h=pixels(images[32,0,:3])[None];g=pixels(images[32,2,-1][None])[None]
        p=torch.as_tensor((actions[32,0,:10]-mean)/std,device='cuda').float().reshape(1,2,10)
        dump(out/'pusht_native_parity.json',native_control(model,h,g,p));dump(out/'pusht_source.json',entry)
        assert weights==state_hash(model.state_dict())
        dump(out/'summary.json',[dict(interface=interface,goal_span=span,n=sum(r['interface']==interface and r['goal_span']==span for r in rows),
            successes=sum(r['success'] for r in rows if r['interface']==interface and r['goal_span']==span)) for interface in ['physical','native'] for span in [25,75]])
        dump(out/'complete.json',dict(completed=True,navigation_episodes=96,candidate_queries_per_task=12,models_unchanged=True))
        shutil.copytree(out,ROOT/out.name)
    except Exception as error:
        dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':run()
