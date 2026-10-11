"""Isolate geometry versus dynamics updates with the frozen Push transfer recipe."""
import argparse
import copy
import gc
import json
import os
import shutil
from pathlib import Path
import numpy as np
import torch
import effect_transfer as t
import effect_training as e

ARMS=['DYNAMICS-ONLY','GEOMETRY-ONLY'];HF=Path('/home/xiang/.cache/huggingface/latent-wm-trained')
def configure(model,arm):
 model.train()
 for name in ['encoder','projector','predictor','action_encoder','pred_proj']:
  part=getattr(model,name);active=(name in ['encoder','projector'])==(arm=='GEOMETRY-ONLY');part.requires_grad_(active)
  if not active:
   part.eval()
   for p in part.parameters():p.grad=None
 assert sum(p.requires_grad for p in model.parameters())==(204 if arm=='GEOMETRY-ONLY' else 93)
def frozen(model,arm):
 return {k:v for k,v in model.state_dict().items() if k.startswith(('encoder.','projector.'))==(arm=='DYNAMICS-ONLY')}
def batch(images,actions,rng,mean,std,device):
 anchors=rng.integers(0,32,8);branches=np.stack([rng.choice(np.array([0]+list(range(2,12))),4,replace=False) for _ in anchors])
 frames=images[anchors[:,None],branches].reshape(32,8,224,224,3)
 raw=torch.as_tensor((actions[anchors[:,None],branches]-mean)/std,device=device).float().reshape(32,7,10)
 return e.normalized_pixels(frames,device),torch.cat([raw,torch.zeros_like(raw[:,:1])],1),raw,dict(anchors=anchors.tolist(),branches=branches.tolist())
def preflight(args):
 out=Path(args.output);assert not out.exists() and not (t.ARTIFACTS/out.name).exists();out.mkdir(parents=True);shutil.copy2(__file__,out/'pusht_module_learning_used.py')
 try:
  torch.set_num_threads(4);images,actions,physical=t.load_bank(args.bank);records=[];initials=[]
  for arm in ARMS:
   model,cfg,mean,std,norm=t.load_source(args.device);initials.append(e.state_hash(model.state_dict()));configure(model,arm);before=e.state_hash(frozen(model,arm));clone=copy.deepcopy(model)
   reg=e.SIGReg(knots=17,num_proj=1024).to(args.device);x,a,raw,ids=batch(images,actions,np.random.default_rng(105800),mean,std,args.device)
   cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if args.device=='cuda' else None
   with torch.autocast(args.device,dtype=torch.bfloat16):loss,base,regularizer,aux=e.losses(model,None,reg,x,a,raw,'PLAIN',8,4)
   torch.set_rng_state(cpu)
   if cuda is not None:torch.cuda.set_rng_state_all(cuda)
   with torch.autocast(args.device,dtype=torch.bfloat16):
    info=clone.encode({'pixels':x,'action':a});z,act=info['emb'],info['act_emb'];p=[clone.predict(z[:,h:h+3],act[:,h:h+3])[:,-1] for h in range(5)];expected=(torch.stack(p,1)-z[:,3:]).square().mean()+.09*reg(z.transpose(0,1))
   assert torch.equal(loss,expected) and aux==0 and torch.isfinite(loss)
   opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=5e-5,weight_decay=1e-3);assert not opt.state;loss.backward()
   assert all(p.grad is None for p in model.parameters() if not p.requires_grad) and all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad)
   torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.);opt.step();assert len(opt.state)==(204 if arm=='GEOMETRY-ONLY' else 93) and all(int(v['step'])==1 for v in opt.state.values());assert before==e.state_hash(frozen(model,arm));model.eval()
   parity=t.queries(model,images,actions,physical,mean,std,args.device) if args.device=='cpu' else None
   from lewm_pilot import native_control
   native=native_control(model,x[:1,:3],x[:1,-1:],a[:1,:2]) if args.device=='cuda' else None
   records.append(dict(arm=arm,initial_sha256=initials[-1],frozen_sha256=before,first_batch=ids,optimizer_states=len(opt.state),loss=float(loss.detach()),native_parity=native,all12_queries_complete=bool(parity is not None)))
   print('Push module preflight',args.device,arm,'PASS',flush=True);del model,clone,opt,reg,x,a,raw,loss,base,regularizer,expected,z,act,p,info;gc.collect()
   if args.device=='cuda':torch.cuda.empty_cache()
  assert len(set(initials))==1 and e.digest(t.SOURCE)==t.SOURCE_SHA
  e.dump(out/'controls.json',dict(passed=True,device=args.device,records=records,source_sha256=e.digest(__file__),transfer_helper_sha256=e.digest(t.__file__),loss_helper_sha256=e.digest(e.__file__),checkpoint_sha256=t.SOURCE_SHA,all_frozen_parameters_buffers_unchanged=True));shutil.copytree(out,t.ARTIFACTS/out.name)
 except Exception as error:
  e.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,t.ARTIFACTS/out.name);raise
def train(args):
 torch.set_num_threads(4)
 for device in ['cpu','cuda']:
  c=json.loads((t.ARTIFACTS/f'20261005-E20-pusht-module-{device}-preflight/controls.json').read_text());assert c['passed'] and c['source_sha256']==e.digest(__file__) and c['transfer_helper_sha256']==e.digest(t.__file__) and c['loss_helper_sha256']==e.digest(e.__file__)
 name=f'20261005-E20-pusht-module-{args.arm}-A100-s0';out=Path('/tmp/latent-wm-runs')/name;cache=HF/name;assert all(not p.exists() for p in [out,cache,t.ARTIFACTS/name]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'pusht_module_learning_used.py')
 try:
  images,actions,physical=t.load_bank(args.bank);model,cfg,mean,std,norm=t.load_source('cuda');initial=e.state_hash(model.state_dict());configure(model,args.arm);unchanged=e.state_hash(frozen(model,args.arm))
  torch.manual_seed(0);torch.cuda.manual_seed_all(0);reg=e.SIGReg(knots=17,num_proj=1024).cuda();rng=np.random.default_rng(105800);params=[p for p in model.parameters() if p.requires_grad];opt=torch.optim.AdamW(params,lr=5e-5,weight_decay=1e-3);assert not opt.state
  e.dump(out/'config.json',dict(vars(args),updates=2000,batch=32,source_checkpoint=str(t.SOURCE),source_sha256=t.SOURCE_SHA,initial_sha256=initial,frozen_sha256=unchanged,normalization_sha256=norm,sample_seed=105800,objective='same grouped8x4 PLAIN five teacher future +.09 SIGReg, module permissions only',script_sha256=e.digest(__file__),transfer_helper_sha256=e.digest(t.__file__),loss_helper_sha256=e.digest(e.__file__),hardware=torch.cuda.get_device_name(),scope='one transfer trainseed, published prior split unknown, same branchdata and total updates; inactive BN fixed; not gradient-only causality, frozen encoder already mature baseline'))
  logs=[];summaries=[];tick=e.now();torch.cuda.reset_peak_memory_stats()
  for update in range(2001):
   if update in [0,600,2000]:
    saved=dict(cpu=torch.get_rng_state(),cuda=torch.cuda.get_rng_state_all(),sampler=copy.deepcopy(rng.bit_generator.state));weight=e.state_hash(model.state_dict());rows=t.queries(model,images,actions,physical,mean,std,'cuda');assert weight==e.state_hash(model.state_dict());assert unchanged==e.state_hash(frozen(model,args.arm));e.dump(out/f'queries_u{update}.json',rows)
    torch.set_rng_state(saved['cpu']);torch.cuda.set_rng_state_all(saved['cuda']);rng.bit_generator.state=saved['sampler'];snap=dict(updates=update,successes=sum(r['success'] for r in rows),n=12)
    if update:
     path=cache/f'u{update}.ckpt';torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),steps=update,config=cfg,manifest=dict(action_mean=mean.tolist(),action_std=std.tolist(),base_episodes=[],pretraining_split_unknown=True),rng=saved,module_arm=args.arm),str(path)+'.part');os.replace(str(path)+'.part',path);snap['checkpoint_sha256']=e.digest(path)
    summaries.append(snap);e.dump(out/'summary.json',summaries)
   if update==2000:break
   configure(model,args.arm);x,a,raw,ids=batch(images,actions,rng,mean,std,'cuda')
   if update==0:e.dump(out/'first_batch.json',ids)
   opt.zero_grad(set_to_none=True)
   with torch.autocast('cuda',dtype=torch.bfloat16):value,base,regularizer,aux=e.losses(model,None,reg,x,a,raw,'PLAIN',8,4)
   assert torch.isfinite(value) and aux==0;value.backward();grad=torch.nn.utils.clip_grad_norm_(params,1.);assert torch.isfinite(grad);opt.step()
   if update==0 or (update+1)%25==0:logs.append(dict(update=update+1,loss=float(value.detach()),base=float(base.detach()),sigreg=float(regularizer.detach())));e.dump(out/'training.json',logs);print('Push module train',args.arm,update+1,flush=True)
  assert all(int(v['step'])==2000 for v in opt.state.values()) and e.digest(t.SOURCE)==t.SOURCE_SHA and unchanged==e.state_hash(frozen(model,args.arm))
  e.dump(out/'accounting.json',dict(branch_items=64000,optimizer_states=len(opt.state),frozen_sha256=unchanged,train_seconds=e.now()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30,final_sampler_rng=rng.bit_generator.state));e.dump(out/'complete.json',dict(completed=True,arm=args.arm,seed=0,updates=2000));shutil.copytree(out,t.ARTIFACTS/name)
 except Exception as error:
  e.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,t.ARTIFACTS/name);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train']);p.add_argument('--bank',required=True);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--output');p.add_argument('--arm',choices=ARMS);args=p.parse_args();(preflight if args.mode=='preflight' else train)(args)
