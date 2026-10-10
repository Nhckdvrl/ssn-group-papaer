"""Independent E82 replay and E83 frozen-predictor results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

x = json.loads(Path('results/e82/qwen3_confirmation/analysis.json').read_text())
y = json.loads(Path('results/e83/qwen3_prediction/analysis.json').read_text())
fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.2), constrained_layout=True)
sets = [(x, ['label_final', 'label', 'query', 'label_query', 'full'], 'minus_frozen_base',
         ['Label:\nfinal only', 'Label:\nall query', 'Query\nreads', 'Label +\nquery', 'All\nreads'],
         'E82: structured replay; fixed donor code weights'),
        (y, ['B', 'R', 'RJ', 'RY', 'oracle_label'], 'minus_native',
         ['Budget +\nposition', 'Source +\ninput', '+ Joint\nmatch', '+ Label\nidentity', 'Actual donor\nlabel reads'],
         'E83: frozen forecasts; native code weights')]
for ax, (data, keys, suffix, labels, title) in zip(axes, sets):
    vals = [data['contrasts'][k+'.'+suffix]['margin'] for k in keys]
    means = np.array([v['mean'] for v in vals])
    err = np.array([[v['mean']-v['ci95'][0], v['ci95'][1]-v['mean']] for v in vals]).T
    ax.bar(np.arange(5), means, width=.66, color=['#467c9a','#358a65','#a1a7ad','#83a64a','#d79a47'],
           yerr=err, error_kw=dict(capsize=3, linewidth=1.2), zorder=3)
    ax.set_xticks(np.arange(5), labels, fontsize=8.5)
    ax.set_ylabel('Change in correct Source contrast (nats)', fontsize=9.5)
    ax.axhline(0, color='#555555', linewidth=.7)
    ax.grid(axis='y', alpha=.2, zorder=0)
    ax.spines[['top','right']].set_visible(False)
    ax.set_title(title, fontsize=10.5)
    ax.set_ylim(-.10, .85)
fig.suptitle('From recorded reads to relational forecasts: 64 new contexts per experiment', fontsize=12)
out = Path('results/figs/e82_e83_replay_to_prediction')
fig.savefig(out.with_suffix('.png'), dpi=180)
fig.savefig(out.with_suffix('.pdf'))
plt.close(fig)
