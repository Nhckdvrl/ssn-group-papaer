"""E12: sentence likelihood inside the exact prior E08/E10 prompts.

Score only the causal prefix ending at the last source-sentence character.
Identical token prefixes are evaluated once; future-text nulls are implied by
prefix identity, not presented as independent empirical discoveries.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from data import CACHE, sha
from analyze import estimate


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def prepare(cache, tokenizer, protocol):
    parent=cache/'runs'/protocol
    cfg=json.loads((parent/'config.json').read_text())
    assert cfg['predictions_sha256']==sha(parent/'predictions.jsonl')
    parents={(r['item_id'],r['prompt_id']):r for r in map(json.loads,(parent/'predictions.jsonl').read_text().splitlines())}
    assert len(parents)==cfg['task_count']
    if protocol=='E08':
        from focus_audit import tasks_focus
        tasks=tasks_focus(cache,tokenizer)
    else:
        from option_access import tasks_access
        tasks=tasks_access(cache,tokenizer,mixed_only=False)
    assert len(tasks)==len(parents)
    groups={}; records=[]
    for r,pid,prompt in tasks:
        old=parents[(r['item_id'],pid)]
        assert digest(prompt)==old['prompt_sha256'],'Parent prompt changed'
        marker='Here is the sentence:\n'
        assert prompt.count(marker)==1
        start=prompt.index(marker)+len(marker); end=start+len(r['sentence'])
        assert prompt[start:end]==r['sentence']
        prefix=prompt[:end]
        encoded=tokenizer(prefix,add_special_tokens=False,return_offsets_mapping=True)
        ids=encoded['input_ids']; offsets=encoded['offset_mapping']
        key=digest(json.dumps(ids,separators=(',',':')))
        words=list(re.finditer(r'\S+',r['sentence']))
        wi=[[] for _ in words]
        for j,(a,b) in enumerate(offsets):
            content=prefix[max(a,start):min(b,end)] if b>start and a<end else ''
            if not content.strip():continue
            assert j>0
            assert a>=start or not prefix[a:start].strip(),'Token overlaps source header'
            touched=[i for i,w in enumerate(words) if a<start+w.end() and b>start+w.start()]
            assert len(touched)==1,'Cannot isolate a word from a multiword token; do not invent its surprisal'
            wi[touched[0]].append(j)
        assert all(wi),'A source word has no tokens'
        group=dict(ids=ids,word_token_indices=wi,prefix_sha256=digest(prefix),
                   source_sentence_sha256=digest(r['sentence']),words=[w.group() for w in words])
        if key in groups:
            assert groups[key]==group,'Identical token prefixes with different source alignment'
        else:groups[key]=group
        item={k:v for k,v in r.items() if k not in ('sentence','question','initial_parse_claim','final_parse_claim')}
        item.update(protocol=protocol,prompt_id=pid,parent_prompt_sha256=digest(prompt),
                    prefix_token_sha256=key,prefix_sha256=digest(prefix),
                    source_sentence_sha256=digest(r['sentence']),source_question_sha256=digest(r['question']),
                    answer_p_yes=old['p_yes'],answer_p_correct=old['p_correct'],answer_correct=old['correct'])
        records.append(item)
    return records,groups,cfg


def run(args):
    assert not args.out.exists(),'Immutable run: select a new output path'
    args.out.mkdir(parents=True)
    torch.manual_seed(0);torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32=False
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    tokenizer.pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id
    records,groups,parent=prepare(args.cache,tokenizer,args.protocol)
    manifest=json.loads((args.model/'manifest.json').read_text())
    for old in parent.get('inference_subruns',[parent]):
        assert old['model_manifest']==manifest and old['dtype']=='float32','Parent model or precision differs'
    cfg=dict(experiment='E12',protocol=args.protocol,task_count=len(records),unique_prefixes=len(groups),
             parent_predictions_sha256=parent['predictions_sha256'],parent_config_sha256=sha(args.cache/'runs'/args.protocol/'config.json'),
             git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             code_sha256={p.name:sha(p) for p in Path(__file__).parent.glob('*.py')},
             model_manifest=manifest,model=str(args.model),
             dtype='float32',frozen=True,thinking=False,attention='sdpa',tf32=False,
             torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(),
             batch_size=args.batch_size,seed=0,
             scoring='Teacher-forced token NLL in bits; aggregate original source words. Prefix truncated at last sentence character; parent full prompt hashes verified.',
             reuse='Identical causal token prefixes evaluated once; all parent analytical rows retained. No new questions, gold, or stimuli.')
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    start=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    for parameter in model.parameters():parameter.requires_grad_(False)
    keys=sorted(groups,key=lambda k:(len(groups[k]['ids']),k));scores={}
    with torch.inference_mode():
        for offset in range(0,len(keys),args.batch_size):
            batch=keys[offset:offset+args.batch_size]
            padded=tokenizer.pad([{'input_ids':groups[k]['ids'],'attention_mask':[1]*len(groups[k]['ids'])} for k in batch],return_tensors='pt').to('cuda')
            logits=model(**padded).logits[:,:-1,:].float()
            targets=padded['input_ids'][:,1:]
            # Avoid a second full-vocabulary probability tensor.
            nll=(logits.logsumexp(-1)-logits.gather(-1,targets.unsqueeze(-1)).squeeze(-1))/np.log(2)
            nll=nll.cpu().numpy()
            for j,k in enumerate(batch):
                g=groups[k]; pad=padded['input_ids'].shape[1]-len(g['ids'])
                bits=[float(sum(nll[j,t+pad-1] for t in indices)) for indices in g['word_token_indices']]
                scores[k]=bits
            if offset%(args.batch_size*20)==0:print(f'{offset+len(batch)}/{len(keys)} prefixes elapsed={time.time()-start:.1f}s',flush=True)
    with (args.out/'scores.jsonl').open('w') as f:
        for r in records:
            bits=scores[r['prefix_token_sha256']]
            out=dict(r,sentence_word_bits=bits,sentence_mean_bits=float(np.mean(bits)),sentence_total_bits=sum(bits),source_word_count=len(bits))
            if args.protocol=='E10':
                d=r['disambiguator_index'];assert 0<=d<len(bits)
                out.update(disambiguator_bits=bits[d],disambiguator_plus_two_mean_bits=float(np.mean(bits[d:d+3])),
                           post_disambiguator_mean_bits=float(np.mean(bits[d+1:])) if d+1<len(bits) else None)
            f.write(json.dumps(out)+'\n')
    cfg.update(scores_sha256=sha(args.out/'scores.jsonl'),wall_seconds=time.time()-start,
               gpu_hours=(time.time()-start)/3600,peak_gpu_bytes=torch.cuda.max_memory_allocated())
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    print('DONE',cfg['wall_seconds'],flush=True)


def analyze(path):
    cfg=json.loads((path/'config.json').read_text());assert cfg['scores_sha256']==sha(path/'scores.jsonl')
    rows=list(map(json.loads,(path/'scores.jsonl').read_text().splitlines()));assert len(rows)==cfg['task_count']
    result={'protocol':cfg['protocol'],'cells':{},'processing_effects':{},'gp_interactions':{},
            'units':'bits per source word, except disambiguator_bits (bits of the single original word)',
            'interpretation':'Conditional word prediction is not a direct parse measure or capability accuracy. No new semantic annotation.'}
    def stat(v):
        if len(v)<2:return dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v),pair_ids=sorted(v))
        return dict(estimate([v[s] for s in sorted(v)]),pair_ids=sorted(v))
    def diff(a,b):return {s:a[s]-b[s] for s in sorted(a.keys()&b.keys())}
    families=['pooled','NPZ','NPS','MVRR'] if cfg['protocol']=='E10' else ['pooled','prob','reflexive']
    for family in families:
        sub=rows if family=='pooled' else [r for r in rows if r.get('construction')==family or r.get('subtype')==family]
        strata=['all','target_xlsx','control_xlsx'] if cfg['protocol']=='E10' else ['all69','clean67']
        for stratum in strata:
            rr=[r for r in sub if stratum in ('all','all69') or stratum=='clean67' and r['pair_id'] not in ('set_hyp5_14','set_hyp5_18')
                or stratum=='target_xlsx' and r['source_target_xlsx'] or stratum=='control_xlsx' and not r['source_target_xlsx']]
            def vals(pid,c,m):
                groups=collections.defaultdict(list)
                for r in rr:
                    if r['prompt_id']==pid and r['condition']==c and r[m] is not None:groups[r['pair_id']].append(r[m])
                return {s:float(np.mean(v)) for s,v in groups.items()}
            other='explicit_cue' if cfg['protocol']=='E10' else 'non_gp'
            metrics=['sentence_mean_bits','disambiguator_bits','disambiguator_plus_two_mean_bits','post_disambiguator_mean_bits'] if cfg['protocol']=='E10' else ['sentence_mean_bits']
            for m in metrics:
                for pid in sorted({r['prompt_id'] for r in rows}):
                    prefix=f'{family}/{stratum}/{pid}/{m}'
                    for c in ('gp',other):result['cells'][prefix+'/'+c]=stat(vals(pid,c,m))
                    result['cells'][prefix+'/GP_minus_control']=stat(diff(vals(pid,'gp',m),vals(pid,other,m)))
                for repair in ('base','repair'):
                    contrasts={}
                    if cfg['protocol']=='E10':
                        for mapping in ('option1_A','option1_B'):
                            for o in ('pre','post'):
                                contrasts[f'{mapping}/question_pre_minus_post/options_{o}']=(f'q_pre_o_{o}_{repair}_{mapping}',f'q_post_o_{o}_{repair}_{mapping}')
                            for q in ('pre','post'):
                                contrasts[f'{mapping}/options_pre_minus_post/question_{q}']=(f'q_{q}_o_pre_{repair}_{mapping}',f'q_{q}_o_post_{repair}_{mapping}')
                    else:
                        for a,b in [('initial','final'),('initial','unrelated_initial'),('final','unrelated_final')]:
                            contrasts[f'before/{a}_minus_{b}']=(f'before_{a}_{repair}',f'before_{b}_{repair}')
                        for focus in ('initial','final','unrelated_initial','unrelated_final'):
                            contrasts[f'{focus}/before_minus_none']=(f'before_{focus}_{repair}',f'none_none_{repair}')
                            contrasts[f'{focus}/after_minus_none']=(f'after_{focus}_{repair}',f'none_none_{repair}')
                    for name,(a,b) in contrasts.items():
                        ds={c:diff(vals(a,c,m),vals(b,c,m)) for c in ('gp',other)}
                        prefix=f'{family}/{stratum}/{repair}/{name}/{m}'
                        for c in ds:result['processing_effects'][prefix+'/'+c]=stat(ds[c])
                        result['gp_interactions'][prefix]=stat(diff(ds['gp'],ds[other]))
    result.update(bootstrap_seed=20261005,bootstrap_draws=10000,rows=len(rows),scores_sha256=cfg['scores_sha256'],analysis_code_sha256=sha(Path(__file__)))
    return result


def joint_cue(path):
    """Explicit POST-HOC check of aggregated versus itemwise opposing effects."""
    cfg=json.loads((path/'config.json').read_text())
    assert cfg['scores_sha256']==sha(path/'scores.jsonl') and cfg['protocol']=='E10'
    rows=list(map(json.loads,(path/'scores.jsonl').read_text().splitlines()))
    assert len(rows)==cfg['task_count']
    groups=collections.defaultdict(dict)
    for r in rows:
        if not r['repair'] and r['option_position']=='post' and r['condition']=='explicit_cue':
            groups[(r['pair_id'],r['construction'],r['option_mapping'])][r['question_position']]=r
    effects=[]
    for k,d in sorted(groups.items()):
        assert set(d)=={'pre','post'}
        effects.append(dict(pair_id=k[0],construction=k[1],mapping=k[2],
                            word_change=d['pre']['disambiguator_bits']-d['post']['disambiguator_bits'],
                            answer_change=d['pre']['answer_correct']-d['post']['answer_correct'],
                            answer_probability_change=d['pre']['answer_p_correct']-d['post']['answer_p_correct']))
    byset=collections.defaultdict(list)
    for r in effects:byset[r['pair_id']].append(r)
    metrics=['word_change','answer_change','answer_probability_change']
    v={s:{m:float(np.mean([r[m] for r in rr])) for m in metrics} for s,rr in byset.items()}
    result={m:estimate([v[s][m] for s in sorted(v)]) for m in metrics}
    x=np.array([v[s]['word_change'] for s in sorted(v)]);y=np.array([v[s]['answer_change'] for s in sorted(v)])
    result.update(post_hoc=True,scope='Fixed options post/base; both mappings and three constructions averaged within each of 24 source lexical sets. Association is descriptive, not causal.',
                  pearson_r=float(np.corrcoef(x,y)[0,1]),source_lexical_sets_both_word_facilitated_and_answer_harmed=int(np.sum((x<0)&(y<0))),
                  source_lexical_sets=len(v),source_scores_sha256=cfg['scores_sha256'],rows=effects,
                  interpretation='Opposing aggregate means do not establish opposing effects on every item or a common mechanism.')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--model',type=Path,default=CACHE/'models/Qwen3-8B')
    p.add_argument('--protocol',choices=['E08','E10']);p.add_argument('--batch-size',type=int,default=8)
    p.add_argument('--out',type=Path);p.add_argument('--analyze',type=Path);p.add_argument('--joint-cue',type=Path);a=p.parse_args()
    if a.joint_cue:
        a.out.write_text(json.dumps(joint_cue(a.joint_cue),indent=2)+'\n')
        raise SystemExit(0)
    if a.analyze:
        a.out.write_text(json.dumps(analyze(a.analyze),indent=2)+'\n')
    else:
        assert a.protocol and a.out;run(a)
