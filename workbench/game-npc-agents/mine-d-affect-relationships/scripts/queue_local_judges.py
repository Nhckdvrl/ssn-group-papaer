#!/usr/bin/env python3
"""Complete uniform local evaluations, then advance the nested Summary reference."""
import argparse,json,os,subprocess,time
from pathlib import Path
from summarize_results import parse_arcane_local

def wait_done(path):
 while True:
  if path.exists():
   m=json.loads(path.read_text())
   if m.get('complete'):return
   if m.get('finished_utc'):raise RuntimeError('Dependency failed: '+str(path))
  time.sleep(5)

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python'
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='3',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
 def run(tasks,out,log,cap):
  cmd=[python,'-u',str(scripts/'run_local_text.py'),'--tasks',str(tasks),'--checkpoint',str(root/'models/Qwen3-32B'),'--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',str(out),'--max-tokens',str(cap),'--batch-size','4']
  with log.open('w') as f:subprocess.run(cmd,cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 def recovery(experiment):
  base=root/'runs'/experiment;data=root/'data'/('arcane_'+experiment)
  responses=[parse_arcane_local(json.loads(l)) for l in (base/'local_qwen32_judge/responses.jsonl').read_text().splitlines()]
  invalid={r['judge_id'] for r in responses if not r['parse_ok']}
  audit=dict(n_initial=len(responses),n_missing_complete_scores=len(invalid),invalid_ids=sorted(invalid),policy='Only missing/invalid complete scores are retried once at 1024. Complete JSON preceding trailing commentary is scored with compliance flag, never regenerated.')
  (base/'local_judge_transport_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
  if not invalid:return
  rows=[json.loads(l) for l in (data/'local_judge_tasks.jsonl').read_text().splitlines()];selected=[r for r in rows if r['task_id'] in invalid];assert len(selected)==len(invalid)
  tasks=data/'local_judge_recovery_tasks.jsonl';tasks.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in selected))
  run(tasks,base/'local_qwen32_judge_recovery',root/'logs'/(experiment+'-local-judge-recovery.log'),1024)
 wait_done(root/'runs/D-E01/local_qwen32_judge/metadata.json');recovery('D-E01')
 for model in ['qwen3_8b','arcane_8b_dpo']:wait_done(root/'runs/D-E03'/model/'metadata.json')
 tasks=root/'data/arcane_D-E03/local_judge_tasks.jsonl'
 subprocess.run([python,str(scripts/'prepare_arcane_local_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(root/'data/arcane_D-E03/references.jsonl'),'--sources',str(root/'runs/D-E03/qwen3_8b'),str(root/'runs/D-E03/arcane_8b_dpo'),'--out',str(tasks)],cwd=project,check=True)
 assert len(tasks.read_text().splitlines())==212
 run(tasks,root/'runs/D-E03/local_qwen32_judge',root/'logs/D-E03-local-judge.log',512);recovery('D-E03')
 print('Uniform local D-E01 and D-E03 judging complete',flush=True)
if __name__=='__main__':main()
