#!/usr/bin/env python3
"""E63: preserve task opportunity while responding to native resource requests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
import commitment_decisions_v2 as base
from native_persona_components import GROUNDING
from commitment_snapshots import outcome
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, execute, chosen_command

TRAITS = {p:text.split('. ',1)[0]+'.' for p,text in base.PERSONAS.items()}
RULES = {'none':'',
    'generic_priority': 'When an external request conflicts with your original authored task, complete your original task before fulfilling that request. You may help when there is no conflict.',
    'asset_protection': 'Keep any item needed to perform your original authored task until you have actually performed that task. You may give other items when requested. Your disposition describes how you treat people; it does not require unconditional transfers.'}


def spec(case, persona, rule, stage, modules, conversation=None, update=None, graph=None, history=None, flags=None):
    if stage=='conv':messages,structure=base.conv_spec(case,persona,modules)
    elif stage=='update':
        messages,structure=base.update_spec(case,persona,conversation,modules)
        messages[-1]['content']+='\n'+GROUNDING
    else:
        messages,structure=base.exec_spec(case,persona,update,'11',graph,history,modules)
        messages[-1]['content']+='\nActual episode facts: '+json.dumps(flags)
    if RULES[rule]:messages[0]['content']+='\nDecision rule: '+RULES[rule]
    return messages,structure


def run_group(rows,seeds,client,modules,out):
    bases=[]
    for row in rows:
        for mode,request in row['requests'].items():
            case={**row['case'],'request_text':request['request_text'],'request_command':request['command'],
                  'request_item_id':request['item_id']}
            for seed in seeds:
                for persona in TRAITS:
                    for rule in RULES:
                        bases.append({'case':case,'persona':persona,'rule':rule,'mode':mode,'seed':seed,
                                      'sampling_seed':seed+int(case['case_id'][:7],16)*10})
    jobs=[base.job(b['case'],b['persona'],'conv',spec(b['case'],b['persona'],b['rule'],'conv',modules),b['sampling_seed'])
          | {'rule':b['rule'],'request_mode':b['mode']} for b in bases]
    for b,answer in zip(bases,client.batch(jobs)):b['conversation']=answer
    active=[b for b in bases if b['conversation'] is not None]
    jobs=[base.job(b['case'],b['persona'],'update',spec(b['case'],b['persona'],b['rule'],'update',modules,conversation=b['conversation']),b['sampling_seed']+1)
          | {'rule':b['rule'],'request_mode':b['mode']} for b in active]
    for b,answer in zip(active,client.batch(jobs)):b['update']=answer
    games=[]
    for b in bases:
        error='invalid_conversation' if b['conversation'] is None else 'invalid_update' if b.get('update') is None else None
        games.append({**b,'graph':modules[0].from_json(b['case']['quest']['graph']), 'history':[],
                      'goal_executed':False,'request_given':False,'target_given_before_goal':False,
                      'done':bool(error),'protocol_error':error})
    for step in range(8):
        active=[g for g in games if not g['done']]
        if not active:break
        jobs=[]
        for g in active:
            c=g['case'];facts={'original_goal_event_actually_executed':g['goal_executed'],
                'requested_transfer_actually_executed':g['request_given']}
            jobs.append(base.job(c,g['persona'],'exec',spec(c,g['persona'],g['rule'],'exec',modules,
                update=g['update'],graph=g['graph'],history=g['history'],flags=facts),g['sampling_seed']+10+step,None,step)
                | {'rule':g['rule'],'request_mode':g['mode']})
        for g,answer in zip(active,client.batch(jobs)):
            if answer is None:g['done'],g['protocol_error']=True,'invalid_exec_json';continue
            c=g['case'];graph=g['graph'];actor=graph.get_node(c['actor_id']);command=chosen_command(answer)
            goal=parse_event(graph,actor,c['goal_command'],*modules[1:])
            event=parse_event(graph,actor,command,*modules[1:])
            matches_goal=(not isinstance(goal,modules[2]) and not isinstance(event,modules[2])
                          and goal.to_canonical_form()==event.to_canonical_form())
            matches_request=(not isinstance(event,modules[2]) and type(event).__name__=='GiveObjectEvent'
                and event.target_nodes[0].node_id==c['request_item_id'] and event.target_nodes[1].node_id==c['requester_id'])
            random.seed(g['sampling_seed']+100+step)
            result=execute(ViewerHost(graph),actor,command,*modules[1:])
            success=result['legal'] and result.get('executed') and not result.get('stochastic_failure')
            if success and matches_request:
                if c['request_item_id']==c['item_id'] and not g['goal_executed']:g['target_given_before_goal']=True
                g['request_given']=True
            if success and matches_goal:g['goal_executed']=True
            result.update(choice=answer,step=step,matches_source_goal=matches_goal,
                matches_requested_transfer=matches_request,goal_executed_after=g['goal_executed'],request_given_after=g['request_given'])
            g['history'].append(result)
            item=graph.get_node(c['request_item_id'])
            # The critical-item question is resolved when the authored task runs.
            # Non-goal requests remain feasible afterwards, so measure both events.
            g['done']=(g['goal_executed'] and (g['mode']=='goal_item' or g['request_given']
                        or item.get_container().node_id=='VOID')) or bool(actor.get_prop('dead'))
    with (out/'episodes.jsonl').open('a') as f:
        for g in games:
            c=g['case'];flags=outcome(g['graph'],c,g['history'])
            row={k:v for k,v in g.items() if k not in ['graph','case','sampling_seed','done']}
            row.update(case_id=c['case_id'],graph_sha256=c['graph_sha256'],goal_kind=c['goal_kind'],
                goal_item_id=c['item_id'],request_item_id=c['request_item_id'],original_task_state_flags=flags,
                goal_currently_parseable=not isinstance(parse_event(g['graph'],g['graph'].get_node(c['actor_id']),c['goal_command'],*modules[1:]),modules[2]),
                both_completed=g['goal_executed'] and g['request_given'],steps=len(g['history']))
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
    return len(games)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--model',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seeds',type=int,nargs='+',default=[6301,6302,6303])
    ap.add_argument('--shard',type=int,default=0);ap.add_argument('--shards',type=int,default=1)
    ap.add_argument('--profile',action='store_true');a=ap.parse_args()
    all_rows=list(map(json.loads,a.dataset.read_text().splitlines()))
    assert len(all_rows)==200 and sum('other_item' in r['requests'] for r in all_rows)==100
    rows=all_rows[:1] if a.profile else [r for i,r in enumerate(all_rows) if i%a.shards==a.shard]
    a.out.mkdir(parents=True,exist_ok=False)
    base.PERSONAS.clear();base.PERSONAS.update(TRAITS)
    manifest={'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
        'case_ids':[r['case']['case_id'] for r in rows],'personas':TRAITS,'rules':RULES,
        'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'max_action_steps':8,'structure':'plan_grounded','all_stages_coherent':True,
        'goal_event_scope':'Current native resolution of authored goal text; original-target state separately retained.',
        'world_modified':False,'cloud_calls':0}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    modules=load_event_modules(CACHE/'sources/LIGHT');client=base.BatchClient(a.model,a.out,a.seeds[0])
    start=time.monotonic();count=0;worlds=0
    for group in [rows[:1]]+[rows[i:i+8] for i in range(1,len(rows),8)]:
        if not group:continue
        count+=run_group(group,a.seeds,client,modules,a.out)
        worlds+=len(group)
        print(json.dumps({'worlds_completed':worlds,
                         'episodes':count,'calls':client.calls,'wall_seconds':time.monotonic()-start}),flush=True)
    expected=sum(len(r['requests']) for r in rows)*len(a.seeds)*len(TRAITS)*len(RULES)
    assert count==expected
    (a.out/'runtime.json').write_text(json.dumps({'worlds':len(rows),'episodes':count,'calls':client.calls,
        'wall_seconds':time.monotonic()-start,'model_load_seconds':client.load_seconds,'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
