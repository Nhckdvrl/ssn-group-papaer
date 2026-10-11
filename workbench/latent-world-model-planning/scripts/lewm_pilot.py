"""E16: small native-objective LeWM training, with causal history in MPC.

Pixels are cached, representations are never cached while the encoder trains.
This is a constant-LR pilot, not the upstream Lightning training reproduction.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import h5py
import hdf5plugin
import numpy as np
import torch
from build_lewm import architecture  # Ensures the LeWM, rather than Fast, module.
from module import SIGReg


def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()


def dump(p, x):
    def convert(v):
        if isinstance(v,(np.ndarray,torch.Tensor)): return v.tolist()
        if isinstance(v,np.generic): return v.item()
        if isinstance(v,Path): return str(v)
        raise TypeError(type(v).__name__)
    Path(p).write_text(json.dumps(x,default=convert,indent=2,allow_nan=False)+'\n')


def now():
    torch.cuda.synchronize()
    return time.perf_counter()


def pixels(x):
    x=torch.as_tensor(x,device='cuda').movedim(-1,-3).float()/255
    mean=x.new_tensor([.485,.456,.406]).view(3,1,1)
    std=x.new_tensor([.229,.224,.225]).view(3,1,1)
    return (x-mean)/std


def prepare(path, source, out, base_count, seed):
    if (out/'data_manifest.json').exists():
        return json.loads((out/'data_manifest.json').read_text())
    previous=np.load(source/'anchors.npz')['episodes']
    with h5py.File(path) as f:
        lengths, offsets=f['ep_len'][:],f['ep_offset'][:]
        eligible=np.setdiff1d(np.flatnonzero(lengths>36),previous)
        base=np.random.default_rng(20000+seed).choice(eligible,base_count,replace=False)
        evaluation=np.random.default_rng(31000+seed).choice(np.setdiff1d(eligible,base),48,replace=False)
        rng=np.random.default_rng(32000+seed)
        anchors=[]
        for ep in evaluation:
            t=int(rng.integers(10,int(lengths[ep])-25)); row=int(offsets[ep])+t
            anchors.append({'episode':int(ep),'start':t,'state':f['proprio'][row],
                'goal_state':f['proprio'][row+25], 'pixels':f['pixels'][row+np.array([-10,-5,0])],
                'goal_pixels':f['pixels'][row+25], 'past_actions':f['action'][row-10:row],
                'factual_actions':f['action'][row:row+25]})
        actions=np.concatenate([f['action'][int(offsets[ep]):int(offsets[ep]+lengths[ep])] for ep in base])
        finite=actions[np.isfinite(actions).all(1)]
        mean,std=finite.mean(0),np.maximum(finite.std(0),1e-6)
        manifest={'dataset_file':Path(path).name,'dataset_sha256':json.loads((source/'data_source.json').read_text())['sha256'],
            'base_episodes':base.tolist(),'evaluation_episodes':evaluation.tolist(),
            'excluded_previous_episodes':previous.tolist(),'seed':seed,'base_episode_count':base_count,
            'base_rows':int(sum(lengths[base])),'base_valid_clips':int(sum(lengths[base]-20)),
            'action_mean':mean.tolist(),'action_std':std.tolist(),
            'split_unit':'whole episode','selection_seeds':[20000+seed,31000+seed,32000+seed]}
    np.savez_compressed(out/'eval_anchors.npz',**{k:np.stack([a[k] for a in anchors]) for k in anchors[0]})
    dump(out/'data_manifest.json',manifest)
    return manifest


def load_training(path,manifest):
    started=time.perf_counter()
    images, actions, clips=[],[],[]; offset=0
    with h5py.File(path) as f:
        lengths, offsets=f['ep_len'][:],f['ep_offset'][:]
        for ep in sorted(manifest['base_episodes']):
            start, n=int(offsets[ep]),int(lengths[ep])
            images.append(f['pixels'][start:start+n]);actions.append(f['action'][start:start+n])
            clips.extend(range(offset,offset+n-20));offset+=n
    cache=np.concatenate(images)
    controls=np.concatenate(actions)
    print('loaded_base',cache.shape,'seconds',time.perf_counter()-started,flush=True)
    return cache, controls,np.asarray(clips),time.perf_counter()-started


class NativeCost:
    """Caches frozen features, while retaining the exact native recurrence."""
    def __init__(self,model,history,goal,past,capture=False):
        self.model,self.past,self.capture=model,past,capture
        self.initial=model.encode({'pixels':history})['emb']
        self.goal=model.encode({'pixels':goal})['emb']
        self.banks=[]

    def rollout(self,actions):
        b,s=actions.shape[:2]
        act=torch.cat([self.past[:,None].expand(b,s,2,10),actions],2).flatten(0,1)
        emb=self.initial[:,None].expand(b,s,3,192).flatten(0,1).clone()
        # Exactly five future macro states, after the two causal history blocks.
        for t in range(5):
            act_emb=self.model.action_encoder(act[:,:3+t])
            pred=self.model.predict(emb[:,-3:],act_emb[:,-3:])[:,-1:]
            emb=torch.cat([emb,pred],1)
        return emb[:,-1].reshape(b,s,192)

    def get_cost(self,info,actions):
        terminal=self.rollout(actions)
        cost=(terminal-self.goal[:,-1:, :]).square().sum(-1)
        if self.capture:
            self.banks.append({'actions':actions[0].cpu().numpy(),'cost':cost[0].cpu().numpy(),
                               'terminal':terminal[0].cpu().numpy()})
        return cost


def native_control(model,history,goal,past):
    a=torch.randn(1,37,5,10,device='cuda',generator=torch.Generator(device='cuda').manual_seed(17001))
    cached=NativeCost(model,history,goal,past)
    info={'pixels':history[:,None].expand(1,37,3,3,224,224),
          'goal':goal[:,None].expand(1,37,1,3,224,224),'action':torch.zeros(1,37,3,10,device='cuda')}
    actual=model.get_cost(info,torch.cat([past[:,None].expand(1,37,2,10),a],2))
    test=cached.get_cost({},a)
    diff=float((actual-test).abs().max())
    if not torch.allclose(actual,test,rtol=1e-5,atol=1e-5): raise ValueError(f'Native rollout mismatch {diff}')
    if info['predicted_emb'].shape[2]!=8: raise ValueError('Expected 3 history + 5 future states')
    return {'max_cost_abs_error':diff,'history_frames':3,'future_macro_states':5,'native_total_emb_frames':8}


@torch.inference_mode()
def evaluate(model,anchors,mean,std,out,prefix,count,seed):
    import gymnasium as gym
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    model.eval().requires_grad_(False)
    env=gym.make('swm/TwoRoom-v1',render_mode='rgb_array').unwrapped
    plan=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True)
    rows=[]
    for j in range(count):
        env.reset(seed=seed+j);env._set_state(anchors['state'][j]);env._set_goal_state(anchors['goal_state'][j])
        history=list(anchors['pixels'][j]);past=list(anchors['past_actions'][j])
        goal=pixels(anchors['goal_pixels'][j:j+1]).unsqueeze(0)
        success=False;times=[];steps=0
        for decision in range(2):
            start=now()
            h=pixels(np.asarray(history[-3:])).unsqueeze(0)
            p=torch.tensor((np.asarray(past[-10:])-mean)/std,device='cuda').float().reshape(1,2,10)
            if j==0 and decision==0: dump(out/f'{prefix}_native_control.json',native_control(model,h,goal,p))
            cost=NativeCost(model,h,goal,p)
            solver=swm.solver.CEMSolver(cost,batch_size=1,num_samples=300,topk=30,n_steps=30,device='cuda',seed=seed+j*100+decision)
            solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=plan)
            solved=solver.solve({'pixels':h,'goal':goal,'action':torch.zeros(1,3,10)})
            times.append(now()-start)
            controls=solved['actions'][0].numpy().reshape(25,2)*std+mean
            for t,a in enumerate(controls):
                _,_,done,truncated,_=env.step(a);past.append(a);steps+=1
                if (t+1)%5==0: history.append(env.render())
                if done or truncated: success=bool(done);break
            if done or truncated: break
        rows.append({'anchor':j,'source_episode':int(anchors['episode'][j]),'success':success,
                     'env_steps':steps,'planning_seconds':times})
        dump(out/f'{prefix}_evaluation.json',rows)
        print(prefix,'eval',j,'success',success,'steps',steps,flush=True)
    env.close()
    return rows


def train(args):
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.manual_seed(args.seed);np.random.seed(args.seed)
    manifest=prepare(args.dataset,Path(args.previous),out,args.base_episodes,args.seed)
    cfg=json.loads(Path(args.architecture_config).read_text())
    config=vars(args).copy();config.update({'architecture':cfg,'harness_sha256':digest(__file__),
        'builder_sha256':digest(Path(__file__).with_name('build_lewm.py')),'hardware':torch.cuda.get_device_name(),
        'optimizer':'AdamW','lr':5e-5,'weight_decay':1e-3,'precision':'bf16','gradient_clip':1.,
        'objective':'MSE all 3 shifted targets + .09 SIGReg; no target detach','scheduler':'constant LR pilot',
        'normalization':'base100 episodes only','clip_policy':'no padded or cross-episode clips'})
    dump(out/'config.json',config);(out/'lewm_pilot_used.py').write_text(Path(__file__).read_text())
    cache,controls,starts,io_seconds=load_training(args.dataset,manifest)
    mean,std=np.asarray(manifest['action_mean']),np.asarray(manifest['action_std'])
    model=architecture(cfg).cuda();sigreg=SIGReg(knots=17,num_proj=1024).cuda()
    anchors=np.load(out/'eval_anchors.npz')
    model.eval()
    with torch.inference_mode():
        h=pixels(anchors['pixels'][0:1]);g=pixels(anchors['goal_pixels'][0:1]).unsqueeze(0)
        past=torch.tensor((anchors['past_actions'][0:1]-mean)/std,device='cuda').float().reshape(1,2,10)
        dump(out/'initial_native_control.json',native_control(model,h,g,past))
    optimizer=torch.optim.AdamW(model.parameters(),lr=5e-5,weight_decay=1e-3)
    rows=[];rng=np.random.default_rng(args.seed+33000);step=0
    start_epoch=0
    if args.resume:
        previous=torch.load(args.resume,map_location='cpu',weights_only=False)
        if previous['manifest']['base_episodes']!=manifest['base_episodes']:
            raise ValueError('Resume must retain the same whole-episode base split')
        model.load_state_dict(previous['state_dict'],strict=True);optimizer.load_state_dict(previous['optimizer'])
        start_epoch,step=previous['epoch'],previous['steps']
        if 'torch_rng' in previous:
            torch.set_rng_state(previous['torch_rng']);torch.cuda.set_rng_state(previous['cuda_rng'])
            rng.bit_generator.state=previous['numpy_rng']
        else:
            # Older pilot checkpoint predates RNG persistence: disclose the reset.
            dump(out/'resume_note.json',{'source_sha256':digest(args.resume),
                'limitation':'torch/dropout RNG restarted; not identical to uninterrupted training'})
            for _ in range(start_epoch): rng.permutation(starts)
    torch.cuda.reset_peak_memory_stats();begin=now()
    for epoch in range(start_epoch,args.epochs):
        model.train().requires_grad_(True)
        order=rng.permutation(starts)
        for offset in range(0,len(order)-args.batch_size+1,args.batch_size):
            t0=now();ix=order[offset:offset+args.batch_size]
            batch_pixels=pixels(cache[ix[:,None]+np.array([0,5,10,15])])
            ac=(controls[ix[:,None]+np.arange(20)]-mean)/std
            ac=torch.tensor(ac,device='cuda').float().reshape(args.batch_size,4,10)
            prep=now()-t0;t1=now();optimizer.zero_grad(set_to_none=True)
            with torch.autocast('cuda',dtype=torch.bfloat16):
                info=model.encode({'pixels':batch_pixels,'action':ac})
                emb=info['emb'];pred=model.predict(emb[:,:3],info['act_emb'][:,:3])
                mse=(pred-emb[:,1:]).square().mean();reg=sigreg(emb.transpose(0,1));loss=mse+.09*reg
            if not torch.isfinite(loss): raise ValueError(f'Nonfinite loss at step {step}')
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step()
            compute=now()-t1;step+=1
            if step%25==0 or step==1:
                row={'epoch':epoch,'step':step,'loss':float(loss),'pred_mse':float(mse),'sigreg':float(reg),
                     'embedding_std_mean':float(emb.float().std(dim=(0,1)).mean()),'compute_seconds':compute,'prepare_seconds':prep}
                rows.append(row);dump(out/'training.json',rows);print('train',row,flush=True)
        checkpoint=Path(args.checkpoint);checkpoint.parent.mkdir(parents=True,exist_ok=True)
        torch.save({'state_dict':model.state_dict(),'optimizer':optimizer.state_dict(),'epoch':epoch+1,
                    'config':cfg,'manifest':manifest,'steps':step,
                    'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state(),
                    'numpy_rng':rng.bit_generator.state},str(checkpoint)+'.part')
        os.replace(str(checkpoint)+'.part',checkpoint)
        print('epoch',epoch+1,'steps',step,'seconds',now()-begin,flush=True)
    dump(out/'train_summary.json',{'steps':step,'epochs':args.epochs,'training_seconds':now()-begin,
        'initial_hdf5_read_seconds':io_seconds,'cached_pixel_bytes':cache.nbytes,'peak_vram_gib':torch.cuda.max_memory_allocated()/2**30,
        'checkpoint':str(checkpoint),'checkpoint_sha256':digest(checkpoint)})
    evaluate(model,anchors,mean,std,out,'base',args.eval_anchors,args.seed)
    # Released positive control uses its original full-dataset action statistics.
    released=torch.load(args.released_checkpoint,map_location='cpu',weights_only=False).cuda()
    with h5py.File(args.dataset) as f:
        a=f['action'][:];a=a[np.isfinite(a).all(1)];rm,rs=a.mean(0),a.std(0)
    evaluate(released,anchors,rm,rs,out,'released',args.eval_anchors,args.seed)
    dump(out/'complete.json',{'completed':True,'phase':'base training and native positive control only'})


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['dataset','previous','architecture-config','released-checkpoint','checkpoint','output']: p.add_argument('--'+name,required=True)
    p.add_argument('--base-episodes',type=int,default=100);p.add_argument('--epochs',type=int,default=10)
    p.add_argument('--batch-size',type=int,default=128);p.add_argument('--eval-anchors',type=int,default=16)
    p.add_argument('--resume')
    p.add_argument('--seed',type=int,default=0);args=p.parse_args()
    try: train(args)
    except Exception as e:
        out=Path(args.output)
        if out.exists(): dump(out/'failure.json',{'error':type(e).__name__,'message':str(e)})
        raise
