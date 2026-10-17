#!/usr/bin/env python3
"""E51: matched commitment status and goal-reminder interventions, native outcomes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
from commitment_decisions_v2 import BatchClient, PERSONAS, exec_spec, job
from commitment_snapshots import outcome
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute

CONDITIONS={
    'none':(None,False,False,False),
    'pending':('pending',False,False,False),
    'completed':('completed',False,False,False),
    'pending_goal':('pending',True,False,False),
    'completed_goal':('completed',True,False,False),
    'pending_goal_state':('pending',True,True,False),
    'completed_goal_state':('completed',True,True,False),
    'direct_request':(None,False,False,True),
}


def memory(case,condition):
    status,goal,state,direct=CONDITIONS[condition]
    if status is None:return ''
    text=f"I committed to {case['request_command']}; this commitment is {status}."
    if goal:text+=' My original task is to '+case['goal_command']+'.'
    return text


def spec(branch,modules):
    c,p=branch['case'],branch['persona']
    status,goal,state,direct=CONDITIONS[branch['condition']]
    update={'priority_actions':[c['request_command']],'intention_memory':memory(c,branch['condition'])}
    messages,sch=exec_spec(c,p,update,'11' if status else '10',branch['graph'],branch['history'],modules)
    # Acceptance is held fixed, visible in every cell, including no-memory.
    shared=f'\nPrior conversation, before any physical action: You said "Yes, I will {c["request_command"]} now."'
    if state and not branch['history']:
        shared+='\nCurrent physical observation: the item is still in your inventory; no transfer has occurred.'
    if direct:shared+='\nFor this control, carry out '+c['request_command']+' as your next physical action.'
    messages[-1]['content']+=shared
    return messages,sch


def run(cases,client,modules,out,seed):
    branches=[]
    for c in cases:
        for p in PERSONAS:
            for condition in CONDITIONS:
                branches.append({'case':c,'persona':p,'condition':condition,
                                 'graph':modules[0].from_json(c['quest']['graph']),
                                 'history':[],'done':False,'sampling_seed':seed+int(c['case_id'][:7],16)*10})
    for step in range(6):
        active=[g for g in branches if not g['done']]
        if not active:break
        jobs=[{**job(g['case'],g['persona'],'exec',spec(g,modules),g['sampling_seed']+10+step,'11',step),
               'status_condition':g['condition']} for g in active]
        answers=client.batch(jobs)
        for g,answer in zip(active,answers):
            if answer is None:
                g['done'],g['protocol_error']=True,'invalid_exec_json';continue
            command=('say '+answer['utterance'] if answer['action']=='say'
                     else answer['action'].replace('<SOMETHING>',answer['utterance']))
            random.seed(g['sampling_seed']+100+step)
            row=execute(ViewerHost(g['graph']),g['graph'].get_node(g['case']['actor_id']),command,*modules[1:])
            row['choice']=answer;g['history'].append(row)
            flags=outcome(g['graph'],g['case'],g['history'])
            g['done']=bool(flags['own_task'] or flags['request']
                          or g['graph'].get_node(g['case']['item_id']).get_container().node_id!=g['case']['actor_id'])
    result=[]
    with (out/'branches.jsonl').open('a') as f:
        for g in branches:
            flags=outcome(g['graph'],g['case'],g['history'])
            assert not(flags['own_task'] and flags['request'])
            row={'case_id':g['case']['case_id'],'graph_sha256':g['case']['graph_sha256'],
                 'goal_kind':g['case']['goal_kind'],'seed':seed,'persona':g['persona'],
                 'condition':g['condition'],'memory':memory(g['case'],g['condition']),
                 'flags':flags,'steps':len(g['history']),'history':g['history'],
                 'protocol_error':g.get('protocol_error'),'all_legal':all(x['legal'] for x in g['history'])}
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
            result.append({k:v for k,v in row.items() if k!='history'})
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--split',default='pilot');ap.add_argument('--limit',type=int,default=40)
    ap.add_argument('--seeds',type=int,nargs='+',default=[5101,5102,5103]);a=ap.parse_args()
    rows=[r for r in map(json.loads,a.dataset.read_text().splitlines()) if r['split']==a.split][:a.limit]
    assert len({r['graph_sha256'] for r in rows})==len(rows)
    a.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    manifest={'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
              'case_ids':[r['case_id'] for r in rows],'conditions':CONDITIONS,'personas':PERSONAS,
              'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cloud_calls':0,'fixed_conversation':'accept immediate request, before any action',
              'scope':'controlled commitment fixture, first physical decision; not total persona effect'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=load_event_modules(CACHE/'sources/LIGHT');client=BatchClient(a.model,a.out,a.seeds[0])
    t=time.monotonic();summary=[]
    for seed in a.seeds:
        for i in range(0,len(rows),10):
            summary.extend(run(rows[i:i+10],client,modules,a.out,seed))
            (a.out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps({'seed':seed,'graphs':min(i+10,len(rows)),'branches':len(summary),'calls':client.calls}),flush=True)
    (a.out/'runtime.json').write_text(json.dumps({'wall_seconds':time.monotonic()-t,
        'model_load_seconds':client.load_seconds,'calls':client.calls,'cloud_calls':0,
        'graphs':len(rows),'branches':len(summary)},indent=2)+'\n')


if __name__=='__main__':main()
