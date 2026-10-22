#!/usr/bin/env python3
"""Complete two independent ordinary memory chains, then measure role behavior."""
import argparse,copy,hashlib,json,os,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue_local_judges import wait_done,wait_gpu_idle
from summarize_results import parse_arcane_local

def read(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';data=root/'data/prefix_D-E09';base=root/'runs/D-E09'
 def run(argv,log,gpu):
  wait_gpu_idle(gpu);env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu),HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
  with (root/'logs'/log).open('w') as f:subprocess.run([python,'-u']+list(map(str,argv)),cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 def worker(shard):
  consumer='qwen3_32b' if shard==0 else 'arcane_8b_dpo';gpu=0 if shard==0 else 2;wait_done(root/'runs/D-E06'/('consumer_'+consumer)/'likelihood/metadata.json');run([scripts/'run_prefix_memory.py','--asset-root',root,'--shard',shard],'D-E09-memory-shard'+str(shard)+'.log',gpu)
 with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(worker,[0,1]))
 index={};chains={c['chain_id']:c for c in read(data/'chains.jsonl')}
 for shard in [0,1]:
  folder=base/('memory_shard'+str(shard));meta=json.loads((folder/'metadata.json').read_text());assert meta['complete'];rows=read(folder/'states.jsonl');assert len(rows)==meta['n_blocks']
  previous={}
  for r in rows:
   if r['chain_id'] in previous:assert r['prior_profile_sha256']==previous[r['chain_id']]
   previous[r['chain_id']]=r['profile_sha256'];b=chains[r['chain_id']]['blocks'][r['step']-1];assert b['source_sha256']==r['source_sha256']
   if r['checkpoint'] is not None:
    assert r['completed_through_unit']==r['checkpoint'];key=(r['novel'],r['character_slug'],r['checkpoint']);assert key not in index;index[key]=r
 tasks=[]
 for source in read(data/'actor_templates.jsonl'):
  t=source['trial'];state=index[t['novel'],t['character_slug'],t['query_chapter']];v=copy.deepcopy(source);prefix,tail=v['messages'][0]['content'].split('<context>\n',1);old,suffix=tail.rsplit('\n</context>',1);v['messages'][0]['content']=prefix+'<context>\nCurrent character state inferred from the narrative read so far:\n'+state['profile']+'\n</context>'+suffix;v.update(task_id=t['probe_id']+'__p'+str(t['phase_idx'])+'__prefix_memory',mode='prefix_memory',memory_state_task_id=state['task_id'],memory_profile_sha256=state['profile_sha256']);assert v['messages'][1:]==source['messages'][1:];tasks.append(v)
 assert len(tasks)==47;taskfile=data/'tasks.jsonl';assert not taskfile.exists();taskfile.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in tasks));print('Frozen full-prefix actor tasks',len(tasks),'unique memory checkpoints',len(index),flush=True)
 models=[('qwen3_8b','/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218','b968826d9c46dd6066d109eabc6255188de91218','Qwen/Qwen3-8B'),('arcane_8b_dpo',root/'models/ArcANE-8B-DPO','67b9bea604bea65a5245928ed87103545814b4f7','arcane-8B-dpo')]
 for name,checkpoint,rev,model in models:run([scripts/'run_local_arcane.py','--arcane',root/'vendor/ArcANE','--tasks',taskfile,'--checkpoint',checkpoint,'--revision',rev,'--model',model,'--out',base/name,'--max-tokens',8192,'--batch-size',4],'D-E09-'+name+'.log',2)
 judgefile=data/'local_judge_tasks.jsonl';subprocess.run([python,str(scripts/'prepare_arcane_local_judge.py'),'--arcane',str(root/'vendor/ArcANE'),'--references',str(data/'references.jsonl'),'--sources',str(base/'qwen3_8b'),str(base/'arcane_8b_dpo'),'--out',str(judgefile)],cwd=project,check=True);assert len(read(judgefile))==124
 def judge(taskfile,name,cap):run([scripts/'run_local_text.py','--tasks',taskfile,'--checkpoint',root/'models/Qwen3-32B','--revision','9216db5781bf21249d130ec9da846c4624c16137','--model','Qwen/Qwen3-32B','--out',base/name,'--max-tokens',cap,'--batch-size',4],'D-E09-'+name+'.log',2)
 judge(judgefile,'local_qwen32_judge',512);missing={r['task_id'] for r in read(base/'local_qwen32_judge/responses.jsonl') if not parse_arcane_local(r)['parse_ok']}
 if missing:
  p=data/'judge_recovery_tasks.jsonl';p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in read(judgefile) if r['task_id'] in missing));judge(p,'local_qwen32_judge_recovery',1024)
 (base/'transport_complete.json').write_text(json.dumps(dict(complete=True,n_actor_calls=94,n_primary_judgments=124))+'\n');print('Full-prefix ordinary memory measurement complete',flush=True)
if __name__=='__main__':main()
