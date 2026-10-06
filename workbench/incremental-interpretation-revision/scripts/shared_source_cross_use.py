"""E63 task-after-source QA and free roles, with one source-only donor per use."""
import argparse
import collections
import fcntl
import inspect
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha,write_jsonl
from data_v2 import digest
from natural_cue_patching import blocks,donor_cache,score,word_tokens,unpack
from paraphrase_map import INSTRUCTION,sentence_parts
from reading_map import encode_choices
from revision_interventions import token_region
from source_scope_map import RULES,single_token_scores


def unit_key(r):
    return digest(json.dumps([r['sentence_sha256'],r['donor_sentence_sha256'],r['patch_words']['ambiguous'],r['donor_words']['ambiguous']],sort_keys=True))


def build(source,out):
    original=[json.loads(l) for l in source.read_text().splitlines()];index={r['item_id']:r for r in original}
    rows=[];units={}
    for r in original:
        d=index[r['donor_item_id']]
        x=dict(r,donor_sentence_sha256=d['sentence_sha256'])
        x['source_unit']='E63-source:'+unit_key(x)
        rows.append(x)
        if x['source_unit'] not in units:
            units[x['source_unit']]=dict(item_id=x['source_unit'],sentence=r['sentence'],sentence_sha256=r['sentence_sha256'],
                donor_sentence_sha256=d['sentence_sha256'],construction=r['construction'],condition=r['condition'],
                cluster_id=r['analysis_cluster_id'],member_ids=[])
        assert units[x['source_unit']]['cluster_id']==r['analysis_cluster_id']
        units[x['source_unit']]['member_ids'].append(r['item_id'])
    idx={r['item_id']:r for r in rows}
    for r in rows:r['donor_source_unit']=idx[r['donor_item_id']]['source_unit']
    assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
    write_jsonl(out,rows);write_jsonl(out.with_name('sources-v1.jsonl'),[units[k] for k in sorted(units)])
    manifest=dict(source_path=str(source),source_sha256=sha(source),data_sha256=sha(out),QA=len(rows),source_units=len(units),
        policy='No change to published source/question or gold. Units depend only on paired sources and existing spans.')
    out.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest),flush=True)


def render(tokenizer,sentence,task):
    body='Read this sentence carefully.\nSentence:\n'+sentence+'\n\nTask:\n'+task
    if tokenizer.chat_template:
        return tokenizer.apply_chat_template([dict(role='user',content=body)],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    return body+'\n\nAnswer:'


def source_info(tokenizer,t):
    p=t['prompt'];s=t['row']['sentence'];start=p.index(s);end=start+len(s)
    z=tokenizer(p,return_offsets_mapping=True,add_special_tokens=not bool(tokenizer.chat_template))
    tok=token_region(z['offset_mapping'],start,end)
    assert tok and not p[end:z['offset_mapping'][tok[-1]][1]].strip(),'Source token includes Task'
    return z['input_ids'][:tok[-1]+1],tok


def prepare(rows,tokenizer,layer):
    tasks=[];prefixes={};source_tokens={};invalid=set();idx={r['item_id']:r for r in rows};generations={}
    for r in rows:
        uid=r['source_unit']
        for readout in ('words','letters'):
            for mapping,shown in enumerate((['Yes','No'],['No','Yes'])):
                letters=['A','B'];task=RULES['G2']+'\nQuestion:\n'+r['question']+'\n'
                task+='\n'.join(f'{a}. {b}' for a,b in zip(letters,shown))
                task+='\nAnswer only '+('Yes or No.' if readout=='words' else 'A or B.')
                t=dict(row=r,prompt=render(tokenizer,r['sentence'],task),candidates=shown if readout=='words' else letters,
                    candidate_gold=shown.index(r['grounded_gold']),readout=readout,mapping=mapping,format='B')
                t['encoded']=encode_choices(tokenizer,t)
                assert all(len(s)==t['encoded'][1]+1 for s in t['encoded'][0])
                prefix,tok=source_info(tokenizer,t)
                assert prefix==t['encoded'][0][0][:len(prefix)]
                if uid in prefixes:assert prefixes[uid]==prefix
                prefixes[uid]=prefix;source_tokens[uid]=tok
                t['word_tokens']=word_tokens(tokenizer,t,t['encoded'],r['patch_words'])['ambiguous'];tasks.append(t)
        if uid not in generations:
            g=dict(row=r,prompt=render(tokenizer,r['sentence'],INSTRUCTION+'\nSplitted:'))
            prefix,tok=source_info(tokenizer,g);assert prefixes[uid]==prefix and source_tokens[uid]==tok
            g['ids']=tokenizer.encode(g['prompt'],add_special_tokens=not bool(tokenizer.chat_template))
            g['word_tokens']=word_tokens(tokenizer,g,None,r['patch_words'])['ambiguous'];generations[uid]=g
    index={(t['row']['item_id'],t['readout'],t['mapping']):t for t in tasks}
    for t in tasks:
        d=index[(t['row']['donor_item_id'],t['readout'],t['mapping'])]
        if any(not a or len(a)!=len(b) for a,b in zip(t['word_tokens'],d['word_tokens'])):
            invalid.add((t['row']['analysis_pair_id'],t['row']['question']))
    base=[t for t in tasks if (t['row']['analysis_pair_id'],t['row']['question']) not in invalid]
    eligible={t['row']['source_unit'] for t in base}
    gens=[g for uid,g in sorted(generations.items()) if uid in eligible]
    assert eligible=={g['row']['donor_source_unit'] for g in gens}
    # Same source occurrence and aligned word cardinality for every use.
    for g in gens:
        uid=g['row']['source_unit'];q=next(t for t in base if t['row']['source_unit']==uid)
        assert q['word_tokens']==g['word_tokens']
    selected=[]
    for t in base:
        r=t['row'];d=index[(r['donor_item_id'],t['readout'],t['mapping'])]
        for op in ('BASE','PAIR'):
            # Existing score helper keys caches by row donor_item_id; rebind to source units.
            row=dict(r,donor_item_id=r['donor_source_unit'],item_id=r['source_unit'])
            selected.append(dict(t,row=row,original_row=r,operation=op,layer=None if op=='BASE' else layer,
                patch_tokens=[i for word in t['word_tokens'] for i in word] if op=='PAIR' else [],
                donor_tokens=[i for word in d['word_tokens'] for i in word] if op=='PAIR' else []))
    for g in gens:
        d=generations[g['row']['donor_source_unit']]
        g.update(patch_tokens=[i for word in g['word_tokens'] for i in word],donor_tokens=[i for word in d['word_tokens'] for i in word])
        assert len(g['patch_tokens'])==len(g['donor_tokens'])
    return selected,gens,{u:prefixes[u] for u in eligible},{u:source_tokens[u] for u in eligible},sorted(invalid)


def replacement(model,decoder,cache,g,layer,op):
    """Patch source positions on every full-prefix recomputation, with task-unknown donor cache."""
    counts=[];uid=g['row']['source_unit'] if op=='SELF' else g['row']['donor_source_unit']
    source=g['patch_tokens'] if op=='SELF' else g['donor_tokens']
    def hook(module,args,output):
        h=unpack(output)
        if h.shape[1]==1:return output
        assert h.shape[0]==1 and h.shape[1]>=len(g['ids'])
        h=h.clone()
        for receiver,donor in zip(g['patch_tokens'],source):h[0,receiver]=cache[uid][layer][donor].to(h.device)
        counts.append(1)
        return (h,*output[1:]) if isinstance(output,tuple) else h
    handle=decoder[layer].register_forward_hook(hook) if op!='BASE' else None
    return handle,counts


def greedy(model,decoder,cache,g,layer,op,cap):
    import torch
    ids=torch.tensor([g['ids']],device=model.device);generated=[]
    ends=model.generation_config.eos_token_id
    ends=set(ends if isinstance(ends,list) else [ends])
    handle,count=replacement(model,decoder,cache,g,layer,op)
    try:
        for step in range(cap):
            kw=dict(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False)
            if 'logits_to_keep' in inspect.signature(model.forward).parameters:kw['logits_to_keep']=1
            with torch.inference_mode():output=model(**kw)
            token=int(output.logits[0,-1].argmax());generated.append(token)
            if token in ends:break
            ids=torch.cat([ids,torch.tensor([[token]],device=model.device)],1)
        assert len(count)==(0 if op=='BASE' else len(generated))
    finally:
        if handle:handle.remove()
    return generated


def instrument(model,decoder,tokenizer,cache,tasks,gens,layer):
    import torch
    fixed=sorted(gens,key=lambda g:g['row']['source_unit'])[:4]
    ids={g['row']['source_unit'] for g in fixed};base=[t for t in tasks if t['operation']=='BASE' and t['row']['source_unit'] in ids]
    direct=single_token_scores(model,[t['encoded'] for t in base],tokenizer.pad_token_id)
    values=score(model,decoder,cache,base,tokenizer.pad_token_id)
    direct_delta=max(abs(a-b) for x,y in zip(direct,values) for a,b in zip(x,y));assert direct_delta<.001
    selftasks=[dict(t,operation='SELF',layer=layer,patch_tokens=next(g['patch_tokens'] for g in fixed if g['row']['source_unit']==t['row']['source_unit']),donor_tokens=[]) for t in base]
    selfvalues=score(model,decoder,cache,selftasks,tokenizer.pad_token_id)
    selfdelta=max(abs(a-b) for x,y in zip(values,selfvalues) for a,b in zip(x,y));assert selfdelta<.001
    reports=[]
    for g in fixed:
        x=torch.tensor([g['ids']],device=model.device)
        collected={}
        def capture(module,args,output):collected['h']=unpack(output)[0,g['patch_tokens']].detach().clone()
        h=decoder[layer].register_forward_hook(capture)
        with torch.inference_mode():plain=model(input_ids=x,use_cache=False).logits[:,-1].float()
        h.remove();old=torch.stack([cache[g['row']['source_unit']][layer][i].to(model.device) for i in g['patch_tokens']])
        diff=collected['h']-old;absolute=diff.abs().amax(-1);relative=diff.double().norm(dim=-1)/old.double().norm(dim=-1).clamp_min(1e-12)
        assert bool(((absolute<.001)|(relative<1e-5)).all())
        h,count=replacement(model,decoder,cache,g,layer,'SELF')
        try:
            with torch.inference_mode():self_lp=model(input_ids=x,use_cache=False).logits[:,-1].float()
        finally:h.remove()
        lp_delta=float((plain.log_softmax(-1)-self_lp.log_softmax(-1)).abs().max());assert lp_delta<.001 and len(count)==1
        plain_tokens=greedy(model,decoder,cache,g,layer,'BASE',16)
        self_tokens=greedy(model,decoder,cache,g,layer,'SELF',16)
        assert plain_tokens==self_tokens, 'SELF changed fixed-input greedy continuation'
        reports.append(dict(source_unit=g['row']['source_unit'],source_max_abs=float(absolute.max()),source_max_rel_l2=float(relative.max()),self_lp_delta=lp_delta,self_greedy_tokens_identical=True))
    return dict(fixed_sources=reports,QA_independent_lp_delta=direct_delta,QA_self_lp_delta=selfdelta,
                all_task_source_prefixes_identical=True,source_only_no_task_cache=True)


def run(args):
    import torch
    from transformers import AutoTokenizer,AutoConfig,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(args.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(63);torch.set_num_threads(8);start=time.monotonic()
    args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'predictions.jsonl').exists()
    rows=[json.loads(l) for l in args.data.read_text().splitlines()]
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    decoder=blocks(model);layer=math.floor(.25*(len(decoder)-1))
    tasks,gens,prefixes,tokens,excluded=prepare(rows,tok,layer)
    write_jsonl(args.out/'tokenization-excluded.jsonl',[dict(pair=x,reason='Input-only paired selected-word token count differs') for x in excluded])
    cache_prefixes=prefixes
    if args.instrument_only:
        fixed=sorted(gens,key=lambda g:g['row']['source_unit'])[:4]
        fixed_ids={u for g in fixed for u in (g['row']['source_unit'],g['row']['donor_source_unit'])}
        cache_prefixes={u:prefixes[u] for u in fixed_ids}
    cache=donor_cache(model,decoder,cache_prefixes,tokens,[layer]);report=instrument(model,decoder,tok,cache,tasks,gens,layer)
    (args.out/'instrument.json').write_text(json.dumps(report,indent=2)+'\n')
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        code_sha256=sha(Path(__file__)),layer=layer,dtype='float32',attention='eager',seed=63,gpu_index=args.gpu,
        qa_tasks=len(tasks),source_units=len(gens),role_tasks=len(gens)*2,cap=args.cap,cohort=sorted(prefixes),
        decoding='Full-prefix FP32 recomputation; no KV-cache. Manual greedy argmax with pinned model EOS ids.',phase='instrument_only' if args.instrument_only else 'science')
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    if args.instrument_only:print('E63 instrument passed',args.model.name,len(tasks),len(gens),flush=True);return
    torch.save(cache,args.out/'source-cache.pt')
    for name in ('shared_source_cross_use.py','natural_cue_patching.py','paraphrase_map.py','reading_map.py','source_scope_map.py'):
        (args.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    tasks.sort(key=lambda t:(t['operation'],len(t['prompt'])))
    with (args.out/'qa-predictions.jsonl').open('w') as f:
        for op in ('BASE','PAIR'):
            group=[t for t in tasks if t['operation']==op]
            for begin in range(0,len(group),4):
                batch=group[begin:begin+4];values=score(model,decoder,cache,batch,tok.pad_token_id)
                for t,lp in zip(batch,values):
                    r=t['original_row'];den=max(lp)+math.log(sum(math.exp(v-max(lp)) for v in lp))
                    record={k:r[k] for k in ('item_id','sentence_sha256','question','construction','condition','source_gold_matches_grounding','literal_label','source_unit','donor_source_unit')}
                    record.update(operation=op,readout=t['readout'],mapping=t['mapping'],question_target=r['analysis_question_target'],cluster_id=r['analysis_cluster_id'],pair_id=r['analysis_pair_id'],candidate_gold=t['candidate_gold'],candidate_logprobs=lp,
                        correct=max(range(len(lp)),key=lp.__getitem__)==t['candidate_gold'],p_correct=math.exp(lp[t['candidate_gold']]-den),prompt_sha256=digest(t['prompt']))
                    f.write(json.dumps(record)+'\n')
                f.flush()
        print('E63 QA complete',len(tasks),flush=True)
    with (args.out/'predictions.jsonl').open('w') as f:
        for i,g in enumerate(gens):
            for op in ('BASE','PAIR'):
                generated=greedy(model,decoder,cache,g,layer,op,args.cap);text=tok.decode(generated,skip_special_tokens=True)
                r=g['row'];parts=sentence_parts(text)
                record=dict(item_id=r['source_unit'],sentence_sha256=r['sentence_sha256'],construction=r['construction'],condition=r['condition'],cluster_id=r['analysis_cluster_id'],format='TASK_AFTER_SOURCE',reading=op,
                    prompt_sha256=digest(g['prompt']),text=text,text_sha256=digest(text),generated_token_ids=generated,capped=len(generated)==args.cap,
                    finish_reason='length' if len(generated)==args.cap else 'stop',automatic_sentence_parts=parts,automatic_two_sentences=len(parts)==2,
                    donor_source_unit=r['donor_source_unit'],patch_tokens=g['patch_tokens'] if op=='PAIR' else [],layer=layer if op=='PAIR' else None)
                f.write(json.dumps(record)+'\n');f.flush()
            if (i+1)%10==0:print('E63 role sources',i+1,'/',len(gens),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),qa_predictions_sha256=sha(args.out/'qa-predictions.jsonl'),source_cache_sha256=sha(args.out/'source-cache.pt'),gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');print('Completed E63',args.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--build-out',type=Path)
    ap.add_argument('--model',type=Path);ap.add_argument('--out',type=Path);ap.add_argument('--gpu',type=int);ap.add_argument('--cap',type=int,default=256);ap.add_argument('--instrument-only',action='store_true')
    args=ap.parse_args()
    if args.build_out:build(args.data,args.build_out)
    else:assert args.model and args.out and args.gpu is not None;run(args)
