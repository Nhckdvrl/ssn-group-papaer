"""G2 actual 11-observation warm history and every-step real feedback control."""
import argparse
import gc
import shutil
import subprocess
import sys
from pathlib import Path
import gymnasium as gym
import numpy as np
import torch
import goal_policy_control as n
import goal_policy_history as h
import effect_transfer as t
import pusht_fresh_control as p
from fixed_data_train_seed import normalized_pixels,state_hash
g=h.g


def bank(task):return g.ROOT/('20261004-E20-fresh-control-bank48' if task=='nav' else '20261005-E20-pusht-fresh-control-bank48')
def state(env,task):return env.agent_position.numpy().copy() if task=='nav' else p.diagnostic(env)
def success(s,goal,task):return bool(np.linalg.norm(s-goal)<16) if task=='nav' else p.success(s[:7],goal)


def warm(entry,task):
    env=gym.make('swm/TwoRoom-v1' if task=='nav' else 'swm/PushT-v1',render_mode='rgb_array').unwrapped
    env.reset(seed=entry['reset_seed']);env._set_state(np.asarray(entry['initial_state']));env._set_goal_state(np.asarray(entry['goal_state']))
    images=[env.render().copy()]
    for action in entry['warm_actions']:
        env.step(np.asarray(action,dtype=np.float32));images.append(env.render().copy())
    images=np.asarray(images);j=entry['anchor'];b=bank(task)
    assert images.shape==(11,224,224,3) and np.array_equal(images[[0,5,10]],np.load(b/f'history_{j:03d}.npy'))
    assert np.array_equal(state(env,task),np.load(b/f'factual_states_{j:03d}.npy')[0])
    return env,images


def load(task,arm,device):
    run=g.ROOT/f'20261005-E14-history-{task}-{arm}-RTX-s0';cfg=g.read(run/'config.json');path=g.HF/run.name/'epoch50.ckpt'
    assert g.read(run/'complete.json')==dict(completed=True,task=task,arm=arm,epochs=50)
    assert cfg['script_sha256']==g.sha(h.__file__) and g.sha(path)==g.read(run/'summary.json')['checkpoint_sha256']
    c=torch.load(path,map_location='cpu',weights_only=False);net=h.model(device);net.load_state_dict(c['state_dict'],strict=True);net.eval().requires_grad_(False)
    if task=='nav':
        phi,unused,priorcfg,_=n.load('PRED',0,'GCBC-MATCHED',device);del unused
        assert priorcfg['feature_metadata']['source_sha256']==cfg['feature_metadata']['source_sha256']
    else:
        phi,_,_,_,_=t.load_source(device);phi.eval().requires_grad_(False)
        assert state_hash(phi.state_dict())==cfg['feature_metadata']['frozen_model_sha256']
    return phi,net,path,cfg


def inputs(history,zgoal,arm):
    assert history.shape==(11,192)
    current=history[[-11,-6,-1]] if arm=='TRUE-HISTORY' else history[-1:].expand(3,-1)
    return current.reshape(1,576),zgoal.repeat(1,3)


@torch.inference_mode()
def preflight(task,device):
    assert g.read(g.WB/'results/E14_20261005_history_policy_endpoint_audit.json')['completed']
    out=g.ROOT/f'20261005-E14-history-v2-{task}-{device}-control-preflight';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');records=[]
    for entry in g.read(bank(task)/'ledger.json'):
        env,images=warm(entry,task);env.close()
    for arm in h.ARMS:
        phi,net,path,cfg=load(task,arm,device);before=(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        env,images=warm(g.read(bank(task)/'ledger.json')[0],task);env.close()
        encoded=n.encode(phi,normalized_pixels(images,device));zg=n.encode(phi,normalized_pixels(np.load(bank(task)/'goal_000.npy')[None],device))
        subset=torch.cat([n.encode(phi,normalized_pixels(images[j:j+1],device)) for j in range(11)])
        assert torch.allclose(encoded,subset,atol=2e-4,rtol=1e-5)
        current,goal=inputs(encoded,zg,arm);actual=net(current,goal,torch.zeros(1,dtype=torch.long,device=device))
        reference=encoded[[-11,-6,-1]] if arm=='TRUE-HISTORY' else encoded[-1:].repeat(3,1)
        expected=net(reference.reshape(1,576),torch.cat([zg,zg,zg],-1),torch.zeros(1,dtype=torch.long,device=device))
        assert torch.equal(actual,expected) and torch.isfinite(actual).all()
        assert before==(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        records.append(dict(arm=arm,checkpoint_sha256=g.sha(path),input_return_manual_exact=True,warm_encoder_subset_error=float((encoded-subset).abs().max()),weights_unchanged=True))
        print('History deployment actual preflight',task,device,arm,'PASS',flush=True);del phi,net;gc.collect()
    g.save(out/'controls.json',dict(passed=True,task=task,device=device,all48_11frame_warm_and_initial_state_exact=True,records=records,script_sha256=g.sha(__file__),trainer_sha256=g.sha(h.__file__)))


@torch.inference_mode()
def control(task):
    for device in ['cpu','cuda']:
        pre=g.read(g.ROOT/f'20261005-E14-history-v2-{task}-{device}-control-preflight/controls.json');assert pre['passed'] and pre['script_sha256']==g.sha(__file__)
    b=bank(task);ledger=g.read(b/'ledger.json')
    for arm in h.ARMS:
        phi,net,path,cfg=load(task,arm,'cuda');before=(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        for interface in ['native','physical']:
            name=f'20261005-E14-history-v2-control-{task}-{arm}-{interface}-RTX-s0';out=Path('/tmp/latent-wm-runs')/name
            assert not out.exists() and not (g.ROOT/name).exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
            try:
                g.save(out/'config.json',dict(task=task,arm=arm,interface=interface,train_seed=0,budget=100,history=3,history_lags=[-10,-5,0],executed_steps_per_decision=1,checkpoint=str(path),checkpoint_sha256=g.sha(path),bank_ledger_sha256=g.sha(b/'ledger.json'),script_sha256=g.sha(__file__),trainer_sha256=g.sha(h.__file__),geometry_source_sha256=cfg['feature_metadata']['source_sha256'],hardware=torch.cuda.get_device_name(),scope='Matched capacity, goals, starts and same raw primitive-action targets; true past observation inputs versus current copies. One head seed, shared48development, known memory baseline; no novel method or dynamics-only causality.'))
                rows=[]
                for entry in ledger:
                    j=entry['anchor'];goal=np.asarray(entry['goal_state']);env,images=warm(entry,task)
                    history=n.encode(phi,normalized_pixels(images,'cuda'));zg=n.encode(phi,normalized_pixels(np.load(b/f'goal_{j:03d}.npy')[None],'cuda'))
                    s=state(env,task);reached=success(s,goal,task);initial=reached;states=[s];actions=[];decisions=[]
                    for step in range(100):
                        if reached:break
                        x,y=inputs(history,zg,arm);issued=net(x,y,torch.zeros(1,dtype=torch.long,device='cuda')).cpu().numpy()[0]
                        assert np.isfinite(issued).all();actual=np.clip(issued,-1,1) if interface=='physical' else issued
                        _,_,done,truncated,_=env.step(actual.astype(np.float32));assert not truncated
                        s=state(env,task);reached=success(s,goal,task);assert bool(done)==reached
                        states.append(s);actions.append(actual);decisions.append(dict(decision=step,executed_steps=1,remaining_horizon=0,relative_observation_steps=[step-10,step-5,step],issued_action=issued.tolist(),issued_out_of_bounds_components=int((np.abs(actual)>1).sum())))
                        new=n.encode(phi,normalized_pixels(env.render()[None].copy(),'cuda'));history=torch.cat([history[1:],new])
                    env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial,success_by50=bool(initial or (reached and len(actions)<=50)),env_steps=len(actions),decisions=decisions,trace_sha256=g.sha(trace)))
                    g.save(out/'rows.json',rows);print('History policy control',task,arm,interface,j,int(reached),flush=True)
                assert before==(state_hash(phi.state_dict()),state_hash(net.state_dict()))
                g.save(out/'summary.json',[dict(goal_span=span,n=24,successes=sum(r['success'] for r in rows if r['goal_span']==span)) for span in [25,75]])
                g.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,g.ROOT/name)
            except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,g.ROOT/name);raise
        del phi,net;gc.collect();torch.cuda.empty_cache()


def queue(task):
    out=g.ROOT/f'20261005-E14-history-v2-control-{task}-pipeline';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    commands=[['preflight','--device',d] for d in ['cpu','cuda']]+[['control']]
    try:
        for command in commands:subprocess.run([sys.executable,'-u',__file__,*command,'--task',task],check=True)
        g.save(out/'complete.json',dict(completed=True,task=task,episodes=192))
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise


if __name__=='__main__':
    p0=argparse.ArgumentParser();p0.add_argument('mode',choices=['preflight','control','queue']);p0.add_argument('--task',choices=['nav','pusht'],required=True);p0.add_argument('--device',choices=['cpu','cuda'],default='cpu');args=p0.parse_args();torch.set_num_threads(4)
    if args.mode=='queue':queue(args.task)
    elif args.mode=='control':control(args.task)
    else:preflight(args.task,args.device)
