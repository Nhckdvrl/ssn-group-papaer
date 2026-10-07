"""E77: original Source stays encoded, but no later position can consume it."""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha
from data_v2 import digest
from event_first_draft import free_drafts,prepare as parent_prepare
from shared_source_cross_use import source_info
from cross_source_consumption import forward
from natural_cue_patching import blocks


def prepared(rows,tok,parent,freeparent,model,shard):
    d=parent/'runs-v1'/model/str(shard);cfg=json.loads((d/'config.json').read_text())
    assert cfg['predictions_sha256']==sha(d/'predictions.jsonl') and cfg['drafts_sha256']==sha(d/'drafts.jsonl')
    plan={g['source_unit']:g for g in map(json.loads,(d/'drafts.jsonl').read_text().splitlines())}
    free,_=free_drafts(freeparent,model,rows);tasks=parent_prepare(rows,tok,dict(FREE=free,EVENT_FIRST=plan))
    base={(p['item_id'],p['operation'],p['readout'],p['mapping']):p for p in map(json.loads,(d/'predictions.jsonl').read_text().splitlines())}
    assert len(base)==len(tasks)
    for t in tasks:
        prefix,keys=source_info(tok,t);t['sequences'],t['common']=t['encoded'];end=len(prefix)
        t['spans']=[(keys,end) for _ in t['sequences']];t['queries']=[list(range(end,len(s))) for s in t['sequences']]
        old=base[t['row']['item_id'],t['operation'],t['readout'],t['mapping']]
        assert old['prompt_sha256']==digest(t['prompt']) and old['candidate_gold']==t['candidate_gold']
        assert max(keys)<end and all(0<=i<end for i in keys)
        t['parent']=old
    return tasks,cfg


def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(77);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    rows=list(map(json.loads,a.data.read_text().splitlines()));assert sha(a.data)==json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows=[r for r in rows if int(r['sentence_sha256'][:16],16)%a.shards==a.shard]
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks,pcfg=prepared(rows,tok,a.parent,a.free_parent,a.model.name,a.shard)
    assert pcfg['data_sha256']==sha(a.data) and pcfg['model_manifest_sha256']==sha(a.model/'manifest.json') and pcfg['shards']==a.shards
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();decoder=blocks(model)
    checks=[];uid=min(r['source_unit'] for r in rows)
    for t in [t for t in tasks if t['row']['source_unit']==uid]:
        native,hs,_=forward(model,decoder,t,tok.pad_token_id,hidden=True);ref,_,_=forward(model,decoder,t,tok.pad_token_id,use_4d=False)
        _,cut_h,counts=forward(model,decoder,t,tok.pad_token_id,cut=True,hidden=True)
        delta=max(abs(x-y) for x,y in zip(native,ref));parent_delta=max(abs(x-y) for x,y in zip(native,t['parent']['candidate_logprobs']));assert max(delta,parent_delta)<.001
        maximum=0.
        for x,y in zip(hs,cut_h):
            for i,s in enumerate(t['sequences']):
                offset=x.shape[1]-len(s);end=t['spans'][i][1];maximum=max(maximum,float((x[i,offset:offset+end]-y[i,offset:offset+end]).abs().max()))
        assert maximum==0. and min(counts)>0
        checks.append(dict(item_id=t['row']['item_id'],draft=t['operation'],readout=t['readout'],mapping=t['mapping'],native_LP_max_delta=delta,parent_LP_max_delta=parent_delta,source_hidden_max_delta=maximum,removed_edges_per_layer=counts))
    a.out.mkdir(exist_ok=True,parents=True);assert not (a.out/'predictions.jsonl').exists()
    config=dict(data_sha256=sha(a.data),model_manifest_sha256=sha(a.model/'manifest.json'),code_sha256=sha(Path(__file__)),dtype='float32',attention='eager',seed=77,shard=a.shard,shards=a.shards,gpu=a.gpu,QA=len(rows),tasks=len(tasks),instrument=checks,parent_predictions_sha256=pcfg['predictions_sha256'],parent_drafts_sha256=pcfg['drafts_sha256'],free_predictions_sha256=pcfg['free_predictions_sha256'],dependencies={n:sha(Path(__file__).with_name(n)) for n in ['event_first_draft.py','cross_source_consumption.py','shared_source_cross_use.py','reading_map.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for j,t in enumerate(tasks):
            lp,_,counts=forward(model,decoder,t,tok.pad_token_id,cut=True);m=max(lp);den=m+math.log(sum(math.exp(v-m) for v in lp));gold=t['candidate_gold'];r=t['row']
            f.write(json.dumps(dict(item_id=r['item_id'],source_unit=r['source_unit'],draft=t['operation'],operation='CUT_SOURCE',readout=t['readout'],mapping=t['mapping'],candidate_gold=gold,candidate_logprobs=lp,correct=float(max(range(2),key=lp.__getitem__)==gold),p_correct=math.exp(lp[gold]-den),prompt_sha256=digest(t['prompt']),removed_edges_per_layer=counts))+'\n')
            if j%64==0:f.flush();print('E77',a.model.name,a.shard,j+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E77 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--free-parent',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
