"""E156 source-cross figures from the sealed analysis summary, CPU only."""
import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1] / 'results' / 'e156'
SOURCES = ('P', 'A', 'B')
POLICIES = ('full', 'receiverP32')


def value(record):
    return float(record['point'])


def matrix(cross, policy, metric):
    return np.array([[value(cross[r+s][policy][metric]) for s in SOURCES] for r in SOURCES])


def interval(record):
    lo, hi = record['question_ci95']
    return f"{record['point']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def native_caption(native, metric):
    return ' / '.join(f"{s} {value(native[s]['full'][metric]):.3f} / {value(native[s]['receiverP32'][metric]):.3f}" for s in SOURCES)


def render(summary, scope, output):
    row = summary['scopes'][scope]
    cross, native = row['cross'], row['native']
    contrasts = row['AB_source_contrasts']
    # Damage is full minus masked for accuracy, masked minus full for NLL.
    acc_full = matrix(cross, 'full', 'raw_accuracy')
    acc_mask = matrix(cross, 'receiverP32', 'raw_accuracy')
    acc_drop = matrix(cross, 'receiverP32', 'accuracy_drop')
    nll_full = matrix(cross, 'full', 'true_answer_token_NLL')
    nll_mask = matrix(cross, 'receiverP32', 'true_answer_token_NLL')
    nll_increase = matrix(cross, 'receiverP32', 'true_answer_token_NLL_increase')
    grids = ((acc_full, acc_mask, acc_drop), (nll_full, nll_mask, nll_increase))
    titles = (('Full accuracy', 'P-mask accuracy', 'Accuracy drop'),
              ('Full answer-token NLL', 'P-mask answer-token NLL', 'NLL increase'))
    fig, axes = plt.subplots(2, 3, figsize=(12.4, 9.7), layout=None)
    fig.subplots_adjust(left=.075, right=.96, top=.88, bottom=.36, wspace=.31, hspace=.36)
    for ri in range(2):
        shared = np.concatenate((grids[ri][0].ravel(), grids[ri][1].ravel()))
        lo, hi = float(shared.min()), float(shared.max())
        if lo == hi: lo -= .5; hi += .5
        common_norm = Normalize(vmin=lo, vmax=hi)
        bound = max(float(np.max(np.abs(grids[ri][2]))), 1e-12)
        for ci in range(3):
            ax = axes[ri, ci]
            norm = common_norm if ci < 2 else TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound)
            cmap = 'viridis' if ci < 2 else 'coolwarm'
            arr = grids[ri][ci]
            im = ax.imshow(arr, cmap=cmap, norm=norm, aspect='equal')
            ax.set_xticks(range(3), SOURCES); ax.set_yticks(range(3), SOURCES)
            ax.set_xlabel('S source'); ax.set_ylabel('R source')
            ax.set_title(titles[ri][ci], fontsize=11)
            for i in range(3):
                for j in range(3):
                    color = 'white' if ci < 2 and norm(arr[i,j]) < .48 else 'black'
                    ax.text(j, i, f'{arr[i,j]:.3f}', ha='center', va='center', color=color, fontsize=10)
            fig.colorbar(im, ax=ax, fraction=.046, pad=.04)
    subtitle = ('All questions (64 biology + 64 mathematics)' if scope == 'all_questions' else
                'Common native success (44 questions: 36 biology + 8 mathematics); not independent confirmation')
    fig.suptitle('E156: R/S source cross in common P receiver (D/G = P)\n' + subtitle, fontsize=13)
    cfull, cmask, cbudget = contrasts['policies']['full'], contrasts['policies']['receiverP32'], contrasts['budget']
    caption = (
        'Native reference, full / P-mask:  accuracy  ' + native_caption(native, 'raw_accuracy') + '\n'
        'Native reference, full / P-mask:  answer-token NLL  ' + native_caption(native, 'true_answer_token_NLL') + '\n'
        'A/B same-source advantage (same − cross accuracy):  full ' + interval(cfull['raw_accuracy']) +
        ';  P-mask ' + interval(cmask['raw_accuracy']) + '\n'
        'A/B matching contrast (cross − same NLL):  full ' + interval(cfull['true_answer_token_NLL']) +
        ';  P-mask ' + interval(cmask['true_answer_token_NLL']) + '\n'
        'A/B budget damage contrast (cross − same):  accuracy drop ' + interval(cbudget['accuracy_drop']) +
        ';  NLL increase ' + interval(cbudget['true_answer_token_NLL_increase']) + '\n'
        'Intervals: paired question bootstrap within each fixed subject, equal subject macro. '
        'A/B contrast excludes the P/P identity corner.'
    )
    fig.text(.075, .27, caption, va='top', ha='left', fontsize=9, linespacing=1.55)
    output.mkdir(parents=True, exist_ok=True)
    for extension in ('png','pdf'):
        fig.savefig(output / f'e156_source_cross_{scope}.{extension}', dpi=200, bbox_inches='tight')
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--summary', type=Path, default=ROOT/'summary.json')
    p.add_argument('--output', type=Path, default=ROOT/'figures')
    args = p.parse_args()
    summary = json.loads(args.summary.read_text())
    if summary.get('experiment') != 'E156' or summary.get('status') != 'complete':
        raise ValueError('A complete E156 summary is required')
    if tuple(summary['source_order']) != SOURCES or tuple(summary['policy_order']) != POLICIES:
        raise ValueError('Unexpected source or policy order')
    for scope in ('all_questions', 'common_native_success'):
        render(summary, scope, args.output)


if __name__ == '__main__':
    main()
