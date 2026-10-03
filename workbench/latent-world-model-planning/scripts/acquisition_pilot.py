"""E16 equal-data pilot. Public selection is sealed before any branch executes."""
import argparse
import copy
from collections import Counter
import json
import os
from pathlib import Path
import time
import h5py
import hdf5plugin
import numpy as np
import torch
from lewm_pilot import architecture, digest, dump, pixels, now, load_training, NativeCost, evaluate
from module import SIGReg
from branch_selector import pbb

POLICIES=['NO-ADD','IID','UNIFORM-COMMON-RESET','COVERAGE','GLOBAL-U','TASK-U','PBB']


def optimizer_steps(state_dict):
    """Detach scalar values so the common AdamW step snapshot is immutable."""
    return tuple((key,int(value['step'])) for key,value in sorted(state_dict['state'].items()) if 'step' in value)


def load_base(checkpoint):
    state=torch.load(checkpoint,map_location='cpu',weights_only=False)
    if state['epoch']!=30: raise ValueError('This pilot requires the locked 30-epoch base')
    model=architecture(state['config']).cuda();model.load_state_dict(state['state_dict'],strict=True)
    model.eval().requires_grad_(False)
    return model,state


@torch.inference_mode()
def encode_cache(model,cache):
    features=[]
    for i in range(0,len(cache),128):
        emb=model.encode({'pixels':pixels(cache[i:i+128]).unsqueeze(1)})['emb'][:,0]
        features.append(emb.cpu())
    return torch.cat(features).cuda()


def bootstrap_heads(base,features,controls,starts,state,steps,seed,out):
    manifest=state['manifest'];mean,std=np.asarray(manifest['action_mean']),np.asarray(manifest['action_std'])
    # The ordering of the cached episodes matches load_training's sorted order.
    with h5py.File(out['dataset']) as f: lengths=f['ep_len'][:]
    episodes=sorted(manifest['base_episodes']); boundaries=np.cumsum([0]+[int(lengths[e]) for e in episodes])
    clip_episode=np.searchsorted(boundaries,starts,side='right')-1
    heads=[]
    for head_id in range(3):
        torch.manual_seed(seed+head_id+41000);rng=np.random.default_rng(seed+head_id+42000)
        counts=np.bincount(rng.integers(0,len(episodes),len(episodes)),minlength=len(episodes))
        weights=counts[clip_episode].astype(float);weights/=weights.sum()
        model=copy.deepcopy(base)
        model.encoder=base.encoder;model.projector=base.projector
        for part in [model.predictor,model.action_encoder,model.pred_proj]:part.train().requires_grad_(True)
        opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=5e-5,weight_decay=1e-3)
        log=[];begin=now()
        for step in range(steps):
            ix=rng.choice(starts,256,replace=True,p=weights)
            target=features[torch.tensor(ix[:,None]+np.array([0,5,10,15]),device='cuda')]
            actions=torch.tensor((controls[ix[:,None]+np.arange(15)]-mean)/std,device='cuda').float().reshape(256,3,10)
            opt.zero_grad(set_to_none=True)
            with torch.autocast('cuda',dtype=torch.bfloat16):
                pred=model.predict(target[:,:3],model.action_encoder(actions))
                loss=(pred-target[:,1:]).square().mean()
            if not torch.isfinite(loss):raise ValueError('Nonfinite auxiliary head loss')
            loss.backward();torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.);opt.step()
            if step%100==0:log.append({'step':step,'mse':float(loss)})
        model.eval().requires_grad_(False);heads.append(model)
        path=Path(out['output'])/f'head_{head_id}_summary.json'
        ckpt=Path(out['head_cache'])/f'head_{head_id}.pt';ckpt.parent.mkdir(parents=True,exist_ok=True)
        torch.save({k:v for k,v in model.state_dict().items() if not k.startswith(('encoder.','projector.'))},ckpt)
        dump(path,{'head':head_id,'bootstrap_episode_counts':counts,'steps':steps,'seconds':now()-begin,
                   'losses':log,'checkpoint':str(ckpt),'sha256':digest(ckpt),'shared_encoder':True})
        print('bootstrap_head',head_id,'seconds',now()-begin,'loss',float(loss),flush=True)
    return heads


def choose_diverse(actions,count):
    x=actions.reshape(len(actions),-1);ids=[int(np.argmax(np.linalg.norm(x-x.mean(0),axis=1)))]
    distance=np.linalg.norm(x-x[ids[0]],axis=1)
    for _ in range(count-1):
        score=distance.copy();score[ids]=-np.inf;j=int(score.argmax());ids.append(j)
        distance=np.minimum(distance,np.linalg.norm(x-x[j],axis=1))
    return ids


def bank(args):
    import gymnasium as gym
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);torch.manual_seed(args.seed)
    while not (Path(args.base_run)/'train_summary.json').exists():
        if (Path(args.base_run)/'failure.json').exists():raise RuntimeError('Base training failed')
        time.sleep(5)
    base,state=load_base(args.checkpoint);manifest=state['manifest']
    config=vars(args).copy();config.update({'base_sha256':digest(args.checkpoint),'harness_sha256':digest(__file__),
        'hardware':torch.cuda.get_device_name(),'logical_steps_per_policy':2000,'actual_branch_steps':'reported separately',
        'head_steps':500,'public_bank_iteration':15,'policies':POLICIES})
    dump(out/'config.json',config);(out/'acquisition_pilot_used.py').write_text(Path(__file__).read_text())
    cache,controls,starts,io=load_training(args.dataset,manifest)
    features=encode_cache(base,cache).clone()
    torch.save({'features':features.cpu(),'base_sha256':config['base_sha256']},Path(args.head_cache)/'features.pt')
    heads=bootstrap_heads(base,features,controls,starts,state,500,args.seed,vars(args))
    rng=np.random.default_rng(args.seed+43000)
    with h5py.File(args.dataset) as f:
        lengths,offsets=f['ep_len'][:],f['ep_offset'][:]
        episodes=rng.choice(manifest['base_episodes'],64,replace=False)
        anchors=[]
        for ep in episodes:
            t=int(rng.integers(10,int(lengths[ep])-25));row=int(offsets[ep])+t
            anchors.append({'episode':int(ep),'start':t,'state':f['proprio'][row],
                'goal_state':f['proprio'][row+25],'pixels':f['pixels'][row+np.array([-10,-5,0])],
                'goal_pixels':f['pixels'][row+25],'past_actions':f['action'][row-10:row]})
    np.savez_compressed(out/'acquisition_anchors.npz',**{k:np.stack([a[k] for a in anchors]) for k in anchors[0]})
    mean,std=np.asarray(manifest['action_mean']),np.asarray(manifest['action_std'])
    env=gym.make('swm/TwoRoom-v1',render_mode='rgb_array').unwrapped
    plan=swm.PlanConfig(horizon=5,receding_horizon=5,action_block=5,warm_start=True)
    public=[]
    with torch.inference_mode():
        for j,anchor in enumerate(anchors):
            h=pixels(anchor['pixels']).unsqueeze(0);g=pixels(anchor['goal_pixels'][None]).unsqueeze(0)
            past=torch.tensor((anchor['past_actions']-mean)/std,device='cuda').float().reshape(1,2,10)
            cost=NativeCost(base,h,g,past,capture=True)
            solver=swm.solver.CEMSolver(cost,batch_size=1,num_samples=300,topk=30,n_steps=30,device='cuda',seed=args.seed+j+44000)
            solver.configure(action_space=batch_space(env.action_space,1),n_envs=1,config=plan)
            solver.solve({'pixels':h,'goal':g,'action':torch.zeros(1,3,10)})
            trace=cost.banks[15];actions=trace['actions'];terminal=[trace['terminal']];scores=[trace['cost']]
            for head in heads:
                evaluator=NativeCost(head,h,g,past)
                a=torch.tensor(actions[None],device='cuda');t=evaluator.rollout(a)
                terminal.append(t[0].cpu().numpy());scores.append(evaluator.get_cost({},a)[0].cpu().numpy())
            terminal,scores=np.asarray(terminal),np.asarray(scores)
            selected=pbb(scores,actions,terminal[0],k=30,branches=8,seed=args.seed+j+45000)
            global_u=terminal.var(0).mean(-1);task_u=scores.var(0)
            distance=torch.cdist(cost.initial[:,-1],features).topk(50,largest=False).values.mean()
            row={'actions':actions,'terminals':terminal,'costs':scores,'global_candidate_u':global_u,
                 'task_candidate_u':task_u,'global_score':float(global_u.mean()),'task_score':float(task_u.mean()),
                 'coverage_score':float(distance),'pbb_score':selected['score'],'pbb_ids':selected['ids']}
            public.append(row)
            np.savez_compressed(out/f'public_{j:03d}.npz',**row)
            print('public_pool',j,'pbb_score',selected['score'],flush=True)
    # All selectors run before the hidden file exists. Only union keys will execute.
    ledger={};n=len(anchors)
    for policy in POLICIES[2:]:
        selector_rng=np.random.default_rng(args.seed+46000)
        if policy=='UNIFORM-COMMON-RESET': chosen=selector_rng.choice(n,10,replace=False)
        else:
            field={'COVERAGE':'coverage_score','GLOBAL-U':'global_score','TASK-U':'task_score','PBB':'pbb_score'}[policy]
            values=np.array([r[field] for r in public])
            chosen=np.argsort(-values,kind='stable')[:10] if values.max()>0 else selector_rng.choice(n,10,replace=False)
        queries=[]
        for j in chosen:
            row=public[int(j)]
            if policy=='UNIFORM-COMMON-RESET':ids=selector_rng.choice(300,8,replace=False)
            elif policy=='COVERAGE':ids=choose_diverse(row['actions'],8)
            elif policy=='GLOBAL-U':ids=np.argsort(-row['global_candidate_u'],kind='stable')[:8]
            elif policy=='TASK-U':ids=np.argsort(-row['task_candidate_u'],kind='stable')[:8]
            else:ids=row['pbb_ids']
            queries.extend([[int(j),int(i)] for i in ids])
        ledger[policy]=queries
    ledger['NO-ADD']=[]
    forbidden=set(manifest['base_episodes']+manifest['evaluation_episodes']+manifest.get('excluded_previous_episodes',[]))
    with h5py.File(args.dataset) as f:
        eligible=np.setdiff1d(np.flatnonzero(f['ep_len'][:]>26),list(forbidden))
        ledger['IID']=np.random.default_rng(args.seed+47000).choice(eligible,80,replace=False).tolist()
    dump(out/'selection_ledger.json',ledger)
    seal=digest(out/'selection_ledger.json');dump(out/'selection_seal.json',{'sha256':seal,'hidden_file_existed':False})
    print('selection_sealed',seal,flush=True)
    union=sorted({tuple(q) for policy,qs in ledger.items() if policy not in ['NO-ADD','IID'] for q in qs})
    order=np.random.default_rng(args.seed+48000).permutation(len(union));replays=0;max_replay=0.;max_pixels=0.
    with h5py.File(out/'hidden_branches.h5','x') as hidden:
        for z in order:
            j,i=union[int(z)];a=anchors[j];acts=public[j]['actions'][i].reshape(25,2)*std+mean
            def replay():
                env.reset(seed=args.seed+j+49000);env._set_state(a['state']);env._set_goal_state(a['goal_state'])
                states=[env._get_obs()];images=[env.render()]
                for control in acts:
                    env.step(control);states.append(env._get_obs());images.append(env.render())
                return np.asarray(states),np.asarray(images)
            states,images=replay()
            group=hidden.create_group(f'a{j:03d}_c{i:03d}')
            group.create_dataset('pixels',data=images,compression='gzip',compression_opts=1)
            group.create_dataset('actions',data=acts);group.create_dataset('states',data=states)
            if z<8:
                for _ in range(3):
                    s,im=replay();replays+=1;max_replay=max(max_replay,float(np.abs(s-states).max()))
                    max_pixels=max(max_pixels,float(np.abs(im.astype(float)-images).max()))
        with h5py.File(args.dataset) as f:
            lengths,offsets=f['ep_len'][:],f['ep_offset'][:];rng=np.random.default_rng(args.seed+50000)
            for ep in ledger['IID']:
                t=int(rng.integers(0,int(lengths[ep])-25));row=int(offsets[ep])+t
                group=hidden.create_group(f'iid_{ep}')
                group.create_dataset('pixels',data=f['pixels'][row:row+26],compression='gzip',compression_opts=1)
                group.create_dataset('actions',data=f['action'][row:row+25])
    env.close()
    if digest(out/'selection_ledger.json')!=seal:raise ValueError('Selection ledger changed after observing outcomes')
    if max_replay!=0 or max_pixels!=0:raise ValueError('TwoRoom common reset is not exact')
    dump(out/'bank_summary.json',{'union_branches':len(union),'actual_branch_env_steps':25*len(union),
        'reset_replays':replays,'control_env_steps':25*replays,'actual_resets':len(union)+replays,
        'replay_state_max_abs':max_replay,'replay_pixel_max_abs':max_pixels,'logical_steps_per_policy':2000,
        'iid_source':'precollected official dataset, logical consumption only','ledger_sha256':seal,
        'hidden_sha256':digest(out/'hidden_branches.h5'),'initial_base_read_seconds':io})
    dump(out/'complete.json',{'completed':True,'phase':'bank; no acquisition-effect claim'})


def train_one(args,policy,base_state,base_cache,base_controls,base_starts,source_steps):
    out=Path(args.output)/policy;out.mkdir(parents=True,exist_ok=False)
    source=Path(args.bank);ledger=json.loads((source/'selection_ledger.json').read_text())
    torch.manual_seed(args.seed+51000);rng=np.random.default_rng(args.seed+52000)
    manifest=base_state['manifest'];mean,std=np.asarray(manifest['action_mean']),np.asarray(manifest['action_std'])
    cache,controls,starts=base_cache,base_controls,base_starts
    if policy!='NO-ADD':
        chunks=[];acts=[];new_starts=[];offset=len(cache)
        with h5py.File(source/'hidden_branches.h5') as f:
            keys=[f'iid_{ep}' for ep in ledger[policy]] if policy=='IID' else [f'a{j:03d}_c{i:03d}' for j,i in ledger[policy]]
            for key in keys:
                im=f[key]['pixels'][:];a=f[key]['actions'][:]
                if len(im)!=26 or len(a)!=25:raise ValueError('Unequal purchased branch length')
                chunks.append(np.concatenate([im,np.repeat(im[-1:],4,axis=0)]))
                acts.append(np.concatenate([a,np.zeros((5,2),dtype=a.dtype)]))
                new_starts.extend(range(offset,offset+11));offset+=30
        cache=np.concatenate([cache,*chunks]);controls=np.concatenate([controls,*acts]);starts=np.concatenate([starts,new_starts])
    config=vars(args).copy();config.update({'policy':policy,'base_sha256':digest(args.checkpoint),
        'logical_added_steps':0 if policy=='NO-ADD' else 2000,'gradient_steps':600,'harness_sha256':digest(__file__),
        'selection_ledger_sha256':digest(source/'selection_ledger.json'),'train_seed':args.seed,
        'normalization':'same base100 statistics','objective':'native all3 MSE + .09 SIGReg',
        'hardware':torch.cuda.get_device_name(),'torch':torch.__version__,'precision':'bf16',
        'helper_sha256':digest(Path(__file__).with_name('lewm_pilot.py')),
        'architecture_builder_sha256':digest(Path(__file__).with_name('build_lewm.py'))})
    dump(out/'config.json',config)
    (out/'acquisition_pilot_used.py').write_text(Path(__file__).read_text())
    model=architecture(base_state['config']).cuda();model.load_state_dict(base_state['state_dict'],strict=True)
    optimizer=torch.optim.AdamW(model.parameters(),lr=5e-5,weight_decay=1e-3)
    # Noncapturable AdamW keeps CPU step tensors; clone before each method.
    optimizer.load_state_dict(copy.deepcopy(base_state['optimizer']))
    begin_steps=optimizer_steps(optimizer.state_dict())
    if begin_steps!=source_steps or optimizer_steps(base_state['optimizer'])!=source_steps:
        raise ValueError('Method optimizer must begin at the immutable source steps')
    config['optimizer_step_counts']={'source':dict(Counter(v for _,v in source_steps)),
        'begin':dict(Counter(v for _,v in begin_steps)),'parameter_states':len(source_steps)}
    dump(out/'config.json',config)
    model.train().requires_grad_(True);sigreg=SIGReg(knots=17,num_proj=1024).cuda();log=[];begin=now()
    actual_steps=0
    for step in range(600):
        ix=rng.choice(starts,128,replace=True);batch=pixels(cache[ix[:,None]+np.array([0,5,10,15])])
        a=torch.tensor((controls[ix[:,None]+np.arange(20)]-mean)/std,device='cuda').float().reshape(128,4,10)
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast('cuda',dtype=torch.bfloat16):
            info=model.encode({'pixels':batch,'action':a});emb=info['emb']
            pred=model.predict(emb[:,:3],info['act_emb'][:,:3]);mse=(pred-emb[:,1:]).square().mean()
            reg=sigreg(emb.transpose(0,1));loss=mse+.09*reg
        if not torch.isfinite(loss):raise ValueError('Nonfinite main loss')
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);optimizer.step()
        actual_steps+=1
        if step%100==0:
            log.append({'step':step,'mse':float(mse),'sigreg':float(reg),'loss':float(loss)})
            dump(out/'training.json',log);print(policy,'train',step,float(loss),flush=True)
    end_steps=optimizer_steps(optimizer.state_dict())
    if optimizer_steps(base_state['optimizer'])!=source_steps:
        raise ValueError('Method training mutated the common optimizer source steps')
    if end_steps!=tuple((key,value+actual_steps) for key,value in begin_steps):
        raise ValueError('Method optimizer end steps do not equal begin plus actual updates')
    config['optimizer_step_counts'].update({'end':dict(Counter(v for _,v in end_steps)),
        'actual_updates':actual_steps,'source_unchanged':True})
    dump(out/'config.json',config)
    checkpoint=Path(args.model_cache)/f'E16_{policy}_seed{args.seed}.pt';checkpoint.parent.mkdir(parents=True,exist_ok=True)
    torch.save({'state_dict':model.state_dict(),'config':base_state['config'],'manifest':manifest,'policy':policy},checkpoint)
    dump(out/'train_summary.json',{'seconds':now()-begin,'steps':600,'checkpoint':str(checkpoint),'sha256':digest(checkpoint),
        'optimizer_step_counts':config['optimizer_step_counts']})
    anchors=np.load(Path(args.base_run)/'eval_anchors.npz')
    evaluate(model,anchors,mean,std,out,'evaluation',48,args.seed)
    dump(out/'complete.json',{'completed':True,'science_scope':'one exploratory train seed; no seed filtering'})


def train(args):
    torch.set_num_threads(4);state=torch.load(args.checkpoint,map_location='cpu',weights_only=False)
    source_steps=optimizer_steps(state['optimizer'])
    if state['epoch']!=30:raise ValueError('Expected 30-epoch common base')
    source=Path(args.bank)
    if not (source/'complete.json').exists():raise ValueError('Branch bank is not complete')
    if json.loads((source/'config.json').read_text())['base_sha256']!=digest(args.checkpoint):
        raise ValueError('Acquisition and training must start from the identical base model')
    if json.loads((source/'selection_seal.json').read_text())['sha256']!=digest(source/'selection_ledger.json'):
        raise ValueError('Selection ledger changed after the pre-outcome seal')
    if args.base_cache:
        p=Path(args.base_cache);metadata=json.loads(p.with_name('manifest.json').read_text())
        if metadata['data_manifest']!=state['manifest']:raise ValueError('Base cache manifest mismatch')
        if digest(p)!=metadata['sha256']:raise ValueError('Base cache checksum mismatch')
        cache=np.load(p);base_cache,base_controls,base_starts=cache['pixels'],cache['actions'],cache['starts']
        print('loaded_exact_base_cache',base_cache.shape,flush=True)
    else:base_cache,base_controls,base_starts,_=load_training(args.dataset,state['manifest'])
    for policy in args.methods.split(','):
        if policy not in POLICIES:raise ValueError(policy)
        train_one(args,policy,state,base_cache,base_controls,base_starts,source_steps)
        torch.cuda.empty_cache()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['bank','train'],required=True)
    for name in ['dataset','checkpoint','output']:p.add_argument('--'+name,required=True)
    p.add_argument('--head-cache');p.add_argument('--model-cache');p.add_argument('--bank');p.add_argument('--base-run')
    p.add_argument('--base-cache')
    p.add_argument('--methods',default=','.join(POLICIES));p.add_argument('--seed',type=int,default=0)
    args=p.parse_args()
    try:
        if args.phase=='bank':
            Path(args.head_cache).mkdir(parents=True,exist_ok=True);bank(args)
        else:train(args)
    except Exception as e:
        out=Path(args.output)
        if out.exists():dump(out/'failure.json',{'error':type(e).__name__,'message':str(e)})
        raise
