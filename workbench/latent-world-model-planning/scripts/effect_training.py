"""E20 joint encoder/predictor comparison; shared legal branches, no outcome selection."""
import argparse, copy, json, os, shutil
from pathlib import Path
import numpy as np
import torch
from fixed_data_train_seed import objective as original_objective, normalized_pixels, state_hash
from lewm_pilot import architecture, digest, dump, now
from module import SIGReg

METHODS = ['PLAIN','GLOBAL-SG','CENTER','DET-INVERSE','PROB-INVERSE']

def load_bank(path):
    path=Path(path); complete=json.loads((path/'complete.json').read_text())
    assert complete['completed'] and complete['anchors']==88 and complete['branches']==1056
    cfg=json.loads((path/'config.json').read_text()); ledger=json.loads((path/'ledger.json').read_text())
    rows=json.loads((path/'rows.json').read_text()); frames=[]; actions=[]; physical=[]
    entries=sorted([e for e in ledger if e['task']=='tworoom'],key=lambda e:e['anchor'])
    assert [e['anchor'] for e in entries]==list(range(44))
    for e in entries:
        images=[]; controls=[]; states=[]
        for b in range(12):
            p=path/f'tworoom_{e["anchor"]:03d}_b{b:02d}.npz'
            row=next(r for r in rows if r['task']=='tworoom' and r['anchor']==e['anchor'] and r['branch']==b)
            assert digest(p)==row['trace_sha256']; d=np.load(p)
            images.append(np.concatenate([d['history'],d['pixels'][[5,10,15,20,25]]]))
            a=np.concatenate([np.asarray(e['warm_actions']),d['issued_actions']]);assert a.shape==(35,2) and (np.abs(a)<=1).all()
            controls.append(a);states.append(d['diagnostic_states'][-1])
        frames.append(images);actions.append(controls);physical.append(states)
    return np.asarray(frames),np.asarray(actions),np.asarray(physical),cfg

def prediction(model,x,a):
    info=model.encode({'pixels':x,'action':a});z=info['emb'];act=info['act_emb']
    pred=torch.stack([model.predict(z[:,h:h+3],act[:,h:h+3])[:,-1] for h in range(5)],1)
    return pred,z,act

def losses(model,head,sigreg,x,a,raw,method,groups,k):
    pred,z,act=prediction(model,x,a);target=z[:,3:];base=(pred-target).square().mean()
    reg=sigreg(z.transpose(0,1));aux=base.new_zeros(())
    if method=='GLOBAL-SG':aux=(pred-target.detach()).square().mean()
    elif method=='CENTER':
        p=pred.reshape(groups,k,5,-1);y=target.reshape(groups,k,5,-1).detach()
        aux=((p-p.mean(1,keepdim=True))-(y-y.mean(1,keepdim=True))).square().mean()
    elif method in ['DET-INVERSE','PROB-INVERSE']:
        recovered=head(torch.cat([z[:,2:7],pred],-1));label=raw[:,2:7].detach()
        if method=='DET-INVERSE':aux=.1*(recovered-label).square().mean()
        else:
            mean,logvar=recovered.chunk(2,-1);logvar=logvar.clamp(-5,5)
            aux=.1*.5*((label-mean).square()*(-logvar).exp()+logvar).mean()
    return base+.09*reg+aux,base,reg,aux

@torch.no_grad()
def audit_candidates(model,images,actions,physical,mean,std):
    model.eval(); rows=[]
    for j in range(32,44):
        goal_id=2+j%10;past=normalized_pixels(images[j,0,:3][None],'cuda')
        initial=model.encode({'pixels':past})['emb'].expand(12,-1,-1).clone()
        goal=model.encode({'pixels':normalized_pixels(images[j,goal_id,-1][None,None],'cuda')})['emb'][0,-1]
        a=torch.as_tensor((actions[j]-mean)/std,device='cuda').float().reshape(12,7,10)
        act=model.action_encoder(a);z=initial
        for h in range(5):z=torch.cat([z,model.predict(z[:,-3:],act[:,h:h+3])[:,-1:]],1)
        scores=(z[:,-1]-goal).square().sum(-1).cpu().numpy();selected=int(scores.argmin())
        distances=np.linalg.norm(physical[j]-physical[j,goal_id],axis=-1)
        assert distances[goal_id]==0 and np.isfinite(scores).all()
        rows.append(dict(anchor=j,goal_candidate=goal_id,selected=selected,success=bool(distances[selected]<16),
            physical_distance=float(distances[selected]),best_distance=float(distances.min()),
            predicted_scores=scores.tolist(),actual_distances=distances.tolist()))
    return rows

def run(args):
    torch.set_num_threads(4);out=Path(args.output);cache=Path(args.model_cache)
    assert not out.exists() and not cache.exists() and cache.resolve().is_relative_to(Path('/home/xiang/.cache/huggingface'))
    out.mkdir(parents=True);cache.mkdir(parents=True)
    images,actions,physical,bank_cfg=load_bank(args.bank)
    c=torch.load(args.checkpoint,map_location='cpu',weights_only=False);assert c['steps']==5650 and len(c['manifest']['base_episodes'])==100
    mean,std=np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std'])
    torch.manual_seed(args.seed);np.random.seed(args.seed);model=architecture(c['config']);model.load_state_dict(c['state_dict'],strict=True)
    initial=state_hash(model.state_dict());source_hash=digest(args.checkpoint);model=model.cuda()
    head=torch.nn.Sequential(torch.nn.Linear(384,256),torch.nn.ReLU(),torch.nn.Linear(256,20 if args.method=='PROB-INVERSE' else 10)).cuda()
    torch.cuda.manual_seed_all(args.seed);torch.manual_seed(args.seed)
    parameters=list(model.parameters())+(list(head.parameters()) if 'INVERSE' in args.method else [])
    optimizer=torch.optim.AdamW(parameters,lr=5e-5,weight_decay=1e-3);assert not optimizer.state
    sigreg=SIGReg(knots=17,num_proj=1024).cuda();rng=np.random.default_rng(104800+args.seed);legal_ids=np.array([0]+list(range(2,12)))
    config=dict(vars(args),initial_tensor_sha256=initial,source_checkpoint_sha256=source_hash,bank_complete_sha256=digest(Path(args.bank)/'complete.json'),bank_config=bank_cfg,
        train_anchors=list(range(32)),query_anchors=list(range(32,44)),duplicate_branch_excluded=True,
        objective='five sliding teacher-forced future targets; no target detach in base + .09 SIGReg + named aux',
        batch_groups=8,branches_per_group=4,updates=2000,lr=5e-5,weight_decay=1e-3,precision='bf16',script_sha256=digest(__file__),
        scope='joint encoder/predictor training; raw inverse component is not full SMWM/AD-WM; held-out branches from WM-pretrained episodes; no native closed-loop proof',hardware=torch.cuda.get_device_name())
    dump(out/'config.json',config);shutil.copy2(__file__,out/'effect_training_used.py');logs=[];summaries=[]
    before=audit_candidates(model,images,actions,physical,mean,std);dump(out/'queries_u0.json',before)
    summaries.append(dict(updates=0,successes=sum(r['success'] for r in before),n=12))
    for step in range(1,2001):
        model.train().requires_grad_(True);head.train();anchors=rng.integers(0,32,8);branches=np.stack([rng.choice(legal_ids,4,replace=False) for _ in anchors])
        picked=images[anchors[:,None],branches].reshape(32,8,224,224,3);physical_actions=actions[anchors[:,None],branches]
        raw=torch.as_tensor((physical_actions-mean)/std,device='cuda').float().reshape(32,7,10)
        a=torch.cat([raw,torch.zeros_like(raw[:,:1])],1);x=normalized_pixels(picked,'cuda')
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast('cuda',dtype=torch.bfloat16):loss,base,reg,aux=losses(model,head,sigreg,x,a,raw,args.method,8,4)
        assert torch.isfinite(loss);loss.backward();grad=torch.nn.utils.clip_grad_norm_(parameters,1.);assert torch.isfinite(grad);optimizer.step()
        if step==1 or step%25==0:
            logs.append(dict(step=step,loss=float(loss),base=float(base),reg=float(reg),aux=float(aux)));dump(out/'training.json',logs);print('effect_train',args.method,args.seed,step,flush=True)
        if step in [600,2000]:
            saved=(torch.get_rng_state(),torch.cuda.get_rng_state_all(),copy.deepcopy(np.random.get_state()),copy.deepcopy(rng.bit_generator.state))
            weight_hash=state_hash(model.state_dict());rows=audit_candidates(model,images,actions,physical,mean,std);dump(out/f'queries_u{step}.json',rows)
            assert weight_hash==state_hash(model.state_dict())
            torch.set_rng_state(saved[0]);torch.cuda.set_rng_state_all(saved[1]);np.random.set_state(saved[2]);rng.bit_generator.state=saved[3]
            p=cache/f'u{step}.ckpt';torch.save(dict(state_dict=model.state_dict(),aux_head=head.state_dict(),optimizer=optimizer.state_dict(),steps=step,config=c['config'],manifest=c['manifest'],rng=saved),p)
            summaries.append(dict(updates=step,successes=sum(r['success'] for r in rows),n=12,checkpoint_sha256=digest(p)));dump(out/'summary.json',summaries)
    assert digest(args.checkpoint)==source_hash
    dump(out/'complete.json',dict(completed=True,method=args.method,seed=args.seed,updates=2000));shutil.copytree(out,Path('/home/xiang/.cache/latent-wm-results')/out.name)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['bank','checkpoint','output','model-cache']:p.add_argument('--'+n,required=True)
    p.add_argument('--method',choices=METHODS,required=True);p.add_argument('--seed',type=int,required=True);args=p.parse_args()
    try:run(args)
    except Exception as error:
        if Path(args.output).exists():dump(Path(args.output)/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise
