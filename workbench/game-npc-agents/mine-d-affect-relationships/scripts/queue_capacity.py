#!/usr/bin/env python3
"""Run the preregistered 32B ordinary role-player on the fixed nested cohort."""
import argparse,json,os,subprocess,hashlib
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';assets=root/'data/arcane_D-E03';run=root/'runs/D-E03'
 def read(p):return [json.loads(l) for l in p.read_text().splitlines()]
 selected={r['trial_id'].rsplit('__p',1)[0] for r in read(assets/'references.jsonl')}
 tasks=[r for r in read(root/'data/arcane_D-E01/tasks.jsonl') if r['trial']['probe_id'] in selected]+read(assets/'tasks.jsonl');assert len(tasks)==243 and len({r['task_id'] for r in tasks})==243
 tasks.sort(key=lambda t:hashlib.sha256(('D-E03-capacity|'+t['task_id']).encode()).hexdigest());taskfile=assets/'capacity_tasks.jsonl'
 if taskfile.exists():assert read(taskfile)==tasks
 else:taskfile.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in tasks))
 env=dict(os.environ,HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
 wait_done(root/'runs/D-E04/qwen3_32b/metadata.json')
 actor=[python,'-u',str(scripts/'run_local_arcane.py'),'--arcane',str(root/'vendor/ArcANE'),'--tasks',str(taskfile),'--checkpoint',str(root/'models/Qwen3-32B'),'--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',str(run/'qwen3_32b'),'--max-tokens','8192','--batch-size','4']
 with (root/'logs/D-E03-qwen3_32b.log').open('w') as log:subprocess.run(actor,cwd=project,env=dict(env,CUDA_VISIBLE_DEVICES='2'),stdout=log,stderr=subprocess.STDOUT,check=True)
 judgetasks=assets/'capacity_judge_tasks.jsonl'
 subprocess.run([python,str(scripts/'prepare_arcane_local_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(assets/'references.jsonl'),'--sources',str(run/'qwen3_32b'),'--out',str(judgetasks)],cwd=project,check=True)
 assert len(read(judgetasks))==318
 wait_done(run/'local_qwen32_judge/metadata.json')
 if (run/'local_qwen32_judge_recovery/metadata.json').exists():wait_done(run/'local_qwen32_judge_recovery/metadata.json')
 # Completion sentinel includes transport recovery and process teardown, avoiding a GPU collision.
 while not (run/'local_judge_transport_complete.json').exists():
  import time;time.sleep(5)
 def judge(tasks,out,log,cap):
  cmd=[python,'-u',str(scripts/'run_local_text.py'),'--tasks',str(tasks),'--checkpoint',str(root/'models/Qwen3-32B'),'--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',str(out),'--max-tokens',str(cap),'--batch-size','4']
  with log.open('w') as f:subprocess.run(cmd,cwd=project,env=dict(env,CUDA_VISIBLE_DEVICES='1'),stdout=f,stderr=subprocess.STDOUT,check=True)
 judge(judgetasks,run/'local_qwen32_capacity_judge',root/'logs/D-E03-capacity-judge.log',512)
 rows=[parse_arcane_local(r) for r in read(run/'local_qwen32_capacity_judge/responses.jsonl')];missing={r['judge_id'] for r in rows if not r['parse_ok']}
 if missing:
  recovery=assets/'capacity_judge_recovery_tasks.jsonl';recovery.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in read(judgetasks) if t['task_id'] in missing));judge(recovery,run/'local_qwen32_capacity_judge_recovery',root/'logs/D-E03-capacity-judge-recovery.log',1024)
 print('32B role capacity reference complete',flush=True)
if __name__=='__main__':main()
