"""A12 T1 Fast costs with original Push native/physical CEM and full replay."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import torch
import stable_worldmodel as swm
from gymnasium.vector.utils import batch_space
import predictive_object_pusht as a
import bounded_control as b
from experience_transfer_control_audit import ROOT,WB,read,save,sha
from fixed_data_train_seed import normalized_pixels,state_hash
p=a.component.p;r=a.r;BANK=p.BANK


def load(arm,device):
    assert read(WB/'results/E13_20261005_pusht_object_endpoint_audit.json')['completed']
    source=ROOT/a.name(arm);cfg=read(source/'config.json');summary=read(source/'summary.json')
    path=a.HF/a.name(arm)/'u2825.ckpt';assert sha(path)==summary['checkpoint_sha256'] and cfg['script_sha256']==sha(a.__file__)
    c=torch.load(path,map_location='cpu',weights_only=False);assert (c['arm'],c['steps'],c['train_seed'])==(arm,2825,0)
    net=a.Model();net.load_state_dict(c['state_dict'],strict=True);net=net.to(device).eval().requires_grad_(False)
    assert net.frozen_hash()==summary['frozen_phi_sha256']
    return net,path,c,cfg


@torch.inference_mode()
def preflight(arm,device):
    out=ROOT/f'20261005-E13-pusht-object-{arm}-{device}-control-preflight';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        for entry in read(BANK/'ledger.json'):
            env,history=p.restore(entry,np.asarray(entry['goal_state']));j=entry['anchor']
            assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'))
            assert np.array_equal(p.diagnostic(env),np.load(BANK/f'factual_states_{j:03d}.npy')[0]);env.close()
        net,path,c,cfg=load(arm,device);before=state_hash(net.state_dict())
        current=normalized_pixels(np.load(BANK/'history_000.npy')[-1:],device);goal=normalized_pixels(np.load(BANK/'goal_000.npy')[None],device)
        mean,std=np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std'])
        physical=np.random.default_rng(113201).uniform(-1,1,(1,37,5,5,2));actions=torch.tensor((physical-mean)/std,device=device).float().flatten(-2)
        mode='DIRECT' if arm=='DIRECT' else 'LOCAL';cost=r.Cost(net,current,goal,mode);actual=cost.get_cost({},actions)
        z=net.encode_pixels(current).expand(37,-1);zg=net.encode_pixels(goal)
        if arm=='DIRECT':
            ap=net.core['action'](actions[0],latent=z[:,None]);pr=net.core['predictor'](z[:,None],ap)
            z=net.core['projection'](pr.flatten(0,1)).reshape(pr.shape)[:,-1]
        else:
            for h in range(5):
                ap=net.core['action'](actions[0,:,h:h+1],latent=z[:,None]);pr=net.core['predictor'](z[:,None],ap);z=net.core['projection'](pr[:,0])
        manual=(z-zg).square().sum(-1)[None]
        assert torch.equal(actual,manual) and torch.isfinite(actual).all() and before==state_hash(net.state_dict())
        save(out/'controls.json',dict(passed=True,arm=arm,device=device,checkpoint_sha256=sha(path),full_cost_error=0,all48_full25D_warm_pixels_exact=True,weights_unchanged=True,script_sha256=sha(__file__),trainer_sha256=sha(a.__file__)))
        print('Push prediction actual deployment preflight',arm,device,'PASS',flush=True)
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


@torch.inference_mode()
def control(arm):
    for device in ['cpu','cuda']:
        c=read(ROOT/f'20261005-E13-pusht-object-{arm}-{device}-control-preflight/controls.json');assert c['passed'] and c['script_sha256']==sha(__file__)
    net,path,c,cfg=load(arm,'cuda');before=state_hash(net.state_dict());mean,std=np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std'])
    for interface in ['native','physical']:
        name=f'20261005-E13-pusht-object-control-{arm}-{interface}-RTX-s0';out=Path('/tmp/latent-wm-runs')/name
        assert not out.exists() and not (ROOT/name).exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
        try:
            save(out/'config.json',dict(task='pusht',arm=arm,train_seed=0,interface=interface,budget=100,history=1,executed_steps_per_decision=25,checkpoint=str(path),checkpoint_sha256=sha(path),geometry_source_sha256=a.t.SOURCE_SHA,source_training_run=a.name(arm),model_training_updates=2825,bank_ledger_sha256=sha(BANK/'ledger.json'),script_sha256=sha(__file__),trainer_sha256=sha(a.__file__),controller_sha256=sha(b.__file__),restore_sha256=sha(p.__file__),action_mean=mean.tolist(),action_std=std.tolist(),hardware=torch.cuda.get_device_name(),scope='All same48 development tasks, T1 same Fast capacity and endpoints; known prediction objects, one headseed and unknown published phi pretraining. Native normalized unbounded vs physical bounded CEM changes proposal coordinates as well as bounds. Published H3 and stepwise goal-policy references differ, not pure history causality, numerical paper reproduction or novelty.'))
            rows=[]
            for entry in read(BANK/'ledger.json'):
                j=entry['anchor'];goal=np.asarray(entry['goal_state']);env,history=p.restore(entry,goal)
                assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'))
                s=p.diagnostic(env);assert np.array_equal(s,np.load(BANK/f'factual_states_{j:03d}.npy')[0])
                reached=p.success(s[:7],goal);initial=reached;states=[s];actions=[];decisions=[]
                goal_image=normalized_pixels(np.load(BANK/f'goal_{j:03d}.npy')[None],'cuda')
                for decision in range(4):
                    if reached:break
                    current=normalized_pixels(env.render()[None].copy(),'cuda');native=r.Cost(net,current,goal_image,'DIRECT' if arm=='DIRECT' else 'LOCAL');planner_seed=109400+j*100+decision
                    if interface=='physical':
                        class Physical:
                            def get_cost(self,info,commands):return native.get_cost(info,((commands.reshape(1,-1,5,5,2)-commands.new_tensor(mean))/commands.new_tensor(std)).flatten(-2).float())
                        chosen,_=b.bounded_cem(Physical(),planner_seed)
                    else:
                        solver=swm.solver.CEMSolver(native,num_samples=300,topk=30,n_steps=30,device='cuda',seed=planner_seed)
                        solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True))
                        chosen=solver.solve({})['actions'][0].numpy().reshape(25,2)*std+mean
                    steps=0;outside=0
                    for issued in chosen:
                        _,_,done,truncated,_=env.step(issued.astype(np.float32));assert not truncated
                        s=p.diagnostic(env);reached=p.success(s[:7],goal);assert bool(done)==reached
                        states.append(s);actions.append(issued);steps+=1;outside+=int((np.abs(issued)>1).sum())
                        if reached:break
                    decisions.append(dict(decision=decision,executed_steps=steps,planner_seed=planner_seed,issued_out_of_bounds_components=outside))
                env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial,env_steps=len(actions),decisions=decisions,trace_sha256=sha(trace)))
                save(out/'rows.json',rows);print('Push prediction control',arm,interface,j,int(reached),flush=True)
            assert before==state_hash(net.state_dict())
            save(out/'summary.json',[dict(goal_span=span,n=24,successes=sum(row['success'] for row in rows if row['goal_span']==span)) for span in [25,75]])
            save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,ROOT/name)
        except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,ROOT/name);raise


def queue(arm):
    out=ROOT/f'20261005-E13-pusht-object-control-{arm}-pipeline';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        for device in ['cpu','cuda']:subprocess.run([sys.executable,'-u',__file__,'preflight','--arm',arm,'--device',device],check=True)
        subprocess.run([sys.executable,'-u',__file__,'control','--arm',arm],check=True)
        save(out/'complete.json',dict(completed=True,arm=arm,episodes=96))
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['queue','preflight','control']);parser.add_argument('--arm',choices=a.ARMS,required=True);parser.add_argument('--device',choices=['cpu','cuda'],default='cpu');v=parser.parse_args();torch.set_num_threads(4)
    if v.mode=='queue':queue(v.arm)
    elif v.mode=='preflight':preflight(v.arm,v.device)
    else:control(v.arm)
