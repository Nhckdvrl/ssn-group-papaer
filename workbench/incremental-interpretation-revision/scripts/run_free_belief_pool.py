"""E108 free belief proposals, frozen credit and actual use. Human deadline guarded."""
import argparse
import collections
import fcntl
import json
import os
from pathlib import Path
import re
import time
from data import CACHE,sha
from data_v2 import digest
from gpu_deadline import ensure_gpu_allowed
from current_open_baseline import tokenizer
from free_belief_contract import prompt,reader_prompt
from reconstruction_reward import prepare
from run_reconstruction_reward import score
from run_native_revision_pool import region_scores,generate as sample

def load(path):return [json.loads(line) for line in path.read_text().splitlines()]

def greedy(model,tok,text,cap):
    import torch
    ids=tok.encode(text,add_special_tokens=False);x=torch.tensor([ids],device=model.device)
    with torch.inference_mode():
        y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,max_new_tokens=cap,
                         use_cache=True,pad_token_id=tok.pad_token_id)
    new=y[0,len(ids):].tolist();eos=model.generation_config.eos_token_id
    eos=[eos] if isinstance(eos,int) else eos or [];stopped=bool(new and new[-1] in eos)
    return dict(text=tok.decode(new,skip_special_tokens=True),output_tokens=new,stopped=stopped,
                capped=len(new)>=cap and not stopped,prompt_sha256=digest(text),cap=cap,seed=None)

def answer(model,tok,text,question):
    z=greedy(model,tok,reader_prompt(text,question,tok),64);final=z['text'].rsplit('</think>',1)[-1].strip()
    m=re.fullmatch(r'(Yes|No)[.!]?\s*',final,re.IGNORECASE)
    z['answer']=m.group(1).capitalize() if m and z['stopped'] else None
    z['unknown']=z['answer'] is None;return z

def run(a):
    ensure_gpu_allowed()
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX);ensure_gpu_allowed()
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    import torch,transformers
    from transformers import AutoConfig,AutoModelForImageTextToText,FineGrainedFP8Config
    torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    data=a.root/'data-v1.jsonl';assert sha(data)==json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    rows=[r for r in load(data) if int(digest(r['cluster_id'])[:16],16)%a.shards==a.shard];assert rows
    positions=collections.defaultdict(set)
    for r in load(a.root.parent/'E52/qualified-v3.jsonl'):
        if r.get('step5_position_agreed'):positions[r['sentence_sha256']].add(r['step5_annotation']['disamb_word_index'])
    tok=tokenizer(a.model);cfg=AutoConfig.from_pretrained(a.model,local_files_only=True)
    kwargs=dict(local_files_only=True,dtype=torch.bfloat16,attn_implementation='eager')
    if getattr(cfg,'quantization_config',None):
        q=dict(cfg.quantization_config);q['dequantize']=True;kwargs['quantization_config']=FineGrainedFP8Config(**q)
    start=time.monotonic();model=AutoModelForImageTextToText.from_pretrained(a.model,**kwargs).to('cuda').eval()
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    seed_for=lambda uid,j:int(digest(json.dumps([108,a.model.name,uid,j]))[:16],16)%(2**31)
    fixed=min(rows,key=lambda r:r['item_id']);seed=seed_for(fixed['item_id'],1)
    test=sample(model,tok,prompt(fixed,'gp',tok),seed)
    assert sample(model,tok,prompt(fixed,'gp',tok),seed)['output_tokens']==test['output_tokens']
    task=prepare(dict(fixed['sources']['gp'],interpretation=test['text'].rsplit('</think>',1)[-1]),tok)
    assert score(model,task)==score(model,task)
    question=min(fixed['questions'],key=lambda q:q['question_id'])['question']
    testq=answer(model,tok,fixed['sources']['control']['sentence'],question)
    assert answer(model,tok,fixed['sources']['control']['sentence'],question)['output_tokens']==testq['output_tokens']
    unfinished='<think>' in test['text'] and '</think>' not in test['text']
    preflight=dict(item_id=fixed['item_id'],sample_repeat_exact=True,LP_repeat_exact=True,reader_repeat_exact=True,
                   sample=test,reader=testq,writer_valid=bool(test['stopped'] and test['text'].strip() and not unfinished),
                   reader_valid=not testq['unknown'])
    (a.out/'instrument-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    if not preflight['writer_valid'] or not preflight['reader_valid']:
        raise RuntimeError('Writer/reader instrument unavailable; no zero-ability inference or cap adjustment')
    config=dict(model=a.model.name,model_manifest_sha256=sha(a.model/'manifest.json'),data_sha256=sha(data),
        writer_code_sha256=sha(Path(__file__).with_name('free_belief_contract.py')),runner_code_sha256=sha(Path(__file__)),
        torch=torch.__version__,transformers=transformers.__version__,gpu=a.gpu,shard=a.shard,shards=a.shards,pairs=len(rows),
        writer_cap=96,reader_cap=64,temperature=.8,top_p=.95,effective_generation_config=model.generation_config.to_dict(),
        instrument=dict(sample_repeat_exact=True,LP_repeat_exact=True,reader_repeat_exact=True),
        T2_sha256=sha(a.root.parent/'E52/qualified-v3.jsonl'),
        helper_sha256={name:sha(Path(__file__).with_name(name)) for name in
                       ['free_belief_contract.py','reconstruction_reward.py','run_reconstruction_reward.py','run_native_revision_pool.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as out:
        for i,r in enumerate(sorted(rows,key=lambda r:r['item_id'])):
            source=r['sources']['gp'];ps=positions[source['sentence_sha256']];assert len(ps)==1 and None not in ps
            targets=[]
            for j in range(10):
                ensure_gpu_allowed();side='control' if j==9 else 'gp';text=prompt(r,side,tok,recovery=j==8)
                z=sample(model,tok,text,seed_for(r['item_id'],j)) if 1<=j<=7 else greedy(model,tok,text,96)
                final=z['text'].rsplit('</think>',1)[-1];task=prepare(dict(source,interpretation=final),tok)
                lp=score(model,task);regions=region_scores(source,z['text'],lp,tok,next(iter(ps)))
                targets.append((regions['target_ids'],regions['target_offsets']));qs=[]
                for q in r['questions']:
                    ensure_gpu_allowed();v=answer(model,tok,final,q['question'])
                    qs.append(dict(v,question_id=q['question_id'],source_gold=q['source_gold']))
                out.write(json.dumps(dict(z,item_id=r['item_id'],operation='BELIEF',candidate=j,primary_pool=j<8,
                    source_condition=side,recovery=j==8,cluster_id=r['cluster_id'],construction=r['construction'],
                    sentence_sha256=source['sentence_sha256'],text_sha256=digest(z['text']),
                    exact_source_copy=final.strip()==r['sources'][side]['sentence'].strip(),
                    token_logprobs=lp,scores=regions,reader_answers=qs))+'\n');out.flush()
            assert all(t==targets[0] for t in targets)
            for side in ['gp','control']:
                for q in r['questions']:
                    ensure_gpu_allowed();v=answer(model,tok,r['sources'][side]['sentence'],q['question'])
                    out.write(json.dumps(dict(v,operation='SOURCE_READ',item_id=r['item_id'],source_condition=side,
                        question_id=q['question_id'],source_gold=q['source_gold']))+'\n');out.flush()
            print('E108',a.model.name,a.shard,i+1,'/',len(rows),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    for name in ['run_free_belief_pool.py',*config['helper_sha256']]:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E108 DONE',config['gpu_hours'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['root','model','out']:p.add_argument('--'+name,type=Path,required=True)
    for name in ['gpu','shard','shards']:p.add_argument('--'+name,type=int,required=True)
    run(p.parse_args())
