"""E51 preserved pending DPO job: lock any free GPU after old waiter stopped."""
import fcntl,json,os,subprocess,time
from pathlib import Path
from dense_stage_data import specs
from run_followup_queue import ROOT,PYTHON

if __name__=='__main__':
    proof=json.loads(Path('workbench/pragmatic-inference-calibration/results/E51-scheduler-resume-audit.json').read_text())
    assert proof['original_coordinator_terminated'] and not proof['active_scientific_workers_before_relocation']
    cp='OLMo-2-1124-13B-DPO';m=next(x for x in specs(ROOT) if x['id'].endswith('/'+cp));name='E51-circa-'+cp
    assert not (ROOT/'runs'/name).exists() and (ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json').exists()
    pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E51-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(ROOT)
    deadline=time.monotonic()+7200
    while time.monotonic()<deadline:
        for gpu in range(8):
            lock=(ROOT/'gpu-locks'/f'{gpu}.lock').open('w')
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:lock.close();continue
            used=int(subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
            if used>=10000:lock.close();continue
            env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
            print(json.dumps({'start':name,'gpu':gpu,'waiting_job_relocated':True}),flush=True)
            with lock,(ROOT/(name+'-retry.log')).open('w') as log:
                code=subprocess.run([PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_dense_stage.py',
                    '--root',str(ROOT),'--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],
                    '--task','circa','--output',str(ROOT/'runs'/name)],env=env,stdout=log,stderr=subprocess.STDOUT).returncode
            print(json.dumps({'done':name,'exit':code}),flush=True);raise SystemExit(code)
        time.sleep(5)
    raise TimeoutError(name)
