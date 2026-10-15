#!/usr/bin/env python3
"""Reproduce the E58 native-role component figure from frozen aggregate results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1] / 'results'
fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
colors = {'full': '#275A86', 'traits': '#E09B30', 'priority': '#648F6A'}
models = [('32b', 'Qwen3-32B'), ('27b', 'Qwen3.5-27B'), ('gemma', 'Gemma3-12B')]
for ax, condition, title in zip(axes, ['direct', 'plan_grounded'],
                              ['Direct native decisions', 'Dialogue → plan → native decisions']):
    for j, pack in enumerate(['full', 'traits', 'priority']):
        xs, ys, low, high = [], [], [], []
        for i, (model, label) in enumerate(models):
            result = json.loads((root / f'E58_{model}_components.json').read_text())
            d = result['persona_effects'][pack + '/' + condition + '/request']
            xs.append(i + (j-1)*.19); ys.append(100*d['mean'])
            low.append(100*(d['mean']-d['graph_bootstrap_95'][0]))
            high.append(100*(d['graph_bootstrap_95'][1]-d['mean']))
        ax.errorbar(xs, ys, yerr=[low, high], fmt='o', color=colors[pack], capsize=3, ms=5,
                    label={'full': 'Full role package', 'traits': 'Trait clause only',
                           'priority': 'Priority clause only'}[pack])
    ax.axhline(0, color='#AAA', lw=.8)
    ax.set_xticks(range(3), [label for _, label in models]); ax.set_title(title, fontsize=11)
    ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='y', alpha=.18)
    ax.tick_params(axis='x', labelsize=8)
axes[0].set_ylabel('Agreeable − firm: actual item handover (pp)')
fig.legend(*axes[0].get_legend_handles_labels(), frameon=False, ncol=3,
           loc='upper center', bbox_to_anchor=(.5, 1.01), fontsize=8)
fig.text(.5, .01, '200 paired native LIGHT worlds; one fixed sampling seed; graph bootstrap 95% intervals.\n'
         'Text-package interventions include multiple traits; first resource disposition, not total welfare.',
         ha='center', fontsize=8)
fig.tight_layout(rect=[0, .10, 1, .91])
for suffix in ['png', 'pdf', 'svg']:
    fig.savefig(root / ('E58_persona_components.' + suffix), dpi=160)
