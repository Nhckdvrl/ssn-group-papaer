"""G3 same raw-action policy, independent data size by optimization budget."""
import argparse
import dataclasses
import os
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
import goal_policy_baseline as g
import goal_policy_pusht_adapter as a
from fixed_data_train_seed import state_hash


def load(episodes):
    source=a.CACHE if episodes==86 else g.ROOT/'20261005-E14-goalpolicy-pusht-860-features'
    meta=g.read(source/'config.json');done=g.read(source/'complete.json');assert done['completed'] and done['episodes']==episodes
    for key,value in meta['array_sha256'].items():assert g.sha(source/f'{key}.npy')==value
    z=np.load(source/'features.npy');act=np.load(source/'actions.npy');ep=np.load(source/'episode_ids.npy');end=np.zeros(len(ep),np.int64);covered=np.zeros(len(ep),bool)
    assert np.isfinite(z).all() and z.shape==(len(ep),192)
    for row in meta['layout']:
        start=row['cache_row'];stop=start+row['frames'];assert not covered[start:stop].any() and (ep[start:stop]==row['episode']).all()
        covered[start:stop]=True;end[start:stop]=stop
    assert covered.all() and len(set(ep))==episodes and not set(ep)&set(meta['excluded_fresh_eval_episodes'])
    valid=np.flatnonzero((ep[:-1]==ep[1:])&np.isfinite(act[:-1]).all(1));order=np.random.default_rng(115200).permutation(valid);nval=int(len(valid)*.1)
    return z,act,ep,end,order[nval:],order[:nval],meta


def sample(data,starts_rng,goal_rng,device):
    z,a,ep,end,starts,_,_=data;ix=starts_rng.choice(starts,1024,replace=True)
    horizon=goal_rng.integers(1,np.minimum(50,end[ix]-1-ix)+1);gi=ix+horizon
    assert np.array_equal(ep[ix],ep[gi]) and np.isfinite(a[ix]).all()
    return tuple(torch.tensor(v,device=device) for v in [z[ix],z[gi],np.zeros(1024,np.int64),a[ix]]),dict(indices=ix.tolist(),goal_indices=gi.tolist(),physical_horizon=horizon.tolist())


def preflight(device):
    out=g.ROOT/f'20261005-E14-coverage-{device}-preflight';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');records=[]
    try:
        small=load(86);large=load(860)
        assert np.array_equal(small[0],large[0][:len(small[0])]) and np.array_equal(small[1],large[1][:len(small[1])],equal_nan=True)
        assert small[-1]['source_sha256']==large[-1]['source_sha256'] and small[-1]['frozen_model_sha256']==large[-1]['frozen_model_sha256']
        for episodes,data in [(86,small),(860,large)]:
            net=g.model(0,device);net.train();initial=state_hash(net.state_dict())
            batch,ids=sample(data,np.random.default_rng(115200),np.random.default_rng(115100),device);x,goal,h,target=batch
            cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if device=='cuda' else None
            prediction=net(x,goal,h);loss=F.mse_loss(prediction,target);torch.set_rng_state(cpu)
            if cuda is not None:torch.cuda.set_rng_state_all(cuda)
            manual=net.head(net.backbone(torch.cat([x,goal],-1)))
            assert torch.equal(prediction,manual) and torch.equal(loss,(manual-target).square().mean())
            opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001);assert not opt.state;loss.backward()
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in net.parameters())
            torch.nn.utils.clip_grad_norm_(net.parameters(),1.);opt.step();assert all(int(v['step'])==1 for v in opt.state.values())
            records.append(dict(episodes=episodes,frames=len(data[0]),initial_sha256=initial,manual_loss_exact=True,first_batch=ids))
            print('Coverage policy actual preflight',episodes,device,'PASS',flush=True)
        assert records[0]['initial_sha256']==records[1]['initial_sha256']
        g.save(out/'controls.json',dict(passed=True,first86_subset_exact=True,records=records,script_sha256=g.sha(__file__),official_model_sha256=g.sha(g.VENDOR/'idm/model.py')))
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


def train(episodes,updates):
    data=load(episodes);z,a,ep,end,starts,val,meta=data
    for device in ['cpu','cuda']:
        pre=g.read(g.ROOT/f'20261005-E14-coverage-{device}-preflight/controls.json');assert pre['passed'] and pre['script_sha256']==g.sha(__file__)
    name=f'20261005-E14-coverage-e{episodes}-u{updates}-RTX-s0';out=Path('/tmp/latent-wm-runs')/name;cache=g.HF/name
    assert all(not p.exists() for p in [out,cache,g.ROOT/name]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        net=g.model(0,'cuda');initial=state_hash(net.state_dict());assert initial==pre['records'][0]['initial_sha256'];torch.save(net.state_dict(),cache/'initial.pt')
        torch.manual_seed(0);torch.cuda.manual_seed_all(0);opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001)
        scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=updates,eta_min=.00001);indices=np.random.default_rng(115200);goals=np.random.default_rng(115100)
        g.save(out/'config.json',dict(episodes=episodes,updates=updates,train_seed=0,batch=1024,official_config=dataclasses.asdict(net.cfg),horizon_input=0,initial_sha256=initial,feature_metadata=meta,train_starts=starts.tolist(),validation_starts=val.tolist(),script_sha256=g.sha(__file__),official_model_sha256=g.sha(g.VENDOR/'idm/model.py'),optimizer=dict(lr=.001,weight_decay=.0001,cosine_eta_min=.00001,cosine_T_max=updates),hardware=torch.cuda.get_device_name(),scope='Coverage by optimization budget; new86x400 anchor because with-replacement sampling/per-update cosine differ from G1. All final endpoints, one trainseed, frozen published phi pretrain unknown.'))
        import time
        tick=time.perf_counter();logs=[];torch.cuda.reset_peak_memory_stats()
        for step in range(1,updates+1):
            net.train();batch,ids=sample(data,indices,goals,'cuda')
            if step==1:g.save(out/'first_batch.json',ids)
            opt.zero_grad(set_to_none=True);loss=F.mse_loss(net(*batch[:3]),batch[3]);assert torch.isfinite(loss);loss.backward()
            grad=torch.nn.utils.clip_grad_norm_(net.parameters(),1.);assert torch.isfinite(grad);opt.step();scheduler.step()
            if step==1 or step%100==0:
                logs.append(dict(update=step,train_mse=float(loss.detach()),lr=scheduler.get_last_lr()[0]));g.save(out/'training.json',logs)
                print('Coverage policy train',episodes,updates,step,flush=True)
        assert all(int(v['step'])==updates for v in opt.state.values()) and all(torch.isfinite(v).all() for v in net.state_dict().values())
        path=cache/f'u{updates}.ckpt';torch.save(dict(state_dict=net.state_dict(),optimizer=opt.state_dict(),scheduler=scheduler.state_dict(),config=dataclasses.asdict(net.cfg),episodes=episodes,updates=updates,indices_rng=indices.bit_generator.state,goal_rng=goals.bit_generator.state,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),str(path)+'.part');os.replace(str(path)+'.part',path)
        g.save(out/'summary.json',dict(checkpoint_sha256=g.sha(path),initial_sha256=initial,updates=updates,training_examples=updates*1024,optimizer_states=len(opt.state),train_seconds=time.perf_counter()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30))
        g.save(out/'complete.json',dict(completed=True,episodes=episodes,updates=updates));shutil.copytree(out,g.ROOT/name)
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,g.ROOT/name);raise


def queue():
    out=g.ROOT/'20261005-E14-coverage-pipeline';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    commands=[['preflight','--device',d] for d in ['cpu','cuda']]+[['train','--episodes',str(e),'--updates',str(u)] for e in [86,860] for u in [400,4000]]
    try:
        for command in commands:subprocess.run([sys.executable,'-u',__file__,*command],check=True)
        g.save(out/'complete.json',dict(completed=True,training_runs=4))
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train','queue']);p.add_argument('--episodes',type=int,choices=[86,860]);p.add_argument('--updates',type=int,choices=[400,4000]);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');args=p.parse_args();torch.set_num_threads(4)
    if args.mode=='queue':queue()
    elif args.mode=='preflight':preflight(args.device)
    else:train(args.episodes,args.updates)
