#!/usr/bin/env python3
"""Predefined numerical controls: first/last Wavelength and Hu original generate."""
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from run_native_readout import target_logprobs, next_logits, get_instruction

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--model',type=Path,required=True)
ap.add_argument('--model-id',required=True)
ap.add_argument('--dtype',choices=['bfloat16','float32'],required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
if args.output.exists():raise FileExistsError(args.output)
torch.backends.cuda.matmul.allow_tf32=False
torch.backends.cudnn.allow_tf32=False
seq=AutoConfig.from_pretrained(args.model,local_files_only=True).is_encoder_decoder
tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left',use_fast=not seq)
if tok.pad_token_id is None:tok.pad_token=tok.eos_token
cls=AutoModelForSeq2SeqLM if seq else AutoModelForCausalLM
model=cls.from_pretrained(args.model,local_files_only=True,torch_dtype=getattr(torch,args.dtype),device_map={'':0}).eval()
result={'model':args.model_id,'dtype':args.dtype,'tf32':False,'hu':[],'wavelength':[],'multi':[]}
rows=[json.loads(s) for s in (args.root/'data/hu.jsonl').read_text().splitlines()]
chosen=[rows[0],rows[-1]]
for r in chosen:
    inp=tok(r['prompt'],return_tensors='pt').to(model.device)
    ids=[tok.encode(c,add_special_tokens=False)[0] for c in r['choices']]
    with torch.inference_mode():
        direct=next_logits(model,inp)[0,ids].softmax(-1).tolist()
        gen=model.generate(**inp,max_new_tokens=1,do_sample=False,return_dict_in_generate=True,output_scores=True)
        parent=gen.scores[0][0,ids].float().softmax(-1).tolist()
    result['hu'].append({'phenomenon':r['phenomenon'],'item_id':r['item_id'],'parent_generate_max_prob_delta':max(abs(a-b) for a,b in zip(direct,parent))})
if not seq:
    wave=[json.loads(s) for s in (args.root/'data/wavelength.jsonl').read_text().splitlines()]
    inst=get_instruction(args.root)
    for r in [wave[0],wave[-1]]:
        s=r['source'];targets=[f'<answer>{x}</answer>' for x in range(0,101,5)]
        prompt=inst.format(left=s['left'],right=s['right'],clue=s['clue'],scale=5,possible_values=', '.join(map(str,range(0,101,5))))
        one,_=target_logprobs(model,tok,prompt,targets,1)
        many,_=target_logprobs(model,tok,prompt,targets,8)
        result['wavelength'].append({'item_id':r['item_id'],'batch_max_abs_logprob_delta':max(abs(a-b) for a,b in zip(one,many)),
            'argmax_same':np.argmax(one).item()==np.argmax(many).item()})
    multi=[json.loads(s) for s in (args.root/'data/multiprageval.jsonl').read_text().splitlines()]
    from run_multichoice_logprob import options
    for r in [multi[0],multi[-1]]:
        targets=options(r['prompt'])
        one,_=target_logprobs(model,tok,r['prompt'],targets,1)
        many,_=target_logprobs(model,tok,r['prompt'],targets,16)
        result['multi'].append({'item_id':r['item_id'],'language':r['language'],'batch_max_abs_logprob_delta':max(abs(a-b) for a,b in zip(one,many)),
            'argmax_same':np.argmax(one).item()==np.argmax(many).item()})
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
