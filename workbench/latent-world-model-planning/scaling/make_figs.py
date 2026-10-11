"""Main E21/E22 figures from the evaluation files (writes results/figs/E22_*.png)."""
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOTS = ['/tmp/latent-wm-runs/scaling', '/home/xiang/.cache/latent-wm-results/scaling']
OUT = Path(__file__).resolve().parents[1] / 'results' / 'figs'
OUT.mkdir(parents=True, exist_ok=True)
PARAMS = {'XXS': 1.71, 'XS': 4.07, 'S': 17.92, 'M': 71.43, 'L': 285.2}
SIZES = ['XXS', 'XS', 'S', 'M', 'L']
C = {'cem': '#c0392b', 'sfa': '#2471a3', 'mix': '#1f9e89', 'gcidm': '#7d3c98', 'lcost': '#b9770e'}


def base_runs(task):
    out = defaultdict(list)
    for r in ROOTS:
        for rd in glob.glob(f'{r}/{task}_*_ep0_s*_st60000'):
            m = re.match(rf'{task}_(\w+)_ep0_s(\d)_st60000$', Path(rd).name)
            if m:
                out[m[1]].append(Path(rd))
    return out


def sr(f):
    try:
        return json.loads(Path(f).read_text())['success_rate']
    except Exception:
        return None


def collect(task, offs):
    runs = base_runs(task)
    res = {k: defaultdict(list) for k in ['cem', 'sfa', 'mix', 'gcidm', 'lcost']}
    for size, rds in runs.items():
        for rd in rds:
            for off in offs:
                v = sr(rd / 'eval' / f'0060000_off{off}_300x30_n200.json')
                if v is not None:
                    res['cem'][(size, off)].append(v)
            for kind in ['gcidm', 'lcost']:
                f = rd / 'eval' / f'{kind}_model_0060000.json'
                if f.exists():
                    for r in json.loads(f.read_text()):
                        res[kind][(size, r['offset'])].append(r['success_rate'])
            for kind in ['sfa', 'mix']:
                f = rd / 'eval' / f'{kind}_model_0060000.json'
                if f.exists():
                    best = defaultdict(list)
                    for r in json.loads(f.read_text()):
                        best[(r['offset'], r[kind] if kind in r else r.get('pca'))].append(r['success_rate'])
                    for (off, k), v in best.items():
                        if (kind == 'sfa' and k == 4) or (kind == 'mix' and k == 4):
                            res[kind][(size, off)].append(np.mean(v))
    return res


def fig_scaling():
    fig, axes = plt.subplots(1, 4, figsize=(17, 3.8))
    panels = [('tworoom', 50), ('tworoom', 75), ('pusht', 25), ('pusht', 50)]
    for ax, (task, off) in zip(axes, panels):
        res = collect(task, [off])
        for kind, lab in [('cem', 'CEM + latent L2 (default)'), ('sfa', 'CEM + slow-feature cost (k=4, no training)'),
                          ('mix', 'CEM + multi-scale cost (k=4, no training)'), ('gcidm', 'GC-IDM (amortized, same latent)')]:
            xs, ys, es = [], [], []
            for s in SIZES:
                v = res[kind].get((s, off))
                if v:
                    xs.append(PARAMS[s]); ys.append(np.mean(v)); es.append(np.std(v) if len(v) > 1 else 0)
            if xs:
                ax.errorbar(xs, ys, yerr=es, marker='o', color=C[kind], label=lab, capsize=3)
        ax.set_xscale('log'); ax.set_ylim(0, 1.02); ax.set_xlabel('world-model parameters (M)')
        ax.set_title(f'{task} — goal offset {off}'); ax.grid(alpha=.3)
    axes[0].set_ylabel('closed-loop success (n=200)')
    axes[-1].legend(fontsize=7, loc='lower right')
    fig.tight_layout(); fig.savefig(OUT / 'E22_success_vs_size.png', dpi=150)


def fig_bandwidth():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, task in zip(axes[:2], ['tworoom', 'pusht']):
        pts = defaultdict(list)
        for r in ROOTS:
            for f in glob.glob(f'{r}/{task}_*/eval/kell_model_00*.json'):
                m = re.match(rf'{task}_(\w+?)_ep0_s\d_st60000$', Path(f).parents[1].name)
                if not m:
                    continue
                try:
                    d = json.loads(Path(f).read_text())
                except Exception:
                    continue
                pts[m[1]].append((d['deff'], d['ell']))
        for s in SIZES:
            if pts.get(s):
                a = np.array(pts[s]); ax.scatter(a[:, 0], a[:, 1], label=s, s=14)
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('latent effective dimension D_eff')
        ax.set_ylabel('metric bandwidth ell (Gaussian fit, state units)'); ax.set_title(f'{task}: bandwidth vs D_eff (all checkpoints)')
        ax.grid(alpha=.3, which='both'); ax.legend(fontsize=7)
    ax = axes[2]
    for task, col in [('tworoom', '#c0392b'), ('pusht', '#2471a3')]:
        xs, ys = [], []
        for r in ROOTS:
            for f in glob.glob(f'{r}/{task}_*/eval/kell_model_00*.json'):
                rd = Path(f).parents[1]
                if 'aux' in rd.name:
                    continue
                ck = int(Path(f).stem.split('_')[-1])
                try:
                    d = json.loads(Path(f).read_text()); log = json.loads((rd / 'log.json').read_text())
                except Exception:
                    continue
                v = [x['sigreg'] for x in log if abs(x['step'] - ck) <= 2500]
                if v:
                    xs.append(np.mean(v)); ys.append(d['ell'])
        if xs:
            ax.scatter(xs, np.array(ys) / np.median(ys), s=12, color=col, label=task)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('training SIGReg loss (lower = more isotropic)')
    ax.set_ylabel('bandwidth / task median'); ax.set_title('better-optimized isotropy -> more local metric'); ax.legend()
    ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / 'E22_bandwidth.png', dpi=150)


def fig_budget():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, (task, off) in zip(axes, [('tworoom', 50), ('pusht', 25)]):
        runs = base_runs(task)
        for s in SIZES:
            xs, ys = [], []
            for sm, it in [(30, 3), (100, 10), (300, 30), (1000, 30), (3000, 30)]:
                v = [sr(rd / 'eval' / f'0060000_off{off}_{sm}x{it}_n200.json') for rd in runs.get(s, [])]
                v = [x for x in v if x is not None]
                if v:
                    xs.append(sm * it); ys.append(np.mean(v))
            if xs:
                ax.plot(xs, ys, marker='o', label=s)
        ax.set_xscale('log'); ax.set_xlabel('CEM candidate evaluations per plan'); ax.set_ylabel('success')
        ax.set_title(f'{task} offset {off}: planning compute'); ax.grid(alpha=.3); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(OUT / 'E22_budget.png', dpi=150)


if __name__ == '__main__':
    fig_scaling(); fig_bandwidth(); fig_budget()
    print('written', sorted(p.name for p in OUT.glob('E22_*.png')))
