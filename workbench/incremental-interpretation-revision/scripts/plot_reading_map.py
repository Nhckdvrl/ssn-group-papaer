"""Standalone E52 figures, with missing cells kept visibly missing."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from data import sha


CONSTRUCTIONS = ('NPZ', 'NPS', 'MVRR', 'NPVP')


def point(ax, report, position, color, marker='o'):
    value = report.get('estimate')
    if value is None:
        ax.text(0, position, 'missing', va='center', ha='center', color='0.65', fontsize=7)
        return
    ci = report.get('ci95')
    if ci is not None:
        ax.plot(np.array(ci)*100, [position, position], color=color, lw=1.3)
    ax.plot(value*100, position, marker, color=color, markersize=4)
    ax.annotate(f"n={report['n_clusters']}", (value*100, position),
                xytext=(4, 4), textcoords='offset points', color=color, fontsize=6)


def plot(summary, out, stratum='genuine', metric='correct'):
    data = json.loads(summary.read_text())
    models = list(data['models'])
    assert models
    colors = plt.get_cmap('tab10').colors
    labels = [f'{construction} | {model}' for construction in CONSTRUCTIONS for model in models]
    rows = [(construction, model) for construction in CONSTRUCTIONS for model in models]
    height = max(5, len(rows)*.35)
    fig, axes = plt.subplots(1, 2, figsize=(13, height), sharey=True)
    for index, (construction, model) in enumerate(rows):
        report = data['models'][model].get(f'{construction}/B/{stratum}/{metric}', {})
        color = colors[models.index(model) % len(colors)]
        point(axes[0], report.get('cells', {}).get('R0/gp', {}), index-.09, color, 'o')
        point(axes[0], report.get('cells', {}).get('R0/control', {}), index+.09, color, 's')
        point(axes[1], report.get('gaps', {}).get('R0', {}), index, color)
    axes[0].set_title('Single reading: GP (circle), control (square)')
    axes[0].set_xlabel('Correct response (%)' if metric == 'correct' else 'Correct-choice probability (%)')
    axes[0].set_xlim(-3, 103)
    axes[1].set_title('Control − GP')
    axes[1].set_xlabel('Gap (percentage points)')
    axes[1].axvline(0, color='0.6', lw=.8)
    axes[0].set_yticks(range(len(labels)), labels, fontsize=8)
    axes[0].invert_yaxis()
    for ax in axes:
        ax.grid(axis='x', alpha=.18)
    conventional = stratum in ('NEITHER', 'initial_all')
    heading = 'Published answer-convention agreement' if conventional else 'Qualified literal-contradiction items'
    fig.suptitle(f'{heading} · native chat · {metric}', fontsize=12)
    footer = '95% linked lexical-cluster bootstrap intervals. Missing is not zero. Low control accuracy limits attribution.'
    fig.text(.02, .015, footer, fontsize=8)
    fig.tight_layout(rect=(0, .035, 1, .96))
    out.mkdir(parents=True, exist_ok=True)
    name = f'native-{stratum}-{metric}-baseline'
    for extension in ('png', 'pdf'):
        fig.savefig(out/f'{name}.{extension}', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 4, figsize=(17, height), sharey=True)
    specifications = (
        ('R1 gap reduction', lambda r: r.get('reductions', {}).get('R1', {})),
        ('Full repeat − truncated repeat', lambda r: r.get('R1_vs_controls', {}).get('R2', {})),
        ('Full repeat − matched filler', lambda r: r.get('R1_vs_controls', {}).get('R3', {})),
        ('One instruction: GP − control gain', lambda r: r.get('instruction_recovery', {}).get('selective_gain', {})))
    for ax, (title, getter) in zip(axes, specifications):
        for index, (construction, model) in enumerate(rows):
            report = data['models'][model].get(f'{construction}/B/{stratum}/{metric}', {})
            point(ax, getter(report), index, colors[models.index(model) % len(colors)])
        ax.axvline(0, color='0.6', lw=.8)
        ax.grid(axis='x', alpha=.18)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Percentage points')
    axes[0].set_yticks(range(len(labels)), labels, fontsize=8)
    axes[0].invert_yaxis()
    fig.suptitle(f'{heading} · reading contrasts', fontsize=12)
    fig.text(.02, .015, 'Positive values favor GP-selective recovery; inspect raw GP/control gains before attributing it. Each contrast uses matched items and its own n.', fontsize=8)
    fig.tight_layout(rect=(0, .035, 1, .96))
    name = f'native-{stratum}-{metric}-contrasts'
    for extension in ('png', 'pdf'):
        fig.savefig(out/f'{name}.{extension}', dpi=180)
    plt.close(fig)
    (out/f'native-{stratum}-{metric}.json').write_text(json.dumps(dict(
        summary=str(summary), summary_sha256=sha(summary), models=models,
        stratum=stratum, metric=metric, missing_cells_not_zero=True,
        inference='Descriptive display of preregistered estimates; not automatic account selection.'), indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--stratum', choices=['genuine', 'NEITHER', 'initial_all'], default='genuine')
    parser.add_argument('--metric', choices=['correct', 'p_correct'], default='correct')
    args = parser.parse_args()
    plot(args.summary, args.out, args.stratum, args.metric)
