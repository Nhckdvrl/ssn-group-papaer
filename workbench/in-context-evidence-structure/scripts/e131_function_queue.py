"""Operational stage handoff; fixed science, isolated outputs and continuous fence."""
import argparse, datetime, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
BASE=ROOT/'results/e131'
DEST=BASE/'llama70_confirmation_function'
FENCE=DEST/'behavior.jsonl'
CLAIM=BASE/'.llama70_confirmation_function_stage_claim.json'
MODEL='/tmp/ices_models/Llama-3.1-70B'
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def reserve(parent, worker):
 assert os.uname().nodename=='fvcrc10'
 expected=['/home/xiang/miniconda3/envs/verl-clean/bin/python','scripts/e131_protocol.py','--family','llama70','--model',MODEL,'--phases','confirmation']
 assert [x.decode() for x in Path(f'/proc/{worker}/cmdline').read_bytes().split(b'\0')[:-1]]==expected
 assert str(worker) in Path(f'/proc/{parent}/task/{parent}/children').read_text().split()
 assert json.loads((BASE/'.llama70_confirmation_launch_claim.json').read_text())['queue_pid']==parent
 assert CLAIM.exists()
 os.kill(worker,signal.SIGSTOP)
 try:
  deadline=time.monotonic()+10
  while 'State:\tT' not in Path(f'/proc/{worker}/status').read_text():
   assert time.monotonic()<deadline
   time.sleep(.02)
  # Its sequential native stage is unfinished, so function's guard cannot have passed.
  assert not (BASE/'llama70_confirmation_native/run.json').exists()
  assert not (DEST/'operational_launch.json').exists() and not FENCE.exists()
  DEST.mkdir(parents=True,exist_ok=True)
  fd=os.open(FENCE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600); os.close(fd)
  (DEST/'operational_handoff.json').write_text(json.dumps({'created_at_utc':utc(),'legacy_host':'fvcrc10','legacy_parent_pid':parent,'legacy_worker_pid':worker,'fence':str(FENCE),'fence_scientific_rows':0,'new_execution_root':str(BASE/'function_parallel_execution'),'scope':'Scheduling only; continuous canonical fence blocks legacy function guard.'},indent=2)+'\n')
 finally: os.kill(worker,signal.SIGCONT)
 print('Owned worker resumed; continuous canonical fence installed',flush=True)
def launch(parent,worker,resume=False):
 host=os.uname().nodename; assert host=='fvcrc13'
 info=json.loads((BASE/f'model_identity_llama70_{host}.json').read_text())
 assert info['family']=='llama70' and info['repo']=='NousResearch/Meta-Llama-3.1-70B'
 assert info['revision']=='beb678ba5bd7eb1aafeffa01e2a2b3b5e93d1dd3'
 assert info['host']==host and info['target']==MODEL
 assert info['all_weights_sha256_passed'] and info['official_mirror_all30_match']
 rows=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()
 assert len(rows)==4 and all(float(r.split(',')[1])<128 and float(r.split(',')[2])==0 for r in rows)
 if resume:
  old=json.loads(CLAIM.read_text())
  assert old['host']==host and not Path(f"/proc/{old['pid']}").exists()
  assert FENCE.exists() and FENCE.stat().st_size==0
  assert not (BASE/'function_parallel_execution').exists()
  assert json.loads((DEST/'operational_handoff.json').read_text())['legacy_worker_pid']==worker
  old.update(worker_exit_code=1,error='0-GPU initialization failure: remote fence had not yet become visible through NFS negative caching',finished_at_utc=utc(),scientific_rows=0)
  (BASE/'function_queue_attempt_1_2026-10-12.json').write_text(json.dumps(old,indent=2)+'\n')
 else:
  assert not FENCE.exists()
 fd=os.open(CLAIM,os.O_CREAT|os.O_WRONLY|(os.O_TRUNC if resume else os.O_EXCL),0o600)
 record={'host':host,'pid':os.getpid(),'stage':'function','phase':'confirmation','seed':131103,'n':32,'conditions':85,'started_at_utc':utc(),'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scientific_protocol_changed':False,'isolated_output_publication':True}
 with os.fdopen(fd,'w') as f: json.dump(record,f,indent=2);f.write('\n')
 if not resume:
  subprocess.run(['ssh','-o','LogLevel=ERROR','-o','IdentityAgent=none','-o','ProxyCommand=none','-o','BatchMode=yes','-o','ConnectTimeout=7','fvcrc10',f'cd {ROOT} && python3 scripts/e131_function_queue.py --reserve --legacy-parent {parent} --legacy-worker {worker}'],check=True)
 deadline=time.monotonic()+60
 while not FENCE.exists():
  assert time.monotonic()<deadline
  time.sleep(.5)
 assert FENCE.stat().st_size==0
 stage_root=BASE/'function_parallel_execution'; stage_base=stage_root/'results/e131'
 stage_base.mkdir(parents=True,exist_ok=False)
 (stage_root/'scripts').symlink_to(ROOT/'scripts',target_is_directory=True)
 for name in ['engine_parent_manifest.json','independent_pre_score_review_2026-10-12.json',f'model_identity_llama70_{host}.json','preflight_llama70_confirmation_function','llama70_discovery_function']:
  (stage_base/name).symlink_to(BASE/name,target_is_directory=(BASE/name).is_dir())
 os.environ.update(CUDA_VISIBLE_DEVICES='0,1,2,3',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='6',HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1')
 import e131_protocol as protocol
 assert protocol.STAGES['function']=={'conditions':85,'discovery_seed':123001,'confirmation_seed':131103}
 protocol.STAGES={'function':protocol.STAGES['function']}; protocol.ROOT=stage_root
 def journal(args,resident,label,complete,error=None):
  now=time.time()
  (BASE/'worker_llama70_confirmation_function_parallel.json').write_text(json.dumps({'family':args.family,'host':host,'model':args.model,'started_at':resident['started_at'],'last_observed_at':now,'num_devices':resident['num_devices'],'resident_device_hours_so_far':(now-resident['started_at'])/3600*resident['num_devices'],'scope':'Continuous residency of independently scheduled fixed function stage, including loading and analysis.','last_stage':label,'worker_complete':complete,'failed':error is not None,'error':error,'schedule_helper_sha256':record['helper_sha256'],'isolated_execution_root':str(stage_root)},indent=2)+'\n')
 protocol.record_worker=journal
 sys.argv=[str(ROOT/'scripts/e131_protocol.py'),'--family','llama70','--model',MODEL,'--phases','confirmation']
 try:
  protocol.main()
  completed=stage_base/DEST.name
  assert (completed/'run.json').exists()
  assert sum(bool(line.strip()) for line in (completed/'behavior.jsonl').open())==32
  assert FENCE.exists() and FENCE.stat().st_size==0
  # Never remove the fence; replace it with complete raw. Publish run.json last.
  for p in sorted(completed.iterdir(),key=lambda p:p.name=='run.json'):
   assert p.is_file()
   if p.name!='behavior.jsonl': assert not (DEST/p.name).exists()
   os.replace(p,DEST/p.name)
  record.update(worker_exit_code=0,published_at_utc=utc())
 except BaseException as exc:
  record.update(worker_exit_code=1,error=repr(exc));raise
 finally:
  record['finished_at_utc']=utc();CLAIM.write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--reserve',action='store_true');ap.add_argument('--resume-reservation',action='store_true');ap.add_argument('--legacy-parent',type=int,required=True);ap.add_argument('--legacy-worker',type=int,required=True);a=ap.parse_args()
 try:
  if a.reserve: reserve(a.legacy_parent,a.legacy_worker)
  else: launch(a.legacy_parent,a.legacy_worker,a.resume_reservation)
 except BaseException as exc:
  if not a.reserve and CLAIM.exists():
   record=json.loads(CLAIM.read_text())
   if record.get('pid')==os.getpid():
    record.update(worker_exit_code=1,error=repr(exc),finished_at_utc=utc())
    CLAIM.write_text(json.dumps(record,indent=2)+'\n')
  raise
