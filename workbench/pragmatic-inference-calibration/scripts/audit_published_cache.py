#!/usr/bin/env python3
"""All published open/no-thinking caches; no new metric or model inference."""
import hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from aggregate import estimate
from run_implicaturex import prepare

root=Path('/data1/xiangding/work/pragmatic-inference-calibration')
source,audit=prepare(root);folder=root/'upstream/ImplicatureX-lfs'
files=[p for p in sorted(folder.glob('*.jsonl')) if 'thinking' not in p.name and not p.name.startswith('gpt')]
assert len(files)==19
out={'audit':audit,'models':{},'limits':['Source cached raw probabilities retained, no items deleted.',
     '±epsilon mathematical bounds are sensitivity descriptions, not measured noise or new metrics.',
     'Order disagreement or tiny residuals do not prove lack of underlying pragmatic knowledge.',
     'Pilot for Qwen3-4B was POST-HOC; broader source audit frozen in E24 before other caches measured.']}
lookup={(r['item_id'],r['state'],r['true_label']):r for r in source};items=sorted({r['item_id'] for r in source})
for p in files:
 raw=list(map(json.loads,p.read_text().splitlines()));index={(r['system_prompt'],r['prompt']):r for r in raw}
 assert len(index)==3252 and len(raw)==3252
 probs={key:index[r['system_prompt'],r['prompt']]['option_probs'] for key,r in lookup.items()}
 assert all(np.isfinite(x) and 0<=x<=1 for pr in probs.values() for x in pr.values())
 assert all(pr['True']+pr['False']>0 for pr in probs.values())
 groups=defaultdict(list)
 for item in items:
  original={st:np.mean([probs[item,st,o]['True'] for o in ['1','2']]) for st in ['baseline','cancel','irrelevant','negation','strengthen','prior']}
  repaired={st:np.mean([probs[item,st,o]['True']/(probs[item,st,o]['True']+probs[item,st,o]['False']) for o in ['1','2']]) for st in original}
  false={st:np.mean([probs[item,st,o]['False'] for o in ['1','2']]) for st in original}
  b,c=original['baseline'],original['cancel'];delta=c-b
  b1,b2=[probs[item,'baseline',o]['True'] for o in ['1','2']]
  d={'recognition_source_code':float(b>.5),'recognition_paper_true_gt_false':float(b>false['baseline']),
     'recognition_recomputed_unit_sum':float(repaired['baseline']>.5),
     'cancellation_source_code':float(delta<0),'joint_source_code':float(b>.5 and delta<0),
     'cancellation_recomputed_unit_sum':float(repaired['cancel']<repaired['baseline']),
     'joint_recomputed_unit_sum':float(repaired['baseline']>.5 and repaired['cancel']<repaired['baseline']),
     'baseline_order_gap':abs(b1-b2),'baseline_order_argmax_agree':float((b1>probs[item,'baseline','1']['False'])==(b2>probs[item,'baseline','2']['False'])),
     'baseline_average_margin':abs(b-.5),'cancel_abs_delta':abs(delta),
     'max_raw_pair_sum_deviation':max(abs(probs[item,s,o]['True']+probs[item,s,o]['False']-1) for s in original for o in ['1','2'])}
  for eps in [.001,.01]:
   tag=str(eps)
   d['baseline_margin_le_'+tag]=float(abs(b-.5)<=eps)
   d['cancel_abs_delta_le_'+tag]=float(abs(delta)<=eps)
   d['recognition_lower_'+tag]=float(b>.5+eps);d['recognition_upper_'+tag]=float(b>.5-eps)
   d['cancel_lower_'+tag]=float(delta<-2*eps);d['cancel_upper_'+tag]=float(delta<2*eps)
   d['joint_lower_'+tag]=float(b>.5+eps and delta<-2*eps)
   d['joint_upper_'+tag]=float(b>.5-eps and delta<2*eps)
  groups[lookup[item,'baseline','1']['phenomenon']].append(d)
 out['models'][p.stem]={'n_items':271,'n_cache_entries':3252,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
     'excluded_from_original_main_model_table':p.stem.startswith('mistralai'),
     'conditions':{g:{k:estimate([r[k] for r in rs]) for k in rs[0]} for g,rs in groups.items()}}
path=Path('workbench/pragmatic-inference-calibration/results/E24-published-cache-boundary.json')
path.write_text(json.dumps(out,indent=2)+'\n')
for name,d in out['models'].items():
 m=d['conditions']['naturally_occurring_conversational']
 print(json.dumps({'model':name,'natural_recognition':m['recognition_source_code']['mean'],
  'unit_sum_recomputed_recognition':m['recognition_recomputed_unit_sum']['mean'],
  'near_001':m['baseline_margin_le_0.001']['mean'],'order_agreement':m['baseline_order_argmax_agree']['mean']}))
