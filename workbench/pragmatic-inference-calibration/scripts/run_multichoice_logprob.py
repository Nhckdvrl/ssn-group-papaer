#!/usr/bin/env python3
"""E08 MCQ readout controls; no claim of direct access to pragmatic knowledge."""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
from run_native_readout import next_logits, target_logprobs

SUFFIX='\n\nReturn only the letter (A, B, C, D, or E) of the selected option.'


def options(prompt):
    matches=list(re.finditer(r'^\(([A-E])\)\s*',prompt,re.MULTILINE))
    assert [m.group(1) for m in matches]==list('ABCDE')
    return [prompt[m.end():matches[i+1].start() if i+1<len(matches) else len(prompt)].strip() for i,m in enumerate(matches)]


def t5_targets(model,tok,prompt,targets):
    previous_padding = tok.padding_side
    # Decoder targets must be right padded. Left padding adds decoder steps
    # before the answer and makes teacher forcing depend on other targets.
    tok.padding_side = 'right'
    inp=tok([prompt]*len(targets),padding=True,return_tensors='pt').to(model.device)
    labels=tok(targets,padding=True,return_tensors='pt').input_ids.to(model.device)
    mask=labels!=tok.pad_token_id
    labels=labels.masked_fill(~mask,-100)
    with torch.inference_mode():
        logits=model(**inp,labels=labels,use_cache=False).logits.float()
        lps=logits.log_softmax(-1).gather(-1,labels.clamp_min(0).unsqueeze(-1)).squeeze(-1)
    tok.padding_side = previous_padding
    return (lps*mask).sum(-1).tolist(),mask.sum(-1).tolist()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--model-id',required=True)
    ap.add_argument('--revision',required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--language')
    ap.add_argument('--dtype',choices=['bfloat16','float32'],default='bfloat16')
    args=ap.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    start=time.monotonic()
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    seq=AutoConfig.from_pretrained(args.model,local_files_only=True).is_encoder_decoder
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left',use_fast=not seq)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cls=AutoModelForSeq2SeqLM if seq else AutoModelForCausalLM
    actual_dtype='float32' if seq else args.dtype
    model=cls.from_pretrained(args.model,local_files_only=True,torch_dtype=getattr(torch,actual_dtype),device_map={'':0}).eval()
    data=args.root/'data/multiprageval.jsonl'
    rows=[r for r in map(json.loads,data.read_text().splitlines()) if not args.language or r['language']==args.language]
    choices=list('ABCDE')
    ids=[tok.encode(c,add_special_tokens=False) for c in choices]
    assert all(len(x)==1 for x in ids)
    text_options=[options(r['prompt']) for r in rows]
    assert all(len(v)==5 and all(v) for v in text_options)
    metadata={'model':args.model_id,'revision':args.revision,'n':len(rows),'readout':'metalinguistic native/format letter and original-MCQ option text likelihood',
        'data_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'likelihood_helper_sha256':hashlib.sha256(Path(__file__).with_name('run_native_readout.py').read_bytes()).hexdigest(),
        'format_instruction':SUFFIX,'enable_thinking':False,'encoder_decoder':seq,'tokenizer':type(tok).__name__,
        'dtype':actual_dtype,'tf32':False,
        'text_length_definition':'full assistant completion incl chat terminator / T5 EOS; whole sequence sum divided by same token count',
        'batch_size':16,'letter_token_ids':ids,'packages':{'torch':torch.__version__},'limitations':['MCQ options are in context; copy likelihood and option length are confounds','No inference licensing labels; not SDT or direct knowledge']}
    (args.output/'config.json').write_text(json.dumps(metadata,indent=2)+'\n')
    records=[r | {'model':args.model_id,'revision':args.revision} for r in rows]
    for condition in ['native','format']:
        prompts=[r['prompt']+(SUFFIX if condition=='format' else '') for r in rows]
        full=[p if seq else tok.apply_chat_template([{'role':'user','content':p}],add_generation_prompt=True,tokenize=False,enable_thinking=False) for p in prompts]
        for i in range(0,len(rows),16):
            inp=tok(full[i:i+16],padding=True,return_tensors='pt',add_special_tokens=seq).to(model.device)
            with torch.inference_mode():logits=next_logits(model,inp)
            probs=logits[:,[x[0] for x in ids]].softmax(-1).tolist()
            for r,p,pr in zip(records[i:i+16],full[i:i+16],probs):
                r[f'{condition}_letter_probs']=dict(zip(choices,pr))
                r[f'{condition}_letter_prediction']=choices[int(np.argmax(pr))]
                r[f'{condition}_prompt_sha256']=hashlib.sha256(p.encode()).hexdigest()
    parity=[]
    with (args.output/'predictions.jsonl').open('w') as f:
        for i,(r,targets) in enumerate(zip(records,text_options)):
            if seq:
                lps,lengths=t5_targets(model,tok,r['prompt'],targets)
            else:
                lps,_=target_logprobs(model,tok,r['prompt'],targets,16)
                prefix=tok.apply_chat_template([{'role':'user','content':r['prompt']}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                prefix_n=len(tok.encode(prefix,add_special_tokens=False))
                lengths=[len(tok.encode(tok.apply_chat_template([{'role':'user','content':r['prompt']},{'role':'assistant','content':t}],tokenize=False,enable_thinking=False),add_special_tokens=False))-prefix_n for t in targets]
                if i<12:
                    one,_=target_logprobs(model,tok,r['prompt'],targets,1)
                    parity.append(max(abs(a-b) for a,b in zip(lps,one)))
            norm=[v/n for v,n in zip(lps,lengths)]
            r.update(option_text_logprobs=dict(zip(choices,lps)),option_completion_lengths=dict(zip(choices,lengths)),
                text_cumulative_prediction=choices[int(np.argmax(lps))],text_per_token_prediction=choices[int(np.argmax(norm))])
            f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
            if i%100==0:print(json.dumps({'done':i+1,'total':len(rows)}),flush=True)
    metadata.update(wall_seconds=time.monotonic()-start,batch_parity_max_abs_logprob_delta=max(parity) if parity else None,
        batch_parity_pass=max(parity)<1e-3 if parity else None,peak_gpu_memory_bytes=torch.cuda.max_memory_allocated())
    (args.output/'config.json').write_text(json.dumps(metadata,indent=2)+'\n')
    metrics={key:float(np.mean([r[key]==r['gold'] for r in records])) for key in ['native_letter_prediction','format_letter_prediction','text_cumulative_prediction','text_per_token_prediction']}
    (args.output/'summary.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps({'complete':True,**metrics,'seconds':metadata['wall_seconds']}))


if __name__=='__main__':main()
