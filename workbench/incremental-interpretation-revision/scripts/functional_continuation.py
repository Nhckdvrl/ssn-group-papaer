"""E23 greedy ordinary continuations, followed by independent semantic audit."""
import argparse
import collections
import json
import os
from pathlib import Path
import subprocess
import time
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from data import CACHE, sha, write_jsonl
from event_identity import digest

RECOVERY = 'Complete the final sentence while following the explicitly stated participant restrictions for that same activity.\n'


def build(cache, out):
    assert not out.exists()
    parents=[]
    for ex,style,version in [('E20','named','v1'),('E21','generic','v3')]:
        p=cache/f'{ex}-material-preparation-v1/audited-{version}.jsonl'
        for r in map(json.loads,p.read_text().splitlines()):
            if r['target_kind']=='source_np' and r['episode_anchor']=='same' and (ex=='E20' or r['exclusion_style']==style):
                parents.append((ex,style,r,p))
    rows=[]
    for ex,style,r,path in parents:
        prefix=r['sentence'][:r['target_start_char']]
        for mode in ('base','one_instruction'):
            prompt=prefix if mode=='base' else RECOVERY+prefix
            rows.append(dict(item_id='E23:'+r['item_id']+':'+mode, parent_item_id=r['item_id'], parent_experiment=ex,
                parent_data_sha256=sha(path), parent_sentence_sha256=r['sentence_sha256'], pair_id=r['pair_id'],
                source_np_option=r['source_np_option'], condition=r['condition'], role_evidence=r['role_evidence'],
                exclusion_style=style, mode=mode, prompt=prompt, prompt_sha256=digest(prompt), narrative_prefix=prefix,
                prefix_sha256=digest(prefix), original_sentence=r['sentence'], target_start_char=r['target_start_char'],
                prior_faithful_role=r['faithful_order'], prior_eligible=r['eligible'], gold=None))
    assert len(rows)==224 and len({r['prefix_sha256'] for r in rows})==112
    write_jsonl(out,rows)
    return dict(variants=len(rows), unique_narrative_prefixes=112, candidate_sha256=sha(out))


def adopt(data,reviews,out):
    j=list(map(json.loads,data.read_text().splitlines())); annotations={}
    for p in reviews:
        a=json.loads(p.read_text()); assert a['model']=='gpt-6-luna'
        for r in a['prefix_reviews']:
            assert r['prefix_sha256'] not in annotations
            annotations[r['prefix_sha256']]=(r,sha(p))
    assert set(annotations)=={r['prefix_sha256'] for r in j}
    for r in j:
        a,h=annotations[r['prefix_sha256']]
        assert a['prefix_is_exact_truncation'] is True
        assert a['role_restriction_status'] in ('clear','uncertain','changed')
        assert a['continuation_episode_scope'] in ('same_activity','uncertain','separate_activity')
        r.update(prefix_audit=a,prefix_review_sha256=h,eligible=r['prior_eligible'],
                 clear_functional_role=r['prior_faithful_role'] and a['role_restriction_status']=='clear' and a['continuation_episode_scope']=='same_activity')
    write_jsonl(out,j)
    report=dict(variants=len(j),candidate_sha256=sha(data),audited_sha256=sha(out),source_items=7,
                reviewed_prefixes=len(annotations),review_sha256=[sha(p) for p in reviews],
                clear_functional_role=sum(r['clear_functional_role'] for r in j),semantic_gold_labels=0)
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def run(args):
    assert not args.out.exists()
    report=json.loads(args.data.with_suffix('.audit.json').read_text()); assert report['audited_sha256']==sha(args.data)
    rows=list(map(json.loads,args.data.read_text().splitlines())); assert len(rows)==report['variants']==224
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left'); tok.pad_token_id=tok.eos_token_id
    groups={}; prefix_tokens={}
    for r in rows:
        assert digest(r['prompt'])==r['prompt_sha256']
        pre='' if r['mode']=='base' else RECOVERY
        # Encode with a real authored NP to reproduce likelihood prefix BPE,
        # rather than tokenizing a dangling space as an extra input token.
        full=pre+r['original_sentence']; start=len(pre)+r['target_start_char']
        enc=tok(full,add_special_tokens=False,return_offsets_mapping=True)
        index=next(i for i,(a,b) in enumerate(enc['offset_mapping']) if b>start and full[a:b].strip())
        ids=enc['input_ids'][:index]
        assert len(ids)>0
        groups[r['item_id']]=ids
        if r['mode']=='base': prefix_tokens[r['parent_item_id']]=digest(json.dumps(ids,separators=(',',':')))
    args.out.mkdir(parents=True)
    torch.manual_seed(0);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    cfg=dict(experiment='E23',task_count=len(rows),source_items=7,model=str(args.model),model_manifest=json.loads((args.model/'manifest.json').read_text()),
             data_sha256=sha(args.data),audit_sha256=sha(args.data.with_suffix('.audit.json')),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             code_sha256=sha(Path(__file__)),frozen=True,dtype='float32',tf32=False,attention='sdpa',seed=0,
             torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(),
             batch_size=8,do_sample=False,max_new_tokens=48,chat_template=False,
             recovery_instruction=RECOVERY,base_prefix_token_sha256=prefix_tokens,
             outcome='Independent auditor classifies first activity continuation; capped/unclear/no-activity outputs retained, no lexical heuristic gold.')
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n'); start=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    for p in model.parameters():p.requires_grad_(False)
    keys=sorted(groups,key=lambda k:(len(groups[k]),k));byid={r['item_id']:r for r in rows}; outputs={}
    with torch.inference_mode():
        for off in range(0,len(keys),8):
            kk=keys[off:off+8]
            batch=tok.pad([dict(input_ids=groups[k],attention_mask=[1]*len(groups[k])) for k in kk],return_tensors='pt').to('cuda')
            generation=model.generate(**batch,do_sample=False,max_new_tokens=48,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,use_cache=True)
            for i,k in enumerate(kk):
                ids=generation[i,batch['input_ids'].shape[1]:].tolist()
                if tok.eos_token_id in ids:ids=ids[:ids.index(tok.eos_token_id)+1]
                r=byid[k]
                outputs[k]=dict(r,completion=tok.decode(ids,skip_special_tokens=True),generated_token_ids=ids,
                                generated_sha256=digest(tok.decode(ids,skip_special_tokens=True)),input_token_sha256=digest(json.dumps(groups[k],separators=(',',':'))),
                                eos_reached=bool(ids and ids[-1]==tok.eos_token_id),token_cap_reached=len(ids)==48 and ids[-1]!=tok.eos_token_id)
            print(f'{off+len(kk)}/{len(keys)} elapsed={time.time()-start:.1f}s',flush=True)
    write_jsonl(args.out/'generations.jsonl',[outputs[r['item_id']] for r in rows])
    elapsed=time.time()-start;cfg.update(generations_sha256=sha(args.out/'generations.jsonl'),wall_seconds=elapsed,gpu_hours=elapsed/3600,peak_gpu_bytes=torch.cuda.max_memory_allocated())
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--out',type=Path,required=True)
    r=s.add_parser('run');r.add_argument('--data',type=Path,required=True);r.add_argument('--model',type=Path,default=CACHE/'models/Qwen3-8B');r.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt(args.data,args.reviews,args.out),indent=2))
    else:run(args)
