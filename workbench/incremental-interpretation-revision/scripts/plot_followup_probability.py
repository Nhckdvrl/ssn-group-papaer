"""Render the fixed E13 primary and secondary contrasts; no source text."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def draw(summary, out):
    d = json.loads(summary.read_text())
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6), constrained_layout=True)
    for ax in axes:
        ax.axvline(0, color='#777777', lw=1, linestyle='--')
        ax.spines[['top', 'right']].set_visible(False)
    def points(ax, stats, labels):
        for i, v in enumerate(stats):
            x = v['estimate']; low, high = v['ci95']
            ax.errorbar(x, i, xerr=[[x-low], [high-x]], fmt='o', capsize=4, color='#245b86')
        ax.set_yticks(range(len(labels)), labels)
        ax.invert_yaxis()
        ax.set_ylim(len(labels)-.6, -.6)
    points(axes[0], [d['gp_minus_comma'][f'all24/second_sentence_mean_bits/option{i}'] for i in (0, 1)],
           ['Source NP option 0', 'Source NP option 1'])
    axes[0].set_title('Primary: all second-sentence words\n24 source sets')
    axes[0].set_xlabel('GP minus comma, mean bits / word')
    points(axes[1], [d['option0_minus_option1_gp_effect'][f'all24/{m}'] for m in
                    ('pre_reference_mean_bits', 'literal_reference_mean_bits', 'post_reference_mean_bits')],
           ['Up to 2 words before', 'Literal reference', 'Up to 2 words after'])
    axes[1].set_title('Secondary: NP option interaction\n22 reference-bearing source sets')
    axes[1].set_xlabel('(GP − comma) option 0 − option 1, bits / word')
    fig.suptitle('E13: original published continuations, no diagnostic question\nPaired source-set bootstrap 95% CI; conditional prediction is not parse accuracy', fontsize=11)
    for ext in ('png', 'pdf'):
        fig.savefig(out.with_suffix('.' + ext), dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('summary', type=Path)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    draw(a.summary, a.out)
