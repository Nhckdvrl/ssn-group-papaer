"""E52 secondary surprisal with Oh & Schuler (2024) trailing-boundary correction."""
import argparse
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import re
import time

import torch
import transformers
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, Gemma3ForConditionalGeneration
from data import sha


def boundary_ids(tokenizer):
    special = set(tokenizer.all_special_ids)
    result = []
    for token, index in tokenizer.get_vocab().items():
        if index in special: continue
        decoded = tokenizer.convert_tokens_to_string([token])
        if token.startswith(('Ġ', '▁')) or (decoded and decoded[0].isspace()): result.append(index)
    assert result
    return sorted(set(result))


def encode_word(row, tokenizer):
    index = row.get('disamb_word_index')
    if index is None: return None, 'No independently accepted landmark'
    spans = list(re.finditer(r'\S+', row['sentence']))
    span = spans[index]
    prefix = row['sentence'][:span.start()].rstrip()
    full = row['sentence'][:span.end()]
    before = tokenizer.encode(prefix, add_special_tokens=True)
    tokens = tokenizer.encode(full, add_special_tokens=True)
    if not prefix or not before: return None, 'No preceding context'
    if tokens[:len(before)] != before: return None, 'Tokenization crosses previous word boundary'
    assert len(tokens) > len(before)
    return dict(tokens=tokens, n=len(before), context=prefix,
                displayed_word=span.group(), full_prefix=full,
                sentence_final_word=index==len(spans)-1,
                contains_terminal_punctuation=bool(re.search(r'[.!?]$',span.group()))), None


def scores(model, batch, pad, boundaries):
    width = max(len(r['tokens']) for r in batch)
    keep = max(len(r['tokens'])-r['n']+1 for r in batch)
    ids = torch.full((len(batch), width), pad, device=model.device, dtype=torch.long)
    mask = torch.zeros_like(ids)
    for i,r in enumerate(batch):
        ids[i,-len(r['tokens']):] = torch.tensor(r['tokens'],device=model.device)
        mask[i,-len(r['tokens']):] = 1
    positions = mask.cumsum(-1)-1;positions.masked_fill_(mask==0,0)
    kwargs = dict(input_ids=ids,attention_mask=mask,position_ids=positions,use_cache=False)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters: kwargs['logits_to_keep']=keep
    with torch.inference_mode():
        logits=model(**kwargs).logits.float();logp=logits.log_softmax(-1)
        start=width-logits.shape[1];values=[]
        for i,r in enumerate(batch):
            offset=width-len(r['tokens']);previous=offset+r['n']-1-start
            raw=sum(logp[i,offset+j-1-start,r['tokens'][j]] for j in range(r['n'],len(r['tokens'])))
            before=torch.logsumexp(logp[i,previous,boundaries],0)
            after=torch.logsumexp(logp[i,-1,boundaries],0)
            wt=raw+after-before
            assert float(wt)<=1e-4, 'A corrected word probability cannot exceed one'
            values.append(dict(raw_bits=-float(raw)/math.log(2),wt_bits=-float(wt)/math.log(2),
                boundary_before_logprob=float(before),boundary_after_logprob=float(after)))
    return values


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--model',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--batch-size',type=int,default=16);args=parser.parse_args()
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(52);torch.set_num_threads(8)
    args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'surprisal.jsonl').exists()
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tokenizer.pad_token_id is None: tokenizer.pad_token=tokenizer.eos_token
    boundaries=boundary_ids(tokenizer);rows=[json.loads(x) for x in args.data.read_text().splitlines()]
    tasks=[];missing=[]
    for row in rows:
        encoded,error=encode_word(row,tokenizer)
        if error:missing.append(dict(item_id=row['item_id'],reason=error))
        else: tasks.append((row,encoded))
    config=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if config.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic()
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda').eval()
    with (args.out/'surprisal.jsonl').open('w') as stream:
        for begin in range(0,len(tasks),args.batch_size):
            batch=tasks[begin:begin+args.batch_size]
            for (row,encoded),value in zip(batch,scores(model,[e for r,e in batch],tokenizer.pad_token_id,boundaries)):
                record={k:row[k] for k in ('item_id','pair_id','cluster_id','construction','condition','sentence_sha256')}
                stream.write(json.dumps(record|{k:v for k,v in encoded.items() if k!='tokens'}|value)+'\n')
            stream.flush()
    (args.out/'missing.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in missing))
    (args.out/'disambiguator_surprisal.py').write_bytes(Path(__file__).read_bytes())
    report=dict(data_sha256=sha(args.data),model_manifest_sha256=sha(args.model/'manifest.json'),
        model_path=str(args.model),torch=torch.__version__,transformers=transformers.__version__,
        source='https://arxiv.org/html/2406.10851v1',formula='log P_WT(word)=log P_raw(word)+log P(boundary|after)-log P(boundary|before)',
        boundary_convention='Whitespace-starting tokens only, excluding specials; WT conditional on trailing whitespace, not document-EOS probability.',
        boundary_ids=boundaries,tasks=len(tasks),missing=len(missing),seed=52,
        surprisal_sha256=sha(args.out/'surprisal.jsonl'),missing_sha256=sha(args.out/'missing.jsonl'),
        code_sha256=sha(Path(__file__)),gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
