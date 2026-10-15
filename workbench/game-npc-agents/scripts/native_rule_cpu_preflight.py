#!/usr/bin/env python3
"""CPU replay validation; cache outputs are appended, latest complete batch compared."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from native_rule_execution import *
configure();m=policy.load_event_modules(policy.CACHE/'sources/LIGHT');root=policy.CACHE/'runs'
rows=[json.loads(x) for x in (root/'e63_native_dependency_qualification/snapshots.jsonl').read_text().splitlines() if json.loads(x)['case']['goal_kind'] in ['wear','wield']]
cid=sorted(r['case']['case_id'] for r in rows)[0];r=next(r for r in rows if r['case']['case_id']==cid);req=r['requests']['goal_item'];case={**r['case'],'request_text':req['request_text'],'request_command':req['command'],'request_item_id':req['item_id']}
report=[]
for model,sources in [('gemma',['e63_gemma_dependency']),('32b',['e63_32b_dependency_s0','e63_32b_dependency_s1'])]:
 episodes=[];calls={}
 for dn in sources:
  p=root/dn
  for l in (p/'episodes.jsonl').open():
   x=json.loads(l)
   if x['case_id']==cid and x['mode']=='goal_item' and x['rule'] in ['asset_protection','generic_priority']:episodes.append(x)
  for l in (p/'model_calls.jsonl').open():
   x=json.loads(l)
   if x['case_id']==cid and x['stage']=='exec' and x['request_mode']=='goal_item' and x['rule'] in ['asset_protection','generic_priority']:calls[x['persona'],x['seed'],x['rule'],x['step']]=x
 class Replay:
  def __init__(self):self.count=0;self.view_order_differences=0
  def batch(self,jobs):
   answers=[]
   for j in jobs:
    x=calls[j['persona'],j['seed'],j['exec_rule'],j['step']]
    
    assert j['schema']==x['schema'] and j['messages'][0]==x['messages'][0]
    assert j['messages'][1]['content'].split('\nOriginal authored task:',1)[1]==x['messages'][1]['content'].split('\nOriginal authored task:',1)[1]
    self.view_order_differences += int(j['messages']!=x['messages'])
    answers.append(x['parsed']);self.count+=1
   return answers
 bases=[]
 for e in episodes:
  bases.append({'case':case,'mode':'goal_item','seed':e['seed'],'persona':e['persona'],'upstream_rule':e['rule'],'exec_rule':e['rule'],'feedback':'legacy','conversation':e['conversation'],'update':e['update'],'sampling_seed':e['seed']+int(cid[:7],16)*10})
 out=root/('e67_cpu_preflight_'+model);out.mkdir(exist_ok=True);client=Replay();run_execution(bases,client,m,out)
 replay=list(map(json.loads,(out/'episodes.jsonl').read_text().splitlines()))[-len(episodes):]
 assert len(replay)==len(episodes)==12
 for a,b in zip(episodes,replay):assert [{k:v for k,v in h.items() if k!='messages'} for h in a['history']]==[{k:v for k,v in h.items() if k!='messages'} for h in b['history']] and a['goal_executed']==b['goal_executed'] and a['request_given']==b['request_given']
 report.append({'model':model,'episodes':len(replay),'fixed_fields_and_schema_matches':client.count,'all_physical_history_equal':True,'native_view_order_differences':client.view_order_differences,'scope':'Historical look/inventory ordering varies with Python process; schema/system/task/history/plan/memory equal. New paired conditions use fixed PYTHONHASHSEED=0 and fresh diagonals.'})
# Actual native canonical block, error and one truthful feedback addition.
g=m[0].from_json(case['quest']['graph']);a=g.get_node(case['actor_id']);e=next(e for e in m[1].BlockEvent.get_valid_actions(g,a) if e.target_nodes[0].node_id==case['requester_id']);command=e.to_canonical_form()
first=execute(ViewerHost(g),a,command,*m[1:]);second=execute(ViewerHost(g),a,command,*m[1:]);assert first['legal'] and first['executed'] and not second['legal']
b={**bases[0],'graph':g,'history':[first,second],'goal_executed':False,'request_given':False,'feedback':'block_status'};msgs,_=execution_spec(b,m)
report.append({'native_block':command,'repeat_error':second['error'],'feedback_lines':msgs[-1]['content'].splitlines()[-2:],'world_modified':False})
p=Path('/home/xiang/ssn-group-papaer/workbench/game-npc-agents/results/E67_cpu_preflight.json');p.write_text(json.dumps({'model_calls':0,'checks':report},indent=2)+'\n');print(json.dumps(report),flush=True)
