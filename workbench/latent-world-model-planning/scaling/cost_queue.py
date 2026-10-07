"""E23 worker: on every finished final checkpoint, measure the metric-horizon curve (full latent L2 and
slow-feature k=4) and run the training-free cost variants (sfa / auto, k=4) at the task's offsets.
Atomic lock files let several workers share the run directories. Writes <run>/eval/mh_<ckpt>.json and
<run>/eval/<mode>_<ckpt>.json (same format as pca_test.py)."""
import argparse
import glob
import json
import socket
import time
from pathlib import Path

import torch

from eval_plan import metric_horizon, run, sfa_basis

OFFS = {'tworoom': [25, 50, 75], 'pmazemedium': [50, 100, 200], 'pmazelarge': [50, 100, 200],
        'vantmazemedium': [25, 50, 100]}


def wanted(name):
    # base runs and SIGReg-weight runs; other variants (latent dim, aux, data size) are E21/E22 material
    tail = name.split('_st60000')[-1]
    return tail == '' or tail.startswith('sigreg_w')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--roots', default='/tmp/latent-wm-runs/scaling/*,/home/xiang/.cache/latent-wm-results/scaling/*')
    p.add_argument('--modes', default='sfa,auto')
    p.add_argument('--tasks', default='')
    a = p.parse_args()
    host = socket.gethostname()
    while True:
        did = False
        runs = sorted(set(sum([glob.glob(g) for g in a.roots.split(',')], [])))
        for rd in map(Path, runs):
            cfgp = rd / 'config.json'
            if not cfgp.exists() or not wanted(rd.name):
                continue
            cfg = json.loads(cfgp.read_text())
            task = cfg['task']
            if a.tasks and task not in a.tasks.split(','):
                continue
            ck = rd / f"model_{cfg['steps']:07d}.pt"
            if not ck.exists():
                continue
            ed = rd / 'eval'
            ed.mkdir(exist_ok=True)
            offs = OFFS.get(task, [25, 50])
            jobs = [('mh', None)] + [(m, off) for m in a.modes.split(',') for off in offs]
            for mode, off in jobs:
                out = ed / f'{mode}_{ck.stem}.json'
                if mode == 'mh':
                    if out.exists():
                        continue
                else:
                    res = json.loads(out.read_text()) if out.exists() else []
                    if any(r['offset'] == off and r['pca'] == 4 for r in res):
                        continue
                lock = ed / f'{mode}_{ck.stem}_{off}.lock'
                if (ed / f'{mode}_{ck.stem}_{off}.fail').exists():
                    continue
                try:
                    with open(lock, 'x') as f:
                        f.write(host)
                except FileExistsError:
                    continue
                try:
                    if mode == 'mh':
                        model = torch.load(ck, map_location='cuda', weights_only=False).eval()
                        full = metric_horizon(model, task, 'cuda', return_curve=True)
                        W = sfa_basis(model, task, 4, 'cuda')
                        slow = metric_horizon(model, task, 'cuda', return_curve=True, W=W)
                        pl = full[-1][1]
                        mh = next(h for h, m in full if m >= 0.9 * pl)
                        out.write_text(json.dumps({'full': full, 'sfa4': slow, 'metric_horizon': mh}))
                        print(rd.name, 'mh', mh, flush=True)
                        del model
                    else:
                        r = run(str(ck), task, off, 200, 300, 30, 30, 5, 0, **{mode: 4})
                        r['pca'] = 4
                        res = json.loads(out.read_text()) if out.exists() else []
                        res.append(r)
                        out.write_text(json.dumps(res))
                        print(rd.name, mode, 'off', off, 'sr', r['success_rate'], flush=True)
                    did = True
                except Exception as e:  # noqa: BLE001
                    print(rd.name, mode, off, 'ERROR', repr(e)[:300], flush=True)
                    (ed / f'{mode}_{ck.stem}_{off}.fail').write_text(repr(e))
                finally:
                    lock.unlink(missing_ok=True)
                    torch.cuda.empty_cache()
        if not did:
            time.sleep(300)


if __name__ == '__main__':
    main()
