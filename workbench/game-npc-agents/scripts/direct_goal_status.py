#!/usr/bin/env python3
"""E53: fixed real dialogue, direct NPC actions, counterfactual goal events."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
from commitment_decisions_v2 import BatchClient, PERSONAS, header, schema, job
from commitment_snapshots import outcome
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute, observation, legal_commands

CONDITIONS=['none','both_unexecuted','own_executed','request_executed','own_executed_truth','request_executed_truth']

def build_spec(g,modules):
    c=g['case'];actor=g['graph'].get_node(c['actor_id'])
    view=observation(ViewerHost(g['graph']),actor,*modules[1:]);menu=legal_commands(g['graph'],actor)
    messages=[{'role':'system','content':header(c,g['persona'])},
              {'role':'user','content':view+'\nYour current authored task: '+c['goal_command']+'\n'+c['requester_name']+' says: '+c['request_text']},
              {'role':'assistant','content':g['conversation']['reply']}]
    text='Current game observation:\n'+view+'\nChoose your next legal game action.'
    cond=g['condition']
    if cond!='none':
        own='has already been executed' if cond.startswith('own_executed') else 'has not yet been executed'
        requested='has already been executed' if cond.startswith('request_executed') else 'has not yet been executed'
        text+=f'\nRetrieved record from the end of this conversation: The authored action "{c["goal_command"]}" {own} in this encounter. The requested action "{c["request_command"]}" {requested} in this encounter.'
    if cond.endswith('_truth') and not g['history']:
        text+='\nActual game observation check: no physical game action has occurred since this conversation; neither of these two actions has been executed.'
    if g['history']:text+='\nYour recent actual game actions: '+json.dumps([r['command'] for r in g['history']])
    text+='\nLegal commands:\n'+'\n'.join(menu)
    messages.append({'role':'user','content':text})
    return messages,schema({'action':{'type':'string','enum':menu+['say']},'utterance':{'type':'string'},'reason':{'type':'string'}})

def run(cases,source,seed,client,modules,out):
    branches=[]
    for c in cases:
        for p in PERSONAS:
            u=source[(c['case_id'],seed-300,p)]
            for cond in CONDITIONS:
                branches.append({'case':c,'persona':p,'condition':cond,'conversation':u,
                                 'graph':modules[0].from_json(c['quest']['graph']),
                                 'history':[],'done':False,'sampling_seed':seed+int(c['case_id'][:7],16)*10})
    for step in range(6):
        active=[g for g in branches if not g['done']]
        if not active:break
        jobs=[{**job(g['case'],g['persona'],'exec',build_spec(g,modules),g['sampling_seed']+10+step,None,step),
               'goal_status_condition':g['condition']} for g in active]
        answers=client.batch(jobs)
        for g,answer in zip(active,answers):
            if answer is None:g['done'],g['protocol_error']=True,'invalid_exec_json';continue
            command='say '+answer['utterance'] if answer['action']=='say' else answer['action'].replace('<SOMETHING>',answer['utterance'])
            random.seed(g['sampling_seed']+100+step)
            row=execute(ViewerHost(g['graph']),g['graph'].get_node(g['case']['actor_id']),command,*modules[1:])
            row['choice']=answer;g['history'].append(row)
            flags=outcome(g['graph'],g['case'],g['history'])
            g['done']=bool(flags['own_task'] or flags['request'] or g['graph'].get_node(g['case']['item_id']).get_container().node_id!=g['case']['actor_id'])
    records=[]
    with (out/'branches.jsonl').open('a') as f:
        for g in branches:
            flags=outcome(g['graph'],g['case'],g['history']);assert not(flags['own_task'] and flags['request'])
            r={'case_id':g['case']['case_id'],'graph_sha256':g['case']['graph_sha256'],
               'persona':g['persona'],'condition':g['condition'],'seed':seed,'conversation':g['conversation'],
               'flags':flags,'goal_kind':g['case']['goal_kind'],'steps':len(g['history']),
               'protocol_error':g.get('protocol_error'),'history':g['history']}
            f.write(json.dumps(r,ensure_ascii=False)+'\n');records.append({k:v for k,v in r.items() if k!='history'})
    return records

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--shard',type=int,default=0)
    ap.add_argument('--shards',type=int,default=1);ap.add_argument('--seeds',type=int,nargs='+',default=[5301,5302,5303])
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    cases=[r for r in map(json.loads,a.dataset.read_text().splitlines()) if r['split']=='pilot'][a.shard::a.shards]
    source={}
    for r in map(json.loads,(a.source/'branches.jsonl').read_text().splitlines()):
        k=(r['case_id'],r['seed'],r['conv_persona'])
        if k in source:assert source[k]==r['conversation']
        source[k]=r['conversation']
    assert all((c['case_id'],s-300,p) in source for c in cases for s in a.seeds for p in PERSONAS)
    manifest={'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
              'case_ids':[c['case_id'] for c in cases],'conditions':CONDITIONS,'personas':PERSONAS,
              'source_dialogue_sha256':hashlib.sha256((a.source/'branches.jsonl').read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'world_modified':False,'cloud_calls':0,'architecture':'direct dialogue history to native action; no Planner/agenda update'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=load_event_modules(CACHE/'sources/LIGHT');client=BatchClient(a.model,a.out,a.seeds[0]);start=time.monotonic();all_rows=[]
    for s in a.seeds:
        for i in range(0,len(cases),10):
            all_rows.extend(run(cases[i:i+10],source,s,client,modules,a.out))
            print(json.dumps({'seed':s,'graphs':min(i+10,len(cases)),'calls':client.calls,'branches':len(all_rows)}),flush=True)
    (a.out/'runtime.json').write_text(json.dumps({'graphs':len(cases),'branches':len(all_rows),'calls':client.calls,
        'wall_seconds':time.monotonic()-start,'model_load_seconds':client.load_seconds,'cloud_calls':0},indent=2)+'\n')

if __name__=='__main__':main()
