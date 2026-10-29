"""Durable sequential two-family chain; never retry or introduce conditions."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    import e166_common as c
    parser=argparse.ArgumentParser();parser.add_argument('--physical-gpu',type=int,default=1);args=parser.parse_args()
    plan=c.checked_plan()
    if (c.ROOT/'execution_complete.json').exists():raise FileExistsError('Preserve completed run')
    for family in ('olmoe','emo'):
        status=c.ROOT/('supervision_'+family+'.json')
        if status.exists():raise FileExistsError('Inspect earlier family; no automatic retry')
        subprocess.run([sys.executable,'-B',str(c.SCRIPTS/'supervised_process.py'),
                '--status',str(status),'--log',str(c.ROOT/('run_'+family+'.log')),
                '--cwd',str(c.WB),'--timeout','28800','--',sys.executable,'-B','-u',
                str(c.SCRIPTS/'e166_run.py'),family,'--physical-gpu',str(args.physical_gpu)],cwd=c.WB,check=True)
        state=c.read(status)
        if state['status']!='complete' or state['returncode']!=0:raise ValueError('Worker not complete')
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for name in ('e166_analyze.py','e166_verify.py'):
        subprocess.run([sys.executable,'-B',str(c.SCRIPTS/name)],cwd=c.WB,env=env,check=True)
    seconds=sum(row['gpu_seconds'] for row in c.read(c.ROOT/'budget.json')['attempts'])
    if seconds>plan['gpu_limit_seconds'] or c.read(c.ROOT/'independent_audit.json')['status']!='passed':raise ValueError('Invalid final package')
    c.write(c.ROOT/'execution_complete.json',{'experiment':'E166','status':'complete',
            'numerical_source_commit':plan['numerical_source_commit'],'gpu_seconds':seconds,
            'plan_sha256':c.sha(c.ROOT/'plan.json'),'independent_audit_sha256':c.sha(c.ROOT/'independent_audit.json'),
            'manifest_sha256':{f:c.sha(c.ROOT/(f+'_manifest.json')) for f in ('emo','olmoe')},
            'summary_sha256':{f:c.sha(c.ROOT/(f+'_summary.json')) for f in ('emo','olmoe')},
            'new_training':0,'no_automatic_followup':True})
    print(json.dumps({'status':'complete','GPU_seconds':seconds}),flush=True)


if __name__=='__main__':main()
