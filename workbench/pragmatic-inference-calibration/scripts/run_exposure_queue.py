"""Eight cached-model jobs; locks coordinate with the E51 pinned-stage queue."""
import fcntl
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from exposure_data import ROOT,specs

PY='/data1/xiangding/env/pragmatic-inference-calibration/bin/python'


def run(index,m):
    cp=m['id'].split('/')[-1];name='E57-exposure-'+cp
    assert not (ROOT/'runs'/name).exists()
    deadline=time.monotonic()+7200
    while time.monotonic()<deadline:
        for gpu in [(index+j)%8 for j in range(8)]:
            lock=(ROOT/'gpu-locks'/f'{gpu}.lock').open('w')
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:lock.close();continue
            used=int(subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
            if used>=10000:lock.close();continue
            env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),OMP_NUM_THREADS='8',TOKENIZERS_PARALLELISM='false')
            print(json.dumps({'start':name,'gpu':gpu}),flush=True)
            with lock,(ROOT/(name+'.log')).open('w') as log:
                code=subprocess.run([PY,'workbench/pragmatic-inference-calibration/scripts/run_exposure.py',
                    '--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],
                    '--output',str(ROOT/'runs'/name)],env=env,stdout=log,stderr=subprocess.STDOUT).returncode
            print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
            if code:raise RuntimeError(name)
            return
        time.sleep(5)
    raise TimeoutError(name)


if __name__=='__main__':
    pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E57-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(ROOT)
    failures=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for f in as_completed([pool.submit(run,i,m) for i,m in enumerate(specs(ROOT))]):
            try:f.result()
            except Exception as e:failures.append(str(e));print(json.dumps({'failure':str(e)}),flush=True)
    print(json.dumps({'failures':failures}),flush=True);raise SystemExit(bool(failures))
