"""Run GC-IDM (amortized controller) on every finished final checkpoint of the given tasks."""
import argparse
import glob
import json
import subprocess
import time
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tasks', default='tworoom')
    p.add_argument('--script', default='gcidm')
    p.add_argument('--roots', default='/tmp/latent-wm-runs/scaling/*,/home/xiang/.cache/latent-wm-results/scaling/*')
    a = p.parse_args()
    tasks = a.tasks.split(',')
    while True:
        did = False
        for rd in sorted(sum([glob.glob(g) for g in a.roots.split(',')], [])):
            cfgp = Path(rd) / 'config.json'
            if not cfgp.exists():
                continue
            cfg = json.loads(cfgp.read_text())
            if cfg['task'] not in tasks:
                continue
            ck = Path(rd) / f"model_{cfg['steps']:07d}.pt"
            out = Path(rd) / 'eval' / f'{a.script}_{ck.stem}.json'
            lock = Path(rd) / 'eval' / f'{a.script}_{ck.stem}.lock'
            if not ck.exists() or out.exists() or lock.exists() or time.time() - ck.stat().st_mtime < 120:
                continue
            lock.parent.mkdir(exist_ok=True)
            lock.write_text('x')
            offs = '25,50,75' if cfg['task'] == 'tworoom' else ('50,100,200' if cfg['task'].startswith('pmaze') else ('25,50,100' if cfg['task'].startswith('vantmaze') else '25,50'))
            r = subprocess.run(['/home/xiang/.venvs/latent-wm/bin/python', f'{a.script}.py', '--ckpt', str(ck), '--offsets', offs],
                               capture_output=True, text=True, cwd=str(Path(__file__).parent))
            print(Path(rd).name, r.stdout.strip().splitlines()[-1:] if r.stdout else '', r.stderr[-300:] if r.returncode else '', flush=True)
            lock.unlink(missing_ok=True)
            did = True
        if not did:
            time.sleep(300)


if __name__ == '__main__':
    main()
