"""Move the fixed native confirmation after resource contention; retain the attempt."""
import argparse, datetime, gc, hashlib, ipaddress, json, os, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/e131'
DEST = BASE / 'llama70_confirmation_native'
ARCHIVE = BASE / 'llama70_confirmation_native_fvcrc10_interrupted'
MODEL = '/tmp/ices_models/Llama-3.1-70B'
CLAIM = BASE / '.llama70_confirmation_native_restart_claim.json'
FROZEN = {
    'e131_protocol.py':'550890014e6553290695f7fb6f35823a4b25ef06acca551649934a69d30b643f',
    'e131_dispatch.py':'5abd14f91ac0cd56f40e714413d83d066ff4173af5a24e0de1cd4788a5f0beb9',
    'e131_mechanism.py':'75290f9f3d354e981955b7482f09122c60d80f664d0bd8639f2b4ef0aec78961',
    'e131_native.py':'a4285fe0eba3818f6cd8e6cc677dca0fac2c5be2e05bbb3fbc8c3b5b17a90f80',
    'e131_function.py':'b145f6278e9217930f07640535dcd782daec89157caed3c8c808e05f408fb428'}

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def stop_legacy(parent, worker):
    assert os.uname().nodename == 'fvcrc10'
    expected = ['/home/xiang/miniconda3/envs/verl-clean/bin/python',
                'scripts/e131_protocol.py', '--family', 'llama70',
                '--model', MODEL, '--phases', 'confirmation']
    assert [x.decode() for x in Path(f'/proc/{worker}/cmdline').read_bytes().split(b'\0')[:-1]] == expected
    assert str(worker) in Path(f'/proc/{parent}/task/{parent}/children').read_text().split()
    assert json.loads((BASE / '.llama70_confirmation_launch_claim.json').read_text())['queue_pid'] == parent
    assert not ARCHIVE.exists()
    os.kill(worker, signal.SIGSTOP)
    stopped = True
    try:
        deadline = time.monotonic() + 10
        while 'State:\tT' not in Path(f'/proc/{worker}/status').read_text():
            assert time.monotonic() < deadline
            time.sleep(.02)
        raw = DEST / 'behavior.jsonl'
        count = raw.read_bytes().count(b'\n') if raw.exists() else 0
        if (DEST / 'run.json').exists() or count >= 32:
            print(json.dumps({'status': 'ALREADY_FINISHING', 'rows': count}), flush=True)
            return
        assert 0 < count < 32
        record = {'status': 'EXECUTION_INTERRUPTED_FOR_RESOURCE_MIGRATION',
                  'created_at_utc': utc(), 'legacy_host': 'fvcrc10',
                  'legacy_parent_pid': parent, 'legacy_worker_pid': worker,
                  'partial_rows': count, 'planned_rows': 32,
                  'partial_raw_sha256': sha(raw), 'archive': str(ARCHIVE),
                  'reason': 'Other compute processes began sharing the four GPUs after launch.',
                  'scientific_selection': False, 'scientific_protocol_changed': False,
                  'restart_host': 'fvcrc20', 'stage': 'native', 'seed': 131101}
        os.kill(worker, signal.SIGTERM)
        os.kill(worker, signal.SIGCONT)
        stopped = False
        deadline = time.monotonic() + 30
        while Path(f'/proc/{worker}').exists():
            if 'State:\tZ' in Path(f'/proc/{worker}/status').read_text():
                break
            assert time.monotonic() < deadline, 'Owned writer has not exited; do not archive'
            time.sleep(.1)
        assert not Path(f'/proc/{worker}').exists() or 'State:\tZ' in Path(f'/proc/{worker}/status').read_text()
        # Only this terminated writer's incomplete output moves; the function fence is untouched.
        DEST.rename(ARCHIVE)
        assert sha(ARCHIVE / 'behavior.jsonl') == record['partial_raw_sha256']
        DEST.mkdir()
        save(ARCHIVE / 'operational_interruption.json', record)
        save(DEST / 'operational_restart.json', record)
        journal = BASE / 'worker_llama70_confirmation.json'
        old = json.loads(journal.read_text())
        assert old['host'] == 'fvcrc10' and old['num_devices'] == 4
        save(ARCHIVE / 'worker_journal_before_interruption.json', old)
        now = time.time()
        old.update(last_observed_at=now, resident_device_hours_so_far=(now-old['started_at'])/3600*4,
                   worker_terminated_for_rescheduling=True, worker_complete=False,
                   failed=True, error=record['reason'], failure_class='OPERATIONAL_RESCHEDULING')
        save(journal, old)
        print(json.dumps(record), flush=True)
    finally:
        if stopped and Path(f'/proc/{worker}').exists():
            os.kill(worker, signal.SIGCONT)

def launch(parent, worker):
    assert os.uname().nodename == 'fvcrc20'
    os.chdir(ROOT)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    assert subprocess.check_output(['git', 'show', commit+':workbench/in-context-evidence-structure/scripts/e131_native_restart.py']) == Path(__file__).read_bytes()
    for name, expected in FROZEN.items():
        path = ROOT/'scripts'/name
        assert sha(path) == expected
        assert subprocess.check_output(['git','show',commit+':workbench/in-context-evidence-structure/scripts/'+name]) == path.read_bytes()
    review = json.loads((BASE/'native_migration_static_review_2026-10-12.json').read_text())
    assert review['status'] == 'PASS_STATIC_RUNTIME_GUARDS_REQUIRED'
    assert review['native_restart_helper_sha256'] == sha(Path(__file__))
    assert review['peer_helper_sha256'] == sha(BASE/'peer_distribution_helper_fvcrc20.py')
    info = json.loads((BASE / 'model_identity_llama70_fvcrc20.json').read_text())
    assert info['host'] == 'fvcrc20' and info['target'] == MODEL
    assert info['repo'] == 'NousResearch/Meta-Llama-3.1-70B'
    assert info['revision'] == 'beb678ba5bd7eb1aafeffa01e2a2b3b5e93d1dd3'
    assert info['all_weights_sha256_passed'] and info['official_mirror_all30_match']
    rows = subprocess.check_output(['nvidia-smi', '--query-gpu=index,memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True).splitlines()
    assert len(rows) == 4 and all(float(r.split(',')[1]) < 128 and float(r.split(',')[2]) == 0 for r in rows)
    assert not CLAIM.exists()
    os.environ.update(CUDA_VISIBLE_DEVICES='0,1,2,3', PYTHONUNBUFFERED='1', OMP_NUM_THREADS='6', HF_HUB_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    import torch
    import e131_protocol as protocol
    assert protocol.STAGES['native'] == {'conditions':64, 'discovery_seed':120001, 'confirmation_seed':131101}
    # Check this CUDA runtime before stopping the existing computation.
    held = [torch.zeros(1, device=f'cuda:{i}') for i in range(4)]
    for i in range(4):
        torch.cuda.synchronize(i)
    fd = os.open(CLAIM, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    record = {'host': 'fvcrc20', 'pid': os.getpid(), 'stage': 'native', 'phase': 'confirmation',
              'seed':131101, 'n':32, 'conditions':64, 'started_at_utc':utc(),
              'helper_sha256':sha(Path(__file__)), 'scientific_protocol_changed':False}
    with os.fdopen(fd, 'w') as f:
        json.dump(record, f, indent=2); f.write('\n')
    try:
        connection = ['ssh', '-o', 'LogLevel=ERROR', '-o', 'IdentityAgent=none', '-o', 'ProxyCommand=none', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=7']
        address = os.environ.get('ICES_E131_LEGACY_ADDRESS')
        if address:
            ipaddress.ip_address(address)
            connection += ['-o', 'HostName='+address, '-o', 'HostKeyAlias=fvcrc10']
        output = subprocess.check_output(connection + ['fvcrc10',
                                         f'cd {ROOT} && python3 scripts/e131_native_restart.py --stop-legacy --legacy-parent {parent} --legacy-worker {worker}'], text=True)
        handoff = json.loads(output)
        if handoff['status'] == 'ALREADY_FINISHING':
            record.update(status='LEGACY_FINISHED_BEFORE_MIGRATION', scientific_rows=0)
            return
        assert handoff['status'] == 'EXECUTION_INTERRUPTED_FOR_RESOURCE_MIGRATION'
        deadline = time.monotonic() + 60
        while not (DEST / 'operational_restart.json').exists() or (DEST / 'behavior.jsonl').exists():
            assert time.monotonic() < deadline
            time.sleep(.5)
        assert json.loads((DEST / 'operational_restart.json').read_text()) == handoff
        del held; gc.collect(); torch.cuda.empty_cache()
        protocol.STAGES = {'native': protocol.STAGES['native']}
        def journal(args, resident, label, complete, error=None):
            now = time.time()
            save(BASE / 'worker_llama70_confirmation_native_restarted.json',
                 {'family':args.family, 'host':'fvcrc20', 'model':args.model,
                  'started_at':resident['started_at'], 'last_observed_at':now,
                  'num_devices':resident['num_devices'],
                  'resident_device_hours_so_far':(now-resident['started_at'])/3600*resident['num_devices'],
                  'scope':'Continuous restart residency, including loading and analysis; interrupted 10 attempt remains separately counted.',
                  'last_stage':label, 'worker_complete':complete, 'failed':error is not None,
                  'error':error, 'schedule_helper_sha256':record['helper_sha256']})
        protocol.record_worker = journal
        sys.argv = [str(ROOT/'scripts/e131_protocol.py'), '--family','llama70','--model',MODEL,'--phases','confirmation']
        protocol.main()
        record.update(worker_exit_code=0, finished_at_utc=utc())
    except BaseException as exc:
        record.update(worker_exit_code=1, error=repr(exc)); raise
    finally:
        record['last_observed_at_utc'] = utc()
        save(CLAIM, record)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--stop-legacy', action='store_true')
    p.add_argument('--legacy-parent', type=int, required=True)
    p.add_argument('--legacy-worker', type=int, required=True)
    a = p.parse_args()
    if a.stop_legacy:
        stop_legacy(a.legacy_parent, a.legacy_worker)
    else:
        launch(a.legacy_parent, a.legacy_worker)
