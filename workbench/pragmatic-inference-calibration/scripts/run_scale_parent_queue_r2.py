#!/usr/bin/env python3
"""E28 exact parent contracts at modern larger endpoints; finite asset waits."""
import fcntl,json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON

def download(m):
 cp=m['id'].split('/')[-1]
 with (ROOT/(cp+'-download.log')).open('w') as log:
  code=subprocess.run([PYTHON,'workbench/pragmatic-inference-calibration/scripts/download_models.py','--root',str(ROOT),'--model-id',m['id'],'--revision',m['sha']],stdout=log,stderr=subprocess.STDOUT).returncode
 print(json.dumps({'download':cp,'exit':code}),flush=True)
 if code:raise RuntimeError('download '+cp)

def run(gpu,m,kind):
 cp=m['id'].split('/')[-1];name='E28-'+kind+'-'+cp
 marker=ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json'
 for _ in range(2160):
  if marker.exists():break
  time.sleep(5)
 else:raise TimeoutError(str(marker))
 if kind=='implicaturex':script='run_implicaturex.py';extra=[]
 else:
  script='run_scale_readout.py';extra=['--task','wavelength' if kind=='wavelength' else 'hu','--dtype','float32','--numerical-gate','--batch-size','8']
  if kind.startswith('hu'):extra+=['--no-special-tokens','--hu-readout',kind[3:]]
 cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/'+script,'--root',str(ROOT),'--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],'--output',str(ROOT/'runs'/name)]+extra
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
  print(json.dumps({'start':name,'gpu':gpu}),flush=True)
  with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
  print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
  if code:raise RuntimeError(name)

def main():
 models=json.loads((ROOT/'models/qwen3-scale-manifest.json').read_text());failed=[]
 with ThreadPoolExecutor(max_workers=8) as ex:
  # Existing pinned download subprocesses are retained; no duplicate download.
  fs = [ex.submit(run,4*mi+ki,m,k) for mi,m in enumerate(models) for ki,k in enumerate(['hu-bare','hu-chat','implicaturex','wavelength'])]
  for f in as_completed(fs):
   try:f.result()
   except Exception as e:failed.append(str(e));print(json.dumps({'failure':str(e)}),flush=True)
 print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
if __name__=='__main__':main()
