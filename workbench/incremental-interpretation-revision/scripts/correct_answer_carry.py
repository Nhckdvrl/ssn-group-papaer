"""E73: cut correct first-label consumption in the original joint task."""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE, sha
from data_v2 import digest
from joint_relation_use import prepare as joint_prepare
from revision_interventions import token_region
from run_correct_prefix_binding import forward
from natural_cue_patching import blocks


def prepare(rows, tok):
    tasks=[]
    for old in joint_prepare(rows,tok):
        if old['operation']!='JOINT':continue
        first=old['row']['gold'][old['order']]
        selected=[i for i,c in enumerate(old['candidates']) if c.split('; ')[0]==first]
        assert [old['candidates'][i].split('; ')[1] for i in selected]==['Yes','No']
        seq,common=old['encoded'];sequences=[seq[i] for i in selected];spans=[]
        for i,s in zip(selected,sequences):
            text=old['prompt']+old['candidates'][i]
            z=tok(text,return_offsets_mapping=True,add_special_tokens=not bool(tok.chat_template))
            assert z['input_ids']==s
            start=len(old['prompt']);end=start+len(first)
            keys=token_region(z['offset_mapping'],start,end)
            queries=token_region(z['offset_mapping'],end,len(text))
            assert keys and queries and max(keys)<min(queries),(keys,queries)
            spans.append((keys,min(queries)))
        tasks.append(dict(row=old['row'],order=old['order'],target='final' if old['order']==0 else 'initial',
            prompt=old['prompt'],sequences=sequences,common=common,spans=spans,
            first_gold=first,second_gold=old['row']['gold'][1-old['order']]))
    assert len(tasks)==2*len(rows)
    return tasks


def run(a):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(73);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    rows=[json.loads(s) for s in a.data.read_text().splitlines()]
    assert json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']==sha(a.data)
    rows=[r for r in rows if int(r['sentence_sha256'][:16],16)%a.shards==a.shard]
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks=prepare(rows,tok);start=time.monotonic()
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    decoder=blocks(model);checks=[];uid=min(r['item_id'] for r in rows)
    for t in [t for t in tasks if t['row']['item_id']==uid]:
        lp,hs,_=forward(model,decoder,t,tok.pad_token_id,hidden=True)
        ref,_,_=forward(model,decoder,t,tok.pad_token_id,use_4d=False)
        _,changed,counts=forward(model,decoder,t,tok.pad_token_id,cut=True,hidden=True)
        delta=max(abs(x-y) for x,y in zip(lp,ref));assert delta<.001,delta
        maximum=0.
        for x,y in zip(hs,changed):
            for i,s in enumerate(t['sequences']):
                offset=x.shape[1]-len(s);end=t['spans'][i][1]
                maximum=max(maximum,float((x[i,offset:offset+end]-y[i,offset:offset+end]).abs().max()))
        assert maximum==0.
        checks.append(dict(item_id=uid,order=t['order'],native_LP_max_delta=delta,prefix_hidden_max_delta=maximum,removed_edges_per_layer=counts))
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    config=dict(data_sha256=sha(a.data),code_sha256=sha(Path(__file__)),model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),
        dtype='float32',attention='eager',seed=73,shard=a.shard,shards=a.shards,gpu=a.gpu,units=len(rows),tasks=2*len(tasks),instrument=checks,
        dependencies={n:sha(Path(__file__).with_name(n)) for n in ['joint_relation_use.py','run_correct_prefix_binding.py','natural_cue_patching.py','revision_interventions.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for j,t in enumerate(tasks):
            for op,cut in [('NATIVE',False),('CUT_FIRST',True)]:
                lp,_,counts=forward(model,decoder,t,tok.pad_token_id,cut=cut)
                m=max(lp);den=m+math.log(sum(math.exp(x-m) for x in lp));probs=[math.exp(x-den) for x in lp]
                gold=0 if t['second_gold']=='Yes' else 1
                record=dict(item_id=t['row']['item_id'],operation=op,order=t['order'],target=t['target'],first_gold=t['first_gold'],second_gold=t['second_gold'],
                    candidate_logprobs=lp,probabilities=probs,correct=float(max(range(2),key=lp.__getitem__)==gold),p_correct=probs[gold],
                    prompt_sha256=digest(t['prompt']),removed_edges_per_layer=counts)
                f.write(json.dumps(record)+'\n');f.flush()
            if j%20==0:print('E73',a.model.name,a.shard,j+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    (a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print('E73 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
