"""E78 strong offline model families, real Source/notes consumption pipelines."""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha
from data_v2 import digest
from paraphrase_map import INSTRUCTION
from shared_source_cross_use import render,source_info
from event_first_draft import prepare as notes_prepare
from source_scope_map import RULES
from reading_map import encode_choices,sequence_scores

MODELS=['Qwen3-32B','gemma-3-27b-it','Mistral-Small-24B-Instruct-2501']


def prepare(rows,tok,drafts):
    tasks=notes_prepare(rows,tok,dict(SOURCE_AND_DRAFT=drafts))
    for r in rows:
        for op,text in [('DIRECT',r['sentence']),('DRAFT_ONLY',drafts[r['source_unit']]['text'])]:
            for ro in ['words','letters']:
                for mp,shown in enumerate([['Yes','No'],['No','Yes']]):
                    task=RULES['G2']+'\nQuestion:\n'+r['question']+'\n'+'\n'.join(f'{a}. {b}' for a,b in zip(['A','B'],shown))+'\nAnswer only '+('Yes or No.' if ro=='words' else 'A or B.')
                    t=dict(row=r,format='B',operation=op,readout=ro,mapping=mp,prompt=render(tok,text,task),candidates=shown if ro=='words' else ['A','B'],candidate_gold=shown.index(r['grounded_gold']))
                    t['encoded']=encode_choices(tok,t);tasks.append(t)
    return tasks


def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(78);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    allrows=list(map(json.loads,a.data.read_text().splitlines()));assert sha(a.data)==json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows=[r for r in allrows if int(r['sentence_sha256'][:16],16)%a.shards==a.shard];sources={r['source_unit']:r for r in rows}
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='eager').to('cuda').eval()
    a.out.mkdir(exist_ok=True,parents=True);assert not (a.out/'drafts.jsonl').exists()
    config=dict(data_sha256=sha(a.data),model_manifest_sha256=sha(a.model/'manifest.json'),model_path=str(a.model),code_sha256=sha(Path(__file__)),dtype='bfloat16',logprob_dtype='float32',attention='eager',seed=78,gpu=a.gpu,shard=a.shard,shards=a.shards,QA=len(rows),sources=len(sources),cap=256,generation='HF generate greedy cache=True',operations=['DIRECT','SOURCE_AND_DRAFT','DRAFT_ONLY'],dependencies={n:sha(Path(__file__).with_name(n)) for n in ['event_first_draft.py','shared_source_cross_use.py','reading_map.py','paraphrase_map.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');drafts={}
    with (a.out/'drafts.jsonl').open('w') as f:
        for i,(uid,r) in enumerate(sorted(sources.items())):
            prompt=render(tok,r['sentence'],INSTRUCTION);ids=tok.encode(prompt,add_special_tokens=not bool(tok.chat_template));prefix,_=source_info(tok,dict(row=r,prompt=prompt));assert ids[:len(prefix)]==prefix
            inp=torch.tensor([ids],device=model.device)
            with torch.inference_mode():out=model.generate(input_ids=inp,attention_mask=torch.ones_like(inp),max_new_tokens=256,do_sample=False,use_cache=True,pad_token_id=tok.pad_token_id)
            generated=out[0,len(ids):].tolist();text=tok.decode(generated,skip_special_tokens=True)
            g=dict(source_unit=uid,sentence_sha256=r['sentence_sha256'],text=text,text_sha256=digest(text),generated_token_ids=generated,capped=len(generated)==256,finish_reason='length' if len(generated)==256 else 'stop',prompt_sha256=digest(prompt));drafts[uid]=g;f.write(json.dumps(g)+'\n');f.flush()
            if i%10==0:print('E78 draft',a.model.name,a.shard,i+1,'/',len(sources),flush=True)
    config.update(drafts_sha256=sha(a.out/'drafts.jsonl'),draft_gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    tasks=prepare(rows,tok,drafts);checks=[];uid=min(sources)
    for t in [t for t in tasks if t['row']['source_unit']==uid]:
        ss,n=t['encoded'];v1=sequence_scores(model,ss,[n]*2,tok.pad_token_id);v2=sequence_scores(model,ss,[n]*2,tok.pad_token_id);delta=max(abs(x-y) for x,y in zip(v1,v2));assert delta==0.
        checks.append(dict(item_id=t['row']['item_id'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],repeat_LP_max_delta=delta))
    config.update(tasks=len(tasks),instrument=checks);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');tasks.sort(key=lambda t:max(map(len,t['encoded'][0])))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),a.batch_size):
            batch=tasks[begin:begin+a.batch_size];ss=[s for t in batch for s in t['encoded'][0]];ns=[t['encoded'][1] for t in batch for _ in range(2)];scores=sequence_scores(model,ss,ns,tok.pad_token_id)
            for j,t in enumerate(batch):
                lp=scores[2*j:2*j+2];m=max(lp);den=m+math.log(sum(math.exp(x-m) for x in lp));r=t['row'];gold=t['candidate_gold']
                f.write(json.dumps(dict(item_id=r['item_id'],source_unit=r['source_unit'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],candidate_gold=gold,candidate_logprobs=lp,correct=float(max(range(2),key=lp.__getitem__)==gold),p_correct=math.exp(lp[gold]-den),prompt_sha256=digest(t['prompt'])))+'\n')
            f.flush()
            if begin%256==0:print('E78 QA',a.model.name,a.shard,begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E78 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);p.add_argument('--batch-size',type=int,default=1);run(p.parse_args())
