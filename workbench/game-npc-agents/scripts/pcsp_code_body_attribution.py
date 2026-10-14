#!/usr/bin/env python3
"""E27 original body fixed; causal role-code controls with frozen external probes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv,N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    from src.eval.independent_behavior import extract_features,fit_ridge_probe,balanced_accuracy
    torch.set_num_threads(1)
    axes=['E','N','A','C','O'];levels={'low':0,'mid':1,'high':2}
    train=json.loads((args.source/'research/data/personas/train_400_v3.json').read_text())
    test=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    lookup={int(r['id']):r for r in train+test}
    embeddings=np.load(args.source/'results/embeddings/persona_embeddings_500.npy').astype(np.float32)
    label=lambda ids:np.asarray([[levels[lookup[int(pid)]['big_five'][a]] for a in axes] for pid in ids])
    dump=lambda name,value:(args.out/name).write_text(json.dumps(value,indent=2)+'\n')
    start=time.monotonic()
    # Build frozen author features from previously retained original rollouts.
    features={p:{r:[] for r in ['action_only','behavior_context']} for p in ['train','calibration']}
    labels={p:[] for p in features}
    for seed in [42,43,44]:
        for mode in ['full','no_consist']:
            for phase in features:
                with np.load(args.runs/f'e17_full_no{seed}/{mode}_{phase}.npz') as data:
                    for actions,obs in zip(data['actions'],data['obs']):
                        row=extract_features(actions,obs)
                        for representation in features[phase]:features[phase][representation].append(row[representation])
                    labels[phase].extend(label(data['ids']))
    y={p:np.asarray(v) for p,v in labels.items()}
    probes={}
    for representation in features['train']:
        x=np.asarray(features['train'][representation]);cal=np.asarray(features['calibration'][representation])
        probes[representation]=[fit_ridge_probe(x,y['train'][:,i],cal,y['calibration'][:,i]) for i in range(5)]
        np.savez_compressed(args.out/f'{representation}_probes.npz',**{f'{axis}_{key}':getattr(probe,key) for axis,probe in zip(axes,probes[representation]) for key in ['mean','scale','weight','regularization','temperature']})
    groups={}
    for row in test:
        key=json.dumps({k:row[k] for k in ['big_five','decay_modifiers','preferred_actions']},sort_keys=True)
        groups.setdefault(key,[]).append(int(row['id']))
    assert sorted(map(len,groups.values()))==[20]*5
    within={ids[i]:ids[(i+1)%len(ids)] for ids in groups.values() for i in range(len(ids))}
    between={int(test[i]['id']):int(test[(i+20)%100]['id']) for i in range(100)}
    assert all(lookup[pid]['big_five']!=lookup[donor]['big_five'] for pid,donor in between.items())
    assignments={'own':{int(r['id']):int(r['id']) for r in test},'constant':{int(r['id']):int(train[0]['id']) for r in test},'within_body':within,'cross_body':between}
    dump('manifest.json',{'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'assignments':assignments,
        'world_seeds':[27011,27012,27013],'probe_fit_test_used':False,'body_or_reward_changed':False,'cloud_calls':0})
    def collect(policy,rows,seed,condition):
        actual=len(rows);padded=list(rows)
        while len(padded)<N_AGENTS:padded.append(rows[len(padded)%actual])
        ids=[int(r['id']) for r in padded];donors=[assignments[condition][pid] for pid in ids]
        env=MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(r) for r in padded],max_steps=200)
        env.reset(seed=seed);torch.manual_seed(seed+1000003)
        e=torch.from_numpy(embeddings[np.asarray(donors)-1]);observations=[];actions=[];rewards=np.zeros(N_AGENTS)
        for _ in range(200):
            obs=np.stack([env.observe(a) for a in env.possible_agents])
            with torch.inference_mode():selected=torch.distributions.Categorical(logits=policy.action_logits(torch.from_numpy(obs),e)).sample().numpy()
            observations.append(obs);actions.append(selected)
            for i,(agent,action) in enumerate(zip(env.possible_agents,selected)):
                assert env.agent_selection==agent;env.step(int(action));rewards[i]+=float(env.rewards[agent])
        data={'obs':np.stack(observations).transpose(1,0,2)[:actual],'actions':np.stack(actions).T[:actual],
            'rewards':rewards[:actual],'ids':np.asarray(ids[:actual]),'donor_ids':np.asarray(donors[:actual]),'final_needs':env.needs[:actual].copy()}
        env.close();return data
    summary={}
    for seed in [42,43,44]:
        for mode in ['full','no_consist']:
            policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
            file=args.source/f'research/results/pcsp_v3_large/{mode}_seed{seed}/{mode}/policy.pt'
            policy.load_state_dict(torch.load(file,map_location='cpu',weights_only=True),strict=True);policy.eval().requires_grad_(False)
            if not summary:
                one=collect(policy,test[:N_AGENTS],27011,'own');two=collect(policy,test[:N_AGENTS],27011,'own')
                assert all(np.array_equal(one[k],two[k]) for k in one)
                dump('native_gate.json',{'complete_replay_byte_identical':True,'within_body_configs_exactly_equal':True})
            results={};base_scores=None
            for condition in assignments:
                parts=[]
                for world in [27011,27012,27013]:
                    rows=[test[int(i)] for i in np.random.default_rng(world).permutation(100)]
                    for offset in range(0,100,N_AGENTS):parts.append(collect(policy,rows[offset:offset+N_AGENTS],world+offset*100,condition))
                data={k:np.concatenate([p[k] for p in parts]) for k in parts[0]}
                np.savez_compressed(args.out/f'{mode}_s{seed}_{condition}.npz',**data)
                body=label(data['ids']);donor=label(data['donor_ids']);feature_rows=[extract_features(a,o) for a,o in zip(data['actions'],data['obs'])]
                readings={};scores={}
                for representation,models in probes.items():
                    x=np.stack([r[representation] for r in feature_rows])
                    pred=np.stack([p.probabilities(x).argmax(-1) for p in models],axis=1);scores[representation]=(pred==body)
                    if condition=='own':continue
                    readings[representation]={}
                    for index,axis in enumerate(axes):
                        discord=body[:,index]!=donor[:,index]
                        delta=(scores[representation][:,index].astype(float)-base_scores[representation][:,index]).reshape(3,100)
                        # Within each seed, IDs occur in a distinct fixed shuffled
                        # order. Cluster by the actual ID rather than row position.
                        dif=(scores[representation][:,index].astype(float)-base_scores[representation][:,index])
                        role_dif=np.asarray([dif[data['ids']==pid].mean() for pid in sorted(set(data['ids']))])
                        rng=np.random.default_rng(272727);boot=[rng.choice(role_dif,100,replace=True).mean() for _ in range(1000)]
                        readings[representation][axis]={'body_balanced_accuracy':balanced_accuracy(body[:,index],pred[:,index]),
                            'body_accuracy_change':float(dif.mean()),'paired_persona_cluster95':np.quantile(boot,[.025,.975]).tolist(),
                            'discordant_n':int(discord.sum()),'follows_body_if_discordant':float(np.mean(pred[discord,index]==body[discord,index])) if discord.any() else None,
                            'follows_code_if_discordant':float(np.mean(pred[discord,index]==donor[discord,index])) if discord.any() else None}
                if condition=='own':
                    base_scores=scores
                    readings={representation:{axis:{'body_balanced_accuracy':balanced_accuracy(body[:,i],np.stack([p.probabilities(np.stack([r[representation] for r in feature_rows])).argmax(-1) for p in probes[representation]],axis=1)[:,i])} for i,axis in enumerate(axes)} for representation in probes}
                results[condition]={'native_reward':float(data['rewards'].mean()),'readings':readings}
            label_name=f'{mode}_seed{seed}';summary[label_name]=results
            dump('summary.json',{'policies':summary,'cloud_calls':0,'scientific_increment':0})
            print(json.dumps({'policy':label_name,'action_only_body_balanced_mean':{c:float(np.mean([r['body_balanced_accuracy'] for r in d['readings']['action_only'].values()])) for c,d in results.items()},'seconds':time.monotonic()-start}),flush=True)
    dump('runtime.json',{'wall_seconds':time.monotonic()-start,'gpu_hours':0,'cloud_calls':0})


if __name__=='__main__':main()
