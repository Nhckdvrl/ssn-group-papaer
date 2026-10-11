"""A10: five-step BPTT with frozen A8/A9 architecture, inputs and budgets."""
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
import predictive_object as original
import predictive_object_repeat as r
from fixed_data_train_seed import state_hash
from experience_transfer_control_audit import read


def setup(seed):
    r.SEED=seed
    r.g.SOURCES={key:Path(str(value).replace('-s0/',f'-s{seed}/')) for key,value in r.BASE_SOURCES.items()}


def data(geometry,seed):
    setup(seed)
    return original.load_data(geometry) if seed==0 else r.load_data(geometry)


def predictions(model,z,a):
    current=z[:,0];values=[]
    for step in range(5):
        current=model.prefix(current,a[:,step:step+1])[:,0]
        values.append(current)
    return values


def loss(model,z,a,device):
    with torch.autocast(device,dtype=torch.bfloat16):
        return (torch.stack(predictions(model,z,a),1)-z[:,1:]).square().mean()


def name(geometry,seed):return f'20261005-E13-rollout-{geometry}-s{seed}'


def preflight(geometry,seed,device):
    d,cfg=data(geometry,seed);out=r.m.ROOT/(name(geometry,seed)+f'-{device}-preflight')
    assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        model=r.Model(cfg['architecture'],geometry).to(device);model.training_mode();initial=state_hash(model.core.state_dict());frozen=model.frozen_hash()
        assert frozen==cfg['frozen_phi_sha256']
        priorname=f'20261005-E13-object-{geometry}-DIRECT-A100-s{seed}'
        assert initial==read(r.m.ROOT/priorname/'config.json')['head_initial_sha256']
        z,a,ids=r.sample(d,cfg,np.random.default_rng(113100+seed),device);clone=copy.deepcopy(model)
        cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state_all() if device=='cuda' else None
        actual=loss(model,z,a,device);torch.set_rng_state(cpu)
        if cuda is not None:torch.cuda.set_rng_state_all(cuda)
        with torch.autocast(device,dtype=torch.bfloat16):
            current=z[:,0];values=[]
            for step in range(5):
                ap=clone.core['action'](a[:,step:step+1],latent=current[:,None])
                pr=clone.core['predictor'](current[:,None],ap)
                current=clone.core['projection'](pr[:,0]);values.append(current)
            expected=(torch.stack(values,1)-z[:,1:]).square().mean()
        assert torch.equal(actual,expected) and torch.isfinite(actual)
        opt=torch.optim.AdamW(model.core.parameters(),lr=5e-5,weight_decay=.001);assert not opt.state
        actual.backward();assert all(v.grad is not None and torch.isfinite(v.grad).all() for v in model.core.parameters())
        assert all(v.grad is None for v in list(model.encoder.parameters())+list(model.projector.parameters()))
        torch.nn.utils.clip_grad_norm_(model.core.parameters(),1.);opt.step()
        assert all(int(v['step'])==1 for v in opt.state.values()) and frozen==model.frozen_hash()
        clone.eval();clone.zero_grad(set_to_none=True)
        with torch.autocast(device,dtype=torch.bfloat16):
            values=predictions(clone,z,a);values[0].retain_grad();last=(values[-1]-z[:,-1]).square().mean()
        last.backward();assert values[0].grad is not None and torch.isfinite(values[0].grad).all() and values[0].grad.abs().sum()>0
        with torch.inference_mode():
            before=torch.stack(predictions(clone,z[:4],a[:4]),1);changed=z[:4].clone();changed[:,1:]+=100
            assert torch.equal(before,torch.stack(predictions(clone,changed,a[:4]),1))
            terminal=clone.terminal(z[:1,0].expand(7,-1),a[:7],'LOCAL')
            singles=torch.cat([clone.terminal(z[:1,0],a[j:j+1],'LOCAL') for j in range(7)])
            assert torch.allclose(terminal,singles,atol=2e-4,rtol=1e-5)
            assert torch.equal(terminal,torch.stack(predictions(clone,z[:1].expand(7,-1,-1),a[:7]),1)[:,-1])
        r.m.dump(out/'controls.json',dict(passed=True,geometry=geometry,seed=seed,device=device,initial_sha256=initial,frozen_phi_sha256=frozen,first_ids=ids,manual_loss_exact=True,last_loss_gradient_to_first_prediction=True,target_not_model_input=True,batch_subset_error=float((terminal-singles).abs().max()),script_sha256=r.m.digest(__file__),repeat_component_sha256=r.m.digest(r.__file__),original_component_sha256=r.m.digest(original.__file__),vendor_sha256=r.m.digest(r.VENDOR/'module.py')))
        print('BPTT rollout actual preflight',geometry,seed,device,'PASS',flush=True)
    except Exception as error:
        r.m.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


def train(geometry,seed):
    d,cfg=data(geometry,seed)
    for device in ['cpu','cuda']:
        control=read(r.m.ROOT/(name(geometry,seed)+f'-{device}-preflight')/'controls.json')
        assert control['passed'] and control['script_sha256']==r.m.digest(__file__)
    runname=name(geometry,seed)+'-A100';out=Path('/tmp/latent-wm-runs')/runname;cache=r.m.HF/runname
    assert all(not p.exists() for p in [out,cache,r.m.ROOT/runname]);out.mkdir();cache.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        model=r.Model(cfg['architecture'],geometry).cuda();frozen=model.frozen_hash();initial=state_hash(model.core.state_dict())
        assert initial==control['initial_sha256'] and frozen==control['frozen_phi_sha256']
        torch.save(model.core.state_dict(),cache/'initial_head.pt');rng=np.random.default_rng(113100+seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
        opt=torch.optim.AdamW(model.core.parameters(),lr=5e-5,weight_decay=.001);tick=r.m.now();logs=[];torch.cuda.reset_peak_memory_stats()
        r.m.dump(out/'config.json',dict(geometry=geometry,train_seed=seed,arm='OPEN-ROLLOUT',updates=2825,batch=128,head_seed=113000+seed,sampler_seed=113100+seed,head_initial_sha256=initial,feature_metadata=cfg,script_sha256=r.m.digest(__file__),repeat_component_sha256=r.m.digest(r.__file__),original_component_sha256=r.m.digest(original.__file__),vendor_sha256=r.m.digest(r.VENDOR/'module.py'),hardware=torch.cuda.get_device_name(),scope='Known multi-step BPTT baseline; same five targets/starts/capacity/init/budget as A8/A9, predictions recurrent and never detached. Frozen prior geometry budgets differ. Recursive BN/dropout calls differ from flattened teacher training; no novelty or pure BN causality.'))
        for step in range(1,2826):
            model.training_mode();z,a,ids=r.sample(d,cfg,rng,'cuda')
            if step==1:r.m.dump(out/'first_ids.json',ids)
            opt.zero_grad(set_to_none=True);value=loss(model,z,a,'cuda');assert torch.isfinite(value);value.backward()
            norm=torch.nn.utils.clip_grad_norm_(model.core.parameters(),1.);assert torch.isfinite(norm);opt.step()
            if step==1 or step%25==0:
                logs.append(dict(update=step,loss=float(value.detach())));r.m.dump(out/'training.json',logs);print('BPTT rollout train',geometry,seed,step,flush=True)
        assert frozen==model.frozen_hash() and all(int(v['step'])==2825 for v in opt.state.values())
        checkpoint=cache/'u2825.ckpt'
        torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),steps=2825,geometry=geometry,arm='OPEN-ROLLOUT',config=cfg['architecture'],manifest=cfg['manifest'],train_seed=seed,sampler=rng.bit_generator.state,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),str(checkpoint)+'.part');os.replace(str(checkpoint)+'.part',checkpoint)
        r.m.dump(out/'summary.json',dict(checkpoint_sha256=r.m.digest(checkpoint),total_clips=361600,total_future_targets=1808000,optimizer_states=len(opt.state),frozen_phi_sha256=frozen,final_sampler=rng.bit_generator.state,train_seconds=r.m.now()-tick,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30))
        r.m.dump(out/'complete.json',dict(completed=True,geometry=geometry,seed=seed,updates=2825));shutil.copytree(out,r.m.ROOT/runname)
    except Exception as error:
        r.m.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,r.m.ROOT/runname);raise


def queue(geometry,seed):
    out=r.m.ROOT/(name(geometry,seed)+'-pipeline');assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    commands=[['preflight','--device',d] for d in ['cpu','cuda']]+[['train']]
    r.m.dump(out/'config.json',dict(geometry=geometry,seed=seed,commands=commands,script_sha256=r.m.digest(__file__)))
    try:
        for command in commands:subprocess.run([sys.executable,'-u',__file__,*command,'--geometry',geometry,'--seed',str(seed)],check=True)
        r.m.dump(out/'complete.json',dict(completed=True,geometry=geometry,seed=seed))
    except Exception as error:r.m.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','train','queue']);p.add_argument('--geometry',required=True,choices=['PRED','VALUE']);p.add_argument('--seed',required=True,type=int,choices=[0,1,2]);p.add_argument('--device',default='cpu',choices=['cpu','cuda']);args=p.parse_args();torch.set_num_threads(4)
    if args.mode=='queue':queue(args.geometry,args.seed)
    elif args.mode=='preflight':preflight(args.geometry,args.seed,args.device)
    else:train(args.geometry,args.seed)
