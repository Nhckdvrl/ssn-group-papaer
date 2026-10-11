"""Run frozen E001b prompts and retain complete raw generated labels."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for key,sub in [('XDG_CACHE_HOME','xdg'),('TRITON_CACHE_DIR','triton'),('TORCH_HOME','torch'),('CUDA_CACHE_PATH','cuda'),('MPLCONFIGDIR','mpl')]:os.environ[key]=str(ROOT/'.cache'/sub)
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
import argparse,datetime,hashlib,json,shutil,sys,time,importlib.metadata
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--run-id',required=True);a=p.parse_args()
    src=ROOT/'experiments/E001b_native_labels';proto=json.loads((src/'protocol.json').read_text());spec=proto['models'][a.model]
    for name,h in proto['artifact_hashes'].items():assert sha(src/name)==h
    out=ROOT/'runs'/a.run_id;out.mkdir(exist_ok=False)
    for name in ('protocol.json','jobs.jsonl','samples.jsonl'):shutil.copyfile(src/name,out/name)
    shutil.copyfile(__file__,out/Path(__file__).name)
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(8);torch.manual_seed(20260908)
    tok=AutoTokenizer.from_pretrained(spec['path'],local_files_only=True,**({'fix_mistral_regex':True} if a.model=='mistral24b' else {}));tok.padding_side='left'
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    jobs=[json.loads(l) for l in (src/'jobs.jsonl').read_text().splitlines()]
    for j in jobs:j['rendered']=tok.apply_chat_template([{'role':'user','content':j['prompt']}],tokenize=False,add_generation_prompt=True,**({'enable_thinking':False} if a.model=='qwen32b' else {}))
    (out/'rendered_prompts.jsonl').write_text(''.join(json.dumps({'job_id':j['job_id'],'text':j['rendered']})+'\n' for j in jobs))
    meta={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':a.model,'spec':spec,'python':sys.executable,'cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),'gpu':torch.cuda.get_device_name(0),'versions':{n:importlib.metadata.version(n) for n in ('torch','transformers','accelerate','tokenizers')},'protocol_sha256':sha(src/'protocol.json'),'script_sha256':sha(Path(__file__))}
    (out/'environment.json').write_text(json.dumps(meta,indent=2)+'\n')
    start=time.monotonic();print('Loading',a.model,flush=True)
    model=AutoModelForCausalLM.from_pretrained(spec['path'],local_files_only=True,torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},attn_implementation='sdpa');model.eval()
    meta['load_seconds']=time.monotonic()-start
    jobs.sort(key=lambda j:(len(j['rendered']),j['job_id']))
    with (out/'predictions.jsonl').open('x') as f:
        for i in range(0,len(jobs),2):
            batch=jobs[i:i+2];enc=tok([j['rendered'] for j in batch],return_tensors='pt',padding=True,truncation=False,add_special_tokens=False)
            assert enc.input_ids.shape[1]+8<=model.config.max_position_embeddings
            lens=enc.attention_mask.sum(-1).tolist();enc=enc.to('cuda:0');torch.cuda.synchronize();t=time.monotonic()
            with torch.inference_mode():ids=model.generate(**enc,max_new_tokens=8,do_sample=False,pad_token_id=tok.pad_token_id)
            torch.cuda.synchronize();elapsed=time.monotonic()-t
            generated=ids[:,enc.input_ids.shape[1]:].cpu().tolist()
            for j,n,ts in zip(batch,lens,generated):
                raw=tok.decode(ts,skip_special_tokens=True);s=raw.strip();pred=s if s in ('DNI','INI') else None
                f.write(json.dumps({'job_id':j['job_id'],'sample_id':j['sample_id'],'condition':j['condition'],'input_tokens':n,'generated_token_ids':ts,'raw_response':raw,'prediction':pred,'batch_seconds':elapsed})+'\n')
            f.flush();print(f'{a.model} {i+len(batch)}/{len(jobs)} batch_s={elapsed:.2f}',flush=True)
    meta.update(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),total_seconds=time.monotonic()-start,peak_memory_allocated_bytes=torch.cuda.max_memory_allocated(),output_sha256=sha(out/'predictions.jsonl'))
    (out/'completion.json').write_text(json.dumps(meta,indent=2)+'\n');print('COMPLETE',a.run_id,flush=True)
