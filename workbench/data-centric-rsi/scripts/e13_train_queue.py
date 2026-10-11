import datetime, hashlib, json, os, pathlib, socket, subprocess, sys, time

ROOT = pathlib.Path('/var/tmp/xiang-data-rsi/e13')
REPO = pathlib.Path('/home/xiang/ssn-group-papaer')
PYTHON = '/home/xiang/.venvs/data-centric-rsi/bin/python'
LAUNCHER = REPO / 'workbench/data-centric-rsi/scripts/e13_run_train.py'
LAUNCHER_SHA = '2217d7741525303de2a03ba9a097bbb1907b2824603662ea276333a0e2ce7550'
ASSIGNMENTS = {0: [('init','replay')], 1: [('used','replay')],
               2: [('init','fresh_selected'),('init','fresh_law')],
               3: [('used','fresh_selected'),('used','fresh_law')]}
gpu = int(sys.argv[1])
queue_dir = ROOT / 'train_queue'
queue_dir.mkdir(exist_ok=True)
state_path = queue_dir / f'gpu{gpu}.json'
assert not state_path.exists(), state_path
state = {'node':socket.gethostname(),'gpu':gpu,'queue':ASSIGNMENTS[gpu],
         'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'launcher_sha256':LAUNCHER_SHA,'runs':[]}
def save(): state_path.write_text(json.dumps(state,indent=2)+'\n')
save()
env=os.environ.copy()
env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='')
for parent,action in ASSIGNMENTS[gpu]:
    assert hashlib.sha256(LAUNCHER.read_bytes()).hexdigest()==LAUNCHER_SHA
    run=ROOT/'train_runs'/f'{parent}_{action}_s29'
    assert not run.exists(), run
    while True:
        lines=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines()
        row=next(line for line in lines if int(line.split(',')[0])==gpu)
        _,uuid,free=[x.strip() for x in row.split(',')]
        apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
        if int(free)>=75000 and uuid not in apps: break
        state['waiting_for_free_gpu_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();time.sleep(30)
    command=[PYTHON,str(LAUNCHER),'--root',str(ROOT),'--e12-root','/var/tmp/xiang-data-rsi/e12',
             '--init-parent',str(ROOT/'parents/init'),'--used-parent',str(ROOT/'parents/used'),
             '--processor-sentinel-path',str(ROOT/'processor_sentinel'),'--parent',parent,'--action',action,
             '--gpu',str(gpu),'--out-root',str(ROOT/'train_runs')]
    stdout=queue_dir/f'{parent}_{action}.stdout';stderr=queue_dir/f'{parent}_{action}.stderr'
    assert not stdout.exists() and not stderr.exists()
    start=time.monotonic()
    entry={'parent':parent,'action':action,'gpu':gpu,'command':command,'run_dir':str(run),
           'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'prelaunch_gpu_memory_free_mib':int(free),'prelaunch_no_compute_apps':True}
    state['runs'].append(entry);save()
    with stdout.open('w') as out,stderr.open('w') as err:
        process=subprocess.Popen(command,cwd=REPO,env=env,stdout=out,stderr=err)
        entry['launcher_pid']=process.pid;save();print(json.dumps(entry),flush=True)
        code=process.wait()
    entry.update(returncode=code,queue_wrapper_wall_seconds=round(time.monotonic()-start,3),
                 finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
    assert code==0, entry
    completion=json.loads((run/'completion.json').read_text())
    assert completion['returncode']==0 and completion['model_saved'] and completion['observed_windows']==625
    entry['completion']=completion;save()
state['status']='completed';save()
