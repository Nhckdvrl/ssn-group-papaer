"""E65 original multi-question sources: reading goals versus later, unprimed uses."""
import argparse
import collections
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE, sha, write_jsonl
from data_v2 import digest
from shared_source_cross_use import render, source_info
from source_scope_map import RULES, single_token_scores
from reading_map import encode_choices


def build(source, out):
    rows=[json.loads(l) for l in source.read_text().splitlines()]
    grouped=collections.defaultdict(list)
    for r in rows:grouped[r['sentence_sha256']].append(r)
    eligible={s for s,g in grouped.items() if {'initial','final'}<={r['analysis_question_target'] for r in g}}
    pairs=collections.defaultdict(list)
    for r in rows:pairs[(r['analysis_pair_id'],r['question'])].append(r)
    paired={r['item_id'] for g in pairs.values() if len(g)==2 and {r['condition'] for r in g}=={'gp','control'} and all(r['sentence_sha256'] in eligible for r in g) for r in g}
    result=[]
    for sentence,g in grouped.items():
        if sentence not in eligible:continue
        assert len({r['analysis_cluster_id'] for r in g})==1
        goals={target:sorted((r for r in g if r['analysis_question_target']==target),key=lambda r:(r['item_id'],r['question']))[0]['question'] for target in ('initial','final')}
        for r in g:
            if r['item_id'] in paired:result.append(dict(r,source_unit='E65-source:'+sentence,reading_goals=goals))
    assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);write_jsonl(out,result)
    by_source={r['source_unit']:r for r in result}
    report=dict(source_path=str(source),source_sha256=sha(source),data_sha256=sha(out),QA=len(result),sources=len(by_source),
        clusters=len({r['analysis_cluster_id'] for r in result}),gp_sources_by_construction=dict(collections.Counter(r['construction'] for r in by_source.values() if r['condition']=='gp')),
        policy='Existing published source and questions, final E59 G2 gold, exact paired input eligibility. Goals selected by input-only ordering; no outcome or model filtering.')
    out.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


def prepare(rows,tokenizer):
    tasks=[];prefixes={}
    for r in rows:
        for operation,target in [('NONE',None),('INITIAL','initial'),('FINAL','final')]:
            goal=None if target is None else r['reading_goals'][target]
            for readout in ('words','letters'):
                for mapping,shown in enumerate((['Yes','No'],['No','Yes'])):
                    task=RULES['G2']+'\nQuestion:\n'+r['question']+'\n'+'\n'.join(f'{a}. {b}' for a,b in zip(['A','B'],shown))
                    task+='\nAnswer only '+('Yes or No.' if readout=='words' else 'A or B.')
                    prompt=render(tokenizer,r['sentence'],task)
                    if goal is not None:
                        marker='Read this sentence carefully.\nSentence:\n'
                        assert prompt.count(marker)==1
                        prompt=prompt.replace(marker,'Read this sentence carefully.\nReading goal:\n'+goal+'\nSentence:\n')
                    t=dict(row=r,prompt=prompt,candidates=shown if readout=='words' else ['A','B'],candidate_gold=shown.index(r['grounded_gold']),format='B',
                        operation=operation,readout=readout,mapping=mapping,primed_question=goal,exact_primed_question=goal==r['question'])
                    t['encoded']=encode_choices(tokenizer,t)
                    assert all(len(s)==t['encoded'][1]+1 for s in t['encoded'][0])
                    prefix,_=source_info(tokenizer,t);key=(r['source_unit'],operation)
                    if key in prefixes:assert prefixes[key]==prefix
                    prefixes[key]=prefix;tasks.append(t)
    return tasks


def run(args):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(args.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(65);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    rows=[json.loads(l) for l in args.data.read_text().splitlines()];manifest=json.loads(args.data.with_suffix('.manifest.json').read_text());assert manifest['data_sha256']==sha(args.data)
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(args.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    tasks=prepare(rows,tok);args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'predictions.jsonl').exists()
    fixed=set(sorted({r['source_unit'] for r in rows})[:4]);local=[t for t in tasks if t['row']['source_unit'] in fixed]
    # Single-token scoring agrees with an independent full causal-sequence forward.
    from source_scope_map import sequence_scores
    maximum=0
    for t in local:
        a=single_token_scores(model,[t['encoded']],tok.pad_token_id)[0];b=sequence_scores(model,[t['encoded']],tok.pad_token_id)[0]
        maximum=max(maximum,*[abs(x-y) for x,y in zip(a,b)])
    assert maximum<.001
    (args.out/'instrument.json').write_text(json.dumps(dict(fixed_sources=sorted(fixed),independent_LP_max_delta=maximum,source_prefix_identical_within_goal=True),indent=2)+'\n')
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),code_sha256=sha(Path(__file__)),
        dtype='float32',attention='eager',seed=65,gpu_index=args.gpu,tasks=len(tasks),source_units=len({r['source_unit'] for r in rows}),phase='instrument_only' if args.instrument_only else 'science')
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    if args.instrument_only:print('E65 instrument passed',args.model.name,flush=True);return
    tasks.sort(key=lambda t:len(t['prompt']))
    with (args.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),args.batch_size):
            batch=tasks[begin:begin+args.batch_size];values=single_token_scores(model,[t['encoded'] for t in batch],tok.pad_token_id)
            for t,lp in zip(batch,values):
                r=t['row'];den=max(lp)+math.log(sum(math.exp(x-max(lp)) for x in lp))
                record={k:r[k] for k in ('item_id','sentence_sha256','question','construction','condition','source_unit','source_gold_matches_grounding','literal_label')}
                record.update(operation=t['operation'],readout=t['readout'],mapping=t['mapping'],primed_question=t['primed_question'],exact_primed_question=t['exact_primed_question'],
                    question_target=r['analysis_question_target'],cluster_id=r['analysis_cluster_id'],pair_id=r['analysis_pair_id'],candidate_logprobs=lp,
                    candidate_gold=t['candidate_gold'],correct=max(range(len(lp)),key=lp.__getitem__)==t['candidate_gold'],p_correct=math.exp(lp[t['candidate_gold']]-den),prompt_sha256=digest(t['prompt']))
                f.write(json.dumps(record)+'\n')
            f.flush()
            if begin%512==0:print('E65 scores',begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(args.out/'goal_conditioned_reading.py').write_bytes(Path(__file__).read_bytes());print('E65 complete',args.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--build-out',type=Path);p.add_argument('--model',type=Path)
    p.add_argument('--out',type=Path);p.add_argument('--gpu',type=int);p.add_argument('--instrument-only',action='store_true');p.add_argument('--batch-size',type=int,default=16);a=p.parse_args()
    if a.build_out:build(a.data,a.build_out)
    else:assert a.model and a.out and a.gpu is not None;run(a)
