#!/usr/bin/env python3
"""Use the otherwise idle GPU2 for native interaction; await complete training."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);a=p.parse_args()
    root=Path(a.asset_root);out=root/'runs/D-E11';out.mkdir(exist_ok=True)
    state=dict(complete=False,error=None,systems_completed=[],started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save(): (out/'queue_status.json').write_text(json.dumps(state,indent=2)+'\n')
    if (out/'queue_status.json').exists():raise FileExistsError('Do not replace an existing queue')
    save()
    try:
        for system in ['base','update_sft','multitask_sft']:
            if system!='base':
                mode='update' if system=='update_sft' else 'multitask'
                while True:
                    path=root/'runs/D-E10'/('train_'+mode+'_v2/metadata.json')
                    try:meta=json.loads(path.read_text())
                    except json.JSONDecodeError:time.sleep(5);continue
                    if meta.get('error') or meta.get('stop_reason'):raise RuntimeError('Final training unavailable: '+system)
                    if meta.get('complete'):break
                    time.sleep(30)
            preferred=os.environ.get('CUDA_VISIBLE_DEVICES','0').split(',')[0]
            state['phase']='waiting_for_idle_gpu';state['waiting_system']=system;save()
            while True:
                candidates=[preferred]
                earlier=root/'runs/D-E10/finish_status.json'
                try:earlier_complete=json.loads(earlier.read_text()).get('complete',False)
                except (FileNotFoundError,json.JSONDecodeError):earlier_complete=False
                # After D-E10 releases all of its GPUs, avoid indefinite
                # dependence on another project's use of the preferred GPU.
                if earlier_complete:candidates+=['0','1','3']
                available=[g for g in dict.fromkeys(candidates) if int(subprocess.check_output(
                    ['nvidia-smi','--id='+g,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())<1024]
                if available:
                    gpu=available[0];break
                time.sleep(30)
            used=sum(json.loads(q.read_text()).get('wall_s',0) for q in out.glob(system+'_interrupted*/metadata.json'))
            remaining=3-used/3600
            if remaining<=0:raise TimeoutError('Registered cumulative generation budget exhausted: '+system)
            command=[sys.executable,str(Path(__file__).with_name('run_native_rollouts.py')),
                     '--asset-root',str(root),'--system',system,'--max-hours',str(remaining)]
            state['phase']='generating';state['selected_gpu']=gpu;save()
            with (root/'logs'/('D-E11-'+system+'.log')).open('x') as f:
                subprocess.run(command,env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu),stdout=f,stderr=subprocess.STDOUT,check=True)
            meta=json.loads((out/system/'metadata.json').read_text())
            if not meta.get('complete'):raise RuntimeError('Registered interaction cohort incomplete: '+system)
            state['systems_completed'].append(system);save()
        state['complete']=True
    except BaseException as e:
        state['error']=repr(e);raise
    finally:
        state['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()


if __name__=='__main__':main()
