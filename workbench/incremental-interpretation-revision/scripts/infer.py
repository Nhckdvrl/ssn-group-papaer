"""Frozen Qwen inference, preserving upstream raw-continuation protocol for E00."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from data import CACHE, amouyal, verified_root, sha

REPAIR='Read the whole sentence and revise any initial interpretation before answering.'

def clean_word(word):
    word=word.replace(' ','').lower().strip()
    if word and not word[0].isascii():word=word[1:]
    return word

def tasks_e00(cache,tokenizer):
    root=verified_root(cache,'amouyal');rows=amouyal(cache)
    tasks=[]
    for order,file in [('reg','prefixes.json'),('rev','prefixes_rev.json')]:
        prefixes=json.loads((root/'prefixes'/file).read_text());assert len(prefixes)==8
        for pi,pref in enumerate(prefixes):
            for r in rows:
                q=pref['question'].replace('SENTENCE',r['sentence']).replace('QUESTION',r['question'])
                raw=pref['system']+'\n\n'+q+'\n\n'+pref['suffix']
                tasks.append((r,f'raw_{order}_{pi}',raw))
                if pi==0:
                    for repair in (False,True):
                        system=pref['system']+('\n\n'+REPAIR if repair else '')
                        chat=tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':q}],
                            tokenize=False,add_generation_prompt=True,enable_thinking=False)+pref['suffix']
                        tasks.append((r,f'chat_{order}'+('_repair' if repair else ''),chat))
    # Identical first raw prefix evaluated a second time; no prompt selection.
    tasks += [(r,'raw_reg_0_repeat',prompt) for r,pid,prompt in tasks if pid=='raw_reg_0']
    return tasks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=CACHE)
    ap.add_argument('--model',type=Path,default=CACHE/'models/Qwen3-8B')
    ap.add_argument('--experiment',choices=['E00','E01','E02','E03'],default='E00')
    ap.add_argument('--dtype',choices=['bfloat16','float32'],default='bfloat16')
    ap.add_argument('--data',type=Path);ap.add_argument('--batch-size',type=int,default=32)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    assert not (args.out/'predictions.jsonl').exists(),'Do not silently overwrite a run'
    torch.manual_seed(0);torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32=False
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    start=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=getattr(torch,args.dtype),attn_implementation='sdpa').to('cuda').eval()
    for parameter in model.parameters():parameter.requires_grad_(False)
    if args.experiment=='E00':tasks=tasks_e00(args.cache,tokenizer)
    elif args.experiment=='E03':
        from order_audit import tasks_order
        tasks=tasks_order(args.cache,tokenizer)
    else:
        from stimuli import tasks_jurayj
        assert args.data is not None
        tasks=tasks_jurayj(args.data,tokenizer,args.experiment)
    tokens={choice:[idx for word,idx in tokenizer.get_vocab().items() if clean_word(word)==choice.lower()] for choice in ('Yes','No')}
    assert all(tokens.values())
    config=dict(experiment=args.experiment,model=str(args.model),model_manifest=json.loads((args.model/'manifest.json').read_text()),
                torch=torch.__version__,transformers=transformers.__version__,cuda=torch.version.cuda,
                gpu=torch.cuda.get_device_name(),dtype=args.dtype,softmax='float32',attention='sdpa',
                frozen=True,thinking=False,batch_size=args.batch_size,seed=0,choice_token_ids=tokens,
                task_count=len(tasks),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                code_sha256={p.name:sha(p) for p in Path(__file__).parent.glob('*.py')},
                data_sha256=sha(args.data) if args.data else sha(args.cache/'normalized/amouyal.jsonl'))
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (args.out/'predictions.jsonl').open('w') as f, torch.inference_mode():
        for offset in range(0,len(tasks),args.batch_size):
            batch=tasks[offset:offset+args.batch_size]
            inputs=tokenizer([x[2] for x in batch],return_tensors='pt',padding=True).to('cuda')
            logits=model(**inputs,logits_to_keep=1).logits[:,-1,:].float()
            probs=logits.softmax(-1)
            yes=probs[:,tokens['Yes']].sum(-1);no=probs[:,tokens['No']].sum(-1)
            for j,(r,pid,prompt) in enumerate(batch):
                py=float((yes[j]/(yes[j]+no[j])).item());mass=float((yes[j]+no[j]).item())
                item={k:v for k,v in r.items() if k not in ('sentence','question','initial_parse_claim','final_parse_claim')}
                item.update(prompt_id=pid,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                    input_tokens=int(inputs['attention_mask'][j].sum()),p_yes=py,choice_mass=mass,
                    p_correct=None if r['gold'] is None else py if r['gold']=='Yes' else 1-py,
                    correct=None if r['gold'] is None else int((py>0.5)==(r['gold']=='Yes')),
                    greedy_token=tokenizer.decode([int(logits[j].argmax())]))
                f.write(json.dumps(item)+'\n')
            f.flush()
            if offset%(args.batch_size*10)==0:print(f'{offset+len(batch)}/{len(tasks)} elapsed={time.time()-start:.1f}s',flush=True)
    config.update(wall_seconds=time.time()-start,gpu_hours=(time.time()-start)/3600,
                  peak_gpu_bytes=torch.cuda.max_memory_allocated(),predictions_sha256=sha(args.out/'predictions.jsonl'))
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    print('DONE',config['wall_seconds'],flush=True)

if __name__=='__main__':main()
