#!/usr/bin/env python3
"""E70 static scientific exports: first recipients and paired control effects."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def save(fig, folder, name):
    for ext in ['png', 'pdf', 'svg']:
        p = folder/(name+'.'+ext)
        fig.savefig(p, dpi=180)
        if ext == 'svg':
            p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(exist_ok=True)
    reports = {model: json.loads((args.results/f'E70_{model}_complete.json').read_text())
               for model in ['gemma', '32b']}
    plt.rcParams.update({'font.size': 10, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout='constrained', sharey=True)
    outcomes = [('to_goal', 'Authored recipient', '#4477AA'),
                ('to_competitor', 'Other peer', '#CC6677'),
                ('to_other', 'Other recipient', '#999999'),
                ('no_transfer', 'No selected-item Give', '#DDCC77')]
    for i, (model, name) in enumerate([('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
        for j, state in enumerate(['ready', 'equipped']):
            ax = axes[i, j]; bottom = np.zeros(4)
            keys = [p+'/'+state+'_'+d for d in ['aligned', 'divert'] for p in ['firm', 'agreeable']]
            for metric, label, color in outcomes:
                means = np.array([reports[model]['cells'][k][metric]['mean'] for k in keys])*100
                ax.bar(np.arange(4), means, bottom=bottom, label=label, color=color, width=.7)
                bottom += means
            ax.set_xticks(np.arange(4), ['Firm\naligned', 'Agreeable\naligned', 'Firm\ndivert', 'Agreeable\ndivert'])
            ax.set_title(name+' / '+('item ready' if state == 'ready' else 'item equipped'))
            ax.set_ylim(0, 100); ax.set_ylabel('First selected-item disposition (%)')
            ax.spines[['top', 'right']].set_visible(False)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside upper center', ncol=4, frameon=False)
    fig.supxlabel('117 source worlds, three seeds; up to eight actions, stopping at first selected-item Give.\nAligned = speaker is authored recipient. Source goal, personas and native rules retained.', fontsize=10)
    save(fig, args.out, 'E70_first_disposition')
    selections = [
        ('mechanics_minus_baseline/aligned', 'to_goal', 'Mechanics / aligned: to authored recipient'),
        ('mechanics_minus_baseline/divert', 'to_goal', 'Mechanics / divert: to authored recipient'),
        ('mechanics_minus_baseline/divert', 'to_competitor', 'Mechanics / divert: to requesting peer'),
        ('priority_minus_baseline/divert', 'to_goal', 'Priority / divert: to authored recipient'),
        ('staged_minus_baseline/aligned', 'to_goal', 'Staged / aligned: to authored recipient'),
        ('staged_minus_baseline/divert', 'to_goal', 'Staged / divert: to authored recipient')]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), layout='constrained', sharey=True)
    for ax, (model, name) in zip(axes, [('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
        for persona, color, offset in [('firm', '#4477AA', .10), ('agreeable', '#AA3377', -.10)]:
            vals = [reports[model]['contrasts'][persona+'/'+term][metric] for term, metric, _ in selections]
            means = np.array([v['mean'] for v in vals])*100
            lower = np.array([v['graph_bootstrap_95'][0] for v in vals])*100
            upper = np.array([v['graph_bootstrap_95'][1] for v in vals])*100
            ax.errorbar(means, np.arange(len(vals))+offset, xerr=[means-lower, upper-means], fmt='o', capsize=3,
                        label=persona.capitalize(), color=color)
        ax.axvline(0, color='#777777', linewidth=.8); ax.grid(axis='x', alpha=.2)
        ax.set_yticks(np.arange(len(selections)), [r[2] for r in selections]); ax.set_ylim(len(selections)-.5, -.5)
        ax.spines[['top', 'right']].set_visible(False); ax.set_title(name)
        ax.set_xlabel('Paired difference (percentage points)'); ax.legend(frameon=False)
    fig.supxlabel('All controls hold equipped physical state fixed. Pointwise graph-cluster 95% intervals.\nStaged and direct interfaces share the exact same conversation; interface packages differ.', fontsize=10)
    save(fig, args.out, 'E70_paired_controls')


if __name__ == '__main__':
    main()
