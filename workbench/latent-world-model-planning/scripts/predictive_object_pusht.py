"""A12: matched Fast prediction objects on cached Push facts, frozen full phi."""
import argparse
import copy
import gc
import os
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import torch
from torch import nn
# Pin the published JEPA namespace before other world-model adapters load it.
import goal_policy_pusht_control as component
import predictive_object_rollout as rollout
from experience_transfer_control_audit import ROOT, WB, read, save, sha
from fixed_data_train_seed import state_hash
r=rollout.r;t=component.t;fast=r.fast
CACHE=ROOT/'20261005-E14-goalpolicy-pusht-RELEASED-features-retry1'
HF=Path('/home/xiang/.cache/huggingface/latent-wm-trained')
ARMS=['DIRECT','LOCAL','OPEN'];UPDATES=2825


class Model(r.Model):
    def __init__(self):
        nn.Module.__init__(self)
        phi,_,_,_,_=t.load_source('cpu')
        self.encoder=phi.encoder;self.projector=phi.projector
        self.encoder.eval().requires_grad_(False);self.projector.eval().requires_grad_(False)
        torch.manual_seed(113000)
        self.core=nn.ModuleDict(dict(action=fast.Embedder(input_dim=10,emb_dim=192,
            transformer_depth=3,transformer_heads=6,transformer_dim_head=32,transformer_mlp_dim=768,
            use_positional_encoding=True,use_latent_condition=True,latent_dim=192),
            predictor=fast.ARPredictor(input_dim=192,hidden_dim=192,output_dim=192,depth=6,
                value_heads=16,value_dim_head=64,mlp_dim=2048,dropout=.1,emb_dropout=0.,
                action_fusion_hidden_dim=768,action_fusion_zero_init=True,token_processing='batch'),
            projection=fast.MLP(input_dim=192,output_dim=192,hidden_dim=2048,norm_fn=nn.BatchNorm1d)))
        assert state_hash(self.core.state_dict())==read(ROOT/'20261005-E13-object-PRED-DIRECT-A100-s0/config.json')['head_initial_sha256']


def data():
    c=read(CACHE/'config.json');assert read(CACHE/'complete.json')['completed']
    assert c['source_sha256']==t.SOURCE_SHA==sha(t.SOURCE)
    for key,value in c['array_sha256'].items():assert sha(CACHE/f'{key}.npy')==value
    z=np.load(CACHE/'features.npy');actions=np.load(CACHE/'actions.npy');ep=np.load(CACHE/'episode_ids.npy');starts=[]
    for row in c['layout']:
        begin=row['cache_row'];end=begin+row['frames']
        assert (ep[begin:end]==row['episode']).all()
        # A35-action clip needs current10 and the observed endpoint at35.
        starts.extend(range(begin,end-35))
    starts=np.asarray(starts)
    assert len(starts)>0 and z.shape==(9374,192) and actions.shape==(9374,2)
    assert np.isfinite(actions[starts[:,None]+np.arange(35)]).all()
    assert np.array_equal(ep[starts],ep[starts+35])
    assert not set(ep)&set(c['excluded_fresh_eval_episodes'])
    normpath=ROOT/'20261002-pusht-native-s0/action_normalization.npz';norm=np.load(normpath)
    assert sha(normpath)==c['unused_cem_action_normalization_sha256']
    manifest=dict(base_episodes=c['training_episodes'],action_mean=norm['mean'].tolist(),action_std=norm['std'].tolist())
    return dict(features=z,actions=actions,starts=starts),dict(feature_metadata=c,manifest=manifest,normalizer_sha256=sha(normpath),legal_starts=len(starts))


def sample(d,cfg,rng,device):
    ix=rng.choice(d['starts'],128,replace=True)
    z=torch.tensor(d['features'][ix[:,None]+np.arange(10,36,5)],device=device)
    a=(d['actions'][ix[:,None]+np.arange(10,35)]-np.asarray(cfg['manifest']['action_mean']))/np.asarray(cfg['manifest']['action_std'])
    return z,torch.tensor(a,device=device).float().reshape(128,5,10),ix.tolist()


def objective(net,z,a,arm,device):
    return rollout.loss(net,z,a,device) if arm=='OPEN' else r.objective(net,z,a,arm,device)


def name(arm):return f'20261005-E13-pusht-object-{arm}-RTX-s0'


def preflight(arm,device):
    out=ROOT/(name(arm)+f'-{device}-preflight');assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        d,cfg=data();net=Model().to(device);net.training_mode();frozen=net.frozen_hash();initial=state_hash(net.core.state_dict())
        z,a,ids=sample(d,cfg,np.random.default_rng(113100),device)
        assert np.array_equal(z.cpu().numpy(),d['features'][np.asarray(ids)[:,None]+np.arange(10,36,5)])
        clone=copy.deepcopy(net);cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if device=='cuda' else None
        actual=objective(net,z,a,arm,device);torch.set_rng_state(cpu)
        if cuda is not None:torch.cuda.set_rng_state_all(cuda)
        with torch.autocast(device,dtype=torch.bfloat16):
            if arm=='DIRECT':
                ap=clone.core['action'](a,latent=z[:,0,None]);pr=clone.core['predictor'](z[:,0,None],ap)
                predicted=clone.core['projection'](pr.flatten(0,1)).reshape(pr.shape)
            elif arm=='LOCAL':
                current=z[:,:5].flatten(0,1);ap=clone.core['action'](a.reshape(640,1,10),latent=current[:,None]);pr=clone.core['predictor'](current[:,None],ap)
                predicted=clone.core['projection'](pr[:,0]).reshape(128,5,192)
            else:
                current=z[:,0];values=[]
                for step in range(5):
                    ap=clone.core['action'](a[:,step:step+1],latent=current[:,None]);pr=clone.core['predictor'](current[:,None],ap)
                    current=clone.core['projection'](pr[:,0]);values.append(current)
                predicted=torch.stack(values,1)
            expected=(predicted-z[:,1:]).square().mean()
        assert torch.equal(actual,expected) and torch.isfinite(actual)
        opt=torch.optim.AdamW(net.core.parameters(),lr=5e-5,weight_decay=.001);assert not opt.state
        actual.backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in net.core.parameters())
        assert all(p.grad is None for p in list(net.encoder.parameters())+list(net.projector.parameters()))
        torch.nn.utils.clip_grad_norm_(net.core.parameters(),1.);opt.step()
        assert all(int(v['step'])==1 for v in opt.state.values()) and frozen==net.frozen_hash()
        clone.eval();clone.zero_grad(set_to_none=True)
        with torch.inference_mode():
            current=z[:4,0];before=clone.prefix(current,a[:4]) if arm=='DIRECT' else torch.stack(rollout.predictions(clone,z[:4],a[:4]),1)
            changed=z[:4].clone();changed[:,1:]+=100
            after=clone.prefix(changed[:,0],a[:4]) if arm=='DIRECT' else torch.stack(rollout.predictions(clone,changed,a[:4]),1)
            assert torch.equal(before,after)
            if arm=='DIRECT':
                aa=a[:4].clone();aa[:,3:]+=100;assert torch.equal(before[:,:3],clone.prefix(current,aa)[:,:3])
            terminal=clone.terminal(z[:1,0].expand(7,-1),a[:7],'DIRECT' if arm=='DIRECT' else 'LOCAL')
            single=torch.cat([clone.terminal(z[:1,0],a[j:j+1],'DIRECT' if arm=='DIRECT' else 'LOCAL') for j in range(7)])
            assert torch.allclose(terminal,single,atol=2e-4,rtol=1e-5)
        if arm=='OPEN':
            values=rollout.predictions(clone,z,a);values[0].retain_grad();(values[-1]-z[:,-1]).square().mean().backward()
            assert values[0].grad is not None and torch.isfinite(values[0].grad).all() and values[0].grad.abs().sum()>0
        save(out/'controls.json',dict(passed=True,arm=arm,device=device,head_initial_sha256=initial,frozen_phi_sha256=frozen,first_ids=ids,manual_loss_exact=True,target_not_prediction_input=True,last_loss_to_first_prediction_checked=arm=='OPEN',batch_subset_error=float((terminal-single).abs().max()),data_metadata=cfg,script_sha256=sha(__file__),rollout_component_sha256=sha(rollout.__file__),source_loader_sha256=sha(t.__file__),vendor_sha256=sha(r.VENDOR/'module.py')))
        print('Push prediction actual preflight',arm,device,'PASS',flush=True)
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


def train(arm):
    for device in ['cpu','cuda']:
        pre=read(ROOT/(name(arm)+f'-{device}-preflight')/'controls.json');assert pre['passed'] and pre['script_sha256']==sha(__file__)
    out=ROOT/name(arm);cache=HF/name(arm);assert not out.exists() and not cache.exists();out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        d,cfg=data();net=Model().cuda();initial=state_hash(net.core.state_dict());frozen=net.frozen_hash()
        assert initial==pre['head_initial_sha256'] and frozen==pre['frozen_phi_sha256']
        torch.save(net.core.state_dict(),cache/'initial_head.pt');rng=np.random.default_rng(113100);torch.manual_seed(0);torch.cuda.manual_seed_all(0)
        opt=torch.optim.AdamW(net.core.parameters(),lr=5e-5,weight_decay=.001);logs=[];import time;tick=time.perf_counter();torch.cuda.reset_peak_memory_stats()
        save(out/'config.json',dict(task='pusht',arm=arm,train_seed=0,updates=UPDATES,batch=128,head_seed=113000,sampler_seed=113100,head_initial_sha256=initial,frozen_phi_sha256=frozen,data_metadata=cfg,script_sha256=sha(__file__),rollout_component_sha256=sha(rollout.__file__),repeat_component_sha256=sha(r.__file__),source_loader_sha256=sha(t.__file__),vendor_sha256=sha(r.VENDOR/'module.py'),hardware=torch.cuda.get_device_name(),scope='Known shared-capacity prediction objects, same86facts/targets/examples/initialization; frozen published phi including BN, published pretraining overlap unknown. Local teacher, open BPTT and direct have different train conditioning/BN calls. One source, fixed final checkpoint, no numeric paper replication or novel method claim.'))
        for update in range(1,UPDATES+1):
            net.training_mode();z,a,ids=sample(d,cfg,rng,'cuda')
            if update==1:save(out/'first_ids.json',ids)
            opt.zero_grad(set_to_none=True);value=objective(net,z,a,arm,'cuda');assert torch.isfinite(value);value.backward()
            norm=torch.nn.utils.clip_grad_norm_(net.core.parameters(),1.);assert torch.isfinite(norm);opt.step()
            if update==1 or update%25==0:
                logs.append(dict(update=update,loss=float(value.detach())));save(out/'training.json',logs);print('Push prediction train',arm,update,flush=True)
        assert frozen==net.frozen_hash() and all(int(v['step'])==UPDATES for v in opt.state.values())
        path=cache/'u2825.ckpt';torch.save(dict(state_dict=net.state_dict(),optimizer=opt.state_dict(),steps=UPDATES,arm=arm,train_seed=0,manifest=cfg['manifest'],sampler=rng.bit_generator.state,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),str(path)+'.part');os.replace(str(path)+'.part',path)
        save(out/'summary.json',dict(checkpoint_sha256=sha(path),total_clips=361600,total_future_targets=1808000,frozen_phi_sha256=frozen,final_sampler=rng.bit_generator.state,head_initial_sha256=initial,optimizer_states=len(opt.state),train_seconds=time.perf_counter()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30))
        save(out/'complete.json',dict(completed=True,task='pusht',arm=arm,train_seed=0,updates=UPDATES))
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


def queue(arm):
    out=ROOT/(name(arm)+'-pipeline');assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        for device in ['cpu','cuda']:subprocess.run([sys.executable,'-u',__file__,'preflight','--arm',arm,'--device',device],check=True)
        subprocess.run([sys.executable,'-u',__file__,'train','--arm',arm],check=True)
        save(out/'complete.json',dict(completed=True,arm=arm))
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train','queue']);p.add_argument('--arm',choices=ARMS,required=True);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');a=p.parse_args();torch.set_num_threads(4)
    if a.mode=='queue':queue(a.arm)
    elif a.mode=='preflight':preflight(a.arm,a.device)
    else:train(a.arm)
