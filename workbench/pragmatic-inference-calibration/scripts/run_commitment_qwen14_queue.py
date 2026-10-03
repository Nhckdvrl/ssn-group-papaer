import fcntl,json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON
from commitment_qwen14_data import GROUPS

def run(gpu,m,group):
    cp=m['id'].split('/')[-1];name='E46-commitment-'+cp+'-'+group
    assert json.loads((ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json').read_text())
    path=ROOT/'runs'/name
    if path.exists():
        # Resume the coordinator, never resume or overwrite incomplete predictions.
        cfg=json.loads((path/'config.json').read_text())
        assert cfg.get('complete') and cfg['numerical_gate_pass'] and cfg['model']==m['id'] and cfg['revision']==m['sha'] and cfg['group']==group
        print(json.dumps({'already_complete':name}),flush=True);return
    print(json.dumps({'queued':name,'gpu':gpu}),flush=True)
    lock=None
    while lock is None:
        for candidate in [gpu]+[i for i in range(8) if i!=gpu]:
            trial=(ROOT/'gpu-locks'/f'{candidate}.lock').open('w')
            try:fcntl.flock(trial,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:trial.close();continue
            # The GPU can have a process whose previous coordinator exited. Locks
            # alone cannot establish that it is free. Keep unrelated small processes.
            memory=int(subprocess.check_output(['nvidia-smi','-i',str(candidate),
                '--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
            if memory>10000:
                fcntl.flock(trial,fcntl.LOCK_UN);trial.close();continue
            lock=trial;gpu=candidate;break
        if lock is None:time.sleep(2)
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    with lock:
        assert not path.exists()
        print(json.dumps({'start':name,'gpu':gpu}),flush=True)
        cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/run_commitment_qwen14.py','--root',str(ROOT),
            '--model',str(ROOT/'models'/cp),'--model-id',m['id'],'--revision',m['sha'],'--group',group,'--output',str(ROOT/'runs'/name)]
        with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
        print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
        if code:raise RuntimeError(name)
if __name__=='__main__':
    pre=json.loads(open('workbench/pragmatic-inference-calibration/results/E46-source-preflight.json').read());assert pre['gate_pass']
    manifest=json.loads((ROOT/'models/qwen25-14-stage-manifest.json').read_text());failed=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        for f in as_completed([ex.submit(run,i*4+j,m,g) for i,m in enumerate(manifest) for j,g in enumerate(GROUPS)]):
            try:f.result()
            except Exception as e:failed.append(str(e))
    print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
