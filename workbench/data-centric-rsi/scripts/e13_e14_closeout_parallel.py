"""Finish only the eight already-trained E13/E14 terminals using frozen E12 eval.

Operational recovery: local judge weights, idle-card discovery, one shared judge,
individually authenticated descendants across process groups, independent guard.
No retraining, new candidates, new seeds, or checkpoint selection.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import argparse
import datetime as dt
import fcntl
import json
import math
import os
from pathlib import Path
import shlex
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import uuid

import e13_eval_batch_v2 as frozen
from e14_eval_batch import digest, ticks, write, read
from e12_validate_eval import validate_results

BASE = Path('/var/tmp/xiang-data-rsi/closeout')
SELF = Path(__file__).resolve()
REPO = frozen.REPO
PORT = 8034
URL = f'http://fvcrc20:{PORT}'
TOKEN_KEY = 'RSI_CLOSEOUT_OWNER'
JUDGE_CAP = 8 * 3600  # Recovery allocation, additional to the failed old attempt.
EVAL_CAP = 3 * 3600
TOTAL_CAP = {'E13':18*3600, 'E14':8*3600}
TRAIN_SPENT = {'E13':32131.095, 'E14':7490.509}
RUNS = [('E13', n, 'fvcrc13', f'/var/tmp/xiang-data-rsi/e13/train_runs/{n}/model') for n in frozen.RUNS]
RUNS += [('E14', f'{p}_source_only_fresh_s29', 'fvcrc10', f'/var/tmp/xiang-data-rsi/e14/copied_models/{p}_source_only_fresh_s29') for p in ('init', 'used')]


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def rpc(node, *args):
    return json.loads(subprocess.check_output(['ssh', '-o', 'ConnectTimeout=15', node, shlex.join(['python3', str(SELF), *map(str, args)])], text=True, timeout=600))


def owned(token):
    """The token, not PPID/PGID/command name, authenticates each live process."""
    assert len(token) == 32 and all(c in '0123456789abcdef' for c in token)
    marker = f'{TOKEN_KEY}={token}'.encode()
    result = []
    for directory in Path('/proc').iterdir():
        if not directory.name.isdigit(): continue
        try:
            stat = (directory / 'stat').read_text().rsplit(')', 1)[1].split()
            if stat[0] == 'Z': continue
            if marker in (directory / 'environ').read_bytes().split(b'\0'):
                result.append({'pid':int(directory.name), 'start_ticks':stat[19]})
        except (FileNotFoundError, PermissionError, ProcessLookupError): pass
    return result


def cleanup(token):
    before = owned(token)
    for sig, seconds in ((signal.SIGTERM, 20), (signal.SIGKILL, 10)):
        for process in owned(token):
            if ticks(process['pid']) == process['start_ticks']:
                try: os.kill(process['pid'], sig)
                except ProcessLookupError: pass
        end = time.monotonic() + seconds
        while owned(token) and time.monotonic() < end: time.sleep(.2)
        if not owned(token): break
    return {'utc':utc(), 'before':before, 'remaining':owned(token)}


def idle():
    rows = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.free','--format=csv,noheader,nounits'], text=True).splitlines()
    apps = subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'], text=True)
    minimum = 80000 if socket.gethostname().startswith('fvcrc20') else 75000
    return [int(i) for i, u, free in (tuple(x.strip() for x in row.split(',')) for row in rows) if int(free) >= minimum and u not in apps]


def guard(directory):
    m = read(directory / 'launch.json')
    deadline = dt.datetime.fromisoformat(m['started_utc']).timestamp() + m['cap_seconds']
    while time.time() < deadline:
        if (directory / 'cleanup.json').exists() and not owned(m['token']): return
        # Also catch a worker/coordinator dying unexpectedly after server launch.
        if ticks(m['owner_pid']) != m['owner_ticks']:
            break
        time.sleep(10)
    result = cleanup(m['token'])
    result['reason'] = 'allocation deadline or owner exited'
    write(directory / 'guard_cleanup.json', result)


def launch(command, directory, gpu, cap, token):
    directory.mkdir(parents=True, exist_ok=False)
    assert gpu in idle(), 'Selected card acquired another workload before launch'
    env = os.environ.copy()
    env.update({TOKEN_KEY:token, 'CUDA_DEVICE_ORDER':'PCI_BUS_ID', 'VLLM_USE_FLASHINFER_SAMPLER':'0',
                'PATH':'/home/xiang/.local/bin:' + env.get('PATH',''),
                'UV_PROJECT_ENVIRONMENT':str(frozen.E12 / 'vlmeval_venv')})
    if socket.gethostname().startswith('fvcrc20'): env['CUDA_VISIBLE_DEVICES'] = str(gpu)
    m = {'started_utc':utc(), 'command':command, 'gpu':gpu, 'token':token, 'cap_seconds':cap,
         'owner_pid':os.getpid(), 'owner_ticks':ticks(os.getpid()), 'source_sha256':digest(SELF),
         'source_git_sha':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()}
    with (directory / 'stdout').open('x') as log:
        p = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    m.update(pid=p.pid, start_ticks=ticks(p.pid))
    write(directory / 'launch.json', m)
    with (directory / 'guard.log').open('x') as log:
        g = subprocess.Popen(['python3',str(SELF),'guard','--directory',str(directory)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    m.update(guard_pid=g.pid, guard_ticks=ticks(g.pid)); write(directory / 'launch.json', m)
    return p, m


def smoke():
    models = json.load(urllib.request.urlopen(URL + '/v1/models', timeout=10))
    assert [x['id'] for x in models['data']] == ['Qwen3.5-27B']
    payload = {'model':'Qwen3.5-27B','messages':[{'role':'user','content':'Reply only OK'}], 'temperature':0,'max_tokens':8,'chat_template_kwargs':{'enable_thinking':False}}
    req = urllib.request.Request(URL+'/v1/chat/completions', data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    r = json.load(urllib.request.urlopen(req,timeout=30))
    assert r['choices'][0]['message']['content'].strip() == 'OK'


def student(experiment, name, gpu, attempt, cap_seconds):
    item = next(r for r in RUNS if r[:2] == (experiment,name))
    assert socket.gethostname().startswith(item[2])
    d = BASE / attempt / name
    env_audit = frozen.environment()
    model = Path(item[3])
    if experiment == 'E13':
        old = read(REPO / 'workbench/data-centric-rsi/results/E13_original_eval_wait_state.json')
        expected = next(c['target_files'] for c in old['copies'] if c['name'] == name)
    else:
        old = read(REPO / 'workbench/data-centric-rsi/results/E14_original_eval_attempt_state.json')
        expected = next(c['files'] for c in old['terminal_models'] if c['name'] == name)
    actual = frozen.files(model)
    assert actual == expected, 'Terminal weights differ from previously hashed training output'
    smoke()
    out = d / 'eval'
    command = [frozen.TRAIN_PYTHON, str(SELF.parent / 'e12_run_eval.py'), '--model',str(model),'--eval-data',str(frozen.E12 / 'LMUData'), '--judge-url',URL+'/v1/chat/completions','--gpu',str(gpu),'--out',str(out)]
    token = uuid.uuid4().hex
    assert 60 < cap_seconds <= EVAL_CAP
    p, m = launch(command,d,gpu,cap_seconds,token)
    write(d / 'preflight.json', {'environment':env_audit,'terminal_files':actual})
    start = time.monotonic()
    result = {'experiment':experiment, 'name':name, 'launch':m, 'status':'running'}
    try:
        rc = p.wait(timeout=cap_seconds-45)
        assert rc == 0, f'Eval returned {rc}'
        completion = read(out / 'completion.json')
        assert completion['status'] == 'completed' and completion.get('error') is None
        for log in ('eval_stdout.txt','eval_stderr.txt'):
            assert 'will use exact matching for evaluation' not in (out / log).read_text(errors='replace')
        scores = validate_results(read(out / 'results/results.json'))
        saved = read(out / 'validated_scores.json')
        assert math.isclose(scores['accuracy_percent'], saved['accuracy_percent'], rel_tol=0, abs_tol=1e-12)
        assert set(scores['benchmarks']) == set(saved['benchmarks'])
        for benchmark, row in scores['benchmarks'].items():
            other = saved['benchmarks'][benchmark]
            assert row['field'] == other['field']
            assert all(math.isclose(row[k], other[k], rel_tol=0, abs_tol=1e-12) for k in ('raw', 'max', 'normalized'))
        manifest = read(out / 'eval_manifest.json')
        assert manifest['gpu'] == gpu and manifest['judge_url'] == URL+'/v1/chat/completions'
        assert manifest['use_vllm'] and set(manifest['benchmarks']) == set(frozen.BENCHMARKS)
        result.update(status='completed', scores=saved, completion=completion)
        for suffix, source in [('raw_results',out/'results/results.json'),('validated_scores',out/'validated_scores.json'),('eval_manifest',out/'eval_manifest.json'),('completion',out/'completion.json')]:
            dst = REPO / 'workbench/data-centric-rsi/results' / f'{experiment}_{name}_{suffix}.json'
            with dst.open('xb') as f: f.write(source.read_bytes())
    except Exception as error:
        result.update(status='failed',error=repr(error)); raise
    finally:
        result['cleanup'] = cleanup(token)
        result.update(finished_utc=utc(),eval_wrapper_seconds=time.monotonic()-start,returncode=p.poll())
        write(d/'cleanup.json',result['cleanup'])
        write(d/'result.json',result)
    return result


def coordinator(attempt):
    assert socket.gethostname().startswith('fvcrc20')
    directory = BASE / attempt
    directory.mkdir(parents=True,exist_ok=False)
    lock = (BASE/'coordinator.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    stage = read(BASE/'model_verified.json')
    assert stage['all_equal'] and stage['revision'] == Path(frozen.JUDGE_MODEL).name
    for f in stage['files']:
        p = BASE/'model'/f['path']; assert p.stat().st_size == f['bytes']
        assert p.stat().st_mtime <= dt.datetime.fromisoformat(stage['utc']).timestamp()
    version = subprocess.check_output([frozen.JUDGE_PYTHON,'-c','import importlib.metadata;print(importlib.metadata.version("vllm"))'],text=True).strip()
    assert version == '0.23.0+cu129'
    state = {'started_utc':utc(),'status':'waiting_idle_cards','runs':[],'active':[],
             'scope':'eight existing terminal models only, parallel independent single-A100 evaluations',
             'prior_failure_audit':'E14_judge_startup_failure_audit.json',
             'judge_recovery_cap_seconds':JUDGE_CAP,'API_paid_requests':0,
             'driver_pid':os.getpid(),'driver_ticks':ticks(os.getpid()),
             'verified_judge_manifest_sha256':digest(BASE/'model_verified.json')}
    def save(): write(directory/'state.json',state)
    def evaluate(item,gpu,cap):
        experiment,name,node,model=item
        command=['ssh',node,shlex.join(['python3',str(SELF),'student','--experiment',experiment,'--name',name,'--gpu',str(gpu),'--attempt',attempt,'--cap-seconds',str(cap)])]
        with (directory/f'{name}.log').open('x') as log:
            rc=subprocess.call(command,stdout=log,stderr=subprocess.STDOUT)
        try: result=rpc(node,'result','--directory',str(BASE/attempt/name))
        except Exception as error:
            result={'experiment':experiment,'name':name,'status':'failed_before_result','error':repr(error)}
        result['ssh_returncode']=rc
        return result
    save()
    pending=list(RUNS); active={}; judge=None; token=uuid.uuid4().hex
    pool=ThreadPoolExecutor(max_workers=5)
    try:
        while pending or active:
            for future in list(active):
                if future.done():
                    result=future.result(); state['runs'].append(result); del active[future]
                    save()
            state['active']=list(active.values()); save()
            choices=[]
            reserved={(r['node'],r['gpu']) for r in active.values()}
            for node in sorted({r[2] for r in pending}):
                available=[g for g in rpc(node,'idle') if (node,g) not in reserved]
                candidates=[r for r in pending if r[2]==node]
                if node=='fvcrc10':
                    copied=REPO/'workbench/data-centric-rsi/results/E14_closeout_copy_provenance.json'
                    if not copied.exists() or len(read(copied))!=2: continue
                choices.extend(zip(candidates,available))
            if judge is not None:
                assert judge.poll() is None, 'Judge exited before all terminal evaluations finished'
            if not choices:
                if not pending and not active: break
                time.sleep(10); continue
            if judge is None:
                available=idle()
                if not available: time.sleep(30); continue
                with socket.socket() as s: assert s.connect_ex(('127.0.0.1',PORT)) != 0
                command=[frozen.JUDGE_PYTHON,'-m','vllm.entrypoints.openai.api_server','--model',str(BASE/'model'),'--served-model-name','Qwen3.5-27B','--host','0.0.0.0','--port',str(PORT),'--dtype','bfloat16','--tensor-parallel-size','1','--max-model-len','4096','--max-num-seqs','16','--gpu-memory-utilization','0.78','--default-chat-template-kwargs','{"enable_thinking":false}']
                judge,m=launch(command,directory/'judge',available[0],JUDGE_CAP,token)
                state.update(status='judge_starting',judge=m); save()
                deadline=time.monotonic()+7200
                while True:
                    try: smoke(); break
                    except Exception:
                        assert judge.poll() is None and time.monotonic()<deadline, 'Judge failed readiness'
                        time.sleep(10)
                continue
            for item,gpu in choices:
                experiment,name,node,model=item
                # Conservative per-run reservations keep the sum within the
                # original total allocation even when all workers overlap.
                n=sum(r[0]==experiment for r in RUNS)
                cap=min(EVAL_CAP,int((TOTAL_CAP[experiment]-TRAIN_SPENT[experiment])/n))
                assert cap>60
                future=pool.submit(evaluate,item,gpu,cap)
                active[future]={'experiment':experiment,'name':name,'node':node,'gpu':gpu,'cap_seconds':cap,'submitted_utc':utc()}
                pending.remove(item)
            state.update(status='evaluating',active=list(active.values())); save()
            time.sleep(5)
        assert len(state['runs'])==8 and all(r['status']=='completed' and r['ssh_returncode']==0 for r in state['runs']), 'One or more terminal evaluations failed; preserve all attempts'
        state['status']='eight_evaluations_completed'
    except Exception as error:
        state.update(status='failed',error=repr(error)); raise
    finally:
        # Workers have independent caps and token-based guards; allow their
        # bounded cleanup to complete before shutting down the shared judge.
        pool.shutdown(wait=True)
        for future in list(active):
            try: state['runs'].append(future.result())
            except Exception as error: state.setdefault('worker_errors',[]).append(repr(error))
        state['active']=[]
        if judge:
            try:
                (directory/'judge'/'metrics_final.prom').write_bytes(urllib.request.urlopen(URL+'/metrics',timeout=15).read())
            except Exception as error: state['metrics_error']=repr(error)
            state['judge_cleanup']=cleanup(token)
            write(directory/'judge'/'cleanup.json',state['judge_cleanup'])
            state['judge_launch_to_cleanup_seconds']=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(state['judge']['started_utc'])).total_seconds()
        state['finished_utc']=utc(); save()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['idle','student','coordinator','guard','result'])
    p.add_argument('--experiment');p.add_argument('--name');p.add_argument('--gpu',type=int)
    p.add_argument('--cap-seconds',type=int);p.add_argument('--attempt',default='attempt1');p.add_argument('--directory',type=Path)
    a=p.parse_args()
    def interrupted(signum, frame): raise RuntimeError(f'Closeout received signal {signum}')
    if a.mode in ('coordinator','student'):
        signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    if a.mode=='idle': result=idle()
    elif a.mode=='student': result=student(a.experiment,a.name,a.gpu,a.attempt,a.cap_seconds)
    elif a.mode=='coordinator': result=coordinator(a.attempt)
    elif a.mode=='guard': result=guard(a.directory)
    else: result=read(a.directory/'result.json')
    print(json.dumps(result))

if __name__=='__main__':main()
