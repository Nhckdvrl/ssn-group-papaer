#!/usr/bin/env python3
import fcntl,json,os,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON,Q25,Q3,Q14,T5
from run_qwen_stage_queue import BASE

def run(gpu,m):
 cp,mid,sha=m;name='E29-r2-knowledge-'+cp;env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
  print(json.dumps({'start':name,'gpu':gpu}),flush=True)
  cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_knowledge_controls.py','--root',str(ROOT),'--model',str(ROOT/'models'/cp),'--model-id',mid,'--revision',sha,'--output',str(ROOT/'runs'/name)]
  with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
  print(json.dumps({'done':name,'exit':code,'gpu':gpu}),flush=True);return code
models=[BASE,Q25,Q3,Q14]+[(m['id'].split('/')[-1],m['id'],m['sha']) for m in json.loads((ROOT/'models/olmoe-stage-manifest.json').read_text())]+[T5]
with ThreadPoolExecutor(max_workers=8) as ex:codes=list(ex.map(lambda e:run(*e),enumerate(models)))
raise SystemExit(any(codes))
