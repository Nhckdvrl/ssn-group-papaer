"""E55 finite source-only residual patches from paired natural cue sentences."""
import argparse
import collections
import difflib
import fcntl
import inspect
import json
import math
import os
from pathlib import Path
import time

from data import CACHE, sha, write_jsonl
from data_v2 import digest
from prequestion_oracle_map import load, normalized_words, regions
from revision_interventions import word_character_spans, token_region


def build(data, out):
    rows = load(data)
    sources = collections.defaultdict(set)
    for r in rows:
        if r['condition']=='gp' and r.get('disamb_word_index') is not None:
            sources[(r['source'],r['sentence_sha256'])].add(r['disamb_word_index'])
    pairs = collections.defaultdict(list)
    for r in rows:
        pairs[(r.get('analysis_pair_id',r['pair_id']),r['question'])].append(r)
    result, excluded = [], []
    for key, group in pairs.items():
        gp=next(r for r in group if r['condition']=='gp')
        cue=next(r for r in group if r['condition']=='control')
        landmarks=sources.get((gp['source'],gp['sentence_sha256']),set())
        if not gp['oracle_anchor'] or len(landmarks)!=1:
            excluded.append(dict(pair=key,reason='No existing consistent span and disambiguating word'))
            continue
        a,b=normalized_words(gp['sentence']),normalized_words(cue['sentence'])
        mapping={}
        for match in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_matching_blocks():
            mapping.update((match.a+i,match.b+i) for i in range(match.size))
        start,end=gp['oracle_anchor']['span']
        words={'ambiguous':list(range(start,end)), 'disambiguating':[next(iter(landmarks))], 'last':[len(a)-1]}
        if any(i not in mapping for region in words.values() for i in region):
            excluded.append(dict(pair=key,reason='Selected source words do not all align'))
            continue
        for r in group:
            receiver_words=words if r['condition']=='gp' else {k:[mapping[i] for i in v] for k,v in words.items()}
            donor=cue if r['condition']=='gp' else gp
            donor_words={k:[mapping[i] for i in v] for k,v in words.items()} if r['condition']=='gp' else words
            result.append(dict(r,patch_words=receiver_words,donor_words=donor_words,donor_item_id=donor['item_id']))
    assert not out.exists()
    out.parent.mkdir(parents=True,exist_ok=True)
    write_jsonl(out,result)
    write_jsonl(out.with_suffix('.excluded.jsonl'),excluded)
    original={r['item_id']:r for r in rows}
    for r in result:
        assert original[r['item_id']]=={k:v for k,v in r.items() if k not in ['patch_words','donor_words','donor_item_id']}
    groups=collections.defaultdict(set)
    for r in result:
        if r['condition']=='gp':groups[(r['source'],r['sentence_sha256'])].add(r['analysis_question_target'])
    manifest=dict(input_path=str(data),input_sha256=sha(data),data_sha256=sha(out),rows=len(result),
        question_pairs=len(result)//2,unique_gp_sources=len(groups),multi_use_sources=sum({'initial','final'} <= v for v in groups.values()),
        construction_counts=dict(collections.Counter(r['construction'] for r in result if r['condition']=='gp')),
        exclusions=len(excluded),policy='Existing sentence-level T2 only; exact normalized word sequence alignment; no model outcomes or new gold.')
    out.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2),flush=True)


def word_tokens(tokenizer, task, encoded, words):
    row=task['row'];prompt=task['prompt'];start=prompt.index(row['sentence'])
    offsets=tokenizer(prompt,return_offsets_mapping=True,add_special_tokens=not bool(tokenizer.chat_template))['offset_mapping']
    spans=word_character_spans(row['sentence'])
    return {name:[token_region(offsets,start+spans[i][0],start+spans[i][1]) for i in indices]
            for name,indices in words.items()}


def prepare(rows, tokenizer, n_layers):
    from source_scope_map import tasks
    from reading_map import encode_choices
    baseline=[t for t in tasks(rows,tokenizer) if t['scope']=='G2' and t['reading']=='R0']
    prepared={};prefixes={};source_tokens={};invalid=set();excluded=[]
    for t in baseline:
        r=t['row'];encoded=encode_choices(tokenizer,t)
        assert all(len(s)==encoded[1]+1 for s in encoded[0])
        tokens,_=regions(tokenizer,t,encoded)
        prefix=encoded[0][0][:tokens[-1]+1]
        uid=r['item_id']
        if uid in prefixes:assert prefixes[uid]==prefix
        prefixes[uid]=prefix;source_tokens[uid]=tokens
        prepared[(uid,t['readout'],t['mapping'])]=dict(t,encoded=encoded,source_tokens=tokens,
            word_tokens=word_tokens(tokenizer,t,encoded,r['patch_words']))
    for k,t in prepared.items():
        r=t['row'];donor=prepared[(r['donor_item_id'],t['readout'],t['mapping'])]
        for name in r['patch_words']:
            a,b=t['word_tokens'][name],donor['word_tokens'][name]
            if len(a)!=len(b) or any(not x or len(x)!=len(y) for x,y in zip(a,b)):
                invalid.add((r.get('analysis_pair_id',r['pair_id']),r['question']))
    source_prefixes={}
    for t in prepared.values():
        r=t['row'];source=(r['source'],r['sentence_sha256'])
        if source in source_prefixes:assert source_prefixes[source]==prefixes[r['item_id']], 'Source prefix changed across questions'
        source_prefixes[source]=prefixes[r['item_id']]
    selected=[]
    layers=sorted({math.floor(f*(n_layers-1)) for f in (.25,.5,.75,1.)})
    assert len(layers)==4
    for k,t in prepared.items():
        r=t['row'];pair=(r.get('analysis_pair_id',r['pair_id']),r['question'])
        if pair in invalid:
            if t['readout']=='words' and t['mapping']==0:excluded.append(dict(item_id=r['item_id'],pair=pair,reason='Corresponding selected word token counts differ; both sides excluded'))
            continue
        selected.append(dict(t,operation='BASE',layer=None,region=None,patch_tokens=[],donor_tokens=[]))
        donor=prepared[(r['donor_item_id'],t['readout'],t['mapping'])]
        for layer in layers:
            for name in r['patch_words']:
                selected.append(dict(t,operation='PAIR',layer=layer,region=name,
                    patch_tokens=[i for word in t['word_tokens'][name] for i in word],
                    donor_tokens=[i for word in donor['word_tokens'][name] for i in word]))
    assert {t['row']['item_id'] for t in selected}=={t['row']['donor_item_id'] for t in selected}
    return selected,prefixes,source_tokens,layers,excluded


def blocks(model):
    if hasattr(model,'language_model'):return model.language_model.model.layers
    return model.model.layers


def unpack(output):
    return output[0] if isinstance(output,tuple) else output


def donor_cache(model, decoder, prefixes, source_tokens, layers):
    import torch
    cache={};by_prefix={}
    for uid,prefix in prefixes.items():
        prefix_key=tuple(prefix)
        if prefix_key in by_prefix:
            cache[uid]=by_prefix[prefix_key]
            continue
        handles=[];collected={}
        def capture(layer):
            def hook(module,inputs,output):
                collected[layer]=unpack(output)[0,source_tokens[uid]].detach().cpu().clone()
            return hook
        for layer in layers:handles.append(decoder[layer].register_forward_hook(capture(layer)))
        try:
            ids=torch.tensor([prefix],device=model.device)
            kw=dict(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False)
            if 'logits_to_keep' in inspect.signature(model.forward).parameters:kw['logits_to_keep']=1
            with torch.inference_mode():model(**kw)
        finally:
            for handle in handles:handle.remove()
        assert set(collected)==set(layers)
        cache[uid]={layer:{position:collected[layer][i] for i,position in enumerate(source_tokens[uid])} for layer in layers}
        by_prefix[prefix_key]=cache[uid]
    return cache


def score(model, decoder, cache, batch, pad):
    import torch
    layer=batch[0]['layer']
    assert all(t['layer']==layer for t in batch)
    prefixes=[t['encoded'][0][0][:t['encoded'][1]] for t in batch]
    width=max(map(len,prefixes));ids=torch.full((len(batch),width),pad,device=model.device,dtype=torch.long)
    mask=torch.zeros_like(ids)
    for i,prefix in enumerate(prefixes):ids[i,width-len(prefix):]=torch.tensor(prefix,device=model.device);mask[i,width-len(prefix):]=1
    positions=mask.cumsum(-1)-1;positions.masked_fill_(mask==0,0)
    def patch(module,inputs,output):
        hidden=unpack(output).clone()
        for i,t in enumerate(batch):
            uid=t['row']['donor_item_id'] if t['operation']=='PAIR' else t['row']['item_id']
            donor_positions=t['donor_tokens'] if t['operation']=='PAIR' else t['patch_tokens']
            for receiver,donor in zip(t['patch_tokens'],donor_positions):
                hidden[i,receiver+width-len(prefixes[i])]=cache[uid][layer][donor].to(hidden.device)
        return (hidden,*output[1:]) if isinstance(output,tuple) else hidden
    handle=decoder[layer].register_forward_hook(patch) if layer is not None else None
    try:
        kw=dict(input_ids=ids,attention_mask=mask,position_ids=positions,use_cache=False)
        if 'logits_to_keep' in inspect.signature(model.forward).parameters:kw['logits_to_keep']=1
        with torch.inference_mode():logp=model(**kw).logits[:,-1].float().log_softmax(-1)
        return [[float(logp[i,s[n]]) for s in t['encoded'][0]] for i,t in enumerate(batch) for n in [t['encoded'][1]]]
    finally:
        if handle:handle.remove()


def instrument(model, decoder, cache, tasks, layers, pad):
    import torch
    from source_scope_map import single_token_scores
    available=[t for t in tasks if t['operation']=='BASE']
    selected_sources=sorted({t['row']['sentence_sha256'] for t in available})[:4]
    first_ids={source:min(t['row']['item_id'] for t in available if t['row']['sentence_sha256']==source) for source in selected_sources}
    base=[t for t in available if t['row']['item_id'] in first_ids.values()]
    baseline=score(model,decoder,cache,base,pad)
    width=max(t['encoded'][1] for t in base)
    hidden_deltas=[];relative_deltas=[];hidden_scales=[];within_tolerance=[];handles=[]
    def compare(layer):
        def hook(module,inputs,output):
            hidden=unpack(output)
            for i,t in enumerate(base):
                for position in t['source_tokens']:
                    reference=cache[t['row']['item_id']][layer][position]
                    difference=hidden[i,position+width-t['encoded'][1]].detach().cpu()-reference
                    absolute=float(difference.abs().max())
                    relative=float(difference.double().norm()/reference.double().norm().clamp_min(1e-12))
                    hidden_deltas.append(absolute);relative_deltas.append(relative)
                    within_tolerance.append(absolute<1e-3 or relative<1e-5)
                    hidden_scales.append(float(reference.abs().max()))
        return hook
    for layer in layers:handles.append(decoder[layer].register_forward_hook(compare(layer)))
    try:score(model,decoder,cache,base,pad)
    finally:
        for handle in handles:handle.remove()
    direct=single_token_scores(model,[t['encoded'] for t in base],pad)
    direct_delta=max(abs(a-b) for aa,bb in zip(baseline,direct) for a,b in zip(aa,bb))
    self_deltas=[]
    for layer in layers:
        for region in ('ambiguous','disambiguating','last'):
            local=[]
            for t in base:
                tokens=[i for word in t['word_tokens'][region] for i in word]
                local.append(dict(t,operation='SELF',layer=layer,patch_tokens=tokens,donor_tokens=tokens))
            values=score(model,decoder,cache,local,pad)
            self_deltas.append(max(abs(a-b) for aa,bb in zip(baseline,values) for a,b in zip(aa,bb)))
    report=dict(item_ids=[t['row']['item_id'] for t in base],prefix_score_max_delta=direct_delta,
        source_prefix_self_patch_max_lp_delta=max(self_deltas),self_deltas=self_deltas,
        source_prefix_full_hidden_max_delta=max(hidden_deltas),
        source_prefix_full_hidden_max_relative_l2_delta=max(relative_deltas),source_hidden_max_absolute_scale=max(hidden_scales),
        source_hidden_every_position_within_absolute_or_relative_tolerance=all(within_tolerance),
        donor_policy='Truncated at last source token; shared across original questions/mappings/readouts, no answer tokens')
    assert max(direct_delta,*self_deltas)<1e-3 and all(within_tolerance), 'Source truncation/patch instrument failed: '+json.dumps(report)
    return report


def run(args):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(55);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    lock=(CACHE/'E52/gpu-slots'/str(args.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    start=time.monotonic();args.out.mkdir(parents=True,exist_ok=True)
    assert not (args.out/'predictions.jsonl').exists()
    manifest=json.loads(args.data.with_suffix('.manifest.json').read_text());assert manifest['data_sha256']==sha(args.data)
    rows=load(args.data)
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    cfg=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    decoder=blocks(model);selected,prefixes,source_tokens,layers,excluded=prepare(rows,tokenizer,len(decoder))
    write_jsonl(args.out/'tokenization-excluded.jsonl',excluded)
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        code_sha256=sha(Path(__file__)),layers=layers,regions=['ambiguous','disambiguating','last'],dtype='float32',attention='eager',
        seed=55,batch_size=args.batch_size,tasks=len(selected),eligible_qa=len({t['row']['item_id'] for t in selected}),gpu_index=args.gpu)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    eligible={t['row']['item_id'] for t in selected};prefixes={uid:prefix for uid,prefix in prefixes.items() if uid in eligible}
    cache=donor_cache(model,decoder,prefixes,source_tokens,layers)
    report=instrument(model,decoder,cache,selected,layers,tokenizer.pad_token_id)
    (args.out/'instrument.json').write_text(json.dumps(report,indent=2)+'\n')
    if args.instrument_only:
        (args.out/'instrument-only.json').write_text(json.dumps(dict(config,gpu_hours=(time.monotonic()-start)/3600),indent=2)+'\n')
        print('E55 instrument passed',args.model.name,'QA',config['eligible_qa'],'tasks',config['tasks'],flush=True);return
    torch.save(cache,args.out/'source-cache.pt')
    for name in ['natural_cue_patching.py','prequestion_oracle_map.py','source_scope_map.py','reading_map.py']:
        (args.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    selected.sort(key=lambda t:(-1 if t['layer'] is None else t['layer'],t['region'] or '',len(t['prompt'])))
    with (args.out/'predictions.jsonl').open('w') as stream:
        done=0
        for group_key,group in __import__('itertools').groupby(selected,key=lambda t:(t['layer'],t['region'])):
            group=list(group)
            for begin in range(0,len(group),args.batch_size):
                batch=group[begin:begin+args.batch_size];values=score(model,decoder,cache,batch,tokenizer.pad_token_id)
                for t,lp in zip(batch,values):
                    r=t['row'];den=max(lp)+math.log(sum(math.exp(v-max(lp)) for v in lp))
                    record={k:r[k] for k in ['item_id','source','construction','sentence_sha256','question','literal_label','source_gold_matches_grounding']}
                    record.update(pair_id=r.get('analysis_pair_id',r['pair_id']),cluster_id=r.get('analysis_cluster_id',r['cluster_id']),condition=r['condition'],
                        question_target=r['analysis_question_target'],operation=t['operation'],layer=t['layer'],region=t['region'],
                        readout=t['readout'],mapping=t['mapping'],candidate_gold=t['candidate_gold'],candidate_logprobs=lp,
                        correct=max(range(len(lp)),key=lp.__getitem__)==t['candidate_gold'],p_correct=math.exp(lp[t['candidate_gold']]-den),
                        prompt_sha256=digest(t['prompt']),patch_tokens=t['patch_tokens'],donor_tokens=t['donor_tokens'],donor_item_id=r['donor_item_id'])
                    stream.write(json.dumps(record)+'\n')
                stream.flush();done+=len(batch)
                if done%400==0:print(done,'/',len(selected),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),source_cache_sha256=sha(args.out/'source-cache.pt'),
        gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    print('Completed E55',args.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True);parser.add_argument('--build-out',type=Path)
    parser.add_argument('--model',type=Path);parser.add_argument('--out',type=Path);parser.add_argument('--gpu',type=int)
    parser.add_argument('--batch-size',type=int,default=4);parser.add_argument('--instrument-only',action='store_true')
    args=parser.parse_args()
    if args.build_out:build(args.data,args.build_out)
    else:assert args.model and args.out and args.gpu is not None;run(args)
