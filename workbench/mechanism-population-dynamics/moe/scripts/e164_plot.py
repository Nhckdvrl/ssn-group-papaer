"""Scientific E164 figures from complete, independently checked results only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]/'results/e164'
CONTRASTS = ('natural_B_minus_P', 'R_B_minus_P_at_route_P', 'R_B_minus_P_at_route_B',
             'route_B_minus_P_at_R_P', 'route_B_minus_P_at_R_B', 'interaction')
LABELS = ('Natural B minus P', 'R bank B minus P | P route', 'R bank B minus P | B route',
          'B minus P route | R bank P', 'B minus P route | R bank B', 'Bank × route interaction')


def save(fig, name):
    out = ROOT/'figures'; out.mkdir(exist_ok=True)
    fig.savefig(out/(name+'.png'), dpi=190, bbox_inches='tight')
    fig.savefig(out/(name+'.pdf'), bbox_inches='tight')
    plt.close(fig)


def errorbar(ax, row, position, scale=1., color='#247ba0', label=None):
    p = row['point']*scale; lo, hi = np.asarray(row['ci95'])*scale
    ax.errorbar(p, position, xerr=[[p-lo], [hi-p]], fmt='o', color=color,
                capsize=3, ms=5, label=label)


def source_effects(s, field, name, xlabel):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True)
    scale = 100 if field.endswith('accuracy') else 1
    for ax, policy, title in zip(axes, ('full', 'P32'), ('Full computation', 'Common P validation selector: 31R + S')):
        for i, key in enumerate(CONTRASTS):
            errorbar(ax, s['fresh_primary'][field][policy+'/'+key], i, scale)
        ax.axvline(0, color='.6', ls='--', lw=1)
        ax.set(title=title, xlabel=xlabel, yticks=range(6), yticklabels=LABELS)
        ax.grid(axis='x', alpha=.18)
    axes[0].invert_yaxis()
    fig.suptitle('Expert responses versus induced routing: all predeclared contrasts', fontsize=13)
    fig.text(.5, .015, 'Common P backbone / gate weights / S_P; P and B label the R bank or its routing trajectory.\n'
             'Fresh55 subjects, 8 questions each. Paired95% subject-cluster intervals; not training-seed intervals.',
             ha='center', fontsize=8.5)
    fig.subplots_adjust(left=.27, right=.98, top=.84, bottom=.19, wspace=.20)
    save(fig, name)


def shared(s):
    x = s['fresh_primary']['true_answer_token_NLL']
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    labels = ('Natural routing', 'Fixed P routing', 'Fixed B routing')
    pairs = (('S_effect/natural_R_P', 'S_effect/natural_R_B'),
             ('S_effect/R_P_G_P', 'S_effect/R_B_G_P'), ('S_effect/R_P_G_B', 'S_effect/R_B_G_B'))
    for i, pair in enumerate(pairs):
        for r, key in enumerate(pair):
            errorbar(axes[0], x[key], i+(r-.5)*.2, color=('#30343b', '#c94c4c')[r],
                     label=('R bank P', 'R bank B')[r] if i == 0 else None)
    for i, key in enumerate(('natural', 'fixed_route_P', 'fixed_route_B')):
        errorbar(axes[1], x['S_partner_change/'+key], i)
    for ax in axes:
        ax.axvline(0, color='.6', ls='--', lw=1)
        ax.set(yticks=range(3), yticklabels=labels); ax.invert_yaxis(); ax.grid(axis='x', alpha=.18)
    axes[0].set(title='Same S_P: removal effect', xlabel='Answer NLL damage (nats)')
    axes[0].legend(frameon=False, fontsize=9)
    axes[1].set(title='Partner change: R bank B minus P', xlabel='Difference in S_P removal effect (nats)')
    fig.suptitle('Does fixing the realized route change the shared function’s role?', fontsize=13)
    fig.text(.5, .015, 'Full computation; frozen routes were produced with S present. Controlled diagnostic, not a unique mediation fraction.\n'
             'Fresh55 subjects /440 questions; paired95% subject-cluster intervals.', ha='center', fontsize=8.5)
    fig.subplots_adjust(left=.14, right=.98, top=.80, bottom=.23, wspace=.55)
    save(fig, 'shared_partner_role')


def main():
    summary = json.loads((ROOT/'summary.json').read_text())
    audit = json.loads((ROOT/'independent_audit.json').read_text())
    if summary['status'] != 'complete' or audit['status'] != 'passed':
        raise ValueError('Complete and independently checked results required')
    source_effects(summary, 'true_answer_token_NLL', 'source_effects_NLL', 'Answer NLL change (negative = better)')
    source_effects(summary, 'raw_accuracy', 'source_effects_accuracy', 'Accuracy change (percentage points; positive = better)')
    shared(summary)
    print(json.dumps({'status': 'complete', 'figures': 3, 'new_model_forwards': 0}))


if __name__ == '__main__':
    main()
