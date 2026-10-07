"""E76: event-first draft and released free paraphrase before original source QA."""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha
from data_v2 import digest
from natural_cue_patching import blocks
from shared_source_cross_use import render,source_info,greedy
from source_scope_map import RULES
from reading_map import encode_choices

PLAN='Describe the main-clause event first, then every modifier or subordinate-clause event. For each event write one simple sentence with the original participant names, without adding information. Output only these sentences.'


def free_drafts(parent,model,rows):
    directory=parent/'runs-v2'/model;cfg=json.loads((directory/'config.json').read_text());assert cfg['predictions_sha256']==sha(directory/'predictions.jsonl')
    items={r['item_id']:r for r in map(json.loads,(directory/'predictions.jsonl').read_text().splitlines()) if r['reading']=='NONE'}
    assert len(items)==356
    for r in rows:assert items[r['source_unit']]['sentence_sha256']==r['sentence_sha256'] and items[r['source_unit']]['text_sha256']==digest(items[r['source_unit']]['text'])
    return items,cfg


def prepare(rows,tok,drafts):
    tasks=[];prefixes={}
    for r in rows:
        for operation,notes in drafts.items():
            text=notes[r['source_unit']]['text']
            for readout in ['words','letters']:
                for mapping,shown in enumerate([['Yes','No'],['No','Yes']]):
                    task=RULES['G2']+'\nDraft relational notes (may be wrong; judge only the original source):\n'+text+'\nQuestion:\n'+r['question']+'\n'+'\n'.join(f'{a}. {b}' for a,b in zip(['A','B'],shown))
                    task+='\nAnswer only '+('Yes or No.' if readout=='words' else 'A or B.')
                    t=dict(row=r,format='B',operation=operation,readout=readout,mapping=mapping,prompt=render(tok,r['sentence'],task),candidates=shown if readout=='words' else ['A','B'],candidate_gold=shown.index(r['grounded_gold']))
                    t['encoded']=encode_choices(tok,t);prefix,_=source_info(tok,t)
                    oldprefix,_=source_info(tok,dict(row=r,prompt=render(tok,r['sentence'],RULES['G2'])))
                    assert prefix==oldprefix and all(s[:len(prefix)]==prefix for s in t['encoded'][0])
                    if r['source_unit'] in prefixes:assert prefixes[r['source_unit']]==prefix
                    prefixes[r['source_unit']]=prefix;tasks.append(t)
    return tasks


def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    from reading_map import sequence_scores
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(76);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    all_rows=list(map(json.loads,a.data.read_text().splitlines()));assert json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']==sha(a.data)
    rows=[r for r in all_rows if int(r['sentence_sha256'][:16],16)%a.shards==a.shard];assert rows
    free,fcfg=free_drafts(a.parent,a.model.name,rows);assert fcfg['model_manifest_sha256']==sha(a.model/'manifest.json')
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();decoder=blocks(model)
    a.out.mkdir(exist_ok=True,parents=True);assert not (a.out/'drafts.jsonl').exists()
    sources={r['source_unit']:r for r in rows};plan={}
    config=dict(data_sha256=sha(a.data),code_sha256=sha(Path(__file__)),model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),free_predictions_sha256=fcfg['predictions_sha256'],
        dtype='float32',attention='eager',seed=76,gpu=a.gpu,shard=a.shard,shards=a.shards,QA=len(rows),sources=len(sources),cap=256,operations=['FREE','EVENT_FIRST'],
        dependencies={n:sha(Path(__file__).with_name(n)) for n in ['shared_source_cross_use.py','paraphrase_map.py','reading_map.py','source_scope_map.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'drafts.jsonl').open('w') as f:
        for j,(uid,r) in enumerate(sorted(sources.items())):
            prompt=render(tok,r['sentence'],PLAN);ids=tok.encode(prompt,add_special_tokens=not bool(tok.chat_template));g=dict(row=dict(r,donor_source_unit=uid),prompt=prompt,ids=ids,patch_tokens=[],donor_tokens=[])
            generated=greedy(model,decoder,{},g,None,'BASE',256);text=tok.decode(generated,skip_special_tokens=True)
            x=dict(source_unit=uid,sentence_sha256=r['sentence_sha256'],text=text,text_sha256=digest(text),generated_token_ids=generated,capped=len(generated)==256,finish_reason='length' if len(generated)==256 else 'stop',prompt_sha256=digest(prompt));plan[uid]=x;f.write(json.dumps(x)+'\n');f.flush()
            if j%10==0:print('E76 drafts',a.model.name,a.shard,j+1,'/',len(sources),flush=True)
    config.update(drafts_sha256=sha(a.out/'drafts.jsonl'),draft_gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    tasks=prepare(rows,tok,dict(FREE=free,EVENT_FIRST=plan));uid=min(sources);maximum=0.
    for t in [t for t in tasks if t['row']['source_unit']==uid]:
        ss,n=t['encoded'];lp=sequence_scores(model,ss,[n]*2,tok.pad_token_id);ind=[sequence_scores(model,[s],[n],tok.pad_token_id)[0] for s in ss];maximum=max(maximum,*[abs(x-y) for x,y in zip(lp,ind)])
    assert maximum<.001,maximum;config.update(instrument_LP_max_delta=maximum,tasks=len(tasks),source_prefix_identical=True);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    tasks.sort(key=lambda t:max(map(len,t['encoded'][0])))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),a.batch_size):
            batch=tasks[begin:begin+a.batch_size];ss=[s for t in batch for s in t['encoded'][0]];ns=[t['encoded'][1] for t in batch for _ in range(2)];scores=sequence_scores(model,ss,ns,tok.pad_token_id)
            for j,t in enumerate(batch):
                lp=scores[2*j:2*j+2];m=max(lp);den=m+math.log(sum(math.exp(x-m) for x in lp));r=t['row'];gold=t['candidate_gold']
                x=dict(item_id=r['item_id'],source_unit=r['source_unit'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],candidate_gold=gold,candidate_logprobs=lp,correct=float(max(range(2),key=lp.__getitem__)==gold),p_correct=math.exp(lp[gold]-den),prompt_sha256=digest(t['prompt']))
                f.write(json.dumps(x)+'\n')
            f.flush()
            if begin%256==0:print('E76 QA',a.model.name,a.shard,begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E76 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);p.add_argument('--batch-size',type=int,default=4);run(p.parse_args())
