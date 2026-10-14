#!/usr/bin/env python3
"""E20: independently authored opposing goals, unchanged native LIGHT graph."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import tarfile
import time

from light_npc_episodes import (CACHE, ViewerHost, actor_for, execute, observation,
    legal_commands, system_message, choose, chosen_command, material_state)
from light_native_gate import load_event_modules, parse_event
from native_actioncastle import dump


def load_pairs():
    rows = json.loads((Path(__file__).parents[1]/'results/E16_resource_qualification.json').read_text())['cases']
    rows = [r for r in rows if r['qualified']]
    needed = {f for r in rows for f in r['files']}
    quests = {}
    with tarfile.open(CACHE/'quest_stems.tar.gz', 'r|gz') as archive:
        for member in archive:
            name = member.name.split('/')[-1]
            if name in needed:
                quests[name] = json.load(archive.extractfile(member))['data']
    for row in rows:
        row['quests'] = [quests[f] for f in row['files']]
        assert row['quests'][0]['graph'] == row['quests'][1]['graph']
    return rows


def run(pair, seed, first, modules, out, client=None, cpu=False):
    OOGraph, events, ErrorEvent = modules
    graph = OOGraph.from_json(pair['quests'][0]['graph'])
    host = ViewerHost(graph)
    actors = [actor_for(graph, q['character']) for q in pair['quests']]
    item = graph.get_node(pair['item_node_id'])
    assert item.get_container().node_id == pair['initial_owner']
    histories = [[], []]
    complete = [False, False]
    expressions = [None, None]
    turns = []
    random.seed(seed)
    if client:
        for index, quest in enumerate(pair['quests']):
            client.seed = seed+90_000+index-len(client.calls)
            expressions[index] = client.chat([{'role': 'system', 'content':system_message(quest)},
                {'role':'user','content':'Introduce yourself in two sentences, describing your values and motivations.'}],
                max_tokens=128, kind='expression_shadow')
    for step in range(12):
        index = (first+step)%2
        actor, quest = actors[index], pair['quests'][index]
        if any(a.get_prop('dead') for a in actors) or item.get_container().node_id == 'VOID':
            break
        obs = observation(host, actor, events, ErrorEvent)
        menu = legal_commands(graph, actor)
        context = obs+'\nYour authored goal event previously executed: '+str(complete[index])
        context += '\nRecent visible interaction:\n'+'\n'.join(histories[index][-12:])
        context += '\nLegal commands:\n'+'\n'.join(menu)
        messages = [{'role':'system','content':system_message(quest)}, {'role':'user','content':context}]
        own_turn = step//2
        draw_seed = seed+index*10_000+own_turn*100
        intention = None
        if client:
            if own_turn == 0:
                intention = choose(client, [messages[0], {'role':'user','content':context+
                    '\nIn an independent hypothetical check, which next action do you currently intend?'}],
                    menu, draw_seed+5)
            choice = choose(client, messages, menu, draw_seed+17)
            if choice is None:
                raise RuntimeError('Invalid action JSON; no scripted fallback')
            command = chosen_command(choice)
        elif cpu:
            command = quest['goal']
            expected = parse_event(graph, actor, command, events, ErrorEvent)
            if isinstance(expected, ErrorEvent) and item.get_container().room:
                command = 'get '+item.name
            elif isinstance(expected, ErrorEvent):
                command = 'wait'
            choice = {'action':command,'utterance':'','reasoning':'CPU qualification only'}
        else:
            raise RuntimeError('No action controller')
        expected = parse_event(graph, actor, quest['goal'], events, ErrorEvent)
        selected = parse_event(graph, actor, command, events, ErrorEvent)
        goal_match = (not isinstance(expected, ErrorEvent) and type(expected)==type(selected)
            and [x.node_id for x in expected.target_nodes]==[x.node_id for x in selected.target_nodes])
        row = execute(host, actor, command, events, ErrorEvent)
        if goal_match and row.get('executed') and not row.get('stochastic_failure'):
            complete[index] = True
        for recipient, recipient_actor in enumerate(actors):
            histories[recipient].extend(m['text'] for m in row['messages'] if m['viewer']==recipient_actor.node_id)
        histories[index].append('Your chosen action: '+command)
        if not row['legal']:
            histories[index].append(row['error'])
        turns.append({'step':step,'actor_index':index,'context':context,'menu':menu,
            'intention_shadow':intention,'choice':choice,'native':row,'goal_event_match':goal_match,
            'goals_executed':complete.copy(),'item_container':item.get_container().node_id})
    summary = {'files':pair['files'],'seed':seed,'first_actor_index':first,
        'characters':[a.name for a in actors],'original_goals':[q['goal'] for q in pair['quests']],
        'initial_owner':pair['initial_owner'],'final_item_container':item.get_container().node_id,
        'turns':len(turns),'legal_actions':sum(t['native']['legal'] for t in turns),
        'material_actions':sum(t['native']['material_changed'] for t in turns),
        'goals_executed':complete,'expression_shadow':expressions,
        'consumer_index':next((t['actor_index'] for t in turns if t['goal_event_match']
            and t['native'].get('executed') and not t['native'].get('stochastic_failure')),None),
        'final_state':material_state(graph)}
    dump(out/'episode.json',turns)
    dump(out/'summary.json',summary)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['cpu','model'],required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--model',type=Path)
    ap.add_argument('--limit',type=int,default=6)
    ap.add_argument('--seeds',nargs='+',type=int,default=[2001,2002,2003])
    args = ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    pairs = load_pairs()[:args.limit]
    modules = load_event_modules(CACHE/'sources/LIGHT')
    dump(args.out/'source_pairs.json',pairs)
    dump(args.out/'manifest.json',{'source_sha':'71a06cae8573048b1af41507ac52fe33b650fab3',
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'model':str(args.model),'seeds':args.seeds,'files':[p['files'] for p in pairs],
        'first_actor_indices':[0,1],'max_actions':12,'cloud_calls':0,
        'scope':'task binding from authored private goals; no original learned Soul/RL/scorer'})
    client = None
    if args.mode=='model':
        from strong_native_baseline import ModelClient
        os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
        client = ModelClient(args.model,2001,args.out/'unused.jsonl')
    else:
        OOGraph, events, ErrorEvent = modules
        for pair in pairs:
            graph = OOGraph.from_json(pair['quests'][0]['graph'])
            before = material_state(graph)
            bad = execute(ViewerHost(graph),actor_for(graph,pair['quests'][0]['character']),
                'get definitely_missing_item',events,ErrorEvent)
            assert not bad['legal'] and material_state(graph)==before
    start = time.monotonic()
    rows = []
    for seed in args.seeds:
        for pair in pairs:
            for first in [0,1]:
                folder = args.out/f"p{pair['files'][0].split('.')[0]}_s{seed}_first{first}"
                folder.mkdir()
                if client:
                    client.calls,client.trace_file = [],folder/'model_calls.jsonl'
                row = run(pair,seed,first,modules,folder,client,cpu=args.mode=='cpu')
                if client:
                    row.update(model_calls=len(client.calls),prompt_tokens=sum(x['prompt_tokens'] for x in client.calls),
                        completion_tokens=sum(x['completion_tokens'] for x in client.calls))
                rows.append(row)
                dump(args.out/'summary.json',rows)
                print(json.dumps({k:v for k,v in row.items() if k not in ['final_state','expression_shadow']}),flush=True)
    if args.mode=='cpu':
        assert all(sum(row['goals_executed'])==1 and row['final_item_container']=='VOID' for row in rows)
    dump(args.out/'runtime.json',{'wall_seconds':time.monotonic()-start,'cloud_calls':0})


if __name__=='__main__':
    main()
