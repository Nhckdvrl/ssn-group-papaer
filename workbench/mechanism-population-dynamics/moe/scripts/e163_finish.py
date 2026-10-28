"""Finish the registered E163 jobs with CPU statistics, audit and figures only.

No GPU/model entrypoint is called. A failed job stops this finisher; it neither
retries experiments nor starts another experiment. The parent monitors results.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

WB=Path(__file__).resolve().parents[2]
ROOT=WB/'moe/results/e163'


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text())


def main():
    while True:
        states={g:read(ROOT/('supervision_'+g+'.json')) for g in ('PAB','F')}
        if any(v['status']=='failed' for v in states.values()):
            raise RuntimeError('A registered job failed; preserve its ledger and inspect it before any retry')
        if all(v['status']=='complete' for v in states.values()):break
        time.sleep(15)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for args in [('e163_analyze.py','analyze'),('e163_verify.py','verify'),('e163_plot.py',)]:
        subprocess.run([sys.executable,'-B',str(WB/'moe/scripts'/args[0]),*args[1:]],cwd=WB,env=env,check=True)
    manifest={'experiment':'E163','status':'complete','numerical_source_commit':read(ROOT/'plan.json').get('numerical_source_commit','19f6f3a5'),
        'plan_sha256':sha(ROOT/'plan.json'),'summary_sha256':sha(ROOT/'summary.json'),
        'independent_audit_sha256':sha(ROOT/'independent_audit.json'),
        'raw':{name:read(ROOT/('manifest_'+name+'.json'))['raw'] for name in ('P','A','B','F','cross')},
        'supervision':{g:sha(ROOT/('supervision_'+g+'.json')) for g in ('PAB','F')},
        'gpu_seconds':{g:sum(a['gpu_seconds'] for a in read(ROOT/('budget_'+g+'.json'))['attempts']) for g in ('PAB','F')},
        'finisher_sha256':sha(__file__),'plot_source_sha256':sha(WB/'moe/scripts/e163_plot.py'),
        'no_new_training_or_followup_experiments':True}
    if (ROOT/'resource_adapter.json').exists():
        resource=read(ROOT/'resource_adapter.json')
        if resource['status']!='complete' or sha(resource['adapter_source'])!=resource['adapter_sha256']:
            raise ValueError('Resource adapter did not finish with its registered source')
        manifest['resource_adapter']={'path':str(ROOT/'resource_adapter.json'),'sha256':sha(ROOT/'resource_adapter.json')}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'complete','experiment':'E163','gpu_seconds':manifest['gpu_seconds']}),flush=True)


if __name__=='__main__':main()
