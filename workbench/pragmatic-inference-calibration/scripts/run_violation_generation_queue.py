"""Eight finite independent stage/source jobs, actual memory checked under locks."""
import fcntl
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from run_followup_queue import ROOT, PYTHON
from violation_data import specs


def run(gpu, m):
    cp=m['id'].split('/')[-1];name='E64-violation-generation-'+cp
    marker=ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json'
    for _ in range(1440):
        if marker.exists():break
        time.sleep(5)
    else:raise TimeoutError('Pinned download missing '+cp)
    assert not (ROOT/'runs'/name).exists()
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        used=int(subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
        assert used<10000, 'Other GPU process under lock; no process terminated'
        cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_violation_generation.py','--root',str(ROOT),
             '--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],
             '--output',str(ROOT/'runs'/name)]
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        with (ROOT/(name+'.log')).open('w') as log:
            code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        if code:raise RuntimeError(name)


if __name__=='__main__':
    pre=json.loads(open('workbench/pragmatic-inference-calibration/results/E64-source-preflight.json').read())
    assert pre['gate_pass'] and pre['models']==specs(ROOT)
    failed=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        fs=[ex.submit(run,i,m) for i,m in enumerate(specs(ROOT))]
        for f in as_completed(fs):
            try:f.result()
            except Exception as e:failed.append(str(e));print(json.dumps({'failure':str(e)}),flush=True)
    print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
