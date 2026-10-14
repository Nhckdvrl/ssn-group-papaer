"""E42 source LLM-as-policy paradigm, strong local models, native v3 loop.

Only observation/menu adaptation changes the v1 B5 interface. Original world
rules and both author-defined C utility functions stay unchanged. All parser
fallbacks are explicit. Batching is across independent worlds, never actors
whose observations depend on a previous actor's unexecuted action.
"""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import sys
import time


BASE_IDS=[401,421,441,461,481]
PEER_IDS=[402,409,416,422,429,436,442,449,456,462,469,476,482,489,496]
WORLD_SEEDS=[33011,33012,33013]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--model',type=Path)
    ap.add_argument('--prompt-mode',choices=['persona','preference_cue'],default='persona')
    ap.add_argument('--peer-route',choices=['no_consist','full'],default='no_consist')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--pilot',action='store_true')
    ap.add_argument('--cpu-control',action='store_true')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig,NEED_NAMES
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv
    from src.env.v3_constants import ACTION_NAMES_V3,ACTION_RESTORE_V3,OBS_DIM_V3_LARGE,N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    torch.set_num_threads(1);start=time.monotonic()
    records=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    lookup={int(r['id']):r for r in records}
    tree=ast.parse((args.source/'research/scripts/generate_personas_500.py').read_text())
    desc=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='_BF_DESC' for t in n.targets))
    def changed(pid,level):
        r=copy.deepcopy(lookup[pid]);r['big_five']['C']=level
        r['text']=f"{r['age']}세 {r['occupation']}. "+', '.join(desc[f'{k}_{v}'] for k,v in r['big_five'].items())+'.'
        return r
    def parity(envs):
        for key in ['positions','needs','last_actions','repeat_counts','novelty_steps']:
            assert np.array_equal(getattr(envs[0],key),getattr(envs[1],key)),key
        assert envs[0].agent_selection==envs[1].agent_selection
    def observation_fields(obs):
        fields={'self_position_normalized':obs[:2].tolist(),'time_normalized':float(obs[2]),
                'own_needs':dict(zip(NEED_NAMES,map(float,obs[3:11]))),
                'nearest_world_object_one_hot':obs[11:19].tolist(),
                'nearby_fraction':float(obs[19]),'previous_was_social':float(obs[20]),
                'previous_was_respond':float(obs[21]),'repeat_fraction':float(obs[22]),
                'novelty_fraction':float(obs[23]),
                'other_positions_previous_actions_normalized':obs[24:].reshape(15,3).tolist()}
        restored=np.asarray(fields['self_position_normalized']+[fields['time_normalized']]
              +list(fields['own_needs'].values())+fields['nearest_world_object_one_hot']
              +[fields[k] for k in ['nearby_fraction','previous_was_social','previous_was_respond','repeat_fraction','novelty_fraction']]
              +[x for row in fields['other_positions_previous_actions_normalized'] for x in row],dtype=np.float32)
        assert np.array_equal(restored,obs)
        return fields
    menu='\n'.join(f'{i}: {name}; restores '+', '.join(f'{NEED_NAMES[n]} by {v:g}' for n,v in ACTION_RESTORE_V3.get(i,[]))
                    for i,name in enumerate(ACTION_NAMES_V3))
    system=('You are controlling an NPC in a life simulation game. Choose the single best action number (0-19) '
            'for its persona and current needs. Output only the action number and nothing else. All listed actions '
            'are legal; need restoration applies anywhere. Need levels range from 0 to 1, with levels below 0.2 critical. '
            'Time is normalized by 23; positions by 11; previous action numbers by 19.\nActions:\n'+menu)
    cases=[]
    for pid in BASE_IDS[:1] if (args.pilot or args.cpu_control) else BASE_IDS:
        for world in WORLD_SEEDS[:1] if (args.pilot or args.cpu_control) else WORLD_SEEDS:
            for level in ['high'] if args.pilot else ['high','low']:
                envs=[MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(changed(pid,g))]
                        +[PersonaConfig.from_dict(lookup[i]) for i in PEER_IDS],max_steps=200) for g in ['high','low']]
                for e in envs:e.reset(seed=world)
                parity(envs);assert np.array_equal(envs[0].observe('agent_0'),envs[1].observe('agent_0'))
                cases.append({'id':pid,'world_seed':world,'input_C':level,'persona':changed(pid,level),
                    'envs':envs,'uniforms':np.random.default_rng(world+1000003).random((200,16)),
                    'fallback_rng':np.random.default_rng(world+pid+420000),
                    'obs':[],'actions':[],'rewards':[],'needs':[],'positions':[],'calls':[]})
    peer_path=args.runs/f'e34_cpu_s42_{args.peer_route}/checkpoint_0300/policy.pt'
    policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
    policy.load_state_dict(torch.load(peer_path,map_location='cpu',weights_only=True));policy.eval().requires_grad_(False)
    codes=np.load(args.runs/'e23_embedding_context/proper_pool.npy').astype(np.float32)
    peer_codes=torch.from_numpy(codes[np.asarray(PEER_IDS)-1])
    manifest={'host':socket.gethostname(),'visible_gpu':os.environ.get('CUDA_VISIBLE_DEVICES'),
              'model':str(args.model),'prompt_mode':args.prompt_mode,'peer_route':args.peer_route,
              'peer_policy_sha256':hashlib.sha256(peer_path.read_bytes()).hexdigest(),
              'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
              'world_seeds':WORLD_SEEDS,'base_ids':BASE_IDS,'peer_ids':PEER_IDS,
              'world_or_reward_modified':False,'cloud_calls':0,'greedy':True,'nonthinking':True,
              'adaptation':'Original B5 v1 paradigm adapted explicitly to source v3 69 observations/20 actions; not exact 1.7B reproduction.',
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'system_prompt':system,'physical_goal_worlds':'high/low C utility worlds forced to identical actual action tape; native private-goal evaluation scope.'}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    load_seconds=0
    if not args.cpu_control:
        assert args.model is not None
        from vllm import LLM,SamplingParams
        before=time.monotonic()
        engine=LLM(model=str(args.model),tensor_parallel_size=1,dtype='bfloat16',
                   gpu_memory_utilization=.82,max_model_len=8192,enforce_eager=True,
                   enable_prefix_caching=True,seed=42001,language_model_only=True)
        tokenizer=engine.get_tokenizer();load_seconds=time.monotonic()-before
    total_calls=0;fallbacks=0;repeat_control=None
    cycles=2 if args.cpu_control else 200
    for cycle in range(cycles):
        prompts=[];messages_batch=[]
        for case in cases:
            parity(case['envs']);obs=case['envs'][0].observe('agent_0').copy()
            case['obs'].append(obs);view=observation_fields(obs)
            message='Persona: '+case['persona']['text']+'\nGame observation: '+json.dumps(view,ensure_ascii=False)
            if args.prompt_mode=='preference_cue':
                preferred=', '.join(ACTION_NAMES_V3[a] for a in case['persona']['preferred_actions'])
                message+='\nThis NPC\'s authored preferred actions are '+preferred+'; consider them together with current needs, persona and situation.'
            message+='\nChoose action (0-19): /no_think'
            messages=[{'role':'system','content':system},{'role':'user','content':message}]
            messages_batch.append(messages)
            if not args.cpu_control:
                prompts.append(tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False))
        batch_start=time.monotonic()
        if args.cpu_control:
            outputs=['0']*len(cases);token_counts=[(0,0)]*len(cases)
        else:
            request=prompts+([prompts[0]] if cycle==0 else [])
            out=engine.generate(request,SamplingParams(max_tokens=8,temperature=0.,seed=42001+cycle),use_tqdm=False)
            if cycle==0:
                repeat_control=out[0].outputs[0].text==out[-1].outputs[0].text
            outputs=[o.outputs[0].text for o in out[:len(cases)]]
            token_counts=[(len(o.prompt_token_ids),len(o.outputs[0].token_ids)) for o in out[:len(cases)]]
        batch_seconds=time.monotonic()-batch_start
        for ci,(case,response) in enumerate(zip(cases,outputs)):
            parsed=None
            for token in response.split():
                try:
                    number=int(token)
                    if 0<=number<20:parsed=number;break
                except ValueError:pass
            fallback=parsed is None
            action=int(case['fallback_rng'].integers(20)) if fallback else parsed
            fallback_count=int(fallback);fallbacks+=fallback_count;total_calls+=int(not args.cpu_control)
            row={'cycle':cycle,'id':case['id'],'world_seed':case['world_seed'],'input_C':case['input_C'],
                 'messages':messages_batch[ci],'response':response,'parsed_action':parsed,
                 'executed_action':action,'random_fallback':fallback,
                 'prompt_tokens':token_counts[ci][0],'completion_tokens':token_counts[ci][1],
                 'batch_seconds':batch_seconds,'batch_size':len(cases),'batch_id':cycle}
            with (args.out/'model_calls.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
            case['calls'].append(row);action_tape=[];reward_pair=[]
            for index,agent in enumerate(case['envs'][0].possible_agents):
                if index:
                    fresh=case['envs'][0].observe(agent)
                    with torch.inference_mode():
                        p=policy.action_logits(torch.from_numpy(fresh).unsqueeze(0),peer_codes[index-1:index]).softmax(-1).numpy()[0]
                    action=min(int(np.searchsorted(np.cumsum(p),case['uniforms'][cycle,index],side='right')),19)
                action_tape.append(action)
                rr=[]
                for e in case['envs']:
                    assert e.agent_selection==agent;e.step(action);rr.append(float(e.rewards[agent]))
                if index==0:reward_pair=rr
            parity(case['envs']);case['actions'].append(action_tape);case['rewards'].append(reward_pair)
            case['needs'].append(case['envs'][0].needs.copy());case['positions'].append(case['envs'][0].positions.copy())
        if cycle%20==0:print(json.dumps({'cycle':cycle,'episodes':len(cases),'calls':total_calls,'fallbacks':fallbacks,'seconds':time.monotonic()-start}),flush=True)
    episodes=[]
    for case in cases:
        q=args.out/f"p{case['id']}_{case['input_C']}_w{case['world_seed']}";q.mkdir()
        r=np.asarray(case['rewards']);a=np.asarray(case['actions'])
        np.savez_compressed(q/'native.npz',obs=np.asarray(case['obs']),actions=a,rewards=r,
                            needs=np.asarray(case['needs']),positions=np.asarray(case['positions']))
        row={'id':case['id'],'world_seed':case['world_seed'],'input_C':case['input_C'],
             'cycles':cycles,'J_high':float(r[:,0].sum()),'J_low':float(r[:,1].sum()),
             'physical_parity':True,'action_counts':np.bincount(a[:,0],minlength=20).tolist(),
             'random_fallbacks':sum(c['random_fallback'] for c in case['calls']),'raw':str(q)}
        episodes.append(row)
        for e in case['envs']:e.close()
    result={'manifest':manifest,'episodes':episodes,'episode_count':len(episodes),
            'calls':total_calls,'random_fallbacks':fallbacks,'load_seconds':load_seconds,
            'wall_seconds':time.monotonic()-start,'greedy_duplicate_response_equal':repeat_control,
            'observation_roundtrip_byte_equal':True,'cloud_calls':0,'cpu_control':args.cpu_control,
            'scope':'Native strong LLM reference; authored preferred-action cue is ordinary information recovery, not a novelty claim.'}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['manifest','episodes']}),flush=True)


if __name__=='__main__':main()
