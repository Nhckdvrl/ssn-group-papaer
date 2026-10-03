import fcntl,json,os,subprocess,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from speaker_listener_data import specs

ROOT=Path('/data1/xiangding/work/pragmatic-inference-calibration')
PY='/data1/xiangding/env/pragmatic-inference-calibration/bin/python'
def run(index,m):
    cp,mid,revision=m;name='E49-speaker-listener-'+cp
    while True:
        for gpu in [(index+j)%8 for j in range(8)]:
            lock=(ROOT/'gpu-locks'/f'{gpu}.lock').open('w')
            try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError: lock.close();continue
            used=int(subprocess.check_output(['nvidia-smi',f'--id={gpu}','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
            if used>10000: lock.close();continue
            env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),OMP_NUM_THREADS='8',TOKENIZERS_PARALLELISM='false')
            print(json.dumps({'start':name,'gpu':gpu}),flush=True)
            with lock,(ROOT/(name+'.log')).open('w') as log:
                code=subprocess.run([PY,'workbench/pragmatic-inference-calibration/scripts/run_speaker_listener_qwen25.py','--root',str(ROOT),
                    '--model',str(ROOT/'models'/cp),'--model-id',mid,'--revision',revision,'--output',str(ROOT/'runs'/name)],env=env,stdout=log,stderr=subprocess.STDOUT).returncode
            print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
            if code:raise RuntimeError(name)
            return
        time.sleep(5)

if __name__=='__main__':
    failed=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for f in as_completed([pool.submit(run,i,m) for i,m in enumerate([m for m in specs(ROOT) if m[0] in ['Qwen2.5-3B-Instruct','Qwen2.5-14B-Instruct']])]):
            try:f.result()
            except Exception as e:failed.append(str(e))
    print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
