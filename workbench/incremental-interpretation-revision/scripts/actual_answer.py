"""E87 exact existing native prompts, greedy answer measurement without new gold."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import time
from data import CACHE, sha
from data_v2 import digest
from current_open_baseline import tokenizer, prepare as strict_prepare
from source_acceptance import prepare as plain_prepare


def tasks(root, tok):
    rows = list(map(json.loads, (root.parent / 'E86/data-v1.jsonl').read_text().splitlines()))
    originals = [dict(r, item_id=r['original_item_id']) for r in rows if r['task_kind'] == 'QA_PLAIN']
    all_tasks = []
    for t in strict_prepare(originals, tok):
        if t['readout'] != 'words':
            continue
        t['operation'] = 'QA_STRICT' if t['operation'] == 'DIRECT' else 'QA_RECOVER'
        all_tasks.append(t)
    for t in plain_prepare(rows, tok):
        if t['readout'] != 'words':
            continue
        t['operation'] = t['row']['task_kind']
        all_tasks.append(t)
    assert len(all_tasks) == 6064
    assert len({(t['row']['item_id'], t['mapping'], t['operation']) for t in all_tasks}) == 6064
    return all_tasks


def run(a):
    import torch, transformers
    from transformers import AutoConfig, AutoModelForImageTextToText, FineGrainedFP8Config
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com')
    lock = (CACHE / 'E52/gpu-slots' / str(a.gpu)).open('a'); fcntl.flock(lock, fcntl.LOCK_EX)
    torch.manual_seed(87); torch.set_num_threads(4); torch.backends.cuda.matmul.allow_tf32=False
    tok = tokenizer(a.model); all_tasks = tasks(a.root, tok)
    selected = [t for t in all_tasks if int(t['row']['sentence_sha256'][:16], 16) % a.shards == a.shard]
    assert selected
    # Verify every visible prompt against original run bytes before any generation.
    mothers = {}
    for parent in ['E82', 'E86']:
        for r in json.loads((a.root.parent / parent / 'runner-pids-v1.json').read_text()):
            if r['model'] != a.model.name: continue
            p = Path(r['out']); c = json.loads((p/'config.json').read_text())
            assert sha(p/'predictions.jsonl') == c['predictions_sha256']
            for x in map(json.loads, (p/'predictions.jsonl').read_text().splitlines()):
                if x['readout'] != 'words': continue
                if parent == 'E82': op='QA_STRICT' if x['operation']=='DIRECT' else 'QA_RECOVER'
                else: op='GRAM_ACCEPT' if x['item_id'].startswith('GRAM:') else 'QA_PLAIN'
                key=x['item_id'], x['mapping'], op
                assert key not in mothers; mothers[key]=x
    for t in all_tasks:
        old = mothers[t['row']['item_id'], t['mapping'], t['operation']]
        assert old['prompt_sha256'] == digest(t['prompt'])
        assert old['candidate_gold'] == t['candidate_gold']
    a.out.mkdir(parents=True,exist_ok=True); assert not (a.out/'predictions.jsonl').exists()
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True)
    kwargs=dict(local_files_only=True,dtype=torch.bfloat16,attn_implementation='eager')
    if getattr(cfg,'quantization_config',None):
        q=dict(cfg.quantization_config);q['dequantize']=True;kwargs['quantization_config']=FineGrainedFP8Config(**q)
    start=time.monotonic()
    model=AutoModelForImageTextToText.from_pretrained(a.model,**kwargs).to('cuda').eval()
    config=dict(model=a.model.name, model_manifest_sha256=sha(a.model/'manifest.json'),
        data_sha256=sha(a.root.parent/'E86/data-v1.jsonl'),parent_QA_sha256=sha(a.root.parent/'E82/data-v1.jsonl'),
        code_sha256=sha(Path(__file__)), tasks=len(selected), shard=a.shard,shards=a.shards,gpu=a.gpu,
        seed=87,max_new_tokens=32,do_sample=False, thinking_enabled=False,dtype='bfloat16',
        transformers=transformers.__version__,torch=torch.__version__,prompt_verification='Every task SHA matches completed E82/E86 scoring prompt')
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    selected.sort(key=lambda t:(t['common'],t['row']['item_id'],t['operation'],t['mapping']))
    with (a.out/'predictions.jsonl').open('w') as f:
        for i,t in enumerate(selected):
            ids=tok.encode(t['prompt'],add_special_tokens=False)
            x=torch.tensor([ids],device=model.device)
            with torch.inference_mode():
                y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,
                    max_new_tokens=32,use_cache=True,pad_token_id=tok.pad_token_id)
            new=y[0,len(ids):].tolist(); text=tok.decode(new,skip_special_tokens=True)
            eos=model.generation_config.eos_token_id
            eos=[eos] if isinstance(eos,int) else (eos or [])
            stopped=bool(new and new[-1] in eos);cap=len(new)>=32 and not stopped
            match=re.match(r'^(Yes|No)(?=$|[\s.,!?;:])',text.strip(),re.IGNORECASE)
            label=match.group(1).capitalize() if match else None
            gold=t['row']['grounded_gold']; old=mothers[t['row']['item_id'],t['mapping'],t['operation']]
            old_label=gold if old['correct'] else ('No' if gold=='Yes' else 'Yes')
            z=dict(item_id=t['row']['item_id'],source_unit=t['row']['source_unit'],operation=t['operation'],
                mapping=t['mapping'],prompt_sha256=digest(t['prompt']),prompt_tokens=len(ids),output_token_ids=new,
                output_text=text,label=label,grounded_gold=gold,stopped=stopped,cap=cap,
                known_correct=None if label is None else label==gold,
                lower_correct=bool(stopped and label==gold),upper_correct=bool(label is None or not stopped or label==gold),
                strict_exact=text.strip().lower() in ['yes','no'],forced_label=old_label,
                differs_from_forced=None if label is None else label!=old_label,
                forced_choice_mass=sum(__import__('math').exp(v) for v in old['candidate_logprobs']))
            f.write(json.dumps(z)+'\n')
            if i%64==0:f.flush();print('E87',a.model.name,a.shard,i+1,'/',len(selected),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    (a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print('E87 DONE',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['root','model','out']:p.add_argument('--'+n,type=Path,required=True)
    for n in ['gpu','shard','shards']:p.add_argument('--'+n,type=int,required=True)
    run(p.parse_args())
