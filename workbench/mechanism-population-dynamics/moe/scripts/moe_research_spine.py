"""Plot the completed scientific argument from existing audited estimates.

This is post-hoc figure organization, not a new experiment or statistical test.
No models, raw-data rescoring, fitting, or new bootstrap draws are used. Every
estimate and interval is copied from its original completed experiment; the
sidecar records the exact source file, JSON path, and SHA256 for each panel.
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

MOE = Path(__file__).resolve().parents[1]
ROOT = MOE / 'results/e163'
NAMES = ('P', 'A', 'B', 'F')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative):
    path = MOE / relative
    value = json.loads(path.read_text())
    if value['status'] != 'complete':
        raise ValueError('A completed source is required: ' + relative)
    return value, {'path': str(path), 'sha256': sha(path)}


def estimate(source, keys, records, label):
    value = source
    for key in keys:
        value = value[key]
    ci_key = next(k for k in ('ci95', 'file_ci95', 'question_ci95') if k in value)
    record = {'source_json_path': list(keys), 'point': value['point'],
              'ci95': list(value[ci_key]), 'original_ci_field': ci_key}
    if not np.isfinite([record['point'], *record['ci95']]).all():
        raise ValueError('A plotted estimate is not finite')
    records[label] = record
    return record


def points(ax, values, labels, color, offset=0, horizontal=False, legend=None):
    p = np.array([v['point'] for v in values])
    lo, hi = np.array([v['ci95'] for v in values]).T
    position = np.arange(len(values)) + offset
    if horizontal:
        ax.errorbar(p, position, xerr=[p-lo, hi-p], fmt='o', color=color,
                    capsize=3, ms=5, label=legend)
        ax.set(yticks=np.arange(len(labels)), yticklabels=labels)
    else:
        ax.errorbar(position, p, yerr=[p-lo, hi-p], fmt='o', color=color,
                    capsize=3, ms=5, label=legend)
        ax.set(xticks=np.arange(len(labels)), xticklabels=labels)


def main():
    s163, p163 = load('results/e163/summary.json')
    s156, p156 = load('results/e156/transfer_contrasts.json')
    s159, p159 = load('results/e159/summary.json')
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    audit = json.loads((ROOT / 'independent_audit.json').read_text())
    if (manifest['status'] != 'complete' or audit['status'] != 'passed'
            or manifest['summary_sha256'] != p163['sha256']
            or audit['summary_sha256'] != p163['sha256']):
        raise ValueError('E163 must be complete and independently checked')

    panels = {key: {} for key in 'ABCD'}
    a, b, c, d = (panels[key] for key in 'ABCD')
    quality = [estimate(s163, ['native', 'LM', 'nll', n, 'absolute', 'native'], a, n+'_native') for n in NAMES]
    routed = [estimate(s163, ['native', 'LM', 'nll', n, 'damage', 'R_zero'], a, n+'_remove_R') for n in NAMES]
    shared = [estimate(s163, ['native', 'LM', 'nll', n, 'damage', 'S_zero'], a, n+'_remove_S') for n in NAMES]
    effects = {}
    for policy in ('full', 'receiverP32'):
        effects[policy] = [estimate(s156, ['scopes', 'all_questions', key, 'policies', policy,
                                          'true_answer_token_NLL'], b, key+'_'+policy)
                           for key in ('RB_SP_minus_PP', 'RP_SB_minus_PP')]
    roles = [estimate(s159, ['metrics', 'true_answer_token_NLL', 'shared_necessity', key], c, key)
             for key in ('PP', 'AP', 'BP')]
    reuse = [estimate(s163, ['cross', 'true_answer_token_NLL', 'matching_cost', rule], d, rule)
             for rule in ('raw', 'norm', 'gram')]

    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42})
    fig, axes = plt.subplots(2, 2, figsize=(12.3, 8.2))
    ax = axes[0, 0]
    points(ax, quality, NAMES, '#30343b', offset=-.13, legend='Intact NLL')
    points(ax, routed, NAMES, '#247ba0', legend='Remove R: NLL damage')
    points(ax, shared, NAMES, '#c94c4c', offset=.13, legend='Remove S: NLL damage')
    ax.set(title='A  Similar quality, different R/S dependence', ylabel='Text NLL or NLL damage (nats)', ylim=(0, 7.4))
    ax.legend(frameon=False, fontsize=9, loc='upper right')

    ax = axes[0, 1]
    labels = ('R_B with S_P', 'S_B with R_P')
    points(ax, effects['full'], labels, '#30343b', offset=-.11, horizontal=True, legend='Full computation')
    points(ax, effects['receiverP32'], labels, '#247ba0', offset=.11, horizontal=True, legend='Receiver P: 31R + S')
    ax.axvline(0, color='.65', ls='--', lw=1)
    ax.set(title='B  A budget property transfers; full quality does not',
           xlabel='Answer NLL change from P (negative = better)', ylim=(-.55, 1.65))
    ax.invert_yaxis()
    ax.legend(frameon=False, fontsize=9, loc='lower left')

    ax = axes[1, 0]
    points(ax, roles, ('R_P', 'R_A', 'R_B'), '#c94c4c')
    ax.set(title='C  Same S_P function, different partners',
           ylabel='S_P removal: answer NLL damage (nats)',
           xlabel='R context; P backbone / gate and S_P held fixed', ylim=(0, 1.2))

    ax = axes[1, 1]
    points(ax, reuse, ('Raw', 'Norm corrected', 'Gram corrected'), '#247ba0')
    ax.axhline(0, color='.65', ls='--', lw=1)
    ax.set(title='D  Local geometry correction leaves a reuse cost',
           ylabel='Foreign minus own answer NLL (nats)', ylim=(-.015, .34), xlim=(-.4, 2.4))
    ax.text(.03, .10, 'Same S_P, same input; all 27 cells\nConsumer clean scalar witnesses',
            transform=ax.transAxes, fontsize=9, va='bottom')
    for ax in axes.flat:
        ax.grid(axis='y', alpha=.15)
    fig.suptitle('MoE selection, property transfer, and message reuse can separate', fontsize=15, y=.98)
    fig.text(.5, .025, 'A: 64 windows / 20 file clusters. B–D: all 128 biology + mathematics questions. '
             '95% input CIs, conditional on the fixed models.\n'
             'Published mature paths, not independent training seeds. R/S denote all 16 layer suites. '
             'Likelihood and accuracy remain separate in the full results.',
             ha='center', va='bottom', fontsize=8.5)
    fig.subplots_adjust(left=.075, right=.98, top=.90, bottom=.15, wspace=.37, hspace=.48)
    out = ROOT / 'figures'
    out.mkdir(exist_ok=True)
    fig.savefig(out / 'research_spine.png', dpi=190, bbox_inches='tight')
    fig.savefig(out / 'research_spine.pdf', bbox_inches='tight')
    plt.close(fig)
    sidecar = {'status': 'complete', 'kind': 'Post-hoc organization of existing estimates; no new tests',
               'sources': {'A_D': p163, 'B': p156, 'C': p159}, 'panels': panels,
               'full_results': ['e156/transfer_contrasts.json', 'e159/summary.json', 'e163/summary.json'],
               'scope': 'Input intervals, not seed or task-population intervals. Full grids and accuracy remain in original results.',
               'plot_source_sha256': sha(Path(__file__))}
    (ROOT / 'research_spine.json').write_text(json.dumps(sidecar, indent=2)+'\n')
    print(json.dumps({'status': 'complete', 'figure': str(out / 'research_spine.png'),
                      'new_model_runs': 0, 'new_statistical_tests': 0}))


if __name__ == '__main__':
    main()
