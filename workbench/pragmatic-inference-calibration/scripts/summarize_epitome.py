#!/usr/bin/env python3
"""Join fixed E19/E20 items, retain missing pairs and unconditional bounds."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from epitome_data import prepare, original_accuracy
from aggregate import estimate

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();_,trials,audit=prepare(a.root)
out={'source_audit':audit,'atomic':{},'betting':{},'incomplete':[],
 'limits':['No binary warranted/unwarranted assignment or SDT.',
           'Native betting changes instruction/warmup/generation/chat jointly; comparisons are boundaries, not isolated causal effects.',
           'Invalid bets are not pragmatic errors. Conditional valid metrics and full-denominator bounds are separate.',
           '40 item bootstrap2000 seed0; trials/conditions of a shared item are not independent people.']}
atomic_paths={}
for p in sorted((a.root/'runs').glob('E19-*/config.json')):
 cfg=json.loads(p.read_text())
 if not cfg.get('complete') or not cfg.get('numerical_gate_pass'):continue
 name=cfg['model'].split('/')[-1];assert name not in atomic_paths
 atomic_paths[name]=p.parent;summary=json.loads((p.parent/'summary.json').read_text())
 pairs={}
 by_condition={c:{(r['item'],r['experiment'],r['access'],r['n']):r for r in map(json.loads,(p.parent/(c+'-si-trials.jsonl')).read_text().splitlines())} for c in ['bare','format']}
 groups=defaultdict(list)
 for key,b in by_condition['bare'].items():
  f=by_condition['format'][key];g=f"E{b['experiment']}:a{b['access']}:n{b['n']}"
  groups[g].append({k:f[k]-b[k] for k in ['parent_rounded_accuracy','delta_p2','delta_p3','knowledge_correct_prob']})
 for g,rs in groups.items():pairs[g]={k:estimate([r[k] for r in rs]) for k in rs[0]}
 out['atomic'][name]={'summary':summary,'paired_format_minus_bare':pairs,
                     'config_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
folders=defaultdict(list)
for p in sorted((a.root/'runs').glob('E20-*/config.json')):
 cfg=json.loads(p.read_text())
 if not cfg.get('complete'):out['incomplete'].append(p.parent.name);continue
 folders[cfg['model'].split('/')[-1]].append(p.parent)
for name,ps in folders.items():
 rows=[r for p in ps for r in map(json.loads,(p/'predictions.jsonl').read_text().splitlines())]
 if len(rows)!=760:out['incomplete'].append(name);continue
 assert len({r['key'] for r in rows})==760 and {r['item'] for r in rows}==set(range(1,41))
 lookup={r['key']:r for r in rows};details=[];groups=defaultdict(list)
 for t in trials.to_dict('records'):
  item=int(t['item']);exp=int(t['experiment']);access=int(t['access']);n=str(t['n']);suffix=f':{exp}:{access}:{n}'
  prior=lookup[f'si:{item}:prior'];post=lookup[f'si:{item}:speach'+suffix];knowledge=lookup[f'si:{item}:knowledge'+suffix]
  valid=prior['valid'] and post['valid']
  d2=post['bets'][2]-prior['bets'][2] if valid else None
  d3=post['bets'][3]-prior['bets'][3] if valid else None
  correct=float(original_accuracy(exp,access,n,d2,d3)) if valid else None
  rec={'item':item,'experiment':exp,'access':access,'n':n,'paired_valid':valid,
       'parent_accuracy_valid_conditional':correct,'accuracy_lower':correct if valid else 0.,'accuracy_upper':correct if valid else 1.,
       'delta_p2_valid_conditional':d2/100 if valid else None,'delta_p3_valid_conditional':d3/100 if valid else None,
       'knowledge_correct_bet':knowledge['bets'][0 if access==3 else 1]/100 if knowledge['valid'] else None}
  details.append(rec);groups[f'E{exp}:a{access}:n{n}'].append(rec)
 stats={}
 for g,rs in groups.items():
  stats[g]={'paired_valid_n':sum(r['paired_valid'] for r in rs),'n':len(rs)}
  for k in ['accuracy_lower','accuracy_upper','parent_accuracy_valid_conditional','delta_p2_valid_conditional','delta_p3_valid_conditional','knowledge_correct_bet']:
   values=[r[k] for r in rs if r[k] is not None]
   stats[g][k]=estimate(values) if values else None
 valid_by_item=defaultdict(list)
 for r in rows:valid_by_item[r['item']].append(float(r['valid']))
 out['betting'][name]={'n':len(rows),'valid':sum(r['valid'] for r in rows),'invalid':sum(not r['valid'] for r in rows),
                      'truncated':sum(r['truncated'] for r in rows),'valid_fraction_item_cluster':estimate([np.mean(x) for x in valid_by_item.values()]),
                      'conditions':stats,'runs':[p.name for p in ps]}
a.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'atomic_models':list(out['atomic']),'betting':{k:{c:v[c] for c in ['n','valid','invalid','truncated']} for k,v in out['betting'].items()},'incomplete':out['incomplete']}))
