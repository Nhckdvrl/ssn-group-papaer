#!/usr/bin/env python3
"""Use the complete strong ordinary profiles with two fixed role consumers."""
import argparse,copy,hashlib,json,os,subprocess,time
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local

def read(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);a.add_argument('--gpu',default='2');a.add_argument('--after');args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';data=root/'data/arcane_D-E08';base=root/'runs/D-E08'
 wait_done(base/'step5_compiler/metadata.json');raw=read(base/'step5_compiler/responses.jsonl');expected={r['task_id']:r for r in read(data/'compiler_tasks.jsonl')};index={}
 for r in raw:
  assert r['request']['messages']==expected[r['task_id']]['messages']
  if r.get('usable'):index.setdefault(r['task_id'],r)
 assert set(index)==set(expected),'Do not score selectively complete profiles';tasks=[];proof=[]
 for r in read(root/'data/arcane_D-E07_v2/summary_tasks_all.jsonl'):
  v=copy.deepcopy(r);key=r['task_id'].removesuffix('__summary')+'__compiler';text=index[key]['response'];prefix,tail=v['messages'][0]['content'].split('<context>\n',1);old,suffix=tail.rsplit('\n</context>',1);v['messages'][0]['content']=prefix+'<context>\nCurrent character state inferred from the supplied recent summaries:\n'+text+'\n</context>'+suffix;v.update(task_id=r['task_id'].removesuffix('__summary')+'__state_summary_step',mode='state_summary_step',compiler_response_sha256=hashlib.sha256(text.encode()).hexdigest());assert v['messages'][1:]==r['messages'][1:];tasks.append(v);proof.append(dict(task_id=v['task_id'],compiler_task_id=key,selected_attempt=index[key]['attempt'],compiler_response_sha256=v['compiler_response_sha256']))
 taskfile=data/'tasks.jsonl';content=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in tasks)
 if taskfile.exists():assert taskfile.read_text()==content,'Never replace frozen actor inputs'
 else:taskfile.write_text(content)
 (data/'actor_provenance.json').write_text(json.dumps(dict(n=81,only_context_changed=True,details=proof),indent=2)+'\n');print('Complete Step profiles frozen for actors',len(tasks),flush=True)
 wait_done(Path(args.after) if args.after else root/'runs/D-E06/consumer_arcane_8b_dpo/likelihood/metadata.json');time.sleep(3);env=dict(os.environ,CUDA_VISIBLE_DEVICES=args.gpu,HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
 def run(argv,log):
  with (root/'logs'/log).open('w') as f:subprocess.run([python,'-u']+list(map(str,argv)),cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 models=[('qwen3_8b','/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218','b968826d9c46dd6066d109eabc6255188de91218','Qwen/Qwen3-8B'),('arcane_8b_dpo',root/'models/ArcANE-8B-DPO','67b9bea604bea65a5245928ed87103545814b4f7','arcane-8B-dpo')]
 for name,checkpoint,rev,model in models:run([scripts/'run_local_arcane.py','--arcane',root/'vendor/ArcANE','--tasks',taskfile,'--checkpoint',checkpoint,'--revision',rev,'--model',model,'--out',base/name,'--max-tokens',8192,'--batch-size',4],'D-E08-'+name+'.log')
 judgefile=data/'local_judge_tasks.jsonl';subprocess.run([python,str(scripts/'prepare_arcane_local_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(root/'data/arcane_D-E03/references.jsonl'),'--sources',str(base/'qwen3_8b'),str(base/'arcane_8b_dpo'),'--out',str(judgefile)],cwd=project,check=True);assert len(read(judgefile))==212
 def judge(tasks,name,cap):run([scripts/'run_local_text.py','--tasks',tasks,'--checkpoint',root/'models/Qwen3-32B','--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',base/name,'--max-tokens',cap,'--batch-size',4],'D-E08-'+name+'.log')
 judge(judgefile,'local_qwen32_judge',512);missing={r['task_id'] for r in read(base/'local_qwen32_judge/responses.jsonl') if not parse_arcane_local(r)['parse_ok']}
 if missing:
  p=data/'judge_recovery_tasks.jsonl';p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in read(judgefile) if r['task_id'] in missing));judge(p,'local_qwen32_judge_recovery',1024)
 (base/'transport_complete.json').write_text(json.dumps(dict(complete=True,n_actors=162,n_primary_judgments=212))+'\n');print('Strong ordinary compiler measurement complete',flush=True)
if __name__=='__main__':main()
