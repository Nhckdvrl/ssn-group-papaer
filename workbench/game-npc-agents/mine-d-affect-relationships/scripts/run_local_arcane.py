#!/usr/bin/env python3
"""Local HF execution of unmodified native ArcANE rendered messages."""
import argparse,json,time,hashlib,sys,subprocess,datetime,os
from pathlib import Path


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def rows(path):return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def main():
 a=argparse.ArgumentParser();a.add_argument('--arcane',required=True);a.add_argument('--tasks',required=True);a.add_argument('--checkpoint',required=True);a.add_argument('--revision',required=True);a.add_argument('--model',required=True);a.add_argument('--out',required=True);a.add_argument('--batch-size',type=int,default=4);a.add_argument('--max-tokens',type=int,default=8192);args=a.parse_args()
 tasks=rows(args.tasks);assert len({t['task_id'] for t in tasks})==len(tasks)
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 if (out/'metadata.json').exists():raise FileExistsError(out)
 sys.path.insert(0,str(Path(args.arcane)))
 from inference.loaders import Trial
 from inference.runner import _row,_build_full_trial_id
 from inference._api import strip_think_block
 meta=dict(started_utc=stamp(),args=vars(args),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),arcane_commit=subprocess.check_output(['git','-C',args.arcane,'rev-parse','HEAD'],text=True).strip(),script_sha256=sha(__file__),tasks_sha256=sha(args.tasks),complete=False,seed=0,decoding='greedy; explicit controlled choice, original API wrapper leaves temperature unspecified')
 dump(out/'metadata.json',meta);(out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
 start=time.monotonic()
 try:
  import torch,transformers
  from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
  set_seed(0);torch.set_num_threads(8)
  tok=AutoTokenizer.from_pretrained(args.checkpoint,local_files_only=True);tok.padding_side='left'
  if tok.pad_token_id is None:tok.pad_token_id=tok.eos_token_id
  model=AutoModelForCausalLM.from_pretrained(args.checkpoint,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':0}).eval()
  meta.update(torch=torch.__version__,transformers=transformers.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),generation_config=model.generation_config.to_dict(),tokenizer_template_sha256=hashlib.sha256(str(tok.chat_template).encode()).hexdigest(),checkpoint_files=[dict(name=p.name,size=p.stat().st_size,blob=p.resolve().name) for p in Path(args.checkpoint).glob('*') if p.is_file()]);dump(out/'metadata.json',meta)
  seen=set()
  with (out/'responses.jsonl').open('a') as f:
   for offset in range(0,len(tasks),args.batch_size):
    block=tasks[offset:offset+args.batch_size];assert all(t['task_id'] not in seen for t in block)
    prompts=[tok.apply_chat_template(t['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False) for t in block]
    enc=tok(prompts,padding=True,add_special_tokens=False,return_tensors='pt').to(model.device)
    if enc.input_ids.shape[1]+args.max_tokens>model.config.max_position_embeddings:raise ValueError('context overflow; do not silently truncate')
    bstart=time.monotonic();started=stamp()
    with torch.inference_mode():generated=model.generate(**enc,do_sample=False,max_new_tokens=args.max_tokens,pad_token_id=tok.pad_token_id,temperature=None,top_p=None,top_k=None)
    torch.cuda.synchronize();elapsed=time.monotonic()-bstart
    eos=model.generation_config.eos_token_id;eos=set(eos if isinstance(eos,list) else [eos])
    for j,t in enumerate(block):
     ids=generated[j,enc.input_ids.shape[1]:].tolist();token_end=next((i+1 for i,x in enumerate(ids) if x in eos),len(ids));ids=ids[:token_end]
     raw=tok.decode(ids,skip_special_tokens=True);text=strip_think_block(raw)
     trial=Trial(**t['trial']);system,user=t['messages'][0]['content'],t['messages'][1]['content']
     usage=dict(prompt_tokens=int(enc.attention_mask[j].sum()),completion_tokens=len(ids))
     rec=_row(trial,t['mode'],args.model,_build_full_trial_id(trial,t['mode'],args.model),system,user,hashlib.sha1((system+'\n---\n'+user).encode()).hexdigest()[:16],len(system),text,usage,int(1000*elapsed/len(block)),None,error=None,record_prompts=True)
     rec.update(task_id=t['task_id'],model_revision=args.revision,raw=raw,generated_token_ids=ids,finish_reason='stop' if ids and ids[-1] in eos else 'length',batch_started_utc=started,batch_wall_s=elapsed,batch_size=len(block))
     f.write(json.dumps(rec,ensure_ascii=False)+'\n');seen.add(t['task_id'])
    f.flush();os.fsync(f.fileno());print(f'{offset+len(block)}/{len(tasks)} prompt_pad={enc.input_ids.shape[1]} batch_s={elapsed:.2f}',flush=True)
  assert len(seen)==len(tasks);meta.update(complete=True,n_responses=len(seen),peak_allocated_bytes=torch.cuda.max_memory_allocated())
 finally:
  meta.update(finished_utc=stamp(),wall_s=time.monotonic()-start);dump(out/'metadata.json',meta)

if __name__=='__main__':main()
