"""Pinned GC-IDM component on existing fact data; fixed endpoint, no CEM."""
import argparse
import dataclasses
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sys
import numpy as np
import torch
import torch.nn.functional as F
from fixed_data_train_seed import state_hash
from experience_transfer_control_audit import ROOT,WB,read,save,sha

VENDOR=WB/'vendor/gc-idm'
for name,file in [('goal_policy_official_model','idm/model.py'),('goal_policy_official_dataset','idm/dataset.py')]:
    spec=importlib.util.spec_from_file_location(name,VENDOR/file)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    globals()[name]=mod
ARMS=['GC-IDM','GCBC-MATCHED','PAIRWISE'];GEOMETRIES=['PRED','VALUE'];EPOCHS=50;BATCH=1024
HF=Path('/home/xiang/.cache/huggingface/latent-wm-derived')
META=Path('/tmp/latent-wm-data/E16-base100-trainseed-cache/cache_manifest.json')


def load(geometry,seed):
    name=f'20261005-E13-object-{geometry}-features'+(f'-s{seed}' if seed else '')
    p=ROOT/name;c=read(p/'config.json');assert read(p/'complete.json')['completed']
    assert sha(META)==c['cache_manifest_sha256']
    for key,value in c['array_sha256'].items():assert sha(p/f'{key}.npy')==value
    z=np.load(p/'features.npy');a=np.load(p/'actions.npy');meta=read(META)
    ep=np.full(len(z),-1,np.int64);end=np.zeros(len(z),np.int64)
    for v in meta['layout']:
        start=v['cache_row'];stop=start+v['frames'];assert (ep[start:stop]==-1).all()
        ep[start:stop]=v['episode'];end[start:stop]=stop
    assert (ep>=0).all() and z.shape==(9295,192) and a.shape==(9295,2)
    assert np.isfinite(z).all() and set(ep)==set(c['manifest']['base_episodes'])
    assert not set(ep)&{v['episode'] for v in read(ROOT/'20261004-E20-fresh-control-bank48/ledger.json')}
    valid=np.flatnonzero((ep[:-1]==ep[1:])&np.isfinite(a[:-1]).all(1))
    perm=np.random.default_rng(115200+seed).permutation(valid)
    nval=int(len(valid)*.1);train=perm[nval:];val=perm[:nval]
    return z,a,ep,end,train,val,c


def sample(z,a,ep,end,ix,rng,arm,device):
    maxh=np.minimum(50,end[ix]-1-ix);assert (maxh>=1).all()
    h=np.ones(len(ix),np.int64) if arm=='PAIRWISE' else rng.integers(1,maxh+1)
    gi=ix+h;assert np.array_equal(ep[gi],ep[ix]) and np.isfinite(a[ix]).all()
    steps=np.zeros_like(h) if arm=='GCBC-MATCHED' else h
    return tuple(torch.tensor(v,device=device) for v in [z[ix],z[gi],steps,a[ix]]),dict(indices=ix.tolist(),goal_indices=gi.tolist(),physical_horizon=h.tolist(),input_horizon=steps.tolist())


def model(seed,device):
    torch.manual_seed(115000+seed)
    return goal_policy_official_model.GoalConditionedIDM(goal_policy_official_model.IDMConfig()).to(device)


def preflight(geometry,seed,device):
    z,a,ep,end,train,val,c=load(geometry,seed)
    out=ROOT/f'20261005-E14-goalpolicy-{geometry}-{device}-preflight-s{seed}'
    assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');records=[]
    temp=out/'official_input.npz';np.savez(temp,embeddings=z,actions=a,episode_ids=ep)
    official=goal_policy_official_dataset.EmbeddingTripleDataset(str(temp),max_goal_horizon=50)
    assert np.array_equal(np.asarray(official.valid_indices),np.sort(np.concatenate([train,val])))
    # Directly exercise pinned __getitem__, not just our vectorized sampler.
    for pos in [0,len(official)//2,len(official)-1]:
        np.random.seed(115999+seed+pos);v=official[pos];i=official.valid_indices[pos];h=int(v['steps_remaining'])
        assert 1<=h<=min(50,end[i]-1-i) and np.array_equal(v['z_t'].numpy(),z[i])
        assert np.array_equal(v['z_goal'].numpy(),z[i+h]) and np.array_equal(v['action'].numpy(),a[i])
    for arm in ARMS:
        net=model(seed,device);initial=state_hash(net.state_dict());net.eval()
        batch,ids=sample(z,a,ep,end,train[:BATCH],np.random.default_rng(115100+seed),arm,device)
        x,g,h,target=batch
        with torch.no_grad():
            actual=net(x,g,h);h0=net(x,g,torch.zeros_like(h))
            hidden=net.backbone(torch.cat([x,g],-1));manual=net.head(hidden)
            assert torch.equal(actual,manual) and torch.equal(actual,h0)
        # Initially AdaLN is zero, then the official forward must expose horizon.
        with torch.no_grad():
            net.ada_shift.weight.fill_(.001)
            assert not torch.equal(net(x,g,torch.zeros_like(h)),net(x,g,torch.full_like(h,50)))
        net=model(seed,device);net.train();initial=state_hash(net.state_dict())
        state=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if device=='cuda' else None
        prediction=net(x,g,h);loss=F.mse_loss(prediction,target)
        torch.set_rng_state(state)
        if cuda is not None:torch.cuda.set_rng_state_all(cuda)
        hidden=net.backbone(torch.cat([x,g],-1));he=net.horizon_embed(net._sinusoidal_embed(h.float()/50))
        manual=net.head(hidden*(1+net.ada_scale(he))+net.ada_shift(he))
        assert torch.equal(prediction,manual) and torch.equal(loss,(manual-target).square().mean())
        opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001);assert not opt.state
        loss.backward();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in net.parameters())
        norm=torch.nn.utils.clip_grad_norm_(net.parameters(),1.);assert torch.isfinite(norm);opt.step()
        assert all(int(v['step'])==1 for v in opt.state.values()) and state_hash(net.state_dict())!=initial
        records.append(dict(arm=arm,initial_sha256=initial,parameters=sum(p.numel() for p in net.parameters()),manual_exact=True,official_dataset_samples_checked=3,optimizer_states=len(opt.state),first_batch=ids))
        print('goal policy preflight',geometry,seed,device,arm,'PASS',flush=True)
    assert len({v['initial_sha256'] for v in records})==1
    save(out/'controls.json',dict(passed=True,geometry=geometry,seed=seed,device=device,script_sha256=sha(__file__),vendor_model_sha256=sha(VENDOR/'idm/model.py'),vendor_dataset_sha256=sha(VENDOR/'idm/dataset.py'),feature_metadata=c,records=records))


def train(geometry,seed,arm):
    z,a,ep,end,starts,val,c=load(geometry,seed)
    for device in ['cpu','cuda']:
        control=read(ROOT/f'20261005-E14-goalpolicy-{geometry}-{device}-preflight-s{seed}/controls.json')
        assert control['passed'] and control['script_sha256']==sha(__file__) and control['vendor_model_sha256']==sha(VENDOR/'idm/model.py')
    name=f'20261005-E14-goalpolicy-{geometry}-{arm}-A100-s{seed}';out=Path('/tmp/latent-wm-runs')/name;cache=HF/name
    assert all(not p.exists() for p in [out,cache,ROOT/name]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'used.py')
    net=model(seed,'cuda');initial=state_hash(net.state_dict());assert initial==control['records'][0]['initial_sha256']
    torch.save(net.state_dict(),cache/'initial.pt');torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
    opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001)
    scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=EPOCHS,eta_min=.00001)
    rng=np.random.default_rng(115100+seed);shuffle=np.random.default_rng(115200+seed)
    updates=0;log=[];torch.cuda.reset_peak_memory_stats()
    save(out/'config.json',dict(geometry=geometry,train_seed=seed,arm=arm,official_config=dataclasses.asdict(net.cfg),epochs=50,batch_size=BATCH,drop_last=True,optimizer='AdamW',lr=.001,weight_decay=.0001,cosine_eta_min=.00001,initial_sha256=initial,feature_metadata=c,script_sha256=sha(__file__),vendor_model_sha256=sha(VENDOR/'idm/model.py'),vendor_commit='48c45b1cb2b34dd2c1c61d222c8309de567fde55',train_starts=starts.tolist(),validation_starts=val.tolist(),scope='fixed final epoch; original raw physical actions, no standardization; policy component reuse not full numerical paper replication; within-episode validation diagnostic only'))
    import time
    tick=time.perf_counter()
    for epoch in range(EPOCHS):
        order=shuffle.permutation(starts);losses=[];net.train()
        for begin in range(0,len(order)-BATCH+1,BATCH):
            ix=order[begin:begin+BATCH];batch,ids=sample(z,a,ep,end,ix,rng,arm,'cuda')
            if updates==0:save(out/'first_batch.json',ids)
            opt.zero_grad(set_to_none=True);loss=F.mse_loss(net(*batch[:3]),batch[3]);assert torch.isfinite(loss)
            loss.backward();norm=torch.nn.utils.clip_grad_norm_(net.parameters(),1.);assert torch.isfinite(norm);opt.step();updates+=1;losses.append(float(loss.detach()))
        assert losses;scheduler.step()
        net.eval();batch,_=sample(z,a,ep,end,val,np.random.default_rng(115300+seed+epoch),arm,'cuda')
        with torch.no_grad():v=float(F.mse_loss(net(*batch[:3]),batch[3]))
        log.append(dict(epoch=epoch+1,updates=updates,train_mse=float(np.mean(losses)),validation_mse=v,lr=scheduler.get_last_lr()[0]));save(out/'training.json',log)
        print('goal policy training',geometry,seed,arm,epoch+1,updates,flush=True)
    assert updates==(len(starts)//BATCH)*50 and all(int(v['step'])==updates for v in opt.state.values())
    assert all(torch.isfinite(v).all() for v in net.state_dict().values())
    checkpoint=cache/'epoch50.ckpt';torch.save(dict(state_dict=net.state_dict(),optimizer=opt.state_dict(),scheduler=scheduler.state_dict(),config=dataclasses.asdict(net.cfg),geometry=geometry,train_seed=seed,arm=arm,updates=updates,goal_rng=rng.bit_generator.state,shuffle_rng=shuffle.bit_generator.state,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),str(checkpoint)+'.part');os.replace(str(checkpoint)+'.part',checkpoint)
    save(out/'summary.json',dict(checkpoint_sha256=sha(checkpoint),epochs=50,updates=updates,training_examples=updates*BATCH,initial_sha256=initial,train_seconds=time.perf_counter()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30,optimizer_states=len(opt.state),geometry_source_sha256=c['source_sha256']))
    save(out/'complete.json',dict(completed=True,geometry=geometry,seed=seed,arm=arm,epochs=50));shutil.copytree(out,ROOT/name)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train']);p.add_argument('--geometry',choices=GEOMETRIES,required=True);p.add_argument('--seed',type=int,choices=[0,1,2],required=True);p.add_argument('--arm',choices=ARMS);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');v=p.parse_args();torch.set_num_threads(4)
    if v.mode=='preflight':preflight(v.geometry,v.seed,v.device)
    else:train(v.geometry,v.seed,v.arm)
