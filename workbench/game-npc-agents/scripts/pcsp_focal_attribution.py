#!/usr/bin/env python3
"""E18 native AEC, exact source-unit control and focal/peer assignment forks."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--world-seeds',nargs='+',type=int,default=[17301,17302,17303])
    ap.add_argument('--policy-seed',type=int,default=42)
    args=ap.parse_args()
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv,N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3,ACTION_NAMES_V3
    from src.training.pcsp_trainer import PCSPActorCritic,TrajectoryEncoder
    from src.eval.consistency import _rollout_persona
    torch.set_num_threads(1)
    args.out.mkdir(parents=True,exist_ok=False)
    folder=args.source/f'research/results/pcsp_v3_large/full_seed{args.policy_seed}/full'
    policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
    policy.load_state_dict(torch.load(folder/'policy.pt',map_location='cpu',weights_only=True),strict=True)
    encoder=TrajectoryEncoder(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
    encoder.load_state_dict(torch.load(folder/'traj_encoder.pt',map_location='cpu',weights_only=True),strict=True)
    policy.eval().requires_grad_(False);encoder.eval().requires_grad_(False)
    records=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    embeddings=np.load(args.source/'results/embeddings/persona_embeddings_500.npy').astype(np.float32)
    vectors=torch.from_numpy(embeddings[[int(r['id'])-1 for r in records]])
    with torch.inference_mode():targets=policy.persona_proj(vectors)
    a=0
    distances=1-(targets@targets[a]).numpy()
    eligible=[i for i,r in enumerate(records) if r['big_five']!=records[a]['big_five']]
    b=max(eligible,key=lambda i:distances[i])
    configs={i:PersonaConfig.from_dict(records[i]) for i in [a,b]}
    dump=lambda f,v:Path(f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    manifest={'source':str(args.source),'policy_seed':args.policy_seed,'world_seeds':args.world_seeds,
        'A':records[a],'B':records[b],'agents':N_AGENTS,'cycles':200,'candidate_count':len(records),
        'asset_hashes':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in
            [folder/'policy.pt',folder/'traj_encoder.pt',args.source/'results/embeddings/persona_embeddings_500.npy',Path(__file__)]},
        'gpu_hours':0,'cloud_calls':0}
    dump(args.out/'manifest.json',manifest)
    def decode(obs,actions):
        with torch.inference_mode():
            z=encoder(torch.from_numpy(np.asarray(obs,dtype=np.float32)).unsqueeze(0),
                      torch.from_numpy(np.asarray(actions,dtype=np.int64)).unsqueeze(0))
            scores=(z@targets.T).numpy()[0]
        order=np.argsort(-scores)
        return {'top1_id':records[int(order[0])]['id'],'top3_ids':[records[int(i)]['id'] for i in order[:3]],
            'cosine_A':float(scores[a]),'cosine_B':float(scores[b]),'all_cosines':scores.tolist()}
    start=time.monotonic();summary=[]
    for world_seed in args.world_seeds:
        for condition,focal,peer in [('all_A',a,a),('all_B',b,b),('focal_A_peer_B',a,b),('focal_B_peer_A',b,a)]:
            assignment=[focal]+[peer]*(N_AGENTS-1)
            env=MiniInzoiV3LargeEnv(personas=[configs[i] for i in assignment],max_steps=200)
            env.reset(seed=world_seed);torch.manual_seed(world_seed+17)
            joint_obs,joint_actions,actor_ids=[],[],[]
            own_obs,own_actions,own_rewards,own_kl=[],[],[],[]
            for cycle in range(200):
                for index,agent in enumerate(env.possible_agents):
                    assert env.agent_selection==agent
                    obs=env.observe(agent).copy()
                    with torch.inference_mode():
                        action,_,_=policy.get_action(torch.from_numpy(obs).unsqueeze(0),vectors[assignment[index]].unsqueeze(0))
                        action=int(action.item())
                        if index==0:
                            log_a=policy.action_logits(torch.from_numpy(obs).unsqueeze(0),vectors[a].unsqueeze(0)).log_softmax(-1)
                            log_b=policy.action_logits(torch.from_numpy(obs).unsqueeze(0),vectors[b].unsqueeze(0)).log_softmax(-1)
                            own_kl.append(float((log_a.exp()*(log_a-log_b)).sum()))
                    joint_obs.append(obs);joint_actions.append(action);actor_ids.append(index)
                    env.step(action)
                    if index==0:
                        own_obs.append(obs);own_actions.append(action);own_rewards.append(float(env.rewards[agent]))
            joint_obs=np.asarray(joint_obs,dtype=np.float32);joint_actions=np.asarray(joint_actions,dtype=np.int64)
            folder_out=args.out/f'{condition}_s{world_seed}';folder_out.mkdir()
            np.savez_compressed(folder_out/'native_trace.npz',obs=joint_obs,actions=joint_actions,
                actor_ids=np.asarray(actor_ids,dtype=np.int16))
            row={'condition':condition,'world_seed':world_seed,'focal_id':records[focal]['id'],
                'peer_id':records[peer]['id'],'joint_frames':len(joint_actions),'own_frames':len(own_actions),
                'source_joint_first200':decode(joint_obs[:200],joint_actions[:200]),
                'focal_own200':decode(own_obs,own_actions),'own_action_counts':dict(Counter(ACTION_NAMES_V3[i] for i in own_actions)),
                'focal_native_reward':sum(own_rewards),'final_focal_needs':env.needs[0].tolist(),
                'same_state_persona_A_B_KL_mean':float(np.mean(own_kl)),
                'joint_actor_counts_first200':dict(Counter(actor_ids[:200]))}
            if condition=='all_A' and world_seed==args.world_seeds[0]:
                torch.manual_seed(world_seed+17)
                original=_rollout_persona(policy,vectors[a].unsqueeze(0),configs[a],1,torch.device('cpu'),
                    seed_offset=world_seed,n_agents=N_AGENTS,
                    env_factory=lambda personas:MiniInzoiV3LargeEnv(personas=personas,max_steps=200))[0]
                assert np.array_equal(joint_obs,original['obs_seq'])
                assert np.array_equal(joint_actions,original['act_seq'])
                row['original_helper_byte_replay_matched']=True
            env.close();dump(folder_out/'summary.json',row);summary.append(row)
            dump(args.out/'summary.json',summary)
            print(json.dumps({k:v for k,v in row.items() if k not in ['source_joint_first200','focal_own200','joint_actor_counts_first200','own_action_counts','final_focal_needs']}|{
                'joint_pred':row['source_joint_first200']['top1_id'],'focal_pred':row['focal_own200']['top1_id']}),flush=True)
    dump(args.out/'runtime.json',{'wall_seconds':time.monotonic()-start,'scientific_increment':0})


if __name__=='__main__':main()
