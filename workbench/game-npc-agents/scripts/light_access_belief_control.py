#!/usr/bin/env python3
"""E22 two native snapshots, independent legality forecasts and action forks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

from light_resource_episodes import load_pairs
from light_npc_episodes import (CACHE, ViewerHost, actor_for, execute, observation,
    legal_commands, system_message, chosen_command, material_state)
from light_native_gate import load_event_modules, parse_event
from native_actioncastle import dump

CONDITIONS = ['no_dialog','partner_only','all_dialog','all_dialog_fact','all_dialog_binding']
CASES = [('p14908_s2001_first1','14908.json',0),('p14207_s2001_first0','14207.json',0)]


def build_snapshots(modules):
    OOGraph, events, ErrorEvent = modules
    pairs = {p['files'][0]:p for p in load_pairs()}
    snapshots = []
    for folder_name, filename, target_index in CASES:
        pair = pairs[filename]
        path = CACHE/'runs/e21_qwen35_gate'/folder_name/'episode.json'
        turns = json.loads(path.read_text())
        graph = OOGraph.from_json(pair['quests'][0]['graph'])
        host = ViewerHost(graph)
        actors = [actor_for(graph,q['character']) for q in pair['quests']]
        actor = actors[target_index]
        history = {name:[] for name in ['no_dialog','partner_only','all_dialog']}
        random.seed(2001)
        for row in turns:
            if row['phase']=='physical' and row['actor_index']==target_index:
                assert material_state(graph)==row['native']['before'], 'Native snapshot replay mismatch'
                break
            # WorldViewer maintains viewing state even though Look/Inventory
            # leave the material graph unchanged. Replay these original reads.
            observation(host,actors[row['actor_index']],events,ErrorEvent)
            replay = execute(host,actors[row['actor_index']],row['native']['command'],events,ErrorEvent)
            assert replay['after']==row['native']['after'], 'Native event replay mismatch'
            for condition in history:
                if row['phase']=='speech' and (condition=='no_dialog' or
                    (condition=='partner_only' and row['actor_index']==target_index)):
                    continue
                history[condition].extend(m['text'] for m in replay['messages'] if m['viewer']==actor.node_id)
                if row['actor_index']==target_index:
                    history[condition].append('Your chosen '+row['phase']+': '+row['native']['command'])
                    if not replay['legal']:
                        history[condition].append(replay['error'])
        else:
            raise AssertionError('Missing target decision')
        fresh_obs = observation(host,actor,events,ErrorEvent)
        # Upstream viewer iterates sets: Python hash randomization changes
        # object/inventory presentation order across processes. Reuse the exact
        # cached native view only after checking its contents and physical state.
        obs = row['context'].split('\nYour authored goal event previously executed:',1)[0]
        def normalized_view(value):
            lines=[]
            for line in value.splitlines():
                if line.startswith("There's ") or line.startswith('You are carrying '):
                    prefix="There's " if line.startswith("There's ") else 'You are carrying '
                    body=line[len(prefix):].removesuffix(' here.').removesuffix('.')
                    lines.append(prefix+','.join(sorted(x.strip() for x in body.replace(', and ', ', ').replace(' and ', ', ').split(','))))
                else:lines.append(line)
            return '\n'.join(lines)
        assert normalized_view(fresh_obs)==normalized_view(obs), 'Cached native view contents mismatch'
        menu = [c for c in legal_commands(graph,actor) if c.split(' ',1)[0] not in ['say','tell','whisper','shout']]
        contexts = {}
        for condition, records in history.items():
            contexts[condition] = (obs+'\nYour authored goal event previously executed: False'+
                '\nRecent visible interaction:\n'+'\n'.join(records[-12:])+
                '\nDialogue has already been exchanged this round. Choose one remaining native action.\nLegal commands:\n'+'\n'.join(menu))
        if contexts['all_dialog']!=row['context']:
            import difflib
            delta='\n'.join(difflib.unified_diff(row['context'].splitlines(),contexts['all_dialog'].splitlines()))
            raise AssertionError('Original prompt replay mismatch:\n'+delta)
        bird = filename=='14908.json'
        if bird:
            fields = ['fox_get_current_held_worm_legal','fox_get_after_put_on_nests_legal','put_blocks_fox_direct_get']
            question = ('Predict the original game engine legality, not moral rights or whether the fox will choose to act. '
                'Is "get worm from bird" legal for the fox now? If the bird successfully executes '
                '"put worm on nests", is "get worm from nests" legal for the fox next? '
                'Does putting the worm on nests block the fox from a direct get?')
            fact = ('In this original game, the worm is currently held by the bird; putting it on the shared nests '
                'makes "get worm from nests" legal for the fox without stealing, so that placement does not make it private.')
            binding = 'Original authored goals: your short goal is to eat the worm; your mid motivation is to feed your young with the nut.'
            fox = actors[1]
            current = parse_event(graph,fox,'get worm from bird',events,ErrorEvent)
            fork = OOGraph.from_json(graph.to_json());bird_fork=actor_for(fork,pair['quests'][0]['character'])
            placed = execute(ViewerHost(fork),bird_fork,'put worm on nests',events,ErrorEvent)
            assert placed['legal'] and placed['material_changed']
            after = parse_event(fork,actor_for(fork,pair['quests'][1]['character']),'get worm from nests',events,ErrorEvent)
            truth = {fields[0]:not isinstance(current,ErrorEvent),fields[1]:not isinstance(after,ErrorEvent),fields[2]:isinstance(after,ErrorEvent)}
            assert truth==dict(zip(fields,[False,True,False]))
        else:
            fields = ['creature_get_algae_now_legal','eel_get_algae_now_legal','say_ownership_changes_get_legality']
            question = ('Predict the original game engine legality, not moral rights, intimidation or who will choose to act. '
                'Is "get algae" legal for the creature now? Is the same "get algae" legal for the electric eel now? '
                'Does merely saying that the algae is yours change either character\'s mechanical get legality?')
            fact = 'The algae is still in the shared room; both characters can legally get it, and saying it is yours creates no mechanical block.'
            binding = 'Your original authored goal is eat algae; your mid motivation says you cannot find flies and need to eat to avoid starvation.'
            legal = [not isinstance(parse_event(graph,a,'get algae',events,ErrorEvent),ErrorEvent) for a in actors]
            before = material_state(graph)
            spoke = execute(host,actors[1],'say The algae is mine.',events,ErrorEvent)
            assert spoke['legal'] and material_state(graph)==before
            truth = dict(zip(fields,legal+[False]))
            assert truth==dict(zip(fields,[True,True,False]))
        contexts['all_dialog_fact'] = contexts['all_dialog']+'\n'+fact
        contexts['all_dialog_binding'] = contexts['all_dialog']+'\n'+binding
        source_calls=[json.loads(line) for line in (path.parent/'model_calls.jsonl').read_text().splitlines()]
        source_action=next(c for c in source_calls if c.get('parsed')==row['choice'] and
            c['messages'][-1]['content']==row['context'])
        snapshots.append({'name':folder_name,'quest':pair['quests'][target_index],'actor_id':actor.node_id,
            'graph':graph.to_json(),'before':material_state(graph),'menu':menu,'contexts':contexts,
            'fields':fields,'question':question,'truth':truth,'discovery_action':row['native']['command'],
            'fresh_view_order_equal':fresh_obs==obs,'cached_native_view_reused':True,
            'original_action_schema':source_action['schema'],
            'original_action_prompt_sha256':source_action['prompt_sha256']})
    return snapshots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['cpu','model'],required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--model',type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    modules=load_event_modules(CACHE/'sources/LIGHT')
    snapshots=build_snapshots(modules)
    dump(args.out/'snapshots.json',snapshots)
    dump(args.out/'manifest.json',{'source_sha':'71a06cae8573048b1af41507ac52fe33b650fab3',
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model':str(args.model),
        'draws':32,'conditions':CONDITIONS,'discovery_scope':True,'cloud_calls':0})
    if args.mode=='cpu':
        dump(args.out/'summary.json',{'snapshots':2,'material_replay_exact':True,'prompt_replay_exact':True,
            'truth':{s['name']:s['truth'] for s in snapshots},'model_calls':0,'gpu_hours':0})
        print('Two original native states/prompts replayed exactly; access controls passed.',flush=True)
        return
    from strong_native_baseline import ModelClient
    from vllm import SamplingParams
    from vllm.sampling_params import StructuredOutputsParams
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    client=ModelClient(args.model,220001,args.out/'unused.jsonl')
    jobs=[]
    for index,snap in enumerate(snapshots):
        action_schema=snap['original_action_schema']
        assert action_schema['properties']['action']['enum']==snap['menu']
        forecast_schema={'type':'object','properties':{k:{'type':'boolean'} for k in snap['fields']},
            'required':snap['fields'],'additionalProperties':False}
        for condition_index,condition in enumerate(CONDITIONS+['neutral_forecast']):
            for branch in (['forecast'] if condition=='neutral_forecast' else ['action','forecast']):
                schema=action_schema if branch=='action' else forecast_schema
                header=system_message(snap['quest']) if condition!='neutral_forecast' else (
                    'You are an independent auditor of the LIGHT game engine. Predict mechanical Can, not moral entitlement or likely Will.')
                ctx=snap['contexts'].get(condition,snap['contexts']['all_dialog'])
                if branch=='forecast':ctx+='\nIndependent hypothetical engine check: '+snap['question']
                if branch=='action':
                    header+=('\nChoose one game action using the choose_action tool. Return only its JSON arguments; '
                        'reasoning must be one short sentence. Schema: '+json.dumps(schema))
                else:
                    header+='\nReturn only JSON matching this schema: '+json.dumps(schema)+'. Any reasoning must be one short sentence.'
                prompt=client.tokenizer.apply_chat_template([{'role':'system','content':header},
                    {'role':'user','content':ctx}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                if condition=='all_dialog' and branch=='action':
                    assert hashlib.sha256(prompt.encode()).hexdigest()==snap['original_action_prompt_sha256']
                for draw in range(32):
                    seed=220000+index*10000+condition_index*100+draw
                    jobs.append({'snapshot':index,'condition':condition,'branch':branch,'draw':draw,'seed':seed,
                        'schema':schema,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()})
    assert len(jobs)==704
    start=time.monotonic();records=[]
    OOGraph,events,ErrorEvent=modules
    for offset in range(0,len(jobs),16):
        batch=jobs[offset:offset+16]
        outputs=client.llm.generate([j['prompt'] for j in batch],[SamplingParams(temperature=.7,
            max_tokens=128,seed=j['seed'],structured_outputs=StructuredOutputsParams(json=j['schema'])) for j in batch],use_tqdm=False)
        for job,out in zip(batch,outputs):
            raw=out.outputs[0].text
            try: parsed=json.loads(raw);error=None
            except Exception as exc:parsed=None;error=f'{type(exc).__name__}: {exc}'
            record={k:v for k,v in job.items() if k not in ['prompt','schema']}
            record.update(response=raw,parsed=parsed,error=error,prompt_tokens=len(out.prompt_token_ids),
                completion_tokens=len(out.outputs[0].token_ids),finish_reason=out.outputs[0].finish_reason)
            snap=snapshots[job['snapshot']]
            if parsed is not None and job['branch']=='forecast':
                record['correct_fields']={k:parsed[k]==v for k,v in snap['truth'].items()}
                record['all_correct']=all(record['correct_fields'].values())
            if parsed is not None and job['branch']=='action':
                graph=OOGraph.from_json(snap['graph']);assert material_state(graph)==snap['before']
                random.seed(job['seed'])
                native=execute(ViewerHost(graph),graph.get_node(snap['actor_id']),chosen_command(parsed),events,ErrorEvent)
                record['native']=native
            records.append(record)
            with (args.out/'calls.jsonl').open('a') as trace:trace.write(json.dumps(record,ensure_ascii=False)+'\n')
        print(json.dumps({'completed':len(records),'total':len(jobs)}),flush=True)
    summary={}
    for index,snap in enumerate(snapshots):
        result={}
        for condition in CONDITIONS+['neutral_forecast']:
            actions=[r for r in records if r['snapshot']==index and r['condition']==condition and r['branch']=='action']
            forecasts=[r for r in records if r['snapshot']==index and r['condition']==condition and r['branch']=='forecast']
            from collections import Counter
            result[condition]={'forecast_all_correct':sum(r.get('all_correct',False) for r in forecasts)/len(forecasts),
                'forecast_field_accuracy':{k:sum(r.get('correct_fields',{}).get(k,False) for r in forecasts)/len(forecasts) for k in snap['fields']},
                'actions':dict(Counter(r['parsed']['action'] if r['parsed'] else 'JSON_ERROR' for r in actions)),
                'native_legal':sum(r.get('native',{}).get('legal',False) for r in actions),'action_draws':len(actions)}
        summary[snap['name']]={'truth':snap['truth'],'discovery_action':snap['discovery_action'],'conditions':result}
    dump(args.out/'summary.json',summary)
    dump(args.out/'runtime.json',{'wall_seconds':time.monotonic()-start,'calls':len(records),
        'parse_errors':sum(r['error'] is not None for r in records),'cloud_calls':0,'scientific_increment':0,
        'prompt_tokens':sum(r['prompt_tokens'] for r in records),'completion_tokens':sum(r['completion_tokens'] for r in records)})
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()
