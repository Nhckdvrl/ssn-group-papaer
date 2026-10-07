"""E71: same correct first-clause prefill, native vs later-consumption cut."""
import argparse
import fcntl
import inspect
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha,write_jsonl
from data_v2 import digest
from natural_cue_patching import blocks
from reading_map import sequence_scores
from revision_interventions import token_region
from shared_source_cross_use import render


def freeze(root):
    report=json.loads((root/'step5/summary.json').read_text())
    assert report['items']==240 and report['unresolved']==0 and report['complete_both']==240
    assert report['data_sha256']==sha(root/'packets-v1.jsonl')
    assert report['annotated_sha256']==sha(root/'step5/annotated.jsonl')
    ann={r['item_id']:r for r in map(json.loads,(root/'step5/annotated.jsonl').read_text().splitlines())}
    draft=[json.loads(x) for x in (root/'draft-v1.jsonl').read_text().splitlines()]
    passed={};reasons={}
    for r in draft:
        bad=[]
        for role,uid in r['clause_atoms'].items():
            x=ann[uid];z=x['step5_annotation'];assert x['sentence_sha256']==r['sentence_sha256']
            if z['grammar']!='acceptable' or not all(p['grammar']=='acceptable' for p in x['step5_passes']):bad.append(role+':grammar')
            if (z['label']=='ENTAILED')!=(role!='p2_unsupported'):bad.append(role+':source-support')
        passed[r['item_id']]=not bad;reasons[r['item_id']]=bad
    bypair={}
    for r in draft:bypair.setdefault(r['pair_id'],[]).append(r)
    eligible=[];excluded=[]
    for pid,g in bypair.items():
        assert len(g)==2 and {x['condition'] for x in g}=={'gp','cue'}
        if all(passed[x['item_id']] for x in g):eligible.extend(g)
        else:excluded.append(dict(pair_id=pid,reasons={x['condition']:reasons[x['item_id']] for x in g}))
    out=root/'qualified-v1.jsonl';assert not out.exists();write_jsonl(out,eligible)
    m=dict(data_sha256=sha(out),draft_sha256=sha(root/'draft-v1.jsonl'),audit_summary=report,
        sources=len(eligible),clusters=len({r['cluster_id'] for r in eligible}),excluded=excluded,
        qualification_before_model_behavior=True)
    (root/'qualified-v1.manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m),flush=True)


def prepare(row,tok):
    task='Split the source faithfully into two simple sentences, preserving who did what. Use the format Sentence 1: ... and Sentence 2: ... .'
    stem=render(tok,row['sentence'],task);prefill='Sentence 1: '+row['p1']+'\n\nSentence 2: '
    prompt=stem+prefill;add=not bool(tok.chat_template)
    base=tok.encode(prompt,add_special_tokens=add);seq=[tok.encode(prompt+c,add_special_tokens=add) for c in row['candidates']]
    n=0
    for values in zip(base,*seq):
        if len(set(values))!=1:break
        n+=1
    assert n>0 and all(len(s)>n for s in seq)
    pstart=len(stem)+len('Sentence 1: ');qstart=len(stem)+len(prefill)-len('Sentence 2: ')
    spans=[]
    for cand,s in zip(row['candidates'],seq):
        z=tok(prompt+cand,return_offsets_mapping=True,add_special_tokens=add)
        assert z['input_ids']==s
        p=token_region(z['offset_mapping'],pstart,qstart)
        q=token_region(z['offset_mapping'],qstart,len(prompt+cand))
        assert p and q and max(p)<min(q) and min(q)<n
        spans.append((list(range(min(p),min(q))),min(q)))
    return dict(row=row,prompt=prompt,sequences=seq,common=n,spans=spans)


def forward(model,decoder,t,pad,cut=False,hidden=False,use_4d=True):
    import torch
    ss=t['sequences'];width=max(map(len,ss));ids=torch.full((2,width),pad,dtype=torch.long,device=model.device);valid=torch.zeros_like(ids)
    masks=[];counts=[]
    for i,s in enumerate(ss):
        offset=width-len(s);ids[i,offset:]=torch.tensor(s,device=model.device);valid[i,offset:]=1
        allowed=torch.ones(width,width,dtype=torch.bool,device=model.device).tril();allowed[offset:,:offset]=False
        native=allowed.clone();keys,first=t['spans'][i]
        if cut:
            q=torch.arange(first+offset,width,device=model.device);k=torch.tensor(keys,device=model.device)+offset
            allowed[q[:,None],k[None,:]]=False
        removed=native&~allowed;qq,kk=removed.nonzero(as_tuple=True)
        assert all(x>=first+offset for x in qq.tolist()) and set(kk.tolist())<=set(k+offset for k in keys)
        assert not ((~native)&allowed).any()
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
    torch.manual_seed(71);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    rows=[json.loads(x) for x in a.data.read_text().splitlines()];assert rows
    start=time.monotonic();tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();decoder=blocks(model)
    tasks=[prepare(r,tok) for r in rows];checks=[]
    for t in sorted(tasks,key=lambda x:x['row']['item_id'])[:4]:
        native,states,_=forward(model,decoder,t,tok.pad_token_id,hidden=True)
        ref,_,_=forward(model,decoder,t,tok.pad_token_id,use_4d=False)
        changed,hs,counts=forward(model,decoder,t,tok.pad_token_id,cut=True,hidden=True)
        diff=max(abs(x-y) for x,y in zip(native,ref));assert diff<.001
        maximum=0
        for x,y in zip(states,hs):
            for i,s in enumerate(t['sequences']):
                off=x.shape[1]-len(s);q=t['spans'][i][1];maximum=max(maximum,float((x[i,off:off+q]-y[i,off:off+q]).abs().max()))
        assert maximum==0,'Earlier/source/first-clause computation changed'
        checks.append(dict(item_id=t['row']['item_id'],native_LP_max_difference=diff,earlier_hidden_max_difference=maximum,removed_edges=counts))
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    (a.out/'instrument.json').write_text(json.dumps(checks,indent=2)+'\n')
    config=dict(data_sha256=sha(a.data),model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),code_sha256=sha(Path(__file__)),dtype='float32',attention='eager',seed=71,sources=len(rows),tasks=2*len(rows),gpu_index=a.gpu,phase='science')
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for j,t in enumerate(tasks):
            for op,cut in [('NATIVE',False),('CUT_P1',True)]:
                lp,_,counts=forward(model,decoder,t,tok.pad_token_id,cut=cut);den=max(lp)+math.log(sum(math.exp(x-max(lp)) for x in lp))
                r=dict(t['row'],operation=op,candidate_logprobs=lp,p_correct=math.exp(lp[0]-den),correct=lp[0]>lp[1],margin=lp[0]-lp[1],prompt_sha256=digest(t['prompt']),candidate_token_counts=[len(s)-t['common'] for s in t['sequences']],removed_edges_per_layer=counts)
                f.write(json.dumps(r)+'\n');f.flush()
            if (j+1)%10==0:print('E71',j+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    (a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E71 complete',a.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['freeze','run']);p.add_argument('--root',type=Path);p.add_argument('--data',type=Path);p.add_argument('--model',type=Path);p.add_argument('--out',type=Path);p.add_argument('--gpu',type=int);a=p.parse_args()
    if a.mode=='freeze':freeze(a.root)
    else:run(a)
