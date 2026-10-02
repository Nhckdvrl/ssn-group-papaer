#!/usr/bin/env python3
"""Fixed engineering probes; never interpret an unclosed think prefix as CoT."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from run_implicaturex import prepare
from run_native_readout import next_logits

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--dtype',choices=['float32','bfloat16'],required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();rows,audit=prepare(a.root)
types=sorted({r['phenomenon'] for r in rows});selected=set()
for t in types:
 ids=sorted({r['item_id'] for r in rows if r['phenomenon']==t});selected.update([ids[0],ids[-1]])
rows=[r for r in rows if r['item_id'] in selected];assert len(rows)==96
a.output.mkdir(parents=True);start=time.monotonic()
torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
p=a.root/'models/Qwen3-4B';tok=AutoTokenizer.from_pretrained(p,local_files_only=True)
model=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,torch_dtype=getattr(torch,a.dtype),device_map={'':0},weights_only=True).eval()
labels=[tok.encode(c,add_special_tokens=False)[0] for c in ['1','2']]
raw=[];maxdelta=0.
with (a.output/'predictions.jsonl').open('w') as f:
 for thinking in [False,True]:
  for r in rows:
   inp=tok.apply_chat_template([{'role':'system','content':r['system_prompt']},{'role':'user','content':r['prompt']}],
        add_generation_prompt=True,return_dict=True,enable_thinking=thinking,return_tensors='pt').to(model.device)
   with torch.inference_mode():
    logits=model(**inp,output_hidden_states=True).logits[0,-1].float()
    full=logits[labels].softmax(-1)
    fast=next_logits(model,inp)[0,labels].softmax(-1)
    delta=float((full-fast).abs().max());maxdelta=max(maxdelta,delta)
   rec={'item_id':r['item_id'],'state':r['state'],'true_label':r['true_label'],'phenomenon':r['phenomenon'],
        'dtype':a.dtype,'enable_thinking_prefix':thinking,'actual_reasoning_generated':False,
        'p_true_full_forward':float(full[int(r['true_label'])-1]),'p_true_optimized':float(fast[int(r['true_label'])-1]),
        'forward_max_delta':delta,'input_token_sha256':hashlib.sha256(json.dumps(inp.input_ids.tolist()).encode()).hexdigest(),
        'template_suffix':tok.decode(inp.input_ids[0,-24:]),'support_mass':float(logits[labels].logsumexp(-1).sub(logits.logsumexp(-1)).exp())}
   f.write(json.dumps(rec)+'\n');raw.append(rec)
  f.flush();print(json.dumps({'prefix_done':thinking,'n':96}),flush=True)
summary={'dtype':a.dtype,'n':len(raw),'selected_items':sorted(selected),'max_optimized_full_prob_delta':maxdelta,
         'model_revision':'1cfa9a7208912126459214e8b04321603b3df60c','seconds':time.monotonic()-start,
         'complete':True,'source_audit':audit,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'limits':'Unclosed thinking prefix is an implementation probe, not generated reasoning or a pragmatic capability result.'}
(a.output/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps({'complete':True,'seconds':summary['seconds'],'max_forward_delta':maxdelta}),flush=True)
