"""Run one already-authorized batch when a local GPU is genuinely empty."""
import argparse
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time
import torch

p=argparse.ArgumentParser();p.add_argument('--gpus',required=True);p.add_argument('--script',required=True)
p.add_argument('arguments',nargs=argparse.REMAINDER);args=p.parse_args()
eligible={int(x) for x in args.gpus.split(',')};last_report=0
visible=os.environ.get('CUDA_VISIBLE_DEVICES')
physical=[int(x) for x in visible.split(',')] if visible else None
while True:
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],text=True)
    rows=[[int(c.strip().split()[0]) for c in line.split(',')] for line in raw.strip().splitlines()]
    states={index:(memory,utilization) for index,memory,utilization in rows}
    mapping={local:physical[local] if physical is not None else local for local in eligible}
    free=[local for local,index in mapping.items() if states[index][0]<100 and states[index][1]==0]
    if free:
        gpu=free[0];torch.cuda.set_device(gpu)
        # Initialize a real CUDA context immediately, before loading model modules.
        context=torch.empty(1,device='cuda');torch.cuda.synchronize()
        print('selected_empty_gpu',gpu,'physical',mapping[gpu],torch.cuda.get_device_name(),flush=True);break
    if time.monotonic()-last_report>60:
        print('waiting_for_empty_gpu',sorted(eligible),flush=True);last_report=time.monotonic()
    time.sleep(10)
argv=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
sys.argv=[args.script,*argv]
runpy.run_path(args.script,run_name='__main__')
