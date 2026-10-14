#!/usr/bin/env python3
"""E21 speech/action opportunity control, all original LIGHT physical events."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

from light_resource_episodes import load_pairs
from light_npc_episodes import (CACHE, ViewerHost, actor_for, execute, observation,
    legal_commands, system_message, choose, chosen_command, material_state)
from light_native_gate import load_event_modules, parse_event
from native_actioncastle import dump


def run(pair, seed, first, modules, folder, client=None):
    OOGraph, events, ErrorEvent = modules
    graph = OOGraph.from_json(pair['quests'][0]['graph'])
    host = ViewerHost(graph)
    actors = [actor_for(graph,q['character']) for q in pair['quests']]
    item = graph.get_node(pair['item_node_id'])
    histories, turns, goal_done = [[], []], [], [False, False]
    random.seed(seed)

    def context(index):
        return (observation(host,actors[index],events,ErrorEvent)+
            '\nYour authored goal event previously executed: '+str(goal_done[index])+
            '\nRecent visible interaction:\n'+'\n'.join(histories[index][-12:]))

    def execute_record(index, command, phase, extra):
        actor = actors[index]
        expected = parse_event(graph,actor,pair['quests'][index]['goal'],events,ErrorEvent)
        selected = parse_event(graph,actor,command,events,ErrorEvent)
        match = (not isinstance(expected,ErrorEvent) and type(expected)==type(selected)
            and [x.node_id for x in expected.target_nodes]==[x.node_id for x in selected.target_nodes])
        native = execute(host,actor,command,events,ErrorEvent)
        if match and native.get('executed') and not native.get('stochastic_failure'):
            goal_done[index] = True
        for recipient, receiver in enumerate(actors):
            histories[recipient].extend(m['text'] for m in native['messages'] if m['viewer']==receiver.node_id)
        histories[index].append('Your chosen '+phase+': '+command)
        if not native['legal']:
            histories[index].append(native['error'])
        if phase=='speech':
            assert not native['material_changed'], 'Native speech unexpectedly changed physical state'
        turns.append({'actor_index':index,'phase':phase,'native':native,'goal_event_match':match,
            'goals_executed':goal_done.copy(),'item_container':item.get_container().node_id,**extra})

    expressions = [None,None]
    if client:
        for index,quest in enumerate(pair['quests']):
            client.seed = seed+90_000+index-len(client.calls)
            expressions[index] = client.chat([{'role':'system','content':system_message(quest)},
                {'role':'user','content':'Introduce yourself in two sentences, describing your values and motivations.'}],
                max_tokens=128,kind='expression_shadow')
    for round_index in range(6):
        if item.get_container().node_id=='VOID' or any(a.get_prop('dead') for a in actors):
            break
        for index in [first,1-first]:
            ctx = context(index)
            messages = [{'role':'system','content':system_message(pair['quests'][index])},
                {'role':'user','content':ctx+'\nYou may now speak one brief sentence to the other character before the physical action phase.'}]
            if client:
                client.seed = seed+index*10_000+round_index*100+31-len(client.calls)
                speech = client.native_tool(messages,{'name':'speak','parameters':{'type':'object',
                    'properties':{'utterance':{'type':'string','minLength':1,'maxLength':400}},
                    'required':['utterance'],'additionalProperties':False}})
                if speech is None:
                    raise RuntimeError('Invalid speech JSON; no fallback')
            else:
                speech = {'utterance':'CPU event qualification.'}
            execute_record(index,'say '+speech['utterance'],'speech',{'round':round_index,'context':ctx,'speech':speech})
        for index in [first,1-first]:
            if item.get_container().node_id=='VOID' or any(a.get_prop('dead') for a in actors):
                break
            actor = actors[index]
            # Native physical actions are kept verbatim. Only the separately
            # provided speech events are removed from this phase's candidates.
            menu = [c for c in legal_commands(graph,actor) if c.split(' ',1)[0] not in ['say','tell','whisper','shout']]
            ctx = context(index)+'\nDialogue has already been exchanged this round. Choose one remaining native action.\nLegal commands:\n'+'\n'.join(menu)
            messages = [{'role':'system','content':system_message(pair['quests'][index])}, {'role':'user','content':ctx}]
            intention = None
            if client:
                draw = seed+index*10_000+round_index*100
                if round_index==0:
                    intention = choose(client,[messages[0],{'role':'user','content':ctx+
                        '\nIn an independent hypothetical check, which next action do you currently intend?'}],menu,draw+5,allow_speech=False)
                choice = choose(client,messages,menu,draw+17,allow_speech=False)
                if choice is None:
                    raise RuntimeError('Invalid action JSON; no fallback')
                if choice['action']=='say':
                    raise RuntimeError('Speech selected outside physical-phase schema')
                command = chosen_command(choice)
            else:
                command = pair['quests'][index]['goal']
                expected = parse_event(graph,actor,command,events,ErrorEvent)
                if isinstance(expected,ErrorEvent):
                    command = 'get '+item.name if item.get_container().room else 'wait'
                choice = {'action':command,'utterance':'','reasoning':'CPU only'}
            execute_record(index,command,'physical',{'round':round_index,'context':ctx,'menu':menu,
                'choice':choice,'intention_shadow':intention})
    summary = {'files':pair['files'],'seed':seed,'first_actor_index':first,
        'characters':[a.name for a in actors],'initial_owner':pair['initial_owner'],
        'final_item_container':item.get_container().node_id,'goals_executed':goal_done,
        'physical_actions':sum(t['phase']=='physical' for t in turns),
        'physical_legal':sum(t['phase']=='physical' and t['native']['legal'] for t in turns),
        'speech_events':sum(t['phase']=='speech' for t in turns),
        'speech_legal':sum(t['phase']=='speech' and t['native']['legal'] for t in turns),
        'consumer_index':next((t['actor_index'] for t in turns if t['goal_event_match']
            and t['native'].get('executed') and not t['native'].get('stochastic_failure')),None),
        'expression_shadow':expressions}
    dump(folder/'episode.json',turns)
    dump(folder/'summary.json',summary)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['cpu','model'],required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--model',type=Path)
    ap.add_argument('--seeds',nargs='+',type=int,default=[2001])
    args = ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    pairs = load_pairs();modules = load_event_modules(CACHE/'sources/LIGHT')
    dump(args.out/'manifest.json',{'source_sha':'71a06cae8573048b1af41507ac52fe33b650fab3',
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'files':[p['files'] for p in pairs],'seeds':args.seeds,'model':str(args.model),
        'schedule':'two native speeches then two physical choices; not original Dragon RL model',
        'cloud_calls':0})
    client = None
    if args.mode=='model':
        from strong_native_baseline import ModelClient
        os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
        client = ModelClient(args.model,2001,args.out/'unused.jsonl')
    start = time.monotonic();summaries = []
    for seed in args.seeds:
        for pair in pairs:
            for first in [0,1]:
                folder = args.out/f"p{pair['files'][0].split('.')[0]}_s{seed}_first{first}";folder.mkdir()
                if client:
                    client.calls,client.trace_file = [],folder/'model_calls.jsonl'
                row = run(pair,seed,first,modules,folder,client)
                if client:
                    row.update(model_calls=len(client.calls),prompt_tokens=sum(c['prompt_tokens'] for c in client.calls),
                        completion_tokens=sum(c['completion_tokens'] for c in client.calls))
                summaries.append(row);dump(args.out/'summary.json',summaries)
                print(json.dumps({k:v for k,v in row.items() if k!='expression_shadow'}),flush=True)
    dump(args.out/'runtime.json',{'wall_seconds':time.monotonic()-start,'cloud_calls':0})


if __name__=='__main__':
    main()
