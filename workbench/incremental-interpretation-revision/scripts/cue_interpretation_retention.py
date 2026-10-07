"""E74: original published GP/cue order, reusing original single-source baseline."""
import argparse
import collections
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha,write_jsonl
from data_v2 import digest
from joint_relation_use import SYSTEM
from shared_source_cross_use import render,source_info


def build(source,out):
    pairs=collections.defaultdict(dict)
    for r in map(json.loads,source.read_text().splitlines()):pairs[r['pair_id']][r['condition']]=r
    rows=[]
    for pid,g in sorted(pairs.items()):
        assert set(g)=={'gp','control'};a,b=g['gp'],g['control'];assert a['questions']==b['questions'] and a['gold']==b['gold'] and a['cluster_id']==b['cluster_id']
        rows.append(dict(item_id=digest(pid),pair_id=pid,cluster_id=a['cluster_id'],construction=a['construction'],questions=a['questions'],gold=a['gold'],
            gp=a['sentence'],cue=b['sentence'],gp_sha256=a['sentence_sha256'],cue_sha256=b['sentence_sha256'],parent_item_ids={c:r['item_id'] for c,r in g.items()}))
    assert not out.exists();out.parent.mkdir(exist_ok=True,parents=True);write_jsonl(out,rows)
    out.with_suffix('.manifest.json').write_text(json.dumps(dict(data_sha256=sha(out),parent_sha256=sha(source),pairs=len(rows),counts=dict(collections.Counter(r['construction'] for r in rows)),policy='Original published S/Q/gold retained, no new labels or API.'),indent=2)+'\n')
    print('E74 input',len(rows),sha(out),flush=True)


def prepare(rows,tok):
    tasks=[]
    for r in rows:
        for order,first,second in [('GP_CUE','gp','cue'),('CUE_GP','cue','gp')]:
            source=r[first]+'\n\n'+r[second]
            for target in range(2):
                task=SYSTEM+'\nQuestion:\n'+r['questions'][target]+'\nAnswer only Yes or No.'
                prompt=render(tok,source,task);seq=[tok.encode(prompt+c,add_special_tokens=not bool(tok.chat_template)) for c in ['Yes','No']]
                base=tok.encode(prompt,add_special_tokens=not bool(tok.chat_template));common=0
                for values in zip(base,*seq):
                    if len(set(values))!=1:break
                    common+=1
                assert common and all(len(s)>common for s in seq)
                firstprefix,_=source_info(tok,dict(prompt=prompt,row={'sentence':r[first]}))
                oldprefix,_=source_info(tok,dict(prompt=render(tok,r[first],task),row={'sentence':r[first]}))
                assert firstprefix==oldprefix
                prefix,_=source_info(tok,dict(prompt=prompt,row={'sentence':source}))
                assert all(s[:len(prefix)]==prefix for s in seq)
                tasks.append(dict(row=r,order=order,target=target,prompt=prompt,encoded=(seq,common),source_prefix=prefix))
        for order in ['GP_CUE','CUE_GP']:
            group=[t for t in tasks if t['row']['item_id']==r['item_id'] and t['order']==order];assert group[0]['source_prefix']==group[1]['source_prefix']
    return tasks


def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    from reading_map import sequence_scores
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(74);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    rows=[json.loads(x) for x in a.data.read_text().splitlines()];assert json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']==sha(a.data)
    rows=[r for r in rows if int(r['item_id'][:16],16)%a.shards==a.shard];assert rows
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks=prepare(rows,tok);cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();maximum=0.
    uid=min(r['item_id'] for r in rows)
    for t in [t for t in tasks if t['row']['item_id']==uid]:
        ss,n=t['encoded'];lp=sequence_scores(model,ss,[n]*2,tok.pad_token_id);ind=[sequence_scores(model,[s],[n],tok.pad_token_id)[0] for s in ss];maximum=max(maximum,*[abs(x-y) for x,y in zip(lp,ind)])
    assert maximum<.001,maximum
    a.out.mkdir(exist_ok=True,parents=True);assert not (a.out/'predictions.jsonl').exists()
    config=dict(data_sha256=sha(a.data),code_sha256=sha(Path(__file__)),model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),dtype='float32',attention='eager',seed=74,
        gpu=a.gpu,shard=a.shard,shards=a.shards,units=len(rows),tasks=len(tasks),native_LP_max_delta=maximum,first_source_prefix_identical=True,
        dependencies={n:sha(Path(__file__).with_name(n)) for n in ['joint_relation_use.py','shared_source_cross_use.py','reading_map.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');tasks.sort(key=lambda t:max(map(len,t['encoded'][0])))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),a.batch_size):
            batch=tasks[begin:begin+a.batch_size];ss=[s for t in batch for s in t['encoded'][0]];ns=[t['encoded'][1] for t in batch for _ in range(2)];lp=sequence_scores(model,ss,ns,tok.pad_token_id)
            for j,t in enumerate(batch):
                v=lp[2*j:2*j+2];m=max(v);den=m+math.log(sum(math.exp(x-m) for x in v));ps=[math.exp(x-den) for x in v];gold=0 if t['row']['gold'][t['target']]=='Yes' else 1
                f.write(json.dumps(dict(item_id=t['row']['item_id'],order=t['order'],target=t['target'],candidate_logprobs=v,probabilities=ps,correct=float(max(range(2),key=v.__getitem__)==gold),p_correct=ps[gold],prompt_sha256=digest(t['prompt'])))+'\n')
            f.flush()
            if begin%128==0:print('E74',a.model.name,a.shard,begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E74 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['build','run']);p.add_argument('--data',type=Path,required=True);p.add_argument('--source',type=Path);p.add_argument('--model',type=Path);p.add_argument('--out',type=Path);p.add_argument('--gpu',type=int);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);p.add_argument('--batch-size',type=int,default=4);a=p.parse_args()
    if a.mode=='build':build(a.source,a.data)
    else:run(a)
