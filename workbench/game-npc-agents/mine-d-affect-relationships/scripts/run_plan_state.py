#!/usr/bin/env python3
"""Bounded authorized Plan-only strong actor, never a cash/provider fallback."""
import argparse,json,hashlib,datetime,time,os,getpass,importlib.util
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

ENDPOINT='https://api.stepfun.com/step_plan/v1/chat/completions'
MODEL='step-5-preview'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 a=argparse.ArgumentParser();a.add_argument('--tasks',required=True);a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);out=Path(args.out);out.mkdir(parents=True,exist_ok=True);assert not (out/'metadata.json').exists();tasks=[json.loads(l) for l in Path(args.tasks).read_text().splitlines()];assert len(tasks)==len({t['task_id'] for t in tasks})==64
 spec=importlib.util.spec_from_file_location('native_utils',root/'vendor/EvolvingWorld/simulation/utils.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
 def usable(text):
  try:
   o=native.extract_json_fragment(text);flag=o.get('profile_updated');p=o.get('updated_profile');profile=native.dict_to_markdown_text(p) if isinstance(p,(dict,list)) else p
   return type(flag) is bool and ((flag and isinstance(profile,str) and bool(profile.strip())) or (not flag and p is None and 'updated_profile' in o)) and 'hidden_tracker' in o and isinstance(o.get('short_description'),str) and bool(o['short_description'].strip())
  except Exception:return False
 meta=dict(started_utc=now(),complete=False,transport='step_plan',kind='state_update_actor',model=MODEL,endpoint=ENDPOINT,args=vars(args),task_sha256=hashlib.sha256(Path(args.tasks).read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),temperature=0,reasoning_effort='low',workers=2,max_tokens_firstpass=8192,max_tokens_recovery=16384,max_requests=72,recorded_token_budget=800000,json_object_transport=True)
 def save():(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes());key=getpass.getpass('Authorized Step Plan key (hidden): ');assert key;start=time.monotonic();rows=[];usage=Counter()
 import requests
 def call(spec):
  task,cap,attempt=spec;payload=dict(model=MODEL,messages=task['messages'],temperature=0,reasoning_effort='low',max_tokens=cap,response_format={'type':'json_object'},stream=False);r={k:v for k,v in task.items() if k!='messages'};r.update(model=MODEL,transport='step_plan',attempt=attempt,started_utc=now(),request=payload,endpoint=ENDPOINT,generated_token_ids=None);begin=time.monotonic()
  try:
   with requests.Session() as session:
    session.trust_env=False;resp=session.post(ENDPOINT,json=payload,headers={'Authorization':'Bearer '+key},timeout=(20,300),allow_redirects=False)
   r.update(http_status=resp.status_code,request_id=resp.headers.get('x-request-id'));body=resp.json();r['response_body']=body
   if resp.status_code!=200:r['error']='HTTP '+str(resp.status_code)
   else:
    c=body['choices'][0];text=c['message'].get('content') or '';r.update(response=text,raw=text,finish_reason=c.get('finish_reason'),usage=body.get('usage',{}),provider_model=body.get('model'),response_id=body.get('id'),complete_state=usable(text))
  except Exception as exc:r['error']=type(exc).__name__
  r['latency_s']=time.monotonic()-begin;return r
 def dispatch(specs,pool,f):
  for off in range(0,len(specs),2):
   block=specs[off:off+2];assert len(rows)+len(block)<=72
   reserve=sum(len(json.dumps(t['messages'],ensure_ascii=False).encode())+cap+1024 for t,cap,_ in block)
   if usage['total_tokens']+reserve>800000:raise RuntimeError('Registered recorded-token budget guard reached')
   rr=list(pool.map(call,block))
   for r in rr:
    f.write(json.dumps(r,ensure_ascii=False)+'\n');rows.append(r)
    for k in ['prompt_tokens','completion_tokens','total_tokens']:usage[k]+=r.get('usage',{}).get(k,0)
   f.flush();os.fsync(f.fileno());meta.update(n_attempts=len(rows),usage=dict(usage),n_complete_state_tasks=len({r['task_id'] for r in rows if r.get('complete_state')}));save();print('attempts',len(rows),'complete state tasks',meta['n_complete_state_tasks'],'recorded tokens',usage['total_tokens'],flush=True)
   if any(r.get('error') for r in rr):raise RuntimeError('Plan transport failed closed: '+str([r.get('error') for r in rr]))
 try:
  with ThreadPoolExecutor(max_workers=2) as pool,(out/'responses.jsonl').open('a') as f:
   dispatch([(t,8192,1) for t in tasks],pool,f);meta['firstpass_complete_state']=sum(r.get('complete_state',False) for r in rows)
   done={r['task_id'] for r in rows if r.get('complete_state')};missing=[t for t in tasks if t['task_id'] not in done]
   if 0<len(missing)<=8:dispatch([(t,16384,2) for t in missing],pool,f)
   elif missing:meta['recovery_not_run']='More than eight missing states; no selected-subset recovery'
   meta.update(complete=True,n_source_tasks=64,n_responses=sum(r.get('http_status')==200 for r in rows))
 finally:meta.update(finished_utc=now(),wall_s=time.monotonic()-start,n_attempts=len(rows),usage=dict(usage));save()
if __name__=='__main__':main()
