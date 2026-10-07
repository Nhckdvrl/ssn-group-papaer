"""E68: goals bypass source encoding and remain directly visible to consumers."""
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
from goal_conditioned_reading import prepare
from natural_cue_patching import blocks
from prequestion_oracle_map import tensors
from shared_source_cross_use import source_info
from revision_interventions import token_region


def locate(tasks,tok):
    for t in tasks:
        prompt=t['prompt'];prefix,source=source_info(tok,t)
        marker='Reading goal:\n' if t['primed_question'] is not None else 'Sentence:\n'
        start=prompt.index(marker);end=prompt.index(t['row']['sentence'])
        offsets=tok(prompt,return_offsets_mapping=True,add_special_tokens=not bool(tok.chat_template))['offset_mapping']
        region=token_region(offsets,start,end)
        assert region and min(region)<source[0]
        cut=list(range(min(region),source[0]))
        assert cut and max(cut)<min(source) and len(prefix)==source[-1]+1
        t.update(source_tokens=source,cut_tokens=cut,query_tokens=None)


def forward(model,decoder,batch,pad,cut=True,hidden=False):
    import torch
    kw=tensors(model,batch,pad);mask=kw['attention_mask'].clone();width=kw['input_ids'].shape[1];counts=[]
    for i,t in enumerate(batch):
        offset=width-t['encoded'][1];keys=[j+offset for j in t['cut_tokens']];after=[j+offset for j in t['source_tokens']]
        if cut:
            q=torch.tensor(after,device=model.device);k=torch.tensor(keys,device=model.device)
            mask[i,0,q[:,None],k[None,:]]=torch.finfo(model.dtype).min
        removed=(kw['attention_mask'][i,0]==0)&(mask[i,0]<0)
        qq,kk=removed.nonzero(as_tuple=True)
        assert set(qq.tolist())<=set(after) and set(kk.tolist())<=set(keys)
        assert not ((kw['attention_mask'][i,0]<0)&(mask[i,0]==0)).any()
        counts.append(int(removed.sum()))
    handles=[];calls=[]
    for layer,block in enumerate(decoder):
        def hook(module,args,kwargs,layer=layer):
            assert kwargs['attention_mask'].shape==mask.shape
            calls.append(layer);return args,dict(kwargs,attention_mask=mask)
        handles.append(block.register_forward_pre_hook(hook,with_kwargs=True))
    try:
        if hidden:kw['output_hidden_states']=True
        if 'logits_to_keep' in inspect.signature(model.forward).parameters:kw['logits_to_keep']=1
        with torch.inference_mode():out=model(**kw)
        assert calls==list(range(len(decoder)))
        lp=out.logits[:,-1].float().log_softmax(-1)
        values=[[float(lp[i,s[t['encoded'][1]]]) for s in t['encoded'][0]] for i,t in enumerate(batch)]
        return values,out.hidden_states if hidden else None,counts
    finally:
        for h in handles:h.remove()


def instrument(model,decoder,tok,tasks,reference):
    fixed=sorted({t['row']['source_unit'] for t in tasks})[:4];checks=[];maximum=0
    for uid in fixed:
        chosen=min(t['row']['item_id'] for t in tasks if t['row']['source_unit']==uid)
        for goal in ('NONE','INITIAL','FINAL'):
            batch=[t for t in tasks if t['row']['item_id']==chosen and t['operation']==goal]
            native,states,_=forward(model,decoder,batch,tok.pad_token_id,False,True)
            _,changed,counts=forward(model,decoder,batch,tok.pad_token_id,True,True)
            width=max(t['encoded'][1] for t in batch);absolute=relative=0;valid=True
            for a,b in zip(states,changed):
                for i,t in enumerate(batch):
                    pos=[j+width-t['encoded'][1] for j in range(t['source_tokens'][0])];d=b[i,pos]-a[i,pos]
                    ab=d.abs().amax(-1);re=d.double().norm(dim=-1)/a[i,pos].double().norm(dim=-1).clamp_min(1e-12)
                    absolute=max(absolute,float(ab.max()));relative=max(relative,float(re.max()));valid &= bool(((ab<.001)|(re<1e-5)).all())
            assert valid,'Goal or earlier pre-source computation changed'
            for t,lp in zip(batch,native):
                ref=reference[(t['row']['item_id'],goal,t['readout'],t['mapping'])]
                maximum=max(maximum,*[abs(a-b) for a,b in zip(lp,ref['candidate_logprobs'])])
            checks.append(dict(source=uid,goal=goal,max_presource_abs=absolute,max_presource_relative=relative,presource_identical_within_tolerance=valid,removed_edges=counts))
    assert maximum<.001
    return dict(native_E65_max_LP_difference=maximum,checks=checks,all_layers_hooked=True,no_future_edges=True)


def run(a):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(68);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    rows=[json.loads(x) for x in a.data.read_text().splitlines()];refcfg=json.loads((a.reference/'config.json').read_text())
    assert refcfg['data_sha256']==sha(a.data) and refcfg['predictions_sha256']==sha(a.reference/'predictions.jsonl')
    assert refcfg['model_manifest_sha256']==sha(a.model/'manifest.json')
    reference={(r['item_id'],r['operation'],r['readout'],r['mapping']):r for r in map(json.loads,(a.reference/'predictions.jsonl').read_text().splitlines())}
    start=time.monotonic();tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();decoder=blocks(model)
    tasks=prepare(rows,tok);locate(tasks,tok)
    assert len(tasks)==len(reference)==refcfg['tasks']
    for t in tasks:assert reference[(t['row']['item_id'],t['operation'],t['readout'],t['mapping'])]['prompt_sha256']==digest(t['prompt'])
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    check=instrument(model,decoder,tok,tasks,reference);(a.out/'instrument.json').write_text(json.dumps(check,indent=2)+'\n')
    config=dict(model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),data_sha256=sha(a.data),code_sha256=sha(Path(__file__)),
        reference_config_sha256=sha(a.reference/'config.json'),dtype='float32',attention='eager',seed=68,gpu_index=a.gpu,tasks=len(tasks),source_units=356,
        route='READ_ONLY',phase='instrument_only' if a.instrument_only else 'science',dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in ['goal_conditioned_reading.py','prequestion_oracle_map.py','shared_source_cross_use.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    if a.instrument_only:print('E68 instrument passed',a.model.name,flush=True);return
    tasks.sort(key=lambda t:len(t['prompt']))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),a.batch_size):
            batch=tasks[begin:begin+a.batch_size];values,_,counts=forward(model,decoder,batch,tok.pad_token_id)
            for t,lp,count in zip(batch,values,counts):
                r=dict(reference[(t['row']['item_id'],t['operation'],t['readout'],t['mapping'])]);den=max(lp)+math.log(sum(math.exp(x-max(lp)) for x in lp))
                r.update(candidate_logprobs=lp,correct=max(range(len(lp)),key=lp.__getitem__)==r['candidate_gold'],p_correct=math.exp(lp[r['candidate_gold']]-den),route='READ_ONLY',removed_edges_per_layer=count)
                f.write(json.dumps(r)+'\n')
            f.flush()
            if begin%512==0:print('E68 scores',begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    for n in ['goal_source_readout.py','goal_conditioned_reading.py','prequestion_oracle_map.py','shared_source_cross_use.py']:(a.out/n).write_bytes(Path(__file__).with_name(n).read_bytes())
    print('E68 complete',a.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--batch-size',type=int,default=4);p.add_argument('--instrument-only',action='store_true');run(p.parse_args())
