#!/usr/bin/env python3
"""E09: same-budget native versus format generation on the original Flan anchor."""
import argparse
import hashlib
import json
import time
from pathlib import Path

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, set_seed
from scoring import parse_choice, summarize

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
if args.output.exists():
    raise FileExistsError(args.output)
args.output.mkdir(parents=True)
start=time.monotonic()
data=args.root/'data/multiprageval.jsonl'
rows=[r for r in map(json.loads,data.read_text().splitlines()) if r['language']=='english']
model_path=args.root/'models/flan-t5-xl'
tok=T5Tokenizer.from_pretrained(model_path,local_files_only=True,padding_side='left')
model=T5ForConditionalGeneration.from_pretrained(model_path,local_files_only=True,torch_dtype=torch.float32,device_map={'':0}).eval()
cfg={'model':'google/flan-t5-xl','revision':'7d6315df2c2fb742f0f5b556879d730926ca9001',
    'data_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'dtype':'float32','tokenizer':type(tok).__name__,
    'seeds':[0,1,2],'n_per_seed':len(rows),'max_new_tokens':256,'temperature':.5,'top_p':1.,'top_k':0,
    'batch_size':32,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'scorer_sha256':hashlib.sha256(Path(__file__).with_name('scoring.py').read_bytes()).hexdigest(),
    'answer_token_ids':{c:tok.encode(c,add_special_tokens=False) for c in 'ABCDE'},'task':'E09 English Multi generation'}
(args.output/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
out_summary={}
for condition in ['native','format']:
    suffix='\n\nReturn only the letter (A, B, C, D, or E) of the selected option.' if condition=='format' else ''
    texts=[r['prompt']+suffix for r in rows]
    token_ids=[tok.encode(t) for t in texts]
    cfg[condition]={'instruction':suffix,'prompt_sha256':hashlib.sha256(json.dumps(texts).encode()).hexdigest(),
        'max_input_tokens':max(map(len,token_ids)),
        'unknown_token_fraction':sum(ids.count(tok.unk_token_id) for ids in token_ids)/sum(map(len,token_ids))}
    for seed in [0,1,2]:
        set_seed(seed)
        outputs=[]
        with (args.output/f'{condition}-seed{seed}.jsonl').open('w') as f:
            for i in range(0,len(rows),32):
                inp=tok(texts[i:i+32],return_tensors='pt',padding=True).to(model.device)
                with torch.inference_mode():
                    generated=model.generate(**inp,do_sample=True,temperature=.5,top_p=1.,top_k=0,max_new_tokens=256)
                for r,tokens in zip(rows[i:i+32],generated):
                    raw=tok.decode(tokens,skip_special_tokens=True)
                    rec=r | {'model':cfg['model'],'revision':cfg['revision'],'condition':condition,'seed':seed,
                        'response':raw,'prediction':parse_choice(raw,r['choices']),
                        'truncated':len(tokens)>=257 and not any(int(t)==tok.eos_token_id for t in tokens)}
                    outputs.append(rec);f.write(json.dumps(rec,ensure_ascii=False)+'\n')
                f.flush()
            out_summary[f'{condition}-seed{seed}']=summarize(outputs)
            (args.output/'summary.json').write_text(json.dumps(out_summary,indent=2)+'\n')
        print(json.dumps({'condition':condition,'seed':seed,'done':len(outputs)}),flush=True)
cfg.update(wall_seconds=time.monotonic()-start,peak_gpu_memory_bytes=torch.cuda.max_memory_allocated())
(args.output/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
print(json.dumps({'complete':True,'wall_seconds':cfg['wall_seconds']}))
