#!/usr/bin/env python3
"""E29 fixed original items: subject knowledge, conveyed information and polarity."""
import argparse,hashlib,json,re,time
from collections import defaultdict
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoConfig,AutoModelForCausalLM,AutoModelForSeq2SeqLM
from epitome_data import prepare
from run_native_readout import next_logits
from aggregate import estimate
from knowledge_variants import variants
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--model',type=Path,required=True);ap.add_argument('--model-id',required=True);ap.add_argument('--revision',required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();a.output.mkdir(parents=True);start=time.monotonic()
source,_,audit=prepare(a.root);rows=[r for r in source if r['task']=='si' and r['phase']=='knowledge'];assert len(rows)==360
for r in rows:
 r['variants']=variants(r['prompt'])
torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
seq=AutoConfig.from_pretrained(a.model,local_files_only=True).is_encoder_decoder
common=a.model
if 'OLMoE' in a.model.name:common=a.root/'models/OLMoE-1B-7B-0125-SFT'
if a.model.name in ['Qwen2.5-3B','Qwen2.5-3B-Instruct']:common=a.root/'models/Qwen2.5-3B-Instruct'
tok=AutoTokenizer.from_pretrained(common,local_files_only=True,padding_side='left',use_fast=not seq)
if tok.pad_token_id is None:tok.pad_token=tok.eos_token
labels=[tok.encode(x,add_special_tokens=False) for x in ['Yes','No']];assert all(len(x)==1 for x in labels);labels=[x[0] for x in labels]
cls=AutoModelForSeq2SeqLM if seq else AutoModelForCausalLM
model=cls.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
def text(r,variant,interface):
 p=r['variants'][variant]
 if interface=='bare':return p
 p='Reply with only one answer from: Yes, No.\n\n'+p
 return tok.apply_chat_template([{'role':'user','content':p}],tokenize=False,add_generation_prompt=True,enable_thinking=False) if tok.chat_template and not seq else p
@torch.inference_mode()
def read(ids):
 inp=tok.pad({'input_ids':ids,'attention_mask':[[1]*len(x) for x in ids]},padding=True,return_tensors='pt').to(model.device)
 logits=next_logits(model,inp);target=logits[:,labels]
 pr=target.softmax(-1).cpu().tolist();mass=(target.logsumexp(-1)-logits.logsumexp(-1)).exp().cpu().tolist()
 margins=(target[:,0]-target[:,1]).cpu().tolist();tops=logits.argmax(-1).cpu().tolist()
 return [{'yes_prob':p[0],'support_mass':m,'yes_minus_no_logit':g,'support_argmax_present':t in labels} for p,m,g,t in zip(pr,mass,margins,tops)]
allrows=[];controls=[];hashes={}
with (a.output/'predictions.jsonl').open('w') as f:
 for interface in ['bare','common-chat']:
  for variant in ['parent','role','access-only','negative']:
   texts=[text(r,variant,interface) for r in rows];ids=[tok.encode(p,add_special_tokens=seq) for p in texts]
   probe=ids[:7]+ids[-1:];many=read(probe)
   delta=max(abs(read([probe[i]])[0][k]-many[i][k]) for i in [0,7] for k in ['yes_prob','support_mass'])
   controls.append({'interface':interface,'variant':variant,'delta':delta,'pass':delta<.001});(a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert delta<.001
   hashes[interface+'/'+variant]=hashlib.sha256(json.dumps(ids).encode()).hexdigest()
   for off in range(0,360,8):
    for j,(r,z) in enumerate(zip(rows[off:off+8],read(ids[off:off+8]))):
     norm_yes=(r['access']==3) != (variant=='negative')
     rec={k:r[k] for k in ['key','item','experiment','access','n']};rec.update(z,interface=interface,variant=variant,parent_norm_yes=norm_yes,parent_norm_probability=z['yes_prob'] if norm_yes else 1-z['yes_prob'],correct=((z['yes_prob']>.5)==norm_yes),readout_prompt_sha256=hashlib.sha256(texts[off+j].encode()).hexdigest())
     f.write(json.dumps(rec)+'\n');allrows.append(rec)
    f.flush()
   print(json.dumps({'done':interface+'/'+variant,'n':360}),flush=True)
groups=defaultdict(list)
for r in allrows:groups[r['interface'],r['variant'],r['experiment'],r['access'],r['n']].append(r)
summary={'/'.join(map(str,g)):{k:estimate([r[k] for r in rs]) for k in ['parent_norm_probability','correct','support_mass']} for g,rs in groups.items()}
(a.output/'summary.json').write_text(json.dumps(summary,indent=2))
config={'task':'speaker_knowledge_controls','model':a.model_id,'revision':a.revision,'common_tokenizer':str(common),'dtype':'float32','tf32':False,'n':len(allrows),'n_original_items':40,'source_audit':audit,'input_token_hashes':hashes,'numerical_gate_pass':True,'complete':True,'wall_seconds':time.monotonic()-start,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(a.output/'config.json').write_text(json.dumps(config,indent=2));print(json.dumps({'complete':True,'seconds':config['wall_seconds']}),flush=True)
