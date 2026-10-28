"""Resource-only E163 adapter: keep prepared CPU models while a card is busy.

The frozen C31 numerical driver, all model/intervention code, inputs, metrics
and GPU ledgers are unchanged. Only its resource-acquisition function waits.
No CUDA context or file reservation is retained during a busy-card wait.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import e163_run as run
torch=run.torch


def write(path,values):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(values,indent=2)+'\n');os.replace(tmp,path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('run',))
    parser.add_argument('--group',choices=('PAB',),default='PAB')
    parser.add_argument('--physical-gpu',type=int,required=True)
    args=parser.parse_args()
    path=run.ROOT/'resource_adapter.json'
    if path.exists():raise FileExistsError('Keep the earlier resource adapter record')
    with Path(__file__).open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    record={'status':'registered','numerical_source_commit':'c31e4b0e',
        'adapter_source':str(Path(__file__).resolve()),'adapter_sha256':digest,
        'plan_sha256':run.n.sha(run.ROOT/'plan.json'),'physical_gpu':args.physical_gpu,
        'scope':'Only wait for the original GPU lock after CPU readiness. No model or floating calculation modified.',
        'max_wait_seconds':7200,'maximum_MoE_GPU_concurrency':2,'GPU_cap':4}
    write(path,record)
    original=run.n.old.gpu_lock
    def waiting_lock(physical):
        start=time.monotonic();last_report=-60.
        while True:
            if torch.cuda.is_initialized():raise RuntimeError('CUDA initialized before resource acquisition')
            rows=subprocess.check_output(['nvidia-smi','-i',str(physical),'--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
            reason='GPU occupied: '+rows if rows else None
            if not rows:
                try:
                    handle=original(physical)
                except (BlockingIOError,RuntimeError) as error:
                    if torch.cuda.is_initialized() or not (isinstance(error,BlockingIOError) or 'occupied:' in str(error)):
                        raise
                    reason=str(error)
                else:
                    write(run.ROOT/'GPU_wait_PAB.json',{'status':'acquired','physical_gpu':physical,
                        'CPU_wait_seconds':time.monotonic()-start,'GPU_reserved_while_waiting':False})
                    return handle
                # Leave the exception scope so its traceback/file lock is freed
                # before waiting. We hold neither a GPU nor a file reservation.
            elapsed=time.monotonic()-start
            if elapsed>=7200:raise TimeoutError('Registered CPU GPU-wait bound reached')
            write(run.ROOT/'GPU_wait_PAB.json',{'status':'CPU_waiting','physical_gpu':physical,
                'CPU_wait_seconds':elapsed,'CUDA_initialized':False,'reason':reason,'GPU_reserved_while_waiting':False})
            if elapsed-last_report>=60:
                run.n.old.emit('E163_CPU_wait_for_GPU',physical_gpu=physical,CPU_wait_seconds=elapsed,reason=reason)
                last_report=elapsed
            time.sleep(10)
    run.n.old.gpu_lock=waiting_lock
    try:
        run.evaluate(args.group,args.physical_gpu)
        record['status']='complete'
    except BaseException as error:
        record.update(status='failed',error=type(error).__name__+': '+str(error));raise
    finally:
        run.n.old.gpu_lock=original;write(path,record)


if __name__=='__main__':main()
