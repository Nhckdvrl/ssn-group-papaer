#!/usr/bin/env python3
"""Run registered D-E10 systems sequentially on the assigned independent GPU."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--systems',nargs='+',required=True)
    p.add_argument('--wait-for-training',choices=['update','multitask']);a=p.parse_args();root=Path(a.asset_root)
    if a.wait_for_training:
        path=root/'runs/D-E10'/('train_'+a.wait_for_training+'_v2')/'metadata.json'
        while True:
            if path.exists():
                try:m=json.loads(path.read_text())
                except json.JSONDecodeError:time.sleep(5);continue
                if m.get('complete'):break
                if m.get('error') or m.get('stop_reason'):raise RuntimeError('Training stopped; no partial-checkpoint evaluation')
            time.sleep(30)
    for system in a.systems:
        meta=root/'runs/D-E10'/('system_'+system)/'metadata.json'
        if meta.exists():
            if json.loads(meta.read_text()).get('complete'):continue
            raise RuntimeError('Existing incomplete system requires inspection: '+system)
        subprocess.run([sys.executable,str(Path(__file__).with_name('run_adaptation_pipeline.py')),
                        '--asset-root',str(root),'--system',system],check=True)


if __name__=='__main__':main()
