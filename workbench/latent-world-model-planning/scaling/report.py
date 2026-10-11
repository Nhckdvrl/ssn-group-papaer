"""Collect all E21 evaluations into one table (+ training FLOPs) and draw the main figures.

FLOPs per training step ~= 6 * B * (P_enc * T * (tokens+1) + (P_pred + P_proj) * T)
(B=128, T=4 frames, tokens=(res/patch)^2). Planning FLOPs per decision ~= 2 * P_pred * samples * iters * H * hist.
Outputs: results/E21_scaling_table.json and results/figs/E21_*.png
"""
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOTS = ['/tmp/latent-wm-runs/scaling', '/home/xiang/.cache/latent-wm-results/scaling']
WB = Path(__file__).resolve().parents[1]


def run_info(run_dir):
    cfg = json.loads((Path(run_dir) / 'config.json').read_text())
    return cfg


def flops_per_step(cfg, n_enc, n_pred):
    toks = (cfg.get('res', 64) // cfg.get('patch', 8)) ** 2 + 1
    return 6 * cfg['batch'] * (n_enc * 4 * toks + n_pred * 4)


def collect():
    rows = []
    pcache = {}
    for root in ROOTS:
        for rd in sorted(glob.glob(f'{root}/*')):
            if not Path(rd, 'config.json').exists():
                continue
            cfg = run_info(rd)
            key = (cfg['size'], cfg.get('latent', 0))
            if key not in pcache:
                import sys
                sys.path.insert(0, str(Path(__file__).parent))
                from wm import build_model, n_params
                m = build_model(cfg['size'], latent=cfg.get('latent') or None)
                pcache[key] = (n_params(m.encoder), n_params(m) - n_params(m.encoder))
            n_enc, n_rest = pcache[key]
            fps = flops_per_step(cfg, n_enc, n_rest)
            base = dict(run=Path(rd).name, task=cfg['task'], size=cfg['size'], latent=cfg.get('latent') or 0,
                        seed=cfg['seed'], episodes=cfg['train_episodes'], params=cfg['params'], n_enc=n_enc, n_pred=n_rest)
            for f in glob.glob(f'{rd}/eval/0*.json'):
                r = json.loads(open(f).read())
                ck = int(Path(r['ckpt']).stem.split('_')[1])
                rows.append(base | dict(kind='plan', ck=ck, train_flops=fps * ck, off=r['offset'], samples=r['samples'],
                                        iters=r['iters'], sr=r['success_rate'], n=r['n'],
                                        plan_flops=2 * n_rest * r['samples'] * r['iters'] * 5 * 3))
            for f in glob.glob(f'{rd}/eval/bank_*.json'):
                ck = int(re.search(r'model_(\d+)', f).group(1))
                rows.append(base | dict(kind='bank', ck=ck, train_flops=fps * ck, bank=re.search(r'bank_(\w+?)_model', f).group(1))
                            | json.loads(open(f).read()))
            for f in glob.glob(f'{rd}/eval/diag_*.json'):
                ck = int(re.search(r'model_(\d+)', f).group(1))
                d = json.loads(open(f).read())
                d.pop('dist_curve', None); d.pop('probe_r2', None); d.pop('ckpt', None)
                rows.append(base | dict(kind='diag', ck=ck, train_flops=fps * ck) | d)
            for f in glob.glob(f'{rd}/eval/gcidm_*.json'):
                ck = int(re.search(r'model_(\d+)', f).group(1))
                for r in json.loads(open(f).read()):
                    rows.append(base | dict(kind='gcidm', ck=ck, train_flops=fps * ck, off=r['offset'], sr=r['success_rate'], n=r['n']))
    return rows


def main():
    rows = collect()
    out = WB / 'results' / 'E21_scaling_table.json'
    out.write_text(json.dumps(rows))
    print('rows', len(rows), '->', out)
    # compact console view: final-checkpoint success by task/off/size/latent/episodes
    tab = defaultdict(list)
    for r in rows:
        if r['kind'] == 'plan' and (r['samples'], r['iters']) == (300, 30):
            tab[(r['task'], r['off'], r['episodes'], r['latent'], r['ck'], r['size'])].append(r['sr'])
    for k in sorted(tab):
        print(k, np.round(tab[k], 3).tolist())


if __name__ == '__main__':
    main()
