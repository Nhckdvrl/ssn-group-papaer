"""E80: reliability metadata before unchanged published Source and G2 QA."""
import argparse,fcntl,json,math,os,time
from pathlib import Path
from data import CACHE,sha
from data_v2 import digest
from goal_conditioned_reading import prepare as native_prepare
from shared_source_cross_use import source_info
from source_scope_map import single_token_scores
from reading_map import encode_choices

STATUS={'TRUST':'The sentence is grammatical exactly as printed.','NOISY':'The sentence may contain a missing or misplaced word.'}


def prepare(rows,tok,base):
    original=[t for t in native_prepare(rows,tok) if t['operation']=='NONE'];tasks=[];prefixes={}
    for t in original:
        r=t['row'];old=base[r['item_id'],'NONE',t['readout'],t['mapping']];assert old['prompt_sha256']==digest(t['prompt']) and old['candidate_gold']==t['candidate_gold']
        assert r['step5_annotation']['grammar']=='acceptable' and all(x['grammar']=='acceptable' for x in r['step5_passes'])
        for op,status in STATUS.items():
            marker='Read this sentence carefully.\nSentence:\n';assert t['prompt'].count(marker)==1
            prompt=t['prompt'].replace(marker,'Read this sentence carefully.\nInput status: '+status+'\nSentence:\n')
            q=dict(t,operation=op,prompt=prompt);q['encoded']=encode_choices(tok,q);assert all(len(s)==q['encoded'][1]+1 for s in q['encoded'][0])
            prefix,_=source_info(tok,q);key=r['source_unit'],op
            if key in prefixes:assert prefixes[key]==prefix
            prefixes[key]=prefix;tasks.append(q)
    return tasks,original


def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(80);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    allrows=list(map(json.loads,a.data.read_text().splitlines()));assert sha(a.data)==json.loads(a.data.with_suffix('.manifest.json').read_text())['data_sha256'];rows=[r for r in allrows if int(r['sentence_sha256'][:16],16)%a.shards==a.shard]
    d=a.parent/'runs-v1'/a.model.name;bcfg=json.loads((d/'config.json').read_text());assert bcfg['data_sha256']==sha(a.data) and bcfg['predictions_sha256']==sha(d/'predictions.jsonl') and bcfg['model_manifest_sha256']==sha(a.model/'manifest.json')
    base={(p['item_id'],p['operation'],p['readout'],p['mapping']):p for p in map(json.loads,(d/'predictions.jsonl').read_text().splitlines()) if p['operation']=='NONE'}
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tasks,original=prepare(rows,tok,base);cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval();fixed=min(r['source_unit'] for r in rows);checks=[]
    for t in [t for t in original if t['row']['source_unit']==fixed]:
        lp=single_token_scores(model,[t['encoded']],tok.pad_token_id)[0];old=base[t['row']['item_id'],'NONE',t['readout'],t['mapping']];delta=max(abs(x-y) for x,y in zip(lp,old['candidate_logprobs']));assert delta<.001
        checks.append(dict(item_id=t['row']['item_id'],readout=t['readout'],mapping=t['mapping'],parent_LP_max_delta=delta))
    a.out.mkdir(exist_ok=True,parents=True);assert not (a.out/'predictions.jsonl').exists();config=dict(data_sha256=sha(a.data),model_manifest_sha256=sha(a.model/'manifest.json'),code_sha256=sha(Path(__file__)),parent_predictions_sha256=bcfg['predictions_sha256'],dtype='float32',attention='eager',seed=80,shard=a.shard,shards=a.shards,gpu=a.gpu,QA=len(rows),tasks=len(tasks),status=STATUS,instrument=checks,source_bytes_unchanged=True,original_grammar_qualification_preserved=True,dependencies={n:sha(Path(__file__).with_name(n)) for n in ['goal_conditioned_reading.py','shared_source_cross_use.py','source_scope_map.py','reading_map.py']})
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');tasks.sort(key=lambda t:len(t['prompt']))
    with (a.out/'predictions.jsonl').open('w') as f:
        for begin in range(0,len(tasks),a.batch_size):
            batch=tasks[begin:begin+a.batch_size];scores=single_token_scores(model,[t['encoded'] for t in batch],tok.pad_token_id)
            for t,lp in zip(batch,scores):
                m=max(lp);den=m+math.log(sum(math.exp(x-m) for x in lp));r=t['row'];g=t['candidate_gold']
                f.write(json.dumps(dict(item_id=r['item_id'],source_unit=r['source_unit'],operation=t['operation'],readout=t['readout'],mapping=t['mapping'],candidate_gold=g,candidate_logprobs=lp,correct=max(range(2),key=lp.__getitem__)==g,p_correct=math.exp(lp[g]-den),prompt_sha256=digest(t['prompt']),prompt_tokens=t['encoded'][1]))+'\n')
            f.flush()
            if begin%512==0:print('E80',a.model.name,a.shard,begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600);(a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E80 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);p.add_argument('--batch-size',type=int,default=16);run(p.parse_args())
