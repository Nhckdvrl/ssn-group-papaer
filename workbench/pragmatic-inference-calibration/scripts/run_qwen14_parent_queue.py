import fcntl,json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON

def run(gpu,m,task):
    cp=m['id'].split('/')[-1];name='E41-'+task+'-'+cp
    deadline=time.monotonic()+5400
    print(json.dumps({'queued':name,'gpu':gpu,'prerequisite':'pinned complete weights + CPU gates'}),flush=True)
    while not (ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json').exists():
        if time.monotonic()>deadline:raise TimeoutError('asset '+cp)
        time.sleep(5)
    script='run_projection_qwen14.py' if task=='projection' else 'run_qwen14_parent.py'
    cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/'+script,'--root',str(ROOT),
        '--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],'--output',str(ROOT/'runs'/name)]
    if task!='projection':cmd+=['--task',task]
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        if code:raise RuntimeError(name)
if __name__=='__main__':
    assert __import__('pathlib').Path('workbench/pragmatic-inference-calibration/results/E41-prefix-preflight.json').exists()
    assert __import__('pathlib').Path('workbench/pragmatic-inference-calibration/results/E41-projection-preflight.json').exists()
    manifest=json.loads((ROOT/'models/qwen25-14-stage-manifest.json').read_text());failed=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        fs=[ex.submit(run,4*i+j,m,t) for i,m in enumerate(manifest) for j,t in enumerate(['hu-bare','hu-chat','implicaturex','projection'])]
        for f in as_completed(fs):
            try:f.result()
            except Exception as e:failed.append(str(e))
    print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
