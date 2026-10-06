"""Worker that evaluates finished checkpoints according to the E21 protocol.

Several workers can run concurrently (one per GPU slot); each task is claimed with an atomic
lock file. Results: <run>/eval/<ckpt>_<task-key>.json (one file per (offset, budget)).
"""
import argparse
import glob
import json
import os
import socket
import time
from pathlib import Path

from eval_plan import run

N = 200


def plan_for(run_dir):
    task = json.loads((Path(run_dir) / 'config.json').read_text())['task']
    steps = json.loads((Path(run_dir) / 'config.json').read_text())['steps']
    offsets = [25, 50, 75] if task == 'tworoom' else [25, 50]
    jobs = []
    for ck in [5000, 20000, steps]:
        for off in offsets:
            if ck != steps and off == 75:
                continue
            jobs.append((ck, off, 300, 30))
    for off in [25, 50]:
        for s, it in [(30, 3), (100, 10), (1000, 30), (3000, 30)]:
            jobs.append((steps, off, s, it))
    return task, jobs


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--roots', required=True, help='comma-separated glob(s) of run dirs')
    p.add_argument('--once', action='store_true')
    a = p.parse_args()
    host = socket.gethostname()
    while True:
        did = False
        runs = sorted(set(sum([glob.glob(g) for g in a.roots.split(',')], [])))
        # cheaper first: earlier checkpoints and default budget before sweeps
        todo = []
        for r in runs:
            if not (Path(r) / 'config.json').exists():
                continue
            task, jobs = plan_for(r)
            final = json.loads((Path(r) / 'config.json').read_text())['steps']
            for ck, off, s, it in jobs:
                default = (s, it) == (300, 30)
                pri = 0 if (ck == final and default) else 1 if (ck == 20000 and default) else 3 if ck == 5000 else 2
                todo.append(((pri, s * it, off), ck, r, task, off, s, it))
        todo.sort()
        for _, ck, r, task, off, s, it in todo:
            ckpt = Path(r) / f'model_{ck:07d}.pt'
            if not ckpt.exists():
                continue
            ed = Path(r) / 'eval'
            ed.mkdir(exist_ok=True)
            key = f'{ck:07d}_off{off}_{s}x{it}_n{N}'
            res, lock = ed / f'{key}.json', ed / f'{key}.lock'
            if res.exists():
                continue
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f'{host} {os.getpid()} {time.time()}'.encode())
                os.close(fd)
            except FileExistsError:
                continue
            try:
                if (ed / f'{key}.fail').exists():
                    continue
                out = run(str(ckpt), task, off, N, s, it, min(30, s // 2), 5, 0)
                out['eval_host'] = host
                res.write_text(json.dumps(out))
            except Exception as e:  # keep the worker alive; record the failure (OOM is transient: retry later)
                import traceback
                import torch
                torch.cuda.empty_cache()
                if 'out of memory' not in repr(e).lower():
                    (ed / f'{key}.fail').write_text(traceback.format_exc())
                else:
                    lock.unlink(missing_ok=True)
                    time.sleep(600)  # wait for memory to free up instead of hammering the GPU
                print('FAIL', r, key, repr(e), flush=True)
                continue
                print(json.dumps({'run': Path(r).name, 'ck': ck, 'off': off, 'budget': f'{s}x{it}',
                                  'sr': out['success_rate'], 'sec': round(out['seconds'])}), flush=True)
            finally:
                lock.unlink(missing_ok=True)
            did = True
            break  # rescan so cheap tasks from newly finished checkpoints go first
        if not did:
            if a.once:
                return
            time.sleep(60)


if __name__ == '__main__':
    main()
