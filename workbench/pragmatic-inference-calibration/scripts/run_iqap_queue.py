import fcntl,json,os,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON,Q25,Q3
from run_qwen_stage_queue import BASE

def models():
    ol=[(m['id'].split('/')[-1],m['id'],m['sha']) for m in json.loads((ROOT/'models/olmoe-stage-manifest.json').read_text())]
    qs=[(m['id'].split('/')[-1],m['id'],m['sha']) for m in json.loads((ROOT/'models/qwen3-scale-manifest.json').read_text())]
    return [BASE,Q25]+ol+[Q3]+qs

def run(gpu,m):
    cp,mid,sha=m;name='E33-iqap-'+cp
    assert (ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json').exists()
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_iqap.py','--root',str(ROOT),
             '--model',str(ROOT/'models'/cp),'--model-id',mid,'--revision',sha,'--output',str(ROOT/'runs'/name)]
        with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        if code:raise RuntimeError(name)

if __name__=='__main__':
    failed=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        for f in as_completed([ex.submit(run,g,m) for g,m in enumerate(models())]):
            try:f.result()
            except Exception as e:failed.append(str(e))
    print(json.dumps({'failed':failed}),flush=True)
    raise SystemExit(bool(failed))
