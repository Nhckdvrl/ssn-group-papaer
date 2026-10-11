"""E60 changes source-to-postsource access by depth; source computation stays causal."""
import argparse
import collections
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
from prequestion_oracle_map import load,make_tasks,tensors

OPERATIONS=('BASE','CUT_EARLY_QUARTER','CUT_LATE_QUARTER','CUT_EARLY_HALF','CUT_LATE_HALF')


def windows(n):
    k,h=n//4,n//2
    return dict(BASE=[],CUT_EARLY_QUARTER=list(range(k)),CUT_LATE_QUARTER=list(range(n-k,n)),
                CUT_EARLY_HALF=list(range(h)),CUT_LATE_HALF=list(range(n-h,n)))


def forward(model,decoder,batch,pad,hidden=False):
    import torch
    operation=batch[0]['operation'];assert all(t['operation']==operation for t in batch)
    kw=tensors(model,batch,pad)
    base=kw['attention_mask'];cut=base.clone();width=kw['input_ids'].shape[1]
    counts=[]
    for i,t in enumerate(batch):
        offset=width-t['encoded'][1];source=[j+offset for j in t['source_tokens']]
        after=list(range(source[-1]+1,width))
        q=torch.tensor(after,device=model.device,dtype=torch.long)
        k=torch.tensor(source,device=model.device,dtype=torch.long)
        cut[i,0,q[:,None],k[None,:]]=torch.finfo(model.dtype).min
        removed=(base[i,0]==0)&(cut[i,0]<0)
        qq,kk=removed.nonzero(as_tuple=True)
        assert set(qq.tolist()) <= set(after) and set(kk.tolist()) <= set(source)
        assert not ((base[i,0]<0)&(cut[i,0]==0)).any(), 'Future or previously forbidden edge added'
        counts.append(int(removed.sum()))
    selected=set(windows(len(decoder))[operation]);calls=collections.Counter();handles=[]
    def intercept(layer):
        def hook(module,args,kwargs):
            calls[layer]+=1
            assert kwargs['attention_mask'].shape==base.shape
            if layer in selected:return args,dict(kwargs,attention_mask=cut)
            return args,kwargs
        return hook
    for i,block in enumerate(decoder):handles.append(block.register_forward_pre_hook(intercept(i),with_kwargs=True))
    try:
        if hidden:kw['output_hidden_states']=True
        if 'logits_to_keep' in inspect.signature(model.forward).parameters:kw['logits_to_keep']=1
        with torch.inference_mode():output=model(**kw)
        assert calls=={i:1 for i in range(len(decoder))}, 'Not every block mask hook ran exactly once'
        logp=output.logits[:,-1].float().log_softmax(-1)
        values=[[float(logp[i,s[n]]) for s in t['encoded'][0]] for i,t in enumerate(batch) for n in [t['encoded'][1]]]
        return values,(output.hidden_states if hidden else None),counts
    finally:
        for handle in handles:handle.remove()


def instrument(model,decoder,tokenizer,tasks):
    import torch
    from source_scope_map import single_token_scores
    available=[t for t in tasks if t['operation']=='BASE']
    sources=sorted({t['row']['sentence_sha256'] for t in available})[:4]
    uids={s:min(t['row']['item_id'] for t in available if t['row']['sentence_sha256']==s) for s in sources}
    base=[t for t in available if t['row']['item_id'] in uids.values()]
    baseline,states,_=forward(model,decoder,base,tokenizer.pad_token_id,hidden=True)
    direct=single_token_scores(model,[t['encoded'] for t in base],tokenizer.pad_token_id)
    delta=max(abs(a-b) for aa,bb in zip(baseline,direct) for a,b in zip(aa,bb))
    assert delta<1e-3
    width=max(t['encoded'][1] for t in base)
    checks={}
    for operation in OPERATIONS[1:]:
        local=[dict(t,operation=operation) for t in base]
        values,altered,counts=forward(model,decoder,local,tokenizer.pad_token_id,hidden=True)
        abs_errors=[];rel_errors=[];valid=[]
        for original,changed in zip(states,altered):
            for i,t in enumerate(base):
                positions=[j+width-t['encoded'][1] for j in t['source_tokens']]
                difference=changed[i,positions]-original[i,positions]
                absolute=difference.abs().amax(-1)
                relative=difference.double().norm(dim=-1)/original[i,positions].double().norm(dim=-1).clamp_min(1e-12)
                abs_errors.append(float(absolute.max()));rel_errors.append(float(relative.max()))
                valid.append(bool(((absolute<1e-3)|(relative<1e-5)).all()))
        checks[operation]=dict(source_hidden_max_abs_delta=max(abs_errors),source_hidden_max_relative_l2_delta=max(rel_errors),
                               every_position_within_tolerance=all(valid),removed_edges_per_cut_layer=counts,
                               cut_layers=windows(len(decoder))[operation],scores=values)
        assert all(valid), 'Source computation changed under downstream-only mask: '+json.dumps(checks[operation])
    assert checks['CUT_EARLY_QUARTER']['removed_edges_per_cut_layer']==checks['CUT_LATE_QUARTER']['removed_edges_per_cut_layer']
    assert checks['CUT_EARLY_HALF']['removed_edges_per_cut_layer']==checks['CUT_LATE_HALF']['removed_edges_per_cut_layer']
    return dict(item_ids=[t['row']['item_id'] for t in base],base_4d_2d_max_lp_delta=delta,checks=checks,
                interpretation='Only source-to-postsource edges removed at chosen depth; source hidden computations unchanged. No future edges or candidate answers.')


def run(args):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(60);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    lock=(CACHE/'E52/gpu-slots'/str(args.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    start=time.monotonic();args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'predictions.jsonl').exists()
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    cfg=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    decoder=blocks(model);rows=load(args.data);prepared,_=make_tasks(rows,tokenizer)
    baseline=[t for t in prepared if t['operation']=='CAUSAL']
    assert len(baseline)==len(rows)*4
    selected=[dict(t,operation=operation,query_tokens=None) for t in baseline for operation in OPERATIONS]
    check=instrument(model,decoder,tokenizer,selected)
    (args.out/'instrument.json').write_text(json.dumps(check,indent=2)+'\n')
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        code_sha256=sha(Path(__file__)),dtype='float32',attention='eager',seed=60,batch_size=args.batch_size,gpu_index=args.gpu,
        tasks=len(selected),operations=dict(collections.Counter(t['operation'] for t in selected)),cut_layers=windows(len(decoder)))
    if args.instrument_only:
        (args.out/'instrument-only.json').write_text(json.dumps(dict(config,gpu_hours=(time.monotonic()-start)/3600),indent=2)+'\n')
        print('E60 instrument passed',args.model.name,flush=True);return
    for name in ['source_consumption_depth.py','prequestion_oracle_map.py','natural_cue_patching.py','source_scope_map.py','reading_map.py']:
        (args.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    selected.sort(key=lambda t:(t['operation'],len(t['prompt'])))
    with (args.out/'predictions.jsonl').open('w') as stream:
        done=0
        for operation,group in __import__('itertools').groupby(selected,key=lambda t:t['operation']):
            group=list(group)
            for begin in range(0,len(group),args.batch_size):
                batch=group[begin:begin+args.batch_size];values,_,edges=forward(model,decoder,batch,tokenizer.pad_token_id)
                for t,lp,count in zip(batch,values,edges):
                    r=t['row'];den=max(lp)+math.log(sum(math.exp(v-max(lp)) for v in lp))
                    record={k:r[k] for k in ['item_id','source','construction','sentence_sha256','question','literal_label','source_gold_matches_grounding']}
                    record.update(pair_id=r.get('analysis_pair_id',r['pair_id']),cluster_id=r.get('analysis_cluster_id',r['cluster_id']),condition=r['condition'],
                        question_target=r['analysis_question_target'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],
                        candidate_gold=t['candidate_gold'],candidate_logprobs=lp,correct=max(range(len(lp)),key=lp.__getitem__)==t['candidate_gold'],
                        p_correct=math.exp(lp[t['candidate_gold']]-den),prompt_sha256=digest(t['prompt']),source_tokens=t['source_tokens'],
                        cut_layers=config['cut_layers'][operation],removed_edges_per_cut_layer=count if operation!='BASE' else 0)
                    stream.write(json.dumps(record)+'\n')
                stream.flush();done+=len(batch)
                if done%400==0:print(done,'/',len(selected),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    print('Completed E60',args.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True);parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--gpu',type=int,required=True)
    parser.add_argument('--batch-size',type=int,default=4);parser.add_argument('--instrument-only',action='store_true');run(parser.parse_args())
