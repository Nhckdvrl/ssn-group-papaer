import fcntl,json,os,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON
from projection_budget_data import specs

def run(gpu,m,seeds):
    cp,mid,sha,parent=m;name='E45-bwim-'+cp+'-seeds'+''.join(map(str,seeds))
    env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),OMP_NUM_THREADS='8',TOKENIZERS_PARALLELISM='false')
    with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_bwim_confidence.py','--root',str(ROOT),
            '--model',str(ROOT/'models'/cp),'--model-id',mid,'--revision',sha,'--seeds',','.join(map(str,seeds)),
            '--output',str(ROOT/'runs'/name)]
        with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        if code:raise RuntimeError(name)
if __name__=='__main__':
    selected={'Qwen2.5-3B-Instruct','Qwen3-4B','Qwen3-8B','Qwen3-14B','Mistral-7B-Instruct-v0.3'}
    jobs=[(m,seed) for m in specs(ROOT) if m[0] in selected for seed in [[0,2],[1,3]]];assert len(jobs)==10
    failed=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        for f in as_completed([ex.submit(run,i%8,m,s) for i,(m,s) in enumerate(jobs)]):
            try:f.result()
            except Exception as e:failed.append(str(e))
    print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
