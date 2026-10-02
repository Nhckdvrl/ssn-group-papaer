#!/usr/bin/env python3
import fcntl,json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON
models=json.loads((ROOT/'models/qwen3-scale-manifest.json').read_text())
def run(gpu,m,variant):
 cp=m['id'].split('/')[-1];name=f'E31-knowledge-{cp}-{variant}'
 for _ in range(2160):
  if (ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json').exists():break
  time.sleep(5)
 else:raise TimeoutError(cp)
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
  print(json.dumps({'start':name,'gpu':gpu}),flush=True)
  cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_scale_knowledge_controls.py','--root',str(ROOT),'--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],'--variant',variant,'--output',str(ROOT/'runs'/name)]
  with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
  print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
  if code:raise RuntimeError(name)
failed=[]
with ThreadPoolExecutor(max_workers=8) as ex:
 fs=[ex.submit(run,4*i+j,m,v) for i,m in enumerate(models) for j,v in enumerate(['parent','role','access-only','negative'])]
 for f in as_completed(fs):
  try:f.result()
  except Exception as e:failed.append(str(e));print(json.dumps({'failure':str(e)}),flush=True)
print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
