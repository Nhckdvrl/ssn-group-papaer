#!/usr/bin/env python3
"""Counterbalance substantive MCQ options, keeping 'none of the above' last."""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from run_native_readout import next_logits
from run_multichoice_logprob import SUFFIX

ap = argparse.ArgumentParser()
ap.add_argument('--root', type=Path, required=True)
ap.add_argument('--model', type=Path, required=True)
ap.add_argument('--model-id', required=True)
ap.add_argument('--revision', required=True)
ap.add_argument('--language', required=True)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
assert not args.output.exists(), 'Never overwrite a run'
args.output.mkdir(parents=True)
start = time.monotonic()
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
data = args.root/'data/multiprageval.jsonl'
rows = [r for r in map(json.loads,data.read_text().splitlines()) if r['language']==args.language]
assert len(rows)==300
letters = list('ABCDE')
stimuli = []
for r in rows:
    matches = list(re.finditer(r'^\(([A-E])\)',r['prompt'],re.M))
    assert [m.group(1) for m in matches]==letters
    contents = [r['prompt'][m.end():matches[i+1].start() if i+1<len(matches) else len(r['prompt'])] for i,m in enumerate(matches)]
    for rotation in range(4):
        mapping = letters[rotation:4]+letters[:rotation]+['E']
        if rotation==0:
            prompt = r['prompt']
        else:
            prompt = r['prompt'][:matches[0].start()]+''.join('('+label+')'+contents[letters.index(original)] for label,original in zip(letters,mapping))
        rotated = list(re.finditer(r'^\(([A-E])\)',prompt,re.M))
        for i,m in enumerate(rotated):
            content = prompt[m.end():rotated[i+1].start() if i+1<5 else len(prompt)]
            assert content==contents[letters.index(mapping[i])], 'Lost content during permutation'
        assert mapping[-1]=='E' and len(set(mapping))==5
        gold = letters[mapping.index(r['gold'])]
        for condition in ['native','format']:
            stimuli.append({**r,'rotation':rotation,'condition_readout':condition,'display_to_original':dict(zip(letters,mapping)),
                            'display_gold':gold,'readout_prompt':prompt+(SUFFIX if condition=='format' else '')})
tok = AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
if tok.pad_token_id is None:tok.pad_token=tok.eos_token
model = AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
ids = [tok.encode(x,add_special_tokens=False) for x in letters]
assert all(len(x)==1 for x in ids)
ids = [x[0] for x in ids]
full = [tok.apply_chat_template([{'role':'user','content':r['readout_prompt']}],tokenize=False,add_generation_prompt=True,enable_thinking=False) for r in stimuli]
@torch.inference_mode()
def read(texts):
    inp=tok(texts,padding=True,return_tensors='pt',add_special_tokens=False).to(model.device)
    return next_logits(model,inp)[:,ids].softmax(-1).cpu().numpy()
control_indices=list(range(7))+[len(full)-1]
batch=read([full[i] for i in control_indices])
controls=[{'index':k,'delta':float(np.max(np.abs(read([full[control_indices[k]]])[0]-batch[k])))} for k in [0,7]]
config={'task':'option_order_audit','model':args.model_id,'revision':args.revision,'language':args.language,
        'n':len(stimuli),'n_original_items':len(rows),'dtype':'float32','tf32':False,'enable_thinking':False,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helper_sha256':hashlib.sha256(Path(__file__).with_name('run_native_readout.py').read_bytes()).hexdigest(),
        'data_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'numerical_controls':controls,
        'numerical_gate_pass':all(c['delta']<1e-3 for c in controls),'none_of_above_anchor':'E',
        'readout':'restricted metalinguistic letter probability; not latent language knowledge or SDT'}
(args.output/'config.json').write_text(json.dumps(config,indent=2))
assert config['numerical_gate_pass'], 'Failed numerical gate; do not reinterpret results'
records=[]
with (args.output/'predictions.jsonl').open('w') as f:
    for offset in range(0,len(full),16):
        probs=read(full[offset:offset+16])
        for r,p in zip(stimuli[offset:offset+16],probs):
            prediction=letters[int(np.argmax(p))]
            original=r['display_to_original'][prediction]
            out={k:v for k,v in r.items() if k not in ['prompt','readout_prompt']}
            out.update(display_prediction=prediction,prediction=original,correct=original==r['gold'],
                       original_choice_probs={r['display_to_original'][k]:float(v) for k,v in zip(letters,p)},
                       prompt_sha256=hashlib.sha256(r['readout_prompt'].encode()).hexdigest())
            f.write(json.dumps(out,ensure_ascii=False)+'\n');records.append(out)
        f.flush()
        if offset%160==0:print(json.dumps({'done':len(records),'total':len(full)}),flush=True)
summary={}
for condition in ['native','format']:
    for group in ['maxim','literal']:
        selected=[r for r in records if r['condition_readout']==condition and ((r['phenomenon']=='literal')==(group=='literal'))]
        per_rotation=[float(np.mean([r['correct'] for r in selected if r['rotation']==i])) for i in range(4)]
        per_item={}
        for r in selected:per_item.setdefault(r['item_id'],[]).append(r)
        stable=np.mean([len({r['prediction'] for r in rs})==1 for rs in per_item.values()])
        summary[condition+'_'+group]={'n_items':len(per_item),'accuracy_per_rotation':per_rotation,
                                   'accuracy_mean':float(np.mean(per_rotation)),'semantic_argmax_invariance':float(stable)}
config.update(complete=True,wall_seconds=time.monotonic()-start,peak_gpu_memory_bytes=torch.cuda.max_memory_allocated())
(args.output/'config.json').write_text(json.dumps(config,indent=2))
(args.output/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({'complete':True,'seconds':config['wall_seconds'],'summary':summary}),flush=True)
