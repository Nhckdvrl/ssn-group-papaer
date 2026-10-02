#!/usr/bin/env python3
"""Reproduce frozen ImplicatureX prompts with source and numerical gates."""
import argparse
import ast
import hashlib
import json
import re
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from run_native_readout import next_logits
from aggregate import estimate


def prepare(root):
    up = root/'upstream/ImplicatureX'
    source = up/'src/exps/generate_prompts.py'
    tree = ast.parse(source.read_text())
    # Only pure formatting functions and literal constants from the parent.
    # Avoid run.py, its provider dependencies and mutable shared caches.
    ns = {'pd':pd,'re':re,'SWB_SPEAKERS_CSV':up/'data/prompts/swb_speakers.csv'}
    for n in tree.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try:
                ns[n.targets[0].id] = ast.literal_eval(n.value)
            except (ValueError,TypeError):
                pass
    functions = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name != 'main']
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),ns)
    rows = {}; hashes = {}; counts = {}; ids_by_dataset = []
    states = {'implicatureX':'cancel','implicatureApprox':'irrelevant',
              'implicatureBot':'negation','implicaturePlus':'strengthen','implicatureX_prior':'prior'}
    for dataset, state in states.items():
        p = up/'data/prompts'/f'prompts_{dataset}.csv'
        frame = pd.read_csv(p).fillna('')
        hashes[str(p.relative_to(up))] = hashlib.sha256(p.read_bytes()).hexdigest()
        assert len(frame)==(542 if state=='prior' else 1084)
        assert frame.id.nunique()==271 and 'some_all_8' not in frame.id.tolist()
        ids_by_dataset.append(set(frame.id)); counts[dataset] = len(frame)
        for r in frame.to_dict('records'):
            row = pd.Series(r)
            contains = bool(r['contains_cancellation'])
            assert r['scenario'] == ns['create_scenario'](row,contains,state=='prior')
            assert r['prompt'] == r['prompt_template'].format(scenario=r['scenario'],implicature=r['implicature'],
                   question=r['question'],options=r['options_str'],speaker=r['speaker'])
            assert r['system_prompt'] == ns['SYSTEM_PROMPT']
            enc = ast.literal_eval(r['option_encoding'])
            assert set(enc)=={'True','False'} and set(enc.values())=={'1','2'}
            st = 'prior' if state=='prior' else state if contains else 'baseline'
            key = (r['id'],st,enc['True'])
            rec = {'item_id':r['id'],'phenomenon':r['implicature_type'],'state':st,
                   'true_label':enc['True'],'false_label':enc['False'],
                   'prompt':r['prompt'],'system_prompt':r['system_prompt']}
            if key in rows:
                assert rows[key]==rec, 'Baseline differs across source controls'
            else:
                rows[key] = rec
    assert all(s==ids_by_dataset[0] for s in ids_by_dataset)
    assert len(rows)==3252
    audit = {'upstream_commit':'15d1c58d1d3cb8c198c07ae5c1e63531a672b10d',
             'n_unique':len(rows),'n_items':271,'source_rows':counts,'source_sha256':hashes,
             'source_formatter_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'dropped_source_bug_item':'some_all_8 excluded by canonical parent, not by model results',
             'counts':pd.DataFrame(list(rows.values())).groupby('phenomenon').item_id.nunique().to_dict()}
    return list(rows.values()),audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--model',type=Path)
    ap.add_argument('--model-id')
    ap.add_argument('--revision')
    ap.add_argument('--output',type=Path)
    ap.add_argument('--prepare-only',action='store_true')
    ap.add_argument('--shard',type=int,default=0)
    ap.add_argument('--n-shards',type=int,default=1)
    ap.add_argument('--interface',choices=['bare','common-chat'],required=True)
    ap.add_argument('--common-tokenizer',type=Path,required=True)
    ap.add_argument('--bos-token-id',type=int,default=None)
    a=ap.parse_args();rows,audit=prepare(a.root)
    assert 0 <= a.shard < a.n_shards
    selected=set(sorted({r['item_id'] for r in rows})[a.shard::a.n_shards])
    rows=[r for r in rows if r['item_id'] in selected]
    if a.prepare_only:
        print(json.dumps(audit));return
    assert all([a.model,a.model_id,a.revision,a.output]) and not a.output.exists()
    a.output.mkdir(parents=True);start=time.monotonic()
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    seq=AutoConfig.from_pretrained(a.model,local_files_only=True).is_encoder_decoder
    tok=AutoTokenizer.from_pretrained(a.common_tokenizer,local_files_only=True,padding_side='left',use_fast=not seq)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    common=None
    if a.interface=='common-chat':
        tok.chat_template=AutoTokenizer.from_pretrained(a.common_tokenizer,local_files_only=True).chat_template
        common=str(a.common_tokenizer)
    else:
        tok.chat_template=None
    labels=[tok.encode(c,add_special_tokens=False) for c in ['1','2']]
    assert all(len(x)==1 for x in labels)
    label_ids=[x[0] for x in labels]
    cls=AutoModelForSeq2SeqLM if seq else AutoModelForCausalLM
    model=cls.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,
                             device_map={'':0},weights_only=True).eval()

    def text(r,condition):
        p=r['prompt']+('\nReply with only 1 or 2.' if condition=='format' else '')
        if tok.chat_template and not seq:
            return tok.apply_chat_template([{'role':'system','content':r['system_prompt']},{'role':'user','content':p}],
                     tokenize=False,add_generation_prompt=True,enable_thinking=False)
        return r['system_prompt']+'\n\n'+p

    @torch.inference_mode()
    def read(token_ids):
        inp=tok.pad({'input_ids':token_ids,'attention_mask':[[1]*len(x) for x in token_ids]},padding=True,return_tensors='pt').to(model.device)
        if model.config.model_type=='gpt2':
            inp['position_ids']=(inp.attention_mask.long().cumsum(-1)-1).masked_fill(inp.attention_mask==0,0)
        logits=next_logits(model,inp);target=logits[:,label_ids]
        probs=target.softmax(-1).cpu().tolist()
        mass=(target.logsumexp(-1)-logits.logsumexp(-1)).exp().cpu().tolist()
        tops=logits.argmax(-1).cpu().tolist()
        return [{'label_probs':p,'support_mass':m,'global_top_token_id':t} for p,m,t in zip(probs,mass,tops)]

    results={};controls=[];hashes={}
    for condition in ['parent','format']:
        token_ids=[tok.encode(text(r,condition),add_special_tokens=seq) for r in rows]
        if a.bos_token_id is not None:
            assert a.interface=='common-chat'
            assert all(ids[0]==tok.bos_token_id for ids in token_ids)
            assert 0<=a.bos_token_id<model.get_input_embeddings().weight.shape[0]
            token_ids=[[a.bos_token_id]+ids[1:] for ids in token_ids]
        hashes[condition]=hashlib.sha256(json.dumps(token_ids).encode()).hexdigest()
        probe=token_ids[:7]+token_ids[-1:];many=read(probe)
        delta=max(max(abs(x-y) for x,y in zip(read([probe[i]])[0]['label_probs'],many[i]['label_probs'])) for i in [0,7])
        controls.append({'condition':condition,'first_last_batch_prob_delta':delta,'pass':delta<.001})
        (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2))
        assert delta<.001,'Numerical gate failed'
        with (a.output/(condition+'-predictions.jsonl')).open('w') as f:
            for offset in range(0,len(rows),8):
                for r,reading in zip(rows[offset:offset+8],read(token_ids[offset:offset+8])):
                    rec={k:v for k,v in r.items() if k not in ['prompt','system_prompt']}
                    rec.update(condition=condition,**reading)
                    rec['p_true']=reading['label_probs'][int(r['true_label'])-1]
                    rec['support_argmax_present']=reading['global_top_token_id'] in label_ids
                    rec['prompt_sha256']=hashlib.sha256(text(r,condition).encode()).hexdigest()
                    results[condition,r['item_id'],r['state'],r['true_label']]=rec
                    f.write(json.dumps(rec)+'\n')
                f.flush()
        print(json.dumps({'condition_done':condition,'n':len(rows)}),flush=True)
    items=sorted({r['item_id'] for r in rows});summary={};details=[]
    for condition in ['parent','format']:
        groups=defaultdict(list)
        for item in items:
            states={s:np.mean([results[condition,item,s,o]['p_true'] for o in ['1','2']])
                    for s in ['baseline','prior','cancel','irrelevant','negation','strengthen']}
            base=states['baseline'];delta=states['cancel']-base
            records=[results[condition,item,s,o] for s in states for o in ['1','2']]
            d={'item_id':item,'phenomenon':records[0]['phenomenon'],'condition':condition,**states,
               'recognition':float(base>.5),'cancellation_recognition':float(delta<0),
               'joint_update':float(base>.5 and delta<0),'strengthen_recognition':float(states['strengthen']>base),
               'irrelevant_argmax_preserved':float((states['irrelevant']>.5)==(base>.5)),
               'irrelevant_decrease':float(states['irrelevant']<base),
               'cancel_delta':delta,'irrelevant_delta':states['irrelevant']-base,
               'cancel_minus_irrelevant_delta':states['cancel']-states['irrelevant'],
               'cancel_numerical_boundary':float(abs(delta)<=.001),
               'mean_support_mass':float(np.mean([r['support_mass'] for r in records])),
               'support_argmax_fraction':float(np.mean([r['support_argmax_present'] for r in records])),
               'max_order_ptrue_difference':max(abs(results[condition,item,s,'1']['p_true']-results[condition,item,s,'2']['p_true']) for s in states)}
            groups[d['phenomenon']].append(d);details.append(d)
        summary[condition]={g:{k:estimate([r[k] for r in rs]) for k in rs[0] if k not in ['item_id','phenomenon','condition']} for g,rs in groups.items()}
    (a.output/'item-results.jsonl').write_text(''.join(json.dumps(d)+'\n' for d in details))
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2))
    config={'task':'implicaturex','model':a.model_id,'revision':a.revision,'dtype':'float32','n':len(rows)*2,
            'shard':a.shard,'n_shards':a.n_shards,'items':sorted(selected),
            'interface':a.interface,
            'complete':True,'wall_seconds':time.monotonic()-start,'audit':audit,'numerical_gate_pass':True,
            'input_token_hashes':hashes,'common_template':common,'common_tokenizer':str(a.common_tokenizer),'bos_token_id_override':a.bos_token_id,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'limits':['Exact published prompts; FP32 differs from parent BF16. No source checkpoint revision given.',
                      'Approx control has no human norm and may not be pragmatically neutral; diagnostic is not gold FPR.',
                      'MCQ normalized probability is not direct knowledge or human Likert z-score.']}
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    print(json.dumps({'complete':True,'seconds':config['wall_seconds'],'n':config['n']}),flush=True)


if __name__=='__main__':main()
