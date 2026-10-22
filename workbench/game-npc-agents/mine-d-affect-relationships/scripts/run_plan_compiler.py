#!/usr/bin/env python3
"""Fixed same-information character compiler on authorized Step Token Plan only."""
import argparse,datetime,getpass,hashlib,json,os,subprocess,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from run_plan_state import ENDPOINT,MODEL

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);args=a.parse_args();root=Path(args.asset_root);data=root/'data/arcane_D-E08';out=root/'runs/D-E08/step5_compiler';out.mkdir(parents=True,exist_ok=True);assert not (out/'metadata.json').exists();taskfile=data/'compiler_tasks.jsonl';tasks=[json.loads(l) for l in taskfile.read_text().splitlines()];assert len(tasks)==len({r['task_id'] for r in tasks})==81;assert taskfile.read_bytes()==(root/'data/arcane_D-E07_v2/compiler_tasks.jsonl').read_bytes();assert ENDPOINT=='https://api.stepfun.com/step_plan/v1/chat/completions'
 meta=dict(started_utc=now(),complete=False,experiment='D-E08',transport='step_plan',kind='character_state_summary_teacher',model=MODEL,endpoint=ENDPOINT,temperature=0,reasoning_effort='low',workers=2,max_tokens_firstpass=8192,max_tokens_recovery=16384,max_requests=90,recorded_token_budget=1000000,task_sha256=hashlib.sha256(taskfile.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),json_object_transport=False)
 def save():(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes());key=getpass.getpass('Authorized Step Token Plan key (hidden): ');assert key;start=time.monotonic();rows=[];usage=Counter()
 import requests
 def call(spec):
  task,cap,attempt=spec;payload=dict(model=MODEL,messages=task['messages'],temperature=0,reasoning_effort='low',max_tokens=cap,stream=False);r={k:v for k,v in task.items() if k!='messages'};r.update(model=MODEL,transport='step_plan',attempt=attempt,started_utc=now(),request=payload,endpoint=ENDPOINT,generated_token_ids=None);begin=time.monotonic()
  try:
   with requests.Session() as session:
    session.trust_env=False;resp=session.post(ENDPOINT,json=payload,headers={'Authorization':'Bearer '+key},timeout=(20,300),allow_redirects=False)
   r.update(http_status=resp.status_code,request_id=resp.headers.get('x-request-id'));body=resp.json();r['response_body']=body
   if resp.status_code!=200:r['error']='HTTP '+str(resp.status_code)
   else:
    c=body['choices'][0];text=c['message'].get('content') or '';u=body.get('usage',{});r.update(response=text,raw=text,finish_reason=c.get('finish_reason'),usage=u,provider_model=body.get('model'),response_id=body.get('id'),usable=c.get('finish_reason')=='stop' and bool(text.strip()))
    if not all(type(u.get(k)) is int and u[k]>=0 for k in ['prompt_tokens','completion_tokens','total_tokens']):r['error']='Missing accountable token usage'
  except Exception as exc:r['error']=type(exc).__name__
  r['latency_s']=time.monotonic()-begin;return r
 def dispatch(specs,pool,f):
  for off in range(0,len(specs),2):
   block=specs[off:off+2];assert len(rows)+len(block)<=90
   reserve=sum(len(json.dumps(t['messages'],ensure_ascii=False).encode())+cap+1024 for t,cap,_ in block)
   if usage['total_tokens']+reserve>1000000:raise RuntimeError('Registered token budget guard reached')
   rr=list(pool.map(call,block))
   for r in rr:
    f.write(json.dumps(r,ensure_ascii=False)+'\n');rows.append(r)
    for k in ['prompt_tokens','completion_tokens','total_tokens']:usage[k]+=r.get('usage',{}).get(k,0)
   f.flush();os.fsync(f.fileno());meta.update(n_attempts=len(rows),usage=dict(usage),n_usable_tasks=len({r['task_id'] for r in rows if r.get('usable')}));save();print('Plan attempts',len(rows),'complete profiles',meta['n_usable_tasks'],'recorded tokens',usage['total_tokens'],flush=True)
   if any(r.get('error') for r in rr):raise RuntimeError('Plan transport failed closed: '+str([r.get('error') for r in rr]))
 try:
  with ThreadPoolExecutor(max_workers=2) as pool,(out/'responses.jsonl').open('a') as f:
   dispatch([(t,8192,1) for t in tasks],pool,f);done={r['task_id'] for r in rows if r.get('usable')};missing=[t for t in tasks if t['task_id'] not in done];meta['firstpass_usable']=len(done)
   if 0<len(missing)<=9:dispatch([(t,16384,2) for t in missing],pool,f)
   elif missing:meta['recovery_not_run']='More than nine missing profiles; no selected-subset recovery'
   meta.update(complete=True,n_source_tasks=81)
 finally:meta.update(finished_utc=now(),wall_s=time.monotonic()-start,n_attempts=len(rows),usage=dict(usage));save()
if __name__=='__main__':main()
