#!/usr/bin/env python3
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from aggregate import estimate
from run_multichoice_logprob import SUFFIX
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
original={(r['language'],r['item_id']):r for r in map(json.loads,(a.root/'data/multiprageval.jsonl').read_text().splitlines())}
result={'runs':{},'limits':'Restricted MCQ first-letter probabilities, not generated choice accuracy, language knowledge, or SDT. E anchored as none-of-above; only A-D rotated. Descriptive unadjusted item-cluster CI.'}
for folder in sorted((a.root/'runs').glob('E14-*')):
 cfg=json.loads((folder/'config.json').read_text());assert cfg['complete'] and cfg['numerical_gate_pass']
 rows=list(map(json.loads,(folder/'predictions.jsonl').read_text().splitlines()));assert len(rows)==2400
 summary={}
 for condition in ['native','format']:
  for group in ['maxim','literal']:
   selected=[r for r in rows if r['condition_readout']==condition and (r['phenomenon']=='literal')==(group=='literal')]
   grouped=defaultdict(list)
   for r in selected:grouped[r['item_id']].append(r)
   assert all(len(rs)==4 and set(r['rotation'] for r in rs)==set(range(4)) for rs in grouped.values())
   summary[condition+'_'+group]={'accuracy_rotation_mean':estimate([np.mean([r['correct'] for r in rs]) for rs in grouped.values()]),
    'semantic_argmax_invariance':estimate([len(set(r['prediction'] for r in rs))==1 for rs in grouped.values()]),
    'gold_E_proportion':np.mean([rs[0]['gold']=='E' for rs in grouped.values()]).item(),
    'accuracy_per_rotation':[estimate([r['correct'] for r in selected if r['rotation']==i]) for i in range(4)]}
 name=cfg['model'].split('/')[-1];parity=None
 comparator={'Qwen2.5-3B-Instruct':'E08-qwen25-3b-fp32','Qwen3-4B':'E08-qwen3-4b-fp32'}.get(name)
 if comparator:
  old=list(map(json.loads,(a.root/'runs'/comparator/'predictions.jsonl').read_text().splitlines()))
  old={(r['language'],r['item_id']):r for r in old};delta=[];matches=[]
  tok=AutoTokenizer.from_pretrained(a.root/'models'/name,local_files_only=True)
  for r in rows:
   if r['rotation']!=0:continue
   key=(r['language'],r['item_id']);cond=r['condition_readout'];before=old[key]
   raw=original[key]['prompt']+(SUFFIX if cond=='format' else '')
   assert hashlib.sha256(raw.encode()).hexdigest()==r['prompt_sha256']
   rendered=tok.apply_chat_template([{'role':'user','content':raw}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
   assert hashlib.sha256(rendered.encode()).hexdigest()==before[cond+'_prompt_sha256']
   delta.append(max(abs(r['original_choice_probs'][c]-before[cond+'_letter_probs'][c]) for c in 'ABCDE'))
   matches.append(r['prediction']==before[cond+'_letter_prediction'])
  parity={'n':len(delta),'max_prob_delta':max(delta),'argmax_match_rate':float(np.mean(matches)),'pass':max(delta)<1e-3,'prompt_hashes_match':True}
 result['runs'][folder.name]={'model':cfg['model'],'language':cfg['language'],'summary':summary,'rotation0_E08_parity':parity,
  'config_sha256':hashlib.sha256((folder/'config.json').read_bytes()).hexdigest(),'predictions_sha256':hashlib.sha256((folder/'predictions.jsonl').read_bytes()).hexdigest()}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'runs':len(result['runs']),'readouts':len(result['runs'])*2400,'parity':{k:v['rotation0_E08_parity'] for k,v in result['runs'].items() if v['rotation0_E08_parity']}}))
