#!/usr/bin/env python3
"""E24 same authored personas, frozen policies, native encoding-context forks."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--encodings',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs/e23_embedding_context'))
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv,N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    torch.set_num_threads(1)
    dump=lambda name,obj:(args.out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    records=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    variants=['cached','source_recomputed','singleton','long_peer','proper_pool','fixed_max128']
    encodings={name:np.load(args.encodings/f'{name}.npy').astype(np.float32) for name in variants}
    body_hash=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
    dump('manifest.json',{'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'variants':variants,
        'policy_seeds':[42,43,44],'world_seeds':[24011,24012,24013],'agents':N_AGENTS,'cycles':200,
        'persona_configs_sha256':body_hash,'sampling':'source independent behavior batch-before-cycle',
        'world_or_reward_changed':False,'controller_updated':False,'cloud_calls':0})

    def load(mode,seed):
        path=args.source/f'research/results/pcsp_v3_large/{mode}_seed{seed}/{mode}/policy.pt'
        policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
        policy.load_state_dict(torch.load(path,map_location='cpu',weights_only=True),strict=True)
        policy.eval().requires_grad_(False)
        return policy,hashlib.sha256(path.read_bytes()).hexdigest()

    def rollout(policy,rows,seed,variant):
        actual=len(rows);padded=list(rows)
        while len(padded)<N_AGENTS:padded.append(rows[len(padded)%actual])
        env=MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(r) for r in padded],max_steps=200)
        env.reset(seed=seed);torch.manual_seed(seed+1000003)
        initial=np.concatenate([env.positions.flatten(),env.needs.flatten()]).copy()
        vectors=torch.from_numpy(encodings[variant][[int(r['id'])-1 for r in padded]])
        actions=[];reward=np.zeros(N_AGENTS);need_mean=np.zeros(N_AGENTS);critical=np.zeros(N_AGENTS)
        prefs=np.zeros(N_AGENTS)
        for cycle in range(200):
            obs=np.stack([env.observe(a) for a in env.possible_agents])
            with torch.inference_mode():
                chosen=torch.distributions.Categorical(logits=policy.action_logits(torch.from_numpy(obs),vectors)).sample().numpy()
            actions.append(chosen.copy())
            for index,(agent,action) in enumerate(zip(env.possible_agents,chosen)):
                assert env.agent_selection==agent
                env.step(int(action));reward[index]+=float(env.rewards[agent])
                prefs[index]+=int(int(action) in padded[index]['preferred_actions'])
            need_mean+=env.needs.mean(axis=1);critical+=(env.needs<.2).mean(axis=1)
        result={'actions':np.stack(actions)[:,:actual].T,'rewards':reward[:actual],
            'need_mean':need_mean[:actual]/200,'critical_fraction':critical[:actual]/200,
            'preferred_action_rate':prefs[:actual]/200,'final_needs':env.needs[:actual].copy(),
            'final_positions':env.positions[:actual].copy(),'initial':initial}
        env.close();return result

    start=time.monotonic();policy,_=load('full',42)
    first=rollout(policy,records[:N_AGENTS],24011,'cached')
    again=rollout(policy,records[:N_AGENTS],24011,'cached')
    assert all(np.array_equal(first[k],again[k]) for k in first)
    gate_seconds=time.monotonic()-start
    np.savez_compressed(args.out/'gate_episode.npz',**first)
    dump('native_gate.json',{'exact_complete_replay':True,'actions':N_AGENTS*200,
        'paired_episode_seconds':gate_seconds,'original_reward_mean':float(first['rewards'].mean()),'cloud_calls':0})
    print(json.dumps({'native_gate_seconds':gate_seconds}),flush=True)
    # Cost gate set before looking at encoding/utility effects.
    if gate_seconds>10:
        dump('budget_gate.json',{'reason':'Native gate too slow for predeclared full CPU budget','no_utility_result_seen':True})
        return
    summaries={}
    for policy_seed in [42,43,44]:
        for mode in ['full','no_consist']:
            policy,sha=load(mode,policy_seed);label=f'{mode}_seed{policy_seed}'
            native={v:{k:[] for k in ['actions','rewards','need_mean','critical_fraction',
                'preferred_action_rate','final_needs','final_positions']} for v in variants}
            ids=[];worlds=[]
            for world_seed in [24011,24012,24013]:
                order=np.random.default_rng(world_seed).permutation(len(records))
                shuffled=[records[int(i)] for i in order]
                for offset in range(0,len(shuffled),N_AGENTS):
                    rows=shuffled[offset:offset+N_AGENTS];state_seed=world_seed+offset*100
                    reference_initial=None
                    for variant in variants:
                        data=rollout(policy,rows,state_seed,variant)
                        if reference_initial is None:reference_initial=data['initial']
                        assert np.array_equal(data['initial'],reference_initial)
                        for key in native[variant]:native[variant][key].append(data[key])
                    ids.extend(int(r['id']) for r in rows);worlds.extend([world_seed]*len(rows))
                print(json.dumps({'policy':label,'world_seed':world_seed,'wall_seconds':time.monotonic()-start}),flush=True)
            result={}
            baseline=None
            for variant in variants:
                data={k:np.concatenate(v) for k,v in native[variant].items()}
                data.update(ids=np.asarray(ids),world_seeds=np.asarray(worlds))
                np.savez_compressed(args.out/f'{label}_{variant}.npz',**data)
                if variant=='cached':baseline=data['rewards']
                delta=data['rewards']-baseline
                per_role=np.asarray([delta[data['ids']==pid].mean() for pid in sorted(set(ids))])
                rng=np.random.default_rng(242424)
                boot=[rng.choice(per_role,len(per_role),replace=True).mean() for _ in range(2000)]
                result[variant]={'reward_mean':float(data['rewards'].mean()),'paired_reward_difference':float(delta.mean()),
                    'paired_persona_cluster95':np.quantile(boot,[.025,.975]).tolist(),
                    'preferred_action_rate':float(data['preferred_action_rate'].mean()),
                    'critical_need_fraction':float(data['critical_fraction'].mean()),
                    'mean_needs':float(data['need_mean'].mean()),'focal_trajectories':len(ids)}
            summaries[label]={'policy_sha256':sha,'variants':result}
            dump('summary.json',{'policies':summaries,'scope':'Authored v3 utility includes predefined persona preferences/style; not independent personality semantics.',
                'scientific_increment':0,'cloud_calls':0})
    assert hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()==body_hash
    dump('runtime.json',{'wall_seconds':time.monotonic()-start,'cloud_calls':0,'gpu_hours':0,
        'world_or_reward_changed':False,'controller_updated':False})


if __name__=='__main__':main()
