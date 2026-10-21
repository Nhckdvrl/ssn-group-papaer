#!/usr/bin/env python3
"""Score the complete Plan cohort after the existing GPU1 judge is released."""
import argparse,json,time,os,subprocess
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local
from summarize_state_quality import parse_puf

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';meta=root/'runs/D-E05/step5/metadata.json'
 while True:
  if meta.exists():
   m=json.loads(meta.read_text())
   if m.get('complete'):break
   if m.get('finished_utc'):print('Plan actor incomplete; no complete-cohort grading or capability conclusion',flush=True);return
  time.sleep(5)
 tasks=root/'data/update_D-E04/plan_puf_tasks.jsonl';subprocess.run([python,str(scripts/'prepare_plan_quality.py'),'--asset-root',str(root),'--out',str(tasks)],cwd=project,check=True)
 cap=root/'runs/D-E03/local_qwen32_capacity_judge';wait_done(cap/'metadata.json');rows=[json.loads(l) for l in (cap/'responses.jsonl').read_text().splitlines()]
 if any(not parse_arcane_local(r)['parse_ok'] for r in rows):wait_done(root/'runs/D-E03/local_qwen32_capacity_judge_recovery/metadata.json')
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='1',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
 def run(taskfile,name,tokens,batch):
  cmd=[python,'-u',str(scripts/'run_local_text.py'),'--tasks',str(taskfile),'--checkpoint',str(root/'models/Qwen3-32B'),'--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',str(root/'runs/D-E05'/name),'--max-tokens',str(tokens),'--batch-size',str(batch)]
  with (root/'logs'/('D-E05-'+name+'.log')).open('w') as f:subprocess.run(cmd,cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 run(tasks,'puf_judge',2048,8);rows=[json.loads(l) for l in (root/'runs/D-E05/puf_judge/responses.jsonl').read_text().splitlines()];missing={r['task_id'] for r in rows if not parse_puf(r['response'])['parse_ok']}
 if 0<len(missing)<=8:
  recovery=tasks.with_name('plan_puf_recovery_tasks.jsonl');recovery.write_text(''.join(l+'\n' for l in tasks.read_text().splitlines() if json.loads(l)['task_id'] in missing));run(recovery,'puf_judge_recovery',4096,4)
 print('Strong Plan actor PUF reference complete',flush=True)
if __name__=='__main__':main()
