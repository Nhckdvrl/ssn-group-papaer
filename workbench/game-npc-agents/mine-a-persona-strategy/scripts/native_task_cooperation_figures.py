#!/usr/bin/env python3
"""Final E63/E64 physical-outcome figures; refuse partial cohorts."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def points(cells, labels, metric):
    estimates = [cells[label][metric] for label in labels]
    mean = np.array([v['mean'] for v in estimates])*100
    low = np.array([v['graph_bootstrap_95'][0] for v in estimates])*100
    high = np.array([v['graph_bootstrap_95'][1] for v in estimates])*100
    return mean, np.maximum(0, np.stack([mean-low, high-mean]))


def save(fig, out, name):
    for suffix in ['png', 'pdf', 'svg']:
        fig.savefig(out/(name+'.'+suffix), dpi=190, bbox_inches='tight')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--results', type=Path, required=True)
    a = ap.parse_args(); root = a.results
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none', 'pdf.fonttype': 42})
    families = [('32b', 'Qwen3-32B'), ('27b', 'Qwen3.5-27B'), ('gemma', 'Gemma3-12B')]
    reports = {k: json.loads((root/f'E63_{k}_dependency.json').read_text()) for k, _ in families}
    assert all(r['status'] == 'COMPLETE' and r['complete_worlds'] == 200 and r['episodes'] == 5400
               for r in reports.values())
    rules = ['none', 'generic_priority', 'asset_protection']
    ticks = ['No extra rule', 'Task first', 'Protect assets']
    colors = {'firm': '#2874a6', 'agreeable': '#d45e00'}
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.2), sharey=True)
    for col, (family, title) in enumerate(families):
        r = reports[family]
        for row, mode in enumerate(['goal_item', 'other_item']):
            ax = axes[row, col]
            for p in ['firm', 'agreeable']:
                keys = [f'{mode}/{rule}/{p}' for rule in rules]
                for metric, style, marker in [('goal_executed', '-', 'o'), ('request_given', '--', 's')]:
                    mean, err = points(r['cells'], keys, metric)
                    offset = -.035 if p == 'firm' else .035
                    ax.errorbar(np.arange(3)+offset, mean, yerr=err, color=colors[p],
                                linestyle=style, marker=marker, capsize=3, markersize=4,
                                linewidth=1.3, label=p.capitalize()+' / '+('task' if metric == 'goal_executed' else 'request'))
            ax.set_xticks(range(3), ticks, rotation=15, ha='right')
            ax.set_ylim(-2, 103); ax.set_yticks([0, 25, 50, 75, 100]); ax.grid(axis='y', alpha=.18)
            ax.set_title(title+'\n'+('Goal item: 200 worlds' if row == 0 else 'Other item: 100 worlds'))
            if col == 0: ax.set_ylabel('Actual native event (%)')
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(.5, 1.03))
    fig.text(.5, -.025, 'Goal-item branches stop at task completion; other-item branches continue to measure helping.\n'
             'Rows differ in cohort and post-task observation window; item effects require paired event-order comparisons.',
             ha='center', va='top', fontsize=9)
    fig.tight_layout(h_pad=2.1)
    save(fig, root, 'E63_task_cooperation')

    dyads = {k: json.loads((root/f'E64_{k}_reciprocal.json').read_text()) for k in ['32b', '27b']}
    assert all(r['worlds'] == 9 and r['episodes'] == 108 for r in dyads.values())
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.5), sharey=True)
    metrics = [('focal_resource_ever_attained', 'Focal target acquired'),
               ('actual_two_way_give', 'Both target items exchanged via Give'),
               ('focal_outgoing_give_without_any_acquisition', 'Outgoing target given, own target absent')]
    cell_keys = [p+'/'+cue for p in ['firm', 'agreeable'] for cue in ['none', 'check']]
    for ax, (metric, title) in zip(axes, metrics):
        for j, (family, label) in enumerate(families[:2]):
            mean, err = points(dyads[family]['cells'], cell_keys, metric)
            ax.errorbar(np.arange(4)+(j-.5)*.12, mean, yerr=err,
                        fmt='o' if j == 0 else 's', capsize=3, label=label, markersize=4)
        ax.set_xticks(range(4), ['Firm', 'Firm+check', 'Agreeable', 'Agreeable+check'], rotation=25, ha='right')
        ax.set_title(title); ax.set_ylim(-2, 103); ax.grid(axis='y', alpha=.18)
    axes[0].set_ylabel('Episodes (%)'); axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle('Native two-character pilot: 9 worlds, 3 seeds per cell', y=1.04)
    fig.tight_layout()
    save(fig, root, 'E64_native_negotiation')
    print('Saved E63/E64 final figures (PNG, SVG, PDF); intervals cluster by source world.')


if __name__ == '__main__': main()
