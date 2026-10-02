#!/usr/bin/env python3
"""Keep abs(E[X]-target) distinct from E[abs(X-target)] and invalid bounds."""
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance,pearsonr
from aggregate import estimate
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
stimuli={r['item_id']:r for r in map(json.loads,(a.root/'data/wavelength.jsonl').read_text().splitlines())}
parent={'Qwen2.5-3B-Instruct':'E03-wavelength-qwen25-3b-fp32','Qwen3-4B':'E03-wavelength-qwen3-4b-fp32','Qwen1.5-14B-Chat':'E15-wavelength-Qwen1.5-14B-Chat'}
out={'models':{},'incomplete':[],'bootstrap':'2000 pair-cluster draws seed0, sampling seeds averaged within each item; human uncertainty is not single-model decoding variance.',
 'limits':'Mean-prediction MAE and sample-draw MAE measure different quantities. Conditional valid distributions exclude invalid only with explicit rates and unconditional bounds. Invalid values bounded on the task 0–100 range.'}
for folder in sorted((a.root/'runs').glob('E17-wavelength-*')):
 cfg=json.loads((folder/'config.json').read_text())
 if not cfg.get('complete'):out['incomplete'].append(folder.name);continue
 rows=list(map(json.loads,(folder/'predictions.jsonl').read_text().splitlines()));assert len(rows)==3200
 name=cfg['model'].split('/')[-1];pr={r['item_id']:r for r in map(json.loads,(a.root/'runs'/parent[name]/'predictions.jsonl').read_text().splitlines())}
 groups=defaultdict(list)
 for r in rows:groups[r['item_id']].append(r)
 pairs=defaultdict(list);details=[]
 for item,rs in groups.items():
  assert len(rs)==32 and set(r['seed'] for r in rs)==set(range(32))
  valid=[r['prediction'] for r in rs if not r['invalid']];s=stimuli[item]['source'];target=float(s['target']);human=stimuli[item].get('human_distribution')
  # Parent records retain human mean; probabilities needed only for mean alignment here.
  p=pr[item];n_invalid=32-len(valid);lo=sum(valid)/32;hi=(sum(valid)+100*n_invalid)/32
  lower=0 if lo<=target<=hi else min(abs(lo-target),abs(hi-target));upper=max(abs(lo-target),abs(hi-target))
  conditional_mean=float(np.mean(valid)) if valid else None
  d={'item_id':item,'invalid_fraction':n_invalid/32,'truncated_fraction':sum(r['truncated'] for r in rs)/32,
   'mean_prediction_mae_lower':lower,'mean_prediction_mae_upper':upper,
   'mean_prediction_mae_valid_conditional':abs(conditional_mean-target) if valid else None,
   'sample_draw_mae_lower':sum(abs(x-target) for x in valid)/32,
   'sample_draw_mae_upper':(sum(abs(x-target) for x in valid)+100*n_invalid)/32,
   'parent_likelihood_mean_mae':p['paper_absolute_error'],
   'sampling_minus_parent_mean_mae':abs(conditional_mean-target)-p['paper_absolute_error'] if valid else None,
   'sampling_mean':conditional_mean,'human_mean':p['human_mean']}
  details.append(d);pairs[s['left'],s['right']].append(d)
 keys=[k for k in details[0] if k not in ['item_id','sampling_mean','human_mean']]
 metrics={k:estimate([np.mean([r[k] for r in rs]) for rs in pairs.values()]) for k in keys if all(d[k] is not None for d in details)}
 out['models'][folder.name]={'metrics':metrics,'n_pairs':len(pairs),'n_items':len(details),'n_answers':len(rows),'invalid_answers':sum(r['invalid'] for r in rows),
  'pearson_sampling_human_mean':float(pearsonr([d['sampling_mean'] for d in details],[d['human_mean'] for d in details]).statistic) if all(d['sampling_mean'] is not None for d in details) else None,
  'config_sha256':hashlib.sha256((folder/'config.json').read_bytes()).hexdigest(),'predictions_sha256':hashlib.sha256((folder/'predictions.jsonl').read_bytes()).hexdigest()}
a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
