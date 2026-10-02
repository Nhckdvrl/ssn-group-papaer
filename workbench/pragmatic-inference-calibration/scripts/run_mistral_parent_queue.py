import fcntl,json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON
from mistral_readout import prepare,fingerprint

def run(gpu,m,task):
    cp=m['id'].split('/')[-1];name=f'E35-{task}-{cp}'
    for _ in range(2160):
        if (ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json').exists():break
        time.sleep(5)
    else:raise TimeoutError(cp)
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_mistral_parent.py','--root',str(ROOT),
             '--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],'--task',task,'--output',str(ROOT/'runs'/name)]
        with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        if code:raise RuntimeError(name)

if __name__=='__main__':
    models=json.loads((ROOT/'models/mistral-stage-manifest.json').read_text());tasks=['hu-bare','hu-chat','circa','implicaturex']
    failed=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        fs=[ex.submit(run,4*i+j,m,t) for i,m in enumerate(models) for j,t in enumerate(tasks)]
        for f in as_completed(fs):
            try:f.result()
            except Exception as e:failed.append(str(e))
    print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
