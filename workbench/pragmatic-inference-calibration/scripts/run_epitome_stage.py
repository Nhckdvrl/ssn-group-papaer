#!/usr/bin/env python3
"""EPITOME released prompts, restricted raw logits, preserved source contracts."""
import argparse,hashlib,json,time
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,AutoModelForSeq2SeqLM
from run_native_readout import next_logits
from aggregate import estimate

def prepare(root):
 up=root/'upstream/epitome';src=up/'scalar_implicature/data/processed/si_stimuli_qa_parallel_nums_gpt3-text-davinci-002.csv'
 trials=pd.read_csv(src).fillna('');raw=pd.read_csv(up/'scalar_implicature/data/raw/si_stimuli.csv').set_index('item')
 assert len(trials)==360 and trials.item.nunique()==40
 stimuli={};question_versions=defaultdict(int)
 for r in trials.to_dict('records'):
  item=raw.loc[r['item']];a=int(r['access']);n=str(r['n']);exp=int(r['experiment']);num='Some' if exp==1 else n
  update=item['update'].format(a=a,n=num,h='has' if num=='1' else 'have')
  expected_prior=f"{item['intro']}\nQ: {item['q_prior']}\nA:"
  assert r['prior']==expected_prior
  possible={q:f"{item['intro']}\n{update}\nQ:{item[q]}\nA:" for q in ['q_prior','q_posterior']}
  versions=[q for q,p in possible.items() if p==r['speach']];assert versions,(r['item'],a,n)
  question_versions[versions[0]]+=1
  assert r['knowledge']==f"{item['intro']}\n{update}\nQ:{item['q_knowledge']}\nA:"
  for phase in ['prior','speach','knowledge']:
   key=f"si:{r['item']}:{phase}"+(f':{exp}:{a}:{n}' if phase!='prior' else '')
   rec={'key':key,'task':'si','item':int(r['item']),'phase':phase,'experiment':exp,'access':a,'n':n,
        'prompt':r[phase],'choices':['Yes','No'] if phase=='knowledge' else list('0123')}
   if key in stimuli:assert stimuli[key]['prompt']==rec['prompt']
   else:stimuli[key]=rec
 irsrc=up/'indirect_request/data/raw/stims.csv';irs=pd.read_csv(irsrc)
 assert len(irs)==64 and irs.item.nunique()==16
 missing_ir=irs.loc[irs.critical_utterance.isna(),['item','speaker_knowledge','knowledge_cue']].to_dict('records')
 irs=irs.dropna(subset=['critical_utterance'])  # Exact eligibility in released gpt3_predict.py.
 assert len(irs)==24 and irs.item.nunique()==6
 for r in irs.to_dict('records'):
  assert r['critical_a']==('No' if r['speaker_knowledge']=='aware' else 'Yes')
  key=f"ir:{r['item']}:{r['speaker_knowledge']}:{r['knowledge_cue']}"
  stimuli[key]={'key':key,'task':'ir','item':int(r['item']),'phase':'request','speaker_knowledge':r['speaker_knowledge'],
   'knowledge_cue':r['knowledge_cue'],'gold':r['critical_a'],'choices':['Yes','No'],
   'prompt':r['passage']+'\n\n'+r['critical_utterance']+'\n\n'+r['critical_q']+'\n\n'}
 assert len(stimuli)==784
 hashes={str(p.relative_to(up)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,irsrc,up/'scalar_implicature/data/raw/si_stimuli.csv']}
 return list(stimuli.values()),trials,{'source_hashes':hashes,'released_posterior_question_versions':dict(question_versions),
  'n_trials':len(trials),'n_unique_prompts':len(stimuli),'unavailable_ir_conditions':missing_ir,
  'bare_prompt_sha256':hashlib.sha256(json.dumps([(r['key'],r['prompt']) for r in stimuli.values()],ensure_ascii=False).encode()).hexdigest()}

def original_accuracy(exp,a,n,d2,d3):
 if exp==1:return d3<0 if a==3 else d3>=0
 return {(3,3):d3>0,(3,2):d3<0,(3,1):d3<0 and d2<0,
  (2,2):d2>0 and d3>=0,(2,1):d2>=0 and d3<0,(1,1):d2>=0 and d3>=0}[a,int(n)]

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--model',type=Path,required=True)
ap.add_argument('--model-id',required=True);ap.add_argument('--revision',required=True);ap.add_argument('--output',type=Path,required=True)
ap.add_argument("--common-template",type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();stimuli,trials,audit=prepare(a.root);a.output.mkdir(parents=True)
torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
seq=AutoConfig.from_pretrained(a.model,local_files_only=True).is_encoder_decoder
tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,padding_side='left',use_fast=not seq)
if tok.pad_token_id is None:tok.pad_token=tok.eos_token
tok.chat_template=AutoTokenizer.from_pretrained(a.common_template,local_files_only=True).chat_template
common_template=str(a.common_template)
cls=AutoModelForSeq2SeqLM if seq else AutoModelForCausalLM
model=cls.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
choice_ids={}
for choices in [list('0123'),['Yes','No']]:
 ids=[tok.encode(c,add_special_tokens=False) for c in choices];assert all(len(x)==1 for x in ids)
 choice_ids[tuple(choices)]=[x[0] for x in ids]
def prompt(r,condition):
 if condition=='bare':return r['prompt']
 choices=', '.join(r['choices']);text=f'Reply with only one answer from: {choices}.\n\n'+r['prompt']
 return tok.apply_chat_template([{'role':'user','content':text}],tokenize=False,add_generation_prompt=True,enable_thinking=False) if tok.chat_template and not seq else text
def input_ids(r,condition):
 p=prompt(r,condition)
 if seq:return tok.encode(p,add_special_tokens=True)
 # Echo-based parent scores tokenize the complete prompt+candidate. GPT2 merges
 # terminal double newlines differently before a word; preserve its true prefix.
 candidates=[tok.encode(p+c,add_special_tokens=False) for c in r['choices']]
 ids=choice_ids[tuple(r['choices'])]
 assert all(x[-1]==i for x,i in zip(candidates,ids)),r['key']
 prefixes=[x[:-1] for x in candidates]
 assert all(x==prefixes[0] for x in prefixes),r['key']
 assert tok.decode(prefixes[0])==p,(r['key'],'prompt bytes changed')
 return prefixes[0]
boundary_adjustments={c:sum(input_ids(r,c)!=tok.encode(prompt(r,c),add_special_tokens=seq) for r in stimuli) for c in ['bare','format']}
@torch.inference_mode()
def read_details(rs,condition):
 ids=[input_ids(r,condition) for r in rs]
 inp=tok.pad({'input_ids':ids,'attention_mask':[[1]*len(x) for x in ids]},padding=True,return_tensors='pt').to(model.device)
 if model.config.model_type=='gpt2':
  inp['position_ids']=(inp.attention_mask.long().cumsum(-1)-1).masked_fill(inp.attention_mask==0,0)
 logits=next_logits(model,inp);out=[]
 for k,r in enumerate(rs):
  ids=choice_ids[tuple(r['choices'])];target=logits[k,ids]
  out.append((target.softmax(-1).cpu().tolist(),float((target.logsumexp(-1)-logits[k].logsumexp(-1)).exp()),int(logits[k].argmax()) in ids))
 return out
def read(rs,condition):return [r[0] for r in read_details(rs,condition)]
start=time.monotonic();controls=[]
for condition in ['bare','format']:
 for group in ['si-count','si-knowledge','ir']:
  selected=[r for r in stimuli if ('ir' if r['task']=='ir' else 'si-knowledge' if r['phase']=='knowledge' else 'si-count')==group]
  batch=selected[:7]+selected[-1:];many=read(batch,condition)
  delta=max(max(abs(x-y) for x,y in zip(read([batch[i]],condition)[0],many[i])) for i in [0,7])
  details=read_details(batch,condition);mass_delta=max(abs(read_details([batch[i]],condition)[0][1]-details[i][1]) for i in [0,7])
  controls.append({'condition':condition,'group':group,'max_prob_delta':delta,'max_mass_delta':mass_delta,'pass':max(delta,mass_delta)<1e-3})
(a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert all(c['pass'] for c in controls)
results={};hashes={}
with (a.output/'predictions.jsonl').open('w') as f:
 for condition in ['bare','format']:
  hashes[condition]=hashlib.sha256(json.dumps([input_ids(r,condition) for r in stimuli]).encode()).hexdigest()
  for offset in range(0,len(stimuli),8):
   for r,(pr,mass,top) in zip(stimuli[offset:offset+8],read_details(stimuli[offset:offset+8],condition)):
    rec={k:v for k,v in r.items() if k!='prompt'};rec.update(condition=condition,support_mass=mass,support_argmax_present=top,choice_probs=dict(zip(r['choices'],pr)),
     prediction=r['choices'][int(np.argmax(pr))],readout_prompt_sha256=hashlib.sha256(prompt(r,condition).encode()).hexdigest())
    results[condition,r['key']]=rec;f.write(json.dumps(rec,ensure_ascii=False)+'\n')
   f.flush()
summary={}
for condition in ['bare','format']:
 si=[]
 for r in trials.to_dict('records'):
  base=f"si:{r['item']}";suffix=f":{int(r['experiment'])}:{int(r['access'])}:{r['n']}"
  prior=results[condition,base+':prior']['choice_probs'];post=results[condition,base+':speach'+suffix]['choice_probs']
  knowledge=results[condition,base+':knowledge'+suffix]['choice_probs'];d2=post['2']-prior['2'];d3=post['3']-prior['3']
  # Parent round-to-nearest-even in torch and numpy agree on positive bets.
  bd2=float(np.rint(post['2']*100)-np.rint(prior['2']*100));bd3=float(np.rint(post['3']*100)-np.rint(prior['3']*100))
  si.append({'item':int(r['item']),'experiment':int(r['experiment']),'access':int(r['access']),'n':str(r['n']),
   'delta_p2':d2,'delta_p3':d3,'parent_rounded_accuracy':float(original_accuracy(int(r['experiment']),int(r['access']),str(r['n']),bd2,bd3)),
   'knowledge_correct_prob':knowledge['Yes'] if int(r['access'])==3 else knowledge['No'],
   'knowledge_argmax_correct':float((knowledge['Yes']>knowledge['No'])==(int(r['access'])==3))})
 (a.output/(condition+'-si-trials.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in si))
 groups=defaultdict(list)
 for r in si:groups[f"E{r['experiment']}:a{r['access']}:n{r['n']}"].append(r)
 si_summary={g:{k:estimate([r[k] for r in rs]) for k in ['delta_p2','delta_p3','parent_rounded_accuracy','knowledge_correct_prob','knowledge_argmax_correct']} for g,rs in groups.items()}
 ir_summary={}
 for cue in ['implicit','explicit']:
  contrasts=[];acc=[]
  for item in range(1,7):
   aware=results[condition,f'ir:{item}:aware:{cue}'];unaware=results[condition,f'ir:{item}:unaware:{cue}']
   contrasts.append(unaware['choice_probs']['Yes']-aware['choice_probs']['Yes']);acc.append(((aware['prediction']==aware['gold'])+(unaware['prediction']==unaware['gold']))/2)
  ir_summary[cue]={'unaware_minus_aware_yes_prob':estimate(contrasts),'accuracy':estimate(acc)}
 summary[condition]={'si_conditions':si_summary,'ir':ir_summary}
config={'task':'epitome','model':a.model_id,'revision':a.revision,'dtype':'float32','tf32':False,'n':len(stimuli)*2,
 'n_unique_original_items':{'si':40,'ir':6},'audit':audit,'input_token_hashes':hashes,'token_boundary_adjustments':boundary_adjustments,'common_chat_template':common_template,
 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'numerical_gate_pass':True,'wall_seconds':time.monotonic()-start,'complete':True,
 'limits':['Original scores reproduced; no binary warrant/SDT assignment.','Knowledge check and pragmatic decision are prompted readouts, not representational mechanisms.',
 'SI some ambiguous; original publisher rounding retained; continuous deltas preserved.']}
(a.output/'config.json').write_text(json.dumps(config,indent=2));(a.output/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({'complete':True,'seconds':config['wall_seconds'],'audit':audit}),flush=True)
