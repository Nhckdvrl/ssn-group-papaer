"""Pinned goal-policy on PushT, exact existing fresh tasks and native criterion."""
import argparse
import gc
import shutil
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
import goal_policy_control as n
import goal_policy_baseline as g
import goal_policy_pusht_adapter as adapter
import effect_transfer as t
import pusht_fresh_control as p
from fixed_data_train_seed import normalized_pixels,state_hash


def load(arm,device):
    source=g.ROOT/f'20261005-E14-goalpolicy-RELEASED-{arm}-A100-s0'
    assert g.read(source/'complete.json')==dict(completed=True,geometry='RELEASED',seed=0,arm=arm,epochs=50)
    cfg=g.read(source/'config.json');cpath=g.HF/source.name/'epoch50.ckpt';summary=g.read(source/'summary.json')
    assert g.sha(cpath)==summary['checkpoint_sha256'] and cfg['feature_metadata']['source_adapter_sha256']==g.sha(adapter.__file__)
    assert cfg['script_sha256']==g.sha(g.__file__) and cfg['vendor_model_sha256']==g.sha(g.VENDOR/'idm/model.py')
    c=torch.load(cpath,map_location='cpu',weights_only=False);assert c['arm']==arm and c['geometry']=='RELEASED' and c['train_seed']==0 and c['updates']==400
    phi,_,_,_,_=t.load_source(device);phi.eval().requires_grad_(False)
    assert state_hash(phi.state_dict())==cfg['feature_metadata']['frozen_model_sha256']
    net=g.goal_policy_official_model.GoalConditionedIDM(g.goal_policy_official_model.IDMConfig(**c['config']))
    net.load_state_dict(c['state_dict'],strict=True);net=net.to(device).eval().requires_grad_(False)
    return phi,net,cpath,cfg


@torch.inference_mode()
def preflight(device):
    assert g.read(g.WB/'results/E14_20261005_pusht_goal_policy_endpoint_audit.json')['completed']
    out=g.ROOT/f'20261005-E14-goalpolicy-pusht-{device}-control-preflight-s0';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');records=[]
    for entry in g.read(p.BANK/'ledger.json'):
        j=entry['anchor'];env,history=p.restore(entry,np.asarray(entry['goal_state']))
        assert np.array_equal(history,np.load(p.BANK/f'history_{j:03d}.npy')) and np.array_equal(p.diagnostic(env),np.load(p.BANK/f'factual_states_{j:03d}.npy')[0]);env.close()
    x=normalized_pixels(np.load(p.BANK/'history_000.npy')[-1:],device);goal=normalized_pixels(np.load(p.BANK/'goal_000.npy')[None],device)
    for arm in g.ARMS:
        phi,net,checkpoint,cfg=load(arm,device);before=(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        official=n.OfficialPolicy(phi,n.Mode(net,arm),eval_budget=100,device=torch.device(device));official.set_env(SimpleNamespace(action_space=SimpleNamespace(shape=(1,2))))
        for steps in [0,50,99]:
            official._step_count=steps;action=official.get_action(dict(pixels=x[:,None],goal=goal[:,None]))
            expected=net(n.encode(phi,x),n.encode(phi,goal),torch.tensor([n.horizon(arm,steps)],device=device)).cpu().numpy()
            assert np.array_equal(action,expected) and official._step_count==steps+1 and np.isfinite(action).all()
        assert before==(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        records.append(dict(arm=arm,official_policy_raw_action_exact=True,remaining_control_steps=[0,50,99],checkpoint_sha256=g.sha(checkpoint),parameters_unchanged=True))
        print('Push goal-policy deployment preflight',device,arm,'PASS',flush=True);del phi,net,official;gc.collect()
    g.save(out/'controls.json',dict(passed=True,all48_full25D_initial_state_and_pixels_exact=True,records=records,script_sha256=g.sha(__file__),shared_policy_component_sha256=g.sha(n.__file__),official_policy_sha256=g.sha(g.VENDOR/'eval_idm.py')))


@torch.inference_mode()
def control():
    for device in ['cpu','cuda']:
        v=g.read(g.ROOT/f'20261005-E14-goalpolicy-pusht-{device}-control-preflight-s0/controls.json');assert v['passed'] and v['script_sha256']==g.sha(__file__)
    ledger=g.read(p.BANK/'ledger.json')
    for arm in g.ARMS:
        phi,net,checkpoint,cfg=load(arm,'cuda');initial=(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        for interface in ['native','physical']:
            name=f'20261005-E14-goalpolicy-pusht-control-{arm}-{interface}-RTX-s0';out=Path('/tmp/latent-wm-runs')/name
            assert not out.exists() and not (g.ROOT/name).exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
            try:
                g.save(out/'config.json',dict(task='pusht',arm=arm,interface=interface,train_seed=0,budget=100,history=1,checkpoint=str(checkpoint),checkpoint_sha256=g.sha(checkpoint),geometry_checkpoint=str(t.SOURCE),geometry_source_sha256=t.SOURCE_SHA,bank_ledger_sha256=g.sha(p.BANK/'ledger.json'),script_sha256=g.sha(__file__),policy_component_sha256=g.sha(n.__file__),trainer_sha256=g.sha(g.__file__),source_adapter_sha256=g.sha(adapter.__file__),restore_sha256=g.sha(p.__file__),hardware=torch.cuda.get_device_name(),action_coordinates='raw physical; no inverse standardization; optional output clip only',scope='First86 head fact episodes excluded from fresh48source; encoder pretraining overlap unknown. One trainseed, true observation each step versus CEM25 commitment; no novel method or complete numerical paper replication. 50step readout is prefix of100step-budget control, not new50-budget policy.'))
                rows=[]
                for entry in ledger:
                    j=entry['anchor'];goal=np.asarray(entry['goal_state']);env,history=p.restore(entry,goal)
                    assert np.array_equal(history,np.load(p.BANK/f'history_{j:03d}.npy'))
                    state=p.diagnostic(env);assert np.array_equal(state,np.load(p.BANK/f'factual_states_{j:03d}.npy')[0])
                    zg=n.encode(phi,normalized_pixels(np.load(p.BANK/f'goal_{j:03d}.npy')[None],'cuda'))
                    reached=p.success(env._get_obs(),goal);initial_success=reached;states=[state];actions=[];decisions=[]
                    for step in range(100):
                        if reached:break
                        current=normalized_pixels(env.render()[None].copy(),'cuda')
                        issued=net(n.encode(phi,current),zg,torch.tensor([n.horizon(arm,step)],device='cuda')).cpu().numpy()[0]
                        assert np.isfinite(issued).all();actual=np.clip(issued,-1,1) if interface=='physical' else issued
                        _,_,done,truncated,_=env.step(actual.astype(np.float32));assert not truncated
                        reached=p.success(env._get_obs(),goal);assert bool(done)==reached
                        states.append(p.diagnostic(env));actions.append(actual);decisions.append(dict(decision=step,executed_steps=1,remaining_horizon=n.horizon(arm,step),issued_action=issued.tolist(),issued_out_of_bounds_components=int((np.abs(actual)>1).sum())))
                    env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial_success,success_by50=bool(initial_success or (reached and len(actions)<=50)),env_steps=len(actions),decisions=decisions,trace_sha256=g.sha(trace)))
                    g.save(out/'rows.json',rows);print('Push goalpolicy control',arm,interface,j,int(reached),flush=True)
                assert initial==(state_hash(phi.state_dict()),state_hash(net.state_dict()))
                g.save(out/'summary.json',[dict(goal_span=v,n=24,successes=sum(row['success'] for row in rows if row['goal_span']==v)) for v in [25,75]])
                g.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,g.ROOT/name)
            except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,g.ROOT/name);raise
        del phi,net;gc.collect();torch.cuda.empty_cache()


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['preflight','control']);a.add_argument('--device',choices=['cpu','cuda'],default='cpu');v=a.parse_args();torch.set_num_threads(4)
    if v.mode=='preflight':preflight(v.device)
    else:control()
