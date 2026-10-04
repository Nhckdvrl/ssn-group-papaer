"""Actual policy-component parity before complete original 48-anchor controller matrix."""
import argparse
import ast
import gc
import json
import shutil
import time
from types import SimpleNamespace
from pathlib import Path
import numpy as np
import torch
import matched_learning as m
import geometry_experience as ge
import goal_policy_baseline as g
import bounded_control as b
from fixed_data_train_seed import normalized_pixels,state_hash

BANK=g.ROOT/'20261004-E20-fresh-control-bank48'
# Compile exactly the pinned published class, excluding unrelated broken PairwiseIDM import.
node=next(n for n in ast.parse((g.VENDOR/'eval_idm.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='GoalConditionedPolicy')
namespace=dict(torch=torch,np=np,time=time)
exec(compile(ast.Module(body=[node],type_ignores=[]),str(g.VENDOR/'eval_idm.py'),'exec'),namespace)
OfficialPolicy=namespace['GoalConditionedPolicy']


def load(geometry,train_seed,arm,device):
    source=g.ROOT/f'20261005-E14-goalpolicy-{geometry}-{arm}-A100-s{train_seed}'
    assert g.read(source/'complete.json')==dict(completed=True,geometry=geometry,seed=train_seed,arm=arm,epochs=50)
    cfg=g.read(source/'config.json');feature=cfg['feature_metadata']
    checkpoint=g.HF/source.name/'epoch50.ckpt';assert g.sha(checkpoint)==g.read(source/'summary.json')['checkpoint_sha256']
    c=torch.load(checkpoint,map_location='cpu',weights_only=False)
    assert c['train_seed']==train_seed and c['geometry']==geometry and c['arm']==arm
    assert cfg['script_sha256']==g.sha(g.__file__) and cfg['vendor_model_sha256']==g.sha(g.VENDOR/'idm/model.py')
    prior=Path(str(ge.SOURCES[geometry]).replace('-s0/',f'-s{train_seed}/'))
    assert g.sha(prior)==feature['source_sha256']
    original=torch.load(prior,map_location='cpu',weights_only=False)['state_dict']
    phi,_=m.make_model(feature['architecture'],train_seed,'ABS');state=phi.state_dict()
    for key in state:
        if key.startswith(ge.PREFIX):state[key]=original[key].clone()
    phi.load_state_dict(state,strict=True);phi=phi.to(device).eval().requires_grad_(False)
    assert state_hash({k:v for k,v in phi.state_dict().items() if k.startswith(ge.PREFIX)})==feature['frozen_phi_sha256']
    net=g.goal_policy_official_model.GoalConditionedIDM(g.goal_policy_official_model.IDMConfig(**c['config']))
    net.load_state_dict(c['state_dict'],strict=True);net=net.to(device).eval().requires_grad_(False)
    assert not set(feature['manifest']['base_episodes'])&{e['episode'] for e in g.read(BANK/'ledger.json')}
    return phi,net,cfg,checkpoint


def encode(phi,pixels):
    return phi.projector(phi.encoder(pixels,interpolate_pos_encoding=True).last_hidden_state[:,0])


def horizon(arm,steps):return 0 if arm=='GCBC-MATCHED' else 1 if arm=='PAIRWISE' else min(100-steps,50)


class Mode:
    def __init__(self,net,arm):self.net=net;self.arm=arm;self.max_horizon=50
    def __call__(self,z,goal,steps):
        if self.arm=='GCBC-MATCHED':steps=torch.zeros_like(steps)
        elif self.arm=='PAIRWISE':steps=torch.ones_like(steps)
        return self.net(z,goal,steps)


@torch.inference_mode()
def preflight(geometry,train_seed,device):
    out=g.ROOT/f'20261005-E14-goalpolicy-{geometry}-{device}-control-preflight-s{train_seed}'
    assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    # Original node/task renderer, no relaxation of existing exact guards.
    for entry in g.read(BANK/'ledger.json'):
        env,history=b.restore(entry)
        assert np.array_equal(history,np.load(BANK/f'history_{entry["anchor"]:03d}.npy'))
        assert np.array_equal(env.agent_position.numpy(),np.load(BANK/f'factual_states_{entry["anchor"]:03d}.npy')[0]);env.close()
    records=[]
    for arm in g.ARMS:
        phi,net,cfg,checkpoint=load(geometry,train_seed,arm,device);phash=state_hash(phi.state_dict());nhash=state_hash(net.state_dict())
        x=normalized_pixels(np.load(BANK/'history_000.npy')[-1:],device);goal=normalized_pixels(np.load(BANK/'goal_000.npy')[None],device)
        native=OfficialPolicy(phi,Mode(net,arm),eval_budget=100,device=torch.device(device),cache_goal_encoding=True)
        native.set_env(SimpleNamespace(action_space=SimpleNamespace(shape=(1,2))))
        for steps in [0,50,99]:
            native._step_count=steps
            action=native.get_action(dict(pixels=x[:,None],goal=goal[:,None]))
            manual=net(encode(phi,x),encode(phi,goal),torch.tensor([horizon(arm,steps)],device=device)).cpu().numpy()
            assert np.array_equal(action,manual) and native._step_count==steps+1
            assert np.isfinite(action).all() and np.array_equal(np.clip(action,-1,1),np.maximum(-1,np.minimum(action,1)))
        assert phash==state_hash(phi.state_dict()) and nhash==state_hash(net.state_dict())
        records.append(dict(arm=arm,raw_action_policy_parity_exact=True,remaining_steps_checked=[0,50,99],checkpoint_sha256=g.sha(checkpoint),frozen_parameters_unchanged=True))
        print('goal policy actual controller preflight',geometry,train_seed,device,arm,'PASS',flush=True)
        del phi,net,native;gc.collect()
    g.save(out/'controls.json',dict(passed=True,geometry=geometry,seed=train_seed,device=device,script_sha256=g.sha(__file__),official_policy_sha256=g.sha(g.VENDOR/'eval_idm.py'),all48_initial_pixels_states_exact=True,records=records))


@torch.inference_mode()
def control(geometry,train_seed):
    for device in ['cpu','cuda']:
        passed=g.read(g.ROOT/f'20261005-E14-goalpolicy-{geometry}-{device}-control-preflight-s{train_seed}/controls.json')
        assert passed['passed'] and passed['script_sha256']==g.sha(__file__)
    ledger=g.read(BANK/'ledger.json')
    for arm in g.ARMS:
        phi,net,cfg,checkpoint=load(geometry,train_seed,arm,'cuda');phash=state_hash(phi.state_dict());nhash=state_hash(net.state_dict())
        for interface in ['native','physical']:
            name=f'20261005-E14-goalpolicy-control-{geometry}-{arm}-{interface}-RTX-s{train_seed}'
            out=Path('/tmp/latent-wm-runs')/name;assert not out.exists() and not (g.ROOT/name).exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
            try:
                g.save(out/'config.json',dict(geometry=geometry,arm=arm,train_seed=train_seed,interface=interface,history=1,budget=100,executed_steps_per_decision=1,checkpoint=str(checkpoint),checkpoint_sha256=g.sha(checkpoint),source_training_run=cfg['geometry']+'-'+cfg['arm'],training_artifact=str(g.ROOT/checkpoint.parent.name),bank_ledger_sha256=g.sha(BANK/'ledger.json'),script_sha256=g.sha(__file__),trainer_sha256=g.sha(g.__file__),vendor_model_sha256=g.sha(g.VENDOR/'idm/model.py'),geometry_source_sha256=cfg['feature_metadata']['source_sha256'],hardware=torch.cuda.get_device_name(),action_coordinates='raw physical; no inverse normalization; output clip only in physical interface',scope='Known goal policy component, same100 fact/six priors; real feedback each step differs from CEM25commitment, so not single-factor CEM comparison. Shared48 development goals, no novel method confirmation.'))
                rows=[]
                for entry in ledger:
                    j=entry['anchor'];env,history=b.restore(entry)
                    assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'))
                    state=env.agent_position.numpy().copy();assert np.array_equal(state,np.load(BANK/f'factual_states_{j:03d}.npy')[0])
                    goal=normalized_pixels(np.load(BANK/f'goal_{j:03d}.npy')[None],'cuda');zg=encode(phi,goal)
                    reached=bool(np.linalg.norm(state-entry['goal_state'])<16);initial=reached
                    states=[state];actions=[];decisions=[]
                    for steps in range(100):
                        if reached:break
                        x=normalized_pixels(env.render()[None].copy(),'cuda');z=encode(phi,x)
                        issued=net(z,zg,torch.tensor([horizon(arm,steps)],device='cuda')).cpu().numpy()[0]
                        assert np.isfinite(issued).all();actual=np.clip(issued,-1,1) if interface=='physical' else issued
                        _,_,done,truncated,_=env.step(actual.astype(np.float32));assert not truncated
                        state=env.agent_position.numpy().copy();reached=bool(np.linalg.norm(state-entry['goal_state'])<16);assert bool(done)==reached
                        states.append(state);actions.append(actual);decisions.append(dict(decision=steps,executed_steps=1,remaining_horizon=horizon(arm,steps),issued_action=issued.tolist()))
                    env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial,success_by50=bool(initial or (reached and len(actions)<=50)),env_steps=len(actions),decisions=decisions,trace_sha256=g.sha(trace)))
                    g.save(out/'rows.json',rows);print('goalpolicy control',geometry,train_seed,arm,interface,j,int(reached),flush=True)
                assert phash==state_hash(phi.state_dict()) and nhash==state_hash(net.state_dict())
                g.save(out/'summary.json',[dict(goal_span=v,n=24,successes=sum(row['success'] for row in rows if row['goal_span']==v)) for v in [25,75]])
                g.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,g.ROOT/name)
            except Exception as error:
                g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,g.ROOT/name);raise
        del phi,net;gc.collect();torch.cuda.empty_cache()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','control']);p.add_argument('--geometry',choices=g.GEOMETRIES,required=True);p.add_argument('--seed',type=int,choices=[0,1,2],required=True);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');a=p.parse_args();torch.set_num_threads(4)
    if a.mode=='preflight':preflight(a.geometry,a.seed,a.device)
    else:control(a.geometry,a.seed)
