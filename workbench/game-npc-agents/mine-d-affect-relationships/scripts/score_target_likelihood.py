#!/usr/bin/env python3
"""Secondary native-reference predictive log score, no generation or judge calls."""
import argparse,json,hashlib,time,datetime,os,subprocess
from pathlib import Path
from collections import defaultdict
from statistics import mean
from queue_local_judges import wait_done

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);a.add_argument('--wait-after');args=a.parse_args();root=Path(args.asset_root)
 if args.wait_after:wait_done(Path(args.wait_after))
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True);assert not (out/'metadata.json').exists()
 meta=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),complete=False,model='Qwen/Qwen2.5-7B-Instruct',revision='a09a35458c702b33eeacc393d103063234e8bc28',operation='teacher-forced conditional log likelihood of native target content tokens; no EOS, no generation',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip());start=time.monotonic()
 def save():(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
 try:
  import torch,transformers
  from transformers import AutoTokenizer,AutoModelForCausalLM
  torch.set_num_threads(8);torch.manual_seed(0);checkpoint='/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/snapshots/a09a35458c702b33eeacc393d103063234e8bc28'
  tok=AutoTokenizer.from_pretrained(checkpoint,local_files_only=True);model=AutoModelForCausalLM.from_pretrained(checkpoint,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':0}).eval();meta.update(torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0))
  read=lambda p:[json.loads(l) for l in p.read_text().splitlines()]
  tasks=read(root/'data/phase_D-E02/tasks.jsonl');refs={r['question_id']:r for r in read(root/'data/phase_D-E02/references.jsonl')};scores=[];target_enc={}
  assert len(tasks)==256 and len(refs)==64
  with (out/'scores.jsonl').open('w') as f:
   for i,r in enumerate(tasks):
    target=refs[r['question_id']]['sample']['output'];prefix=tok.apply_chat_template(r['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False);before=tok.encode(prefix,add_special_tokens=False);full=tok.encode(prefix+target,add_special_tokens=False);assert full[:len(before)]==before,'Ambiguous token boundary';ids=full[len(before):];assert ids and len(full)<=16384
    if r['question_id'] in target_enc:assert ids==target_enc[r['question_id']]
    target_enc[r['question_id']]=ids;x=torch.tensor([full],device=model.device);labels=x.clone();labels[:,:len(before)]=-100
    with torch.inference_mode():loss=model(input_ids=x,labels=labels,use_cache=False).loss.float().item()
    v={k:r[k] for k in ['task_id','question_id','corpus','split','role','mode']};v.update(mean_target_nll=loss,n_target_tokens=len(ids),n_prompt_tokens=len(before),target_sha256=hashlib.sha256(target.encode()).hexdigest());scores.append(v);f.write(json.dumps(v,ensure_ascii=False)+'\n');f.flush()
    if (i+1)%16==0:print(f'{i+1}/256',flush=True)
  bucket=defaultdict(lambda:defaultdict(list))
  for r in scores:bucket[r['mode']][r['corpus']].append(r['mean_target_nll'])
  by={m:{c:mean(v) for c,v in cs.items()} for m,cs in bucket.items()};summary=dict(operation=meta['operation'],n=len(scores),by_corpus=by,corpus_macro={m:mean(v.values()) for m,v in by.items()},details=scores,interpretation='Post-hoc reference predictability, not unique valid continuation accuracy; no causal claim for state structure vs extra information.')
  (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n');meta.update(complete=True,n_instances=len(scores),target_token_boundary_exact=True)
 finally:meta.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_s=time.monotonic()-start);save()
if __name__=='__main__':main()
