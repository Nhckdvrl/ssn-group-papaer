"""E23 aggregation: per (task, variant, size, cost, offset) success over seeds, plus the success-vs-log-params
slope with a seed-clustered bootstrap CI. Writes results/E23_table.json and prints a compact table."""
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOTS = ['/tmp/latent-wm-runs/scaling', '/home/xiang/.cache/latent-wm-results/scaling']
OUT = Path(__file__).resolve().parents[1] / 'results' / 'E23_table.json'
PARAMS = {'XXS': 1.71, 'XS': 4.07, 'S': 17.92, 'M': 71.43, 'L': 285.2}
SIZES = ['XXS', 'XS', 'S', 'M', 'L']
PAT = re.compile(r'^(?P<task>[a-z]+)_(?P<size>XXS|XS|S|M|L)_ep0_s(?P<seed>\d)_st60000(?P<var>.*)$')


def load(f):
    try:
        return json.loads(Path(f).read_text())
    except Exception:
        return None


def collect():
    cells = defaultdict(list)  # (task, var, cost, off, size) -> [(seed, sr)]
    mh = defaultdict(list)     # (task, var, size) -> [(seed, metric horizon)]
    for root in ROOTS:
        for rd in glob.glob(f'{root}/*_st60000*'):
            m = PAT.match(Path(rd).name)
            if not m:
                continue
            task, size, seed, var = m['task'], m['size'], int(m['seed']), m['var'] or 'base'
            ev = Path(rd) / 'eval'
            for f in glob.glob(f'{ev}/0060000_off*_300x30_n200.json'):
                d = load(f)
                if d:
                    cells[(task, var, 'l2', d['offset'], size)].append((seed, d['success_rate']))
            for mode in ['sfa', 'auto', 'mix']:
                d = load(ev / f'{mode}_model_0060000.json') or []
                seen = set()
                for r in d:
                    if r.get('pca') == 4 and r['offset'] not in seen:
                        seen.add(r['offset'])
                        cells[(task, var, mode, r['offset'], size)].append((seed, r['success_rate']))
            for kind in ['gcidm']:
                d = load(ev / f'{kind}_model_0060000.json') or []
                for r in d:
                    cells[(task, var, kind, r['offset'], size)].append((seed, r['success_rate']))
            d = load(ev / 'mh_model_0060000.json')
            if d:
                mh[(task, var, size)].append((seed, d['metric_horizon']))
    return cells, mh


def slope(points, B=2000, rng=np.random.default_rng(0)):
    """points: list of (size, seed, sr). OLS slope of sr on log10(params); bootstrap over seeds within size."""
    if len({p[0] for p in points}) < 3:
        return None
    x = np.array([np.log10(PARAMS[p[0]]) for p in points]); y = np.array([p[2] for p in points])
    b = np.polyfit(x, y, 1)[0]
    by = defaultdict(list)
    for s, _, v in points:
        by[s].append(v)
    bs = []
    for _ in range(B):
        xx, yy = [], []
        for s, v in by.items():
            v = np.asarray(v)
            pick = v[rng.integers(0, len(v), len(v))]
            xx += [np.log10(PARAMS[s])] * len(v); yy += list(pick)
        bs.append(np.polyfit(xx, yy, 1)[0])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(b), float(lo), float(hi)


def main():
    cells, mh = collect()
    table = []
    keys = sorted({k[:4] for k in cells})
    for task, var, cost, off in keys:
        row = {'task': task, 'var': var, 'cost': cost, 'offset': off, 'by_size': {}}
        pts = []
        for s in SIZES:
            v = cells.get((task, var, cost, off, s))
            if v:
                srs = [x[1] for x in v]
                row['by_size'][s] = {'mean': float(np.mean(srs)), 'sd': float(np.std(srs)), 'seeds': sorted(x[0] for x in v)}
                pts += [(s, x[0], x[1]) for x in v]
        row['slope_per_decade'] = slope(pts)
        table.append(row)
    mhs = {f'{t}/{v}/{s}': sorted(x[1] for x in vals) for (t, v, s), vals in sorted(mh.items())}
    OUT.write_text(json.dumps({'cells': table, 'metric_horizon': mhs}, indent=1))
    for r in table:
        cells_s = '  '.join(f"{s}:{r['by_size'][s]['mean']*100:5.1f}({len(r['by_size'][s]['seeds'])})" if s in r['by_size'] else f'{s}:   - ' for s in SIZES)
        sl = r['slope_per_decade']
        sl_s = f"slope {sl[0]*100:+.1f}pp/dec [{sl[1]*100:+.1f},{sl[2]*100:+.1f}]" if sl else ''
        print(f"{r['task']:15s} {r['var']:13s} {r['cost']:5s} off{r['offset']:<4d} {cells_s}  {sl_s}")
    print('metric horizon:', mhs)


if __name__ == '__main__':
    main()
