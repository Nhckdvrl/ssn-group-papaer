#!/usr/bin/env python3
"""Advance the preregistered Summary baseline only after dependencies finish."""
import argparse,json,time,subprocess,os
from pathlib import Path


def wait_done(path):
 while True:
  if path.exists():
   m=json.loads(path.read_text())
   if m.get('complete'):return
   if m.get('finished_utc'):raise RuntimeError('Dependency failed: '+str(path))
  time.sleep(5)

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=project/'workbench/game-npc-agents/mine-d-affect-relationships/scripts';python='/home/xiang/miniconda3/envs/openslime/bin/python'
 wait_done(root/'runs/D-E03/summary_teacher/metadata.json')
 subprocess.run([python,str(scripts/'prepare_summary.py'),'apply','--arcane',str(root/'vendor/ArcANE'),'--base-assets',str(root/'data/arcane_D-E01'),'--assets',str(root/'data/arcane_D-E03'),'--manifest',str(project/'workbench/game-npc-agents/mine-d-affect-relationships/results/D-E03-selection.json'),'--teacher-responses',str(root/'runs/D-E03/summary_teacher/responses.jsonl')],check=True,cwd=project)
 specs=[('qwen3_8b','1','/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218','b968826d9c46dd6066d109eabc6255188de91218','Qwen/Qwen3-8B'),('arcane_8b_dpo','2',str(root/'models/ArcANE-8B-DPO'),'67b9bea604bea65a5245928ed87103545814b4f7','arcane-8B-dpo')]
 processes=[]
 for name,gpu,checkpoint,revision,model in specs:
  wait_done(root/'runs/D-E01'/name/'metadata.json')
  log=(root/'logs'/('D-E03-'+name+'.log')).open('w')
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
  cmd=[python,'-u',str(scripts/'run_local_arcane.py'),'--arcane',str(root/'vendor/ArcANE'),'--tasks',str(root/'data/arcane_D-E03/tasks.jsonl'),'--checkpoint',checkpoint,'--revision',revision,'--model',model,'--out',str(root/'runs/D-E03'/name),'--batch-size','4','--max-tokens','8192']
  processes.append((subprocess.Popen(cmd,cwd=project,env=env,stdout=log,stderr=subprocess.STDOUT),log))
 for process,log in processes:
  if process.wait():raise RuntimeError('Summary actor failed')
  log.close()
 print('D-E03 actor dependencies complete',flush=True)
if __name__=='__main__':main()
