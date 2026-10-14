#!/usr/bin/env python3
"""E26 literal presentation controls and native utility; no new reward labels."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['encode','public','corrected'],required=True)
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--model',type=Path)
    ap.add_argument('--arrays',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs/e26_semantic_codes'))
    ap.add_argument('--baseline-prefix',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs/e25_30_'))
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv,N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3,ACTION_NAMES_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    torch.set_num_threads(1)
    records=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    dump=lambda name,value:(args.out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    source_code=Path('/home/xiang/.cache/game-npc-research/runs/e23_embedding_context/proper_pool.npy')
    variants=['canonical','canonical_repeat','reverse_clauses','traits_only','action_cue']
    start=time.monotonic()
    if args.mode=='encode':
        from transformers import AutoTokenizer,AutoModel
        assert args.model is not None
        tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
        texts={variant:[] for variant in variants if variant!='canonical'}
        for row in records:
            header,body=row['text'].split('. ',1)
            clauses=[clause.strip() for clause in body.rstrip('.').split(',')]
            reversed_body=', '.join(reversed(clauses))+'.'
            assert Counter(clauses)==Counter(c.strip() for c in reversed_body.rstrip('.').split(','))
            texts['canonical_repeat'].append(row['text'])
            texts['reverse_clauses'].append(header+'. '+reversed_body)
            texts['traits_only'].append(body)
            texts['action_cue'].append(row['text']+' Preferred actions in this game: '+', '.join(ACTION_NAMES_V3[a] for a in row['preferred_actions'])+'.')
        lengths={v:[len(tok(t)['input_ids']) for t in rows] for v,rows in texts.items()}
        assert all(max(values)<=256 for values in lengths.values()),lengths
        dump('texts.json',{'test_ids':[r['id'] for r in records],'variants':texts})
        manifest={'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
            'model_revision':args.model.name,'pooling':'last real attention-mask token','max_length':256,
            'text_sha256':hashlib.sha256((args.out/'texts.json').read_bytes()).hexdigest(),
            'token_lengths':lengths,'world_or_reward_changed':False,'cloud_calls':0}
        dump('manifest.json',manifest)
        device='cuda' if torch.cuda.is_available() else 'cpu'
        model=AutoModel.from_pretrained(args.model,local_files_only=True,dtype=torch.float16).to(device).eval().requires_grad_(False)
        base=np.load(source_code).astype(np.float32)
        np.save(args.out/'canonical.npy',base)
        result={}
        for variant,rows in texts.items():
            encoded=[]
            for offset in range(0,len(rows),32):
                tokens=tok(rows[offset:offset+32],return_tensors='pt',padding=True,truncation=False).to(device)
                with torch.inference_mode():
                    hidden=model(**tokens).last_hidden_state
                    idx=tokens['attention_mask'].sum(-1)-1
                    pooled=hidden[torch.arange(len(idx),device=device),idx]
                    encoded.append(torch.nn.functional.normalize(pooled,dim=-1).float().cpu().numpy())
            e=np.concatenate(encoded);cos=np.sum(e*base[400:500],axis=1)/(np.linalg.norm(e,axis=1)*np.linalg.norm(base[400:500],axis=1))
            result[variant]={'cosine_mean':float(cos.mean()),'cosine_min':float(cos.min()),'cosines':cos.tolist()}
            out=base.copy();out[400:500]=e;np.save(args.out/f'{variant}.npy',out)
        assert result['canonical_repeat']['cosine_min']>=.9999
        dump('summary.json',{'encoding_controls':result,'canonical_parity_pass':True,
            'wall_seconds':time.monotonic()-start,'cloud_calls':0,'scientific_increment':0})
        print(json.dumps({v:{k:value for k,value in r.items() if k!='cosines'} for v,r in result.items()}),flush=True)
        return

    encodings={v:np.load(args.arrays/f'{v}.npy').astype(np.float32) for v in variants}
    assert json.loads((args.arrays/'summary.json').read_text())['canonical_parity_pass']
    if args.mode=='public':
        folders={f'{mode}_seed{seed}':args.source/f'research/results/pcsp_v3_large/{mode}_seed{seed}/{mode}'
            for seed in [42,43,44] for mode in ['full','no_consist']}
    else:
        folders={route:Path(str(args.baseline_prefix)+route) for route in ['no','full']}
        a=torch.load(Path(str(args.baseline_prefix)+'no')/'policy.pt',map_location='cpu',weights_only=True)
        b=torch.load(Path(str(args.baseline_prefix)+'readout')/'policy.pt',map_location='cpu',weights_only=True)
        assert all(torch.equal(a[k],b[k]) for k in a)
    dump('manifest.json',{'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf','mode':args.mode,
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'world_seeds':[26011,26012,26013],
        'test_ids':[r['id'] for r in records],'variants':variants,'all_16_codes_changed':True,
        'world_or_reward_changed':False,'cloud_calls':0})
    def rollout(policy,rows,seed,variant):
        actual=len(rows);padded=list(rows)
        while len(padded)<N_AGENTS:padded.append(rows[len(padded)%actual])
        env=MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(r) for r in padded],max_steps=200)
        env.reset(seed=seed);torch.manual_seed(seed+1000003)
        initial=np.concatenate([env.positions.flatten(),env.needs.flatten()]).copy()
        e=torch.from_numpy(encodings[variant][[int(r['id'])-1 for r in padded]])
        actions=[];reward=np.zeros(N_AGENTS);prefs=np.zeros(N_AGENTS);critical=np.zeros(N_AGENTS)
        for cycle in range(200):
            obs=np.stack([env.observe(a) for a in env.possible_agents])
            with torch.inference_mode():selected=torch.distributions.Categorical(logits=policy.action_logits(torch.from_numpy(obs),e)).sample().numpy()
            actions.append(selected.copy())
            for i,(agent,action) in enumerate(zip(env.possible_agents,selected)):
                assert env.agent_selection==agent
                env.step(int(action));reward[i]+=float(env.rewards[agent]);prefs[i]+=int(int(action) in padded[i]['preferred_actions'])
            critical+=(env.needs<.2).mean(-1)
        out={'actions':np.stack(actions).T[:actual],'rewards':reward[:actual],
            'preferred_rate':prefs[:actual]/200,'critical_fraction':critical[:actual]/200,
            'final_needs':env.needs[:actual].copy(),'final_positions':env.positions[:actual].copy(),'initial':initial}
        env.close();return out
    summary={}
    for label,folder in folders.items():
        policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
        policy.load_state_dict(torch.load(folder/'policy.pt',map_location='cpu',weights_only=True),strict=True)
        policy.eval().requires_grad_(False)
        if not summary:
            one=rollout(policy,records[:N_AGENTS],26011,'canonical');two=rollout(policy,records[:N_AGENTS],26011,'canonical')
            assert all(np.array_equal(one[k],two[k]) for k in one)
            dump('native_gate.json',{'complete_native_replay_byte_identical':True,'seconds':time.monotonic()-start})
        collected={v:[] for v in variants};ids=[];worlds=[]
        for seed in [26011,26012,26013]:
            shuffled=[records[int(i)] for i in np.random.default_rng(seed).permutation(len(records))]
            for offset in range(0,len(shuffled),N_AGENTS):
                rows=shuffled[offset:offset+N_AGENTS];initial=None
                for variant in variants:
                    data=rollout(policy,rows,seed+offset*100,variant)
                    if initial is None:initial=data['initial']
                    assert np.array_equal(data.pop('initial'),initial)
                    collected[variant].append(data)
                ids.extend(r['id'] for r in rows);worlds.extend([seed]*len(rows))
        table={v:{k:np.concatenate([part[k] for part in parts]) for k in parts[0]} for v,parts in collected.items()}
        result={}
        for variant,data in table.items():
            data.update(ids=np.asarray(ids),world_seeds=np.asarray(worlds));np.savez_compressed(args.out/f'{label}_{variant}.npz',**data)
            delta=data['rewards']-table['canonical']['rewards']
            per_id=np.asarray([delta[data['ids']==pid].mean() for pid in sorted(set(ids))])
            rng=np.random.default_rng(262626)
            boot=[rng.choice(per_id,len(per_id),replace=True).mean() for _ in range(2000)]
            result[variant]={'native_reward':float(data['rewards'].mean()),'paired_reward_delta':float(delta.mean()),
                'paired_persona_cluster95':np.quantile(boot,[.025,.975]).tolist(),
                'preferred_action_rate':float(data['preferred_rate'].mean()),'critical_need_fraction':float(data['critical_fraction'].mean())}
        summary[label]={'policy_sha256':hashlib.sha256((folder/'policy.pt').read_bytes()).hexdigest(),'variants':result}
        dump('summary.json',{'policies':summary,'scientific_increment':0,'cloud_calls':0})
        print(json.dumps({'policy':label,'variants':result,'seconds':time.monotonic()-start}),flush=True)
    dump('runtime.json',{'seconds':time.monotonic()-start,'gpu_hours':0,'cloud_calls':0})


if __name__=='__main__':main()
