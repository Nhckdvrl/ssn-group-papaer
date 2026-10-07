"""E75: second Source cannot read first Source; Task still reads both."""
import argparse
import fcntl
import inspect
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha
from data_v2 import digest
from natural_cue_patching import blocks
from revision_interventions import token_region
from cue_interpretation_retention import prepare as parent_prepare


def prepare(rows,tok):
    tasks=parent_prepare(rows,tok)
    for t in tasks:
        r=t['row'];first,second=('gp','cue') if t['order']=='GP_CUE' else ('cue','gp')
        start=t['prompt'].index(r[first]);end=start+len(r[first]);second_start=end+2;second_end=second_start+len(r[second])
        t['sequences'],t['common']=t['encoded'];t['spans']=[];t['queries']=[]
        for s,c in zip(t['sequences'],['Yes','No']):
            z=tok(t['prompt']+c,return_offsets_mapping=True,add_special_tokens=not bool(tok.chat_template));assert z['input_ids']==s
            keys=token_region(z['offset_mapping'],start,end);queries=token_region(z['offset_mapping'],second_start,second_end)
            assert keys and queries and max(keys)<min(queries)
            assert not (t['prompt']+c)[second_end:z['offset_mapping'][max(queries)][1]].strip()
            t['spans'].append((keys,min(queries)));t['queries'].append(queries)
    return tasks


def forward(model,decoder,t,pad,cut=False,hidden=False,use_4d=True):
    import torch
    ss=t['sequences'];width=max(map(len,ss));ids=torch.full((2,width),pad,dtype=torch.long,device=model.device);valid=torch.zeros_like(ids)
    masks=[];counts=[]
    for i,s in enumerate(ss):
        offset=width-len(s);ids[i,offset:]=torch.tensor(s,device=model.device);valid[i,offset:]=1
        allowed=torch.ones(width,width,dtype=torch.bool,device=model.device).tril();allowed[offset:,:offset]=False
        native=allowed.clone();keys,first=t['spans'][i]
        if cut:
            q=torch.tensor(t['queries'][i],device=model.device)+offset;k=torch.tensor(keys,device=model.device)+offset
            allowed[q[:,None],k[None,:]]=False
        removed=native&~allowed;qq,kk=removed.nonzero(as_tuple=True)
        assert all(x>=first+offset for x in qq.tolist()) and set(kk.tolist())<=set(k+offset for k in keys)
        assert not ((~native)&allowed).any()
        if cut: assert set(qq.tolist())<=set(v+offset for v in t['queries'][i])
        m=torch.zeros((1,width,width),dtype=model.dtype,device=model.device).masked_fill(~allowed,torch.finfo(model.dtype).min)
        masks.append(m);counts.append(int(removed.sum()))
    positions=valid.cumsum(-1)-1;positions.masked_fill_(valid==0,0)
    kw=dict(input_ids=ids,attention_mask=torch.stack(masks) if use_4d else valid,position_ids=positions,use_cache=False,output_hidden_states=hidden)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters:kw['logits_to_keep']=0
    handles=[];calls=[]
    if use_4d:
        for layer,b in enumerate(decoder):
            def hook(module,args,kwargs,layer=layer):
                assert kwargs['attention_mask'].shape==kw['attention_mask'].shape;calls.append(layer)
                return args,dict(kwargs,attention_mask=kw['attention_mask'])
            handles.append(b.register_forward_pre_hook(hook,with_kwargs=True))
    try:
        with torch.inference_mode():out=model(**kw)
        if use_4d:assert calls==list(range(len(decoder)))
        values=[]
        for i,s in enumerate(ss):
            offset=width-len(s);n=t['common'];lp=out.logits[i,offset+n-1:offset+len(s)-1].float().log_softmax(-1)
            targets=ids[i,offset+n:offset+len(s)];values.append(float(lp.gather(-1,targets[:,None]).sum()))
        return values,out.hidden_states if hidden else None,counts
    finally:
        for h in handles:h.remove()


def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(75);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    rows=list(map(json.loads,a.data.read_text().splitlines()));assert json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']==sha(a.data)
    rows=[r for r in rows if int(r['item_id'][:16],16)%a.shards==a.shard];assert rows
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks=prepare(rows,tok);cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    parent=Path(a.parent)/'runs-v1'/a.model.name/str(a.shard);pcfg=json.loads((parent/'config.json').read_text())
    assert pcfg['predictions_sha256']==sha(parent/'predictions.jsonl') and pcfg['data_sha256']==sha(a.data) and pcfg['model_manifest_sha256']==sha(a.model/'manifest.json')
    base={(r['item_id'],r['order'],r['target']):r for r in map(json.loads,(parent/'predictions.jsonl').read_text().splitlines())}
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();decoder=blocks(model);uid=min(r['item_id'] for r in rows);checks=[]
    for t in [t for t in tasks if t['row']['item_id']==uid]:
        lp,hs,_=forward(model,decoder,t,tok.pad_token_id,hidden=True);ref,_,_=forward(model,decoder,t,tok.pad_token_id,use_4d=False)
        _,changed,counts=forward(model,decoder,t,tok.pad_token_id,cut=True,hidden=True)
        old=base[uid,t['order'],t['target']];assert old['prompt_sha256']==digest(t['prompt'])
        delta=max(abs(x-y) for x,y in zip(lp,ref));old_delta=max(abs(x-y) for x,y in zip(lp,old['candidate_logprobs']));assert max(delta,old_delta)<.001
        maximum=0.
        for x,y in zip(hs,changed):
            for i,s in enumerate(t['sequences']):
                offset=x.shape[1]-len(s);end=t['spans'][i][1];maximum=max(maximum,float((x[i,offset:offset+end]-y[i,offset:offset+end]).abs().max()))
        assert maximum==0.
        checks.append(dict(item_id=uid,order=t['order'],target=t['target'],native_LP_max_delta=delta,parent_LP_max_delta=old_delta,first_source_hidden_max_delta=maximum,removed_edges_per_layer=counts,task_queries_unchanged_mask=True))
    a.out.mkdir(exist_ok=True,parents=True);assert not (a.out/'predictions.jsonl').exists()
    config=dict(data_sha256=sha(a.data),model_manifest_sha256=sha(a.model/'manifest.json'),code_sha256=sha(Path(__file__)),model_path=str(a.model),dtype='float32',attention='eager',seed=75,
        shard=a.shard,shards=a.shards,gpu=a.gpu,units=len(rows),tasks=len(tasks),instrument=checks,parent_predictions_sha256=pcfg['predictions_sha256'],parent_config_sha256=sha(parent/'config.json'),
        dependencies={n:sha(Path(__file__).with_name(n)) for n in ['cue_interpretation_retention.py','natural_cue_patching.py','revision_interventions.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for j,t in enumerate(tasks):
            old=base[t['row']['item_id'],t['order'],t['target']];assert old['prompt_sha256']==digest(t['prompt'])
            lp,_,counts=forward(model,decoder,t,tok.pad_token_id,cut=True);m=max(lp);den=m+math.log(sum(math.exp(x-m) for x in lp));probs=[math.exp(x-den) for x in lp];gold=0 if t['row']['gold'][t['target']]=='Yes' else 1
            f.write(json.dumps(dict(item_id=t['row']['item_id'],order=t['order'],target=t['target'],operation='CUT_CROSS',candidate_logprobs=lp,probabilities=probs,correct=float(max(range(2),key=lp.__getitem__)==gold),p_correct=probs[gold],prompt_sha256=digest(t['prompt']),removed_edges_per_layer=counts))+'\n');f.flush()
            if j%20==0:print('E75',a.model.name,a.shard,j+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E75 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
