"""E54 sentence-bounded visibility interventions, frozen before GPU execution."""
import argparse
import collections
import difflib
import fcntl
import inspect
import json
import math
import os
from pathlib import Path
import re
import time

from data import CACHE, sha, write_jsonl


def load(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def normalized_words(sentence):
    return [word.strip('.,;:!?\"\'()').casefold() for word in sentence.split()]


def aligned_span(gp, cue, span):
    a, b = normalized_words(gp), normalized_words(cue)
    mapping = {}
    for match in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        mapping.update((match.a+i, match.b+i) for i in range(match.size))
    if not all(i in mapping for i in range(*span)):
        return None
    indices = [mapping[i] for i in range(*span)]
    assert indices == sorted(indices)
    return [indices[0], indices[-1]+1]


def build(data, out):
    rows = load(data)
    source = collections.defaultdict(list)
    pairs = collections.defaultdict(list)
    for row in rows:
        assert row['literal_label'] != 'PENDING'
        source[(row['source'], row['sentence_sha256'])].append(row)
        pairs[(row.get('analysis_pair_id', row['pair_id']), row['question'])].append(row)
    anchors = {}
    anchor_exclusions = []
    for key, group in source.items():
        positive = [r for r in group if r['condition'] == 'gp' and r.get('amb_span')]
        spans = {tuple(r['amb_span']) for r in positive}
        if len(spans) == 1:
            row = sorted(positive, key=lambda r: r['item_id'])[0]
            anchors[key] = dict(span=list(spans.pop()), item_id=row['item_id'])
        elif spans:
            anchor_exclusions.append(dict(source=key, reason='Conflicting existing positive T2 spans'))
    result = []
    exclusions = []
    for pair, group in pairs.items():
        assert {r['condition'] for r in group} == {'gp', 'control'}
        local = {}
        reason = None
        for row in group:
            if row['condition'] != 'gp':
                continue
            anchor = anchors.get((row['source'], row['sentence_sha256']))
            if not anchor:
                reason = 'No existing consistent sentence-level T2 anchor'
                break
            local[row['item_id']] = dict(span=anchor['span'], anchor_item_id=anchor['item_id'])
        if reason is None:
            gp = next(r for r in group if r['condition'] == 'gp')
            for row in group:
                if row['condition'] == 'control':
                    span = aligned_span(gp['sentence'], row['sentence'], local[gp['item_id']]['span'])
                    if span is None:
                        reason = 'GP anchor words do not align to cue words'
                        break
                    local[row['item_id']] = dict(span=span, anchor_item_id=local[gp['item_id']]['anchor_item_id'])
        if reason:
            exclusions.append(dict(pair=pair, reason=reason))
        for row in group:
            result.append(dict(row, oracle_anchor=None if reason else local[row['item_id']]))
    assert {r['item_id'] for r in result} == {r['item_id'] for r in rows}
    for original, transformed in zip(sorted(rows,key=lambda r:r['item_id']), sorted(result,key=lambda r:r['item_id'])):
        assert original == {k:v for k,v in transformed.items() if k != 'oracle_anchor'}
    out.parent.mkdir(parents=True, exist_ok=True)
    assert not out.exists()
    write_jsonl(out, result)
    write_jsonl(out.with_suffix('.locator-excluded.jsonl'), exclusions)
    groups = collections.defaultdict(set)
    for row in result:
        if row['condition'] == 'gp' and row['oracle_anchor']:
            groups[(row['source'], row['sentence_sha256'])].add(row['analysis_question_target'])
    manifest = dict(input_path=str(data),input_sha256=sha(data), data_sha256=sha(out),rows=len(result),
        locator_rows=sum(r['oracle_anchor'] is not None for r in result),locator_question_pairs=len(pairs)-len(exclusions),
        locator_unique_gp_sentences=len(groups),multi_purpose_gp_sentences=sum({'initial','final'} <= v for v in groups.values()),
        locator_by_construction=dict(collections.Counter(r['construction'] for r in result if r['condition']=='gp' and r['oracle_anchor'])),
        anchor_exclusions=anchor_exclusions, policy='Original qualified data/gold unchanged; same-sentence existing T2 anchors, exact-word cue alignment; no model outcomes used.',
        code_sha256=sha(Path(__file__)))
    out.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2),flush=True)


def regions(tokenizer, task, encoded):
    from revision_interventions import token_region, word_character_spans
    row = task['row']
    prompt = task['prompt']
    sentence = row['sentence']
    assert prompt.count(sentence) == 1
    start = prompt.index(sentence)
    policy = not bool(tokenizer.chat_template)
    tokenized = tokenizer(prompt, return_offsets_mapping=True, add_special_tokens=policy)
    sequences, common = encoded
    assert tokenized['input_ids'][:common-1] == sequences[0][:common-1]
    offsets = tokenized['offset_mapping']
    source_tokens = token_region(offsets,start,start+len(sentence))
    assert source_tokens and max(source_tokens) < common
    question_start = prompt.index('\n\nQuestion:',start+len(sentence))
    # Some tokenizers merge the final punctuation with following whitespace.
    # Permit only that whitespace, never any future question-marker/content bytes.
    sentence_end=start+len(sentence)
    for i in source_tokens:
        a,b=offsets[i]
        assert not prompt[max(sentence_end,a):b].strip(), 'Source token contains future non-whitespace content'
    anchor = row['oracle_anchor']
    ambiguous = None
    if anchor:
        words = word_character_spans(sentence)
        a,b = anchor['span']
        assert 0 <= a < b <= len(words)
        ambiguous = token_region(offsets,start+words[a][0],start+words[b-1][1])
        assert ambiguous and set(ambiguous) <= set(source_tokens)
    return source_tokens, ambiguous


def make_tasks(rows, tokenizer):
    from source_scope_map import tasks, render, RULES
    from reading_map import encode_choices, REPAIR
    selected = []
    locator_skipped = []
    base = [t for t in tasks(rows,tokenizer) if t['scope']=='G2' and t['reading']=='R0']
    prepared = []
    invalid_pairs = set()
    for task in base:
        encoded = encode_choices(tokenizer,task)
        ss,n = encoded
        assert all(len(s)==n+1 for s in ss)
        source_tokens, ambiguous = regions(tokenizer,task,encoded)
        nonambiguous = [i for i in source_tokens if ambiguous is not None and i not in ambiguous]
        if ambiguous and len(nonambiguous) < len(ambiguous):
            invalid_pairs.add((task['row'].get('analysis_pair_id',task['row']['pair_id']),task['row']['question']))
        prepared.append((task,encoded,source_tokens,ambiguous,nonambiguous))
    for task,encoded,source_tokens,ambiguous,nonambiguous in prepared:
        row = task['row']
        pair = (row.get('analysis_pair_id',row['pair_id']),row['question'])
        operations = [('CAUSAL',None),('SOURCE_ALL',source_tokens)]
        if ambiguous and pair not in invalid_pairs:
            operations += [('AMBIGUOUS',ambiguous),('NONAMBIGUOUS',nonambiguous[:len(ambiguous)])]
        elif ambiguous:
            locator_skipped.append(dict(item_id=row['item_id'],reason='Insufficient equal-count nonambiguous rows; both sides excluded'))
        for operation, queries in operations:
            selected.append(dict(task,operation=operation,encoded=encoded,source_tokens=source_tokens,query_tokens=queries))
        # Preserve exactly the original body; only add the registered one-line instruction.
        shown = task['displayed_options']
        body=f'Sentence:\n{row["sentence"]}\n\nQuestion:\n{row["question"]}\nA. {shown[0]}\nB. {shown[1]}\nAnswer only '+('A or B.' if task['readout']=='letters' else 'Yes or No.')
        repaired = dict(task,prompt=render(tokenizer,RULES['G2']+' '+REPAIR,body),operation='INSTRUCTION',query_tokens=None)
        repaired['encoded'] = encode_choices(tokenizer,repaired)
        repaired['source_tokens'], _ = regions(tokenizer,repaired,repaired['encoded'])
        selected.append(repaired)
    return selected, locator_skipped


def tensors(model, tasks, pad, use_4d=True):
    import torch
    from revision_interventions import oracle_mask
    prefixes = [t['encoded'][0][0][:t['encoded'][1]] for t in tasks]
    width = max(map(len,prefixes))
    ids = torch.full((len(tasks),width),pad,dtype=torch.long,device=model.device)
    valid = torch.zeros_like(ids)
    masks = []
    for i,(task,prefix) in enumerate(zip(tasks,prefixes)):
        offset = width-len(prefix)
        ids[i,offset:] = torch.tensor(prefix,device=model.device)
        valid[i,offset:] = 1
        source_tokens = [j+offset for j in task['source_tokens']]
        queries = [j+offset for j in task['query_tokens']] if task['query_tokens'] else None
        if queries:
            mask = oracle_mask(width,source_tokens,queries,model.dtype,model.device)[0]
        else:
            allowed=torch.ones(width,width,dtype=torch.bool,device=model.device).tril()
            mask=torch.zeros((1,width,width),dtype=model.dtype,device=model.device)
            mask.masked_fill_(~allowed,torch.finfo(model.dtype).min)
        # Nonpadding queries can never read padding keys; padding rows retain self edges.
        if offset:
            mask[:,offset:,:offset] = torch.finfo(model.dtype).min
        changed = (mask[0] == 0) & torch.ones(width,width,dtype=torch.bool,device=model.device).triu(1)
        if changed.any():
            q,k = changed.nonzero(as_tuple=True)
            assert set(q.tolist()) <= set(source_tokens) and set(k.tolist()) <= set(source_tokens)
        masks.append(mask)
    positions = valid.cumsum(-1)-1
    positions.masked_fill_(valid==0,0)
    return dict(input_ids=ids,attention_mask=torch.stack(masks) if use_4d else valid,position_ids=positions,use_cache=False)


def score(model,tasks,pad,use_4d=True):
    import torch
    kwargs=tensors(model,tasks,pad,use_4d)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters:
        kwargs['logits_to_keep']=1
    with torch.inference_mode():
        logp=model(**kwargs).logits[:,-1].float().log_softmax(-1)
    return [[float(logp[i,s[n]]) for s in ss] for i,t in enumerate(tasks) for ss,n in [t['encoded']]]


def instrument(model,tokenizer,tasks):
    import torch
    from source_scope_map import single_token_scores
    from reading_map import sequence_scores, encode_choices
    base=[t for t in tasks if t['operation']=='CAUSAL'][:8]
    four=score(model,base,tokenizer.pad_token_id)
    two=score(model,base,tokenizer.pad_token_id,use_4d=False)
    independent=single_token_scores(model,[t['encoded'] for t in base],tokenizer.pad_token_id)
    joint=sequence_scores(model,[s for t in base for s in t['encoded'][0]],
                          [t['encoded'][1] for t in base for s in t['encoded'][0]],tokenizer.pad_token_id)
    delta_joint=max(abs(a-b) for A,B in zip(four,[joint[i:i+2] for i in range(0,len(joint),2)]) for a,b in zip(A,B))
    delta=max(abs(a-b) for A,B in zip(four,two) for a,b in zip(A,B))
    delta_independent=max(abs(a-b) for A,B in zip(four,independent) for a,b in zip(A,B))
    report=dict(items=[t['row']['item_id'] for t in base],four_dimensional=four,two_dimensional=two,
        independent_prefix=independent,joint_sequence=joint,max_joint_delta=delta_joint,
        max_4d_2d_delta=delta,max_independent_delta=delta_independent)
    assert max(delta,delta_independent,delta_joint)<1e-3, 'Causal instrument failed; no effect interpretation permitted'
    # A future-question intervention is a direct test of the no-question-leak claim.
    original=next(t for t in tasks if t['operation']=='SOURCE_ALL')
    altered=dict(original,row=dict(original['row']))
    old_question=original['row']['question']
    new_question='Which relation does the supplied sentence express?'
    assert old_question in original['prompt']
    altered['prompt']=original['prompt'].replace(old_question,new_question)
    altered['row']['question']=new_question
    altered['encoded']=encode_choices(tokenizer,altered)
    altered['source_tokens'],_=regions(tokenizer,altered,altered['encoded'])
    altered['query_tokens']=altered['source_tokens']
    pair=[original,altered]
    kwargs=tensors(model,pair,tokenizer.pad_token_id)
    kwargs['output_hidden_states']=True
    if 'logits_to_keep' in inspect.signature(model.forward).parameters:kwargs['logits_to_keep']=1
    with torch.inference_mode():states=model(**kwargs).hidden_states
    width=kwargs['input_ids'].shape[1]
    indices=[[j+width-t['encoded'][1] for j in t['source_tokens']] for t in pair]
    assert len(indices[0])==len(indices[1])
    hidden_delta=max(float((h[0,indices[0]]-h[1,indices[1]]).abs().max()) for h in states)
    report['source_hidden_future_question_max_delta']=hidden_delta
    assert hidden_delta<1e-3, 'Oracle source states depend on future question; reject instrument'
    # Positive visibility control: append future source words, preserving its first
    # token. Causal computation must ignore them there; SOURCE_ALL must use them.
    extended=dict(original,row=dict(original['row']))
    old_sentence=original['row']['sentence']
    new_sentence=old_sentence+' Alternate future words with different evidence follow.'
    extended['prompt']=original['prompt'].replace(old_sentence,new_sentence)
    extended['row']['sentence']=new_sentence
    extended['encoded']=encode_choices(tokenizer,extended)
    extended['source_tokens'],_=regions(tokenizer,extended,extended['encoded'])
    extended['query_tokens']=extended['source_tokens']
    visibility={}
    for operation in ('CAUSAL','SOURCE_ALL'):
        comparison=[dict(t,operation=operation,query_tokens=None if operation=='CAUSAL' else t['source_tokens']) for t in (original,extended)]
        kw=tensors(model,comparison,tokenizer.pad_token_id)
        kw['output_hidden_states']=True
        if 'logits_to_keep' in inspect.signature(model.forward).parameters:kw['logits_to_keep']=1
        with torch.inference_mode():hs=model(**kw).hidden_states
        w=kw['input_ids'].shape[1]
        idx=[t['source_tokens'][0]+w-t['encoded'][1] for t in comparison]
        visibility[operation]=max(float((h[0,idx[0]]-h[1,idx[1]]).abs().max()) for h in hs)
    report['future_source_visibility_control']=visibility
    assert visibility['CAUSAL']<1e-3 and visibility['SOURCE_ALL']>1e-3, 'Visibility oracle inactive or causal future leakage'
    return report


def run(args):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    from data_v2 import digest
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(54)
    torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32=False
    lock=(CACHE/'E52/gpu-slots'/str(args.gpu)).open('a')
    fcntl.flock(lock,fcntl.LOCK_EX)
    start=time.monotonic()
    args.out.mkdir(parents=True,exist_ok=True)
    assert not (args.out/'predictions.jsonl').exists()
    rows=load(args.data)
    manifest=json.loads(args.data.with_suffix('.manifest.json').read_text())
    assert manifest['data_sha256']==sha(args.data)
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    cfg=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    selected, skipped=make_tasks(rows,tokenizer)
    check=instrument(model,tokenizer,selected)
    (args.out/'instrument.json').write_text(json.dumps(check,indent=2)+'\n')
    write_jsonl(args.out/'locator-tokenization-excluded.jsonl',skipped)
    if args.instrument_only:
        (args.out/'instrument-only.json').write_text(json.dumps(dict(gpu_hours=(time.monotonic()-start)/3600,model=str(args.model),data_sha256=sha(args.data)),indent=2)+'\n')
        print('E54 instrument passed',args.model.name,flush=True)
        return
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        code_sha256=sha(Path(__file__)),dtype='float32',attention='eager',seed=54,tasks=len(selected),batch_size=args.batch_size,
        operations=dict(collections.Counter(t['operation'] for t in selected)),gpu_index=args.gpu,
        interpretation='Clear source-support task, original text and gold unchanged; sentence-bounded visibility is diagnostic, not an ideal semantic oracle.')
    (args.out/'prequestion_oracle_map.py').write_bytes(Path(__file__).read_bytes())
    for name in ['revision_interventions.py','source_scope_map.py','reading_map.py']:
        (args.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    selected.sort(key=lambda t:len(t['prompt']))
    with (args.out/'predictions.jsonl').open('w') as stream:
        for begin in range(0,len(selected),args.batch_size):
            batch=selected[begin:begin+args.batch_size]
            scores=score(model,batch,tokenizer.pad_token_id)
            for task,values in zip(batch,scores):
                row=task['row']
                denominator=max(values)+math.log(sum(math.exp(v-max(values)) for v in values))
                n=task['encoded'][1]
                source=task['source_tokens']
                queries=task['query_tokens'] or []
                edges=sum(sum(k>q for k in source) for q in queries)
                record={k:row[k] for k in ['item_id','source','construction','sentence_sha256','question','literal_label','source_gold_matches_grounding']}
                record.update(pair_id=row.get('analysis_pair_id',row['pair_id']),cluster_id=row.get('analysis_cluster_id',row['cluster_id']),
                    condition=row['condition'],question_target=row['analysis_question_target'],operation=task['operation'],
                    readout=task['readout'],mapping=task['mapping'],candidate_gold=task['candidate_gold'],
                    displayed_options=task['displayed_options'],candidate_logprobs=values,
                    correct=max(range(len(values)),key=values.__getitem__)==task['candidate_gold'],
                    p_correct=math.exp(values[task['candidate_gold']]-denominator),prompt=task['prompt'],prompt_sha256=digest(task['prompt']),
                    prompt_tokens=n,source_tokens=source,query_tokens=queries,new_future_edges=edges,oracle_anchor=row['oracle_anchor'])
                stream.write(json.dumps(record)+'\n')
            stream.flush()
            if begin%(args.batch_size*100)==0:print(begin,'/',len(selected),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    print('Completed E54',args.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--build-out',type=Path)
    parser.add_argument('--model',type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--gpu',type=int)
    parser.add_argument('--batch-size',type=int,default=4)
    parser.add_argument('--instrument-only',action='store_true')
    args=parser.parse_args()
    if args.build_out:build(args.data,args.build_out)
    else:
        assert args.model and args.out and args.gpu is not None
        run(args)
