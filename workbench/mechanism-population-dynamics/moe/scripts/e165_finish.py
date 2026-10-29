"""Durable E165 preflight/run/statistics chain; no retries or new conditions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

WB = Path(__file__).resolve().parents[2]
ROOT = WB/'moe/results/e165'


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(p):return json.loads(Path(p).read_text())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--physical-gpu',type=int,default=0);args=parser.parse_args()
    if (ROOT/'execution_complete.json').exists():
        raise FileExistsError('Preserve prior completed execution')
    for phase in ('preflight','run'):
        status=ROOT/('supervision_'+phase+'.json')
        if status.exists():raise FileExistsError('Inspect prior phase; no automatic retry')
        subprocess.run([sys.executable,'-B',str(WB/'moe/scripts/supervised_process.py'),
                        '--status',str(status),'--log',str(ROOT/('run_'+phase+'.log')),
                        '--cwd',str(WB),'--timeout','28800','--',sys.executable,'-B','-u',
                        str(WB/'moe/scripts/e165_local_adapter.py'),phase,'--physical-gpu',str(args.physical_gpu)],
                       cwd=WB,check=True)
        state=read(status)
        if state['status']!='complete' or state['returncode']!=0:raise ValueError('Phase did not exit successfully')
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for script in ('e165_analyze.py','e165_verify.py'):
        subprocess.run([sys.executable,'-B',str(WB/'moe/scripts'/script)],cwd=WB,env=env,check=True)
    plan=read(ROOT/'plan.json');manifest=read(ROOT/'manifest.json');audit=read(ROOT/'independent_audit.json')
    seconds=sum(row['gpu_seconds'] for row in read(ROOT/'budget.json')['attempts'])
    if manifest['status']!='complete' or audit['status']!='passed' or seconds>plan['gpu_limit_seconds']:
        raise ValueError('Incomplete provenance or exhausted package')
    output={'experiment':'E165','status':'complete','numerical_source_commit':plan['numerical_source_commit'],
            **{key+'_sha256':sha(ROOT/(key+'.json')) for key in ('plan','manifest','summary','independent_audit')},
            'supervision':{p:sha(ROOT/('supervision_'+p+'.json')) for p in ('preflight','run')},
            'gpu_seconds':seconds,'peak_GPU_GB':manifest['peak_GPU_GB'],
            'finisher_sha256':sha(__file__),'new_training':0,'no_followup_experiments':True}
    (ROOT/'execution_complete.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output),flush=True)


if __name__=='__main__':main()
