"""E85 fixed-layout native scoring of the original published coherence task."""
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
from current_open_baseline import tokenizer
from lexical_semantic_recovery import prepare

def prefix_scores(model,tasks,pad_id):
    import torch
    seqs=[t['sequences'][0][:t['common']] for t in tasks];width=max(map(len,seqs))
    ids=torch.full((len(seqs),width),pad_id,dtype=torch.long,device=model.device);mask=torch.zeros_like(ids)
    for i,s in enumerate(seqs):ids[i,-len(s):]=torch.tensor(s,device=model.device);mask[i,-len(s):]=1
    pos=mask.cumsum(-1)-1;pos.masked_fill_(mask==0,0)
    kwargs=dict(input_ids=ids,attention_mask=mask,position_ids=pos,use_cache=False)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters:kwargs['logits_to_keep']=1
    with torch.inference_mode():lp=model(**kwargs).logits[:,-1].float().log_softmax(-1)
    return [[float(lp[i,s[-1]]) for s in t['sequences']] for i,t in enumerate(tasks)]


def full_scores(model,tasks,pad_id):
    import torch
    seqs=[s for t in tasks for s in t['sequences']];width=max(map(len,seqs))
    ids=torch.full((len(seqs),width),pad_id,dtype=torch.long,device=model.device);mask=torch.zeros_like(ids)
    for i,s in enumerate(seqs):ids[i,-len(s):]=torch.tensor(s,device=model.device);mask[i,-len(s):]=1
    pos=mask.cumsum(-1)-1;pos.masked_fill_(mask==0,0)
    kwargs=dict(input_ids=ids,attention_mask=mask,position_ids=pos,use_cache=False)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters:kwargs['logits_to_keep']=2
    with torch.inference_mode():lp=model(**kwargs).logits[:,-2].float().log_softmax(-1)
    values=[float(lp[i,s[-1]]) for i,s in enumerate(seqs)]
    return [[values[i],values[i+1]] for i in range(0,len(values),2)]


def run(a):
    import torch,transformers
    from transformers import AutoConfig,AutoModelForImageTextToText,FineGrainedFP8Config
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(85);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    assert (a.model/'manifest.json').exists(),'Only complete SHA-verified asset set may run'
    assert sha(a.data)==json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']
    allrows=list(map(json.loads,a.data.read_text().splitlines()));rows=[r for r in allrows if int(r['sentence_sha256'][:16],16)%a.shards==a.shard]
    tok=tokenizer(a.model);tasks=prepare(rows,tok);cfg=AutoConfig.from_pretrained(a.model,local_files_only=True)
    start=time.monotonic();kwargs=dict(local_files_only=True,dtype=torch.bfloat16,attn_implementation='eager')
    if getattr(cfg,'quantization_config',None):
        quant=dict(cfg.quantization_config);quant['dequantize']=True;kwargs['quantization_config']=FineGrainedFP8Config(**quant)
    model=AutoModelForImageTextToText.from_pretrained(a.model,**kwargs).to('cuda').eval()
    fixed=min(r['source_unit'] for r in rows);checks=[];score=prefix_scores
    selected=[t for t in tasks if t['row']['source_unit']==fixed];delta=0
    for t in selected:
        v=prefix_scores(model,[t],tok.pad_token_id)[0];f=full_scores(model,[t],tok.pad_token_id)[0]
        delta=max(delta,*[abs(x-y) for x,y in zip(v,f)])
    if delta>=.001:score=full_scores
    for t in selected:
        one=score(model,[t],tok.pad_token_id)[0];two=score(model,[t],tok.pad_token_id)[0]
        repeat=max(abs(x-y) for x,y in zip(one,two));assert repeat==0
        checks.append(dict(item_id=t['row']['item_id'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],repeat_LP_max_delta=repeat))
    tasks.sort(key=lambda t:t['common']);a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    config=dict(model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),data_sha256=sha(a.data),
        code_sha256=sha(Path(__file__)),task_builder_sha256=sha(Path(__file__).with_name('lexical_semantic_recovery.py')),transformers=transformers.__version__,torch=torch.__version__,
        seed=85,dtype='bfloat16',logprobs_dtype='float32',attention='eager',shard=a.shard,shards=a.shards,
        gpu=a.gpu,QA=len(rows),tasks=len(tasks),score_function=score.__name__,prefix_full_LP_max_delta=delta,
        instrument=checks,thinking_enabled=False,official_empty_closed_thinking_boundary=True,
        released_quantization=getattr(cfg,'quantization_config',None),dequantized_to_bfloat16=bool(getattr(cfg,'quantization_config',None)),
        fixed_layout='One task per scoring call for all conditions; no batch-layout changes')
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as stream:
        for i,t in enumerate(tasks):
            lp=score(model,[t],tok.pad_token_id)[0];mx=max(lp);den=mx+math.log(sum(math.exp(x-mx) for x in lp));r=t['row'];gold=t['candidate_gold']
            stream.write(json.dumps(dict(item_id=r['item_id'],source_unit=r['source_unit'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],candidate_gold=gold,
                candidate_logprobs=lp,correct=max(range(2),key=lp.__getitem__)==gold,p_correct=math.exp(lp[gold]-den),prompt_sha256=digest(t['prompt']),prompt_tokens=t['common']))+'\n')
            if i%128==0:stream.flush();print('E85',a.model.name,a.shard,i+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print('E85 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['data','model','out']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1)
    run(p.parse_args())
