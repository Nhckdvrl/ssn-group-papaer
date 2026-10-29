"""Organize existing audited estimates into three paper figures; no new tests."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

MOE = Path(__file__).resolve().parents[1]
OUT = MOE / 'paper/figures'
RECORD = {'kind': 'Post-hoc organization; no new model runs, scoring or statistical tests',
          'sources': {}, 'estimates': {}}
BLUE, RED, DARK, GRAY = '#176b9a', '#bf4548', '#30343b', '#92999f'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def source(experiment):
    path = MOE / 'results' / experiment / 'summary.json'
    data = json.loads(path.read_text())
    assert data['status'] == 'complete'
    RECORD['sources'][experiment] = {'path': str(path), 'sha256': sha(path)}
    if experiment in ('e163', 'e164'):
        audit_path = path.parent / 'independent_audit.json'
        audit = json.loads(audit_path.read_text())
        assert audit['status'] == 'passed' and audit['summary_sha256'] == sha(path)
        RECORD['sources'][experiment]['audit_sha256'] = sha(audit_path)
    return data


def get(data, experiment, keys, name):
    value = data
    for key in keys:
        value = value[key]
    ci_key = next(k for k in ('ci95', 'file_ci95', 'question_ci95') if k in value)
    p, lo, hi = value['point'], *value[ci_key]
    assert np.isfinite([p, lo, hi]).all() and lo <= p <= hi
    row = {'point': p, 'ci95': [lo, hi], 'source': experiment,
           'json_path': keys, 'original_CI_field': ci_key}
    RECORD['estimates'][name] = row
    return row


def dot(ax, value, position, color, *, offset=0, label=None, horizontal=False):
    p = value['point']; lo, hi = value['ci95']
    if horizontal:
        ax.errorbar(p, position + offset, xerr=[[p-lo], [hi-p]], color=color,
                    fmt='o', capsize=3, ms=5, label=label)
    else:
        ax.errorbar(position + offset, p, yerr=[[p-lo], [hi-p]], color=color,
                    fmt='o', capsize=3, ms=5, label=label)


def save(fig, name, footer):
    fig.text(.5, .015, footer, ha='center', va='bottom', fontsize=9)
    fig.savefig(OUT / (name + '.png'), dpi=210, bbox_inches='tight')
    fig.savefig(OUT / (name + '.pdf'), bbox_inches='tight')
    plt.close(fig)


def native(s162, s163):
    fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.8))
    names = ('A', 'B', 'F')
    labels = ('Std anneal\nA', 'Late EMO\nB', 'Full EMO\nF')
    for i, name in enumerate(names):
        v = get(s163, 'e163', ['native', 'LM', 'nll', name, 'absolute', 'native'], 'intact_' + name)
        dot(axes[0], v, i, DARK)
        axes[0].annotate(f"{v['point']:.3f}", (i, v['point']), xytext=(0, 9),
                         textcoords='offset points', ha='center', fontsize=10)
        for key, color, off, lab in [('own_prefix_delta_NLL', BLUE, -.11, 'Selected pool'),
                                      ('random_mean_delta_NLL', GRAY, .11, 'Random pools (mean)')]:
            v = get(s162, 'e162', ['budget', name, 'pool', key], key + '_' + name)
            dot(axes[1], v, i, color, offset=off, label=lab if i == 0 else None)
        for key, color, off, lab in [('R_zero', BLUE, -.11, 'Remove routed suite'),
                                      ('S_zero', RED, .11, 'Remove shared suite')]:
            v = get(s163, 'e163', ['native', 'LM', 'nll', name, 'damage', key], key + '_' + name)
            dot(axes[2], v, i, color, offset=off, label=lab if i == 0 else None)
    for ax, title, ylabel in zip(axes,
            ('A  Intact prediction', 'B  Selective execution: 31R + S', 'C  Predictive dependence'),
            ('Text NLL (nats)', 'Budget NLL damage (nats)', 'Removal NLL damage (nats)')):
        ax.set(title=title, ylabel=ylabel, xticks=range(3), xticklabels=labels, xlim=(-.5, 2.5))
        ax.grid(axis='y', alpha=.18)
    axes[1].set_ylim(bottom=0); axes[2].set_ylim(bottom=0)
    axes[1].legend(frameon=False, fontsize=10); axes[2].legend(frameon=False, fontsize=10)
    fig.subplots_adjust(left=.065, right=.99, bottom=.24, top=.88, wspace=.34)
    save(fig, '01_selection_and_dependence',
         'All three published post-annealing paths; no connecting training trajectory is implied.\n'
         '64 language windows / 20 file clusters; original 95% input intervals. R/S denote all 16 layers.')


def transport(s):
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.15), sharey=True)
    labels = ('Natural routes', 'Fixed P routes', 'Fixed B routes')
    keys = ('natural_B_minus_P', 'R_B_minus_P_at_route_P', 'R_B_minus_P_at_route_B')
    for i, key in enumerate(keys):
        for policy, color, off, lab in [('full', DARK, -.075, 'Full computation'),
                                        ('P32', BLUE, .075, 'Common P selector: 31R + S')]:
            v = get(s, 'e164', ['fresh_primary', 'true_answer_token_NLL', policy + '/' + key], policy + '_' + key)
            dot(axes[0], v, i, color, offset=off, label=lab if i == 0 else None, horizontal=True)
    for i, key in enumerate(('natural', 'fixed_route_P', 'fixed_route_B')):
        v = get(s, 'e164', ['fresh_primary', 'true_answer_token_NLL', 'S_partner_change/' + key], 'shared_' + key)
        dot(axes[1], v, i, RED, horizontal=True)
    axes[0].set(title='A  Replacing R_P with R_B', xlabel='Answer NLL change (negative = better)')
    axes[1].set(title='B  Same S_P: change in removal cost', xlabel='NLL damage difference\n(positive = stronger dependence)')
    for ax in axes:
        ax.set(yticks=range(3), yticklabels=labels, ylim=(2.45, -.45))
        ax.axvline(0, color='.6', ls='--', lw=1); ax.grid(axis='x', alpha=.18)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, fontsize=11,
               loc='upper center', bbox_to_anchor=(.5, .995), ncol=2)
    acc = get(s, 'e164', ['fresh_primary', 'raw_accuracy', 'P32/natural_B_minus_P'], 'P32_accuracy')
    ce = get(s, 'e164', ['fresh_primary', 'choice_CE', 'P32/natural_B_minus_P'], 'P32_choice_CE')
    fig.subplots_adjust(left=.15, right=.98, top=.78, bottom=.28, wspace=.24)
    save(fig, '02_property_and_partner_under_fixed_routes',
         'Common P backbone / gate parameters / S_P. Fixed routes clamp support and weights; other responses remain endogenous.\n'
         f"All 55 subjects / 440 questions; paired 95% subject-cluster intervals. Natural P32 choice CE change = {ce['point']:.3f}; "
         f"accuracy = {acc['point']*100:+.2f} pp [{acc['ci95'][0]*100:.2f}, {acc['ci95'][1]*100:.2f}].")


def message(s):
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8))
    for i, rule in enumerate(('raw', 'norm', 'gram')):
        v = get(s, 'e163', ['cross', 'true_answer_token_NLL', 'matching_cost', rule], 'message_' + rule)
        dot(axes[0], v, i, BLUE)
    axes[0].set(title='A  Message mismatch cost', ylabel='Foreign minus own NLL (nats)',
                xticks=range(3), xticklabels=('Raw', 'Norm', 'Gram'), ylim=(0, .33))
    for ax, field, title, xlabel in [(axes[1], 'true_answer_token_NLL', 'B  Gram minus raw', 'NLL cost change (negative = improvement)'),
                                      (axes[2], 'choice_CE', 'C  Decision distribution', 'Choice CE cost change')]:
        base = ['cross', field, 'rule_contrasts', 'gram_minus_raw']
        for i, subject in enumerate(('high_school_biology', 'high_school_mathematics', None)):
            path = base if subject is None else base + ['per_subject', subject]
            v = get(s, 'e163', path, field + '_gram_minus_raw_' + str(subject))
            dot(ax, v, i, BLUE, horizontal=True)
        ax.set(title=title, xlabel=xlabel, yticks=range(3), yticklabels=('Biology', 'Mathematics', 'Mean'), ylim=(2.4, -.4))
        ax.axvline(0, color='.6', ls='--', lw=1)
    for ax in axes:
        ax.grid(alpha=.16)
    fig.subplots_adjust(left=.065, right=.99, top=.88, bottom=.23, wspace=.65)
    save(fig, '03_actual_message_reuse',
         'Same S_P functions and input text; all 27 source × consumer × correction cells retained.\n'
         '128 biology / mathematics questions, original paired 95% input intervals. Norm/Gram use consumer clean scalar witnesses.')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 12, 'axes.titlesize': 13, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42})
    s162, s163, s164 = (source(e) for e in ('e162', 'e163', 'e164'))
    native(s162, s163); transport(s164); message(s163)
    RECORD.update(status='complete', source_code_sha256=sha(__file__),
                  no_new_model_runs=True, no_new_statistical_tests=True,
                  scope='Conditional input intervals; no initialization population or universal modularity claim.',
                  figures={p.name: sha(p) for p in OUT.glob('*') if p.suffix in ('.pdf', '.png')})
    (OUT / 'figure_sources.json').write_text(json.dumps(RECORD, indent=2) + '\n')
    print(json.dumps({'status': 'complete', 'figures': 3, 'estimates': len(RECORD['estimates']),
                      'source_sidecar': str(OUT / 'figure_sources.json')}))


if __name__ == '__main__':
    main()
