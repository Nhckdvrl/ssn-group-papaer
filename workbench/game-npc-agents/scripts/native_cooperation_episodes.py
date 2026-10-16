#!/usr/bin/env python3
"""E81 strong native-tool baseline for two independently authored actors.

Each action is selected by a local model and executed by the original LIGHT
GraphEvent with its exact entity bindings. No goal-selection macro, escrow,
contract enforcement, invented inventory or partner private-goal disclosure.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

from commitment_decisions_v2 import schema
from native_rule_execution import SharedPrefixClient
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, material_state, observation
from native_reciprocal_deathsafe import character_dead, character_health

SEEDS = [8101, 8102]
MAX_TURNS = 32
SPEECH = {'SayEvent', 'TellEvent', 'WhisperEvent', 'ShoutEvent'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(event):
    return [type(event).__name__, [n.node_id for n in event.target_nodes]]


def header(case, index):
    quest = case['quests'][index]
    fields = [('Character', 'character'), ('Persona', 'persona'),
              ('Short motivation', 'short_motivation'), ('Mid motivation', 'mid_motivation'),
              ('Long motivation', 'long_motivation'), ('Authored immediate goal', 'goal')]
    return ('You control one character in the LIGHT fantasy game.\n'
        + '\n'.join(label+': '+quest[key] for label, key in fields)
        + '\nAuthored timeline (context and prospective plans, not proof of execution): '
        + json.dumps(quest.get('timeline',[]),ensure_ascii=False)
        + '\nChoose for your own character using your motivations, relationships, actual visible state and interaction. '
        'You may ask for help, offer a cooperative plan, negotiate, decline, revise your proposal, or act. '
        'Use the available native tools; each selection is one actual opportunity. '
        'Only a selected speech tool sends your utterance to the other character. '
        'For non-speech tools set utterance to the empty string. Speech does not transfer an item or complete a physical action. '
        'Use actual feedback to decide what happened. Do not invent possessions or completed actions.')


def catalogue(graph, actor):
    from light.graph.events.all_events_list import ALL_EVENTS_LIST
    from light.graph.events.base import ErrorEvent
    entries = {}
    for cls in ALL_EVENTS_LIST:
        for event in cls.get_valid_actions(graph, actor):
            # Enumeration alone does not run native guards (e.g. a repeated
            # block or the equipment limit). Keep exact IDs and native checks.
            event = cls.construct_from_args(actor,event.target_nodes,event.text_content)
            if isinstance(event,ErrorEvent):
                continue
            key = json.dumps([identity(event), event.to_canonical_form()], ensure_ascii=False, sort_keys=True)
            entries.setdefault(key, event)
    ordered = [(key, entries[key]) for key in sorted(entries)]
    result = {f'T{i:03d}': event for i, (key, event) in enumerate(ordered)}
    # A payload-bearing generic Say tool is always available, even when the
    # upstream menu contains no literal speech template.
    return result


def menu_text(menu):
    lines = ['SAY: say your utterance aloud']
    for tool_id, event in menu.items():
        ids = ', '.join(n.node_id for n in event.target_nodes)
        lines.append(f'{tool_id}: {event.to_canonical_form()} [entities: {ids}]')
    return '\n'.join(lines)


def action_spec(game, index, modules):
    actor = game['graph'].get_node(game['case']['actor_ids'][index])
    view = observation(game['host'], actor, *modules[1:])
    menu = catalogue(game['graph'], actor)
    view += '\nRecent actual observable interaction:\n' + '\n'.join(game['visible'][index][-32:])
    blocking = actor.get_blocking()
    if blocking:
        view += '\nActual status: You are already blocking '+blocking.get_prefix_view()+'.'
    view += ('\nUse one available native tool below. Tool entity IDs distinguish similar names; '
             'they reveal no private motivation. Each physical tool implements exactly its named action.\n'
             + menu_text(menu))
    spec = ([{'role':'system','content':header(game['case'], index)},
             {'role':'user','content':view}],
            schema({'tool':{'type':'string','enum':['SAY']+list(menu)},
                    'utterance':{'type':'string','maxLength':500}}))
    return spec, menu


def execute_selected(game, index, event, choice, turn, attempted=None):
    from light.graph.events.base import ErrorEvent
    graph, case = game['graph'], game['case']
    actor = graph.get_node(case['actor_ids'][index])
    before = material_state(graph)
    full_before = graph.to_json()
    start = len(game['host'].messages)
    random.seed(game['seed']+int(case['case_id'][:7],16)*100+turn+1000)
    row = {'actor':actor.node_id,'index':index,'turn':turn,'choice':choice,
           'event_identity':identity(event),'event_type':type(event).__name__,
           'command':event.to_canonical_form() or ('rejected tool '+choice['tool']),'before':before,
           'graph_before_sha256':hashlib.sha256(full_before.encode()).hexdigest(),
           'legal':not isinstance(event,ErrorEvent)}
    if attempted is not None:
        row['selected_identity']=attempted
    if isinstance(event,ErrorEvent):
        row.update(executed=False,error=event.view_as(actor))
    else:
        try:
            event.execute(game['host'])
            row.update(executed=bool(event.executed), stochastic_failure=bool(getattr(event,'failed',False)))
        except Exception as exc:
            row.update(executed=False, native_exception=type(exc).__name__+': '+str(exc))
            game['stop']='native_runtime_error'
    row.update(after=material_state(graph), messages=game['host'].messages[start:])
    row['material_changed'] = before != row['after']
    success = row.get('executed') and not row.get('stochastic_failure')
    if success:
        game['strict_goal_ever'][index] |= row['event_identity'] == case['goal_identities'][index]
    source=case['source_item_id']
    current=row['after'][source]
    holder=case['actor_ids'][1]
    game['receiver_acquired_ever'] |= current['container']==holder
    kind=case['player_goal_kind']
    if kind in ['get','steal']:
        game['receiver_physical_goal_ever'] |= current['container']==holder
    elif kind in ['eat','drink']:
        game['receiver_physical_goal_ever'] |= bool(success and index==1
            and row['event_type'] in ['EatEvent','DrinkEvent','IngestEvent']
            and row['event_identity'][1] and row['event_identity'][1][0]==source
            and current['container']=='VOID')
    elif kind in ['wear','wield']:
        game['receiver_physical_goal_ever'] |= current['container']==holder and bool(current.get('equipped'))
    elif kind=='put':
        goal=case['receiver_goal_identity']
        game['receiver_physical_goal_ever'] |= current['container']==goal[1][1]
    game['turns'].append(row)
    for i, aid in enumerate(case['actor_ids']):
        seen = [m['text'] for m in row['messages'] if m['viewer']==aid]
        if i==index:
            seen.insert(0,'Your actual tool attempt: '+row['command'])
            if row.get('native_exception'):
                seen.append('Native error: '+row['native_exception'])
            elif row.get('error'):
                seen.append('Native rejection: '+row['error'])
            elif not row.get('executed'):
                seen.append('Native tool did not record execution.')
        game['visible'][i].extend(seen)
    # Complete state snapshots preserve locks/paths/properties excluded by
    # material_state. These are raw assets, never committed to git.
    game['states'].append({'turn':turn,'graph':graph.to_json(),
                           'visible':[list(x) for x in game['visible']]})
    if any(character_dead(graph,a) for a in case['actor_ids']):
        game['stop']='character_death'


def apply_choice(game, index, choice, menu, turn, modules):
    if choice is None:
        game['stop']='protocol_error'; return
    actor = game['graph'].get_node(game['case']['actor_ids'][index])
    if choice['tool']=='SAY':
        event = modules[1].SayEvent.construct_from_args(actor,[],choice['utterance'])
        attempted=['SayEvent',[]]
    else:
        event = menu[choice['tool']]
        attempted=identity(event)
        payload=choice['utterance'] if type(event).__name__ in SPEECH else event.text_content
        event=type(event).construct_from_args(actor,event.target_nodes,payload)
    execute_selected(game,index,event,choice,turn,attempted)


def job(game,index,spec,stage,turn):
    return {'case_id':game['case']['case_id'],'episode_seed':game['seed'],
            'stage':stage,'index':index,'turn':turn,
            'seed':game['seed']+int(game['case']['case_id'][:7],16)*100+turn+5000,
            'messages':spec[0],'schema':spec[1]}


def run_group(cases,seeds,client,modules,out):
    games=[]
    for case in cases:
        for seed in seeds:
            graph=modules[0].from_json(case['quests'][0]['graph'])
            games.append({'case':case,'seed':seed,'graph':graph,'host':ViewerHost(graph),
                          'visible':[[],[]],'turns':[],'states':[],
                          'strict_goal_ever':[False,False],'stop':None,
                          'receiver_acquired_ever':False,'receiver_physical_goal_ever':False,
                          'initial_state':material_state(graph)})
    # The recipient/player opens from its own authored goal, not an assigned
    # generic source-item request. This common opening is genuine native Say.
    jobs=[]
    for g in games:
        actor=g['graph'].get_node(g['case']['actor_ids'][1])
        text=observation(g['host'],actor,*modules[1:])
        text+='\nBegin a brief spoken interaction with '+g['case']['quests'][0]['character']+(
            ' about what you want to accomplish. You may propose cooperation or ask for help as appropriate. '
            'This opening sends speech only; actual actions follow separately.')
        spec=([{'role':'system','content':header(g['case'],1)}, {'role':'user','content':text}],
              schema({'utterance':{'type':'string','maxLength':500}}))
        jobs.append(job(g,1,spec,'player_opening',-1))
    for g,answer in zip(games,client.batch(jobs)):
        if answer is None:g['stop']='protocol_error'
        else:
            apply_choice(g,1,{'tool':'SAY','utterance':answer['utterance']},{},-1,modules)
            g['opening']=g['turns'].pop() if g['turns'] else None
    for turn in range(MAX_TURNS):
        index=turn%2
        active=[g for g in games if g['stop'] is None]
        if not active:break
        prepared=[action_spec(g,index,modules) for g in active]
        jobs=[job(g,index,spec,'native_action',turn) for g,(spec,menu) in zip(active,prepared)]
        for g,answer,(_,menu) in zip(active,client.batch(jobs),prepared):
            apply_choice(g,index,answer,menu,turn,modules)
    with (out/'episodes.jsonl').open('a') as f, (out/'states.jsonl').open('a') as s:
        for g in games:
            case=g['case']
            row={k:v for k,v in g.items() if k not in ['case','graph','host','visible','states']}
            row.update(case_id=case['case_id'],graph_sha256=case['graph_sha256'],
                       quest_files=[q['source_file'] for q in case['quests']],
                       stop=g['stop'] or 'turn_limit', final_state=material_state(g['graph']),
                       final_health=[character_health(g['graph'],a) for a in case['actor_ids']],
                       final_dead=[character_dead(g['graph'],a) for a in case['actor_ids']])
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
            s.write(json.dumps({'case_id':case['case_id'],'seed':g['seed'],'states':g['states']},ensure_ascii=False)+'\n')
    return len(games)


def load_cases(path):
    rows=list(map(json.loads,path.read_text().splitlines()))
    assert rows and len(rows)==len({c['graph_sha256'] for c in rows})
    for c in rows:
        assert c['quests'][0]['graph']==c['quests'][1]['graph']
        assert hashlib.sha256(c['quests'][0]['graph'].encode()).hexdigest()==c['graph_sha256']
        c['goal_identities']=[c['npc_native_goal_identity'],
            c['receiver_goal_identity'] or c['player_original_initial_native_identity']]
        c['task_family']='acquisition' if c['player_goal_kind'] in ['get','steal'] else 'use_or_put'
    return rows


def cpu_check(cases,modules):
    counts={'worlds':len(cases),'typed_tools':0,'private_text_checks':0,'native_witnesses':0}
    for case in cases:
        graph=modules[0].from_json(case['quests'][0]['graph'])
        g={'case':case,'seed':SEEDS[0],'graph':graph,'host':ViewerHost(graph),
           'visible':[[],[]],'turns':[],'states':[],'strict_goal_ever':[False,False],'stop':None}
        original=graph.to_json()
        for index in [0,1]:
            (messages,structure),menu=action_spec(g,index,modules)
            assert messages[0]['content']==header(case,index)
            peer=case['quests'][1-index]
            for key in ['short_motivation','mid_motivation','long_motivation']:
                value=peer[key]
                if len(value)>25 and value not in header(case,index):
                    assert value not in json.dumps(messages), (case['case_id'],index,key)
            for event in menu.values():
                assert event.actor.node_id==case['actor_ids'][index]
                counts['typed_tools']+=1
            counts['private_text_checks']+=1
        assert graph.to_json()==original
        for step, witness in enumerate(case['native_witness']):
            actor=graph.get_node(witness['actor_id'])
            kind,targets=witness['identity']
            event=getattr(modules[1],kind).construct_from_args(actor,[graph.get_node(n) for n in targets])
            assert not isinstance(event,modules[2])
            assert identity(event)==witness['identity'],(case['case_id'],step,identity(event),witness)
            event.execute(g['host'])
            assert event.executed
            counts['native_witnesses']+=1
    counts.update(status='PASS',model_calls=0,new_cloud_calls=0)
    return counts


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--model',type=Path)
    ap.add_argument('--profile',action='store_true');ap.add_argument('--cpu-check',action='store_true')
    ap.add_argument('--shard',type=int,default=0);ap.add_argument('--shards',type=int,default=1)
    ap.add_argument('--prior-runs',type=Path,nargs='*',default=[])
    a=ap.parse_args(); assert os.environ.get('PYTHONHASHSEED')=='0'
    modules=load_event_modules(CACHE/'sources/LIGHT');rows=load_cases(a.data)
    if a.cpu_check:
        result=cpu_check(rows,modules);result.update(driver_sha256=sha(Path(__file__)),data_sha256=sha(a.data))
        a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return
    assert a.model
    if a.profile:
        selected=[]
        for group in ['acquisition','use_or_put']:
            found=next((c for c in rows if c['task_family']==group),None)
            if found and found not in selected:selected.append(found)
    else:selected=rows[a.shard::a.shards]
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'experiment':'E81','model':str(a.model),'data':str(a.data),'data_sha256':sha(a.data),
              'driver_sha256':sha(Path(__file__)),'profile':a.profile,'shard':a.shard,'shards':a.shards,
              'seeds':SEEDS,'case_ids':[c['case_id'] for c in selected],'max_turns':MAX_TURNS,
              'personas':'both original authored','new_cloud_calls':0,'world_modified':False,
              'tools':'native typed events selected by both local model actors; one primitive per opportunity'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    client=SharedPrefixClient(a.model,a.out,SEEDS[0])
    for folder in a.prior_runs:
        old=json.loads((folder/'manifest.json').read_text())
        assert old['driver_sha256']==manifest['driver_sha256'] and old['model']==str(a.model)
        assert old['data_sha256']==manifest['data_sha256']
        assert (folder/'runtime.json').exists()
        for row in map(json.loads,(folder/'model_calls.jsonl').open()):
            client.cache.setdefault(row['decision_key'],row['parsed'])
    start=time.monotonic();count=0
    for group in [selected[:2]]+[selected[i:i+8] for i in range(2,len(selected),8)]:
        if not group:continue
        count+=run_group(group,SEEDS,client,modules,a.out)
        print(json.dumps({'worlds_completed':count//len(SEEDS),'episodes':count,'calls':client.inner.calls,
                          'seconds':time.monotonic()-start}),flush=True)
    (a.out/'runtime.json').write_text(json.dumps({'worlds':len(selected),'episodes':count,
        'calls':client.inner.calls,'reused_calls':client.reused,'wall_seconds':time.monotonic()-start,
        'model_load_seconds':client.inner.load_seconds,'new_cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
