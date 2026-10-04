"""G3 fixed four-head Push control, every-step actual observation feedback."""
import argparse
import gc
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
# Published control components must load their pinned JEPA namespace first.
import goal_policy_pusht_control as original
import goal_policy_coverage as c
from fixed_data_train_seed import normalized_pixels,state_hash
g=c.g;n=original.n;p=original.p;t=original.t
CELLS=[(e,u) for e in [86,860] for u in [400,4000]]


def load(episodes,updates,device):
    source=g.ROOT/f'20261005-E14-coverage-e{episodes}-u{updates}-RTX-s0';cfg=g.read(source/'config.json');path=g.HF/source.name/f'u{updates}.ckpt'
    assert g.read(source/'complete.json')==dict(completed=True,episodes=episodes,updates=updates)
    assert cfg['script_sha256']==g.sha(c.__file__) and g.sha(path)==g.read(source/'summary.json')['checkpoint_sha256']
    checkpoint=torch.load(path,map_location='cpu',weights_only=False);assert (checkpoint['episodes'],checkpoint['updates'])==(episodes,updates)
    phi,_,_,_,_=t.load_source(device);phi.eval().requires_grad_(False)
    assert state_hash(phi.state_dict())==cfg['feature_metadata']['frozen_model_sha256'] and t.SOURCE_SHA==cfg['feature_metadata']['source_sha256']
    net=g.model(0,device);net.load_state_dict(checkpoint['state_dict'],strict=True);net.eval().requires_grad_(False)
    return phi,net,path,cfg


@torch.inference_mode()
def preflight(device):
    assert g.read(g.WB/'results/E14_20261005_coverage_policy_endpoint_audit.json')['completed']
    out=g.ROOT/f'20261005-E14-coverage-{device}-control-preflight';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');records=[]
    for entry in g.read(p.BANK/'ledger.json'):
        env,images=p.restore(entry,np.asarray(entry['goal_state']));j=entry['anchor']
        assert np.array_equal(images,np.load(p.BANK/f'history_{j:03d}.npy')) and np.array_equal(p.diagnostic(env),np.load(p.BANK/f'factual_states_{j:03d}.npy')[0]);env.close()
    x=normalized_pixels(np.load(p.BANK/'history_000.npy')[-1:],device);goal=normalized_pixels(np.load(p.BANK/'goal_000.npy')[None],device)
    for episodes,updates in CELLS:
        phi,net,path,cfg=load(episodes,updates,device);before=(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        policy=n.OfficialPolicy(phi,n.Mode(net,'GCBC-MATCHED'),eval_budget=100,device=torch.device(device));policy.set_env(SimpleNamespace(action_space=SimpleNamespace(shape=(1,2))))
        actual=policy.get_action(dict(pixels=x[:,None],goal=goal[:,None]));manual=net(n.encode(phi,x),n.encode(phi,goal),torch.zeros(1,dtype=torch.long,device=device)).cpu().numpy()
        assert np.array_equal(actual,manual) and np.isfinite(actual).all() and before==(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        records.append(dict(episodes=episodes,updates=updates,checkpoint_sha256=g.sha(path),official_raw_return_exact=True,weights_unchanged=True))
        print('Coverage deployment actual preflight',episodes,updates,device,'PASS',flush=True);del phi,net,policy;gc.collect()
    g.save(out/'controls.json',dict(passed=True,all48_full25D_warm_pixels_exact=True,records=records,script_sha256=g.sha(__file__),trainer_sha256=g.sha(c.__file__)))


@torch.inference_mode()
def control():
    for device in ['cpu','cuda']:
        pre=g.read(g.ROOT/f'20261005-E14-coverage-{device}-control-preflight/controls.json');assert pre['passed'] and pre['script_sha256']==g.sha(__file__)
    ledger=g.read(p.BANK/'ledger.json')
    for episodes,updates in CELLS:
        phi,net,path,cfg=load(episodes,updates,'cuda');before=(state_hash(phi.state_dict()),state_hash(net.state_dict()))
        for interface in ['native','physical']:
            name=f'20261005-E14-coverage-control-e{episodes}-u{updates}-{interface}-RTX-s0';out=Path('/tmp/latent-wm-runs')/name
            assert not out.exists() and not (g.ROOT/name).exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
            try:
                g.save(out/'config.json',dict(task='pusht',episodes=episodes,updates=updates,train_seed=0,interface=interface,budget=100,history=1,executed_steps_per_decision=1,horizon_input=0,checkpoint=str(path),checkpoint_sha256=g.sha(path),geometry_source_sha256=t.SOURCE_SHA,bank_ledger_sha256=g.sha(p.BANK/'ledger.json'),script_sha256=g.sha(__file__),trainer_sha256=g.sha(c.__file__),policy_component_sha256=g.sha(n.__file__),restore_sha256=g.sha(p.__file__),hardware=torch.cuda.get_device_name(),scope='Known GCBC same phi, fixed data by compute matrix and matched new86x400 anchor; one trainseed, published encoder overlap unknown, all48development retained. Every-step true observations, raw action with optional output clip only. 50step readout is100-budget prefix.'))
                rows=[]
                for entry in ledger:
                    j=entry['anchor'];goal=np.asarray(entry['goal_state']);env,images=p.restore(entry,goal)
                    assert np.array_equal(images,np.load(p.BANK/f'history_{j:03d}.npy'))
                    s=p.diagnostic(env);assert np.array_equal(s,np.load(p.BANK/f'factual_states_{j:03d}.npy')[0])
                    zg=n.encode(phi,normalized_pixels(np.load(p.BANK/f'goal_{j:03d}.npy')[None],'cuda'));reached=p.success(s[:7],goal);initial=reached;states=[s];actions=[];decisions=[]
                    for step in range(100):
                        if reached:break
                        z=n.encode(phi,normalized_pixels(env.render()[None].copy(),'cuda'));issued=net(z,zg,torch.zeros(1,dtype=torch.long,device='cuda')).cpu().numpy()[0]
                        assert np.isfinite(issued).all();actual=np.clip(issued,-1,1) if interface=='physical' else issued
                        _,_,done,truncated,_=env.step(actual.astype(np.float32));assert not truncated
                        s=p.diagnostic(env);reached=p.success(s[:7],goal);assert bool(done)==reached
                        states.append(s);actions.append(actual);decisions.append(dict(decision=step,executed_steps=1,remaining_horizon=0,issued_action=issued.tolist(),issued_out_of_bounds_components=int((np.abs(actual)>1).sum())))
                    env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                    rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial,success_by50=bool(initial or (reached and len(actions)<=50)),env_steps=len(actions),decisions=decisions,trace_sha256=g.sha(trace)))
                    g.save(out/'rows.json',rows);print('Coverage policy control',episodes,updates,interface,j,int(reached),flush=True)
                assert before==(state_hash(phi.state_dict()),state_hash(net.state_dict()))
                g.save(out/'summary.json',[dict(goal_span=span,n=24,successes=sum(r['success'] for r in rows if r['goal_span']==span)) for span in [25,75]])
                g.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,g.ROOT/name)
            except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,g.ROOT/name);raise
        del phi,net;gc.collect();torch.cuda.empty_cache()


def queue():
    out=g.ROOT/'20261005-E14-coverage-control-pipeline';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    commands=[['preflight','--device',d] for d in ['cpu','cuda']]+[['control']]
    try:
        for command in commands:subprocess.run([sys.executable,'-u',__file__,*command],check=True)
        g.save(out/'complete.json',dict(completed=True,episodes=384))
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise


if __name__=='__main__':
    p0=argparse.ArgumentParser();p0.add_argument('mode',choices=['preflight','control','queue']);p0.add_argument('--device',choices=['cpu','cuda'],default='cpu');args=p0.parse_args();torch.set_num_threads(4)
    if args.mode=='queue':queue()
    elif args.mode=='preflight':preflight(args.device)
    else:control()
