#!/usr/bin/env python3
"""Sample the original Wavelength task; preserve invalid answers and raw text."""
import argparse, hashlib, json, re, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from run_native_readout import get_instruction

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--model',type=Path,required=True)
ap.add_argument('--model-id',required=True)
ap.add_argument('--revision',required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
assert not args.output.exists()
args.output.mkdir(parents=True)
start=time.monotonic()
torch.backends.cuda.matmul.allow_tf32=False
torch.backends.cudnn.allow_tf32=False
tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
if tok.pad_token_id is None:tok.pad_token=tok.eos_token
model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
data=args.root/'data/wavelength.jsonl'
rows=[json.loads(s) for s in data.read_text().splitlines()]
assert len(rows)==100
instruction=get_instruction(args.root)
grid=list(range(0,101,5))
prompts=[]
for r in rows:
    s=r['source']
    p=instruction.format(left=s['left'],right=s['right'],clue=s['clue'],scale=5,possible_values=', '.join(map(str,grid)))
    prompts.append(tok.apply_chat_template([{'role':'user','content':p}],tokenize=False,add_generation_prompt=True,enable_thinking=False))
generation={'do_sample':True,'temperature':1.0,'top_p':1.0,'top_k':0,'repetition_penalty':1.0,'max_new_tokens':128,
            'pad_token_id':tok.pad_token_id,'eos_token_id':model.generation_config.eos_token_id}
config={'task':'wavelength_sampling','model':args.model_id,'revision':args.revision,'n_items':100,'seeds':list(range(32)),
        'dtype':'float32','tf32':False,'enable_thinking':False,'batch_size':16,'generation':generation,
        'inherited_generation_defaults':model.generation_config.to_dict(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'data_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),
        'prompt_token_ids_sha256':hashlib.sha256(json.dumps([tok.encode(p,add_special_tokens=False) for p in prompts]).encode()).hexdigest()}
(args.output/'config.json').write_text(json.dumps(config,indent=2))
answers={r['item_id']:[] for r in rows}
with (args.output/'predictions.jsonl').open('w') as f:
    for seed in range(32):
        torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
        for offset in range(0,100,16):
            inp=tok(prompts[offset:offset+16],padding=True,return_tensors='pt',add_special_tokens=False).to('cuda')
            with torch.inference_mode():out=model.generate(**inp,**generation)
            texts=tok.batch_decode(out[:,inp.input_ids.shape[1]:],skip_special_tokens=True)
            for r,raw,generated in zip(rows[offset:offset+16],texts,out[:,inp.input_ids.shape[1]:]):
                blocks=re.findall(r'<answer>\s*(\d{1,3})\s*</answer>',raw)
                parsed=int(blocks[0]) if len(blocks)==1 and int(blocks[0]) in grid else None
                eos=generation['eos_token_id'];eos=[eos] if isinstance(eos,int) else eos or []
                truncated=generated.numel()>=128 and not any(x in eos for x in generated.tolist())
                rec={'item_id':r['item_id'],'pair_id':r.get('pair_id'),'seed':seed,'raw_response':raw,'prediction':parsed,
                     'invalid':parsed is None,'truncated':truncated,'target':r['source']['target']}
                f.write(json.dumps(rec,ensure_ascii=False)+'\n');answers[r['item_id']].append(parsed)
            f.flush()
        print(json.dumps({'seeds_done':seed+1,'total_seeds':32}),flush=True)
summary=[]
for r in rows:
    xs=answers[r['item_id']];valid=[x for x in xs if x is not None]
    errors=[abs(x-float(r['source']['target'])) for x in valid]
    summary.append({'item_id':r['item_id'],'valid_n':len(valid),'n':len(xs),
                    'valid_conditional_distribution':{str(x):valid.count(x)/len(valid) for x in grid} if valid else None,
                    'valid_conditional_mean':float(np.mean(valid)) if valid else None,
                    'mae_lower_bound':sum(errors)/len(xs),'mae_upper_bound':(sum(errors)+100*(len(xs)-len(valid)))/len(xs)})
(args.output/'item-summary.json').write_text(json.dumps(summary,indent=2))
config.update(complete=True,n=3200,wall_seconds=time.monotonic()-start,peak_gpu_memory_bytes=torch.cuda.max_memory_allocated())
(args.output/'config.json').write_text(json.dumps(config,indent=2))
print(json.dumps({'complete':True,'seconds':config['wall_seconds'],'invalid':sum(x is None for xs in answers.values() for x in xs)}),flush=True)
