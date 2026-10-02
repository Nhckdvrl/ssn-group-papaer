#!/usr/bin/env python3
"""Complete-item joins, source-cache audit and original human norms."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from aggregate import estimate
from run_implicaturex import prepare

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();source,audit=prepare(a.root);cache=a.root/'upstream/ImplicatureX-lfs'
lookup={(r['item_id'],r['state'],r['true_label']):r for r in source}
out={'audit':audit,'models':{},'incomplete':[],'published_cache':{},'human':{},'protocol_audit':{},
     'limits':['Item CIs are not independent human/training-seed uncertainty.',
               'Approx lacks human norms and is not automatically a valid unlicensed condition.',
               'Source-cache parity and published Table6-8 parity are separate contracts.']}
cached={}
for name,file in [('Qwen3-4B','Qwen_Qwen3-4B.jsonl'),('Qwen2.5-3B-Instruct','Qwen_Qwen2.5-3B-Instruct.jsonl')]:
 p=cache/file
 if not p.exists():continue
 rows=list(map(json.loads,p.read_text().splitlines()));keys=[(r['system_prompt'],r['prompt']) for r in rows]
 assert len(set(keys))==len(rows), 'Do not silently choose duplicate cache entries'
 indexed=dict(zip(keys,rows));mapped={}
 for key,r in lookup.items():
  c=indexed[r['system_prompt'],r['prompt']];mapped[key]=float(c['option_probs']['True'])
 cached[name]=mapped;groups=defaultdict(list)
 for item in sorted({r['item_id'] for r in source}):
  r=lookup[item,'baseline','1'];b=np.mean([mapped[item,'baseline',o] for o in ['1','2']]);c=np.mean([mapped[item,'cancel',o] for o in ['1','2']])
  groups[r['phenomenon']].append({'recognition':float(b>.5),'cancellation':float(c<b),'joint_update':float(b>.5 and c<b)})
 out['published_cache'][name]={'n':len(rows),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
   'metrics':{g:{k:estimate([r[k] for r in rs]) for k in rs[0]} for g,rs in groups.items()}}
folders=defaultdict(list)
for p in (a.root/'runs').glob('E21-*/config.json'):
 cfg=json.loads(p.read_text())
 if cfg.get('complete'):folders[cfg['model'].split('/')[-1]].append(p.parent)
 else:out['incomplete'].append(p.parent.name)
for name,ps in sorted(folders.items()):
 details=[r for p in ps for r in map(json.loads,(p/'item-results.jsonl').read_text().splitlines())]
 if len(details)!=542:out['incomplete'].append(name);continue
 assert len({(r['item_id'],r['condition']) for r in details})==542
 groups=defaultdict(list)
 for r in details:groups[r['condition'],r['phenomenon']].append(r)
 summary={}
 for (condition,phen),rs in groups.items():
  summary.setdefault(condition,{})[phen]={k:estimate([r[k] for r in rs]) for k in rs[0] if k not in ['item_id','condition','phenomenon']}
 paired={}
 index={(r['item_id'],r['condition']):r for r in details}
 for phen in audit['counts']:
  items=[r['item_id'] for r in details if r['condition']=='parent' and r['phenomenon']==phen]
  paired[phen]={k:estimate([index[item,'format'][k]-index[item,'parent'][k] for item in items])
                for k in ['recognition','joint_update','cancel_delta','cancel_minus_irrelevant_delta']}
 parity=None
 if name in cached:
  predictions=[r for p in ps for r in map(json.loads,(p/'parent-predictions.jsonl').read_text().splitlines())]
  assert len(predictions)==3252
  differences=[abs(r['p_true']-cached[name][r['item_id'],r['state'],r['true_label']]) for r in predictions]
  parity={'n':len(differences),'mean_absolute_probability_delta':float(np.mean(differences)),
          'max_absolute_probability_delta':float(max(differences))}
 out['models'][name]={'summary':summary,'paired_format_minus_parent':paired,'cache_parity':parity,
                     'n_items':271,'n_predictions':6504,'runs':[p.name for p in ps]}
hp=cache/'prolific_responses.csv'
if hp.exists():
 df=pd.read_csv(hp,skiprows=int(hp.read_bytes().startswith(b'#')))
 assert set(df.item_id)=={r['item_id'] for r in source}
 z=df.groupby('workerid').likelihood.transform(lambda x:(x-x.mean())/x.std())
 assert z.notna().all(), 'Original z-score is undefined; no silent deletion'
 df['z']=z
 by=df.groupby(['item_id','contains_cancellation']).z.mean().unstack()
 types={r['item_id']:r['phenomenon'] for r in source};groups=defaultdict(list)
 for item,r in by.iterrows():
  b,c=float(r[False]),float(r[True]);groups[types[item]].append({'recognition':float(b>0),'cancellation':float(c<b),'joint_update':float(b>0 and c<b)})
 out['human']={'n_responses':len(df),'n_retained_workers':df.workerid.nunique(),'n_items':len(by),
               'source_is_already_attention_filtered':True,'sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),
               'responses_per_item_condition_range':[int(df.groupby(['item_id','contains_cancellation']).size().min()),int(df.groupby(['item_id','contains_cancellation']).size().max())],
               'metrics':{g:{k:estimate([r[k] for r in rs]) for k in rs[0]} for g,rs in groups.items()}}
for dtype in ['float32','bfloat16']:
 p=a.root/'runs'/('E23-Qwen3-4B-'+dtype)
 if not (p/'summary.json').exists():continue
 rows=list(map(json.loads,(p/'predictions.jsonl').read_text().splitlines()));audit=json.loads((p/'summary.json').read_text())
 if 'Qwen3-4B' in cached:
  audit['cache_probe_delta_by_prefix']={str(prefix):{'mean':float(np.mean([abs(r['p_true_full_forward']-cached['Qwen3-4B'][r['item_id'],r['state'],r['true_label']]) for r in rows if r['enable_thinking_prefix']==prefix])),
  'max':max(abs(r['p_true_full_forward']-cached['Qwen3-4B'][r['item_id'],r['state'],r['true_label']]) for r in rows if r['enable_thinking_prefix']==prefix)} for prefix in [False,True]}
 out['protocol_audit'][dtype]=audit
a.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'models':list(out['models']),'incomplete':out['incomplete'],'human_n':out['human'].get('n_responses'),
                  'cache':{n:v['cache_parity'] for n,v in out['models'].items()},
                  'protocol':{n:v.get('cache_probe_delta_by_prefix') for n,v in out['protocol_audit'].items()}}))
