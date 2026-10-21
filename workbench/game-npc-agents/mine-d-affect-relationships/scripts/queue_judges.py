#!/usr/bin/env python3
"""State-based overnight judge queue, one fixed Step Plan policy and bounded calls."""
import argparse,json,time,subprocess,os,getpass
from pathlib import Path


def wait_done(path):
 while True:
  if path.exists():
   m=json.loads(path.read_text())
   if m.get('complete'):return m
   if m.get('finished_utc'):raise RuntimeError('Dependency failed or quota stopped: '+str(path))
  time.sleep(5)

def invalid_ids(path):
 rs=[json.loads(l) for l in path.read_text().splitlines() if l.strip()]
 good={r['judge_id'] for r in rs if r.get('parse_ok')};allids={r['judge_id'] for r in rs}
 return allids-good

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=project/'workbench/game-npc-agents/mine-d-affect-relationships/scripts'
 key=os.environ.get('STEPFUN_API_KEY') or getpass.getpass('Step Plan API key (hidden): ')
 env=dict(os.environ,STEPFUN_API_KEY=key);python='python3'
 def judge(exp,n,budget,resume=False,retry=False):
  asset='arcane_'+exp
  cmd=[python,str(scripts/'run_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(root/'data'/asset/'references.jsonl'),'--sources',str(root/'runs'/exp/'qwen3_8b'),str(root/'runs'/exp/'arcane_8b_dpo'),'--out',str(root/'runs'/exp/'step5_judge'),'--expected-per-source',str(n),'--budget-calls',str(budget),'--reasoning-effort','low','--workers','6']
  if resume:cmd.append('--resume')
  if retry:cmd+=['--retry-invalid-once','--max-tokens','16384']
  with (root/'logs'/(exp+('-recovery' if retry else '-queued-judge')+'.log')).open('w') as f:subprocess.run(cmd,cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 wait_done(root/'runs/D-E01/step5_judge/metadata.json')
 missing=invalid_ids(root/'runs/D-E01/step5_judge/judgments.jsonl')
 if missing:judge('D-E01',410,1180,resume=True,retry=True)
 (root/'runs/D-E01/step5_judge/RECOVERY_COMPLETE.json').write_text(json.dumps(dict(recovery_attempted=bool(missing),invalid_before=len(missing),invalid_after=len(invalid_ids(root/'runs/D-E01/step5_judge/judgments.jsonl'))),indent=2)+'\n')
 wait_done(root/'runs/D-E03/qwen3_8b/metadata.json');wait_done(root/'runs/D-E03/arcane_8b_dpo/metadata.json')
 judge('D-E03',81,250)
 missing=invalid_ids(root/'runs/D-E03/step5_judge/judgments.jsonl')
 if missing:judge('D-E03',81,250,resume=True,retry=True)
 (root/'runs/D-E03/step5_judge/RECOVERY_COMPLETE.json').write_text(json.dumps(dict(recovery_attempted=bool(missing),invalid_before=len(missing),invalid_after=len(invalid_ids(root/'runs/D-E03/step5_judge/judgments.jsonl'))),indent=2)+'\n')
 print('Registered judge queue finished',flush=True)
if __name__=='__main__':main()
