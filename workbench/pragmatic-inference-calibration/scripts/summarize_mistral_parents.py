"""E35: immutable complete-sequence checks and within-family stage descriptions."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from transformers import AutoTokenizer
from mistral_readout import prepare,fingerprint
from aggregate import estimate
from circa_pair_data import prepare as circa_prepare
from summarize_boundary_controls import stats,describe

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists()
models={};paired=defaultdict(list);vals={}
tok=AutoTokenizer.from_pretrained(a.root/'models/Mistral-7B-Instruct-v0.3',local_files_only=True)
plans={task:prepare(a.root,tok,task) for task in ['hu-bare','hu-chat','circa','implicaturex']}
_,pairs,audit=circa_prepare(a.root)
for cp in ['Mistral-7B-v0.3','Mistral-7B-Instruct-v0.3']:
 out={'configs':{},'hu':{},'circa':{},'implicaturex':{}};values={}
 for task,expected in plans.items():
  path=a.root/'runs'/f'E35-{task}-{cp}';c=json.loads((path/'config.json').read_text())
  assert c['complete'] and c['numerical_gate_pass'] and c['input_token_hash']==fingerprint(expected) and c['n']==len(expected)
  controls=json.loads((path/'numerical-control.json').read_text());assert all(z['pass'] for z in controls)
  raw=[json.loads(l) for l in (path/'predictions.jsonl').read_text().splitlines()];assert len(raw)==len(expected)
  out['configs'][task]={'run':path.name,'config_sha256':hashlib.sha256((path/'config.json').read_bytes()).hexdigest(),
                       'n':len(raw),'input_token_hash':c['input_token_hash'],'numerical_controls':controls}
  for z,r in zip(raw,expected):
   assert z['full_choice_ids']==r['plan']['full_choice_ids'] and z['prompt_sha256']==r['plan']['prompt_sha256']
   assert all(z[k]==v for k,v in r['source'].items() if k not in ['prompt','system_prompt'])
   assert abs(sum(z['numeric_choice_probs'].values())-1)<1e-5
  if task.startswith('hu'):
   g=defaultdict(list)
   for z in raw:g[z['phenomenon'],z['item_id']].append(z)
   collapsed={k:{m:float(np.mean([z[m] for z in rs])) for m in ['correct','prob_true_answer','support_mass','conditional_candidate_mass']} for k,rs in g.items()}
   groups=defaultdict(list)
   for (ph,item),d in collapsed.items():groups[ph].append(d)
   out['hu'][task]={ph:describe(ds) for ph,ds in groups.items()};values[task]=collapsed
  elif task=='circa':
   idx={(z['id'],z['interface'],z['condition'],z['order']):z for z in raw};assert len(idx)==len(raw)
   out['circa']=stats(idx,pairs,['bare','common-chat'],['original','strict'])
   v={}
   for p in pairs:
    for interface in ['bare','common-chat']:
     for cond in ['original','strict']:
      for order in [0,1]:
       x=idx[p['left_id'],interface,cond,order]['choice_probs'];y=idx[p['right_id'],interface,cond,order]['choice_probs']
       strong,weak=p['left_label'],p['right_label']
       v[interface,cond,order,p['contrast'],p['question_group']]={'strong_correct':float(max(x,key=x.get)==strong),
          'weak_correct':float(max(y,key=y.get)==weak),'weak_as_strong_error':float(max(y,key=y.get)==strong),
          'strong_gold_probability':x[strong],'weak_gold_probability':y[weak],
          'paired_relative_weak_probability_delta':y[weak]/(y[weak]+y[strong])-x[weak]/(x[weak]+x[strong])}
   values[task]=v
  else:
   idx={(z['condition'],z['item_id'],z['state'],z['true_label']):z for z in raw};assert len(idx)==len(raw)
   v={};groups=defaultdict(list)
   for cond in ['parent','format']:
    for item in sorted({z['item_id'] for z in raw}):
     states={s:float(np.mean([idx[cond,item,s,o]['p_true'] for o in ['1','2']])) for s in ['baseline','prior','cancel','irrelevant','negation','strengthen']}
     rs=[idx[cond,item,s,o] for s in states for o in ['1','2']];ph=rs[0]['phenomenon'];base=states['baseline'];delta=states['cancel']-base
     d={**states,'recognition':float(base>.5),'cancellation_recognition':float(delta<0),'joint_update':float(base>.5 and delta<0),
        'strengthen_recognition':float(states['strengthen']>base),'irrelevant_argmax_preserved':float((states['irrelevant']>.5)==(base>.5)),
        'cancel_delta':delta,'irrelevant_delta':states['irrelevant']-base,'cancel_minus_irrelevant_delta':states['cancel']-states['irrelevant'],
        'cancel_numerical_boundary':float(abs(delta)<=.001),'mean_support_mass':float(np.mean([z['support_mass'] for z in rs])),
        'mean_conditional_candidate_mass':float(np.mean([z['conditional_candidate_mass'] for z in rs])),
        'max_order_ptrue_difference':max(abs(idx[cond,item,s,'1']['p_true']-idx[cond,item,s,'2']['p_true']) for s in states)}
     v[cond,ph,item]=d;groups[cond+'/'+ph].append(d)
   out['implicaturex']={g:describe(ds) for g,ds in groups.items()};values[task]=v
 models[cp]=out;vals[cp]=values
left,right=vals.values();changes={}
for task,vs in left.items():
 assert vs.keys()==right[task].keys();groups=defaultdict(list)
 for key,d in vs.items():
  g=key[0] if task.startswith('hu') else '/'.join(map(str,key[:-1]))
  groups[g].append({m:right[task][key][m]-v for m,v in d.items()})
 changes[task]={g:describe(ds) for g,ds in groups.items()}
out={'models':models,'instruct_minus_base':changes,'source_circa_audit':audit,'within_family_actual_full_input_ids_equal':True,
     'limits':['Original numeric content likelihood, common generated space factored out with independent full teacher-forced checks.',
               'Bare BOS1 and native Mistral template differ from older no-BOS families; no causal cross-family absolute comparisons.',
               'One Base/Instruct pair does not identify RLHF or population-level training effects.',
               'Source CIRCA natural answer contrasts are not one-variable causal inference-license manipulations.',
               'ImplicatureX Approx has no human norm; no global false-alarm rate or SDT.',
               'Confidence intervals describe item/question sampling in fixed selected materials, not family/training replicates.']}
a.output.write_text(json.dumps(out,indent=2)+'\n')
for cp,v in models.items():
 print(cp,'natural',{k:d['mean'] for k,d in v['implicaturex']['parent/naturally_occurring_conversational'].items() if k in ['baseline','cancel_minus_irrelevant_delta','recognition','joint_update']})
 print(cp,'PN',{g:{k:d[k]['mean'] for k in ['strong_correct','weak_correct']} for g,d in v['circa']['descriptions'].items() if g.startswith('common-chat/original/') and g.endswith('negative-strength')})
print('natural stage delta',changes['implicaturex']['parent/naturally_occurring_conversational']['cancel_minus_irrelevant_delta'])
