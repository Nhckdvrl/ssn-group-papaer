"""E79 original E71 correct-P1 input; cut only later direct Source consumption."""
import argparse,fcntl,json,math,os,time
from pathlib import Path
from data import CACHE,sha
from data_v2 import digest
from run_correct_prefix_binding import prepare,forward
from shared_source_cross_use import source_info
from natural_cue_patching import blocks

def prepared(row,tok):
    t=prepare(row,tok);_,keys=source_info(tok,t);first=t['spans'][0][1];assert all(x[1]==first for x in t['spans']) and max(keys)<first
    t['spans']=[(keys,first) for _ in t['sequences']];return t

def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(79);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    rows=list(map(json.loads,a.data.read_text().splitlines()));assert len(rows)==76 and sha(a.data)==json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256'];rows=[r for r in rows if int(r['sentence_sha256'][:16],16)%a.shards==a.shard];assert rows
    d=a.parent/'runs-v1'/a.model.name;pcfg=json.loads((d/'config.json').read_text());assert pcfg['data_sha256']==sha(a.data) and pcfg['predictions_sha256']==sha(d/'predictions.jsonl') and pcfg['model_manifest_sha256']==sha(a.model/'manifest.json')
    base={(r['item_id'],r['operation']):r for r in map(json.loads,(d/'predictions.jsonl').read_text().splitlines())}
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks=[prepared(r,tok) for r in rows];cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();decoder=blocks(model);checks=[]
    for t in sorted(tasks,key=lambda t:t['row']['item_id'])[:2]:
        native,h,_=forward(model,decoder,t,tok.pad_token_id,hidden=True);ref,_,_=forward(model,decoder,t,tok.pad_token_id,use_4d=False);_,ch,counts=forward(model,decoder,t,tok.pad_token_id,cut=True,hidden=True);old=base[t['row']['item_id'],'NATIVE'];assert old['prompt_sha256']==digest(t['prompt'])
        delta=max(abs(x-y) for x,y in zip(native,ref));pd=max(abs(x-y) for x,y in zip(native,old['candidate_logprobs']));assert max(delta,pd)<.001
        hd=0.
        for x,y in zip(h,ch):
            for i,s in enumerate(t['sequences']):off=x.shape[1]-len(s);end=t['spans'][i][1];hd=max(hd,float((x[i,off:off+end]-y[i,off:off+end]).abs().max()))
        assert hd==0. and min(counts)>0;checks.append(dict(item_id=t['row']['item_id'],native_LP_max_delta=delta,parent_LP_max_delta=pd,pre_second_clause_hidden_max_delta=hd,removed_edges_per_layer=counts))
    a.out.mkdir(exist_ok=True,parents=True);assert not (a.out/'predictions.jsonl').exists();config=dict(data_sha256=sha(a.data),model_manifest_sha256=sha(a.model/'manifest.json'),code_sha256=sha(Path(__file__)),parent_predictions_sha256=pcfg['predictions_sha256'],dtype='float32',attention='eager',seed=79,shard=a.shard,shards=a.shards,gpu=a.gpu,sources=len(rows),tasks=len(tasks),instrument=checks,dependencies={n:sha(Path(__file__).with_name(n)) for n in ['run_correct_prefix_binding.py','shared_source_cross_use.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for t in tasks:
            old=base[t['row']['item_id'],'NATIVE'];assert old['prompt_sha256']==digest(t['prompt']);lp,_,counts=forward(model,decoder,t,tok.pad_token_id,cut=True);m=max(lp);den=m+math.log(sum(math.exp(x-m) for x in lp))
            f.write(json.dumps(dict(item_id=t['row']['item_id'],operation='CUT_SOURCE_LATE',candidate_logprobs=lp,p_correct=math.exp(lp[0]-den),correct=lp[0]>lp[1],margin=lp[0]-lp[1],prompt_sha256=digest(t['prompt']),removed_edges_per_layer=counts))+'\n');f.flush()
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E79 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
