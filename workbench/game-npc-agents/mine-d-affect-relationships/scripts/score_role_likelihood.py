#!/usr/bin/env python3
"""Conditional source-turn loss, separating native inner thoughts from visible text."""
import argparse,json,hashlib,datetime,time,subprocess
from pathlib import Path

def character_regions(text):
 depth=0;inside=[];valid=True
 for char in text:
  if char=='[':depth+=1;inside.append(True)
  elif char==']':inside.append(depth>0);depth-=1;valid=valid and depth>=0
  else:inside.append(depth>0)
 return inside,valid and depth==0

def main():
 a=argparse.ArgumentParser();a.add_argument('--tasks',required=True);a.add_argument('--references',required=True);a.add_argument('--checkpoint',required=True);a.add_argument('--revision',required=True);a.add_argument('--model',required=True);a.add_argument('--out',required=True);args=a.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True);assert not (out/'metadata.json').exists();tasks=[json.loads(l) for l in Path(args.tasks).read_text().splitlines()];refs={r['question_id']:r for r in map(json.loads,Path(args.references).read_text().splitlines())};meta=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),complete=False,operation='Source next-turn conditional likelihood; all tokens primary, visible and inner-thought components fixed before computation; no new generation',model=args.model,revision=args.revision,args=vars(args),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),task_sha256=hashlib.sha256(Path(args.tasks).read_bytes()).hexdigest(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=Path(__file__).resolve().parents[4],text=True).strip());start=time.monotonic()
 def save():(out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
 try:
  import torch,transformers
  import torch.nn.functional as F
  from transformers import AutoTokenizer,AutoModelForCausalLM
  from cache_local_weights import resolve_local_checkpoint
  resolved,mirror=resolve_local_checkpoint(args.checkpoint);meta['resolved_checkpoint']=resolved
  if mirror:meta['local_weight_mirror']=mirror
  helper=Path(__file__).with_name('cache_local_weights.py');meta['weight_cache_helper_sha256']=hashlib.sha256(helper.read_bytes()).hexdigest();(out/'cache_local_weights.py').write_bytes(helper.read_bytes())
  torch.set_num_threads(8);torch.manual_seed(0);tok=AutoTokenizer.from_pretrained(resolved,local_files_only=True);load_start=time.monotonic();model=AutoModelForCausalLM.from_pretrained(resolved,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':0}).eval();meta.update(torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0),model_load_wall_s=time.monotonic()-load_start);save();target_ids={}
  with (out/'scores.jsonl').open('w') as f:
   for i,r in enumerate(tasks):
    target=refs[r['question_id']]['target'];prefix=tok.apply_chat_template(r['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False);before=tok.encode(prefix,add_special_tokens=False);encoded=tok(prefix+target,add_special_tokens=False,return_offsets_mapping=True);full=encoded['input_ids'];assert full[:len(before)]==before;ids=full[len(before):];assert ids and len(full)<=32768
    if r['question_id'] in target_ids:assert target_ids[r['question_id']]==ids
    target_ids[r['question_id']]=ids;x=torch.tensor([full],device=model.device);y=torch.tensor(ids,device=model.device)
    with torch.inference_mode():
     pred=model(input_ids=x,use_cache=False,logits_to_keep=len(ids)+1).logits;assert pred.shape[1]==len(ids)+1;losses=F.cross_entropy(pred[0,:-1].float(),y,reduction='none');value=losses.mean().item()
     if i==0:
      labels=x.clone();labels[:,:len(before)]=-100;reference=model(input_ids=x,labels=labels,use_cache=False).loss.float().item();delta=abs(value-reference);assert delta<0.001,('Target-logit alignment mismatch',value,reference);meta['one_forward_alignment_validation']=dict(absolute_difference=delta,extra_forward_calls=1,reference_masked_ce=reference,selective_logits_ce=value)
    flags,balanced=character_regions(target);visible=[];thought=[]
    for j,(a0,b0) in enumerate(encoded['offset_mapping'][len(before):]):
     a0-=len(prefix);b0-=len(prefix);assert 0<=a0<=b0<=len(target);chars=[k for k in range(a0,b0) if not target[k].isspace()]
     if balanced and chars and all(not flags[k] for k in chars):visible.append(j)
     elif balanced and chars and all(flags[k] for k in chars):thought.append(j)
    details={k:r[k] for k in ['task_id','question_id','trajectory_id','book_name','role','after_updates','condition']};details.update(mean_target_nll=value,visible_target_nll=losses[visible].mean().item() if visible else None,thought_target_nll=losses[thought].mean().item() if thought else None,n_target_tokens=len(ids),n_visible_tokens=len(visible),n_thought_tokens=len(thought),n_prompt_tokens=len(before),square_brackets_balanced=balanced,target_sha256=hashlib.sha256(target.encode()).hexdigest());f.write(json.dumps(details,ensure_ascii=False)+'\n');f.flush()
    if (i+1)%8==0:print(i+1,'/',len(tasks),'NLL',flush=True)
  meta.update(complete=True,n_instances=len(tasks),target_token_boundary_exact=True,peak_allocated_bytes=torch.cuda.max_memory_allocated())
 finally:meta.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_s=time.monotonic()-start);save()
if __name__=='__main__':main()
