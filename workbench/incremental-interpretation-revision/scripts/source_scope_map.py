"""E59: fixed source/question, explicit entailment support versus world truth."""
import argparse
import collections
import itertools
import json
import math
import os
from pathlib import Path
import time

import torch
from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
from data import sha,write_jsonl
from data_v2 import digest
from reading_map import SYSTEM,encode_choices,sequence_scores

RULES={
 'O2':SYSTEM,
 'G2':SYSTEM+' Answer Yes only if the sentence explicitly entails a yes answer to the question. Answer No if that answer is unasserted or contradicted. A plausible or merely compatible extra event is insufficient for Yes.',
 'W3':SYSTEM+' Determine what the full sentence establishes. Answer Yes if it entails a yes answer to the question; No if it contradicts that answer; Unknown (not determined by the sentence) if neither is established. Do not assume unmentioned events are impossible.'}


def build(metadata,out):
    rows=[json.loads(x) for x in metadata.read_text().splitlines()]
    groups=collections.defaultdict(list)
    for r in rows:
        if r['needs_revision'] and r['question_format']=='yn':groups[(r.get('analysis_pair_id',r['pair_id']),r['question'])].append(r)
    result=[];rejected=[]
    def qualified(r):
        return r.get('step5_status') in ('agreed','adjudicated') and len(r.get('step5_passes',[]))==2 and all(a['grammar']=='acceptable' for a in r['step5_passes']) and r['step5_annotation']['grammar']=='acceptable'
    for key,group in groups.items():
        if {r.get('analysis_condition',r['condition']) for r in group}!={'gp','control'}:
            rejected.append(dict(pair=key,reason='Unmatched exact source question'));continue
        if not all(qualified(r) for r in group):
            rejected.append(dict(pair=key,reason='Incomplete semantic/grammar qualification'));continue
        labels={r['step5_annotation']['label'] for r in group}
        if len(labels)!=1:
            rejected.append(dict(pair=key,reason='Different literal classes across paired sources'));continue
        for r in group:
            label=r['step5_annotation']['label'];grounded='Yes' if label=='ENTAILED' else 'No'
            world={'ENTAILED':'Yes','CONTRADICTED':'No','NEITHER':'Unknown'}[label]
            result.append({**r,'literal_label':label,'grounded_gold':grounded,'world_gold':world,
                'source_gold_matches_grounding':r['options'][r['gold']]==grounded})
    write_jsonl(out,result);write_jsonl(out.with_suffix('.excluded.jsonl'),rejected)
    out.with_suffix('.manifest.json').write_text(json.dumps(dict(metadata_sha256=sha(metadata),data_sha256=sha(out),
        rows=len(result),question_pairs=len({(r.get('analysis_pair_id',r['pair_id']),r['question']) for r in result}),
        literal_classes=dict(collections.Counter(r['literal_label'] for r in result)),
        gold_derivation='Deterministic mapping of completed Step5 T1 to explicitly defined task rules; source gold retained.',
        excluded_question_pairs=len(rejected)),indent=2)+'\n')


def render(tokenizer,system,content):
    messages=[dict(role='system',content=system),dict(role='user',content=content)]
    if tokenizer.chat_template:
        try:return tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
        except Exception:return tokenizer.apply_chat_template([dict(role='user',content=system+'\n\n'+content)],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    return system+'\n\n'+content+'\n\nAnswer:'


def tasks(rows,tokenizer):
    for row in rows:
        for scope in ('O2','G2','W3'):
            options=row['options'] if scope!='W3' else ['Yes','No','Unknown']
            gold=row['options'][row['gold']] if scope=='O2' else row['grounded_gold'] if scope=='G2' else row['world_gold']
            for reading in ('R0','R1','R5'):
                sentence=row['sentence']+'\n'+row['sentence'] if reading=='R1' else row['sentence']
                for mapping,order in enumerate(itertools.permutations(range(len(options)))):
                    shown=[options[i] for i in order];letters=list('ABC'[:len(shown)])
                    content=f'Sentence:\n{sentence}\n\nQuestion:\n{row["question"]}\n'
                    content+='\n'.join(f'{letter}. {option}' for letter,option in zip(letters,shown))
                    for readout in ('letters','words'):
                        directive=('A or B.' if len(shown)==2 else 'A, B, or C.') if readout=='letters' else ('Yes or No.' if len(shown)==2 else 'Yes, No, or Unknown.')
                        body=content+'\nAnswer only '+directive
                        if reading=='R5':body='Question:\n'+row['question']+'\n\n'+body
                        yield dict(row=row,scope=scope,reading=reading,mapping=mapping,format='B',readout=readout,
                            prompt=render(tokenizer,RULES[scope],body),candidates=letters if readout=='letters' else shown,
                            candidate_gold=shown.index(gold),displayed_options=shown)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--build-out',type=Path)
    ap.add_argument('--model',type=Path);ap.add_argument('--out',type=Path);ap.add_argument('--batch-size',type=int,default=16);args=ap.parse_args()
    if args.build_out:build(args.data,args.build_out);return
    assert args.model and args.out
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(52);torch.set_num_threads(8);start=time.monotonic()
    args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'predictions.jsonl').exists()
    rows=[json.loads(x) for x in args.data.read_text().splitlines()]
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    cfg=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    selected=list(tasks(rows,tokenizer));selected.sort(key=lambda t:len(t['prompt']))
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        code_sha256=sha(Path(__file__)),tasks=len(selected),dtype='float32',seed=52,scope_rules=RULES)
    (args.out/'source_scope_map.py').write_bytes(Path(__file__).read_bytes());(args.out/'reading_map.py').write_bytes(Path(__file__).with_name('reading_map.py').read_bytes())
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (args.out/'predictions.jsonl').open('w') as stream:
        for begin in range(0,len(selected),args.batch_size):
            batch=selected[begin:begin+args.batch_size];enc=[encode_choices(tokenizer,t) for t in batch]
            values=sequence_scores(model,[s for ss,n in enc for s in ss],[n for ss,n in enc for s in ss],tokenizer.pad_token_id)
            cursor=0
            for t,(ss,n) in zip(batch,enc):
                scores=values[cursor:cursor+len(ss)];cursor+=len(ss);row=t['row']
                denom=max(scores)+math.log(sum(math.exp(x-max(scores)) for x in scores))
                winner=max(range(len(scores)),key=scores.__getitem__)
                record={k:row[k] for k in ('item_id','construction','sentence_sha256','literal_label','source_gold_matches_grounding')}
                record.update(pair_id=row.get('analysis_pair_id',row['pair_id']),cluster_id=row.get('analysis_cluster_id',row['cluster_id']),
                    condition=row.get('analysis_condition',row['condition']),question=row['question'],
                    question_target=row.get('analysis_question_target',row['question_target']),
                    scope=t['scope'],readout=t['readout'],reading=t['reading'],mapping=t['mapping'],candidate_gold=t['candidate_gold'],
                    displayed_options=t['displayed_options'],prompt=t['prompt'],prompt_sha256=digest(t['prompt']),
                    prompt_tokens=len(tokenizer.encode(t['prompt'],add_special_tokens=not bool(tokenizer.chat_template))),
                    candidate_logprobs=scores,correct=winner==t['candidate_gold'],p_correct=math.exp(scores[t['candidate_gold']]-denom),
                    predicted_option=t['displayed_options'][winner])
                stream.write(json.dumps(record)+'\n')
            assert cursor==len(values);stream.flush()
            if begin%(args.batch_size*20)==0:print(begin,'/',len(selected),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')


if __name__=='__main__':main()
