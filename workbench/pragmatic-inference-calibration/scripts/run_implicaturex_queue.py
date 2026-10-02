#!/usr/bin/env python3
"""Eight independent E21 shards following E20; immutable outputs."""
import fcntl
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from run_followup_queue import ROOT,PYTHON,Q25,Q3,Q14,T5,wait_run
from run_betting_queue import GPT2

def run(entry):
    gpu,model,shard,parts,prior=entry
    if prior:wait_run(prior)
    checkpoint,mid,sha=model
    name=f'E21-{checkpoint}-shard{shard}of{parts}'
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        assert not (ROOT/'runs'/name).exists()
        with (ROOT/(name+'.log')).open('w') as log:
            code=subprocess.run([PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_implicaturex.py',
                 '--root',str(ROOT),'--model',str(ROOT/'models'/checkpoint),'--model-id',mid,'--revision',sha,
                 '--shard',str(shard),'--n-shards',str(parts),'--output',str(ROOT/'runs'/name)],
                 env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        return name,code

def main():
    entries=[(gpu,m,s,2,f'E20-{m[0]}-items{lo:02}-{hi:02}')
             for gpu,m,s,lo,hi in [(0,Q25,0,1,20),(1,Q25,1,21,40),(2,Q3,0,1,20),(3,Q3,1,21,40),
                                  (4,Q14,0,1,20),(5,Q14,1,21,40)]]
    entries += [(6,T5,0,1,'E20-flan-t5-xl-all'),(7,GPT2,0,1,'E20-gpt2-all')]
    entries += [(gpu,(m['id'].split('/')[-1],m['id'],m['sha']),0,1,'E20-'+m['id'].split('/')[-1]+'-all')
                for gpu,m in zip([5,6,7],json.loads((ROOT/'models/olmoe-stage-manifest.json').read_text()))]
    failed=[]
    with ThreadPoolExecutor(max_workers=11) as pool:
        futures=[pool.submit(run,e) for e in entries]
        for f in as_completed(futures):
            try:
                name,code=f.result()
                if code:failed.append(name)
            except Exception as e:
                failed.append(str(e));print(json.dumps({'queue_failure':str(e)}),flush=True)
    print(json.dumps({'failed':failed}),flush=True)
    raise SystemExit(bool(failed))

if __name__=='__main__':main()
