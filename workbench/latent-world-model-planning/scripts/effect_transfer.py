"""E20 PushT extension: all five mechanisms, matched full joint training.

Published pretraining is unknown. This is a first-seed transfer pilot, not
a fixed-data-from-scratch replication or a complete AD-WM baseline.
"""
import argparse
import copy
import gc
import json
import shutil
from pathlib import Path
import numpy as np
import torch
import effect_training as e
from fixed_data_train_seed import normalized_pixels, state_hash
from lewm_pilot import architecture, digest, dump
from module import SIGReg

SOURCE = Path('/home/xiang/.cache/huggingface/latent-wm-derived/lewm-pusht-object.ckpt')
SOURCE_SHA = '0c095fc4a26856678f67bf299f261506b45f1a25fbdb4cbb8828b4a8281dc048'
ARTIFACTS = Path('/home/xiang/.cache/latent-wm-results')


def load_bank(path):
    path = Path(path); assert json.loads((path/'complete.json').read_text())['anchors'] == 88
    ledger = json.loads((path/'ledger.json').read_text()); records = json.loads((path/'rows.json').read_text())
    entries = sorted([r for r in ledger if r['task']=='pusht'], key=lambda r:r['anchor'])
    assert [r['anchor'] for r in entries] == list(range(44))
    images, actions, states = [], [], []
    for entry in entries:
        im, act, st = [], [], []
        for k in range(12):
            p = path/f'pusht_{entry["anchor"]:03d}_b{k:02d}.npz'
            record = next(r for r in records if r['task']=='pusht' and r['anchor']==entry['anchor'] and r['branch']==k)
            assert digest(p)==record['trace_sha256']; data = np.load(p)
            im.append(np.concatenate([data['history'], data['pixels'][[5,10,15,20,25]]]))
            a = np.concatenate([entry['warm_actions'], data['issued_actions']])
            assert a.shape==(35,2) and (np.abs(a)<=1).all()
            act.append(a); st.append(data['diagnostic_states'][-1,:7])
        images.append(im); actions.append(act); states.append(st)
    return np.asarray(images), np.asarray(actions), np.asarray(states)


def load_source(device):
    assert digest(SOURCE)==SOURCE_SHA
    metadata = json.loads(SOURCE.with_suffix('.metadata.json').read_text()); cfg = metadata['model_config']
    original = torch.load(SOURCE, map_location='cpu', weights_only=False)
    model = architecture(cfg); model.load_state_dict(original.state_dict(), strict=True)
    assert len(model.state_dict())==303 and not getattr(original, 'residual_target', False)
    norm_path = ARTIFACTS/'20261002-pusht-native-s0/action_normalization.npz'; norm = np.load(norm_path)
    return model.to(device), cfg, norm['mean'], norm['std'], digest(norm_path)


@torch.no_grad()
def queries(model, images, actions, physical, mean, std, device):
    model.eval(); rows = []
    for j in range(32,44):
        goal_id = 2+j%10
        initial = model.encode({'pixels':normalized_pixels(images[j,0,:3][None], device)})['emb'].expand(12,-1,-1).clone()
        goal = model.encode({'pixels':normalized_pixels(images[j,goal_id,-1][None,None], device)})['emb'][0,-1]
        raw = torch.as_tensor((actions[j]-mean)/std, device=device).float().reshape(12,7,10)
        act = model.action_encoder(raw); z = initial
        for h in range(5): z = torch.cat([z, model.predict(z[:,-3:],act[:,h:h+3])[:,-1:]],1)
        scores = (z[:,-1]-goal).square().sum(-1).cpu().numpy(); selected = int(scores.argmin())
        distances = np.linalg.norm(physical[j]-physical[j,goal_id], axis=-1)
        position = np.linalg.norm(physical[j,:,:4]-physical[j,goal_id,:4],axis=-1)
        angle = np.abs(physical[j,:,4]-physical[j,goal_id,4]); angle = np.minimum(angle,2*np.pi-angle)
        success = (position<20)&(angle<np.pi/9)
        assert success[goal_id] and distances[goal_id]==0 and np.isfinite(scores).all()
        rows.append(dict(anchor=j,goal_candidate=goal_id,selected=selected,success=bool(success[selected]),
            predicted_scores=scores.tolist(),actual_distances_7d=distances.tolist(),
            actual_position_distances=position.tolist(),actual_angle_distances=angle.tolist(),
            actual_native_success=success.tolist()))
    return rows


def train(args):
    torch.set_num_threads(4); images, actions, physical = load_bank(args.bank)
    for method in e.METHODS:
        name = f'20261004-E20-joint-pusht-{method}-RTX-s0'; out = Path(args.output_root)/name
        cache = Path('/home/xiang/.cache/huggingface/latent-wm-trained')/name
        assert not out.exists() and not cache.exists(); out.mkdir(); cache.mkdir()
        try:
            torch.manual_seed(0); np.random.seed(0); model,cfg,mean,std,norm_sha = load_source('cuda')
            initial = state_hash(model.state_dict())
            head = torch.nn.Sequential(torch.nn.Linear(384,256),torch.nn.ReLU(),torch.nn.Linear(256,20 if method=='PROB-INVERSE' else 10)).cuda()
            torch.manual_seed(0); torch.cuda.manual_seed_all(0)
            params = list(model.parameters())+(list(head.parameters()) if 'INVERSE' in method else [])
            optimizer = torch.optim.AdamW(params,lr=5e-5,weight_decay=1e-3); assert not optimizer.state
            sigreg = SIGReg(knots=17,num_proj=1024).cuda(); rng = np.random.default_rng(105800)
            legal_ids = np.array([0]+list(range(2,12)))
            config = dict(task='pusht',method=method,seed=0,source_checkpoint=str(SOURCE),source_sha256=SOURCE_SHA,
                initial_tensor_sha256=initial,normalization_sha256=norm_sha,bank_complete_sha256=digest(Path(args.bank)/'complete.json'),
                train_anchors=list(range(32)),query_anchors=list(range(32,44)),batch_groups=8,branches_per_group=4,
                updates=2000,precision='bf16',lr=5e-5,weight_decay=1e-3,sample_rng_seed=105800,
                script_sha256=digest(__file__),loss_helper_sha256=digest(e.__file__),hardware=torch.cuda.get_device_name(),
                scope='published source pretraining split unknown; joint transfer first seed; full-bank development, not native closed-loop')
            dump(out/'config.json',config); shutil.copy2(__file__,out/'effect_transfer_used.py'); shutil.copy2(e.__file__,out/'effect_training_used.py')
            summaries=[]; logs=[]
            for step in range(2001):
                if step in [0,600,2000]:
                    saved=(torch.get_rng_state(),torch.cuda.get_rng_state_all(),copy.deepcopy(np.random.get_state()),copy.deepcopy(rng.bit_generator.state))
                    before=state_hash(model.state_dict()); rows=queries(model,images,actions,physical,mean,std,'cuda')
                    assert before==state_hash(model.state_dict()); dump(out/f'queries_u{step}.json',rows)
                    torch.set_rng_state(saved[0]);torch.cuda.set_rng_state_all(saved[1]);np.random.set_state(saved[2]);rng.bit_generator.state=saved[3]
                    snapshot=dict(updates=step,successes=sum(r['success'] for r in rows),n=12)
                    if step:
                        p=cache/f'u{step}.ckpt'
                        torch.save(dict(state_dict=model.state_dict(),aux_head=head.state_dict(),optimizer=optimizer.state_dict(),steps=step,
                            config=cfg,manifest=dict(action_mean=mean.tolist(),action_std=std.tolist(),base_episodes=[],pretraining_split_unknown=True),rng=saved),p)
                        snapshot['checkpoint_sha256']=digest(p)
                    summaries.append(snapshot);dump(out/'summary.json',summaries)
                if step==2000:break
                model.train().requires_grad_(True);head.train()
                anchors=rng.integers(0,32,8);branches=np.stack([rng.choice(legal_ids,4,replace=False) for _ in anchors])
                x=normalized_pixels(images[anchors[:,None],branches].reshape(32,8,224,224,3),'cuda')
                raw=torch.as_tensor((actions[anchors[:,None],branches]-mean)/std,device='cuda').float().reshape(32,7,10)
                a=torch.cat([raw,torch.zeros_like(raw[:,:1])],1);optimizer.zero_grad(set_to_none=True)
                with torch.autocast('cuda',dtype=torch.bfloat16):loss,base,reg,aux=e.losses(model,head,sigreg,x,a,raw,method,8,4)
                assert torch.isfinite(loss);loss.backward();grad=torch.nn.utils.clip_grad_norm_(params,1.);assert torch.isfinite(grad);optimizer.step()
                if step==0 or (step+1)%25==0:
                    logs.append(dict(step=step+1,loss=float(loss),base=float(base),reg=float(reg),aux=float(aux)))
                    dump(out/'training.json',logs);print('effect_transfer',method,step+1,flush=True)
            assert digest(SOURCE)==SOURCE_SHA
            dump(out/'complete.json',dict(completed=True,method=method,seed=0,updates=2000))
            shutil.copytree(out,ARTIFACTS/name)
            del model,head,optimizer,sigreg,params;gc.collect();torch.cuda.empty_cache()
        except Exception as error:
            dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bank',required=True);p.add_argument('--output-root',required=True)
    train(p.parse_args())
