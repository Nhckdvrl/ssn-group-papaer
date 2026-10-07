"""E67 unchanged E65 source/goals, later faithful free role use."""
import argparse
import collections
import fcntl
import json
import os
from pathlib import Path
import time
from data import CACHE,sha,write_jsonl
from data_v2 import digest
from natural_cue_patching import blocks
from shared_source_cross_use import render,source_info,greedy
from paraphrase_map import INSTRUCTION,sentence_parts


def build(data,out):
    grouped=collections.defaultdict(list)
    for r in map(json.loads,data.read_text().splitlines()):grouped[r['source_unit']].append(r)
    result=[]
    for uid,g in sorted(grouped.items()):
        r=g[0];assert all(x['sentence']==r['sentence'] and x['reading_goals']==r['reading_goals'] for x in g)
        result.append(dict(item_id=uid,sentence=r['sentence'],sentence_sha256=r['sentence_sha256'],reading_goals=r['reading_goals'],construction=r['construction'],condition=r['condition'],cluster_id=r['analysis_cluster_id'],member_ids=[x['item_id'] for x in g]))
    assert len(result)==356 and not out.exists();out.parent.mkdir(parents=True,exist_ok=True);write_jsonl(out,result)
    out.with_suffix('.manifest.json').write_text(json.dumps(dict(E65_data_sha256=sha(data),data_sha256=sha(out),sources=356,clusters=len({r['cluster_id'] for r in result})),indent=2)+'\n')


def run(a):
    import torch
    from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    torch.manual_seed(67);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    rows=[json.loads(l) for l in a.data.read_text().splitlines()];assert len(rows)==356
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();decoder=blocks(model)
    tasks=[]
    for r in rows:
        for op,target in [('NONE',None),('INITIAL','initial'),('FINAL','final')]:
            prompt=render(tok,r['sentence'],INSTRUCTION)
            if target:
                marker='Read this sentence carefully.\nSentence:\n';assert prompt.count(marker)==1
                prompt=prompt.replace(marker,'Read this sentence carefully.\nReading goal:\n'+r['reading_goals'][target]+'\nSentence:\n')
            ids=tok.encode(prompt,add_special_tokens=not bool(tok.chat_template));g=dict(row=dict(r,source_unit=r['item_id'],donor_source_unit=r['item_id']),ids=ids,prompt=prompt,patch_tokens=[],donor_tokens=[])
            prefix,source=source_info(tok,dict(row=r,prompt=prompt));assert ids[:len(prefix)]==prefix
            tasks.append((g,op))
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    config=dict(model_path=str(a.model),model_manifest_sha256=sha(a.model/'manifest.json'),data_sha256=sha(a.data),code_sha256=sha(Path(__file__)),seed=67,dtype='float32',attention='eager',gpu_index=a.gpu,tasks=len(tasks),cap=256,operations=['NONE','INITIAL','FINAL'],phase='science',source_before_task=True,dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in ['shared_source_cross_use.py','paraphrase_map.py']})
    (a.out/'input-preflight.json').write_text(json.dumps(dict(tasks=len(tasks),source_prefix_valid=True,examples=[dict(source=g['row']['item_id'],goal=op,prompt_sha256=digest(g['prompt']),start_ids=g['ids'][:8]) for g,op in tasks[:12]]),indent=2)+'\n')
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for i,(g,op) in enumerate(tasks):
            ids=greedy(model,decoder,{},g,None,'BASE',256);text=tok.decode(ids,skip_special_tokens=True);r=g['row'];parts=sentence_parts(text)
            x=dict(item_id=r['item_id'],sentence_sha256=r['sentence_sha256'],construction=r['construction'],condition=r['condition'],cluster_id=r['cluster_id'],format='TASK_AFTER_SOURCE',reading=op,prompt_sha256=digest(g['prompt']),text=text,text_sha256=digest(text),generated_token_ids=ids,capped=len(ids)==256,finish_reason='length' if len(ids)==256 else 'stop',automatic_sentence_parts=parts,automatic_two_sentences=len(parts)==2)
            f.write(json.dumps(x)+'\n');f.flush()
            if (i+1)%30==0:print('E67 roles',i+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    for n in ['goal_free_relations.py','shared_source_cross_use.py','paraphrase_map.py']:(a.out/n).write_bytes(Path(__file__).with_name(n).read_bytes())
    print('E67 complete',a.model.name,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--build-out',type=Path);p.add_argument('--model',type=Path);p.add_argument('--out',type=Path);p.add_argument('--gpu',type=int);a=p.parse_args()
    if a.build_out:build(a.data,a.build_out)
    else:run(a)
