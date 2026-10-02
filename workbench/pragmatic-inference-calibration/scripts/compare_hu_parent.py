#!/usr/bin/env python3
"""Compare released Flan-T5-XL item probabilities; audit prompt token identity."""
import argparse
import ast
import csv
import json
from collections import defaultdict
from pathlib import Path

from transformers import T5Tokenizer

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
tok=T5Tokenizer.from_pretrained(args.root/'models/flan-t5-xl',local_files_only=True)
run=args.root/'runs/E04-hu-flan-t5-xl'
rows=[json.loads(s) for s in (run/'predictions.jsonl').read_text().splitlines()]
cache={};missing=set();errors=[];agreements=[];mismatch=[];text_diff=0;norm_diff=0;tokens_diff=0;by=defaultdict(list)
for r in rows:
    name=f"{r['phenomenon']}_flan-t5-xl_seed{r['seed']}_examples0.csv"
    p=args.root/'upstream/lm-pragmatics/model_data'/name
    if not p.exists():
        missing.add(name)
        continue
    if name not in cache:
        cache[name]={v['item_id']:v for v in csv.DictReader(p.open())}
    t=cache[name][r['item_id']]
    if r['prompt']!=t['prompt']:
        text_diff+=1
        norm_diff+=r['prompt'].replace('\r\n','\n')!=t['prompt'].replace('\r\n','\n')
        tokens_diff+=tok.encode(r['prompt'])!=tok.encode(t['prompt'])
    probs=ast.literal_eval(t['distribution'])
    errors.extend(abs(r['choice_probs'][str(k)]-v) for k,v in probs.items())
    same=r['prediction']==str(int(float(t['answer'])))
    agreements.append(same)
    by[r['phenomenon']].append(same)
    if not same:
        mismatch.append({'phenomenon':r['phenomenon'],'item_id':r['item_id'],'seed':r['seed'],'ours':r['prediction'],'parent':t['answer']})
result={'n':len(agreements),'missing':sorted(missing),'argmax_agreement':sum(agreements)/len(agreements),
    'max_probability_delta':max(errors),'mean_absolute_probability_delta':sum(errors)/len(errors),
    'mismatches':mismatch,'per_phenomenon_agreement':{k:sum(v)/len(v) for k,v in by.items()},
    'prompt_byte_differences':text_diff,'differences_after_line_ending_normalization':norm_diff,
    'prompt_token_differences':tokens_diff,
    'scope':'released prompt CSVs versus original model_data; same model family; historical weight SHA unrecorded'}
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
