"""Evaluate both successful E14 terminal models locally with frozen E12 tasks.

fvcrc12 waits for both seed29 branches; fvcrc20 GPU3/8033 is an independent
owned judge. No E13 globals/services are changed, no checkpoint is copied,
and failed artifacts are preserved. Allocation is queue wrapper + eval wrapper,
including CPU/import/I/O after launch, bounded by 8 A100 hours. Judge residency
has its own detached 4 Blackwell-hour watchdog; neither is kernel active time.
"""
from __future__ import annotations
import argparse
import datetime as dt
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import uuid

ROOT = Path('/var/tmp/xiang-data-rsi/e14')
E12 = Path('/var/tmp/xiang-data-rsi/e12')
REPO = Path('/home/xiang/ssn-group-papaer')
SELF = Path(__file__).resolve()
SCRIPTS = REPO / 'workbench/data-centric-rsi/scripts'
VENDOR = Path('/home/xiang/.cache/research/data-centric-rsi/CurationBench')
TRAIN_PYTHON = '/home/xiang/.venvs/data-centric-rsi/bin/python'
JUDGE_PYTHON = '/home/xiang/.venvs/vllm023-cu128/bin/python'
JUDGE_MODEL = '/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-27B/snapshots/fc05daec18b0a78c049392ed2e771dde82bdf654'
URL = 'http://fvcrc20:8033'
RUNS = ['init_source_only_fresh_s29', 'used_source_only_fresh_s29']
BENCHMARKS = ('HallusionBench','LLaVABench','MMBench','MMMU_DEV_VAL','MMStar','MMVet','MathVista_MINI','OCRBench')
FROZEN_MD5 = ('0c23ac0dc9ef46832d7a24504f2a0c7c','d382a093f749a697820d3dadd61c8428','4115aea3383f3dd0083be6a633e0f820','585e8ad75e73f75dcad265dfd0417d64','e1ecd2140806c1b1bbf54b43372efb9e','748aa6d4aa9d4de798306a63718455e3','f199b98e178e5a2a20e7048f5dcb0464','e953d98a987cc6e26ef717b61260b778')
FROZEN_SOURCE = {
 'workbench/data-centric-rsi/scripts/e12_run_eval.py':'20c9eebb084f544d03ad1a32ccf0c9b28efe2d05640c6e85993da213a721e809',
 'workbench/data-centric-rsi/scripts/e12_validate_eval.py':'2f0f1796a3d7662ee53580504a0eab081e901aa3977bb87e2cbccd38db340601',
 'workbench/data-centric-rsi/compat/sitecustomize.py':'ca25d45f14240a586685815d9b34d2790799f6393aebf6cae82dd4a472d7c469',
}
TOTAL_CAP = 8 * 3600
JUDGE_CAP = 4 * 3600


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def read(path): return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + f'.tmp.{os.getpid()}')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def ticks(pid):
    try: return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]
    except FileNotFoundError: return None


def remote(*args, python='python3'):
    return json.loads(subprocess.check_output(['ssh', 'fvcrc20', shlex.join([python, str(SELF), *args])], text=True))


def gpu_available(gpu, minimum):
    rows = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.free','--format=csv,noheader,nounits'], text=True).splitlines()
    _, gpu_uuid, free = [x.strip() for x in next(row for row in rows if int(row.split(',')[0]) == gpu).split(',')]
    apps = subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'], text=True)
    return int(free) >= minimum and gpu_uuid not in apps


def port_free():
    with socket.socket() as port:
        port.settimeout(3)
        return port.connect_ex(('127.0.0.1', 8033)) != 0


def environment():
    assert socket.gethostname().startswith('fvcrc12')
    vendor_sha = subprocess.check_output(['git','-C',str(VENDOR),'rev-parse','HEAD'], text=True).strip()
    assert vendor_sha == '24eea1526492c00cee421f5db0793789e00aabb2'
    subprocess.run(['git','-C',str(VENDOR),'diff','--exit-code','--quiet'], check=True)
    task = VENDOR / 'src/benchmark/tasks/llava665k_llava_8bench_10k_unlimited.yaml'
    assert digest(task) == 'df20fa6f3146ddf6b80c81b651ca0506aa11c65ae9e12cb3a19a240c8bc69590'
    actual_source = {p: digest(REPO / p) for p in FROZEN_SOURCE}
    assert actual_source == FROZEN_SOURCE
    freeze = subprocess.check_output(['/home/xiang/.local/bin/uv','pip','freeze','--python',str(E12 / 'vlmeval_venv/bin/python')])
    freeze_sha = hashlib.sha256(freeze).hexdigest()
    assert freeze_sha == '8ef6b4ec11c6d563e990ad7a2a3eebb9ac67d3c735792a769bcf86c450da9f40'
    md5 = {b: digest(E12 / 'LMUData' / f'{b}.tsv', 'md5') for b in BENCHMARKS}
    assert tuple(md5.values()) == FROZEN_MD5
    return {'utc':utc(), 'node':socket.gethostname(), 'vendor_sha':vendor_sha,
            'task_sha256':digest(task), 'actual_source_sha256':actual_source,
            'eval_pip_freeze_sha256':freeze_sha, 'TSV_MD5':md5,
            'eval_python':str(E12 / 'vlmeval_venv/bin/python'),
            'deviations_from_E13':{'student_node':'fvcrc12','student_physical_gpu':0,
                                  'judge_physical_gpu':3,'judge_port':8033,'model_copy_bytes':0}}


def training_status():
    directory = ROOT / 'train_queue'
    queues = [read(directory / f'gpu{gpu}.json') for gpu in (0, 1) if (directory / f'gpu{gpu}.json').exists()]
    watch = read(directory / 'budget_watch.json') if (directory / 'budget_watch.json').exists() else None
    def recovered_preflight(entry):
        return (entry.get('returncode') == 1
                and entry.get('same_seed_recovery_authorized') is True
                and entry.get('failure_phase') == 'CPU parent-manifest name/path schema, before training')
    failed = [q for q in queues
              if any(e.get('returncode', 0) != 0 and not recovered_preflight(e) for e in q['runs'])
              or (q.get('status') == 'failed' and not any(recovered_preflight(e) for e in q['runs']))]
    if watch and (watch['status'].startswith('cap_reached') or watch['status'] in ('drivers_missing_no_owned_launchers','queue_failed_preserve_all_runs')):
        failed.append(watch)
    runs = {}
    for name in RUNS:
        directory = ROOT / 'train_runs' / name
        if (directory / 'completion.json').exists():
            runs[name] = {'completion':read(directory / 'completion.json'),
                          'runtime':read(directory / 'runtime_manifest.json') if (directory / 'runtime_manifest.json').exists() else None,
                          'trace_rows':len((directory / 'window_trace.jsonl').read_text().splitlines()) if (directory / 'window_trace.jsonl').exists() else 0}
    ready = len(queues) == 2 and all(q.get('status') == 'completed' for q in queues) and len(runs) == 2
    spent = sum(e.get('queue_wrapper_wall_seconds', (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(e['started_utc'])).total_seconds()) for q in queues for e in q['runs'])
    return {'utc':utc(),'queues':queues,'budget_watch':watch,'failures':failed,'runs':runs,
            'ready':ready,'train_queue_wrapper_seconds':spent}


def verify_terminal(status):
    assert status['ready'] and not status['failures']
    assert status['budget_watch'] and status['budget_watch']['status'] == 'queues_completed'
    for name in RUNS:
        result = status['runs'][name]; c = result['completion']; r = result['runtime']
        assert c['returncode'] == 0 and c['model_saved'] and c['observed_windows'] == 625 and result['trace_rows'] == 625, name
        assert r and r['model_accepts_loss_kwargs'] and r['accelerator_gradient_accumulation_steps'] == 1 and r['trainer_gradient_accumulation_steps'] == 16, name
        assert r['initial_global_step'] == 0 and r['optimizer_initially_none'] and r['lr_scheduler_initially_none'] and r['data_seed'] == 29 and r['use_seedable_sampler'], name
        directory = ROOT / 'train_runs' / name
        manifest = read(directory / 'run_manifest.json')
        assert manifest['experiment'] == 'E14' and manifest['action'] == 'source_only_fresh' and manifest['seed'] == 29
        expected = manifest['processor_sampler_audit']['expected_window_microbatch_n']
        trace = [json.loads(line) for line in (directory / 'window_trace.jsonl').read_text().splitlines()]
        assert len(expected) == 625
        for row, ns in zip(trace, expected):
            assert row['microbatch_n'] == ns and row['num_items_in_batch'] == sum(ns)
        assert sum(row['num_items_in_batch'] for row in trace) == manifest['expected_supervised_tokens'] == 1078803
    assert status['train_queue_wrapper_seconds'] < 6 * 3600


def terminal_hash(directory):
    start = time.monotonic()
    index = read(directory / 'model.safetensors.index.json')
    shards = set(index['weight_map'].values())
    assert len(shards) == 3 and all((directory / shard).is_file() for shard in shards)
    files = [{'path':str(p.relative_to(directory)), 'bytes':p.stat().st_size, 'sha256':digest(p)}
             for p in sorted(directory.rglob('*')) if p.is_file()]
    assert sum(e['bytes'] for e in files) > 14_000_000_000
    return {'directory':str(directory),'node':socket.gethostname(),'files':files,'hashed_utc':utc(),
            'local_terminal_hash_wall_seconds':round(time.monotonic()-start,3),
            'copy_wall_seconds':0,'copy_bytes':0,'copied':False,
            'scope':'Actual new successful E14 terminal files, not historical parent checksums'}


def metrics():
    raw = urllib.request.urlopen(URL + '/metrics', timeout=30).read().decode()
    wanted = ('vllm:num_requests_running{','vllm:num_requests_waiting{','vllm:prompt_tokens_total{','vllm:generation_tokens_total{','vllm:request_success_total{')
    values = {line.split()[0]:float(line.split()[1]) for line in raw.splitlines() if line.startswith(wanted) and len(line.split()) == 2}
    assert any(k.startswith(wanted[0]) for k in values) and any(k.startswith(wanted[1]) for k in values)
    return raw, values


def pending(values):
    return sum(v for k,v in values.items() if k.startswith(('vllm:num_requests_running{','vllm:num_requests_waiting{')))


def own_judge_processes(token):
    """Authenticate each process individually by inherited opaque owner token."""
    m = read(ROOT / 'judge/launch_manifest.json')
    assert m['owner_token'] == token
    marker = f'E14_JUDGE_OWNER_TOKEN={token}'.encode()
    owned = []
    for row in subprocess.check_output(['ps','-eo','pid=,pgid='], text=True).splitlines():
        pid, group = map(int, row.split())
        if group != m['process_group']: continue
        try:
            started = ticks(pid)
            if marker in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0'):
                owned.append({'pid':pid,'start_ticks':started})
        except (FileNotFoundError, PermissionError, ProcessLookupError): pass
    return owned


def judge_stop(token, failure=False):
    d = ROOT / 'judge'
    with (d / 'cleanup.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (d / 'cost_snapshot_final.json').exists():
            saved = read(d / 'cost_snapshot_final.json')
            assert saved['owner_token'] == token
            if saved.get('cleanup_complete'): return saved
        m = read(d / 'launch_manifest.json'); assert m['owner_token'] == token
        owned = own_judge_processes(token)
        server_alive = m['start_ticks'] is not None and ticks(m['pid']) == m['start_ticks']
        values = {}; metric_error = None
        if server_alive:
            try:
                raw, values = metrics()
                assert pending(values) == 0 or failure, 'Owned judge requests have not drained'
                (d / 'metrics_final.prom').write_text(raw)
            except Exception as error:
                if not failure: raise
                metric_error = str(error)
        else: metric_error = 'Owned server has exited; replacement endpoint not queried'
        snapshot = {'utc':utc(),'owner_token':token,'launch_manifest':m,'metrics':values,
                    'pending_requests':pending(values) if values else None,'metrics_error':metric_error,
                    'failure_cleanup':failure,'owned_processes':owned,'active_gpu_time':'unmeasured',
                    'not_A100_converted':True,'API_paid_requests':0}
        write(d / 'cost_snapshot_final.json', snapshot)
        def stop_owned(sig):
            for process in own_judge_processes(token):
                if ticks(process['pid']) == process['start_ticks']:
                    try: os.kill(process['pid'], sig)
                    except ProcessLookupError: pass
        stop_owned(signal.SIGTERM)
        for _ in range(20):
            if not own_judge_processes(token): break
            time.sleep(1)
        if own_judge_processes(token): stop_owned(signal.SIGKILL)
        for _ in range(10):
            if not own_judge_processes(token): break
            time.sleep(1)
        snapshot.update(stopped_utc=utc(), remaining_owned_processes=own_judge_processes(token),
                        server_residency_seconds_upper_bound=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(m['started_utc'])).total_seconds(),
                        endpoint_port_closed=port_free())
        snapshot['cleanup_complete'] = not snapshot['remaining_owned_processes']
        snapshot['judge_allocated_Blackwell_hours_upper_bound'] = snapshot['server_residency_seconds_upper_bound']/3600
        write(d / 'cost_snapshot_final.json', snapshot)
        return snapshot


def judge_watch(token):
    assert socket.gethostname().startswith('fvcrc20')
    d = ROOT / 'judge'; m = read(d / 'launch_manifest.json'); assert m['owner_token'] == token
    # Reserve 90 seconds for TERM/KILL cleanup inside the 4-hour residency cap.
    deadline = dt.datetime.fromisoformat(m['started_utc']) + dt.timedelta(seconds=JUDGE_CAP-90)
    while True:
        if (d / 'cost_snapshot_final.json').exists() and read(d / 'cost_snapshot_final.json').get('cleanup_complete'): return
        if dt.datetime.now(dt.timezone.utc) >= deadline:
            judge_stop(token, failure=True); return
        time.sleep(10)


def judge_environment():
    assert socket.gethostname().startswith('fvcrc20')
    version = importlib.metadata.version('vllm'); assert version == '0.23.0+cu129'
    model = Path(JUDGE_MODEL); assert model.is_dir()
    index = read(model / 'model.safetensors.index.json')
    shards = sorted(set(index['weight_map'].values()))
    assert shards and all((model / shard).is_file() for shard in shards)
    return {'utc':utc(),'node':socket.gethostname(),'vllm':version,'python':sys.executable,
            'model_snapshot':str(model),'revision':model.name,
            'model_config_sha256':digest(model / 'config.json'),
            'model_index_sha256':digest(model / 'model.safetensors.index.json'),
            'shards_present':shards,'model_weight_content_sha256':'not rehashed in CPU preflight',
            'prospective_physical_gpu':3,'prospective_port':8033,
            'gpu_free_and_noapps':gpu_available(3,80000),'port_free':port_free(),
            'status':'CPU preflight only; judge not started; GPU not reserved'}


def judge_start(token):
    assert socket.gethostname().startswith('fvcrc20')
    assert importlib.metadata.version('vllm') == '0.23.0+cu129'
    assert Path(JUDGE_MODEL).is_dir() and gpu_available(3,80000) and port_free()
    d = ROOT / 'judge'; d.mkdir(parents=True, exist_ok=False)
    command = [JUDGE_PYTHON,'-m','vllm.entrypoints.openai.api_server','--model',JUDGE_MODEL,
               '--served-model-name','Qwen3.5-27B','--host','0.0.0.0','--port','8033',
               '--dtype','bfloat16','--tensor-parallel-size','1','--max-model-len','4096',
               '--max-num-seqs','16','--gpu-memory-utilization','0.78',
               '--default-chat-template-kwargs','{"enable_thinking":false}']
    env = os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES='3',CUDA_DEVICE_ORDER='PCI_BUS_ID',VLLM_USE_FLASHINFER_SAMPLER='0',E14_JUDGE_OWNER_TOKEN=token)
    started_utc = utc()
    with (d / 'server.log').open('x') as log:
        process = subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    record = {'owner_token':token,'started_utc':started_utc,'pid':process.pid,'start_ticks':ticks(process.pid),
              'process_group':process.pid,'command':command,
              'environment':{k:env[k] for k in ('CUDA_VISIBLE_DEVICES','CUDA_DEVICE_ORDER','VLLM_USE_FLASHINFER_SAMPLER')},
              'gpu_type':'Blackwell','gpu':3,'residency_cap_seconds':JUDGE_CAP,'active_gpu_time':'unmeasured'}
    try:
        write(d / 'launch_manifest.json',record)
        with (d / 'watch.stdout').open('x') as out, (d / 'watch.stderr').open('x') as err:
            guard = subprocess.Popen(['python3',str(SELF),'--judge-watch','--owner-token',token],stdout=out,stderr=err,start_new_session=True)
        record['watch_pid'] = guard.pid; record['watch_start_ticks'] = ticks(guard.pid)
        write(d / 'launch_manifest.json',record)
    except Exception:
        if (d / 'launch_manifest.json').exists(): judge_stop(token, failure=True)
        elif ticks(process.pid) == record['start_ticks']:
            os.killpg(process.pid,signal.SIGTERM)
        raise
    return record


def smoke():
    models = json.load(urllib.request.urlopen(URL + '/v1/models',timeout=30))
    assert [x['id'] for x in models['data']] == ['Qwen3.5-27B']
    payload = {'model':'Qwen3.5-27B','messages':[{'role':'user','content':'Reply only OK'}],
               'temperature':0,'max_tokens':8,'chat_template_kwargs':{'enable_thinking':False}}
    request = urllib.request.Request(URL + '/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    result = json.load(urllib.request.urlopen(request,timeout=30))
    assert result['choices'][0]['message']['content'].strip() == 'OK'


def stop_eval(process):
    if process is None: return
    # Popen owns this still-live group; children inherit a unique token too.
    if process.poll() is None:
        os.killpg(process.pid,signal.SIGTERM)
        try: process.wait(timeout=25)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL); process.wait(timeout=10)
    # Vendor's subprocess may survive a parent killed by a signal; kill only
    # authenticated inherited-token children, even when the group leader died.
    token = getattr(process, 'e14_owner_token', None)
    if token:
        marker = f'E14_EVAL_OWNER_TOKEN={token}'.encode()
        for row in subprocess.check_output(['ps','-eo','pid=,pgid='],text=True).splitlines():
            pid, group = map(int,row.split())
            if group != process.pid: continue
            try:
                started = ticks(pid)
                if marker in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0') and ticks(pid) == started:
                    os.kill(pid,signal.SIGKILL)
            except (FileNotFoundError,PermissionError,ProcessLookupError): pass


def batch():
    assert socket.gethostname().startswith('fvcrc12')
    d = ROOT / 'eval_batch'; d.mkdir(exist_ok=False)
    state = {'started_utc':utc(),'driver_pid':os.getpid(),'driver_start_ticks':ticks(os.getpid()),
             'driver_source_sha256':digest(SELF),'source_git_sha':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),
             'status':'waiting_training','runs':[],'terminal_models':[],'model_copy_bytes':0,
             'total_A100_cap_seconds':TOTAL_CAP,'judge_cap_seconds':JUDGE_CAP,'API_paid_requests':0}
    owner_token = uuid.uuid4().hex; state['judge_owner_token'] = owner_token
    process = None; judge_started = False; judge_deadline = None; train_spent = 0.0; eval_spent = 0.0; active_start = None; entry = None
    def save(): write(d / 'state.json',state)
    def interrupted(signum, frame): raise RuntimeError(f'Coordinator received signal {signum}')
    signal.signal(signal.SIGTERM,interrupted); signal.signal(signal.SIGINT,interrupted)
    save()
    try:
        while True:
            status = training_status(); train_spent = status['train_queue_wrapper_seconds']; write(d / 'training_status.json',status)
            assert not status['failures'], 'Training failed; both original branches required, no survivor eval'
            if status['ready'] and status['budget_watch'] and status['budget_watch']['status'] == 'queues_completed': break
            # A lost queue driver cannot leave this waiter pretending progress.
            for queue in status['queues']:
                if queue.get('status') not in ('completed','failed'):
                    assert ticks(queue['driver_pid']) == queue['driver_start_ticks'], 'Training queue driver disappeared'
            time.sleep(30)
        verify_terminal(status)
        train_spent = status['train_queue_wrapper_seconds']
        state['train_queue_wrapper_seconds'] = train_spent
        state['environment'] = environment(); state['status'] = 'hashing_local_terminals'; save()
        for name in RUNS:
            state['terminal_models'].append({'name':name, **terminal_hash(ROOT / 'train_runs' / name / 'model')}); save()
        while not gpu_available(0,75000): time.sleep(30)
        state['environment_before_judge'] = environment(); state['status'] = 'waiting_judge_gpu3_port8033'; save()
        while True:
            if gpu_available(0,75000) and remote('--judge-idle') and gpu_available(0,75000): break
            time.sleep(30)
        state['status'] = 'judge_starting'; save()
        # If SSH loses the successful response, the finally block still probes
        # only the matching owner token and cleans up that launch.
        assert gpu_available(0,75000), 'Student GPU became busy before judge launch; judge not started'
        judge_started = True
        judge = remote('--judge-start','--owner-token',owner_token,python=JUDGE_PYTHON)
        state['judge_launch'] = judge; save()
        judge_deadline = dt.datetime.fromisoformat(judge['started_utc']) + dt.timedelta(seconds=JUDGE_CAP-120)
        startup_deadline = time.monotonic() + 1800
        while True:
            try: smoke(); break
            except Exception:
                assert time.monotonic() < startup_deadline, 'Judge startup timeout'
                time.sleep(15)
        for name in RUNS:
            while not gpu_available(0,75000):
                assert dt.datetime.now(dt.timezone.utc) < judge_deadline, 'Judge residency cap while awaiting A100'
                time.sleep(10)
            environment(); smoke()
            assert train_spent + eval_spent < TOTAL_CAP
            out = ROOT / 'eval_runs' / name; assert not out.exists()
            command = [TRAIN_PYTHON,str(SCRIPTS / 'e12_run_eval.py'),'--model',str(ROOT / 'train_runs' / name / 'model'),
                       '--eval-data',str(E12 / 'LMUData'),'--judge-url',URL + '/v1/chat/completions',
                       '--gpu','0','--out',str(out)]
            eval_token = uuid.uuid4().hex
            env = os.environ.copy(); env.update(PATH='/home/xiang/.local/bin:' + env.get('PATH',''),
                    UV_PROJECT_ENVIRONMENT=str(E12 / 'vlmeval_venv'),E14_EVAL_OWNER_TOKEN=eval_token)
            entry = {'name':name,'command':command,'out':str(out),'started_utc':utc(),'owner_token':eval_token}
            state['runs'].append(entry); state['status'] = 'evaluating'; save()
            start = time.monotonic(); active_start = start
            with (d / f'{name}.stdout').open('x') as stdout, (d / f'{name}.stderr').open('x') as stderr:
                process = subprocess.Popen(command,cwd=REPO,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
                process.e14_owner_token = eval_token
                entry.update(pid=process.pid,start_ticks=ticks(process.pid),process_group=process.pid); save()
                while process.poll() is None:
                    current = time.monotonic() - start
                    state['total_train_eval_wrapper_seconds'] = train_spent + eval_spent + current; save()
                    if train_spent + eval_spent + current >= TOTAL_CAP-45 or dt.datetime.now(dt.timezone.utc) >= judge_deadline:
                        entry['cap_terminated'] = True; stop_eval(process)
                        raise RuntimeError('Allocation cap reached; owned evaluation terminated')
                    time.sleep(5)
            elapsed = time.monotonic()-start; eval_spent += elapsed; active_start = None
            entry.update(returncode=process.returncode,eval_queue_wrapper_wall_seconds=round(elapsed,3),finished_utc=utc()); save()
            assert process.returncode == 0, name
            completion = read(out / 'completion.json')
            assert completion['status'] == 'completed' and completion.get('error') is None
            for log in ('eval_stdout.txt','eval_stderr.txt'):
                assert 'will use exact matching for evaluation' not in (out / log).read_text(errors='replace'), 'Judge fallback'
            sys.path.insert(0,str(SCRIPTS))
            from e12_validate_eval import validate_results
            fresh = validate_results(read(out / 'results/results.json')); saved = read(out / 'validated_scores.json')
            assert fresh['benchmarks'] == saved['benchmarks'] and fresh['accuracy_percent'] == saved['accuracy_percent']
            manifest = read(out / 'eval_manifest.json')
            assert set(manifest['benchmarks']) == set(BENCHMARKS) and manifest['gpu'] == 0 and manifest['judge_url'] == URL + '/v1/chat/completions'
            entry.update(completion=completion,validated_scores=saved); save()
            results = REPO / 'workbench/data-centric-rsi/results'
            for suffix, source in [('raw_results',out / 'results/results.json'),('validated_scores',out / 'validated_scores.json'),
                                   ('eval_manifest',out / 'eval_manifest.json'),('completion',out / 'completion.json')]:
                destination = results / f'E14_{name}_{suffix}.json'
                # Exclusive destination prevents a race from overwriting prior evidence.
                with source.open('rb') as src, destination.open('xb') as dst: shutil.copyfileobj(src,dst)
            process = None
        state['status'] = 'two_evaluations_completed'; save()
    except Exception as error:
        state.update(status='failed',error=str(error)); stop_eval(process)
        if active_start is not None:
            elapsed = time.monotonic()-active_start; eval_spent += elapsed; active_start = None
            entry.update(returncode=process.returncode if process else None,
                         eval_queue_wrapper_wall_seconds=round(elapsed,3),finished_utc=utc())
        save(); raise
    finally:
        if judge_started:
            try:
                owned = remote('--judge-owned','--owner-token',owner_token)
                if owned:
                    drain_until = judge_deadline or dt.datetime.now(dt.timezone.utc)
                    while dt.datetime.now(dt.timezone.utc) < drain_until:
                        try:
                            _, values = metrics()
                            if pending(values) == 0: break
                        except Exception: break
                        time.sleep(10)
                    state['judge_cleanup'] = remote('--judge-stop','--owner-token',owner_token,
                        *(['--failure-cleanup'] if state['status'] != 'two_evaluations_completed' else []))
            except Exception as error:
                state['cleanup_error'] = str(error)
                try: state['judge_cleanup'] = remote('--judge-stop','--owner-token',owner_token,'--failure-cleanup')
                except Exception as cleanup_error: state['cleanup_error'] += '; ' + str(cleanup_error)
        state.update(finished_utc=utc(),train_queue_wrapper_seconds=train_spent,
                     successful_and_failed_eval_wrapper_seconds=eval_spent,
                     total_train_eval_wrapper_seconds=train_spent+eval_spent)
        save()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--environment',action='store_true'); p.add_argument('--train-status',action='store_true')
    p.add_argument('--judge-environment',action='store_true'); p.add_argument('--judge-idle',action='store_true'); p.add_argument('--judge-start',action='store_true')
    p.add_argument('--judge-owned',action='store_true'); p.add_argument('--judge-stop',action='store_true')
    p.add_argument('--judge-watch',action='store_true'); p.add_argument('--failure-cleanup',action='store_true')
    p.add_argument('--owner-token'); p.add_argument('--run-batch',action='store_true')
    a = p.parse_args()
    if a.judge_start or a.judge_owned or a.judge_stop or a.judge_watch: assert a.owner_token
    if a.environment: result = environment()
    elif a.train_status: result = training_status()
    elif a.judge_environment: result = judge_environment()
    elif a.judge_idle:
        assert socket.gethostname().startswith('fvcrc20')
        result = gpu_available(3,80000) and port_free()
    elif a.judge_start: result = judge_start(a.owner_token)
    elif a.judge_owned:
        path = ROOT / 'judge/launch_manifest.json'
        result = path.exists() and read(path).get('owner_token') == a.owner_token
    elif a.judge_stop: result = judge_stop(a.owner_token,a.failure_cleanup)
    elif a.judge_watch: judge_watch(a.owner_token); return
    elif a.run_batch: batch(); return
    else: p.error('Select one operation')
    print(json.dumps(result))


if __name__ == '__main__': main()
