#!/usr/bin/env python3
"""Matched-item stage effects, raw output support and interface interactions."""
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from aggregate import estimate
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();runs=a.root/'runs';out={'hu':{},'implicaturex':{},'epitome':{},'betting':{},'pending':[],
'limits':['Item-cluster CIs do not cover training-seed uncertainty.','Approx controls lack human neutrality norms.','Restricted choice probabilities are not transparent knowledge.','Stage changes mix data and training objectives.']}
def load(name,file):
 p=runs/name
 if not (p/'config.json').exists():out['pending'].append(name);return None,None
 c=json.loads((p/'config.json').read_text())
 if not c.get('complete'):out['pending'].append(name);return None,None
 assert c.get('numerical_gate_pass') or c.get('numerical_controls'),name
 return [json.loads(s) for s in (p/file).read_text().splitlines()],c

def paired(left,right,keys,group,metrics):
 li={tuple(r[k] for k in keys):r for r in left};ri={tuple(r[k] for k in keys):r for r in right}
 assert len(li)==len(left) and len(ri)==len(right) and li.keys()==ri.keys()
 d=defaultdict(list)
 for key,l in li.items():
  r=ri[key];assert all(l[k]==r[k] for k in group)
  d[tuple(l[k] for k in group)].append({m:float(r[m])-float(l[m]) for m in metrics})
 return {'/'.join(map(str,g)):{m:estimate([r[m] for r in rs]) for m in metrics} for g,rs in d.items()}

for interface in ['bare','chat']:
 names=[f'E22-hu-Qwen2.5-3B{stage}-{interface}' for stage in ['', '-Instruct']]
 values=[load(n,'predictions.jsonl') for n in names]
 if any(r is None for r,c in values):continue
 (l,lc),(r,rc)=values;assert lc['unpadded_input_token_ids_sha256']==rc['unpadded_input_token_ids_sha256']
 def cluster(rows):
  grouped=defaultdict(list)
  for r in rows:grouped[r['phenomenon'],r['item_id']].append(r)
  return [{'phenomenon':p,'item_id':i,'correct':np.mean([r['correct'] for r in rs]),'prob_true_answer':np.mean([r['prob_true_answer'] for r in rs])} for (p,i),rs in grouped.items()]
 assert all(x['readout_prompt_sha256']==y['readout_prompt_sha256'] for x,y in zip(l,r))
 out['hu'][interface]={'n_trials':len(l),'n_items':len(cluster(l)), 'input_sha256':lc['unpadded_input_token_ids_sha256'],
 'instruct_minus_base':paired(cluster(l),cluster(r),['phenomenon','item_id'],['phenomenon'],['correct','prob_true_answer'])}

metrics=['baseline','recognition','cancel_delta','cancel_minus_irrelevant_delta','joint_update','mean_support_mass','support_argmax_fraction']
xpairs={
 'Qwen-bare':(['E22-implicaturex-Qwen2.5-3B-bare'],['E22-implicaturex-Qwen2.5-3B-Instruct-bare']),
 'Qwen-common-chat':(['E22-implicaturex-Qwen2.5-3B-common-chat'],['E21-Qwen2.5-3B-Instruct-shard0of2','E21-Qwen2.5-3B-Instruct-shard1of2']),
 'OLMoE-common-chat':(['E21-OLMoE-1B-7B-0125-shard0of1'],['E21-OLMoE-1B-7B-0125-SFT-shard0of1']),
 'OLMoE-bare':(['E26-implicaturex-OLMoE-1B-7B-0125-bare'],['E26-implicaturex-OLMoE-1B-7B-0125-SFT-bare'])}
allitems={}
for label,(left,right) in xpairs.items():
 merged=[];valid=True
 for ns in [left,right]:
  v=[]
  for name in ns:
   rows,c=load(name,'item-results.jsonl')
   if rows is None:valid=False;break
   v.extend(rows)
  merged.append(v)
 if not valid:continue
 assert all(len(v)==542 for v in merged)
 # Reused E21 and new E22/E26 must have identical readout prompts per candidate.
 for condition in ['parent','format']:
  ps=[]
  for ns in [left,right]:
   preds=[]
   for n in ns:preds += [json.loads(s) for s in (runs/n/(condition+'-predictions.jsonl')).read_text().splitlines()]
   index={(r['item_id'],r['state'],r['true_label']):r['prompt_sha256'] for r in preds}
   assert len(index)==3252;ps.append(index)
  if ps[0]!=ps[1]:
   valid=False
   out.setdefault('input_mismatch',{})[label+'/'+condition]={'n_mismatches':sum(ps[0][k]!=ps[1][k] for k in ps[0]),'interpretation':'Do not attribute paired differences to training stage'}
 if not valid:continue
 out['implicaturex'][label]={'n_items':271,'instruct_or_sft_minus_base':paired(*merged,['item_id','condition'],['condition','phenomenon'],metrics),'prompt_parity':True}
 allitems[label]=merged
out['interface_interactions']={}
for family in ['Qwen','OLMoE']:
 if all(family+'-'+i in allitems for i in ['bare','common-chat']):
  ds=[]
  for interface in ['bare','common-chat']:
   l,r=allitems[family+'-'+interface];ri={(q['item_id'],q['condition']):q for q in r}
   ds.append([{**{k:q[k] for k in ['item_id','condition','phenomenon']},**{m:ri[q['item_id'],q['condition']][m]-q[m] for m in metrics}} for q in l])
  out['interface_interactions'][family]=paired(*ds,['item_id','condition'],['condition','phenomenon'],metrics)
for stage in ['', '-Instruct']:
 name='E26-atomic-Qwen2.5-3B'+stage;rows,c=load(name,'predictions.jsonl')
 if rows is None:continue
 assert len(rows)==1568
 out['epitome'][name]={'source_summary':json.loads((runs/name/'summary.json').read_text()),'support':{cond:{phase:estimate([r['support_mass'] for r in rows if r['condition']==cond and r['phase']==phase]) for phase in ['prior','speach','knowledge','request']} for cond in ['bare','format']}}
for stage in ['', '-Instruct']:
 for interface in ['bare','common-chat']:
  name=f'E26-betting-Qwen2.5-3B{stage}-{interface}';rows,c=load(name,'predictions.jsonl')
  if rows is None:continue
  assert len(rows)==760
  out['betting'][name]=json.loads((runs/name/'summary.json').read_text())
a.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'hu':list(out['hu']),'implicaturex':list(out['implicaturex']),'betting':out['betting'],'pending':out['pending']}))
