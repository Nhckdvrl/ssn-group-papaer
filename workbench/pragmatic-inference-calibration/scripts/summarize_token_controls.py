#!/usr/bin/env python3
"""E27 matched stages after actual token parity, with item-cluster intervals."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from aggregate import estimate
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
assert not a.output.exists()
runs=a.root/'runs';stages=['OLMoE-1B-7B-0125','OLMoE-1B-7B-0125-SFT','OLMoE-1B-7B-0125-DPO']
out={'implicaturex':{},'hu':{},'atomic':{},'betting':{},'limits':['No training-seed uncertainty in item-cluster CIs.','Common SFT tokenizer controls token identity; base prefix familiarity remains different.','Bare and BOS sensitivity reported, not selected by outcome.','Approx is not human-normed unlicensed gold; no FPR or SDT.']}
def load(name,file='predictions.jsonl'):
 p=runs/name;c=json.loads((p/'config.json').read_text());assert c['complete'] and c['numerical_gate_pass'],name
 return [json.loads(l) for l in (p/file).read_text().splitlines()],c

def compare(ls,rs,keys,group,metrics):
 li={tuple(r[k] for k in keys):r for r in ls};ri={tuple(r[k] for k in keys):r for r in rs};assert len(li)==len(ls) and len(ri)==len(rs) and li.keys()==ri.keys()
 groups=defaultdict(list)
 for k,l in li.items():
  r=ri[k];assert all(l[g]==r[g] for g in group)
  groups[tuple(l[g] for g in group)].append({m:float(r[m])-float(l[m]) for m in metrics})
 return {'/'.join(map(str,g)):{m:estimate([r[m] for r in rows]) for m in metrics} for g,rows in groups.items()}

def descriptions(rows,group,metrics):
 groups=defaultdict(list)
 for r in rows:groups[tuple(r[k] for k in group)].append(r)
 return {'/'.join(map(str,g)):{m:estimate([r[m] for r in rs]) for m in metrics} for g,rs in groups.items()}
metrics=['baseline','recognition','cancel_delta','cancel_minus_irrelevant_delta','joint_update','mean_support_mass','support_argmax_fraction','max_order_ptrue_difference']
for interface in ['bare','bos50279','bos0']:
 names=[]
 for s in stages:
  if interface=='bare':names.append(('E27-implicaturex-bare-' if s.endswith('DPO') else 'E26-implicaturex-')+s+('' if s.endswith('DPO') else '-bare'))
  else:names.append('E27-implicaturex-'+s+'-'+interface)
 values=[load(n,'item-results.jsonl') for n in names];hashes=[c['input_token_hashes'] for rows,c in values];assert hashes[0]==hashes[1]==hashes[2],names
 assert all(len(rows)==542 for rows,c in values)
 for cond in ['parent','format']:
  preds=[load(n,cond+'-predictions.jsonl')[0] for n in names]
  indexes=[{(r['item_id'],r['state'],r['true_label']):r['prompt_sha256'] for r in rs} for rs in preds]
  assert indexes[0]==indexes[1]==indexes[2] and len(indexes[0])==3252
 out['implicaturex'][interface]={'runs':names,'input_token_hashes':hashes[0],'n_items':271,'description':{s:descriptions(rs,['condition','phenomenon'],metrics) for s,(rs,c) in zip(stages,values)},'sft_minus_base':compare(values[0][0],values[1][0],['item_id','condition'],['condition','phenomenon'],metrics),'dpo_minus_sft':compare(values[1][0],values[2][0],['item_id','condition'],['condition','phenomenon'],metrics)}

def hu_cluster(rows):
 groups=defaultdict(list)
 for r in rows:groups[r['phenomenon'],r['item_id']].append(r)
 return [dict(phenomenon=p,item_id=i,correct=np.mean([r['correct'] for r in rs]),prob_true_answer=np.mean([r['prob_true_answer'] for r in rs])) for (p,i),rs in groups.items()]
for interface in ['bare','chat']:
 names=['E27-hu-'+interface+'-'+s if interface=='chat' or s.endswith('DPO') else 'E12-'+s for s in stages]
 # Locate original E12 bare runs by their immutable completed metadata.
 if interface=='bare':
  for i,s in enumerate(stages[:2]):
   candidates=[]
   for p in runs.glob('E12-*'):
    if (p/'config.json').exists():
     c=json.loads((p/'config.json').read_text())
     if c.get('model')=='allenai/'+s and c.get('task')=='hu' and c.get('complete') and c.get('hu_readout','bare')=='bare':candidates.append(p.name)
   assert len(candidates)==1,(s,candidates);names[i]=candidates[0]
 values=[load(n) for n in names];hashes=[c['unpadded_input_token_ids_sha256'] for rs,c in values];assert hashes[0]==hashes[1]==hashes[2]
 cl=[hu_cluster(rs) for rs,c in values]
 out['hu'][interface]={'runs':names,'n_trials':1365,'input_sha256':hashes[0],'description':{s:descriptions(rows,['phenomenon'],['correct','prob_true_answer']) for s,rows in zip(stages,cl)},'sft_minus_base':compare(cl[0],cl[1],['phenomenon','item_id'],['phenomenon'],['correct','prob_true_answer']),'dpo_minus_sft':compare(cl[1],cl[2],['phenomenon','item_id'],['phenomenon'],['correct','prob_true_answer'])}
for s in stages:
 p=runs/('E27-atomic-'+s);rs,c=load(p.name);out['atomic'][s]={'summary':json.loads((p/'summary.json').read_text()),'input_token_hashes':c['input_token_hashes']}
 p=runs/('E27-betting-'+s);rs,c=load(p.name);out['betting'][s]=json.loads((p/'summary.json').read_text())
assert len({json.dumps(v['input_token_hashes'],sort_keys=True) for v in out['atomic'].values()})==1
out['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();a.output.write_text(json.dumps(out,indent=2)+'\n')
for interface,v in out['implicaturex'].items():
 for group in ['parent/scalar','parent/naturally_occurring_conversational']:
  for contrast in ['sft_minus_base','dpo_minus_sft']:
   print(interface,group,contrast,{m:v[contrast][group][m] for m in ['baseline','cancel_minus_irrelevant_delta']})
print('betting:',{s:{k:v for k,v in vals.items() if k in ['n','valid','invalid']} for s,vals in out['betting'].items()})
