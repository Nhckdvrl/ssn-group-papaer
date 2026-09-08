"""Read frozen prompts, record raw two-label likelihoods, no output-dependent tuning."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for key,sub in [('XDG_CACHE_HOME','xdg'),('TRITON_CACHE_DIR','triton'),('TORCH_HOME','torch'),('CUDA_CACHE_PATH','cuda'),('MPLCONFIGDIR','mpl')]:os.environ[key]=str(ROOT/'.cache'/sub)
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
import argparse,json,hashlib,time,datetime,shutil,sys,importlib.metadata

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--run-id',required=True);p.add_argument('--batch-size',type=int,default=2);a=p.parse_args()
    src=ROOT/'experiments/E001a_interpretation';proto=json.loads((src/'protocol.json').read_text());spec=proto['models'][a.model]
    for name,d in proto['artifact_hashes'].items():assert sha(src/name)==d
    out=ROOT/'runs'/a.run_id;out.mkdir(exist_ok=False)
    for name in ('protocol.json','samples.jsonl','jobs.jsonl'):shutil.copyfile(src/name,out/name)
    shutil.copyfile(__file__,out/Path(__file__).name)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(8);torch.manual_seed(20260908)
    tok=AutoTokenizer.from_pretrained(spec['path'],local_files_only=True,**({'fix_mistral_regex':True} if a.model=='mistral24b' else {}));tok.padding_side='left'
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tids={s:tok.encode(s,add_special_tokens=False) for s in ('A','B')};assert all(len(v)==1 for v in tids.values()),tids
    jobs=[json.loads(l) for l in (src/'jobs.jsonl').read_text().splitlines()]
    for j in jobs:
        kwargs={'enable_thinking':False} if a.model=='qwen32b' else {}
        j['rendered']=tok.apply_chat_template([{'role':'user','content':j['prompt']}],tokenize=False,add_generation_prompt=True,**kwargs)
    (out/'rendered_prompts.jsonl').write_text(''.join(json.dumps({'job_id':j['job_id'],'text':j['rendered']},ensure_ascii=False)+'\n' for j in jobs))
    meta={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':a.model,'spec':spec,'python':sys.executable,'cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),'gpu':torch.cuda.get_device_name(0),'versions':{n:importlib.metadata.version(n) for n in ('torch','transformers','accelerate','tokenizers')},'label_token_ids':tids,'batch_size':a.batch_size,'protocol_sha256':sha(src/'protocol.json'),'script_sha256':sha(Path(__file__))}
    meta['model_files']=[{'name':f.name,'bytes':f.stat().st_size,'resolved_blob':f.resolve().name} for f in sorted(Path(spec['path']).iterdir()) if f.is_file()]
    (out/'environment.json').write_text(json.dumps(meta,indent=2)+'\n')
    start=time.monotonic();print('Loading',a.model,flush=True)
    model=AutoModelForCausalLM.from_pretrained(spec['path'],local_files_only=True,torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},attn_implementation='sdpa');model.eval()
    meta['load_seconds']=time.monotonic()-start
    context_limit=model.config.max_position_embeddings
    # Sort by context length for efficient batching; item-level likelihoods never depend on other outputs.
    jobs.sort(key=lambda j:(len(j['rendered']),j['job_id']))
    with (out/'predictions.jsonl').open('x') as f:
        for i in range(0,len(jobs),a.batch_size):
            batch=jobs[i:i+a.batch_size];enc=tok([j['rendered'] for j in batch],return_tensors='pt',padding=True,truncation=False,add_special_tokens=False)
            assert enc.input_ids.shape[1]<=context_limit,(enc.input_ids.shape,context_limit)
            lengths=enc.attention_mask.sum(-1).tolist();enc=enc.to('cuda:0');torch.cuda.synchronize();t=time.monotonic()
            with torch.inference_mode():
                logits=model(**enc,use_cache=False,logits_to_keep=1).logits[:,-1,:].float()
                lp=torch.log_softmax(logits,-1);vals=lp[:,[tids['A'][0],tids['B'][0]]].cpu().tolist();tops=logits.argmax(-1).cpu().tolist()
            torch.cuda.synchronize();elapsed=time.monotonic()-t
            for j,n,v,top in zip(batch,lengths,vals,tops):
                rec={k:j[k] for k in ('job_id','sample_id','condition','order','a_label','b_label')};rec.update(input_tokens=n,logp_A=v[0],logp_B=v[1],top_token_id=top,top_token=tok.decode([top]),batch_seconds=elapsed,batch_start=i)
                f.write(json.dumps(rec)+'\n')
            f.flush();print(f'{a.model} {i+len(batch)}/{len(jobs)} tokens={max(lengths)} batch_s={elapsed:.2f}',flush=True)
            del logits,lp,enc
    meta.update(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),total_seconds=time.monotonic()-start,peak_memory_allocated_bytes=torch.cuda.max_memory_allocated(),output_sha256=sha(out/'predictions.jsonl'))
    (out/'completion.json').write_text(json.dumps(meta,indent=2)+'\n');print('COMPLETE',a.run_id,flush=True)
if __name__=='__main__':main()
