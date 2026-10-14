#!/usr/bin/env python3
"""Resume the two stopped Gemma cohorts on individually checked idle GPUs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

def main():
    cache=Path('/home/xiang/.cache/game-npc-research')
    jobs=[{'gpu':2,'source':'e50_gemma_coherent_pilot_v2','out':'e50_gemma_coherent_pilot_resume','seeds':[5002,5003]},
          {'gpu':3,'source':'e50_gemma_cross_pilot_v2','out':'e50_gemma_cross_pilot_resume','seeds':[5001]}]
    states=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used','--format=csv,noheader,nounits'],text=True)
    mem={int(x.split(',')[0]):int(x.split(',')[1]) for x in states.splitlines()}
    assert all(mem[j['gpu']]<1000 for j in jobs),mem
    handles=[]
    for j in jobs:
        assert not(cache/'runs'/j['out']).exists()
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(j['gpu']),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
                 VLLM_USE_FLASHINFER_SAMPLER='0',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1',
                 PYTHONPATH=str(cache/'e50-legacy-renderer')+':'+str(cache/'deps'))
        env['PATH']='/home/xiang/miniconda3/envs/fgvd/bin:/usr/local/cuda/bin:/usr/bin:/bin'
        stream=(cache/'runs'/(j['out']+'.worker.log')).open('x')
        cmd=[sys.executable,'workbench/game-npc-agents/scripts/commitment_decisions_resume.py',
             '--source',str(cache/'runs'/j['source']),'--out',str(cache/'runs'/j['out']),
             '--seeds',*[str(s) for s in j['seeds']]]
        p=subprocess.Popen(cmd,cwd='/home/xiang/ssn-group-papaer',env=env,stdout=stream,stderr=subprocess.STDOUT)
        handles.append((j,p,stream));print(json.dumps({'pid':p.pid,**j}),flush=True)
    exits={}
    while len(exits)<len(handles):
        for j,p,stream in handles:
            if j['out'] not in exits and p.poll() is not None:
                exits[j['out']]=p.returncode;stream.close()
                print(json.dumps({'out':j['out'],'exit_code':p.returncode}),flush=True)
        if len(exits)<len(handles):time.sleep(10)
    (cache/'runs/e50_gemma_resume_exits.json').write_text(json.dumps(exits,indent=2)+'\n')
    assert all(x==0 for x in exits.values()),exits

if __name__=='__main__':main()
