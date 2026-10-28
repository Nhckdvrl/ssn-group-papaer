"""Finish only the authorized E162 batch after verified assets become available.

No successor experiments are launched. No model imports occur while waiting.
"""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time

WB=Path(__file__).resolve().parents[2]
RAW=Path.home()/'mechpop_cache/e162_full_course_native'
STATUS=RAW/'batch_status.json'
ASSET=WB/'moe/results/full_course_assets_2026-10-28/asset_manifest.json'


def update(phase,**extra):
    state={'experiment':'E162','phase':phase,'host':os.uname().nodename,
           'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'pid':os.getpid(),'max_concurrent_gpus':4,'automatic_successor_experiments':False,**extra}
    temporary=STATUS.with_suffix('.tmp');temporary.write_text(json.dumps(state,indent=2)+'\n');os.replace(temporary,STATUS)


def run(command,log,timeout,device=None):
    env=os.environ.copy()
    if device is not None:env['CUDA_VISIBLE_DEVICES']=str(device)
    with log.open('x') as output:
        result=subprocess.run(command,cwd=WB,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,
                              env=env,timeout=timeout,check=False)
    if result.returncode:raise RuntimeError('Batch command failed; '+log.name+' returncode='+str(result.returncode))


def free_device():
    text=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.total,memory.used','--format=csv,noheader,nounits'],text=True)
    for line in text.splitlines():
        index,total,used=(int(x.strip()) for x in line.split(','))
        if total>=80000 and used<1000:return index
    return None


def main():
    RAW.mkdir(parents=True,exist_ok=True);started=time.monotonic()
    if (WB/'moe/results/e162/manifest.json').exists():raise RuntimeError('Existing scientific result; inspect instead of re-running')
    update('waiting_for_verified_assets',GPU_reserved=False)
    while not ASSET.exists():
        transport=RAW/'nvme_asset_supervision.json'
        if transport.exists() and json.loads(transport.read_text()).get('status')=='failed':
            raise RuntimeError('Asset transport stopped; inspect it before any GPU launch')
        if time.monotonic()-started>21600:raise TimeoutError('Asset wait exceeded six hours; no GPU launched')
        time.sleep(20)
    asset=json.loads(ASSET.read_text())
    if asset['status']!='complete' or asset['model']['revision']!='007852b1e3d22222f8ee03c6a53fa30e47898dcb':raise RuntimeError('Pinned complete asset manifest required')
    if asset['model'].get('execution_host')!=os.uname().nodename:raise RuntimeError('Launch on the verified local-execution host')
    update('waiting_for_one_free_GPU',GPU_reserved=False)
    device=None
    while device is None:
        device=free_device()
        if time.monotonic()-started>21600:raise TimeoutError('No free card in the authorized wait window')
        if device is None:time.sleep(20)
    python=sys.executable
    update('preparing_frozen_plan',device=device,GPU_reserved=False)
    run([python,'-B','moe/scripts/e162_run.py','prepare','--physical-gpu',str(device)],RAW/'prepare.log',900,device)
    update('evaluating',device=device,GPU_reserved=True)
    run([python,'-B','moe/scripts/supervised_process.py','--status',str(RAW/'evaluation_supervision.json'),
         '--log',str(RAW/'evaluation.log'),'--cwd',str(WB),'--timeout','7300','--',
         python,'-B','moe/scripts/e162_run.py','evaluate','--physical-gpu',str(device)],RAW/'evaluation_supervisor.log',7400,device)
    supervision=json.loads((RAW/'evaluation_supervision.json').read_text())
    if supervision.get('returncode')!=0:raise RuntimeError('Scientific subprocess did not exit successfully')
    update('CPU_statistics',device=device,GPU_reserved=False)
    run([python,'-B','moe/scripts/e162_analyze.py','--analyze'],RAW/'analysis.log',1200)
    update('CPU_verification',device=device,GPU_reserved=False)
    run([python,'-B','moe/results/e162_independent_audit/audit.py','--summary','moe/results/e162/summary.json',
         '--output','moe/results/e162_independent_audit/report.json'],RAW/'independent_audit.log',1200)
    update('complete_ready_for_scientific_review_and_consolidation',device=device,GPU_reserved=False,
           no_further_experiment_queued=True)


if __name__=='__main__':
    try:main()
    except Exception as error:
        update('stopped_for_review',GPU_reserved=False,error=type(error).__name__+': '+str(error)[:300])
        raise
