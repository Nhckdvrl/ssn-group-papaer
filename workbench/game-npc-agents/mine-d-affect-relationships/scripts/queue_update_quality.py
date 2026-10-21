#!/usr/bin/env python3
"""One uniform local PUF rubric run after the frozen state-update control finishes."""
import argparse,json,os,subprocess
from pathlib import Path
from queue_local_judges import wait_done
from summarize_state_quality import parse_puf

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';env=dict(os.environ,CUDA_VISIBLE_DEVICES='2',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
 for model in ['qwen3_8b','qwen3_32b']:wait_done(root/'runs/D-E04/identity_line'/model/'metadata.json')
 tasks=root/'data/update_D-E04/puf_tasks.jsonl'
 subprocess.run([python,str(scripts/'prepare_update_quality.py'),'--asset-root',str(root),'--out',str(tasks)],cwd=project,check=True)
 def run(taskfile,name,cap,batch):
  cmd=[python,'-u',str(scripts/'run_local_text.py'),'--tasks',str(taskfile),'--checkpoint',str(root/'models/Qwen3-32B'),'--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',str(root/'runs/D-E04'/name),'--max-tokens',str(cap),'--batch-size',str(batch)]
  with (root/'logs'/('D-E04-'+name+'.log')).open('w') as f:subprocess.run(cmd,cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 run(tasks,'puf_judge',2048,8)
 rows=[json.loads(l) for l in (root/'runs/D-E04/puf_judge/responses.jsonl').read_text().splitlines()];invalid={r['task_id'] for r in rows if not parse_puf(r['response'])['parse_ok']}
 if invalid:
  if len(rows)+len(invalid)>320:raise RuntimeError('Uniform recovery would exceed registered call budget')
  recovery=tasks.with_name('puf_recovery_tasks.jsonl');recovery.write_text(''.join(l+'\n' for l in tasks.read_text().splitlines() if json.loads(l)['task_id'] in invalid));run(recovery,'puf_judge_recovery',4096,4)
 print('PUF complete before-state evaluation complete',flush=True)
if __name__=='__main__':main()
