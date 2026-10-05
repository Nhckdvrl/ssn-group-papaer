"""Reproducible scientific plots of preregistered role-control cells."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot(path, cohort):
    j = json.loads(path.read_text())
    experiment = j['experiment']
    cells = j['probability']['cells']
    if experiment == 'E38':
        forms = ('contrast_parent', 'affirmative_mention_first')
        policies = ('candidate_only', 'procedure_unknown', 'independent_fair', 'selected_source', 'selected_other')
        labels = ('Candidates', 'Unknown procedure', 'Independent fair', 'Selected A', 'Selected B')
        fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        for ax, form in zip(axes, forms):
            for off, order, marker in ((-.07, 'source_first', 'o'), (.07, 'other_first', 's')):
                values = [cells[f'{cohort}/J/{form}/{policy}/{order}'] for policy in policies]
                draw(ax, np.arange(len(values)) + off, values, marker, order.replace('_', ' '))
            ax.set_xticks(range(5), labels, rotation=22, ha='right')
            ax.set_title(form.replace('_', ' '))
    else:
        forms = ('contrast_named', 'affirmative_mention_first', 'affirmative_mention_last') if experiment == 'E39' else ('plain_mention_first', 'plain_mention_last')
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
        for ax, actor in zip(axes, ('same_actor', 'other_actor')):
            for off, form, marker in zip(np.linspace(-.14, .14, len(forms)), forms, ('o', 's', '^')):
                keys = [f'{form}/original_activity/old', f'{form}/{actor}/same_began', f'{form}/{actor}/different_began']
                values = [cells[f'{cohort}/J/{key}'] for key in keys]
                draw(ax, np.arange(3) + off, values, marker, form.replace('_', ' '))
            ax.set_xticks(range(3), ('Earlier event', 'New: same action', 'New: different action'))
            ax.set_title(actor.replace('_', ' '))
    for ax in axes:
        ax.axhline(0, color='0.5', linewidth=.8)
        ax.grid(axis='y', alpha=.2)
        ax.legend(fontsize=8)
    axes[0].set_ylabel('Role effect minus neutral-entity effect J (bits)')
    n = len(j['probability']['cohorts'][cohort])
    fig.suptitle(f'{experiment} | {cohort} | {n} verb families | paired bootstrap 95% CI')
    fig.text(.5, .012, 'Conditional continuation preference; not event probability or an accuracy measure.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, .95))
    out = path.parent / f'{experiment}-role-control-{cohort}'
    for ext in ('png', 'pdf'):
        fig.savefig(str(out) + '.' + ext, dpi=180)
    plt.close(fig)


def draw(ax, x, values, marker, label):
    assert all(v['estimate'] is not None for v in values)
    y = np.array([v['estimate'] for v in values])
    ci = np.array([v['ci95'] for v in values])
    ax.errorbar(x, y, yerr=np.stack((y-ci[:, 0], ci[:, 1]-y)), fmt=marker+'-', capsize=3, label=label)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('summary', type=Path)
    p.add_argument('--cohort', default='all')
    a = p.parse_args()
    plot(a.summary, a.cohort)
