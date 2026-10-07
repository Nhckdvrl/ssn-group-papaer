"""E81 scores unchanged Source tokens under each proposed answer, never the label."""
import argparse
import fcntl
import inspect
import json
import math
import os
from pathlib import Path
import time
from data import CACHE, sha
from data_v2 import digest
from source_scope_map import RULES, single_token_scores
from goal_conditioned_reading import prepare as native_prepare


def render(tok, content):
    system = 'Write a single grammatical sentence satisfying the provided source-support judgement.'
    messages = [dict(role='system', content=system), dict(role='user', content=content)]
    try:
        return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except Exception:
        return tok.apply_chat_template([dict(role='user', content=system+'\n\n'+content)], tokenize=False,
                                      add_generation_prompt=True, enable_thinking=False)


def prepare(rows, tok, base):
    native = [t for t in native_prepare(rows, tok) if t['operation'] == 'NONE']
    for t in native:
        old = base[t['row']['item_id'], 'NONE', t['readout'], t['mapping']]
        assert old['prompt_sha256'] == digest(t['prompt']) and old['candidate_gold'] == t['candidate_gold']
    tasks = []
    for r in rows:
        assert r['sentence_sha256'] == digest(r['sentence'])
        for ro in ['words', 'letters']:
            for mp, shown in enumerate([['Yes', 'No'], ['No', 'Yes']]):
                choices = shown if ro == 'words' else ['A', 'B']
                prompts, sequences, starts, targets = [], [], [], []
                for choice in choices:
                    content = ('A question and a proposed source-support answer are given. Write one grammatical '
                               'sentence for which that proposed answer is correct. Return only the sentence.\n\n'
                               'Source-support rule:\n'+RULES['G2']+'\nQuestion:\n'+r['question']+'\n'+
                               '\n'.join(f'{a}. {b}' for a,b in zip(['A','B'],shown))+
                               '\nProposed answer: '+choice)
                    prompt = render(tok, content)
                    assert r['sentence'] not in prompt
                    prefix = tok.encode(prompt, add_special_tokens=False)
                    seq = tok.encode(prompt+r['sentence'], add_special_tokens=False)
                    assert seq[:len(prefix)] == prefix and len(seq) > len(prefix)
                    prompts.append(prompt); sequences.append(seq); starts.append(len(prefix)); targets.append(seq[len(prefix):])
                assert targets[0] == targets[1]
                tasks.append(dict(row=r, readout=ro, mapping=mp, operation='INVERSE',
                    candidate_gold=shown.index(r['grounded_gold']), prompts=prompts,
                    sequences=sequences, starts=starts, target_token_ids=targets[0]))
    return tasks, native


def scores(model, tasks, pad_id):
    import torch
    sequences = [s for t in tasks for s in t['sequences']]
    starts = [s for t in tasks for s in t['starts']]
    width = max(map(len, sequences))
    keep = max(len(s)-n+1 for s,n in zip(sequences, starts))
    ids = torch.full((len(sequences), width), pad_id, device=model.device, dtype=torch.long)
    mask = torch.zeros_like(ids)
    for i, seq in enumerate(sequences):
        ids[i,-len(seq):] = torch.tensor(seq, device=model.device)
        mask[i,-len(seq):] = 1
    pos = mask.cumsum(-1)-1; pos.masked_fill_(mask == 0, 0)
    kwargs = dict(input_ids=ids, attention_mask=mask, position_ids=pos, use_cache=False)
    if 'logits_to_keep' in inspect.signature(model.forward).parameters:
        kwargs['logits_to_keep'] = keep
    with torch.inference_mode():
        logits = model(**kwargs).logits.float()
        logprobs = logits.log_softmax(-1)
        start_logit = width-logits.shape[1]
        token_lps = []
        for i,(seq,start) in enumerate(zip(sequences,starts)):
            offset = width-len(seq)
            values = [float(logprobs[i, offset+j-1-start_logit, seq[j]]) for j in range(start,len(seq))]
            assert len(values) == len(seq)-start
            token_lps.append(values)
    return [[token_lps[i],token_lps[i+1]] for i in range(0,len(token_lps),2)]


def run(a):
    import torch
    from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM, Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    lock = (CACHE/'E52/gpu-slots'/str(a.gpu)).open('a'); fcntl.flock(lock, fcntl.LOCK_EX)
    torch.manual_seed(81); torch.set_num_threads(4); torch.backends.cuda.matmul.allow_tf32=False
    allrows = list(map(json.loads,a.data.read_text().splitlines()))
    assert sha(a.data) == json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows = [r for r in allrows if int(r['sentence_sha256'][:16],16)%a.shards == a.shard]
    parent = a.parent/'runs-v1'/a.model.name; bcfg=json.loads((parent/'config.json').read_text())
    assert bcfg['data_sha256']==sha(a.data) and bcfg['predictions_sha256']==sha(parent/'predictions.jsonl')
    assert bcfg['model_manifest_sha256']==sha(a.model/'manifest.json')
    base={(p['item_id'],p['operation'],p['readout'],p['mapping']):p for p in map(json.loads,(parent/'predictions.jsonl').read_text().splitlines()) if p['operation']=='NONE'}
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks,native=prepare(rows,tok,base); cfg=AutoConfig.from_pretrained(a.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic(); model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    fixed=min(r['source_unit'] for r in rows); checks=[]
    for t in [t for t in native if t['row']['source_unit']==fixed]:
        lp=single_token_scores(model,[t['encoded']],tok.pad_token_id)[0]
        old=base[t['row']['item_id'],'NONE',t['readout'],t['mapping']]
        delta=max(abs(x-y) for x,y in zip(lp,old['candidate_logprobs'])); assert delta<.001
        checks.append(dict(item_id=t['row']['item_id'],parent_LP_max_delta=delta))
    tasks.sort(key=lambda t:max(map(len,t['sequences'])))
    solo=scores(model,tasks[:1],tok.pad_token_id)[0]
    batched=scores(model,tasks[:a.batch_size],tok.pad_token_id)[0]
    numerical=max(abs(sum(x)-sum(y)) for x,y in zip(solo,batched)); assert numerical<.005
    a.out.mkdir(parents=True,exist_ok=True); assert not (a.out/'predictions.jsonl').exists()
    config=dict(data_sha256=sha(a.data),model_manifest_sha256=sha(a.model/'manifest.json'),
        parent_predictions_sha256=bcfg['predictions_sha256'],code_sha256=sha(Path(__file__)),
        dtype='float32',attention='eager',seed=81,gpu=a.gpu,shard=a.shard,shards=a.shards,
        QA=len(rows),tasks=len(tasks),instrument=checks,inverse_batch_LP_max_delta=numerical,
        score_scope='Only original Source tokens; proposed label and template excluded',
        dependencies={n:sha(Path(__file__).with_name(n)) for n in ['goal_conditioned_reading.py','source_scope_map.py','reading_map.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),a.batch_size):
            batch=tasks[begin:begin+a.batch_size]; vals=scores(model,batch,tok.pad_token_id)
            for t,token_lps in zip(batch,vals):
                lp=[sum(x) for x in token_lps]; maximum=max(lp); den=maximum+math.log(sum(math.exp(x-maximum) for x in lp)); r=t['row']; g=t['candidate_gold']
                f.write(json.dumps(dict(item_id=r['item_id'],source_unit=r['source_unit'],operation='INVERSE',
                    readout=t['readout'],mapping=t['mapping'],candidate_gold=g,candidate_logprobs=lp,
                    correct=max(range(2),key=lp.__getitem__)==g,p_correct=math.exp(lp[g]-den),
                    prompt_sha256=[digest(p) for p in t['prompts']],prompt_tokens=max(t['starts']),
                    source_token_ids=t['target_token_ids'],source_token_logprobs=token_lps))+'\n')
            f.flush()
            if begin%256==0:print('E81',a.model.name,a.shard,begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print('E81 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['data','parent','model','out']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0)
    p.add_argument('--shards',type=int,default=1);p.add_argument('--batch-size',type=int,default=8)
    run(p.parse_args())
