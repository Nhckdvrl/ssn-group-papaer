#!/usr/bin/env python3
"""One SSH handle supervises four pre-registered independent GPU jobs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,required=True);a=ap.parse_args()
    jobs=json.loads(a.manifest.read_text())
    cache=Path('/home/xiang/.cache/game-npc-research')
    paths={'Qwen3.5-27B':'Qwen--Qwen3.5-27B/snapshots/fc05daec18b0a78c049392ed2e771dde82bdf654',
           'Qwen3-32B':'Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137',
           'Gemma3-12B':'google--gemma-3-12b-it/snapshots/96b6f1eccf38110c56df3a15bffe176da04bfd80'}
    states=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used','--format=csv,noheader,nounits'],text=True)
    memory={int(s.split(',')[0]):int(s.split(',')[1]) for s in states.splitlines()}
    assert all(memory[j['gpu']]<1000 for j in jobs), memory
    assert all(not (cache/'runs'/j['out']).exists() for j in jobs), 'Prior output exists; inspect, never overwrite/restart blindly'
    handles=[]
    for j in jobs:
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(j['gpu']),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
                 HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',
                 VLLM_USE_FLASHINFER_SAMPLER='0',PYTHONPATH=str(cache/'deps'))
        env['PATH']='/home/xiang/miniconda3/envs/fgvd/bin:/usr/local/cuda/bin:/usr/bin:/bin'
        log=cache/'runs'/(j['out']+'.worker.log')
        stream=log.open('x')
        cmd=[sys.executable,'workbench/game-npc-agents/scripts/commitment_decisions_v2.py',
             '--dataset',str(cache/'runs/e50_native_snapshots_v1/snapshots.jsonl'),
             '--out',str(cache/'runs'/j['out']),
             '--model',str(Path('/home/xiang/.cache/huggingface/hub')/('models--'+paths[j['model']])),
             '--design',j['design'],'--seeds',*[str(s) for s in j['seeds']]]
        if j.get('controls'):cmd.extend(['--controls',*j['controls']])
        p=subprocess.Popen(cmd,cwd='/home/xiang/ssn-group-papaer',env=env,stdout=stream,stderr=subprocess.STDOUT)
        handles.append((j,p,stream))
        print(json.dumps({'out':j['out'],'gpu':j['gpu'],'pid':p.pid,'log':str(log)}),flush=True)
    exits={}
    while len(exits)<len(handles):
        for j,p,stream in handles:
            if j['out'] not in exits and p.poll() is not None:
                exits[j['out']]=p.returncode;stream.close()
                print(json.dumps({'out':j['out'],'exit_code':p.returncode}),flush=True)
        if len(exits)<len(handles):time.sleep(10)
    dest=a.manifest.with_name('e50_remote_pilot_exits.json')
    dest.write_text(json.dumps(exits,indent=2)+'\n')
    assert all(e==0 for e in exits.values()),exits


if __name__=='__main__':main()
