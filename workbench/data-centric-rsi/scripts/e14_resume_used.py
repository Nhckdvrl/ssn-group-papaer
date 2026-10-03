"""Resume E14's same used/seed29 action after a pre-training schema failure.

Keep the failed attempt and its allocation in the original queue ledger. The
immutable init launcher and running budget watcher remain untouched.
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import time

from e14_train_queue import (ROOT, REPO, PYTHON, utc, save, start_ticks,
                             available, cap_reached)
import json
import signal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launcher-sha', required=True)
    args = parser.parse_args()
    directory = ROOT / 'train_queue'
    path = directory / 'gpu1.json'
    state = json.loads(path.read_text())
    assert state['status'] == 'failed' and len(state['runs']) == 1
    old = state['runs'][0]
    assert old['returncode'] == 1 and old['parent'] == 'used'
    assert not Path(old['run_dir']).exists(), 'A partial training run cannot use this recovery'
    assert start_ticks(old['launcher_pid']) != old['launcher_start_ticks']
    assert start_ticks(state['driver_pid']) != state['driver_start_ticks']
    assert 'Used model content differs from E13' in (directory / 'used.stderr').read_text()
    launcher = REPO / 'workbench/data-centric-rsi/scripts/e14_run_train_v2.py'
    assert hashlib.sha256(launcher.read_bytes()).hexdigest() == args.launcher_sha
    old.update(failure_phase='CPU parent-manifest name/path schema, before training',
               same_seed_recovery_authorized=True, launcher_sha256=state['launcher_sha256'])
    state['previous_driver_pid'] = state['driver_pid']
    state.update(driver_pid=os.getpid(), driver_start_ticks=start_ticks(os.getpid()),
                 launcher_sha256=args.launcher_sha, status='waiting_for_free_gpu',
                 recovery='Filename schema only; same action/parent/seed/recipe')
    save(path, state)
    while True:
        assert not cap_reached(directory), 'No recovery after training cap'
        idle, free = available(1)
        if idle: break
        time.sleep(30)
    command = list(old['command'])
    assert command[0] == PYTHON
    command[1] = str(launcher)
    entry = {'parent': 'used', 'action': old['action'], 'gpu': 1,
             'command': command, 'started_utc': utc(), 'run_dir': old['run_dir'],
             'prelaunch_free_mib': free, 'prelaunch_no_compute_apps': True,
             'launcher_sha256': args.launcher_sha, 'same_seed_retry_of': 0,
             'seed': 29, 'failure_is_not_seed_selection': True}
    state['runs'].append(entry)
    state['status'] = 'running'; save(path, state)
    env = os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    start = time.monotonic()
    with (directory / 'used_retry1.stdout').open('x') as out, (directory / 'used_retry1.stderr').open('x') as err:
        assert not cap_reached(directory)
        p = subprocess.Popen(command, cwd=REPO, env=env, stdout=out, stderr=err,
                             start_new_session=True)
        entry.update(launcher_pid=p.pid, launcher_start_ticks=start_ticks(p.pid), process_group=p.pid)
        save(path, state)
        if cap_reached(directory):
            try: os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError: pass
        code = p.wait()
    entry.update(returncode=code, finished_utc=utc(),
                 queue_wrapper_wall_seconds=round(time.monotonic() - start, 3))
    state['status'] = 'failed' if code else 'completed'; save(path, state)
    assert code == 0, 'Preserve failure; no replacement seed'
    completion = json.loads((Path(old['run_dir']) / 'completion.json').read_text())
    assert completion['returncode'] == 0 and completion['model_saved'] and completion['observed_windows'] == 625
    entry['completion'] = completion; save(path, state)


if __name__ == '__main__': main()
