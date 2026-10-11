"""E81 confirmation: code-carrier weights versus whole-query reading."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

x = json.loads(Path('results/e81/qwen3_confirmation/analysis.json').read_text())
keys = ['D0.native', 'D1.native', 'D0.both', 'D0.full_attention', 'D1.source_flip']
labels = ['Tag:\nnative', 'Prefix:\nnative', 'Tag: donor\ncode only',
          'Tag: donor\nall reads', 'Prefix:\nsource flip']
colors = ['#3972a6', '#dc963c', '#8c98a6', '#358a65', '#ba5d5d']
fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.3), constrained_layout=True)
for ax, metric, scale, ylabel in zip(axes, ['accuracy', 'margin'], [100, 1],
                                   ['Label accuracy (%)', 'Correct logit margin (nats)']):
    vals = [x['conditions'][k][metric] for k in keys]
    means = np.array([v['mean'] for v in vals]) * scale
    err = np.array([[v['mean']-v['ci95'][0], v['ci95'][1]-v['mean']] for v in vals]).T * scale
    ax.bar(np.arange(5), means, color=colors, width=.68, yerr=err,
           error_kw={'linewidth': 1.2, 'capsize': 3}, zorder=3)
    ax.set_xticks(np.arange(5), labels, fontsize=8.5)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y', alpha=.22, zorder=0)
    ax.spines[['top','right']].set_visible(False)
    for i, v in enumerate(means):
        ax.text(i, v+err[1,i]+(.8 if scale==100 else .03),
                f'{v:.1f}' if scale==100 else f'{v:.2f}', ha='center', fontsize=9)
axes[0].set_ylim(0, 85)
axes[1].set_ylim(0, 1.85)
axes[0].set_title('Matched code-carrier weights are insufficient', fontsize=11)
axes[1].set_title('Source allocation matters at fixed reading mass', fontsize=11)
fig.suptitle('E81: 64 held-out contexts; entire query intervened', fontsize=13)
out = Path('results/figs/e81_carrier_and_query')
fig.savefig(out.with_suffix('.png'), dpi=180)
fig.savefig(out.with_suffix('.pdf'))
plt.close(fig)
