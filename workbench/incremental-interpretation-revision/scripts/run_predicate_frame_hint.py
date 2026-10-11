"""E89 two timings of one predicate frame oracle, actual native answers."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import time
from data import CACHE,sha
from data_v2 import digest
from current_open_baseline import tokenizer
from predicate_frame_hint import prepare
from analyze_actual_answer import semantic_label
from gpu_deadline import ensure_gpu_allowed


def run(a):
    ensure_gpu_allowed()
    import torch,transformers
    from transformers import AutoConfig,AutoModelForImageTextToText,FineGrainedFP8Config
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    ensure_gpu_allowed();torch.manual_seed(89);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    data=a.root/'data-v1.jsonl';assert sha(data)==json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    allrows=list(map(json.loads,data.read_text().splitlines()))
    rows=[r for r in allrows if int(r['frame_locator']['GP_source_unit'].split(':')[-1][:16],16)%a.shards==a.shard]
    tok=tokenizer(a.model);tasks=prepare(rows,tok);mothers={}
    for run in json.loads((a.root.parent/'E87/runner-pids-v1.json').read_text()):
        if run['model']!=a.model.name:continue
        out=Path(run['out']);c=json.loads((out/'config.json').read_text());assert sha(out/'predictions.jsonl')==c['predictions_sha256']
        for p in map(json.loads,(out/'predictions.jsonl').read_text().splitlines()):
            if p['operation']=='QA_STRICT':mothers[p['item_id'],p['mapping']]=p
    for t in tasks:
        assert t['native_prompt_sha256']==mothers[t['row']['item_id'],t['mapping']]['prompt_sha256']
        assert t['row']['grounded_gold']==mothers[t['row']['item_id'],t['mapping']]['grounded_gold']
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);kwargs=dict(local_files_only=True,dtype=torch.bfloat16,attn_implementation='eager')
    if getattr(cfg,'quantization_config',None):
        q=dict(cfg.quantization_config);q['dequantize']=True;kwargs['quantization_config']=FineGrainedFP8Config(**q)
    start=time.monotonic();model=AutoModelForImageTextToText.from_pretrained(a.model,**kwargs).to('cuda').eval()
    config=dict(model=a.model.name,model_manifest_sha256=sha(a.model/'manifest.json'),data_sha256=sha(data),
        code_sha256=sha(Path(__file__)),builder_sha256=sha(Path(__file__).with_name('predicate_frame_hint.py')),
        parser_sha256=sha(Path(__file__).with_name('analyze_actual_answer.py')),tasks=len(tasks),QA=len(rows),
        gpu=a.gpu,shard=a.shard,shards=a.shards,seed=89,max_new_tokens=32,do_sample=False,dtype='bfloat16',
        thinking_enabled=False,transformers=transformers.__version__,torch=torch.__version__,
        source_prefix_verification='Every late-hint Source prefix equals original E82; all native baseline prompt SHA match E87')
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    tasks.sort(key=lambda t:(len(t['prompt']),t['row']['item_id'],t['operation'],t['mapping']))
    with (a.out/'predictions.jsonl').open('w') as f:
        for i,t in enumerate(tasks):
            ensure_gpu_allowed();ids=tok.encode(t['prompt'],add_special_tokens=False);x=torch.tensor([ids],device=model.device)
            with torch.inference_mode():y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,max_new_tokens=32,use_cache=True,pad_token_id=tok.pad_token_id)
            new=y[0,len(ids):].tolist();text=tok.decode(new,skip_special_tokens=True);label,status=semantic_label(text,t['mapping'])
            eos=model.generation_config.eos_token_id;eos=[eos] if isinstance(eos,int) else (eos or [])
            stopped=bool(new and new[-1] in eos);cap=len(new)>=32 and not stopped;r=t['row'];gold=r['grounded_gold']
            z=dict(item_id=r['item_id'],source_unit=r['source_unit'],operation=t['operation'],mapping=t['mapping'],
                prompt_sha256=digest(t['prompt']),native_prompt_sha256=t['native_prompt_sha256'],prompt_tokens=len(ids),
                output_text=text,output_token_ids=new,label=label,semantic_parse_status=status,grounded_gold=gold,
                stopped=stopped,cap=cap,valid=label is not None,known_correct=None if label is None else label==gold,
                lower_correct=bool(stopped and label==gold),upper_correct=bool(label is None or not stopped or label==gold))
            f.write(json.dumps(z)+'\n')
            if i%64==0:f.flush();print('E89',a.model.name,a.shard,i+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    for name in ['run_predicate_frame_hint.py','predicate_frame_hint.py','analyze_actual_answer.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E89 DONE',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['root','model','out']:p.add_argument('--'+n,type=Path,required=True)
    for n in ['gpu','shard','shards']:p.add_argument('--'+n,type=int,required=True)
    run(p.parse_args())
