#!/usr/bin/env python3
"""Score completed actor partitions without leaving the evaluator GPU idle."""
import argparse,json,os,subprocess
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);a.add_argument('--capacity-only',action='store_true');args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';base=root/'runs/D-E07';data=root/'data/arcane_D-E07_v2';env=dict(os.environ,CUDA_VISIBLE_DEVICES='3',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
 def run(argv,log):
  with (root/'logs'/log).open('w') as f:subprocess.run([python,'-u']+list(map(str,argv)),cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 partitions=[(['qwen3_8b','arcane_8b_dpo'],'local_qwen32_judge',248),(['qwen3_32b'],'local_qwen32_capacity_judge',124)]
 if args.capacity_only:wait_done(base/'primary_judge_transport_complete.json');partitions=partitions[1:]
 for models,name,n in partitions:
  sources=[base/model for model in models]+[base/'source_repair'/(model+'_summary') for model in models]
  for source in sources:wait_done(source/'metadata.json')
  tasks=data/(name+'_tasks.jsonl');assert not tasks.exists();subprocess.run([python,str(scripts/'prepare_arcane_local_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(root/'data/arcane_D-E03/references.jsonl'),'--sources']+list(map(str,sources))+['--out',str(tasks)],cwd=project,check=True);assert len(tasks.read_text().splitlines())==n
  def judge(taskfile,outname,cap):run([scripts/'run_local_text.py','--tasks',taskfile,'--checkpoint',root/'models/Qwen3-32B','--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',base/outname,'--max-tokens',cap,'--batch-size',4],'D-E07-'+outname+'.log')
  judge(tasks,name,512);raw=[json.loads(l) for l in (base/name/'responses.jsonl').read_text().splitlines()];missing={r['task_id'] for r in raw if not parse_arcane_local(r)['parse_ok']}
  if missing:
   p=data/(name+'_recovery_tasks.jsonl');p.write_text(''.join(l+'\n' for l in tasks.read_text().splitlines() if json.loads(l)['task_id'] in missing));judge(p,name+'_recovery',1024)
  print('Completed judge partition',name,n,flush=True)
  if name=='local_qwen32_judge':(base/'primary_judge_transport_complete.json').write_text(json.dumps(dict(complete=True,n=248))+'\n')
 (base/'transport_complete.json').write_text(json.dumps(dict(complete=True,n_primary_judgments=372,partitions=[248,124]))+'\n')
if __name__=='__main__':main()
