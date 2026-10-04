"""A10 unchanged native/physical CEM with audited rollout-trained endpoints."""
import argparse
import gc
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import torch
import stable_worldmodel as swm
from gymnasium.vector.utils import batch_space
import predictive_object_rollout as a
import bounded_control as b
from experience_transfer_control_audit import read,sha,save
from fixed_data_train_seed import normalized_pixels,state_hash
r=a.r;ROOT=r.m.ROOT;BANK=ROOT/'20261004-E20-fresh-control-bank48'


def load(geometry,train_seed,device):
    assert read(r.m.WB/'results/E13_20261005_rollout_endpoint_audit.json')['completed']
    a.setup(train_seed);run=ROOT/(a.name(geometry,train_seed)+'-A100');cfg=read(run/'config.json');summary=read(run/'summary.json')
    assert read(run/'complete.json')==dict(completed=True,geometry=geometry,seed=train_seed,updates=2825)
    path=r.m.HF/run.name/'u2825.ckpt';assert sha(path)==summary['checkpoint_sha256'] and cfg['script_sha256']==sha(a.__file__)
    c=torch.load(path,map_location='cpu',weights_only=False);assert (c['train_seed'],c['geometry'],c['arm'],c['steps'])==(train_seed,geometry,'OPEN-ROLLOUT',2825)
    model=r.Model(c['config'],geometry);model.load_state_dict(c['state_dict'],strict=True);model=model.to(device).eval().requires_grad_(False)
    assert model.frozen_hash()==summary['frozen_phi_sha256'] and not set(c['manifest']['base_episodes'])&{v['episode'] for v in read(BANK/'ledger.json')}
    return model,path,c,cfg


@torch.inference_mode()
def preflight(geometry,train_seed,device):
    out=ROOT/f'20261005-E13-rollout-{geometry}-s{train_seed}-{device}-control-preflight';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    for entry in read(BANK/'ledger.json'):
        env,history=b.restore(entry);assert np.array_equal(history,np.load(BANK/f'history_{entry["anchor"]:03d}.npy'))
        assert np.array_equal(env.agent_position.numpy(),np.load(BANK/f'factual_states_{entry["anchor"]:03d}.npy')[0]);env.close()
    model,path,c,cfg=load(geometry,train_seed,device);before=state_hash(model.state_dict())
    current=normalized_pixels(np.load(BANK/'history_000.npy')[-1:],device);goal=normalized_pixels(np.load(BANK/'goal_000.npy')[None],device)
    mean,std=np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std']);physical=np.random.default_rng(113201).uniform(-1,1,(1,37,5,5,2))
    actions=torch.tensor((physical-mean)/std,device=device).float().flatten(-2);cost=r.Cost(model,current,goal,'LOCAL');actual=cost.get_cost({},actions)
    z=model.encode_pixels(current).expand(37,-1);zg=model.encode_pixels(goal)
    for h in range(5):
        ap=model.core['action'](actions[0,:,h:h+1],latent=z[:,None]);pr=model.core['predictor'](z[:,None],ap);z=model.core['projection'](pr[:,0])
    manual=(z-zg).square().sum(-1)[None]
    assert torch.equal(actual,manual) and torch.isfinite(actual).all() and before==state_hash(model.state_dict())
    save(out/'controls.json',dict(passed=True,geometry=geometry,train_seed=train_seed,device=device,all48_initial_pixels_states_exact=True,full_cost_error=0,weights_unchanged=True,checkpoint_sha256=sha(path),script_sha256=sha(__file__)))
    print('Rollout actual deployment preflight',geometry,train_seed,device,'PASS',flush=True)


@torch.inference_mode()
def control(geometry,train_seed):
    for device in ['cpu','cuda']:
        pre=read(ROOT/f'20261005-E13-rollout-{geometry}-s{train_seed}-{device}-control-preflight/controls.json');assert pre['passed'] and pre['script_sha256']==sha(__file__)
    model,path,c,cfg=load(geometry,train_seed,'cuda');mean,std=np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std']);before=state_hash(model.state_dict())
    for interface in ['native','physical']:
        name=f'20261005-E13-rollout-control-{geometry}-{interface}-RTX-s{train_seed}';out=Path('/tmp/latent-wm-runs')/name
        assert not out.exists() and not (ROOT/name).exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
        try:
            save(out/'config.json',dict(geometry=geometry,arm='OPEN-ROLLOUT',train_seed=train_seed,interface=interface,history=1,checkpoint=str(path),checkpoint_sha256=sha(path),source_training_run=a.name(geometry,train_seed)+'-A100',model_training_updates=2825,bank_ledger_sha256=sha(BANK/'ledger.json'),script_sha256=sha(__file__),trainer_sha256=sha(a.__file__),controller_sha256=sha(b.__file__),action_mean=mean.tolist(),action_std=std.tolist(),hardware=torch.cuda.get_device_name(),scope='Known matched BPTT baseline; original48/T1/300samples30elites30iterations/H25 EX25/max100, unchanged planner seed and exact bank. Prior geometry training differs. Not novel method or independent task confirmation.'))
            rows=[]
            for entry in read(BANK/'ledger.json'):
                assert train_seed==r.SEED==c['train_seed']==cfg['train_seed']
                j=entry['anchor'];env,history=b.restore(entry);assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'))
                s=env.agent_position.numpy().copy();assert np.array_equal(s,np.load(BANK/f'factual_states_{j:03d}.npy')[0])
                states=[s];actions=[];decisions=[];reached=bool(np.linalg.norm(s-entry['goal_state'])<16);initial=reached
                goal=normalized_pixels(np.load(BANK/f'goal_{j:03d}.npy')[None],'cuda')
                for decision in range(4):
                    if reached:break
                    current=normalized_pixels(env.render()[None].copy(),'cuda');native=r.Cost(model,current,goal,'LOCAL');planner_seed=105400+j*100+decision
                    if interface=='physical':
                        class Physical:
                            def get_cost(self,info,commands):return native.get_cost(info,((commands.reshape(1,-1,5,5,2)-commands.new_tensor(mean))/commands.new_tensor(std)).flatten(-2).float())
                        chosen,_=b.bounded_cem(Physical(),planner_seed)
                    else:
                        solver=swm.solver.CEMSolver(native,num_samples=300,topk=30,n_steps=30,device='cuda',seed=planner_seed)
                        solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True))
                        chosen=solver.solve({})['actions'][0].numpy().reshape(25,2)*std+mean
                    steps=0
                    for issued in chosen:
                        _,_,done,truncated,_=env.step(issued.astype(np.float32));assert not truncated
                        s=env.agent_position.numpy().copy();reached=bool(np.linalg.norm(s-entry['goal_state'])<16);assert bool(done)==reached
                        states.append(s);actions.append(issued);steps+=1
                        if reached:break
                    decisions.append(dict(decision=decision,executed_steps=steps,planner_seed=planner_seed))
                env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial,env_steps=len(actions),decisions=decisions,trace_sha256=sha(trace)))
                save(out/'rows.json',rows);print('Rollout control',geometry,train_seed,interface,j,int(reached),flush=True)
            assert before==state_hash(model.state_dict())
            save(out/'summary.json',[dict(goal_span=v,n=24,successes=sum(row['success'] for row in rows if row['goal_span']==v)) for v in [25,75]])
            save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,ROOT/name)
        except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,ROOT/name);raise


def queue(train_seed):
    out=ROOT/f'20261005-E13-rollout-control-pipeline-s{train_seed}';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        for geometry in ['PRED','VALUE']:
            for device in ['cpu','cuda']:subprocess.run([sys.executable,'-u',__file__,'preflight','--geometry',geometry,'--seed',str(train_seed),'--device',device],check=True)
            subprocess.run([sys.executable,'-u',__file__,'control','--geometry',geometry,'--seed',str(train_seed)],check=True)
        save(out/'complete.json',dict(completed=True,train_seed=train_seed,episodes=192))
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','control','queue']);p.add_argument('--geometry',choices=['PRED','VALUE']);p.add_argument('--seed',type=int,choices=[0,1,2],required=True);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');v=p.parse_args();torch.set_num_threads(4)
    if v.mode=='queue':queue(v.seed)
    elif v.mode=='preflight':preflight(v.geometry,v.seed,v.device)
    else:control(v.geometry,v.seed)
