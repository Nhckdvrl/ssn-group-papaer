import fcntl,json,os,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON
def run(shard):
    name=f'E37-flan-circa-shard{shard}of4';env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(shard)
    with (ROOT/'gpu-locks'/f'{shard}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
        print(json.dumps({'start':name,'gpu':shard}),flush=True)
        cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_flan_circa.py','--root',str(ROOT),'--shard',str(shard),'--output',str(ROOT/'runs'/name)]
        with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'exit':code}),flush=True)
        if code:raise RuntimeError(name)
with ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(run,range(4)))
