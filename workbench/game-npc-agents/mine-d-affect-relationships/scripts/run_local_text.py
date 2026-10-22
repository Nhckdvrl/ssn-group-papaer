#!/usr/bin/env python3
"""Bounded local inference for frozen native PHASE-Tree actor/judge prompts."""
import argparse,json,hashlib,time,os,datetime,subprocess
from pathlib import Path

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 a=argparse.ArgumentParser();a.add_argument('--tasks',required=True);a.add_argument('--checkpoint',required=True);a.add_argument('--revision',required=True);a.add_argument('--model',required=True);a.add_argument('--out',required=True);a.add_argument('--max-tokens',type=int,required=True);a.add_argument('--temperature',type=float,default=0);a.add_argument('--seed',type=int,default=0);a.add_argument('--batch-size',type=int,default=4);a.add_argument('--context-limit',type=int,default=32768);a.add_argument('--adapter');a.add_argument('--max-seconds',type=float);args=a.parse_args()
 tasks=[json.loads(l) for l in Path(args.tasks).read_text().splitlines()];assert len(tasks)==len({t['task_id'] for t in tasks})
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 if (out/'metadata.json').exists():raise FileExistsError(out)
 meta=dict(started_utc=now(),args=vars(args),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),task_sha256=hashlib.sha256(Path(args.tasks).read_bytes()).hexdigest(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),complete=False)
 def save(): (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes());start=time.monotonic()
 try:
  import torch,transformers
  from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
  set_seed(args.seed);torch.set_num_threads(8)
  tok=AutoTokenizer.from_pretrained(args.checkpoint,local_files_only=True);tok.padding_side='left'
  if tok.pad_token_id is None:tok.pad_token_id=tok.eos_token_id
  model=AutoModelForCausalLM.from_pretrained(args.checkpoint,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':0}).eval()
  if args.adapter:
   from peft import PeftModel
   adapter=Path(args.adapter)
   meta['adapter_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in adapter.iterdir() if p.name in ['adapter_config.json','adapter_model.safetensors']}
   model=PeftModel.from_pretrained(model,str(adapter),is_trainable=False).eval()
  meta.update(torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0),cuda=torch.version.cuda,generation_config=model.generation_config.to_dict());save()
  eos=model.generation_config.eos_token_id;eos=set(eos if isinstance(eos,list) else [eos]);seen=set()
  with (out/'responses.jsonl').open('a') as f:
   for off in range(0,len(tasks),args.batch_size):
    if args.max_seconds is not None and time.monotonic()-start>=args.max_seconds:raise TimeoutError('Registered generation budget reached before next batch')
    block=tasks[off:off+args.batch_size];assert all(t['task_id'] not in seen for t in block)
    prompts=[tok.apply_chat_template(t['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False) for t in block]
    enc=tok(prompts,padding=True,add_special_tokens=False,return_tensors='pt').to(model.device)
    if enc.input_ids.shape[1]+args.max_tokens>min(args.context_limit,model.config.max_position_embeddings):raise ValueError('Would truncate native prompt; abort before generation')
    begin=time.monotonic();kwargs=dict(do_sample=args.temperature>0,max_new_tokens=args.max_tokens,pad_token_id=tok.pad_token_id)
    if args.temperature>0:kwargs['temperature']=args.temperature
    else:kwargs.update(temperature=None,top_p=None,top_k=None)
    with torch.inference_mode():gen=model.generate(**enc,**kwargs)
    torch.cuda.synchronize();elapsed=time.monotonic()-begin
    for j,t in enumerate(block):
     ids=gen[j,enc.input_ids.shape[1]:].tolist();end=next((i+1 for i,x in enumerate(ids) if x in eos),len(ids));ids=ids[:end];raw=tok.decode(ids,skip_special_tokens=True);text=raw.split('</think>',1)[-1].strip() if '</think>' in raw else raw.strip()
     r={k:v for k,v in t.items() if k!='messages'};r.update(model=args.model,model_revision=args.revision,response=text,raw=raw,usage=dict(prompt_tokens=int(enc.attention_mask[j].sum()),completion_tokens=len(ids)),finish_reason='stop' if ids and ids[-1] in eos else 'length',batch_wall_s=elapsed,batch_size=len(block),messages=t['messages'],generated_token_ids=ids)
     f.write(json.dumps(r,ensure_ascii=False)+'\n');seen.add(t['task_id'])
    f.flush();os.fsync(f.fileno());print(f'{off+len(block)}/{len(tasks)} prompt_pad={enc.input_ids.shape[1]} batch_s={elapsed:.2f}',flush=True)
  assert len(seen)==len(tasks);meta.update(complete=True,n_responses=len(seen),peak_allocated_bytes=torch.cuda.max_memory_allocated())
 finally:meta.update(finished_utc=now(),wall_s=time.monotonic()-start);save()
if __name__=='__main__':main()
