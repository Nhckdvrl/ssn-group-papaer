#!/usr/bin/env python3
"""E22 matched Qwen Base/Instruct queues, finite prerequisites."""
import fcntl
import hashlib
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from run_followup_queue import ROOT,PYTHON,Q25

BASE=('Qwen2.5-3B','Qwen/Qwen2.5-3B','3aab1f1954e9cc14eb9509a215f9e5ca08227a9b')

def wait_assets(model):
    marker=ROOT/'models'/model[0]/'DOWNLOAD_COMPLETE.json'
    for _ in range(2880):
        if marker.exists():return
        time.sleep(5)
    raise TimeoutError(str(marker))

def run(gpu,model):
    wait_assets(model)
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    checkpoint,mid,sha=model
    specs=[]
    for interface in ['bare','chat']:
        name='E22-hu-'+checkpoint+'-'+interface
        specs.append((name,[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_hu_stage.py',
             '--task','hu','--root',str(ROOT),'--model',str(ROOT/'models'/checkpoint),
             '--model-id',mid,'--revision',sha,'--dtype','float32','--no-special-tokens',
             '--numerical-gate','--batch-size','8','--hu-readout',interface,
             '--common-template',str(ROOT/'models/Qwen2.5-3B-Instruct'),'--output',str(ROOT/'runs'/name)]))
    for interface in ['bare','common-chat']:
        # E21 already measures this exact Instruct chat protocol. Reuse only with
        # per-item token/prompt checks in the final comparison, not a new replicate.
        if checkpoint==Q25[0] and interface=='common-chat':continue
        name='E22-implicaturex-'+checkpoint+'-'+interface
        specs.append((name,[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_implicaturex_stage.py',
               '--root',str(ROOT),'--model',str(ROOT/'models'/checkpoint),'--model-id',mid,
               '--revision',sha,'--interface',interface,'--output',str(ROOT/'runs'/name)]))
    for name,command in specs:
        with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            assert not (ROOT/'runs'/name).exists()
            print(json.dumps({'start':name,'gpu':gpu}),flush=True)
            with (ROOT/(name+'.log')).open('w') as log:
                code=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
            print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
            if code:raise RuntimeError(name)

def main():
    # Compare exact tokenizer assets before entering any stage interpretation.
    # Instruct can start while Base downloads; the final join must check token IDs.
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(run,0,BASE),pool.submit(run,1,Q25)]
        failures=[]
        for f in as_completed(futures):
            try:f.result()
            except Exception as e:
                failures.append(str(e));print(json.dumps({'failure':str(e)}),flush=True)
    raise SystemExit(bool(failures))

if __name__=='__main__':main()
