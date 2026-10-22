#!/usr/bin/env python3
"""Ordinary rolling character profiles over frozen complete source prefixes."""
import argparse,datetime,hashlib,json,os,subprocess,time
from pathlib import Path

SYSTEM='''You maintain a current character profile for roleplay by reading a narrative in chronological order. Update the previous profile using only the new source passage. Preserve still-supported identity and earlier experiences; revise them when the new evidence changes them. Organize current beliefs, goals, relationships, characteristic ways of responding, and stable identity. Distinguish this character's experiences from other people's, and distinguish a narrator's facts from what the character knows or believes. Preserve uncertainty when evidence is insufficient. If the passage adds no relevant evidence about the character, retain the previous information; absence of mention does not erase it. Do not add outside knowledge, later plot, predictions, or answers to hypothetical questions. Return the complete current profile in plain text, at most 500 words.'''
REV='9216db5781bf21249d130ec9da846c4624c16137'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--shard',type=int,choices=[0,1],required=True);args=a.parse_args();root=Path(args.asset_root);path=root/'data/prefix_D-E09/chains.jsonl';chains=[r for r in map(json.loads,path.read_text().splitlines()) if r['shard']==args.shard];out=root/'runs/D-E09'/('memory_shard'+str(args.shard));out.mkdir(exist_ok=True,parents=True);assert not (out/'metadata.json').exists();assert chains
 meta=dict(experiment='D-E09',kind='character_state_summary_teacher',started_utc=now(),complete=False,shard=args.shard,model='Qwen/Qwen3-32B',revision=REV,task_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),script_sha256=sha(Path(__file__).read_text()),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),temperature=0,thinking=False,seed=0,max_tokens=2048,recovery_max_tokens=8192,context_limit=32768,max_batch_size=3,max_start_batch_wall_s=16200,n_chains=len(chains),n_blocks=sum(len(c['blocks']) for c in chains));start=time.monotonic();attempts=0;states_count=0;failures=[]
 def save():(out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
 try:
  import torch,transformers
  from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
  set_seed(0);torch.set_num_threads(8);tok=AutoTokenizer.from_pretrained(root/'models/Qwen3-32B',local_files_only=True);tok.padding_side='left';model=AutoModelForCausalLM.from_pretrained(root/'models/Qwen3-32B',local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':0}).eval();eos=model.generation_config.eos_token_id;eos=set(eos if isinstance(eos,list) else [eos]);meta.update(torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0));save();profiles={c['chain_id']:'No narrative evidence about this character has yet been processed.' for c in chains};positions={c['chain_id']:0 for c in chains}
  with (out/'responses.jsonl').open('w') as f,(out/'states.jsonl').open('w') as sf:
   def infer(specs,cap,attempt):
    nonlocal attempts
    answer={};offset=0
    while offset<len(specs):
     if time.monotonic()-start>=16200:raise RuntimeError('Registered worker wall budget reached; preserve incomplete coverage')
     prepared=[]
     for spec in specs[offset:offset+3]:
      prompt=tok.apply_chat_template(spec['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False);prepared.append((spec,prompt,len(tok.encode(prompt,add_special_tokens=False))))
     batch=len(prepared)
     while batch>1 and max(x[2] for x in prepared[:batch])+cap>40000//batch:batch-=1
     prepared=prepared[:batch];assert max(x[2] for x in prepared)+cap<=32768,'Never truncate source or prior state'
     enc=tok([x[1] for x in prepared],padding=True,add_special_tokens=False,return_tensors='pt').to(model.device);begin=time.monotonic();started=now()
     with torch.inference_mode():gen=model.generate(**enc,do_sample=False,temperature=None,top_p=None,top_k=None,max_new_tokens=cap,pad_token_id=tok.pad_token_id)
     torch.cuda.synchronize();wall=time.monotonic()-begin
     for i,(spec,_,_) in enumerate(prepared):
      ids=gen[i,enc.input_ids.shape[1]:].tolist();end=next((j+1 for j,t in enumerate(ids) if t in eos),len(ids));ids=ids[:end];raw=tok.decode(ids,skip_special_tokens=True);text=raw.split('</think>',1)[-1].strip() if '</think>' in raw else raw.strip();finish='stop' if ids and ids[-1] in eos else 'length';r=dict(spec,attempt=attempt,max_tokens=cap,model='Qwen/Qwen3-32B',model_revision=REV,response=text,raw=raw,generated_token_ids=ids,finish_reason=finish,usable=finish=='stop' and bool(text),usage=dict(prompt_tokens=int(enc.attention_mask[i].sum()),completion_tokens=len(ids)),batch_size=batch,batch_started_utc=started,batch_wall_s=wall);f.write(json.dumps(r,ensure_ascii=False)+'\n');answer[spec['task_id']]=r;attempts+=1
     f.flush();os.fsync(f.fileno());offset+=batch
    return answer
   while any(positions[c['chain_id']]<len(c['blocks']) for c in chains):
    specs=[]
    for c in chains:
     pos=positions[c['chain_id']]
     if pos>=len(c['blocks']):continue
     block=c['blocks'][pos];prior=profiles[c['chain_id']];user=f"Book: {c['novel']}\nCharacter: {c['character']}\n\nPrevious character profile:\n{prior}\n\nNext source passage in narrative order:\n{block['passages']}";specs.append(dict(task_id=block['task_id'],chain_id=c['chain_id'],novel=c['novel'],character=c['character'],character_slug=c['character_slug'],step=block['step'],checkpoint=block['checkpoint'],completed_through_unit=block['completed_through_unit'],source_sha256=block['source_sha256'],prior_profile=prior,prior_profile_sha256=sha(prior),messages=[dict(role='system',content=SYSTEM),dict(role='user',content=user)]))
    initial=infer(specs,2048,1);missing=[s for s in specs if not initial[s['task_id']]['usable']];recovery=infer(missing,8192,2) if missing else {}
    for s in specs:
     r=initial[s['task_id']]
     if not r['usable'] and recovery[s['task_id']]['usable']:r=recovery[s['task_id']]
     current=r['response'] if r['usable'] else s['prior_profile'];profiles[s['chain_id']]=current;positions[s['chain_id']]+=1;state={k:s[k] for k in ['task_id','chain_id','novel','character','character_slug','step','checkpoint','completed_through_unit','source_sha256','prior_profile_sha256']};state.update(profile=current,profile_sha256=sha(current),selected_attempt=r['attempt'],selected_response_sha256=sha(r['response']),carried_previous_after_invalid=not r['usable']);sf.write(json.dumps(state,ensure_ascii=False)+'\n');states_count+=1
     if not r['usable']:failures.append(s['task_id'])
    sf.flush();os.fsync(sf.fileno());meta.update(n_attempts=attempts,n_states=states_count,positions=positions,failures=failures);save();print('prefix shard',args.shard,'states',states_count,'/',meta['n_blocks'],'attempts',attempts,flush=True)
  meta.update(complete=True,peak_allocated_bytes=torch.cuda.max_memory_allocated())
 finally:meta.update(finished_utc=now(),wall_s=time.monotonic()-start,n_attempts=attempts,n_states=states_count,failures=failures);save()
if __name__=='__main__':main()
