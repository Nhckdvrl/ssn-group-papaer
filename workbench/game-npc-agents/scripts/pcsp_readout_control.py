#!/usr/bin/env python3
"""E17 original native policies frozen; only original trajectory reader fitted."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--mode',choices=['smoke','collect','fit'],required=True)
    ap.add_argument('--policy-seed',type=int,default=42)
    ap.add_argument('--updates',type=int,default=1000)
    args=ap.parse_args()
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv,N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic,TrajectoryEncoder,PCSPConfig
    torch.set_num_threads(1)
    dump=lambda f,v:Path(f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    if args.mode!='fit':args.out.mkdir(parents=True,exist_ok=False)
    embeddings=np.load(args.source/'results/embeddings/persona_embeddings_500.npy').astype(np.float32)
    train=json.loads((args.source/'research/data/personas/train_400_v3.json').read_text())
    test=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    groups={'train':(train[:320],2),'calibration':(train[320:],2),'test':(test,3)}
    def modules(mode):
        folder=args.source/f'research/results/pcsp_v3_large/{mode}_seed{args.policy_seed}/{mode}'
        policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
        policy.load_state_dict(torch.load(folder/'policy.pt',map_location='cpu',weights_only=True),strict=True)
        reader=TrajectoryEncoder(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
        reader.load_state_dict(torch.load(folder/'traj_encoder.pt',map_location='cpu',weights_only=True),strict=True)
        policy.eval().requires_grad_(False);reader.eval()
        return policy,reader,folder
    def policy_hash(policy):
        h=hashlib.sha256()
        for k,v in policy.state_dict().items():h.update(k.encode());h.update(v.cpu().numpy().tobytes())
        return h.hexdigest()
    def collect(policy,records,seed):
        actual=len(records);padded=list(records)
        while len(padded)<N_AGENTS:padded.append(records[len(padded)%actual])
        env=MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(r) for r in padded],max_steps=200)
        env.reset(seed=seed);torch.manual_seed(seed+1000003)
        vectors=torch.from_numpy(embeddings[[int(r['id'])-1 for r in padded]])
        observations=[[] for _ in padded];actions=[[] for _ in padded];rewards=[0. for _ in padded]
        for cycle in range(200):
            # Same batch-before-cycle sampling as official independent behavior
            # protocol. All physical application remains the original AEC.
            obs=np.stack([env.observe(a) for a in env.possible_agents])
            with torch.inference_mode():
                logits=policy.action_logits(torch.from_numpy(obs),vectors)
                chosen=torch.distributions.Categorical(logits=logits).sample().numpy()
            for i,(agent,action) in enumerate(zip(env.possible_agents,chosen)):
                assert env.agent_selection==agent
                observations[i].append(obs[i]);actions[i].append(int(action))
                env.step(int(action));rewards[i]+=float(env.rewards[agent])
        env.close()
        return np.asarray(observations[:actual],dtype=np.float32),np.asarray(actions[:actual],dtype=np.int64),np.asarray(rewards[:actual])
    start=time.monotonic()
    if args.mode=='smoke':
        policy,_,folder=modules('no_consist')
        first=collect(policy,train[:N_AGENTS],171717)
        again=collect(policy,train[:N_AGENTS],171717)
        assert all(np.array_equal(a,b) for a,b in zip(first,again))
        np.savez_compressed(args.out/'native_episode.npz',obs=first[0],actions=first[1],rewards=first[2])
        dump(args.out/'summary.json',{'agents':N_AGENTS,'cycles':200,'actions':N_AGENTS*200,
            'exact_native_replay':True,'policy_hash':policy_hash(policy),'wall_seconds':time.monotonic()-start,
            'mean_native_reward':float(first[2].mean()),'cloud_calls':0,'gpu_hours':0})
        return
    if args.mode=='collect':
        manifest={'source':str(args.source),'policy_seed':args.policy_seed,'agents':N_AGENTS,'steps':200,
            'sampling':'official independent_behavior batch-before-cycle, randomized cohort order per episode',
            'reader_protocol':'focal per-agent own200; source joint-prefix is separate E18 control',
            'cloud_calls':0,'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        dump(args.out/'manifest.json',manifest)
        for mode in ['full','no_consist']:
            policy,_,folder=modules(mode);manifest[mode+'_policy_hash']=policy_hash(policy)
            for phase_index,(phase,(records,n_episodes)) in enumerate(groups.items()):
                obs_parts,act_parts,id_parts,reward_parts=[],[],[],[]
                for ep in range(n_episodes):
                    rng=np.random.default_rng(171717+phase_index*10000+ep*1000)
                    order=rng.permutation(len(records))
                    shuffled=[records[int(i)] for i in order]
                    for offset in range(0,len(records),N_AGENTS):
                        batch=shuffled[offset:offset+N_AGENTS]
                        obs,actions,rewards=collect(policy,batch,171717+phase_index*10000+ep*1000+offset)
                        obs_parts.append(obs);act_parts.append(actions);reward_parts.append(rewards)
                        id_parts.extend(int(r['id']) for r in batch)
                obs=np.concatenate(obs_parts);actions=np.concatenate(act_parts);rewards=np.concatenate(reward_parts)
                np.savez_compressed(args.out/f'{mode}_{phase}.npz',obs=obs,actions=actions,rewards=rewards,ids=np.asarray(id_parts))
                print(json.dumps({'mode':mode,'phase':phase,'trajectories':len(obs),'mean_reward':float(rewards.mean())}),flush=True)
            assert policy_hash(policy)==manifest[mode+'_policy_hash']
        manifest['collection_seconds']=time.monotonic()-start;dump(args.out/'manifest.json',manifest)
        return
    # Readout fitting never changes actor, critic, projection or cached world.
    cfg=PCSPConfig();policy,reader,folder=modules('no_consist')
    before=policy_hash(policy);torch.manual_seed(171717)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    reader.to(device).train()
    datasets={}
    for phase in groups:
        with np.load(args.out/f'no_consist_{phase}.npz') as d:
            datasets[phase]={k:d[k].copy() for k in d.files}
    with torch.inference_mode():all_targets=policy.persona_proj(torch.from_numpy(embeddings)).to(device)
    def evaluate(current,mode,phase):
        with np.load(args.out/f'{mode}_{phase}.npz') as data:
            candidate_records=groups[phase][0]
            candidate_ids=[int(r['id']) for r in candidate_records]
            mode_policy,_,_=modules(mode)
            with torch.inference_mode():target=mode_policy.persona_proj(torch.from_numpy(embeddings[np.asarray(candidate_ids)-1])).to(device)
            correct=[];top3=[];ids=[]
            current.eval()
            for offset in range(0,len(data['ids']),32):
                with torch.inference_mode():
                    z=current(torch.from_numpy(data['obs'][offset:offset+32]).to(device),
                              torch.from_numpy(data['actions'][offset:offset+32]).to(device))
                    ranking=(z@target.T).topk(3,dim=-1).indices.cpu().numpy()
                for actual,rank in zip(data['ids'][offset:offset+32],ranking):
                    ids.append(int(actual));correct.append(candidate_ids[int(rank[0])]==int(actual));top3.append(int(actual) in [candidate_ids[int(i)] for i in rank])
            return {'top1':float(np.mean(correct)),'top3':float(np.mean(top3)),'candidate_count':len(candidate_ids),
                'persona_ids':ids,'top1_correct':list(map(int,correct)),'native_reward_mean':float(data['rewards'].mean())}
    # Full positive control and no_consist zero-update reader on same corrected
    # unit, candidate pool and native episode construction.
    _,full_reader,_=modules('full');full_reader.to(device)
    baseline_full=evaluate(full_reader,'full','test')
    baseline_no=evaluate(reader,'no_consist','test')
    dump(args.out/'original_readers.json',{'full':baseline_full,'no_consist':baseline_no})
    if baseline_full['top1'] <= 1.0/baseline_full['candidate_count']:
        dump(args.out/'positive_control_failed.json',{
            'reason':'Original full reader did not exceed chance on the corrected unit; audit protocol before fitting.',
            'full':baseline_full,'no_consist':baseline_no,'policy_unchanged':True})
        return
    train_data=datasets['train'];train_ids=sorted(set(map(int,train_data['ids'])))
    index_by_id={pid:np.flatnonzero(train_data['ids']==pid) for pid in train_ids}
    train_obs=torch.from_numpy(train_data['obs']).to(device);train_act=torch.from_numpy(train_data['actions']).to(device)
    optimizer=torch.optim.Adam(reader.parameters(),lr=cfg.traj_lr)
    rng=np.random.default_rng(171717);best=-1.;best_state=None;history=[]
    for update in range(1,args.updates+1):
        chosen_ids=rng.choice(train_ids,32,replace=False)
        chosen=np.asarray([rng.choice(index_by_id[int(pid)]) for pid in chosen_ids])
        reader.train();output=reader(train_obs[chosen],train_act[chosen])
        target=all_targets[torch.from_numpy(chosen_ids-1).to(device)]
        loss=torch.nn.functional.cross_entropy(output@target.T/cfg.temperature,torch.arange(32,device=device))
        optimizer.zero_grad();loss.backward();optimizer.step()
        if update%100==0:
            val=evaluate(reader,'no_consist','calibration')
            row={'update':update,'train_loss':float(loss.detach()),'calibration_top1':val['top1'],'calibration_top3':val['top3']}
            history.append(row);dump(args.out/'fit_history.json',history);print(json.dumps(row),flush=True)
            if val['top1']>best:
                best=val['top1'];best_state={k:v.detach().cpu().clone() for k,v in reader.state_dict().items()}
    reader.load_state_dict(best_state);calibrated=evaluate(reader,'no_consist','test')
    torch.save(best_state,args.out/'calibrated_reader.pt')
    assert policy_hash(policy)==before
    assert all(p.grad is None for p in policy.parameters())
    boot_rng=np.random.default_rng(171919)
    correct_by_id={pid:np.mean([c for p,c in zip(calibrated['persona_ids'],calibrated['top1_correct']) if p==pid]) for pid in set(calibrated['persona_ids'])}
    scores=np.asarray(list(correct_by_id.values()));boot=[np.mean(boot_rng.choice(scores,len(scores),replace=True)) for _ in range(2000)]
    dump(args.out/'fit_result.json',{'original_full':baseline_full,'original_no_consist':baseline_no,'calibrated_no_consist':calibrated,
        'calibrated_top1_persona_bootstrap95':np.quantile(boot,[.025,.975]).tolist(),'best_calibration_top1':best,
        'policy_projection_hash_before':before,'policy_projection_hash_after':policy_hash(policy),
        'policy_or_projection_updated':False,'native_rollouts_unchanged':True,'world_or_reward_changed':False,
        'fit_seconds':time.monotonic()-start,'scientific_increment':0,'cloud_calls':0})


if __name__=='__main__':main()
