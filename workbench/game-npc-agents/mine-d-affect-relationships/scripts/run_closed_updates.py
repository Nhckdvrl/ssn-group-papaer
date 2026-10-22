#!/usr/bin/env python3
"""Long-lived single-GPU updater across eight real appearance waves."""
import argparse,json,hashlib,time,datetime,os,subprocess,copy,importlib.util
from pathlib import Path

REV='9216db5781bf21249d130ec9da846c4624c16137'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def load_native(root):
 spec=importlib.util.spec_from_file_location('closed_native_utils',root/'vendor/EvolvingWorld/simulation/utils.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def input_state(user):
 from index_update_provenance import section
 return dict(profile=section(user,'Current Profile (State At Scene Start)','Hidden Tracker (State At Scene Start)'),hidden_tracker=section(user,'Hidden Tracker (State At Scene Start)','Current Motivation (State At Scene Start)'),short_description='')
def substitute(user,state):
 a='## Current Profile (State At Scene Start)\n';b='\n\n## Hidden Tracker (State At Scene Start)\n';c='\n\n## Current Motivation (State At Scene Start)\n';prefix,tail=user.split(a,1);oldp,tail=tail.split(b,1);oldh,suffix=tail.split(c,1);v=state['hidden_tracker'];text=str(v) if v else '(Empty)'
 return prefix+a+state['profile']+b+text+c+suffix

def decode_state(text,before,native):
 try:
  o=native.extract_json_fragment(text);flag=o.get('profile_updated');p=o.get('updated_profile');p=native.dict_to_markdown_text(p) if isinstance(p,(dict,list)) else p
  valid=type(flag) is bool and ((flag and isinstance(p,str) and bool(p.strip())) or (not flag and 'updated_profile' in o and p is None)) and 'hidden_tracker' in o and (o['hidden_tracker'] is None or isinstance(o['hidden_tracker'],(str,dict,list))) and isinstance(o.get('short_description'),str) and bool(o['short_description'].strip())
  if not valid:return None
  return dict(profile=p if flag else before['profile'],hidden_tracker=o['hidden_tracker'],short_description=o['short_description'])
 except Exception:return None

SUMMARY_SYSTEM='''You maintain the current state of the character {role} for subsequent roleplay. Using only the supplied prior state and current scene, rewrite one concise, complete current character state. Preserve stable identity and still-relevant background, and capture current beliefs, goals, relationships, and unresolved experiences. Distinguish this character's own actions and knowledge from other people's. Record what remains true at the end of the scene. Do not use outside story knowledge. Keep updated_profile and hidden_tracker together under 900 words.
Return only a JSON object with four fields: profile_updated (always true because this is a complete state rewrite, regardless of the amount of change), updated_profile (the complete current state as one plain-text string), hidden_tracker (supporting unresolved experiences as a string or null), short_description (a concise third-person end-of-scene description). No markdown or explanation.'''
IDENTITY="Keep every update about the specified target character ({role}); distinguish that character's own actions, experiences, relations, and knowledge from those of every other person in the scene."

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--mode',choices=['teacher_forced','recursive_native','recursive_summary'],required=True);args=a.parse_args();root=Path(args.asset_root);taskfile=root/'data/closed_D-E06/trajectories.jsonl';trajectories=[json.loads(l) for l in taskfile.read_text().splitlines()];out=root/'runs/D-E06'/args.mode;out.mkdir(parents=True,exist_ok=True);assert not (out/'metadata.json').exists();native=load_native(root);meta=dict(started_utc=now(),complete=False,experiment='D-E06',kind='state_update',mode=args.mode,model='Qwen/Qwen3-32B',revision=REV,task_sha256=hashlib.sha256(taskfile.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),max_tokens=4096,recovery_max_tokens=8192,context_limit=32768,temperature=0,seed=0,thinking=False,n_trajectories=len(trajectories));start=time.monotonic();states={t['trajectory_id']:copy.deepcopy(t['initial_state']) for t in trajectories};n_attempts=0;failures=[]
 def save():(out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
 try:
  import torch,transformers
  from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
  set_seed(0);torch.set_num_threads(8);tok=AutoTokenizer.from_pretrained(root/'models/Qwen3-32B',local_files_only=True);tok.padding_side='left';model=AutoModelForCausalLM.from_pretrained(root/'models/Qwen3-32B',local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':0}).eval();eos=model.generation_config.eos_token_id;eos=set(eos if isinstance(eos,list) else [eos]);meta.update(torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0));save()
  with (out/'responses.jsonl').open('w') as rawfile,(out/'states.jsonl').open('w') as statefile:
   def infer(specs,cap,attempt):
    nonlocal n_attempts
    answer={};position=0
    while position<len(specs):
     remaining=specs[position:];batch=min(4,len(remaining));prepared=[]
     for spec in remaining[:batch]:
      prompt=tok.apply_chat_template(spec['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False);ids=tok.encode(prompt,add_special_tokens=False);prepared.append((spec,prompt,len(ids)))
     while batch>1 and max(x[2] for x in prepared[:batch])+cap>40000//batch:batch-=1
     prepared=prepared[:batch]
     if max(x[2] for x in prepared)+cap>32768:
      if attempt==1:raise RuntimeError('Complete recursive input exceeds registered context; do not truncate')
      for spec,_,_ in prepared:answer[spec['task_id']]=None;failures.append(dict(task_id=spec['task_id'],reason='Recovery could not fit complete context'))
      position+=batch;continue
     enc=tok([x[1] for x in prepared],padding=True,add_special_tokens=False,return_tensors='pt').to(model.device);begin=time.monotonic();started=now()
     with torch.inference_mode():gen=model.generate(**enc,do_sample=False,temperature=None,top_p=None,top_k=None,max_new_tokens=cap,pad_token_id=tok.pad_token_id)
     torch.cuda.synchronize();wall=time.monotonic()-begin
     for j,(spec,_,_) in enumerate(prepared):
      ids=gen[j,enc.input_ids.shape[1]:].tolist();end=next((i+1 for i,x in enumerate(ids) if x in eos),len(ids));ids=ids[:end];raw=tok.decode(ids,skip_special_tokens=True);text=raw.split('</think>',1)[-1].strip() if '</think>' in raw else raw.strip();after=decode_state(text,spec['state_before'],native);r=dict(spec,model='Qwen/Qwen3-32B',model_revision=REV,attempt=attempt,max_tokens=cap,batch_size=batch,batch_started_utc=started,batch_wall_s=wall,response=text,raw=raw,generated_token_ids=ids,usage=dict(prompt_tokens=int(enc.attention_mask[j].sum()),completion_tokens=len(ids)),finish_reason='stop' if ids and ids[-1] in eos else 'length',complete_state=after is not None,state_after=after);rawfile.write(json.dumps(r,ensure_ascii=False)+'\n');answer[spec['task_id']]=r;n_attempts+=1
     rawfile.flush();os.fsync(rawfile.fileno());position+=batch;print(args.mode,'attempt',attempt,'wave batch',position,'/',len(specs),'wall',round(wall,2),flush=True)
    return answer
   for step in range(8):
    specs=[]
    for t in trajectories:
     update=t['updates'][step];before=input_state(update['messages'][1]['content']) if args.mode=='teacher_forced' else states[t['trajectory_id']];messages=copy.deepcopy(update['messages'])
     if args.mode!='teacher_forced':messages[1]['content']=substitute(messages[1]['content'],before)
     messages[0]['content']=SUMMARY_SYSTEM.format(role=t['role']) if args.mode=='recursive_summary' else messages[0]['content']+'\n\n'+IDENTITY.format(role=t['role'])
     specs.append(dict(task_id=t['trajectory_id']+'/'+args.mode+'/step'+str(step+1),trajectory_id=t['trajectory_id'],book_name=t['book_name'],role=t['role'],step=step+1,scene_index=update['details']['scene_index'],mode=args.mode,messages=messages,state_before=copy.deepcopy(before),state_before_sha256=sha(before)))
    first=infer(specs,4096,1);missing=[s for s in specs if first[s['task_id']]['state_after'] is None];recovered=infer(missing,8192,2) if missing else {}
    for spec in specs:
     tid=spec['task_id'];row=first[tid]
     if row['state_after'] is None and recovered.get(tid) is not None and recovered[tid]['state_after'] is not None:row=recovered[tid]
     final=row['state_after'] if row['state_after'] is not None else spec['state_before'];states[spec['trajectory_id']]=copy.deepcopy(final);v={k:spec[k] for k in ['task_id','trajectory_id','book_name','role','step','scene_index','mode','state_before_sha256']};v.update(state=final,state_sha256=sha(final),selected_attempt=row['attempt'],selected_response_sha256=hashlib.sha256(row['response'].encode()).hexdigest(),complete_state=row['state_after'] is not None,carried_previous_after_invalid=row['state_after'] is None);statefile.write(json.dumps(v,ensure_ascii=False)+'\n')
     if row['state_after'] is None:failures.append(dict(task_id=tid,reason='All registered format attempts incomplete; previous state explicitly carried'))
    statefile.flush();os.fsync(statefile.fileno());meta.update(waves_completed=step+1,n_attempts=n_attempts,failures=failures);save();print('WAVE COMPLETE',args.mode,step+1,flush=True)
  meta.update(complete=True,n_responses=n_attempts,n_states=8*len(trajectories),peak_allocated_bytes=torch.cuda.max_memory_allocated())
 finally:meta.update(finished_utc=now(),wall_s=time.monotonic()-start,n_attempts=n_attempts,failures=failures);save()
if __name__=='__main__':main()
