"""E20 fixed geometry x experience pilot; common reset dynamics, no new aux loss."""
import argparse
import copy
import gc
import json
import os
import shutil
from pathlib import Path
import numpy as np
import torch
import matched_learning as m  # Official namespace before shared data/loss helpers.
import experience_utilization as u
import effect_training as e

GEOMETRIES=['PRED','VALUE'];DATA=['FACT','MIX'];UPDATES=2825;BATCH=128
PREFIX=('encoder.','projector.')
SOURCES={
 'PRED':m.HF/'20261004-E01-matched-ABS-A100-s0/u5650.ckpt',
 'VALUE':m.HF/'20261004-E14-VGIQL-SEPARATE-A100-s0/value_phase_u2825.ckpt'}
VALUE_FINAL=m.HF/'20261004-E14-VGIQL-SEPARATE-A100-s0/u5650.ckpt'
def portion(model,frozen=True):
 return {k:v for k,v in model.state_dict().items() if k.startswith(PREFIX)==frozen}
def construct(d,geometry,device):
 model,init=m.make_model(d['config'],0,'ABS'); common_dynamic=e.state_hash(portion(model,False))
 c=torch.load(SOURCES[geometry],map_location='cpu',weights_only=False)
 assert c['steps']==(5650 if geometry=='PRED' else 2825)
 if geometry=='PRED':assert c['config']==d['config'] and c['manifest']==d['manifest']
 else:
  final=torch.load(VALUE_FINAL,map_location='cpu',weights_only=False)
  assert final['config']==d['config'] and final['manifest']==d['manifest']
  assert all(torch.equal(v,final['state_dict'][k]) for k,v in c['state_dict'].items() if k.startswith(PREFIX))
 state=model.state_dict();keys={k for k in state if k.startswith(PREFIX)}
 assert keys=={k for k in c['state_dict'] if k.startswith(PREFIX)}
 for k in keys:state[k]=c['state_dict'][k].clone()
 model.load_state_dict(state,strict=True); assert e.state_hash(portion(model,False))==common_dynamic
 assert all(torch.equal(model.state_dict()[k],c['state_dict'][k]) for k in keys)
 model=model.to(device);m.configure_phase(model,'dynamics')
 assert sum(p.requires_grad for p in model.parameters())==93 and sum(not p.requires_grad for p in model.parameters())==204
 return model,dict(**init,geometry_checkpoint=str(SOURCES[geometry]),geometry_checkpoint_sha256=e.digest(SOURCES[geometry]),geometry_prior_updates=c['steps'],common_dynamic_initial_sha256=common_dynamic,frozen_geometry_sha256=e.state_hash(portion(model)),value_final_checkpoint_sha256=e.digest(VALUE_FINAL) if geometry=='VALUE' else None)
def sample(d,arm,brng,rrng):
 n=64 if arm=='MIX' else 0
 anchors=brng.integers(0,32,n);branches=brng.choice(u.LEGAL,n,replace=True);ix=rrng.choice(d['starts'],128-n,replace=True)
 frames=np.concatenate([d['branch_images'][anchors,branches],d['images'][ix[:,None]+u.OFFSETS]])
 controls=np.concatenate([d['branch_actions'][anchors,branches],d['actions'][ix[:,None]+np.arange(35)]])
 assert frames.shape==(128,8,224,224,3) and controls.shape==(128,35,2) and np.isfinite(controls).all()
 return frames,controls,dict(branch_anchors=anchors.tolist(),branch_ids=branches.tolist(),replay_cache_starts=ix.tolist(),new_count=n,old_count=128-n)
def tensors(frames,actions,manifest,device):
 raw=torch.as_tensor((actions-np.asarray(manifest['action_mean']))/np.asarray(manifest['action_std']),device=device).float().reshape(128,7,10)
 return e.normalized_pixels(frames,device),torch.cat([raw,torch.zeros_like(raw[:,:1])],1)
def loss(model,x,a,device):
 with torch.autocast(device,dtype=torch.bfloat16):
  pred,z,_=e.prediction(model,x,a)
  assert not z.requires_grad
  return (pred-z[:,3:]).square().mean()
def optimizer(model):return torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=5e-5,weight_decay=1e-3)
def step(model,opt,value):
 assert torch.isfinite(value);value.backward()
 assert all(p.grad is None for p in model.parameters() if not p.requires_grad)
 assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad)
 grad=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.);assert torch.isfinite(grad);opt.step()
def preflight(args):
 out=Path(args.output);assert not out.exists() and not (m.ROOT/out.name).exists();out.mkdir(parents=True);shutil.copy2(__file__,out/'geometry_experience_used.py')
 try:
  torch.set_num_threads(4);d=u.data(args);records=[];initials=[]
  for geometry in GEOMETRIES:
   for arm in DATA:
    model,source=construct(d,geometry,args.device);initials.append(source['common_dynamic_initial_sha256'])
    frames,actions,ids=sample(d,arm,np.random.default_rng(110800),np.random.default_rng(110900))
    n=ids['new_count'];ix=np.asarray(ids['replay_cache_starts']);anchors=np.asarray(ids['branch_anchors'],dtype=int);branches=np.asarray(ids['branch_ids'],dtype=int)
    assert np.array_equal(frames[n:],d['images'][ix[:,None]+u.OFFSETS]) and np.array_equal(actions[n:],d['actions'][ix[:,None]+np.arange(35)])
    assert np.array_equal(frames[:n],d['branch_images'][anchors,branches]) and np.array_equal(actions[:n],d['branch_actions'][anchors,branches])
    assert set(ids['branch_anchors'])<=set(range(32)) and 1 not in ids['branch_ids']
    x,a=tensors(frames,actions,d['manifest'],args.device);clone=copy.deepcopy(model)
    rng=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if args.device=='cuda' else None
    value=loss(model,x,a,args.device);torch.set_rng_state(rng)
    if cuda is not None:torch.cuda.set_rng_state_all(cuda)
    with torch.autocast(args.device,dtype=torch.bfloat16):
     info=clone.encode({'pixels':x,'action':a});z,act=info['emb'],info['act_emb']
     predictions=[clone.predict(z[:,h:h+3],act[:,h:h+3])[:,-1] for h in range(5)]
     reference=((torch.stack(predictions,1)-z[:,3:])**2).mean()
    assert torch.equal(value,reference)
    opt=optimizer(model);assert not opt.state;step(model,opt,value)
    assert len(opt.state)==93 and all(int(v['step'])==1 for v in opt.state.values())
    assert source['frozen_geometry_sha256']==e.state_hash(portion(model)) and source['common_dynamic_initial_sha256']!=e.state_hash(portion(model,False))
    model.eval();parity=m.native_control(model,x[:1,:3],x[:1,-1:],a[:1,:2]) if args.device=='cuda' else None
    assert e.digest(SOURCES[geometry])==source['geometry_checkpoint_sha256']
    records.append(dict(geometry=geometry,arm=arm,source=source,first_batch=ids,loss=float(value.detach()),optimizer_states=93,native_parity=parity))
    print('geometry preflight',args.device,geometry,arm,'PASS',flush=True)
    del model,clone,opt,x,a,value,reference,info,z,act,predictions;gc.collect()
    if args.device=='cuda':torch.cuda.empty_cache()
  assert len(set(initials))==1
  e.dump(out/'controls.json',dict(passed=True,device=args.device,records=records,batch128=True,five_teacher_targets_manual=True,all_frozen_parameters_and_buffers_unchanged=True,all93_dynamic_gradients_finite=True,common_reset_dynamics=True,source_sha256=e.digest(__file__),data_helper_sha256=e.digest(u.__file__),prediction_helper_sha256=e.digest(e.__file__),model_helper_sha256=e.digest(m.__file__)))
  shutil.copytree(out,m.ROOT/out.name)
 except Exception as error:
  e.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,m.ROOT/out.name);raise
def train(args):
 torch.set_num_threads(4)
 for device in ['cpu','cuda']:
  c=json.loads((m.ROOT/f'20261005-E20-geometry-{device}-preflight/controls.json').read_text())
  assert c['passed'] and c['source_sha256']==e.digest(__file__) and c['data_helper_sha256']==e.digest(u.__file__) and c['prediction_helper_sha256']==e.digest(e.__file__) and c['model_helper_sha256']==e.digest(m.__file__)
 name=f'20261005-E20-geometry-{args.geometry}-{args.arm}-A100-s0';out=Path('/tmp/latent-wm-runs')/name;cache=m.HF/name
 assert all(not p.exists() for p in [out,cache,m.ROOT/name]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'geometry_experience_used.py')
 try:
  d=u.data(args);model,source=construct(d,args.geometry,'cuda');opt=optimizer(model);assert not opt.state
  torch.manual_seed(0);torch.cuda.manual_seed_all(0);brng=np.random.default_rng(110800);rrng=np.random.default_rng(110900)
  e.dump(out/'config.json',dict(vars(args),source=source,updates=UPDATES,batch=BATCH,objective='frozen encoder/projector including BN; five teacher future MSE; no SIGReg/aux',script_sha256=e.digest(__file__),data_helper_sha256=e.digest(u.__file__),model_helper_sha256=e.digest(m.__file__),prediction_helper_sha256=e.digest(e.__file__),cache_manifest_sha256=e.digest(Path(args.cache)/'cache_manifest.json'),bank_complete_sha256=e.digest(Path(args.bank)/'complete.json'),hardware=torch.cuda.get_device_name(),scope='one exploratory source; geometry priors have different training objectives and budgets; data effect only within fixed geometry; FACT/MIX differ in purchased branch exposure; common reset dynamics; not novel method or pure geometry-objective causality'))
  mean,std=np.asarray(d['manifest']['action_mean']),np.asarray(d['manifest']['action_std']);logs=[];summaries=[];tick=e.now();torch.cuda.reset_peak_memory_stats()
  for update in range(1,UPDATES+1):
   m.configure_phase(model,'dynamics');frames,actions,ids=sample(d,args.arm,brng,rrng)
   if update==1:e.dump(out/'first_batch.json',ids)
   x,a=tensors(frames,actions,d['manifest'],'cuda');opt.zero_grad(set_to_none=True);value=loss(model,x,a,'cuda');step(model,opt,value)
   if update==1 or update%25==0:
    logs.append(dict(update=update,loss=float(value.detach())));e.dump(out/'training.json',logs);print('geometry train',args.geometry,args.arm,update,flush=True)
   if update in [600,UPDATES]:
    frozen=e.state_hash(portion(model));assert frozen==source['frozen_geometry_sha256']
    saved=dict(cpu=torch.get_rng_state(),cuda=torch.cuda.get_rng_state_all(),branch=copy.deepcopy(brng.bit_generator.state),replay=copy.deepcopy(rrng.bit_generator.state))
    full=e.state_hash(model.state_dict());queries=e.audit_candidates(model,d['branch_images'],d['branch_actions'],d['states'],mean,std)
    assert full==e.state_hash(model.state_dict());e.dump(out/f'queries_u{update}.json',queries)
    torch.set_rng_state(saved['cpu']);torch.cuda.set_rng_state_all(saved['cuda']);brng.bit_generator.state=saved['branch'];rrng.bit_generator.state=saved['replay']
    path=cache/f'u{update}.ckpt';torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),steps=update,config=d['config'],manifest=d['manifest'],rng=saved,geometry_source=source),str(path)+'.part');os.replace(str(path)+'.part',path)
    summaries.append(dict(updates=update,successes=sum(r['success'] for r in queries),n=12,checkpoint_sha256=e.digest(path)));e.dump(out/'summary.json',summaries)
  assert len(opt.state)==93 and all(int(v['step'])==UPDATES for v in opt.state.values()) and e.digest(SOURCES[args.geometry])==source['geometry_checkpoint_sha256']
  e.dump(out/'accounting.json',dict(total_items=BATCH*UPDATES,branch_items=(64 if args.arm=='MIX' else 0)*UPDATES,replay_items=(64 if args.arm=='MIX' else 128)*UPDATES,train_seconds=e.now()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30,frozen_geometry_sha256=e.state_hash(portion(model)),common_dynamic_initial_sha256=source['common_dynamic_initial_sha256'],final_branch_rng=brng.bit_generator.state,final_replay_rng=rrng.bit_generator.state));e.dump(out/'complete.json',dict(completed=True,geometry=args.geometry,arm=args.arm,seed=0,updates=UPDATES));shutil.copytree(out,m.ROOT/name)
 except Exception as error:
  e.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,m.ROOT/name);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train']);p.add_argument('--cache',required=True);p.add_argument('--bank',required=True);p.add_argument('--geometry',choices=GEOMETRIES);p.add_argument('--arm',choices=DATA);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--output');args=p.parse_args();(preflight if args.mode=='preflight' else train)(args)
