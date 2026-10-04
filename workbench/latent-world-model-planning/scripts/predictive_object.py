"""Fixed pixel geometry with official Fast components: prefix or one-step targets."""
import argparse
import copy
import gc
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
import numpy as np
import torch
from torch import nn
import matched_learning as m
import geometry_experience as g
from fixed_data_train_seed import load_cache,normalized_pixels,state_hash

VENDOR=m.WB/'vendor/fast-lewm'
spec=importlib.util.spec_from_file_location('fixed_geometry_fast_components',VENDOR/'module.py')
fast=importlib.util.module_from_spec(spec);sys.modules[spec.name]=fast;spec.loader.exec_module(fast)
UPDATES=2825;BATCH=128;ARMS=['DIRECT','LOCAL']


class Model(nn.Module):
    def __init__(self,config,geometry):
        super().__init__();base,_=m.make_model(config,0,'ABS')
        prior=torch.load(g.SOURCES[geometry],map_location='cpu',weights_only=False)['state_dict']
        state=base.state_dict()
        for k in state:
            if k.startswith(g.PREFIX):state[k]=prior[k].clone()
        base.load_state_dict(state,strict=True)
        self.encoder=base.encoder;self.projector=base.projector
        self.encoder.eval().requires_grad_(False);self.projector.eval().requires_grad_(False)
        torch.manual_seed(113000)
        self.core=nn.ModuleDict(dict(action=fast.Embedder(input_dim=10,emb_dim=192,
            transformer_depth=3,transformer_heads=6,transformer_dim_head=32,transformer_mlp_dim=768,
            use_positional_encoding=True,use_latent_condition=True,latent_dim=192),
            predictor=fast.ARPredictor(input_dim=192,hidden_dim=192,output_dim=192,depth=6,
                value_heads=16,value_dim_head=64,mlp_dim=2048,dropout=.1,emb_dropout=0.,
                action_fusion_hidden_dim=768,action_fusion_zero_init=True,token_processing='batch'),
            projection=fast.MLP(input_dim=192,output_dim=192,hidden_dim=2048,norm_fn=nn.BatchNorm1d)))
    def encode_pixels(self,x):
        shape=x.shape[:-3];cls=self.encoder(x.reshape(-1,*x.shape[-3:]),interpolate_pos_encoding=True).last_hidden_state[:,0]
        return self.projector(cls).reshape(*shape,192)
    def prefix(self,z,a):
        p=self.core['action'](a,latent=z[:,None]);y=self.core['predictor'](z[:,None],p)
        return self.core['projection'](y.flatten(0,1)).reshape(y.shape)
    def local_targets(self,z,a):
        b,h,_=z.shape;return self.prefix(z.flatten(0,1),a.flatten(0,1)[:,None]).reshape(b,h,192)
    def terminal(self,z,a,arm):
        if arm=='DIRECT':return self.prefix(z,a)[:,-1]
        for h in range(a.shape[1]):z=self.prefix(z,a[:,h:h+1])[:,0]
        return z
    def training_mode(self):
        self.core.train();self.encoder.eval();self.projector.eval()
    def frozen_hash(self):return state_hash({k:v for k,v in self.state_dict().items() if k.startswith(g.PREFIX)})


class Cost:
    def __init__(self,model,current,goal,arm):
        self.model=model;self.z=model.encode_pixels(current);self.goal=model.encode_pixels(goal);self.arm=arm
    def get_cost(self,info,actions):
        assert actions.shape[0]==1 and actions.shape[2:]==(5,10)
        end=self.model.terminal(self.z.expand(actions.shape[1],-1),actions[0],self.arm)
        return (end-self.goal).square().sum(-1)[None]


def cache_path(geometry):return Path('/tmp/latent-wm-data')/f'E13-object-{geometry}-frozen-features'
def load_data(geometry):
    p=cache_path(geometry);cfg=json.loads((p/'config.json').read_text())
    assert cfg['source_sha256']==m.digest(g.SOURCES[geometry]) and cfg['vendor_module_sha256']==m.digest(VENDOR/'module.py')
    arrays={k:np.load(p/f'{k}.npy',mmap_mode='r') for k in ['features','actions','starts']}
    assert json.loads((p/'complete.json').read_text())['completed']
    assert all(m.digest(p/f'{k}.npy')==v for k,v in cfg['array_sha256'].items())
    return arrays,cfg
@torch.inference_mode()
def features(args):
    out=cache_path(args.geometry);name=f'20261005-E13-object-{args.geometry}-features'
    assert not out.exists() and not (m.ROOT/name).exists();out.mkdir(parents=True)
    images,actions,_,_,manifest,config,meta=load_cache(args.cache)
    model=Model(config,args.geometry).cuda().eval();frozen=model.frozen_hash();values=[]
    for start in range(0,len(images),64):
        x=normalized_pixels(np.asarray(images[start:start+64]),'cuda');values.append(model.encode_pixels(x).cpu().numpy())
    phi=np.concatenate(values);assert phi.shape==(9295,192) and np.isfinite(phi).all() and frozen==model.frozen_hash()
    starts=np.concatenate([np.arange(v['cache_row'],v['cache_row']+v['frames']-35) for v in meta['layout']]);assert len(starts)==5795
    assert np.isfinite(actions[starts[:,None]+np.arange(35)]).all()
    for k,value in dict(features=phi,actions=actions,starts=starts).items():np.save(out/f'{k}.npy',value)
    m.dump(out/'config.json',dict(geometry=args.geometry,source_sha256=m.digest(g.SOURCES[args.geometry]),frozen_phi_sha256=frozen,
        architecture=config,manifest=manifest,cache_manifest_sha256=m.digest(Path(args.cache)/'cache_manifest.json'),
        pixel_source_sha256=meta['files']['pixels.npy']['sha256'],vendor_module_sha256=m.digest(VENDOR/'module.py'),script_sha256=m.digest(__file__),
        array_sha256={k:m.digest(out/f'{k}.npy') for k in ['features','actions','starts']},hardware=torch.cuda.get_device_name(),
        scope='Frozen training observations only, FP32 batches64, no physical states/evaluation goals/outcomes; different numeric encoding from old bf16 pixel trainer'))
    m.dump(out/'complete.json',dict(completed=True,n=9295));shutil.copytree(out,m.ROOT/name)
    print('frozen features',args.geometry,'9295 PASS',flush=True)
def sample(d,cfg,rng,device):
    ix=rng.choice(d['starts'],128,replace=True)
    phi=np.asarray(d['features'][ix[:,None]+np.arange(10,36,5)])
    actions=np.asarray(d['actions'][ix[:,None]+np.arange(10,35)])
    normalized=(actions-np.asarray(cfg['manifest']['action_mean']))/np.asarray(cfg['manifest']['action_std'])
    return torch.tensor(phi,device=device),torch.tensor(normalized,device=device).float().reshape(128,5,10),ix.tolist()
def objective(model,z,a,arm,device):
    with torch.autocast(device,dtype=torch.bfloat16):
        y=model.prefix(z[:,0],a) if arm=='DIRECT' else model.local_targets(z[:,:5],a)
        return (y-z[:,1:]).square().mean()
def preflight(args):
    d,cfg=load_data(args.geometry);name=f'20261005-E13-object-{args.geometry}-{args.device}-preflight-retry1';out=m.ROOT/name
    assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'predictive_object_used.py');records=[];initials=[]
    for arm in ARMS:
        model=Model(cfg['architecture'],args.geometry).to(args.device);model.training_mode();frozen=model.frozen_hash();assert frozen==cfg['frozen_phi_sha256'];initials.append(state_hash(model.core.state_dict()))
        z,a,ids=sample(d,cfg,np.random.default_rng(113100),args.device)
        assert z.shape==(128,6,192) and a.shape==(128,5,10) and not z.requires_grad
        assert np.array_equal(z.cpu().numpy(),np.asarray(d['features'][np.asarray(ids)[:,None]+np.arange(10,36,5)]))
        clone=copy.deepcopy(model);cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if args.device=='cuda' else None
        loss=objective(model,z,a,arm,args.device);torch.set_rng_state(cpu)
        if cuda is not None:torch.cuda.set_rng_state_all(cuda)
        with torch.autocast(args.device,dtype=torch.bfloat16):
            if arm=='DIRECT':reference=clone.prefix(z[:,0],a)
            else:
                flat=z[:,:5].reshape(640,192);actions=a.reshape(640,1,10)
                prefix=clone.core['action'](actions,latent=flat[:,None]);p=clone.core['predictor'](flat[:,None],prefix)
                reference=clone.core['projection'](p.reshape(640,192)).reshape(128,5,192)
            expected=(reference-z[:,1:]).square().mean()
        assert torch.equal(loss,expected) and torch.isfinite(loss)
        opt=torch.optim.AdamW(model.core.parameters(),lr=5e-5,weight_decay=.001);assert not opt.state;loss.backward()
        assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.core.parameters())
        assert all(p.grad is None for p in list(model.encoder.parameters())+list(model.projector.parameters()))
        torch.nn.utils.clip_grad_norm_(model.core.parameters(),1.);opt.step();assert frozen==model.frozen_hash() and all(int(v['step'])==1 for v in opt.state.values())
        model.eval()
        with torch.inference_mode():
            before=model.prefix(z[:4,0],a[:4]);perturbed=a[:4].clone();perturbed[:,3:]+=5
            after=model.prefix(z[:4,0],perturbed)
            causal_error=float((before[:,:3]-after[:,:3]).abs().max());assert causal_error<1e-5
            all_scores=model.terminal(z[:1,0].expand(7,-1),a[:7],arm)
            singles=torch.cat([model.terminal(z[:1,0],a[j:j+1],arm) for j in range(7)])
            subset_error=float((all_scores-singles).abs().max());assert torch.allclose(all_scores,singles,atol=2e-4,rtol=1e-5)
            bank=m.ROOT/'20261004-E20-fresh-control-bank48'
            current=normalized_pixels(np.load(bank/'history_000.npy')[-1: ],args.device)
            goal=normalized_pixels(np.load(bank/'goal_000.npy')[None],args.device)
            physical=np.random.default_rng(113201).uniform(-1,1,(1,37,5,5,2))
            controls=torch.tensor((physical-np.asarray(cfg['manifest']['action_mean']))/np.asarray(cfg['manifest']['action_std']),device=args.device).float().flatten(-2)
            cached=Cost(model,current,goal,arm);actual=cached.get_cost({},controls)
            direct_z=model.encode_pixels(current).expand(37,-1);goal_z=model.encode_pixels(goal)
            if arm=='DIRECT':
                ap=model.core['action'](controls[0],latent=direct_z[:,None]);pr=model.core['predictor'](direct_z[:,None],ap)
                manual_end=model.core['projection'](pr.flatten(0,1)).reshape(37,5,192)[:,-1]
            else:
                for h in range(5):
                    ap=model.core['action'](controls[0,:,h:h+1],latent=direct_z[:,None]);pr=model.core['predictor'](direct_z[:,None],ap)
                    direct_z=model.core['projection'](pr[:,0])
                manual_end=direct_z
            manual=(manual_end-goal_z).square().sum(-1)[None]
            cost_error=float((actual-manual).abs().max());assert torch.equal(actual,manual) and frozen==model.frozen_hash()
        records.append(dict(arm=arm,head_initial_sha256=initials[-1],first_ids=ids,optimizer_states=len(opt.state),frozen_phi_sha256=frozen,causal_error=causal_error,subset_error=subset_error,max_full_cost_error=cost_error))
        print('object preflight',args.geometry,args.device,arm,'PASS',flush=True)
        del model,clone,opt,loss,reference,expected,z,a,before,after,all_scores,singles
        gc.collect()
        if args.device=='cuda':torch.cuda.empty_cache()
    assert len(set(initials))==1
    m.dump(out/'controls.json',dict(passed=True,records=records,script_sha256=m.digest(__file__),vendor_module_sha256=m.digest(VENDOR/'module.py')))
def train(args):
    d,cfg=load_data(args.geometry)
    for device in ['cpu','cuda']:
        control=json.loads((m.ROOT/f'20261005-E13-object-{args.geometry}-{device}-preflight-retry1/controls.json').read_text())
        assert control['passed'] and control['script_sha256']==m.digest(__file__)
    name=f'20261005-E13-object-{args.geometry}-{args.arm}-A100-s0';out=Path('/tmp/latent-wm-runs')/name;cache=m.HF/name
    assert all(not p.exists() for p in [out,cache,m.ROOT/name]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'predictive_object_used.py')
    model=Model(cfg['architecture'],args.geometry).cuda();frozen=model.frozen_hash();assert frozen==cfg['frozen_phi_sha256'];head=state_hash(model.core.state_dict());assert head==control['records'][0]['head_initial_sha256']
    torch.save(model.core.state_dict(),cache/'initial_head.pt');rng=np.random.default_rng(113100);torch.manual_seed(0);torch.cuda.manual_seed_all(0)
    opt=torch.optim.AdamW(model.core.parameters(),lr=5e-5,weight_decay=.001);logs=[];tick=m.now();torch.cuda.reset_peak_memory_stats()
    m.dump(out/'config.json',dict(geometry=args.geometry,arm=args.arm,updates=UPDATES,batch=128,feature_metadata=cfg,
        head_initial_sha256=head,script_sha256=m.digest(__file__),head_parameters=sum(p.numel() for p in model.core.parameters()),scope='one exploratory source; fixed phi, single current frame, official Fast shared capacity/init; LOCAL teacher training and recursive deployment vs DIRECT prefix; prior budgets differ; no novelty claim'))
    for step in range(1,UPDATES+1):
        model.training_mode();z,a,ids=sample(d,cfg,rng,'cuda')
        if step==1:m.dump(out/'first_ids.json',ids)
        opt.zero_grad(set_to_none=True);value=objective(model,z,a,args.arm,'cuda');assert torch.isfinite(value);value.backward()
        grad=torch.nn.utils.clip_grad_norm_(model.core.parameters(),1.);assert torch.isfinite(grad);opt.step()
        if step==1 or step%25==0:logs.append(dict(update=step,loss=float(value.detach())));m.dump(out/'training.json',logs);print('object train',args.geometry,args.arm,step,flush=True)
    assert frozen==model.frozen_hash() and all(int(v['step'])==UPDATES for v in opt.state.values())
    checkpoint=cache/'u2825.ckpt';torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),steps=UPDATES,geometry=args.geometry,arm=args.arm,config=cfg['architecture'],manifest=cfg['manifest'],sampler=rng.bit_generator.state,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),str(checkpoint)+'.part');os.replace(str(checkpoint)+'.part',checkpoint)
    m.dump(out/'summary.json',dict(checkpoint_sha256=m.digest(checkpoint),total_clips=361600,total_future_targets=1808000,optimizer_states=len(opt.state),frozen_phi_sha256=frozen,final_sampler=rng.bit_generator.state,train_seconds=m.now()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30))
    m.dump(out/'complete.json',dict(completed=True,geometry=args.geometry,arm=args.arm,updates=UPDATES));shutil.copytree(out,m.ROOT/name)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['features','preflight','train']);p.add_argument('--geometry',required=True,choices=g.GEOMETRIES);p.add_argument('--arm',choices=ARMS);p.add_argument('--device',default='cpu',choices=['cpu','cuda']);p.add_argument('--cache',default='/tmp/latent-wm-data/E16-base100-trainseed-cache');args=p.parse_args();torch.set_num_threads(4)
    {'features':features,'preflight':preflight,'train':train}[args.mode](args)
