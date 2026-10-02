#!/usr/bin/env python3
"""E20 preassigned shards and bounded, independent stage followups."""
import fcntl
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from run_followup_queue import ROOT, PYTHON, Q25, Q3, Q14, T5, wait_run

SCRIPT = 'workbench/pragmatic-inference-calibration/scripts/run_epitome_betting.py'
GPT2 = ('gpt2','openai-community/gpt2','607a30d783dfa663caf39e06633721c8d4cfcd7e')


def run(entry):
    gpu, model, lo, hi, prior = entry
    if prior:
        wait_run(prior)
    checkpoint, mid, revision = model
    shard = 'all' if (lo,hi)==(1,40) else f'items{lo:02}-{hi:02}'
    name = f'E20-{checkpoint}-{shard}'
    command = [PYTHON,SCRIPT,'--root',str(ROOT),'--model',str(ROOT/'models'/checkpoint),
               '--model-id',mid,'--revision',revision,'--item-min',str(lo),'--item-max',str(hi),
               '--output',str(ROOT/'runs'/name)]
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu)
    with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        assert not (ROOT/'runs'/name).exists(), 'No overwrite of prior runs'
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        with (ROOT/(name+'.log')).open('w') as log:
            code = subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        return name, code


def main():
    entries = [(0,Q25,1,20,None),(1,Q25,21,40,None),
               (2,Q3,1,20,None),(3,Q3,21,40,None),
               (4,Q14,1,20,None),(5,Q14,21,40,None),
               (6,T5,1,40,None),(7,GPT2,1,40,None)]
    stages = json.loads((ROOT/'models/olmoe-stage-manifest.json').read_text())
    entries += [(gpu,(m['id'].split('/')[-1],m['id'],m['sha']),1,40,
                 'E19-'+m['id'].split('/')[-1]+'-r2') for gpu,m in zip([5,6,7],stages)]
    failures = []
    with ThreadPoolExecutor(max_workers=11) as pool:
        futures = [pool.submit(run,e) for e in entries]
        for f in as_completed(futures):
            try:
                name, code = f.result()
                if code:
                    failures.append(name)
            except Exception as exc:
                failures.append(str(exc))
                print(json.dumps({'queue_failure':str(exc)}),flush=True)
    print(json.dumps({'failed':failures}),flush=True)
    raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
