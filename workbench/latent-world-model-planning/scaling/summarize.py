import glob, json, re, sys
from pathlib import Path
from collections import defaultdict
rows = []
for f in glob.glob('/tmp/latent-wm-runs/scaling/*/eval/0*.json') + glob.glob('/home/xiang/.cache/latent-wm-results/scaling/*/eval/0*.json'):
    r = json.loads(open(f).read()); run = Path(f).parent.parent.name
    m = re.match(r'(\w+?)_(\w+)_ep(\d+)_s(\d+)_st(\d+)(.*)', run)
    rows.append(dict(task=m[1], size=m[2], ep=int(m[3]), seed=int(m[4]), extra=m[6], ck=int(Path(r['ckpt']).stem.split('_')[1]),
                     off=r['offset'], budget=f"{r['samples']}x{r['iters']}", sr=r['success_rate']))
order = ['XXS', 'XS', 'S', 'M', 'L']
tab = defaultdict(dict)
for r in rows:
    tab[(r['task'], r['off'], r['budget'], r['ck'], r['ep'], r['extra'])][(r['size'], r['seed'])] = r['sr']
for k in sorted(tab):
    v = tab[k]
    cells = []
    for s in order:
        xs = [v[(s, sd)] for sd in range(5) if (s, sd) in v]
        cells.append(('/'.join(f'{x:.2f}' for x in xs)) if xs else '-')
    print(f'{k[0]:8s} off{k[1]:<4d} {k[2]:8s} ck{k[3]:<6d} ep{k[4]} {k[5]:6s} | ' + ' | '.join(f'{s}:{c:9s}' for s, c in zip(order, cells)))
