#!/usr/bin/env python3
"""E64 v3: identical v2 policy; read deleted native actor IDs as death outcomes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
from commitment_decisions_v2 import BatchClient, schema
from native_dependency_roles import TRAITS
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, execute, observation, legal_commands, chosen_command, material_state

CUES={'none':'','check':'Before offering an item, consider what physical action by the other character would advance your authored goals; when appropriate, propose a conditional exchange and check its execution.'}


def identity(case,index,persona,cue):
    q=case['quests'][index]
    text=(f"You are {q['character']} in a native LIGHT game.\nCharacter persona: {q['persona']}\n"
        f"Short motivation: {q['short_motivation']}\nMid motivation: {q['mid_motivation']}\n"
        f"Long motivation: {q['long_motivation']}\nAuthored immediate goal action: {q['goal']}\n"
        f"Authored timeline: {json.dumps(q.get('timeline',[]),ensure_ascii=False)}\n")
    if index==0:text+='Personal disposition: '+TRAITS[persona]+'\n'+CUES[cue]+'\n'
    return text+('Choose for this character using the current visible game state, your motivations and social relationships. '
        'You may speak, negotiate or execute a physical action. Use actual feedback to distinguish speech from execution. '
        'Private reasons are not spoken to the other character; only a selected speech command transmits your utterance.')


def character_health(graph, actor_id):
    node=graph.get_node(actor_id)
    if node is None:
        assert graph.get_node(actor_id+'__dead__') is not None
        return 0
    return node.get_prop('health')


def character_dead(graph, actor_id):
    node=graph.get_node(actor_id)
    if node is None:
        assert graph.get_node(actor_id+'__dead__') is not None
        return True
    return bool(node.get_prop('dead'))


def attained(g):
    return [g['graph'].get_node(t).get_container().node_id==a for t,a in zip(g['case']['goal_item_ids'],g['case']['actor_ids'])]


def apply(g,index,command,choice,turn,modules):
    c=g['case'];graph=g['graph'];actor=graph.get_node(c['actor_ids'][index])
    goal=parse_event(graph,actor,c['quests'][index]['goal'],*modules[1:])
    event=parse_event(graph,actor,command,*modules[1:])
    match=(not isinstance(goal,modules[2]) and not isinstance(event,modules[2])
           and goal.to_canonical_form()==event.to_canonical_form())
    before=[character_health(graph,a) for a in c['actor_ids']]
    random.seed(g['seed']+int(c['case_id'][:7],16)*100+turn)
    result=execute(g['host'],actor,command,*modules[1:])
    success=result['legal'] and result.get('executed') and not result.get('stochastic_failure')
    if match and success:g['strict_goal_done'][index]=True
    holders=attained(g)
    g['ever_attained']=[x or y for x,y in zip(g['ever_attained'],holders)]
    after=[character_health(graph,a) for a in c['actor_ids']]
    result.update(index=index,turn=turn,choice=choice,matches_strict_goal=match,
                  attained_after=holders,health_before=before,health_after=after)
    g['turns'].append(result)
    for i,aid in enumerate(c['actor_ids']):
        messages=[m['text'] for m in result['messages'] if m['viewer']==aid]
        if i==index:messages.insert(0,'Your executed command: '+command)
        g['visible'][i].extend(messages)
    if any(character_dead(graph,a) for a in c['actor_ids']):g['stop']='character_death'


def run_group(cases,seeds,client,modules,out):
    jobs=[]
    for c in cases:
        for seed in seeds:
            graph=modules[0].from_json(c['quests'][0]['graph']);actor=graph.get_node(c['actor_ids'][1])
            view=observation(ViewerHost(graph),actor,*modules[1:])
            jobs.append({'case_id':c['case_id'],'episode_seed':seed,'stage':'opening',
                'seed':seed+int(c['case_id'][:7],16),
                'messages':[{'role':'system','content':identity(c,1,'firm','none')},
                {'role':'user','content':view+'\nStart a brief conversation with '+c['quests'][0]['character']
                 +' about your immediate motivation. This initial turn is spoken dialogue only; physical decisions follow separately.'}],
                'schema':schema({'utterance':{'type':'string'}})})
    openings={(j['case_id'],j['episode_seed']):answer for j,answer in zip(jobs,client.batch(jobs))}
    games=[]
    for c in cases:
        for seed in seeds:
            for p in TRAITS:
                for cue in CUES:
                    graph=modules[0].from_json(c['quests'][0]['graph']);opening=openings[c['case_id'],seed]
                    g={'case':c,'persona':p,'cue':cue,'seed':seed,'graph':graph,'host':ViewerHost(graph),
                       'visible':[[],[]],'strict_goal_done':[False,False],'ever_attained':[False,False],
                       'turns':[],'stop':None,'protocol_error':None,'opening':opening,'initial_state':material_state(graph)}
                    if opening is None:g['stop'],g['protocol_error']='protocol_error','invalid_opening_json'
                    else:apply(g,1,'say '+opening['utterance'],opening,-1,modules)
                    games.append(g)
    for turn in range(32):
        index=turn%2;active=[g for g in games if g['stop'] is None]
        if not active:break
        jobs=[]
        for g in active:
            c=g['case'];actor=g['graph'].get_node(c['actor_ids'][index]);view=observation(g['host'],actor,*modules[1:])
            menu=legal_commands(g['graph'],actor)
            text=(view+'\nYour goal resource is currently in your own possession: '+str(attained(g)[index])
                  +'\nYour exact authored goal action has actually executed: '+str(g['strict_goal_done'][index])
                  +'\nRecent observable interaction:\n'+'\n'.join(g['visible'][index][-16:])
                  +'\nLegal game commands:\n'+'\n'.join(menu)+'\nChoose your next legal game action.')
            jobs.append({'case_id':c['case_id'],'persona':g['persona'],'cue':g['cue'],'episode_seed':g['seed'],
                'stage':'native_action','acting_index':index,'turn':turn,
                'seed':g['seed']+int(c['case_id'][:7],16)*100+turn+2000,
                'messages':[{'role':'system','content':identity(c,index,g['persona'],g['cue'])},{'role':'user','content':text}],
                'schema':schema({'action':{'type':'string','enum':menu+['say']},'utterance':{'type':'string'}})})
        for g,answer in zip(active,client.batch(jobs)):
            if answer is None:g['stop'],g['protocol_error']='protocol_error','invalid_action_json'
            else:apply(g,index,chosen_command(answer),answer,turn,modules)
    with (out/'episodes.jsonl').open('a') as f:
        for g in games:
            c=g['case'];row={k:v for k,v in g.items() if k not in ['case','graph','host','visible']}
            row.update(case_id=c['case_id'],graph_sha256=c['graph_sha256'],stop=g['stop'] or 'turn_limit',
                final_state=material_state(g['graph']),final_attained=attained(g),
                final_health=[character_health(g['graph'],a) for a in c['actor_ids']],
                final_dead=[character_dead(g['graph'],a) for a in c['actor_ids']])
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
    return len(games)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--model',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seeds',type=int,nargs='+',default=[6401,6402,6403]);ap.add_argument('--profile',action='store_true')
    a=ap.parse_args();rows=list(map(json.loads,a.dataset.read_text().splitlines()))
    assert len(rows)==len({r['graph_sha256'] for r in rows})==9
    if a.profile:rows=rows[:1]
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
        'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),'case_ids':[r['case_id'] for r in rows],
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'traits':TRAITS,'cues':CUES,
        'max_turns':32,'private_goals_of_partner_fed_to_focal':False,'world_modified':False,'cloud_calls':0,
        'scope':'Resource acquisition and actual health consequences; not full private utility or universally beneficial trade.'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    modules=load_event_modules(CACHE/'sources/LIGHT');client=BatchClient(a.model,a.out,a.seeds[0])
    start=time.monotonic();count=0
    for group in [rows[:1]]+[rows[i:i+3] for i in range(1,len(rows),3)]:
        if group:count+=run_group(group,a.seeds,client,modules,a.out)
        print(json.dumps({'episodes':count,'calls':client.calls,'wall_seconds':time.monotonic()-start}),flush=True)
    assert count==len(rows)*len(a.seeds)*len(TRAITS)*len(CUES)
    (a.out/'runtime.json').write_text(json.dumps({'worlds':len(rows),'episodes':count,'calls':client.calls,
        'wall_seconds':time.monotonic()-start,'model_load_seconds':client.load_seconds,'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
