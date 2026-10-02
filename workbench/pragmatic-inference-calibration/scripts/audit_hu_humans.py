#!/usr/bin/env python3
"""Native Hu human option distributions, with independent Correct-code check."""
import argparse,ast,csv,hashlib,json,re
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from scipy.spatial.distance import jensenshannon
from aggregate import estimate

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--reuse-norms',action='store_true')
ap.add_argument('--runs',nargs='+',default=['E04-hu-flan-t5-xl','E04-hu-qwen25-3b','E07-hu-qwen3-4b'])
a=ap.parse_args();up=a.root/'upstream/lm-pragmatics';dest=a.root/'data/hu-human-norms.jsonl'
if dest.exists() and not a.reuse_norms:raise FileExistsError(dest)
phs=['CoherenceInference','Deceits','Humour','IndirectSpeech','Irony','Maxims','Metaphor']
norms={};coverage={};mismatches=[];hashes={}
for ph in phs:
 pp=up/f'prompts/{ph}_prompts_seed0_examples0.csv';hp=up/f'human_data/fj/Human_{ph}.csv'
 for p in [pp,hp]:hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 with pp.open(newline='') as f:prompts={r['item_id']:r for r in csv.DictReader(f)}
 with hp.open() as f:rows=list(csv.DictReader(f))
 grouped=defaultdict(Counter);omitted=Counter();people=set()
 for r in rows:
  item=str(int(r['itemNum']));people.add(r['pKey'])
  if item not in prompts:omitted[item]+=1;continue
  p=prompts[item];order=ast.literal_eval(p['randomized_option_order']);labels=ast.literal_eval(p['original_labels_complex'])
  if ph=='CoherenceInference':
   texts={int(k):v.strip() for k,v in re.findall(r'^([12])\) (.+)$',p['prompt'],re.MULTILINE)}
   selected=[order[k-1] for k,v in texts.items() if v==r['OptionChosen']]
   assert len(selected)==1,(ph,item,r)
   original=selected[0]
  else:
   assert re.fullmatch(r'Answer[1-5]',r['OptionChosen']),r
   original=int(r['OptionChosen'][6:])
  assert 1<=original<=len(labels)
  correct=labels[original-1].startswith('Correct')
  if correct!=bool(int(r['Correct'])):mismatches.append({'phenomenon':ph,'item':item,'pKey':r['pKey'],'choice':original,'label':labels[original-1],'published_correct':r['Correct']})
  grouped[item][original]+=1
 for item,p in prompts.items():
  counts=grouped[item];assert sum(counts.values())>0
  labels=ast.literal_eval(p['original_labels_complex']);n=sum(counts.values());gold=[i+1 for i,l in enumerate(labels) if l.startswith('Correct')]
  assert len(gold)==1
  distribution=[counts[i+1]/n for i in range(len(labels))]
  maxima=[i+1 for i,v in enumerate(distribution) if v==max(distribution)]
  norms[ph,item]={'phenomenon':ph,'item_id':item,'n_human':n,'option_labels':labels,'distribution':distribution,'gold_original_option':gold[0],
   'gold_endorsement':distribution[gold[0]-1],'human_modal_options':maxima,'modal_includes_gold':gold[0] in maxima}
 coverage[ph]={'human_rows':len(rows),'participants':len(people),'included_items':len(prompts),'omitted_items_rows':dict(omitted),
  'gold_endorsement':estimate([norms[ph,i]['gold_endorsement'] for i in prompts]),'modal_gold_conflicts':sum(not norms[ph,i]['modal_includes_gold'] for i in prompts)}
result={'coverage':coverage,'source_hashes':hashes,'correct_code_mismatches':len(mismatches),'mismatch_examples':mismatches[:10],
 'status':'VALID_CODING' if not mismatches else 'FAILED_CODING: no downstream model comparison','models':{},
 'limits':'human confidence is graded; no unlicensed condition; not SDT; model conditional MCQ probs are not repeated human choices; observational descriptive instrument'}
if not mismatches:
 if dest.exists():
  assert [json.loads(s) for s in dest.read_text().splitlines()]==list(norms.values()),'Existing norms do not match pinned source'
 else:dest.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in norms.values()))
 for name in a.runs:
  run=a.root/'runs'/name;rows=[json.loads(s) for s in (run/'predictions.jsonl').read_text().splitlines()]
  groups=defaultdict(list)
  for r in rows:
   if r['condition']=='original':groups[r['phenomenon'],r['item_id']].append(r)
  comparisons=defaultdict(list)
  for key,rs in groups.items():
   assert len(rs)==5
   ph,item=key;h=norms[key];probs=[];choices=[]
   for r in rs:
    seed=r['seed'];p=up/f'prompts/{ph}_prompts_seed{seed}_examples0.csv'
    with p.open(newline='') as f:raw=next(x for x in csv.DictReader(f) if x['item_id']==item)
    labels=ast.literal_eval(raw['original_labels_complex']);assert labels==h['option_labels']
    order=ast.literal_eval(raw['randomized_option_order']);pr=np.zeros(len(order))
    for k,original in enumerate(order):pr[original-1]=r['choice_probs'][str(k+1)]
    assert abs(pr.sum()-1)<1e-5
    probs.append(pr);choices.append(order[int(r['prediction'])-1])
   mean=np.mean(probs,axis=0);human=np.array(h['distribution'])
   comparisons[ph].append({'js_divergence_bits':float(jensenshannon(mean,human,base=2)**2),
    'human_modal_agreement':float((int(mean.argmax())+1) in h['human_modal_options']),
    'gold_endorsement_human':h['gold_endorsement'],'gold_prob_model':float(mean[h['gold_original_option']-1]),
    'gold_argmax_model':np.mean([c==h['gold_original_option'] for c in choices]).item()})
  result['models'][name]={ph:{k:estimate([r[k] for r in rs]) for k in rs[0]} for ph,rs in comparisons.items()}
a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'mismatches':len(mismatches),'n_items':len(norms),'coverage':coverage},ensure_ascii=False))
