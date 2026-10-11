"""Full published INTACT paper grammar, causal H1 direct control reference."""
import argparse
import ast
import logging
import hashlib
import inspect
import importlib.metadata
import os
import shutil
import subprocess
import sys
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
WB=Path(__file__).resolve().parents[1];VENDOR=WB/'vendor/intact-jepa';RUNTIME=VENDOR/'paper_runtime'
sys.path.insert(0,str(RUNTIME))
sys.path.insert(1,str(VENDOR))
import torch
import jepa,module
assert Path(inspect.getfile(jepa.JEPA)).resolve()==RUNTIME/'jepa.py'
assert Path(module.__file__).resolve()==RUNTIME/'module.py'
import numpy as np
from hydra.utils import instantiate
from transformers import ViTConfig,ViTModel
from sklearn.preprocessing import StandardScaler
from history_policy import BlockStandardScaler
import bounded_control as b
import pusht_fresh_control as p
from experience_transfer_control_audit import ROOT,read,save,sha
HF=Path('/home/xiang/.cache/huggingface/latent-wm-derived/intact-e5-goal-seed0')


def state_hash(state):
    h=hashlib.sha256()
    for name,v in sorted(state.items()):h.update(name.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def pixels(array,device):
    x=torch.as_tensor(array,device=device).movedim(-1,-3).float()/255
    return (x-x.new_tensor([.485,.456,.406])[:,None,None])/x.new_tensor([.229,.224,.225])[:,None,None]


def setup():
    torch.set_num_threads(4)
    torch.backends.cuda.enable_flash_sdp(False);torch.backends.cuda.enable_mem_efficient_sdp(False);torch.backends.cuda.enable_math_sdp(True)
    if hasattr(torch.backends.cuda,'enable_cudnn_sdp'):torch.backends.cuda.enable_cudnn_sdp(False)
    torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
    for key,value in [('INVERSE_QUERY_CONDITION_SOURCE','goal'),('INVERSE_DIRECT_TARGET_MODE','query'),('INVERSE_QUERY_BETA_MODE','off'),('INVERSE_QUERY_BYPASS_PREDICTOR','0'),('INVERSE_QUERY_GAMMA','1.0'),('INVERSE_QUERY_SCALE','1.0')]:os.environ[key]=value


def source(task,device):
    assets=read(ROOT/'20261005-E01-intact-published-assets/complete.json');record=next(x for x in assets['records'] if x['task']==task)
    assert sha(record['path'])==record['sha256'] and Path(record['path']).stat().st_size==record['bytes']
    folder=HF/f'recovery_delta_full_{task}_s0';cfg=read(folder/'config.json');meta=read(folder/'multitask_metadata_epoch_5.json')
    assert cfg['inverse_actor']['feature_layout']=='delta_condition_product' and cfg['predict_residual'] is False
    manifest=read(VENDOR/'checkpoints/PAPER_E5_GOAL_MANIFEST.json')['training_seeds'][0]
    assert (meta['epoch'],meta['seed'],meta['task'],meta['shared_state_sha256'])==(5,0,task,manifest['shared_state_sha256'])
    # Execute only the exact pinned, read-back official ViT constructor.
    # No stable_pretraining installation or change to the live environment.
    code=HF.parent/'intact-reference-code/vit_hf_0.1.7.txt';namespace=dict(nn=torch.nn,ViTConfig=ViTConfig,ViTModel=ViTModel,logging=logging,_TRANSFORMERS_AVAILABLE=True)
    exec(compile(ast.parse(code.read_text()),str(code),'exec'),namespace)
    encoder=namespace['vit_hf'](**{k:v for k,v in cfg['encoder'].items() if not k.startswith('_')})
    kwargs={k:(instantiate(v) if isinstance(v,dict) else v) for k,v in cfg.items() if k not in ['_target_','encoder']}
    net=jepa.JEPA(encoder=encoder,**kwargs);weights=torch.load(record['path'],map_location='cpu',weights_only=True);net.load_state_dict(weights,strict=True)
    actual_shared=state_hash({k:v for k,v in weights.items() if k.startswith(('encoder.','projector.'))});assert actual_shared==manifest['shared_state_sha256']
    assert len(weights)==len(net.state_dict()) and all(torch.isfinite(v).all() for v in weights.values())
    net=net.to(device).eval().requires_grad_(False);assert type(net) is jepa.JEPA and net.get_action_dim()==10 and net.actor_warmstart
    normpath=ROOT/f'20261002-{task}-native-s0/action_normalization.npz';norm=np.load(normpath)
    scaler=StandardScaler();scaler.mean_=norm['mean'];scaler.scale_=norm['std'];scaler.var_=scaler.scale_**2;scaler.n_features_in_=2
    assert scaler.mean_.shape==scaler.scale_.shape==(2,) and (scaler.scale_>0).all()
    return net,BlockStandardScaler(scaler),dict(checkpoint=record,software_versions={name:importlib.metadata.version(name) for name in ['torch','transformers','numpy','stable-worldmodel','scikit-learn','pymunk']},model_config_sha256=sha(folder/'config.json'),metadata_sha256=sha(folder/'multitask_metadata_epoch_5.json'),normalizer_sha256=sha(normpath),shared_encoder_sha256=state_hash({k:v for k,v in weights.items() if k.startswith(('encoder.','projector.'))}),vit_constructor_sha256=sha(code),vit_constructor_manifest=read(code.parent/'source_manifest.json'),runtime_sha256={file:sha(RUNTIME/file) for file in ['jepa.py','module.py','prior_only_solver.py','sitecustomize.py']},history_policy_sha256=sha(VENDOR/'history_policy.py'),model_state_keys=len(weights),parameters=sum(v.numel() for v in net.parameters()),revision=assets['resolved_revision'])


def bank(task):return ROOT/('20261004-E20-fresh-control-bank48' if task=='tworoom' else '20261005-E20-pusht-fresh-control-bank48')
def restore(task,entry):return b.restore(entry) if task=='tworoom' else p.restore(entry,np.asarray(entry['goal_state']))
def diagnostic(task,env):return env.agent_position.numpy().copy() if task=='tworoom' else p.diagnostic(env)
def success(task,state,goal):return bool(np.linalg.norm(state-goal)<16) if task=='tworoom' else p.success(state[:7],goal)


def info(current,goal,past,scaler,device):
    raw=np.asarray(past[-5:],dtype=np.float32);assert raw.shape==(5,2)
    return dict(pixels=pixels(current[None,None],device),goal=pixels(goal[None,None],device),action=torch.as_tensor(scaler.transform(raw.reshape(1,1,10)),device=device).float())


@torch.inference_mode()
def preflight(task,device):
    out=ROOT/f'20261005-E01-intact-v3-{task}-{device}-preflight';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        net,scaler,meta=source(task,device);initial=state_hash(net.state_dict());ledger=read(bank(task)/'ledger.json')
        for entry in ledger:
            env,history=restore(task,entry);j=entry['anchor'];assert np.array_equal(history,np.load(bank(task)/f'history_{j:03d}.npy'))
            assert np.array_equal(diagnostic(task,env),np.load(bank(task)/f'factual_states_{j:03d}.npy')[0]);env.close()
        current=np.load(bank(task)/'history_000.npy')[-1];goal=np.load(bank(task)/'goal_000.npy');past=ledger[0]['warm_actions'];inp=info(current,goal,past,scaler,device)
        actual=net.get_action(inp,horizon=5);assert actual.shape==(1,5,10) and torch.isfinite(actual).all()
        emb=net.encode(dict(pixels=inp['pixels']))['emb'];zg=net.encode(dict(pixels=inp['goal']))['emb'][:,-1];history=inp['action'].clone();manual=[]
        for t in range(5):
            z=emb[:,-1];delta=zg-z;prev=net.action_encoder(history[:,-1:])[:,-1]
            features=torch.cat([z,delta,torch.zeros_like(z),z*delta,prev],-1)
            assert torch.equal(features,net.inverse_actor.actor_features(z,zg,prev))
            mean=net.inverse_actor.net(features).chunk(2,-1)[0];manual.append(mean)
            hs=min(3,emb.size(1),history.size(1));context=history[:,-hs:].clone();context[:,-1]=mean
            next_z=net.predict(emb[:,-hs:],net.action_encoder(context))[:,-1:]
            emb=torch.cat([emb,next_z],1);history=torch.cat([history,mean[:,None]],1)
        assert torch.equal(actual,torch.stack(manual,1)) and initial==state_hash(net.state_dict())
        raw=np.asarray(past[-5:],dtype=np.float32);assert np.array_equal(scaler.scaler.transform(raw),inp['action'].cpu().numpy().reshape(5,2))
        save(out/'controls.json',dict(passed=True,task=task,device=device,manual_full_actor_rollout_exact=True,raw5_standardization_exact=True,all48_state_pixels_exact=True,model_unchanged=True,script_sha256=sha(__file__),source=meta))
        print('INTACT complete published preflight',task,device,'PASS',flush=True)
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


@torch.inference_mode()
def control(task):
    for device in ['cpu','cuda']:
        controls=read(ROOT/f'20261005-E01-intact-v3-{task}-{device}-preflight/controls.json');assert controls['passed'] and controls['script_sha256']==sha(__file__)
    net,scaler,meta=source(task,'cuda');initial=state_hash(net.state_dict());ledger=read(bank(task)/'ledger.json')
    for interface in ['native','physical']:
        out=ROOT/f'20261005-E01-intact-v3-{task}-{interface}-control';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
        try:
            save(out/'config.json',dict(task=task,interface=interface,source=meta,train_seed=0,script_sha256=sha(__file__),bank_ledger_sha256=sha(bank(task)/'ledger.json'),budget=100,history_frames=1,planning_primitive_steps=25,execution_primitive_steps=25,hardware=torch.cuda.get_device_name(),scope='Complete published E5 joint model, causal last5 actual primitive action history, official paper grammar with get_action horizon5. Same48 development states; published pretraining unknown/unmatched, not numerical paper replication or training causality. Native vs output clip; all initial successes retained.'))
            rows=[]
            for entry in ledger:
                j=entry['anchor'];goal=np.asarray(entry['goal_state']);env,warm=restore(task,entry);assert np.array_equal(warm,np.load(bank(task)/f'history_{j:03d}.npy'))
                state=diagnostic(task,env);assert np.array_equal(state,np.load(bank(task)/f'factual_states_{j:03d}.npy')[0])
                reached=success(task,state,goal);initial_success=reached;states=[state];actions=[];past=list(entry['warm_actions']);decisions=[];goal_image=np.load(bank(task)/f'goal_{j:03d}.npy')
                for decision in range(4):
                    if reached:break
                    current=env.render().copy();inputs=info(current,goal_image,past,scaler,'cuda');proposal=net.get_action(inputs,horizon=5).cpu().numpy().reshape(25,2)
                    issued=scaler.scaler.inverse_transform(proposal);actual=np.clip(issued,-1,1) if interface=='physical' else issued;steps=0
                    previous=np.asarray(past[-5:],dtype=np.float32)
                    for command in actual:
                        _,_,done,truncated,_=env.step(command.astype(np.float32));assert not truncated
                        state=diagnostic(task,env);reached=success(task,state,goal);assert bool(done)==reached
                        states.append(state);actions.append(command);past.append(command.astype(np.float32));steps+=1
                        if reached:break
                    decisions.append(dict(decision=decision,executed_steps=steps,previous_executed_actions=previous.tolist(),standardized_proposal=proposal.tolist(),out_of_bounds_components=int((np.abs(actual[:steps])>1).sum())))
                env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2))
                rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial_success,env_steps=len(actions),decisions=decisions,trace_sha256=sha(trace)))
                save(out/'rows.json',rows);print('INTACT published direct',task,interface,j,int(reached),flush=True)
            assert initial==state_hash(net.state_dict());save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True))
        except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


def queue():
    for task in ['tworoom','pusht']:
        for device in ['cpu','cuda']:subprocess.run([sys.executable,'-u',__file__,'preflight','--task',task,'--device',device],check=True)
        subprocess.run([sys.executable,'-u',__file__,'control','--task',task],check=True)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['queue','preflight','control']);a.add_argument('--task',choices=['tworoom','pusht']);a.add_argument('--device',choices=['cpu','cuda'],default='cpu');v=a.parse_args();setup()
    if v.mode=='queue':queue()
    elif v.mode=='preflight':preflight(v.task,v.device)
    else:control(v.task)
