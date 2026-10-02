#!/usr/bin/env python3
"""E29 fixed complete source knowledge items, polarity and source parity checks."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from aggregate import estimate
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
out={'models':{},'pending':[],'limits':['Knowledge norm is the parent task convention, not universal mind-reading gold.','CI clusters are 40 stimulus items, not 360 independent contexts.','Role and ablation manipulations change linguistic evidence, not neural mechanism.','No licensed/unlicensed inference label or SDT.']}
def grouped(rows,keys,metrics):
 groups=defaultdict(list)
 for r in rows:groups[tuple(r[k] for k in keys)].append(r)
 result={}
 for g,rs in groups.items():
  byitem=defaultdict(list)
  for r in rs:byitem[r['item']].append(r)
  result['/'.join(map(str,g))]={m:estimate([np.mean([r[m] for r in irs]) for irs in byitem.values()]) for m in metrics}
 return result
for cp in ['Qwen3-8B','Qwen3-14B']:
 paths = [a.root/'runs'/f'E31-knowledge-{cp}-{v}' for v in ['parent','role','access-only','negative']]
 configs = [json.loads((p/'config.json').read_text()) for p in paths]
 assert all(c['complete'] and c['numerical_gate_pass'] for c in configs)
 assert len({c['model'] for c in configs}) == 1 and len({c['revision'] for c in configs}) == 1
 for p in paths:
  rs=[json.loads(l) for l in (p/'predictions.jsonl').read_text().splitlines()]
  assert len(rs)==720 and len({r['variant'] for r in rs})==1
 p=paths[0]
 if not (p/'config.json').exists():out['pending'].append(p.name);continue
 c=json.loads((p/'config.json').read_text());assert c['complete'] and c['numerical_gate_pass']
 rows=[json.loads(l) for shard in paths for l in (shard/'predictions.jsonl').read_text().splitlines()];assert len(rows)==2880
 idx={(r['key'],r['interface'],r['variant']):r for r in rows};assert len(idx)==len(rows)
 paired=[]
 for r in rows:
  if r['variant']=='parent':
   neg=idx[r['key'],r['interface'],'negative']
   for v in ['role','access-only','negative']:
    nr=idx[r['key'],r['interface'],v]
    paired.append({**r,'variant':v,'norm_probability_delta':nr['parent_norm_probability']-r['parent_norm_probability'],'correct_delta':float(nr['correct'])-float(r['correct']),'support_mass_delta':nr['support_mass']-r['support_mass'],'polarity_agreement':float((r['yes_prob']>.5)!=(neg['yes_prob']>.5)),'polarity_complement_gap':r['yes_prob']+neg['yes_prob']-1})
 parity={}
 cp=cp
 old='E26-atomic-'+cp if cp in ['Qwen2.5-3B','Qwen2.5-3B-Instruct'] else 'E27-atomic-'+cp if cp.startswith('OLMoE') else None
 if old:
  prior=[json.loads(l) for l in (a.root/'runs'/old/'predictions.jsonl').read_text().splitlines()]
  for interface,condition in [('bare','bare'),('common-chat','format')]:
   oi={r['key']:r for r in prior if r['phase']=='knowledge' and r['condition']==condition};assert len(oi)==360
   deltas=[]
   for key,r in oi.items():
    now=idx[key,interface,'parent'];assert now['readout_prompt_sha256']==r['readout_prompt_sha256']
    deltas.append(abs(now['yes_prob']-r['choice_probs']['Yes']))
   parity[interface]={'old_run':old,'n':len(deltas),'max_probability_delta':max(deltas),'pass':max(deltas)<.001}
   parity[interface]['quarantined'] = not parity[interface]['pass']
   parity[interface]['n_over_gate'] = sum(x >= .001 for x in deltas)
 out['models'][c['model']]={'runs':[q.name for q in paths], 'config_hashes':[hashlib.sha256((q/'config.json').read_bytes()).hexdigest() for q in paths], 'input_token_hashes':{k:v for c0 in configs for k,v in c0['input_token_hashes'].items()},'config_sha256':hashlib.sha256((p/'config.json').read_bytes()).hexdigest(),'original_readout_parity':parity,'description':grouped(rows,['interface','variant','experiment','access','n'],['parent_norm_probability','correct','support_mass']), 'paired_changes':grouped(paired,['interface','variant','experiment','access','n'],['norm_probability_delta','correct_delta','support_mass_delta','polarity_agreement','polarity_complement_gap']), 'collapsed':grouped(rows,['interface','variant','access'],['parent_norm_probability','correct','support_mass']), 'collapsed_paired_changes':grouped(paired,['interface','variant','access'],['norm_probability_delta','correct_delta','polarity_agreement','polarity_complement_gap'])}
prior=json.loads((Path(__file__).resolve().parents[1]/'results/E29-knowledge-controls-complete-summary.json').read_text())
small=a.root/'runs/E29-r2-knowledge-Qwen3-4B'
smallc=json.loads((small/'config.json').read_text())
smallrows=[json.loads(l) for l in (small/'predictions.jsonl').read_text().splitlines()]
smallidx={(r['key'],r['interface'],r['variant']):r for r in smallrows}
checks={}
for model,z in out['models'].items():
 assert z['input_token_hashes']==smallc['input_token_hashes']
 bigrows=[json.loads(l) for run in z['runs'] for l in (a.root/'runs'/run/'predictions.jsonl').read_text().splitlines()]
 assert all(r['readout_prompt_sha256']==smallidx[r['key'],r['interface'],r['variant']]['readout_prompt_sha256'] for r in bigrows)
 checks[model]={'same_prompt_sha_all_2880':True,'same_input_token_hashes_all_8_conditions':True}
out['cross_size_input_parity']=checks
out['models']['Qwen/Qwen3-4B']=prior['models']['Qwen/Qwen3-4B']
a.output.write_text(json.dumps(out,indent=2)+'\n')
for model,v in out['models'].items():
 for interface in ['bare','common-chat']:
  print(model,interface,'full-access',{variant:v['collapsed'][interface+'/'+variant+'/3']['parent_norm_probability'] for variant in ['parent','role','access-only','negative']},'polarity-agreement',v['collapsed_paired_changes'][interface+'/negative/3']['polarity_agreement'])
print('pending',out['pending'])
