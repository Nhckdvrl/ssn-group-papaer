"""Show preregistered definition-order effects, without choosing the best order."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


root = Path(__file__).resolve().parents[1]
a = json.loads((root / 'results/e78/qwen3_bridge/analysis.json').read_text())
configs = [(s, o) for s in ['mixed', 'single'] for o in ['copy_first', 'subtract_first']]
labels = ['Mixed\ncopy then subtract', 'Mixed\nsubtract then copy',
          'Single\ncopy then subtract', 'Single\nsubtract then copy']
fig, axes = plt.subplots(1, 2, figsize=(11.3, 4.3), sharey=True)
for ax, mode in zip(axes, ['rule_id', 'numeric']):
    for ri, (rule, color) in enumerate([('copy', '#2878b5'), ('subtract', '#d57931')]):
        vals = []
        for scope, order in configs:
            key = scope + '.' + order
            record = a['rule_identification'][key] if mode == 'rule_id' else a['numeric'][key + '.input_first']['interpolation']
            vals.append(record[rule + '_accuracy'])
        y = np.array([v['mean'] for v in vals])
        lo = y - np.array([v['ci95'][0] for v in vals])
        hi = np.array([v['ci95'][1] for v in vals]) - y
        ax.bar(np.arange(4) + (ri - .5) * .33, y, .31, color=color, label=rule,
               yerr=[lo, hi], capsize=3, error_kw={'lw': 1})
    ax.set_xticks(np.arange(4), labels, fontsize=9)
    ax.set_ylim(0, 1.07)
    ax.set_axisbelow(True)
    ax.grid(axis='y', alpha=.18)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_title('Source rule identification' if mode == 'rule_id' else 'Direct numeric interpolation', fontsize=12)
    ax.axhline(.9 if mode == 'rule_id' else .8, color='gray', linestyle='--', lw=.8)
axes[0].set_ylabel('Exact candidate accuracy')
axes[0].legend(frameon=False, ncol=2, loc='lower left')
fig.suptitle('E78: definition order changes the apparent function boundary', fontsize=14)
fig.text(.5, .02, '32 paired contexts; 95% context bootstrap. Known operator names; raw candidate scores, not free generation.',
         ha='center', fontsize=9)
fig.tight_layout(rect=[0, .06, 1, .94])
out = root / 'results/figs'
fig.savefig(out / 'e78_definition_order.png', dpi=180)
fig.savefig(out / 'e78_definition_order.pdf')
