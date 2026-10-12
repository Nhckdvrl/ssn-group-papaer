"""Operational E131 queue with an atomic launch claim; scientific protocol unchanged."""
import argparse,datetime,json,os,subprocess,time
from pathlib import Path
root=Path('/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure')
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['discovery','confirmation'],required=True);a=p.parse_args()
host=os.uname().nodename;identity=root/'results/e131'/('model_identity_llama70_'+host+'.json')
started=time.time();print(host,a.phase,'waiting for pinned assets and four empty GPUs',flush=True)
while True:
 ready=identity.exists()
 if ready:
  j=json.loads(identity.read_text());ready=j['all_weights_sha256_passed'] and j['target']=='/tmp/ices_models/Llama-3.1-70B'
 if ready and a.phase=='confirmation':
  first=root/'results/e131/llama70_discovery_mechanism/behavior.jsonl';lines=first.read_text().splitlines() if first.exists() else []
  ready=bool(lines) and len(json.loads(lines[0])['conditions'])==43
 if ready:
  rows=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()
  ready=len(rows)==4 and all(float(r.split(',')[1])<128 and float(r.split(',')[2])==0 for r in rows)
 if ready:break
 time.sleep(10)
claim=root/'results/e131'/('.llama70_'+a.phase+'_launch_claim.json')
try:fd=os.open(claim,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
except FileExistsError:
 print('Phase already claimed; no duplicate worker launched:',claim,flush=True);raise SystemExit(0)
record={'host':host,'phase':a.phase,'queue_pid':os.getpid(),'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scientific_protocol_changed':False}
with os.fdopen(fd,'w') as f:json.dump(record,f,indent=2);f.write('\n')
env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='0,1,2,3',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='6',HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1')
print('Starting fixed worker after',round(time.time()-started,1),'seconds',flush=True)
with (root/'results/e131'/('startup_llama70_'+a.phase+'.log')).open('w',buffering=1) as log:
 r=subprocess.run(['/home/xiang/miniconda3/envs/verl-clean/bin/python','scripts/e131_protocol.py','--family','llama70','--model','/tmp/ices_models/Llama-3.1-70B','--phases',a.phase],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
record['worker_exit_code']=r.returncode;record['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();claim.write_text(json.dumps(record,indent=2)+'\n')
raise SystemExit(r.returncode)
