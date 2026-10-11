"""G2: actual past visual latents versus repeated current, matched policy capacity."""
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
import goal_policy_pusht_adapter as push
from fixed_data_train_seed import state_hash

ARMS=['TRUE-HISTORY','CURRENT-COPY']


def load(task):
    z,a,ep,end,_,_,meta=g.load('PRED',0) if task=='nav' else push.load('RELEASED',0)
    ix=np.arange(10,len(ep)-1)
    valid=ix[(ep[ix-10]==ep[ix])&(ep[ix]==ep[ix+1])&np.isfinite(a[ix]).all(1)]
    order=np.random.default_rng(115200).permutation(valid);nval=int(len(valid)*.1)
    return z,a,ep,end,order[nval:],order[:nval],meta


def model(device):
    torch.manual_seed(115000)
    return g.goal_policy_official_model.GoalConditionedIDM(g.goal_policy_official_model.IDMConfig(embed_dim=576)).to(device)


def sample(data,ix,rng,arm,device):
    z,a,ep,end,*_=data
    h=rng.integers(1,np.minimum(50,end[ix]-1-ix)+1);gi=ix+h
    assert (ep[ix-10]==ep[ix]).all() and (ep[gi]==ep[ix]).all()
    past=ix[:,None]+np.array([-10,-5,0]) if arm=='TRUE-HISTORY' else np.repeat(ix[:,None],3,1)
    current=z[past].reshape(len(ix),576);goal=np.tile(z[gi],(1,3))
    return tuple(torch.tensor(v,device=device) for v in [current,goal,np.zeros(len(ix),np.int64),a[ix]]),dict(indices=ix.tolist(),goal_indices=gi.tolist(),history_indices=past.tolist(),physical_horizon=h.tolist())


def preflight(task,device):
    data=load(task);z,a,ep,end,starts,val,meta=data
    out=g.ROOT/f'20261005-E14-history-{task}-{device}-preflight';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');records=[]
    try:
        samples={};initials=[]
        for arm in ARMS:
            net=model(device);net.train();initial=state_hash(net.state_dict());initials.append(initial)
            batch,ids=sample(data,starts[:1024],np.random.default_rng(115100),arm,device);samples[arm]=(batch,ids)
            x,goal,h,target=batch;assert x.shape==goal.shape==(1024,576) and h.eq(0).all()
            assert torch.equal(target,torch.tensor(a[starts[:1024]],device=device))
            if arm=='TRUE-HISTORY':assert np.array_equal(x.cpu().numpy().reshape(1024,3,192),z[starts[:1024,None]+[-10,-5,0]])
            else:assert torch.equal(x[:,:192],x[:,192:384]) and torch.equal(x[:,:192],x[:,384:])
            assert torch.equal(goal[:,:192],goal[:,192:384]) and torch.equal(goal[:,:192],goal[:,384:])
            cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if device=='cuda' else None
            predicted=net(x,goal,h);actual=F.mse_loss(predicted,target)
            torch.set_rng_state(cpu)
            if cuda is not None:torch.cuda.set_rng_state_all(cuda)
            manual=net.head(net.backbone(torch.cat([x,goal],-1)))
            assert torch.equal(predicted,manual) and torch.equal(actual,(manual-target).square().mean())
            opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001);assert not opt.state;actual.backward()
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in net.parameters())
            torch.nn.utils.clip_grad_norm_(net.parameters(),1.);opt.step();assert all(int(v['step'])==1 for v in opt.state.values())
            records.append(dict(arm=arm,initial_sha256=initial,parameters=sum(p.numel() for p in net.parameters()),optimizer_states=len(opt.state),manual_loss_exact=True,first_batch=ids))
            print('History policy actual preflight',task,device,arm,'PASS',flush=True)
        assert len(set(initials))==1
        first=samples[ARMS[0]];second=samples[ARMS[1]]
        assert first[1]['indices']==second[1]['indices'] and first[1]['goal_indices']==second[1]['goal_indices']
        assert all(torch.equal(first[0][i],second[0][i]) for i in [1,2,3])
        assert not torch.equal(first[0][0][:,:384],second[0][0][:,:384])
        g.save(out/'controls.json',dict(passed=True,task=task,device=device,records=records,feature_metadata=meta,script_sha256=g.sha(__file__),official_model_sha256=g.sha(g.VENDOR/'idm/model.py'),matched_goal_targets_capacity_initial=True))
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


def train(task,arm):
    data=load(task);z,a,ep,end,starts,val,meta=data
    for device in ['cpu','cuda']:
        pre=g.read(g.ROOT/f'20261005-E14-history-{task}-{device}-preflight/controls.json')
        assert pre['passed'] and pre['script_sha256']==g.sha(__file__)
    name=f'20261005-E14-history-{task}-{arm}-RTX-s0';out=Path('/tmp/latent-wm-runs')/name;cache=g.HF/name
    assert all(not p.exists() for p in [out,cache,g.ROOT/name]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        net=model('cuda');initial=state_hash(net.state_dict());assert initial==pre['records'][0]['initial_sha256']
        torch.save(net.state_dict(),cache/'initial.pt');torch.manual_seed(0);torch.cuda.manual_seed_all(0)
        opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001);scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=50,eta_min=.00001)
        rng=np.random.default_rng(115100);shuffle=np.random.default_rng(115200);updates=0;logs=[]
        g.save(out/'config.json',dict(task=task,arm=arm,train_seed=0,epochs=50,batch=1024,official_config=dataclasses.asdict(net.cfg),history_lags=[-10,-5,0],goal_mode='three copies of single goal',horizon_input=0,initial_sha256=initial,feature_metadata=meta,train_starts=starts.tolist(),validation_starts=val.tolist(),script_sha256=g.sha(__file__),official_model_sha256=g.sha(g.VENDOR/'idm/model.py'),hardware=torch.cuda.get_device_name(),scope='Matched input history versus capacity/control, one seed and frozen observation features. All methods omit first10 frames equally. No new method or whole-model held-out/pretraining claim.'))
        import time
        tick=time.perf_counter();torch.cuda.reset_peak_memory_stats()
        for epoch in range(50):
            order=shuffle.permutation(starts);net.train();losses=[]
            for begin in range(0,len(order)-1024+1,1024):
                batch,ids=sample(data,order[begin:begin+1024],rng,arm,'cuda')
                if updates==0:g.save(out/'first_batch.json',ids)
                opt.zero_grad(set_to_none=True);loss=F.mse_loss(net(*batch[:3]),batch[3]);assert torch.isfinite(loss);loss.backward()
                norm=torch.nn.utils.clip_grad_norm_(net.parameters(),1.);assert torch.isfinite(norm);opt.step();updates+=1;losses.append(float(loss.detach()))
            scheduler.step();net.eval();batch,_=sample(data,val,np.random.default_rng(115300+epoch),arm,'cuda')
            with torch.inference_mode():value=float(F.mse_loss(net(*batch[:3]),batch[3]))
            logs.append(dict(epoch=epoch+1,updates=updates,train_mse=float(np.mean(losses)),validation_mse=value,lr=scheduler.get_last_lr()[0]));g.save(out/'training.json',logs)
        assert updates==(len(starts)//1024)*50 and all(int(v['step'])==updates for v in opt.state.values())
        assert all(torch.isfinite(v).all() for v in net.state_dict().values())
        checkpoint=cache/'epoch50.ckpt';torch.save(dict(state_dict=net.state_dict(),optimizer=opt.state_dict(),scheduler=scheduler.state_dict(),config=dataclasses.asdict(net.cfg),task=task,arm=arm,updates=updates,goal_rng=rng.bit_generator.state,shuffle_rng=shuffle.bit_generator.state,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),str(checkpoint)+'.part');os.replace(str(checkpoint)+'.part',checkpoint)
        g.save(out/'summary.json',dict(checkpoint_sha256=g.sha(checkpoint),updates=updates,training_examples=updates*1024,initial_sha256=initial,optimizer_states=len(opt.state),train_seconds=time.perf_counter()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30))
        g.save(out/'complete.json',dict(completed=True,task=task,arm=arm,epochs=50));shutil.copytree(out,g.ROOT/name)
        print('History policy train endpoint',task,arm,updates,'DONE',flush=True)
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,g.ROOT/name);raise


def queue(task):
    out=g.ROOT/f'20261005-E14-history-{task}-pipeline';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    commands=[['preflight','--device',d] for d in ['cpu','cuda']]+[['train','--arm',a] for a in ARMS]
    g.save(out/'config.json',dict(task=task,commands=commands,script_sha256=g.sha(__file__)))
    try:
        for command in commands:subprocess.run([sys.executable,'-u',__file__,*command,'--task',task],check=True)
        g.save(out/'complete.json',dict(completed=True,task=task,training_runs=2))
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train','queue']);p.add_argument('--task',required=True,choices=['nav','pusht']);p.add_argument('--arm',choices=ARMS);p.add_argument('--device',default='cpu',choices=['cpu','cuda']);v=p.parse_args();torch.set_num_threads(4)
    if v.mode=='queue':queue(v.task)
    elif v.mode=='preflight':preflight(v.task,v.device)
    else:train(v.task,v.arm)
