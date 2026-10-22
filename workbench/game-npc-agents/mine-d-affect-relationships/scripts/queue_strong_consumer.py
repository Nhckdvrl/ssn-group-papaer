#!/usr/bin/env python3
"""Check state-use with existing strong consumers on frozen cases, no new prompts."""
import argparse,json,time,subprocess,os
from pathlib import Path
from queue_local_judges import wait_done

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);a.add_argument('--consumer',choices=['arcane_8b_dpo','qwen3_32b'],required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';data=root/'data/closed_D-E06';ready=data/'strong_consumers_READY.json';all_tasks=data/'actor_all_conditions.jsonl';subset=data/'actor_preselected_review.jsonl'
 if args.consumer=='arcane_8b_dpo':
  for mode in ['teacher_forced','recursive_native','recursive_summary']:wait_done(root/'runs/D-E06'/mode/'metadata.json')
  subprocess.run([python,str(scripts/'prepare_closed_actor.py'),'--asset-root',str(root),'--conditions','released','frozen','teacher_forced','recursive_native','recursive_summary','--out',str(all_tasks)],cwd=project,check=True);tasks=[json.loads(l) for l in all_tasks.read_text().splitlines()];review=[r for r in tasks if r['preselected_review']];assert len(tasks)==435 and len(review)==120;subset.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in review));ready.write_text(json.dumps(dict(complete=True,n_all=435,n_generation_subset=120,subset='Previously frozen first trajectory per source book; all three checkpoints and all conditions, no output filtering'),indent=2)+'\n');gpu='2';checkpoint=root/'models/ArcANE-8B-DPO';revision='67b9bea604bea65a5245928ed87103545814b4f7';model='arcane-8B-dpo';batch=4
 else:
  for mode in ['baselines','teacher_forced','recursive_native','recursive_summary']:wait_done(root/'runs/D-E06'/('likelihood_'+mode)/'metadata.json')
  while not ready.exists():time.sleep(5)
  gpu='0';checkpoint=root/'models/Qwen3-32B';revision='9216db5781bf21249d130ec9da846c4624c16137';model='Qwen/Qwen3-32B';batch=2
 time.sleep(3);env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false');out=root/'runs/D-E06'/('consumer_'+args.consumer)
 def run(argv,log):
  with (root/'logs'/log).open('w') as f:subprocess.run([python,'-u']+list(map(str,argv)),cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 run([scripts/'run_local_text.py','--tasks',subset,'--checkpoint',checkpoint,'--revision',revision,'--model',model,'--out',out/'actor','--max-tokens',1024,'--batch-size',batch],'D-E06-'+args.consumer+'-actor.log')
 run([scripts/'score_role_likelihood.py','--tasks',all_tasks,'--references',data/'references.jsonl','--checkpoint',checkpoint,'--revision',revision,'--model',model,'--out',out/'likelihood'],'D-E06-'+args.consumer+'-likelihood.log');print('Strong consumer complete',args.consumer,flush=True)
if __name__=='__main__':main()
