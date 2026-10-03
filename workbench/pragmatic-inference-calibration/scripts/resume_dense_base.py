"""E51 download-timeout-only retry; never duplicate an existing Base worker."""
import fcntl,json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from dense_stage_data import specs,sha
from run_followup_queue import ROOT,PYTHON

CP='OLMo-2-1124-13B'

def run(index,task,m):
    name='E51-'+task+'-'+CP;deadline=time.monotonic()+7200
    while time.monotonic()<deadline:
        lines=(ROOT/'E51-queue.log').read_text().splitlines()
        records=[]
        for line in lines:
            try:records.append(json.loads(line))
            except ValueError:pass
        if sum(r.get('start') in ('E51-iqap-'+CP,'E51-circa-'+CP) for r in records)>=2:
            print(json.dumps({'retry_not_needed':task}),flush=True);return
        failures=[r for r in records if r.get('failure')=='Pinned download missing '+CP]
        if len(failures)>=2 and (ROOT/'models'/CP/'DOWNLOAD_COMPLETE.json').exists():break
        time.sleep(10)
    else:raise TimeoutError('Original two Base timeouts and complete pinned marker not available')
    assert not (ROOT/'runs'/name).exists()
    while time.monotonic()<deadline:
        for gpu in [(index+j)%8 for j in range(8)]:
            lock=(ROOT/'gpu-locks'/f'{gpu}.lock').open('w')
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:lock.close();continue
            used=int(subprocess.check_output(['nvidia-smi','-i',str(gpu),'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
            if used>=10000:lock.close();continue
            env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
            print(json.dumps({'start':name,'gpu':gpu,'original_timeout_only_retry':True}),flush=True)
            with lock,(ROOT/(name+'-retry.log')).open('w') as log:
                code=subprocess.run([PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_dense_stage.py',
                    '--root',str(ROOT),'--model',str(ROOT/'models'/CP),'--model-id',m['id'],'--revision',m['sha'],
                    '--task',task,'--output',str(ROOT/'runs'/name)],env=env,stdout=log,stderr=subprocess.STDOUT).returncode
            print(json.dumps({'done':name,'exit':code}),flush=True)
            assert code==0;return
        time.sleep(5)
    raise TimeoutError(name)

if __name__=='__main__':
    m=next(x for x in specs(ROOT) if x['id'].endswith('/'+CP))
    pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E51-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(ROOT)
    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(lambda p:run(p[0],p[1],m),enumerate(('iqap','circa'))))
