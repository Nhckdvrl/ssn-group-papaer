"""E69: published 2x2 plausibility/structure panel under original/source scope."""
import argparse
import collections
import fcntl
import itertools
import json
import math
import os
from pathlib import Path
import time
from data import CACHE, read_table, sha, write_jsonl
from data_v2 import digest


def build(a):
    raw=read_table(a.source);groups=collections.defaultdict(list)
    for r in raw:groups[r['set_id']].append(r)
    assert len(raw)==456 and len(groups)==69
    assert collections.Counter(map(len,groups.values()))=={8:45,4:24}
    rows=[]
    for i,r in enumerate(raw):
        condition='control' if r['sent_type'].startswith('nonGP') else 'gp'
        target={'GP_question':'initial','simple_question':'final'}[r['quest_type']]
        rows.append(dict(item_id=f'amouyal2025:{i}',source_set_id=r['set_id'],cluster_id=r['set_id'],
            source_row=i,source_sent_type=r['sent_type'],source='Amouyal2025',construction='NPZ',
            condition=condition,subtype=r['sent_type'].split('_',1)[1],question_target=target,
            sentence=r['sentence'],question=r['question'],gold=r['correct_answer'],
            sentence_sha256=digest(r['sentence']),source_unit='E69-source:'+digest(r['sentence'])))
    for sid,g in groups.items():
        expected={(c,p,t) for c in ('GP','nonGP') for p in (('prob','improb') if len(g)==8 else ('reflexive',)) for t in ('GP_question','simple_question')}
        assert {(r['sent_type'].split('_')[0],r['sent_type'].split('_')[1],r['quest_type']) for r in g}==expected
    assert not a.data.exists();write_jsonl(a.data,rows)
    m=dict(source_path=str(a.source),source_sha256=sha(a.source),revision='ca1d7f1ff5fe2a177505f55d4ca2dbc9dda88c3b',
        data_sha256=sha(a.data),QA=len(rows),sources=len({r['source_unit'] for r in rows}),clusters=len(groups),
        source_policy='Published stimuli unchanged. Original No means not necessarily; G2 source-support gold retained. No new item audit.',
        counts={str(k):v for k,v in collections.Counter((r['subtype'],r['condition'],r['question_target'],r['gold']) for r in rows).items()})
    a.data.with_suffix('.manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m),flush=True)


def prepare(rows,tok):
    from source_scope_map import RULES,render
    from reading_map import encode_choices
    tasks=[]
    for r in rows:
        for scope in ('O2','G2'):
            for mapping,shown in enumerate((['Yes','No'],['No','Yes'])):
                for readout in ('words','letters'):
                    content=f'Sentence:\n{r["sentence"]}\n\nQuestion:\n{r["question"]}\n'
                    content+='\n'.join(f'{l}. {s}' for l,s in zip('AB',shown))
                    content+='\nAnswer only '+('Yes or No.' if readout=='words' else 'A or B.')
                    t=dict(row=r,scope=scope,mapping=mapping,readout=readout,format='B',prompt=render(tok,RULES[scope],content),
                        candidates=shown if readout=='words' else ['A','B'],candidate_gold=shown.index(r['gold']))
                    t['encoded']=encode_choices(tok,t);assert all(len(s)==t['encoded'][1]+1 for s in t['encoded'][0]);tasks.append(t)
    return tasks


def run(a):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    from source_scope_map import single_token_scores,sequence_scores
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(69);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    rows=[json.loads(l) for l in a.data.read_text().splitlines()];manifest=json.loads(a.data.with_suffix('.manifest.json').read_text());assert manifest['data_sha256']==sha(a.data)
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    tasks=prepare(rows,tok);a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    fixed={r['source_unit'] for r in rows[:8]};assert len(fixed)==4;maximum=0
    for t in tasks:
        if t['row']['source_unit'] not in fixed:continue
        x=single_token_scores(model,[t['encoded']],tok.pad_token_id)[0]
        y=sequence_scores(model,t['encoded'][0],[t['encoded'][1]]*len(t['encoded'][0]),tok.pad_token_id)
        maximum=max(maximum,*[abs(u-v) for u,v in zip(x,y)])
    assert maximum<.001
    (a.out/'instrument.json').write_text(json.dumps(dict(fixed_sources=sorted(fixed),independent_LP_max_delta=maximum),indent=2)+'\n')
    config=dict(model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),data_sha256=sha(a.data),code_sha256=sha(Path(__file__)),
        dtype='float32',attention='eager',seed=69,gpu_index=a.gpu,tasks=len(tasks),phase='science')
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    tasks.sort(key=lambda t:len(t['prompt']))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),a.batch_size):
            batch=tasks[begin:begin+a.batch_size];values=single_token_scores(model,[t['encoded'] for t in batch],tok.pad_token_id)
            for t,lp in zip(batch,values):
                den=max(lp)+math.log(sum(math.exp(x-max(lp)) for x in lp));r=t['row']
                out=dict(r,scope=t['scope'],readout=t['readout'],mapping=t['mapping'],candidate_logprobs=lp,
                    candidate_gold=t['candidate_gold'],correct=max(range(2),key=lp.__getitem__)==t['candidate_gold'],
                    p_correct=math.exp(lp[t['candidate_gold']]-den),prompt_sha256=digest(t['prompt']))
                f.write(json.dumps(out)+'\n')
            f.flush()
            if begin%512==0:print('E69 scores',begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/'plausibility_revision.py').write_bytes(Path(__file__).read_bytes());print('E69 complete',a.model.name,config['gpu_hours'],flush=True)


def analyze(a):
    import numpy as np
    from analyze_reading_map import estimate
    data=[json.loads(l) for l in a.data.read_text().splitlines()];reports={};effects=[];provenance=[]
    def report(key,vs):
        reports[key]=estimate(vs,seed=69)
        effects.extend(dict(report=key,cluster_id=c,value=v) for c,v in vs.items())
    for p in a.runs:
        config=json.loads((p/'config.json').read_text());assert config['predictions_sha256']==sha(p/'predictions.jsonl') and config['data_sha256']==sha(a.data)
        rows=[json.loads(l) for l in (p/'predictions.jsonl').read_text().splitlines()];idx={(r['item_id'],r['scope'],r['readout'],r['mapping']):r for r in rows}
        expected={(r['item_id'],s,d,m) for r in data for s in ('O2','G2') for d in ('words','letters') for m in (0,1)}
        assert len(idx)==len(rows)==len(expected) and set(idx)==expected
        model=Path(config['model_path']).name;provenance.append(dict(path=str(p),config_sha256=sha(p/'config.json')))
        for target,read,metric in itertools.product(('initial','final','joint'),('words','letters'),('correct','p_correct')):
            if target=='joint' and metric!='correct':continue
            cell={}
            for scope,subtype,cond in itertools.product(('O2','G2'),('prob','improb','reflexive'),('gp','control')):
                subset=[r for r in rows if r['scope']==scope and r['readout']==read and r['subtype']==subtype and r['condition']==cond and (target=='joint' or r['question_target']==target)]
                groups=collections.defaultdict(list)
                if target=='joint':
                    qgroups=collections.defaultdict(list)
                    for r in subset:qgroups[(r['cluster_id'],r['mapping'])].append(r)
                    for (c,m),g in qgroups.items():assert len(g)==2;groups[c].append(float(all(r['correct'] for r in g)))
                else:
                    for r in subset:groups[r['cluster_id']].append(float(r[metric]))
                vs={c:float(np.mean(v)) for c,v in groups.items()};cell[scope,subtype,cond]=vs
                report(f'{model}/{scope}/{subtype}/{cond}/{target}/{read}/{metric}',vs)
            def contrast(key,terms):
                keys=set.intersection(*(set(cell[t]) for w,t in terms));vs={c:sum(w*cell[t][c] for w,t in terms) for c in sorted(keys)};report(f'{model}/{key}/{target}/{read}/{metric}',vs)
            for scope in ('O2','G2'):
                for subtype in ('prob','improb','reflexive'):contrast(f'{scope}/{subtype}/cue-minus-gp',[(1,(scope,subtype,'control')),(-1,(scope,subtype,'gp'))])
                for cond in ('gp','control'):contrast(f'{scope}/improb-minus-prob/{cond}',[(1,(scope,'improb',cond)),(-1,(scope,'prob',cond))])
                contrast(f'{scope}/structure-plausibility-interaction',[(1,(scope,'improb','gp')),(-1,(scope,'prob','gp')),(-1,(scope,'improb','control')),(1,(scope,'prob','control'))])
            for subtype,cond in itertools.product(('prob','improb','reflexive'),('gp','control')):contrast(f'G2-minus-O2/{subtype}/{cond}',[(1,('G2',subtype,cond)),(-1,('O2',subtype,cond))])
            for cond in ('gp','control'):
                contrast(f'G2-minus-O2/improb-minus-prob/{cond}',[(1,('G2','improb',cond)),(-1,('G2','prob',cond)),(-1,('O2','improb',cond)),(1,('O2','prob',cond))])
            contrast('G2-minus-O2/structure-plausibility-interaction',[(w*sw,(s,p,c)) for s,sw in [('G2',1),('O2',-1)] for w,p,c in [(1,'improb','gp'),(-1,'prob','gp'),(-1,'improb','control'),(1,'prob','control')]])
    e=a.out.with_suffix('.cluster-effects.jsonl');write_jsonl(e,effects)
    a.out.write_text(json.dumps(dict(data_sha256=sha(a.data),runs=provenance,reports=reports,cluster_effects_sha256=sha(e),
        interpretation='45 original matched plausibility sets; 24 reflexive reference sets separate. Published source-support gold, not world negation. O2/G2 changes task regime, not isolated hidden semantic factor.'),indent=2)+'\n');print('E69 all panels',len(reports),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['build','run','analyze']);p.add_argument('--source',type=Path);p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path);p.add_argument('--out',type=Path);p.add_argument('--gpu',type=int);p.add_argument('--runs',type=Path,nargs='+');p.add_argument('--batch-size',type=int,default=16);a=p.parse_args();globals()[a.mode](a)
