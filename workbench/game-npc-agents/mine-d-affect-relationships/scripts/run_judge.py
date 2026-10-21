#!/usr/bin/env python3
"""Streaming official ArcANE judge prompts through the authorized Step Plan only."""
import argparse,json,sys,time,datetime,hashlib,os,getpass
from pathlib import Path
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor

ENDPOINT='https://api.stepfun.com/step_plan/v1/chat/completions'
MODEL='step-5-preview'
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read_rows(path):
 if not Path(path).exists():return []
 lines=Path(path).read_bytes().splitlines(keepends=True);out=[]
 for i,l in enumerate(lines):
  if not l.endswith(b'\n') and i==len(lines)-1:continue
  if l.strip():out.append(json.loads(l))
 return out

def main():
 a=argparse.ArgumentParser();a.add_argument('--arcane',required=True);a.add_argument('--references',required=True);a.add_argument('--sources',nargs='+',required=True);a.add_argument('--out',required=True);a.add_argument('--expected-per-source',type=int,required=True);a.add_argument('--budget-calls',type=int,default=1200);a.add_argument('--reasoning-effort',choices=['low','medium'],default='low');a.add_argument('--max-wait-s',type=int,default=21600);a.add_argument('--workers',type=int,choices=[1,2,4,6],default=2);a.add_argument('--resume',action='store_true');a.add_argument('--retry-invalid-once',action='store_true');a.add_argument('--max-tokens',type=int,default=8192);args=a.parse_args()
 sys.path.insert(0,args.arcane)
 from evaluation.per_response.prompt import EvalTrial,render_evaluator_messages as single_messages
 from evaluation.trajectory.prompt import PhaseRef,render_evaluator_messages as trajectory_messages
 from evaluation.scoring import scores_with_average
 import requests
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 if (out/'metadata.json').exists() and not args.resume:raise FileExistsError('Use --resume for the exact same protocol only')
 prior=json.loads((out/'metadata.json').read_text()) if args.resume else None
 if prior:
  old_source=out/'runner_source.py'
  if old_source.exists():
   (out/('runner_source_before_resume_'+str(prior.get('calls',0))+'.py')).write_bytes(old_source.read_bytes())
  assert prior['reasoning_effort']==args.reasoning_effort
  assert prior['args']['references']==args.references and prior['args']['sources']==args.sources
 refs={r['trial_id']:r['reference'] for r in read_rows(args.references)}
 expected_phases=defaultdict(set)
 for tid in refs:
  probe,phase=tid.rsplit('__p',1);expected_phases[probe].add(int(phase))
 key=os.environ.get('STEPFUN_API_KEY') or getpass.getpass('Step Plan API key (hidden): ')
 if not key:raise ValueError('Missing authorized key')
 meta=dict(started_utc=stamp(),args=vars(args),endpoint=ENDPOINT,model=MODEL,temperature=0,reasoning_effort=args.reasoning_effort,max_tokens=args.max_tokens,workers=args.workers,complete=False,protocol='Official ArcANE prompts and scale100; Step5 judge substitution; no method/model labels sent',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (out/'runner_source.py').write_bytes(Path(__file__).read_bytes());(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
 existing=read_rows(out/'judgments.jsonl') if args.resume else []
 seen={r['judge_id'] for r in existing if (r.get('parse_ok') if args.retry_invalid_once else (not r.get('error') or r.get('error')=='invalid_judge_verdict'))};attempts=len(existing);scored=sum(bool(r.get('parse_ok')) for r in existing);usage=Counter()
 for r in existing:
  for k,v in r.get('usage',{}).items():
   if isinstance(v,(int,float)):usage[k]+=v
 if prior:
  (out/('metadata_before_resume_'+str(attempts)+'.json')).write_text(json.dumps(prior,indent=2)+'\n')
  meta['initial_started_utc']=prior.get('initial_started_utc',prior['started_utc'])
  meta['prior_wall_s']=prior.get('wall_s',0)+prior.get('prior_wall_s',0)
  meta['resumed_after_calls']=attempts
 started=time.monotonic()
 def call(task):
  payload=dict(model=MODEL,messages=task['messages'],temperature=0,reasoning_effort=args.reasoning_effort,max_tokens=args.max_tokens,response_format={'type':'json_object'},stream=False)
  begin=time.monotonic();row={k:v for k,v in task.items() if k!='messages'};row.update(started_utc=stamp(),request=payload,endpoint=ENDPOINT)
  try:
   with requests.Session() as s:
    s.trust_env=False;r=s.post(ENDPOINT,json=payload,headers={'Authorization':'Bearer '+key},timeout=(20,300),allow_redirects=False)
   row['http_status']=r.status_code;row['response_body']=r.json();row['request_id']=r.headers.get('x-request-id')
   if r.status_code!=200:row['error']='HTTP '+str(r.status_code)
   else:
    body=row['response_body'];c=body['choices'][0];raw=c['message'].get('content') or '';row.update(raw=raw,usage=body.get('usage',{}),finish_reason=c.get('finish_reason'))
    text=raw.strip()
    if text.startswith('```'):text='\n'.join(l for l in text.splitlines() if not l.strip().startswith('```'))
    try:obj=json.loads(text)
    except ValueError:obj=None
    dims=['apf','rpf','rae'] if task['kind']=='per_response' else ['ptf_alignment','ptf_direction','ptf_shape']
    scores=scores_with_average(obj,dims,100);row['scores']=scores;row['parse_ok']=scores is not None
    if scores is None:row['error']='invalid_judge_verdict'
  except Exception as exc:row['error']=type(exc).__name__
  row['latency_s']=time.monotonic()-begin;return row
 def pending():
  inputs=[];complete=True
  for source in args.sources:
   path=Path(source)/'responses.jsonl';rs=read_rows(path)
   if len({r['task_id'] for r in rs})!=len(rs):raise ValueError('Duplicate inference record')
   if len(rs)!=args.expected_per_source:complete=False
   inputs.extend(rs)
  tasks=[];groups=defaultdict(list)
  for r in inputs:
   if r.get('error'):continue
   tid=r['probe_id']+'__p'+str(r['phase_idx']);ref=refs[tid];sid='per_response/'+r['trial_id']
   response=r.get('response') or '[empty response — model returned nothing]'
   if sid not in seen:
    tasks.append(dict(judge_id=sid,kind='per_response',model=r['model'],mode=r['mode'],novel=r['novel'],character_slug=r['character_slug'],probe_id=r['probe_id'],phase_idx=r['phase_idx'],input_response_sha256=hashlib.sha256(response.encode()).hexdigest(),messages=single_messages(EvalTrial(**ref),response,scale=100,include_thought=True)))
   groups[r['model'],r['mode'],r['novel'],r['character_slug'],r['probe_id']].append((r,ref,response))
  for (model,mode,novel,char,probe),members in groups.items():
   if {m[0]['phase_idx'] for m in members}!=expected_phases[probe]:continue
   jid='trajectory/'+model+'/'+mode+'/'+probe
   if jid in seen:continue
   members.sort(key=lambda x:x[0]['phase_idx']);first=members[0][1]
   phases=[PhaseRef(phase_idx=r['phase_idx'],phase_label=ref['phase'],gt_action=ref['gt_action'],gt_speech=ref['gt_speech'],gt_thought=ref['gt_thought'],response=response) for r,ref,response in members]
   tasks.append(dict(judge_id=jid,kind='trajectory',model=model,mode=mode,novel=novel,character_slug=char,probe_id=probe,n_phases=len(phases),messages=trajectory_messages(first['scenario'],first['question'],phases,scale=100,include_thought=True)))
  tasks.sort(key=lambda t:hashlib.sha256(t['judge_id'].encode()).hexdigest())
  return tasks,complete,len(inputs)
 try:
  with ThreadPoolExecutor(max_workers=args.workers) as pool,(out/'judgments.jsonl').open('a') as f:
   while True:
    if (out/'STOP').exists():
     meta['stopped_at_checkpoint']=True;break
    tasks,complete,ninputs=pending()
    if not tasks:
     if complete:meta['complete']=True;break
     if time.monotonic()-started>args.max_wait_s:raise TimeoutError('Inference wait timeout')
     time.sleep(5);continue
    if attempts+min(args.workers,len(tasks))>args.budget_calls:raise RuntimeError('Registered API call budget reached')
    results=list(pool.map(call,tasks[:args.workers]));attempts+=len(results)
    fatal=[]
    for r in results:
     f.write(json.dumps(r,ensure_ascii=False)+'\n');seen.add(r['judge_id']);scored+=int(bool(r.get('parse_ok')))
     for k,v in r.get('usage',{}).items():
      if isinstance(v,(int,float)):usage[k]+=v
     if r.get('error') and r['error']!='invalid_judge_verdict':fatal.append(r['error'])
    f.flush();os.fsync(f.fileno())
    status=dict(calls=attempts,valid_scores=scored,input_responses=ninputs,usage=dict(usage),elapsed_s=time.monotonic()-started,last_errors=[r.get('error') for r in results])
    (out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    print(f'judged={attempts} valid={scored} inputs={ninputs} tokens={usage.get("total_tokens",0)} errors={[r.get("error") for r in results]}',flush=True)
    if fatal:raise RuntimeError('Step Plan transport/quota error; fail closed: '+str(fatal))
 finally:
  meta.update(finished_utc=stamp(),wall_s=time.monotonic()-started,calls=attempts,n_valid=scored,usage=dict(usage));(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')

if __name__=='__main__':main()
