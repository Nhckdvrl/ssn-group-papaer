#!/usr/bin/env python3
"""Use the otherwise idle GPU2 for native interaction; await complete training."""
import argparse
import datetime
import json
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
            command=[sys.executable,str(Path(__file__).with_name('run_native_rollouts.py')),
                     '--asset-root',str(root),'--system',system]
            with (root/'logs'/('D-E11-'+system+'.log')).open('x') as f:
                subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,check=True)
            meta=json.loads((out/system/'metadata.json').read_text())
            if not meta.get('complete'):raise RuntimeError('Registered interaction cohort incomplete: '+system)
            state['systems_completed'].append(system);save()
        state['complete']=True
    except BaseException as e:
        state['error']=repr(e);raise
    finally:
        state['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()


if __name__=='__main__':main()
