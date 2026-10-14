#!/usr/bin/env python3
"""E28 instrument original actual co-training steps; no world/reward edits."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--route',choices=['full','no'],required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv,N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic,TrajectoryEncoder,PCSPTrainer,PCSPConfig
    torch.set_num_threads(1);torch.manual_seed(28001);np.random.seed(28001);random.seed(28001)
    train=json.loads((args.source/'research/data/personas/train_400_v3.json').read_text())
    test=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    e=np.load(args.runs/'e23_embedding_context/proper_pool.npy').astype(np.float32)
    train_e=torch.from_numpy(e[[int(r['id'])-1 for r in train]])
    test_e=torch.from_numpy(e[[int(r['id'])-1 for r in test]])
    folder=args.runs/f'e25_30_{args.route}'
    def new_policy(state):
        policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
        policy.load_state_dict(state,strict=True);policy.eval();return policy
    def state(module):return {k:v.detach().cpu().clone() for k,v in module.state_dict().items()}
    policy=new_policy(torch.load(folder/'policy.pt',map_location='cpu',weights_only=True))
    reader=TrajectoryEncoder(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
    reader.load_state_dict(torch.load(folder/'traj_encoder.pt',map_location='cpu',weights_only=True),strict=True)
    cfg=PCSPConfig(seed=42)
    if args.route=='no':cfg.lambda_consistency=0.
    trainer=PCSPTrainer(policy,reader,cfg,'cpu');trainer.iteration=30
    saved=torch.load(folder/'training_state.pt',map_location='cpu',weights_only=False)
    trainer.optimizer.load_state_dict(saved['policy_optimizer']);trainer.traj_optimizer.load_state_dict(saved['reader_optimizer'])
    # Deliberate fresh sampling stream, paired across routes; original source
    # update, epoch count, rewards, and body configuration are untouched.
    sampler_rng=np.random.default_rng(28001)
    def sampler():
        chosen=sampler_rng.choice(len(train),N_AGENTS,replace=False)
        return [PersonaConfig.from_dict(train[i]) for i in chosen],{
            f'agent_{j}':{'e_llm':train_e[i:i+1]} for j,i in enumerate(chosen)}
    factory=lambda personas:MiniInzoiV3LargeEnv(personas=personas,max_steps=200)
    dump=lambda name,value:(args.out/name).write_text(json.dumps(value,indent=2)+'\n')
    dump('manifest.json',{'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf','route':args.route,
        'cfg':vars(cfg),'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'checkpoint_sha256':hashlib.sha256((folder/'policy.pt').read_bytes()).hexdigest(),
        'fit_ids':[r['id'] for r in train],'native_world_seeds':[28011,28012,28013],
        'counterfactuals_fed_back_to_training':False,'world_or_reward_changed':False,'cloud_calls':0})
    start=time.monotonic()
    transitions,rewards,trajectories=trainer.collect_rollout(factory,sampler,cfg.n_episodes_per_iter)
    snapshots=[];flag={'co':False};pending={}
    original_cons=trainer._consistency_loss
    def consistency(rows):flag['co']=True;return original_cons(rows)
    trainer._consistency_loss=consistency
    original_policy_step=trainer.optimizer.step
    def policy_step(*a,**kw):
        if flag['co']:pending['before']=state(policy);pending['reader_before']=state(reader)
        result=original_policy_step(*a,**kw)
        if flag['co']:pending['after']=state(policy)
        return result
    trainer.optimizer.step=policy_step
    original_reader_step=trainer.traj_optimizer.step
    def reader_step(*a,**kw):
        result=original_reader_step(*a,**kw)
        if flag['co']:
            pending['reader_after']=state(reader);snapshots.append(copy.deepcopy(pending));pending.clear();flag['co']=False
        return result
    trainer.traj_optimizer.step=reader_step
    stats=trainer.update(transitions,trajectories,train_e)
    assert len(snapshots)==cfg.n_epochs==4
    torch.save(snapshots,args.out/'actual_co_snapshots.pt')
    np.savez_compressed(args.out/'actual_rollout.npz',obs=np.asarray([t['obs'] for t in transitions],dtype=np.float32),
        e=np.concatenate([t['context']['e_llm'].numpy() for t in transitions]),actions=np.asarray([t['action'] for t in transitions]))
    obs=torch.from_numpy(np.asarray([t['obs'] for t in transitions],dtype=np.float32))
    context_e=torch.cat([t['context']['e_llm'] for t in transitions])
    def logits(p):
        with torch.inference_mode():return p.action_logits(obs,context_e)
    first=new_policy(snapshots[0]['before'])
    with torch.inference_mode():z=first.persona_proj(train_e)
    # Known finite rotation in the represented span. It is a tool positive
    # control and is never presented as a natural training anomaly.
    _,_,vt=np.linalg.svd(z.numpy(),full_matrices=False)
    u,v=vt[0],vt[1];angle=np.pi/12
    rot=np.eye(64)+(np.cos(angle)-1)*(np.outer(u,u)+np.outer(v,v))+np.sin(angle)*(np.outer(u,v)-np.outer(v,u))
    rotation=torch.from_numpy(rot.astype(np.float32))
    base_logits=logits(first);rotated=new_policy(snapshots[0]['before'])
    rotated.persona_proj.register_forward_hook(lambda m,i,o:o@rotation)
    with torch.no_grad():
        for name,module in rotated.named_modules():
            if name.endswith('film.gamma_net') or name.endswith('film.beta_net'):module.weight.copy_(module.weight@rotation)
    compensated=logits(rotated)
    error=float((base_logits-compensated).abs().max())
    assert error<1e-4,error
    geometry_error=float((z@z.T-(z@rotation)@(z@rotation).T).abs().max())
    assert geometry_error<1e-5
    dump('known_rotation_gate.json',{'compensated_logit_maxabs':error,'geometry_maxabs':geometry_error,'angle_radians':angle})

    def native(p,rows,seed):
        actual=len(rows);padded=list(rows)
        while len(padded)<N_AGENTS:padded.append(rows[len(padded)%actual])
        env=factory([PersonaConfig.from_dict(r) for r in padded]);env.reset(seed=seed);torch.manual_seed(seed+1000003)
        vectors=torch.from_numpy(e[[int(r['id'])-1 for r in padded]])
        acts=[];reward=np.zeros(N_AGENTS)
        for _ in range(200):
            obs_np=np.stack([env.observe(a) for a in env.possible_agents])
            with torch.inference_mode():selected=torch.distributions.Categorical(logits=p.action_logits(torch.from_numpy(obs_np),vectors)).sample().numpy()
            acts.append(selected)
            for index,(agent,action) in enumerate(zip(env.possible_agents,selected)):
                assert env.agent_selection==agent;env.step(int(action));reward[index]+=float(env.rewards[agent])
        out={'actions':np.stack(acts).T[:actual],'rewards':reward[:actual],'final_needs':env.needs[:actual].copy()};env.close();return out
    x=native(first,test[:16],28011);y=native(first,test[:16],28011)
    assert all(np.array_equal(x[k],y[k]) for k in x)
    summary=[]
    for step,snapshot in enumerate(snapshots):
        before=new_policy(snapshot['before']);after=new_policy(snapshot['after'])
        with torch.inference_mode():a=before.persona_proj(train_e).numpy();b=after.persona_proj(train_e).numpy()
        left,_,right=np.linalg.svd(b.T@a);r=left@right
        total=float(np.square(b-a).sum());residual=float(np.square(b@r-a).sum())
        rotated_after=new_policy(snapshot['after']);r_t=torch.from_numpy(r.astype(np.float32))
        rotated_after.persona_proj.register_forward_hook(lambda m,i,o,rr=r_t:o@rr)
        old_projection=new_policy(snapshot['after']);old_projection.persona_proj.load_state_dict(before.persona_proj.state_dict())
        p_before=logits(before).log_softmax(-1)
        diagnostic={}
        for name,p in [('after',after),('aligned',rotated_after),('old_projection',old_projection)]:
            q=logits(p).log_softmax(-1)
            diagnostic[name]={'same_state_KL_mean':float((p_before.exp()*(p_before-q)).sum(-1).mean()),
                'argmax_changed':float((p_before.argmax(-1)!=q.argmax(-1)).float().mean())}
        # Identity readout/metric symmetry for any *fixed* trajectory features.
        trained_reader=TrajectoryEncoder(OBS_DIM_V3_LARGE,N_ACTIONS_V3);trained_reader.load_state_dict(snapshot['reader_after'])
        with torch.inference_mode():
            tau_z=trained_reader(torch.from_numpy(np.stack([t['obs_seq'][:200] for t in trajectories])),torch.from_numpy(np.stack([t['act_seq'][:200] for t in trajectories])))
            role_z=after.persona_proj(torch.stack([t['e_llm'] for t in trajectories]))
            score_error=float((tau_z@role_z.T-(tau_z@r_t)@(role_z@r_t).T).abs().max())
        assert score_error<1e-5
        row={'co_step':step+1,'feature_movement_energy':total,'procrustes_residual_energy':residual,
            'rotation_explained_fraction':1-residual/max(total,1e-30),'fixed_trace_cosine_max_error':score_error,'same_state':diagnostic}
        if step in [0,3]:
            ps={'before':before,'after':after,'aligned':rotated_after,'old_projection':old_projection}
            parts={name:[] for name in ps};ids=[]
            for seed in [28011,28012,28013]:
                rows=[test[int(i)] for i in np.random.default_rng(seed).permutation(100)]
                for offset in range(0,100,N_AGENTS):
                    batch=rows[offset:offset+N_AGENTS]
                    for name,p in ps.items():parts[name].append(native(p,batch,seed+offset*100))
                    ids.extend(int(t['id']) for t in batch)
            native_data={name:{k:np.concatenate([p[k] for p in array]) for k in array[0]} for name,array in parts.items()}
            results={}
            for name,data in native_data.items():
                data['ids']=np.asarray(ids);np.savez_compressed(args.out/f'co{step+1}_{name}.npz',**data)
                delta=data['rewards']-native_data['after']['rewards']
                role_delta=np.asarray([delta[data['ids']==pid].mean() for pid in sorted(set(ids))])
                rng=np.random.default_rng(282828);boot=[rng.choice(role_delta,100,replace=True).mean() for _ in range(2000)]
                results[name]={'native_reward':float(data['rewards'].mean()),'delta_vs_after':float(delta.mean()),
                    'paired_persona_cluster95':np.quantile(boot,[.025,.975]).tolist()}
            row['native']=results
        summary.append(row);dump('summary.json',{'route':args.route,'steps':summary,'source_update_stats':stats,
            'original_training_iteration_mean_reward':float(np.mean(rewards)),'wall_seconds':time.monotonic()-start,'scientific_increment':0,'cloud_calls':0})
        print(json.dumps(row),flush=True)


if __name__=='__main__':main()
