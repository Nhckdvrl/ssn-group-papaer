#!/usr/bin/env python3
"""Correct the source unit mapping, keep caches by exact inputs, then measure C."""
import argparse,json,subprocess,os,time
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);a.add_argument('--capacity-only',action='store_true');args=a.parse_args();root=Path(args.asset_root);scripts=Path(__file__).resolve().parent;project=Path(args.project);python='/home/xiang/miniconda3/envs/openslime/bin/python';env=dict(os.environ,CUDA_VISIBLE_DEVICES='1' if args.capacity_only else '3',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false');data=root/'data/arcane_D-E07_v2';q8='/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218';r8='b968826d9c46dd6066d109eabc6255188de91218';r32='9216db5781bf21249d130ec9da846c4624c16137'
 def run(argv,log):
  with (root/'logs'/log).open('w') as f:subprocess.run([python,'-u']+list(map(str,argv)),cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 def text(taskfile,name,cap,batch):run([scripts/'run_local_text.py','--tasks',taskfile,'--checkpoint',root/'models/Qwen3-32B','--revision',r32,'--model','Qwen/Qwen3-32B','--out',root/'runs/D-E07'/name,'--max-tokens',cap,'--batch-size',batch],'D-E07-'+name+'.log')
 def complete_text(taskfile,name,cap,recovery_cap):
  text(taskfile,name,cap,4);rows=[json.loads(l) for l in (root/'runs/D-E07'/name/'responses.jsonl').read_text().splitlines()];missing={r['task_id'] for r in rows if r['finish_reason']!='stop' or not r['response'].strip()}
  if missing:
   p=taskfile.with_name(name+'_recovery_tasks.jsonl');p.write_text(''.join(l+'\n' for l in taskfile.read_text().splitlines() if json.loads(l)['task_id'] in missing));text(p,name+'_recovery',recovery_cap,2)
 def actor(name,checkpoint,revision,model,batch):
  for suffix,tasks,location in [('',data/'tasks.jsonl',root/'runs/D-E07'/name),('_summary_repair',data/'summary_tasks_repaired.jsonl',root/'runs/D-E07/source_repair'/(name+'_summary'))]:run([scripts/'run_local_arcane.py','--arcane',root/'vendor/ArcANE','--tasks',tasks,'--checkpoint',checkpoint,'--revision',revision,'--model',model,'--out',location,'--max-tokens',8192,'--batch-size',batch],'D-E07-'+name+suffix+'.log')
 if args.capacity_only:
  wait_done(root/'runs/D-E06/recursive_native/metadata.json');time.sleep(3)
  while not (data/'READY.json').exists():time.sleep(5)
  actor('qwen3_32b',root/'models/Qwen3-32B',r32,'Qwen/Qwen3-32B',2);print('Corrected capacity actor complete',flush=True);return
 complete_text(data/'map_tasks.jsonl','source_repair_maps',512,1024);subprocess.run([python,str(scripts/'repair_arcane_source.py'),'reduce','--asset-root',str(root)],cwd=project,check=True)
 complete_text(data/'reduce_tasks.jsonl','source_repair_reduce',1024,4096);subprocess.run([python,str(scripts/'repair_arcane_source.py'),'compile','--asset-root',str(root)],cwd=project,check=True)
 complete_text(data/'compiler_remaining_tasks.jsonl','state_compiler_v2',2048,8192);subprocess.run([python,str(scripts/'repair_arcane_source.py'),'actors','--asset-root',str(root)],cwd=project,check=True)
 actor('qwen3_8b',q8,r8,'Qwen/Qwen3-8B',4);actor('arcane_8b_dpo',root/'models/ArcANE-8B-DPO','67b9bea604bea65a5245928ed87103545814b4f7','arcane-8B-dpo',4)
 wait_done(root/'runs/D-E07/qwen3_32b/metadata.json');wait_done(root/'runs/D-E07/source_repair/qwen3_32b_summary/metadata.json')
 sources=[root/'runs/D-E07'/name for name in ['qwen3_8b','arcane_8b_dpo','qwen3_32b']]+[root/'runs/D-E07/source_repair'/(name+'_summary') for name in ['qwen3_8b','arcane_8b_dpo','qwen3_32b']];tasks=data/'local_judge_tasks.jsonl';subprocess.run([python,str(scripts/'prepare_arcane_local_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(root/'data/arcane_D-E03/references.jsonl'),'--sources']+list(map(str,sources))+['--out',str(tasks)],cwd=project,check=True);text(tasks,'local_qwen32_judge',512,4);rows=[json.loads(l) for l in (root/'runs/D-E07/local_qwen32_judge/responses.jsonl').read_text().splitlines()];missing={r['task_id'] for r in rows if not parse_arcane_local(r)['parse_ok']}
 if missing:
  p=data/'judge_recovery_tasks.jsonl';p.write_text(''.join(l+'\n' for l in tasks.read_text().splitlines() if json.loads(l)['task_id'] in missing));text(p,'local_qwen32_judge_recovery',1024,4)
 print('Corrected S and same-information C measurements complete',flush=True)
if __name__=='__main__':main()
