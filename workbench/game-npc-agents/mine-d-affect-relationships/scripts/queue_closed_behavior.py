#!/usr/bin/env python3
"""Use GPU0 after its updater finishes; phase-source repair cannot stall D-E06."""
import argparse,json,subprocess,os,time
from pathlib import Path
from queue_local_judges import wait_done

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);scripts=Path(__file__).resolve().parent;project=Path(args.project);python='/home/xiang/miniconda3/envs/openslime/bin/python';env=dict(os.environ,CUDA_VISIBLE_DEVICES='0',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false');q8='/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218';rev='b968826d9c46dd6066d109eabc6255188de91218';wait_done(root/'runs/D-E06/teacher_forced/metadata.json');time.sleep(3)
 def run(argv,log):
  with (root/'logs'/log).open('w') as f:subprocess.run([python,'-u']+list(map(str,argv)),cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 todo=['teacher_forced','recursive_native','recursive_summary']
 while todo:
  ready=[]
  for mode in todo:
   p=root/'runs/D-E06'/mode/'metadata.json'
   if p.exists():
    m=json.loads(p.read_text())
    if m['complete']:ready.append(mode)
    elif m.get('finished_utc'):raise RuntimeError('Updater dependency failed: '+mode)
  if not ready:time.sleep(5);continue
  mode=ready[0];tasks=root/'data/closed_D-E06'/('actor_'+mode+'.jsonl');subprocess.run([python,str(scripts/'prepare_closed_actor.py'),'--asset-root',str(root),'--conditions',mode,'--out',str(tasks)],cwd=project,check=True)
  run([scripts/'run_local_text.py','--tasks',tasks,'--checkpoint',q8,'--revision',rev,'--model','Qwen/Qwen3-8B','--out',root/'runs/D-E06'/('actor_'+mode),'--max-tokens',1024,'--batch-size',4],'D-E06-actor_'+mode+'.log')
  run([scripts/'score_role_likelihood.py','--tasks',tasks,'--references',root/'data/closed_D-E06/references.jsonl','--checkpoint',q8,'--revision',rev,'--model','Qwen/Qwen3-8B','--out',root/'runs/D-E06'/('likelihood_'+mode)],'D-E06-likelihood_'+mode+'.log');todo.remove(mode)
 print('D-E06 full linked behavior complete',flush=True)
if __name__=='__main__':main()
