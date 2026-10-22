#!/usr/bin/env python3
"""Own GPU3 after the baseline actor: actual state induction then role behavior."""
import argparse,json,subprocess,os,time
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';env=dict(os.environ,CUDA_VISIBLE_DEVICES='3',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false');q8='/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218';r8='b968826d9c46dd6066d109eabc6255188de91218';r32='9216db5781bf21249d130ec9da846c4624c16137'
 def execute(argv,log):
  with (root/'logs'/log).open('w') as f:subprocess.run([python,'-u']+list(map(str,argv)),cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 def text(tasks,out,checkpoint,revision,model,cap,batch,log):execute([scripts/'run_local_text.py','--tasks',tasks,'--checkpoint',checkpoint,'--revision',revision,'--model',model,'--out',out,'--max-tokens',cap,'--batch-size',batch],log)
 def nll(tasks,name):execute([scripts/'score_role_likelihood.py','--tasks',tasks,'--references',root/'data/closed_D-E06/references.jsonl','--checkpoint',q8,'--revision',r8,'--model','Qwen/Qwen3-8B','--out',root/'runs/D-E06'/name],name+'.log')
 wait_done(root/'runs/D-E06/actor_baselines/metadata.json');nll(root/'data/closed_D-E06/actor_baselines.jsonl','likelihood_baselines')
 tasks=root/'data/arcane_D-E07/compiler_tasks.jsonl';run=root/'runs/D-E07/state_compiler';text(tasks,run,root/'models/Qwen3-32B',r32,'Qwen/Qwen3-32B',2048,4,'D-E07-state_compiler.log');rows=[json.loads(l) for l in (run/'responses.jsonl').read_text().splitlines()];missing={r['task_id'] for r in rows if r['finish_reason']!='stop' or not r['response'].strip()}
 if missing:
  p=tasks.with_name('compiler_recovery_tasks.jsonl');p.write_text(''.join(l+'\n' for l in tasks.read_text().splitlines() if json.loads(l)['task_id'] in missing));text(p,root/'runs/D-E07/state_compiler_recovery',root/'models/Qwen3-32B',r32,'Qwen/Qwen3-32B',8192,2,'D-E07-state_compiler_recovery.log')
 subprocess.run([python,str(scripts/'prepare_state_summary.py'),'apply','--asset-root',str(root)],cwd=project,check=True)
 sources=[]
 for name,checkpoint,revision,model,batch in [('qwen3_8b',q8,r8,'Qwen/Qwen3-8B',4),('arcane_8b_dpo',root/'models/ArcANE-8B-DPO','67b9bea604bea65a5245928ed87103545814b4f7','arcane-8B-dpo',4),('qwen3_32b',root/'models/Qwen3-32B',r32,'Qwen/Qwen3-32B',2)]:
  out=root/'runs/D-E07'/name;execute([scripts/'run_local_arcane.py','--arcane',root/'vendor/ArcANE','--tasks',root/'data/arcane_D-E07/tasks.jsonl','--checkpoint',checkpoint,'--revision',revision,'--model',model,'--out',out,'--batch-size',batch,'--max-tokens',8192],'D-E07-'+name+'.log');sources.append(out)
 judge_tasks=root/'data/arcane_D-E07/local_judge_tasks.jsonl';subprocess.run([python,str(scripts/'prepare_arcane_local_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(root/'data/arcane_D-E03/references.jsonl'),'--sources']+list(map(str,sources))+['--out',str(judge_tasks)],cwd=project,check=True);judge=root/'runs/D-E07/local_qwen32_judge';text(judge_tasks,judge,root/'models/Qwen3-32B',r32,'Qwen/Qwen3-32B',512,4,'D-E07-local_judge.log');rows=[json.loads(l) for l in (judge/'responses.jsonl').read_text().splitlines()];missing={r['task_id'] for r in rows if not parse_arcane_local(r)['parse_ok']}
 if missing:
  p=judge_tasks.with_name('judge_recovery_tasks.jsonl');p.write_text(''.join(l+'\n' for l in judge_tasks.read_text().splitlines() if json.loads(l)['task_id'] in missing));text(p,root/'runs/D-E07/local_qwen32_judge_recovery',root/'models/Qwen3-32B',r32,'Qwen/Qwen3-32B',1024,4,'D-E07-local_judge_recovery.log')
 todo=['teacher_forced','recursive_native','recursive_summary']
 while todo:
  ready=[]
  for mode in todo:
   p=root/'runs/D-E06'/mode/'metadata.json'
   if p.exists():
    m=json.loads(p.read_text())
    if m.get('complete'):ready.append(mode)
    elif m.get('finished_utc'):raise RuntimeError('State dependency failed: '+mode)
  if not ready:time.sleep(5);continue
  mode=ready[0];tasks=root/'data/closed_D-E06'/('actor_'+mode+'.jsonl');subprocess.run([python,str(scripts/'prepare_closed_actor.py'),'--asset-root',str(root),'--conditions',mode,'--out',str(tasks)],cwd=project,check=True);text(tasks,root/'runs/D-E06'/('actor_'+mode),q8,r8,'Qwen/Qwen3-8B',1024,4,'D-E06-actor_'+mode+'.log');nll(tasks,'likelihood_'+mode);todo.remove(mode)
 print('D-E06 linked behavior and D-E07 ordinary state-summary measurements complete',flush=True)
if __name__=='__main__':main()
