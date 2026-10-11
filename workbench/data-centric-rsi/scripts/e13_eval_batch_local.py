"""Evaluate all six E13 endpoints locally on fvcrc13, reusing exact E12 assets.

Run the coordinator on fvcrc13 only after review. Helper modes execute on the
training/judge nodes; no helper imports torch or modifies any environment.
"""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.metadata, json, os, pathlib
import shlex, shutil, signal, socket, subprocess, time, urllib.request, uuid

ROOT = pathlib.Path('/var/tmp/xiang-data-rsi/e13')
E12 = pathlib.Path('/var/tmp/xiang-data-rsi/e12')
REPO = pathlib.Path('/home/xiang/ssn-group-papaer')
SELF = pathlib.Path(__file__).resolve()
VENDOR = pathlib.Path('/home/xiang/.cache/research/data-centric-rsi/CurationBench')
TRAIN_PYTHON = '/home/xiang/.venvs/data-centric-rsi/bin/python'
JUDGE_PYTHON = '/home/xiang/.venvs/vllm023-cu128/bin/python'
JUDGE_MODEL = '/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-27B/snapshots/fc05daec18b0a78c049392ed2e771dde82bdf654'
URL = 'http://fvcrc20:8032'
RUNS = [f'{p}_{a}_s29' for a in ('replay','fresh_selected','fresh_law') for p in ('init','used')]
BENCHMARKS = ('HallusionBench','LLaVABench','MMBench','MMMU_DEV_VAL','MMStar','MMVet','MathVista_MINI','OCRBench')
FROZEN_MD5 = ('0c23ac0dc9ef46832d7a24504f2a0c7c','d382a093f749a697820d3dadd61c8428','4115aea3383f3dd0083be6a633e0f820','585e8ad75e73f75dcad265dfd0417d64','e1ecd2140806c1b1bbf54b43372efb9e','748aa6d4aa9d4de798306a63718455e3','f199b98e178e5a2a20e7048f5dcb0464','e953d98a987cc6e26ef717b61260b778')
FROZEN_SOURCE = {
 'workbench/data-centric-rsi/scripts/e12_run_eval.py':'20c9eebb084f544d03ad1a32ccf0c9b28efe2d05640c6e85993da213a721e809',
 'workbench/data-centric-rsi/scripts/e12_validate_eval.py':'2f0f1796a3d7662ee53580504a0eab081e901aa3977bb87e2cbccd38db340601',
 'workbench/data-centric-rsi/compat/sitecustomize.py':'ca25d45f14240a586685815d9b34d2790799f6393aebf6cae82dd4a472d7c469',
}
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(pathlib.Path(p).read_text())
def write(p,d): pathlib.Path(p).write_text(json.dumps(d,indent=2)+'\n')
def digest(p,algorithm='sha256'):
 h=hashlib.new(algorithm)
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def remote(node,*args,python='python3'):
 return json.loads(subprocess.check_output(['ssh',node,shlex.join([python,str(SELF),*args])],text=True))
def files(directory):
 return [{'path':str(p.relative_to(directory)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(directory.rglob('*')) if p.is_file()]
def gpu_available(gpu,minimum):
 rows=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines()
 row=next(x for x in rows if int(x.split(',')[0])==gpu)
 _,uuid,free=[x.strip() for x in row.split(',')]
 apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
 return int(free)>=minimum and uuid not in apps
def environment():
 assert subprocess.check_output(['git','-C',str(VENDOR),'rev-parse','HEAD'],text=True).strip()=='24eea1526492c00cee421f5db0793789e00aabb2'
 subprocess.run(['git','-C',str(VENDOR),'diff','--exit-code','--quiet'],check=True)
 task=VENDOR/'src/benchmark/tasks/llava665k_llava_8bench_10k_unlimited.yaml'
 assert digest(task)=='df20fa6f3146ddf6b80c81b651ca0506aa11c65ae9e12cb3a19a240c8bc69590'
 for p,s in FROZEN_SOURCE.items():assert digest(REPO/p)==s,p
 freeze=subprocess.check_output(['/home/xiang/.local/bin/uv','pip','freeze','--python',str(E12/'vlmeval_venv/bin/python')])
 assert hashlib.sha256(freeze).hexdigest()=='8ef6b4ec11c6d563e990ad7a2a3eebb9ac67d3c735792a769bcf86c450da9f40'
 md5={b:digest(E12/'LMUData'/f'{b}.tsv','md5') for b in BENCHMARKS}
 assert list(md5.values())==list(FROZEN_MD5)
 return {'utc':utc(),'node':socket.gethostname(),'vendor_sha':'24eea1526492c00cee421f5db0793789e00aabb2','task_sha256':digest(task),'source_sha256':FROZEN_SOURCE,'eval_pip_freeze_sha256':hashlib.sha256(freeze).hexdigest(),'TSV_MD5':md5}
def train_status():
 runs={}
 for name in RUNS:
  p=ROOT/'train_runs'/name
  if (p/'completion.json').exists():
   c=read(p/'completion.json');c['runtime']=read(p/'runtime_manifest.json') if (p/'runtime_manifest.json').exists() else None
   c['trace_rows']=len((p/'window_trace.jsonl').read_text().splitlines()) if (p/'window_trace.jsonl').exists() else 0
   runs[name]=c
 queues=[read(ROOT/'train_queue'/f'gpu{i}.json') for i in range(4)]
 failures=[e for q in queues for e in q['runs'] if e.get('returncode',0)!=0]
 return {'utc':utc(),'runs':runs,'queues':queues,'queue_failures':failures,'budget':read(ROOT/'train_queue/budget_watch.json')}
def metrics():
 raw=urllib.request.urlopen(URL+'/metrics',timeout=30).read().decode()
 wanted=('vllm:num_requests_running{','vllm:num_requests_waiting{','vllm:prompt_tokens_total{','vllm:generation_tokens_total{','vllm:request_success_total{')
 values={line.split()[0]:float(line.split()[1]) for line in raw.splitlines() if line.startswith(wanted) and len(line.split())==2}
 assert any(k.startswith(wanted[0]) for k in values) and any(k.startswith(wanted[1]) for k in values),'Required pending-request metrics absent'
 return raw,values
def pending(values):return sum(v for k,v in values.items() if k.startswith(('vllm:num_requests_running{','vllm:num_requests_waiting{')))
def judge_start(owner_token):
 assert socket.gethostname().startswith('fvcrc20')
 vllm_version_full=importlib.metadata.version('vllm')
 vllm_version_base=vllm_version_full.split('+',1)[0]
 assert vllm_version_full=='0.23.0+cu129' and vllm_version_base=='0.23.0'
 assert gpu_available(0,80000)
 with socket.socket() as port:
  port.settimeout(3);assert port.connect_ex(('127.0.0.1',8032))!=0,'8032 already hosts another service'
 d=ROOT/'judge';d.mkdir(parents=True,exist_ok=False)
 command=[JUDGE_PYTHON,'-m','vllm.entrypoints.openai.api_server','--model',JUDGE_MODEL,'--served-model-name','Qwen3.5-27B','--host','0.0.0.0','--port','8032','--dtype','bfloat16','--max-model-len','4096','--max-num-seqs','16','--gpu-memory-utilization','0.78','--default-chat-template-kwargs','{"enable_thinking":false}']
 env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='0',CUDA_DEVICE_ORDER='PCI_BUS_ID',VLLM_USE_FLASHINFER_SAMPLER='0')
 with (d/'server.log').open('w') as log:p=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 record={'owner_token':owner_token,'started_utc':utc(),'pid':p.pid,'start_ticks':pathlib.Path(f'/proc/{p.pid}/stat').read_text().split()[21],'process_group':p.pid,'command':command,'environment':{k:env[k] for k in ('CUDA_VISIBLE_DEVICES','CUDA_DEVICE_ORDER','VLLM_USE_FLASHINFER_SAMPLER')},'vllm_version_full':vllm_version_full,'vllm_version_base':vllm_version_base,'gpu_type':'Blackwell','gpu':0,'active_gpu_time':'unmeasured'}
 try:write(d/'launch_manifest.json',record)
 except Exception:
  os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=60);raise
 return record
def judge_owned(owner_token):
 p=ROOT/'judge/launch_manifest.json'
 return p.exists() and read(p).get('owner_token')==owner_token
def judge_stop(owner_token,failure=False):
 d=ROOT/'judge';m=read(d/'launch_manifest.json')
 assert m.get('owner_token')==owner_token,'Judge launch belongs to another batch'
 p=m['pid'];stat=pathlib.Path(f'/proc/{p}/stat');already_exited=not stat.exists()
 reused=stat.exists() and stat.read_text().split()[21]!=m['start_ticks']
 owned_server_alive=stat.exists() and not reused
 try:
  assert not reused,'Old server PID has been reused; do not inspect the replacement service'
  raw,values=metrics();assert pending(values)==0 or failure,'Judge still has pending requests'
  (d/'metrics_final.prom').write_text(raw);metric_error=None
 except Exception as error:
  if not failure and owned_server_alive:raise
  values={};metric_error=str(error)
 owned=[] if reused else [int(line.split()[0]) for line in subprocess.check_output(['ps','-eo','pid=,pgid='],text=True).splitlines() if int(line.split()[1])==m['process_group']]
 snapshot={'snapshot_utc':utc(),'launch_manifest':m,'metrics':values,'pending_requests':pending(values) if values else None,'metrics_error':metric_error,'failure_cleanup':failure,'server_already_exited':already_exited,'server_pid_reused_no_kill':reused,'owned_process_group_pids':owned,'server_residency_seconds_upper_bound':(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(m['started_utc'])).total_seconds(),'active_gpu_time':'unmeasured','not_A100_converted':True}
 write(d/'cost_snapshot_final.json',snapshot)
 if owned_server_alive:os.kill(p,signal.SIGTERM)
 for _ in range(30):
  if not pathlib.Path(f'/proc/{p}').exists():break
  time.sleep(1)
 remaining=[] if reused else [int(line.split()[0]) for line in subprocess.check_output(['ps','-eo','pid=,pgid='],text=True).splitlines() if int(line.split()[1])==m['process_group']]
 if remaining:
  try:os.killpg(m['process_group'],signal.SIGTERM)
  except ProcessLookupError:pass
  time.sleep(5)
 snapshot['stop_requested_utc']=utc();snapshot['remaining_owned_pids']=[pid for pid in owned if pathlib.Path(f'/proc/{pid}').exists()]
 snapshot['gpu_after_stop']=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()
 with socket.socket() as port:
  port.settimeout(3);snapshot['endpoint_port_closed']=port.connect_ex(('127.0.0.1',8032))!=0
 write(d/'cost_snapshot_final.json',snapshot);return snapshot
def smoke():
 models=json.load(urllib.request.urlopen(URL+'/v1/models',timeout=30));assert [x['id'] for x in models['data']]==['Qwen3.5-27B']
 payload={'model':'Qwen3.5-27B','messages':[{'role':'user','content':'Reply only OK'}],'temperature':0,'max_tokens':8,'chat_template_kwargs':{'enable_thinking':False}}
 req=urllib.request.Request(URL+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 d=json.load(urllib.request.urlopen(req,timeout=30));assert d['choices'][0]['message']['content'].strip()=='OK'
def batch():
 assert socket.gethostname().startswith('fvcrc13')
 d=ROOT/'eval_batch_local';d.mkdir(exist_ok=False);state={'started_utc':utc(),'runs':[],'copies':[],'status':'waiting_training','checkpoint_copy_required':False,'student_node':'fvcrc13','student_gpu':0,'judge_node':'fvcrc20','judge_gpu':0}
 write(d/'state.json',state)
 while True:
  status=train_status();write(d/'training_status.json',status)
  assert not status['queue_failures'] and status['budget']['status'] not in ('cap_reached_own_queues_terminated','queues_exited_incomplete'),'Training queue failed; do not evaluate partial survivors'
  if len(status['runs'])==6 and all(q.get('status')=='completed' for q in status['queues']):break
  time.sleep(30)
 for name,c in status['runs'].items():
  assert c['returncode']==0 and c['model_saved'] and c['observed_windows']==625 and c['trace_rows']==625,name
  r=c['runtime'];assert r['model_accepts_loss_kwargs'] and r['accelerator_gradient_accumulation_steps']==1 and r['trainer_gradient_accumulation_steps']==16 and r['initial_global_step']==0 and r['optimizer_initially_none'] and r['lr_scheduler_initially_none'],name
 completion_wall=sum(c['wall_seconds'] for c in status['runs'].values())
 queue_entries=[e for q in status['queues'] for e in q['runs']]
 assert len(queue_entries)==6 and {pathlib.Path(e['run_dir']).name for e in queue_entries}==set(RUNS)
 assert all(e['returncode']==0 and e['queue_wrapper_wall_seconds']>=0 for e in queue_entries)
 train_wall=sum(e['queue_wrapper_wall_seconds'] for e in queue_entries)
 state.update(successful_train_wrapper_seconds=completion_wall,
              train_queue_wrapper_seconds=train_wall,
              train_preflight_and_outer_wrapper_seconds=train_wall-completion_wall,
              A100_budget_training_cost_source='Sum of all six terminal queue_wrapper_wall_seconds; completion.wall_seconds retained separately',
              training_queue_entries=queue_entries)
 assert train_wall<64800
 state['environment']=environment();state['status']='waiting_local_student_gpu';write(d/'state.json',state)
 models={name:ROOT/'train_runs'/name/'model' for name in RUNS}
 for name,path in models.items():
  index=read(path/'model.safetensors.index.json');shards=set(index['weight_map'].values())
  assert len(shards)==3 and all((path/shard).is_file() for shard in shards),name
 state['local_model_paths']={name:str(path) for name,path in models.items()};write(d/'state.json',state)
 while not gpu_available(0,75000):time.sleep(30)
 state['environment_before_judge']=environment();state['status']='judge_starting';write(d/'state.json',state)
 while not remote('fvcrc20','--judge-idle'):time.sleep(30)
 owner_token=uuid.uuid4().hex;state['judge_owner_token']=owner_token;write(d/'state.json',state)
 judge_deadline=time.monotonic()+43200
 try:
  judge=remote('fvcrc20','--judge-start','--owner-token',owner_token,python=JUDGE_PYTHON);state['judge_launch']=judge;write(d/'state.json',state)
  startup_deadline=time.monotonic()+7200
  while True:
   try:smoke();break
   except Exception:
    assert time.monotonic()<startup_deadline,'Judge startup timeout';time.sleep(15)
  spent=0.0
  for name in RUNS:
   while not gpu_available(0,75000):
    assert time.monotonic()<judge_deadline,'Judge residency cap while awaiting A100';time.sleep(30)
   environment();smoke();assert train_wall+spent<64800
   out=ROOT/'eval_runs'/name;assert not out.exists()
   command=[TRAIN_PYTHON,str(REPO/'workbench/data-centric-rsi/scripts/e12_run_eval.py'),'--model',str(models[name]),'--eval-data',str(E12/'LMUData'),'--judge-url',URL+'/v1/chat/completions','--gpu','0','--out',str(out)]
   env=os.environ.copy();env.update(PATH='/home/xiang/.local/bin:'+env.get('PATH',''),UV_PROJECT_ENVIRONMENT=str(E12/'vlmeval_venv'))
   start=time.monotonic();entry={'name':name,'command':command,'out':str(out),'started_utc':utc()};state['runs'].append(entry);state['status']='evaluating';write(d/'state.json',state)
   with (d/f'{name}.stdout').open('w') as stdout,(d/f'{name}.stderr').open('w') as stderr:
    p=subprocess.Popen(command,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True);entry['pid']=p.pid;write(d/'state.json',state)
    while p.poll() is None:
     if train_wall+spent+time.monotonic()-start>=64800 or time.monotonic()>=judge_deadline:
      os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=60);entry['cap_terminated']=True;write(d/'state.json',state);raise RuntimeError('Allocation cap reached; owned eval terminated')
     time.sleep(10)
   elapsed=time.monotonic()-start;spent+=elapsed;entry.update(returncode=p.returncode,driver_wrapper_wall_seconds=round(elapsed,3));write(d/'state.json',state)
   assert p.returncode==0,name
   completion=read(out/'completion.json');assert completion['status']=='completed' and completion.get('error') is None
   import sys
   sys.path.insert(0,str(REPO/'workbench/data-centric-rsi/scripts'))
   from e12_validate_eval import validate_results
   scores=validate_results(read(out/'results/results.json'));saved=read(out/'validated_scores.json')
   assert scores['accuracy_percent']==saved['accuracy_percent'] and scores['benchmarks']==saved['benchmarks']
   entry['completion']=completion;entry['validated_scores']=saved;write(d/'state.json',state)
   small_results=REPO/'workbench/data-centric-rsi/results'
   for suffix,source in [('raw_results',out/'results/results.json'),('validated_scores',out/'validated_scores.json'),('eval_manifest',out/'eval_manifest.json'),('completion',out/'completion.json')]:
    destination=small_results/f'E13_{name}_{suffix}.json';assert not destination.exists();shutil.copyfile(source,destination)
  state['status']='six_evaluations_completed';write(d/'state.json',state)
 except Exception as error:
  state.update(status='failed',error=str(error));write(d/'state.json',state);raise
 finally:
  owned=remote('fvcrc20','--judge-owned','--owner-token',owner_token)
  while owned:
   try:
    raw,values=metrics()
    if pending(values)==0:state['judge_cleanup']=remote('fvcrc20','--judge-stop','--owner-token',owner_token,python=JUDGE_PYTHON);break
   except Exception as error:
    state['cleanup_error']=str(error);state['judge_cleanup']=remote('fvcrc20','--judge-stop-after-failure','--owner-token',owner_token,python=JUDGE_PYTHON);write(d/'state.json',state);break
   if time.monotonic()>=judge_deadline:
    state['cleanup_error']='Judge requests did not drain before residency cap';state['judge_cleanup']=remote('fvcrc20','--judge-stop-after-failure','--owner-token',owner_token,python=JUDGE_PYTHON);write(d/'state.json',state);break
   time.sleep(10)
  state['finished_utc']=utc();write(d/'state.json',state)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--train-status',action='store_true');p.add_argument('--hash-model',type=pathlib.Path);p.add_argument('--environment',action='store_true');p.add_argument('--judge-idle',action='store_true');p.add_argument('--judge-start',action='store_true');p.add_argument('--judge-stop',action='store_true');p.add_argument('--judge-stop-after-failure',action='store_true');p.add_argument('--judge-owned',action='store_true');p.add_argument('--owner-token');p.add_argument('--run-batch',action='store_true');a=p.parse_args()
 if a.judge_start or a.judge_stop or a.judge_stop_after_failure or a.judge_owned:assert a.owner_token,'Owner token required for judge lifecycle operations'
 if a.train_status:r=train_status()
 elif a.hash_model:
  start=time.monotonic();index=read(a.hash_model/'model.safetensors.index.json');shards=set(index['weight_map'].values())
  assert len(shards)==3 and all((a.hash_model/shard).is_file() for shard in shards),'Incomplete terminal checkpoint'
  manifest=files(a.hash_model);assert sum(e['bytes'] for e in manifest)>14_000_000_000
  r={'directory':str(a.hash_model),'files':manifest,'utc':utc(),'hash_wall_seconds':round(time.monotonic()-start,3)}
 elif a.environment:r=environment()
 elif a.judge_idle:r=gpu_available(0,80000)
 elif a.judge_start:r=judge_start(a.owner_token)
 elif a.judge_stop:r=judge_stop(a.owner_token)
 elif a.judge_stop_after_failure:r=judge_stop(a.owner_token,failure=True)
 elif a.judge_owned:r=judge_owned(a.owner_token)
 elif a.run_batch:batch();return
 else:p.error('Select one operation')
 print(json.dumps(r))
if __name__=='__main__':main()
