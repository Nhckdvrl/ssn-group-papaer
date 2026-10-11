"""E88 one predicate-vs-NP diagnostic; E54 baseline/instruction cached."""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha
from data_v2 import digest
from gpu_deadline import ensure_gpu_allowed
from prequestion_oracle_map import score,tensors
from verb_frame_lookahead import prepare


def run(a):
    ensure_gpu_allowed()
    import torch
    from transformers import AutoTokenizer,AutoConfig,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    ensure_gpu_allowed();torch.manual_seed(88);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    data=a.root/'data-v1.jsonl';assert sha(data)==json.loads(data.with_suffix('.manifest.json').read_text())['data_sha256']
    allrows=list(map(json.loads,data.read_text().splitlines()))
    rows=[r for r in allrows if int(r['frame_locator']['GP_source_unit'].split(':')[-1][:16],16)%a.shards==a.shard]
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks,baselines=prepare(rows,tok)
    parent=a.root.parent/'E54/runs-v1'/a.model.name;pc=json.loads((parent/'config.json').read_text())
    assert sha(parent/'predictions.jsonl')==pc['predictions_sha256']
    mother={(p['item_id'],p['readout'],p['mapping']):p for p in map(json.loads,(parent/'predictions.jsonl').read_text().splitlines()) if p['operation']=='CAUSAL'}
    for t in baselines:
        old=mother[t['row']['item_id'],t['readout'],t['mapping']]
        assert old['prompt_sha256']==digest(t['prompt']) and old['candidate_gold']==t['candidate_gold']
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    start=time.monotonic();cfg=AutoConfig.from_pretrained(a.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    fixed=min(rows,key=lambda r:r['item_id'])['item_id'];tests=[t for t in baselines if t['row']['item_id']==fixed]
    four=score(model,tests,tok.pad_token_id);two=score(model,tests,tok.pad_token_id,use_4d=False)
    delta=max(abs(x-y) for a1,b1 in zip(four,two) for x,y in zip(a1,b1))
    md=max(abs(x-y) for t,values in zip(tests,four) for x,y in zip(values,mother[t['row']['item_id'],t['readout'],t['mapping']]['candidate_logprobs']))
    assert max(delta,md)<.001,(delta,md)
    # Check every new mask's source boundaries before the first scientific forward.
    edge_counts={}
    for t in tasks:
        edge_counts[t['row']['item_id'],t['readout'],t['mapping'],t['operation']]=sum(k>q for q in t['query_tokens'] for k in t['source_tokens'])
        assert set(t['query_tokens'])<=set(t['source_tokens'])
    config=dict(model=a.model.name,model_manifest_sha256=sha(a.model/'manifest.json'),data_sha256=sha(data),
        code_sha256=sha(Path(__file__)),builder_sha256=sha(Path(__file__).with_name('verb_frame_lookahead.py')),
        mask_score_sha256=sha(Path(__file__).with_name('prequestion_oracle_map.py')),seed=88,dtype='float32',attention='eager',
        tasks=len(tasks),QA=len(rows),gpu=a.gpu,shard=a.shard,shards=a.shards,batch_size=4,
        instrument=dict(fixed_item=fixed,causal_4d_2d_max_delta=delta,mother_E54_max_delta=md),
        reused_baseline=str(parent),reused_predictions_sha256=pc['predictions_sha256'])
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    tasks.sort(key=lambda t:(t['encoded'][1],t['row']['item_id'],t['operation']))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),4):
            ensure_gpu_allowed();batch=tasks[begin:begin+4];values=score(model,batch,tok.pad_token_id)
            for t,lp in zip(batch,values):
                r=t['row'];gold=t['candidate_gold'];mx=max(lp);den=mx+math.log(sum(math.exp(x-mx) for x in lp))
                z=dict(item_id=r['item_id'],source_unit=r['source_unit'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],
                    candidate_gold=gold,candidate_logprobs=lp,correct=max(range(2),key=lp.__getitem__)==gold,p_correct=math.exp(lp[gold]-den),
                    prompt_sha256=digest(t['prompt']),source_tokens=t['source_tokens'],query_tokens=t['query_tokens'],
                    new_future_edges=edge_counts[r['item_id'],t['readout'],t['mapping'],t['operation']],frame_locator=r['frame_locator'])
                f.write(json.dumps(z)+'\n')
            if begin%128==0:f.flush();print('E88',a.model.name,a.shard,begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    for name in ['run_verb_frame_lookahead.py','verb_frame_lookahead.py','prequestion_oracle_map.py','revision_interventions.py']:
        (a.out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    print('E88 DONE',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['root','model','out']:p.add_argument('--'+n,type=Path,required=True)
    for n in ['gpu','shard','shards']:p.add_argument('--'+n,type=int,required=True)
    run(p.parse_args())
