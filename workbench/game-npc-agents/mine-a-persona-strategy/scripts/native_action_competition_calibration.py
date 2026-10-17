#!/usr/bin/env python3
"""E66 small fixed-prefix numeric check against uncached full teacher forcing."""
import argparse
import json
import math
from pathlib import Path
import time
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,AutoModelForImageTextToText
from native_action_competition import command_tree


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert (a.run/'runtime.json').exists()
    manifest=json.loads((a.run/'manifest.json').read_text())
    # Same first four fixed contexts as the existing sham, independent of effect.
    with (a.run/'contexts.jsonl').open() as f:rows=[json.loads(next(f)) for _ in range(4)]
    with (a.run/'readouts.jsonl').open() as f:prior=[json.loads(next(f)) for _ in range(4)]
    torch.set_num_threads(1)
    path=Path(manifest['model']);tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True)
    if tokenizer.pad_token_id is None:tokenizer.pad_token_id=tokenizer.eos_token_id
    config=json.loads((path/'config.json').read_text())
    loader=AutoModelForImageTextToText if config['model_type']=='gemma3' else AutoModelForCausalLM
    start=time.monotonic()
    model=loader.from_pretrained(path,dtype=torch.bfloat16,device_map={'':'cuda:0'},
                                attn_implementation='sdpa',local_files_only=True).eval()
    load=time.monotonic()-start;start=time.monotonic();result=[]
    length=max(len(r['prefix_ids']) for r in rows)
    with torch.inference_mode():
        for target in ['goal','frown','examine_goal_item','observed_action']:
            if any(r['target_paths'][target] is None for r in rows):continue
            paths=[r['target_paths'][target] for r in rows]
            assert len({len(p) for p in paths})==1
            size=len(paths[0])
            ids=torch.tensor([[tokenizer.pad_token_id]*(length-len(r['prefix_ids']))+
                              r['prefix_ids']+p[:-1] for r,p in zip(rows,paths)],device='cuda')
            mask=torch.tensor([[0]*(length-len(r['prefix_ids']))+[1]*(len(r['prefix_ids'])+size-1)
                               for r in rows],device='cuda')
            positions=mask.cumsum(-1)-1;positions.masked_fill_(mask==0,0)
            logits=model(input_ids=ids,attention_mask=mask,position_ids=positions,
                         use_cache=False,logits_to_keep=size).logits.float()
            for i,(r,p,old) in enumerate(zip(rows,paths,prior)):
                _,_,node=command_tree(tokenizer,r['commands']);score=0.
                for step,token in enumerate(p):
                    allowed=[x for x in node if x is not None]
                    score+=float(torch.log_softmax(logits[i,step,allowed]/.7,-1)[allowed.index(token)])
                    node=node[token]
                previous=old['command_probabilities'][target]
                result.append({'case_id':r['case_id'],'persona':r['persona'],'context':r['context'],
                    'rule':r['rule'],'target':target,'cached_log_probability':previous['trie_log_probability'],
                    'teacher_forced_log_probability':score,'cached_probability':previous['trie_probability'],
                    'teacher_forced_probability':math.exp(score),
                    'probability_difference':math.exp(score)-previous['trie_probability']})
    report={'selection':'First four fixed contexts, same padding and batch size, not outcome-selected',
        'model':str(path),'rows':result,'max_abs_probability_difference':max(abs(r['probability_difference']) for r in result),
        'model_load_seconds':load,'wall_seconds':time.monotonic()-start,'native_actions_regenerated':0,'cloud_calls':0,
        'scope':'Numerical sensitivity of cached incremental versus uncached batched scoring; not a new model condition.'}
    a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}),flush=True)


if __name__=='__main__':main()
