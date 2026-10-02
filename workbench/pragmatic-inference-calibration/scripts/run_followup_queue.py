#!/usr/bin/env python3
"""Independent GPU queues: no overlap, bounded waits, immutable run directories."""
import fcntl
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path('/data1/xiangding/work/pragmatic-inference-calibration')
PYTHON = '/data1/xiangding/env/pragmatic-inference-calibration/bin/python'
NATIVE = 'workbench/pragmatic-inference-calibration/scripts/run_native_readout.py'
Q25 = ('Qwen2.5-3B-Instruct','Qwen/Qwen2.5-3B-Instruct','aa8e72537993ba99e69dfaafa59ed015b17504d1')
Q3 = ('Qwen3-4B','Qwen/Qwen3-4B','1cfa9a7208912126459214e8b04321603b3df60c')
Q14 = ('Qwen1.5-14B-Chat','Qwen/Qwen1.5-14B-Chat','9492b22871f43e975435455f5c616c77fe7a50ec')
T5 = ('flan-t5-xl','google/flan-t5-xl','7d6315df2c2fb742f0f5b556879d730926ca9001')

def completed(name):
    folder = ROOT/'runs'/name
    p = folder/'config.json'
    if not p.exists():return False
    d=json.loads(p.read_text())
    if 'numerical_gate_pass' in d and not d['numerical_gate_pass']:
        raise RuntimeError('Prior run numerical gate failed: '+name)
    # Older native runs write wall_seconds only after predictions and summary.
    # Read their existing completion contract without rewriting historical configs.
    if not (d.get('complete') or 'wall_seconds' in d):return False
    predictions=folder/'predictions.jsonl'
    if not predictions.exists() or not (folder/'summary.json').exists():return False
    with predictions.open() as f:n=sum(1 for _ in f)
    return n==d.get('n')

def wait_run(name):
    for _ in range(2880):
        if completed(name):return
        time.sleep(5)
    raise TimeoutError('Prior run did not finish: '+name)

def launch(gpu, model, task, name, readout='bare'):
    checkpoint,mid,sha=model
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    command=[PYTHON,NATIVE,'--task',task,'--root',str(ROOT),'--model',str(ROOT/'models'/checkpoint),
             '--model-id',mid,'--revision',sha,'--dtype','float32','--output',str(ROOT/'runs'/name),'--batch-size','8']
    if task=='hu':command+=['--numerical-gate','--hu-readout',readout]
    if task=='hu' and checkpoint!='flan-t5-xl':command+=['--no-special-tokens']
    if checkpoint=='flan-t5-xl':command+=['--slow-tokenizer']
    lockdir=ROOT/'gpu-locks';lockdir.mkdir(exist_ok=True)
    with (lockdir/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if completed(name):
            print(json.dumps({'already_complete':name}),flush=True)
            return
        if (ROOT/'runs'/name).exists():
            raise RuntimeError('Incomplete run must be audited before restart: '+name)
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'exit':code}),flush=True)
        if code:raise RuntimeError('Failed run: '+name)

def followup(entry):
    gpu,prior,model,task,name,readout=entry
    wait_run(prior)
    launch(gpu,model,task,name,readout)
    if gpu==3:
        launch(3,Q14,'wavelength','E15-wavelength-Qwen1.5-14B-Chat')
        launch(3,Q14,'hu','E16-hu-Qwen1.5-14B-Chat-chat','chat')

def stage(entry):
    gpu,model,prior=entry
    wait_run(prior)
    marker=ROOT/'models'/model[0]/'DOWNLOAD_COMPLETE.json'
    for _ in range(2880):
        if marker.exists():break
        time.sleep(5)
    else:raise TimeoutError('Stage download incomplete: '+model[0])
    launch(gpu,model,'hu','E12-hu-'+model[0])
    launch(gpu,model,'hu','E16-hu-'+model[0]+'-chat','chat')

def main():
    entries=[(3,'E14-Qwen2.5-3B-Instruct-chinese',Q14,'hu','E15-hu-Qwen1.5-14B-Chat','bare'),
             (5,'E14-Qwen3-4B-german',Q3,'hu','E16-hu-Qwen3-4B-chat','chat'),
             (6,'E14-Qwen3-4B-korean',Q25,'hu','E16-hu-Qwen2.5-3B-Instruct-chat','chat'),
             (7,'E14-Qwen3-4B-chinese',T5,'hu','E16-hu-flan-t5-xl-format','format')]
    manifest=json.loads((ROOT/'models/olmoe-stage-manifest.json').read_text())
    stage_entries=[(gpu,(m['id'].split('/')[-1],m['id'],m['sha']),prior) for gpu,m,prior in zip([5,6,7],manifest,
                   ['E16-hu-Qwen3-4B-chat','E16-hu-Qwen2.5-3B-Instruct-chat','E16-hu-flan-t5-xl-format'])]
    with ThreadPoolExecutor(max_workers=7) as pool:
        futures=[pool.submit(followup,e) for e in entries]+[pool.submit(stage,e) for e in stage_entries]
        for f in futures:f.result()

if __name__=='__main__':main()
