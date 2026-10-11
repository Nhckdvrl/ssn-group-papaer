"""All fixed predictive-object endpoints, two interfaces, unchanged actual task bank."""
import argparse
import gc
import json
import shutil
import time
from pathlib import Path
import numpy as np
import torch
import stable_worldmodel as swm
from gymnasium.vector.utils import batch_space
import predictive_object_repeat as r
import bounded_control as b
from fixed_data_train_seed import normalized_pixels,state_hash

ROOT=r.m.ROOT;BANK=ROOT/'20261004-E20-fresh-control-bank48'


@torch.inference_mode()
def evaluate(geometry,train_seed):
    r.set_seed(train_seed)
    torch.set_num_threads(4);ledger=json.loads((BANK/'ledger.json').read_text())
    assert json.loads((BANK/'complete.json').read_text())['all_factual_exact'] and len(ledger)==48
    for arm in r.ARMS:
        name=f'20261005-E13-object-{geometry}-{arm}-A100-s{train_seed}';source=ROOT/name
        while not (source/'complete.json').exists():
            if (source/'failure.json').exists() or (ROOT/f'20261005-E13-object-{geometry}-pipeline-s{train_seed}'/'failure.json').exists():raise RuntimeError(f'Locked endpoint or precontrol failed {name}')
            print('waiting object endpoint',name,flush=True);time.sleep(30)
        assert json.loads((source/'complete.json').read_text())==dict(completed=True,geometry=geometry,arm=arm,seed=train_seed,updates=2825)
        cfg=json.loads((source/'config.json').read_text());summary=json.loads((source/'summary.json').read_text())
        assert cfg['script_sha256']==b.sha(r.__file__)
        checkpoint=r.m.HF/name/'u2825.ckpt';assert b.sha(checkpoint)==summary['checkpoint_sha256']
        c=torch.load(checkpoint,map_location='cpu',weights_only=False)
        assert c['steps']==2825 and c['arm']==arm and c['geometry']==geometry and c['train_seed']==train_seed
        model=r.Model(c['config'],geometry);model.load_state_dict(c['state_dict'],strict=True);model=model.cuda().eval().requires_grad_(False)
        assert model.frozen_hash()==summary['frozen_phi_sha256']==cfg['feature_metadata']['frozen_phi_sha256']
        assert not set(c['manifest']['base_episodes'])&{v['episode'] for v in ledger}
        mean,std=np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std']);initial=state_hash(model.state_dict())
        for interface in ['native','physical']:
            assert r.SEED==train_seed==c['train_seed']==cfg['train_seed']
            out=Path('/tmp/latent-wm-runs')/f'20261005-E13-object-repeat-v2-control-{geometry}-{arm}-{interface}-RTX-s{train_seed}'
            assert not out.exists() and not (ROOT/out.name).exists();out.mkdir();shutil.copy2(__file__,out/'predictive_object_control_used.py')
            try:
                b.save(out/'config.json',dict(geometry=geometry,arm=arm,train_seed=train_seed,interface=interface,history=1,checkpoint=str(checkpoint),checkpoint_sha256=b.sha(checkpoint),
                    source_training_run=name,model_training_updates=2825,bank_ledger_sha256=b.sha(BANK/'ledger.json'),script_sha256=b.sha(__file__),
                    trainer_sha256=b.sha(r.__file__),controller_sha256=b.sha(b.__file__),action_mean=mean.tolist(),action_std=std.tolist(),hardware=torch.cuda.get_device_name(),
                    scope='same48 tasks, both objects T1, 300/30/30 H25 EX25 100step; head capacity/init/data matched; fixed geometry priors budgets differ; old LeWM uses H3; development and no speedup or novelty confirmation'))
                rows=[]
                for entry in ledger:
                    assert train_seed==r.SEED==cfg['train_seed']
                    j=entry['anchor'];env,history=b.restore(entry)
                    assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'))
                    state=env.agent_position.numpy().copy();assert np.array_equal(state,np.load(BANK/f'factual_states_{j:03d}.npy')[0])
                    states=[state];commands=[];decisions=[];reached=bool(np.linalg.norm(state-entry['goal_state'])<16);initial_success=reached
                    goal=normalized_pixels(np.load(BANK/f'goal_{j:03d}.npy')[None],'cuda')
                    for decision in range(4):
                        if reached:break
                        current=normalized_pixels(env.render()[None].copy(),'cuda');native=r.Cost(model,current,goal,arm)
                        planner_seed=105400+j*100+decision
                        if interface=='physical':
                            class Physical:
                                def get_cost(self,info,a):return native.get_cost(info,((a.reshape(1,-1,5,5,2)-a.new_tensor(mean))/a.new_tensor(std)).flatten(-2).float())
                            chosen,_=b.bounded_cem(Physical(),planner_seed)
                        else:
                            solver=swm.solver.CEMSolver(native,num_samples=300,topk=30,n_steps=30,device='cuda',seed=planner_seed)
                            solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True))
                            chosen=solver.solve({})['actions'][0].numpy().reshape(25,2)*std+mean
                        count=0
                        for a in chosen:
                            _,_,done,truncated,_=env.step(a.astype(np.float32));assert not truncated
                            state=env.agent_position.numpy().copy();reached=bool(np.linalg.norm(state-entry['goal_state'])<16);assert bool(done)==reached
                            states.append(state);commands.append(a);count+=1
                            if reached:break
                        decisions.append(dict(decision=decision,executed_steps=count))
                    env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(commands).reshape(-1,2))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial_success,env_steps=len(commands),decisions=decisions,trace_sha256=b.sha(trace)))
                    b.save(out/'rows.json',rows);print('object control',geometry,arm,interface,j,int(reached),flush=True)
                assert initial==state_hash(model.state_dict())
                b.save(out/'summary.json',[dict(goal_span=v,n=24,successes=sum(row['success'] for row in rows if row['goal_span']==v)) for v in [25,75]])
                b.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,ROOT/out.name)
            except Exception as error:
                b.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,ROOT/out.name);raise
        del model,c;gc.collect();torch.cuda.empty_cache()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--geometry',required=True,choices=r.g.GEOMETRIES);p.add_argument('--seed',required=True,type=int,choices=[1,2]);args=p.parse_args();evaluate(args.geometry,args.seed)
