"""Tiny per-node scheduler: launch queued training jobs onto GPUs with free memory.

jobs file lines: <need_GB> <task> <size> <seed> <episodes> <steps> [extra args...]
A job is started when some GPU has >= need_GB free and < cap of our train processes.
Started jobs are recorded in <jobs>.started; rerunning is idempotent (launch.sh skips complete runs).
"""
import argparse
import subprocess
import time
from pathlib import Path


def gpu_free():
    out = subprocess.check_output(['nvidia-smi', '--query-gpu=index,memory.total,memory.used',
                                   '--format=csv,noheader,nounits'], text=True)
    res = {}
    for line in out.strip().splitlines():
        i, tot, used = [int(x) for x in line.split(',')]
        res[i] = (tot - used) / 1024
    return res


def our_jobs_per_gpu():
    out = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader'], text=True)
    uu = subprocess.check_output(['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'], text=True)
    m = {u.strip(): int(i) for i, u in (l.split(',') for l in uu.strip().splitlines())}
    cnt = {i: 0 for i in m.values()}
    for line in out.strip().splitlines():
        if not line.strip():
            continue
        u, pid = [x.strip() for x in line.split(',')]
        try:
            args = Path(f'/proc/{pid}/cmdline').read_text().replace('\0', ' ')
        except Exception:
            continue
        if 'train.py' in args:
            cnt[m[u]] += 1
    return cnt


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--jobs', required=True)
    p.add_argument('--cap', type=int, default=3)
    p.add_argument('--gpus', default='0,1,2,3')
    a = p.parse_args()
    gpus = [int(x) for x in a.gpus.split(',')]
    started_f = Path(a.jobs + '.started')
    while True:
        started = set(started_f.read_text().splitlines()) if started_f.exists() else set()
        jobs = [l.strip() for l in Path(a.jobs).read_text().splitlines() if l.strip() and not l.startswith('#')]
        pending = [j for j in jobs if j not in started]
        if not pending:
            time.sleep(120)
            continue
        free, cnt = gpu_free(), our_jobs_per_gpu()
        launched = False
        for j in pending:
            need = float(j.split()[0])
            cands = [g for g in gpus if free[g] >= need and cnt[g] < a.cap]
            if not cands:
                continue
            g = max(cands, key=lambda x: free[x])
            args = j.split()[1:]
            out = subprocess.check_output(['./launch.sh', str(g)] + args, text=True,
                                          cwd=str(Path(__file__).parent))
            print(time.strftime('%H:%M:%S'), 'gpu', g, out.strip(), flush=True)
            with open(started_f, 'a') as f:
                f.write(j + '\n')
            launched = True
            break
        time.sleep(90 if launched else 120)


if __name__ == '__main__':
    main()
