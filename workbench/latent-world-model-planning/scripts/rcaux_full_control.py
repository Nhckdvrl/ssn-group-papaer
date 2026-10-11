"""Published complete RC-aux with original criterion; explicit history ports."""
import argparse
import copy
import inspect
import json
import os
import shutil
import sys
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
WB=Path(__file__).resolve().parents[1];VENDOR=WB/'vendor/rc-aux';sys.path.insert(0,str(VENDOR))
import torch
import jepa,module
assert Path(inspect.getfile(jepa.JEPA)).resolve()==VENDOR/'jepa.py'
import h5py
import hdf5plugin
import numpy as np
from sklearn.preprocessing import StandardScaler
import stable_worldmodel as swm
from gymnasium.vector.utils import batch_space
import bounded_control as b
from fixed_data_train_seed import state_hash,normalized_pixels
ROOT=Path('/home/xiang/.cache/latent-wm-results');BANK=ROOT/'20261004-E20-fresh-control-bank48'
SOURCE=Path('/home/xiang/.cache/huggingface/hub/models--biubiu116--RC-aux/snapshots/1cb0e604f348191afb1393d63769d752d6b0881d/rcaux/checkpoints/pixel_control/tworoom_rcaux/rcaux_tworoom_object.ckpt')
SHA='56979b8791dc76bab066c8c7a5aaa1c2947be8911b7a50202b69be46ab866099'
CONDITIONS=[(1,.85),(1,0.),(3,.85),(3,0.)]

def load(device):
 assert b.sha(SOURCE)==SHA
 model=torch.load(SOURCE,map_location='cpu',weights_only=False).eval().requires_grad_(False)
 assert type(model)==jepa.JEPA and len(model.state_dict())==312 and model.reachability_head.max_horizon==5
 assert model.goal_cost_reduce=='terminal' and model.latent_cost_weight==1 and not model.use_temporal_distance_cost and model.action_l2_cost_weight==model.action_smooth_cost_weight==0
 return model.to(device)
def stats(dataset):
 with h5py.File(dataset) as f:actions=f['action'][:]
 actions=actions[np.isfinite(actions).all(1)];fit=StandardScaler().fit(actions)
 assert fit.mean_.shape==fit.scale_.shape==(2,) and (fit.scale_>0).all()
 return fit.mean_,fit.scale_,dict(dataset=str(dataset),finite_rows=len(actions),action_mean=fit.mean_.tolist(),action_std=fit.scale_.tolist(),normalization='official eval.py StandardScaler full finite-action dataset; no own100 norm',eval_source_sha256=b.sha(VENDOR/'eval.py'))
class Cost:
 def __init__(self,model,history,goal,past):
  self.model=model;self.initial=model.encode({'pixels':history})['emb'];self.goal=model.encode({'pixels':goal})['emb'];self.past=past
 def embeddings(self,a):
  batch,samples=a.shape[:2];h=self.initial.shape[1]
  actions=torch.cat([self.past[:,None].expand(batch,samples,h-1,10),a],2).flatten(0,1)
  emb=self.initial[:,None].expand(batch,samples,h,192).flatten(0,1).clone()
  for k in range(5):
   act=self.model.action_encoder(actions[:,:h+k]);next_z=self.model.predict(emb[:,-3:],act[:,-3:])[:,-1:];emb=torch.cat([emb,next_z],1)
  return emb.reshape(batch,samples,h+5,192)
 def get_cost(self,info,a):return self.model.criterion({'predicted_emb':self.embeddings(a),'goal_emb':self.goal})
@torch.inference_mode()
def preflight(args):
 out=Path(args.output);assert not out.exists() and not (ROOT/out.name).exists();out.mkdir(parents=True);shutil.copy2(__file__,out/'rcaux_full_control_used.py')
 try:
  torch.set_num_threads(4);mean,std,meta=stats(args.dataset);model=load(args.device);initial=state_hash(model.state_dict());ledger=json.loads((BANK/'ledger.json').read_text());entry=ledger[0]
  history=np.load(BANK/'history_000.npy');goal=normalized_pixels(np.load(BANK/'goal_000.npy')[None,None],args.device)
  physical=np.random.default_rng(112501).uniform(-1,1,(1,37,5,5,2));a=torch.tensor((physical-mean)/std,device=args.device).float().flatten(-2);records=[]
  for h,weight in CONDITIONS:
   model.use_reachability_cost=True;model.reachability_cost_weight=weight
   x=normalized_pixels(history[None,-h:],args.device);past=torch.tensor((np.asarray(entry['warm_actions'])-mean)/std,device=args.device).float().reshape(1,2,10)[:,-(h-1):] if h>1 else a.new_zeros(1,0,10)
   cached=Cost(model,x,goal,past);info={'pixels':x[:,None].expand(1,37,h,3,224,224),'goal':goal[:,None].expand(1,37,1,3,224,224)}
   actual=model.get_cost(info,torch.cat([past[:,None].expand(1,37,h-1,10),a],2));test=cached.get_cost({},a)
   assert torch.equal(actual,test) and info['predicted_emb'].shape==(1,37,h+5,192)
   z=info['predicted_emb'];base=(z[:,:,-1]-cached.goal[:,-1:, :]).square().sum(-1)
   future=z[:,:,1:];remaining=torch.arange(h+4,0,-1,device=args.device).expand(1,37,-1)
   logits=model.reachability_head(future.flatten(0,2),cached.goal[:,-1:, :][:,None].expand_as(future).flatten(0,2),remaining.flatten())
   probability=torch.sigmoid(logits).reshape(1,37,h+4).amax(-1);manual=base*(1-weight*probability).clamp_min(.05)
   assert torch.equal(actual,manual)
   if weight==0:assert torch.equal(actual,base)
   records.append(dict(history=h,weight=weight,max_native_cost_error=float((actual-test).abs().max()),manual_full_head_exact=True,criterion_source_frames=h+4,criterion_horizon=remaining[0,0].tolist(),head_max_horizon=5))
   print('RC full preflight',args.device,h,weight,'PASS',flush=True)
  assert initial==state_hash(model.state_dict());b.save(out/'controls.json',dict(passed=True,device=args.device,script_sha256=b.sha(__file__),checkpoint_sha256=SHA,vendor_sha256={n:b.sha(VENDOR/n) for n in ['jepa.py','module.py','eval.py']},model_keys=312,records=records,statistics=meta,all_weights_buffers_unchanged=True));shutil.copytree(out,ROOT/out.name)
 except Exception as error:
  b.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,ROOT/out.name);raise
@torch.inference_mode()
def evaluate():
 torch.set_num_threads(4)
 for device in ['cpu','cuda']:
  ctl=json.loads((ROOT/f'20261005-E01-rcaux-full-{device}-preflight/controls.json').read_text());assert ctl['passed'] and ctl['script_sha256']==b.sha(__file__) and ctl['checkpoint_sha256']==SHA
 mean,std=np.asarray(ctl['statistics']['action_mean']),np.asarray(ctl['statistics']['action_std']);model=load('cuda');initial=state_hash(model.state_dict());ledger=json.loads((BANK/'ledger.json').read_text())
 for h,weight in CONDITIONS:
  model.use_reachability_cost=True;model.reachability_cost_weight=weight
  for interface in ['native','physical']:
   name=f'20261005-E01-rcaux-full-H{h}-W{weight:.2f}-{interface}-RTX';out=Path('/tmp/latent-wm-runs')/name;assert not out.exists() and not (ROOT/name).exists();out.mkdir();shutil.copy2(__file__,out/'rcaux_full_control_used.py')
   try:
    b.save(out/'config.json',dict(history=h,reachability_weight=weight,interface=interface,checkpoint=str(SOURCE),checkpoint_sha256=SHA,bank_ledger_sha256=b.sha(BANK/'ledger.json'),script_sha256=b.sha(__file__),controller_sha256=b.sha(b.__file__),hardware=torch.cuda.get_device_name(),statistics=ctl['statistics'],scope='complete published RC-aux object; H1 README/object .85 protocol, H3 port with original criterion history scoring; training/pretraining split unknown and unmatched; not paper numeric replication'))
    rows=[]
    for entry in ledger:
     j=entry['anchor'];env,history=b.restore(entry);assert np.array_equal(history,np.load(BANK/f'history_{j:03d}.npy'));history=list(history);past=list(entry['warm_actions']);state=env.agent_position.numpy().copy();assert np.array_equal(state,np.load(BANK/f'factual_states_{j:03d}.npy')[0]);states=[state];actions=[];decisions=[]
     goal=normalized_pixels(np.load(BANK/f'goal_{j:03d}.npy')[None,None],'cuda');reached=bool(np.linalg.norm(state-entry['goal_state'])<16);initial_success=reached
     for decision in range(4):
      if reached:break
      x=normalized_pixels(np.asarray(history[-h:])[None],'cuda');pa=torch.as_tensor((np.asarray(past[-10:])-mean)/std,device='cuda').float().reshape(1,2,10) if h==3 else goal.new_zeros(1,0,10);cost=Cost(model,x,goal,pa)
      if interface=='native':
       solver=swm.solver.CEMSolver(cost,num_samples=300,topk=30,n_steps=30,device='cuda',seed=105400+j*100+decision);solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True));chosen=solver.solve({})['actions'][0].numpy().reshape(25,2)*std+mean
      else:
       class PhysicalCost:
        def get_cost(self,info,a):return cost.get_cost(info,((a.reshape(1,-1,5,5,2)-a.new_tensor(mean))/a.new_tensor(std)).flatten(-2).float())
       chosen,_=b.bounded_cem(PhysicalCost(),105400+j*100+decision)
      count=0
      for t,a in enumerate(chosen):
       _,_,done,truncated,_=env.step(a.astype(np.float32));assert not truncated;state=env.agent_position.numpy().copy();reached=bool(np.linalg.norm(state-entry['goal_state'])<16);assert bool(done)==reached;states.append(state);actions.append(a);past.append(a);count+=1
       if (t+1)%5==0:history.append(env.render().copy())
       if reached:break
      decisions.append(dict(decision=decision,executed_steps=count))
     env.close();trace=out/f'trace_{j:03d}.npz';np.savez_compressed(trace,states=np.asarray(states),actions=np.asarray(actions).reshape(-1,2));rows.append(dict(anchor=j,episode=entry['episode'],goal_span=entry['goal_span'],success=reached,initial_success=initial_success,env_steps=len(actions),decisions=decisions,trace_sha256=b.sha(trace)));b.save(out/'rows.json',rows);print('RC full control',h,weight,interface,j,int(reached),flush=True)
    assert initial==state_hash(model.state_dict());b.save(out/'summary.json',[dict(goal_span=v,n=24,successes=sum(r['success'] for r in rows if r['goal_span']==v)) for v in [25,75]]);b.save(out/'complete.json',dict(completed=True,n=48,model_unchanged=True));shutil.copytree(out,ROOT/name)
   except Exception as error:
    b.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,ROOT/name);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','evaluate']);p.add_argument('--dataset',default='/tmp/latent-wm-data/tworoom.h5');p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--output');args=p.parse_args();(preflight(args) if args.mode=='preflight' else evaluate())
