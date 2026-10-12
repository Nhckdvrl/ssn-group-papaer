"""Figures and numbers for the LaTeX manuscript in paper/.

Every value is read from confirmation-split result files (n=32 contexts per checkpoint);
nothing is fitted or selected here. Reconstruction scatters recompute the per-query rule
double contrast exactly as in scripts/e121_natural_sentiment_mechanism.py and check the
correlation against the stored analysis.

Run with an environment that has numpy and matplotlib, from the workbench root:
    python scripts/paper_figures_v2.py
Writes paper/figures/*.pdf and paper/figures/numbers.json.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'results'
OUT = ROOT / 'paper' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)

COL_W, FULL_W = 3.03, 6.30
plt.rcParams.update({
    'font.family': 'Nimbus Roman', 'mathtext.fontset': 'stix', 'font.size': 8,
    'axes.titlesize': 8, 'axes.labelsize': 8, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'legend.fontsize': 7, 'axes.linewidth': .6, 'xtick.major.width': .6, 'ytick.major.width': .6,
    'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'axes.spines.top': False,
    'axes.spines.right': False, 'pdf.fonttype': 42, 'savefig.bbox': 'tight', 'savefig.pad_inches': .02})

# One palette for the whole paper.
GRAY, BLUE, ORANGE, RED, GREEN, LIGHT = '#6b6b6b', '#2f6db3', '#e08a2c', '#c4473d', '#3c9a64', '#b9c7d8'

MODELS = [  # label, function source, operation source, reconstruction source
    ('Qwen3-8B', 'e123/qwen3_confirmation', 'e120/qwen3_confirmation', 'e121/qwen3_confirmation'),
    ('Qwen3-14B', 'e123/qwen14_confirmation', 'e120/qwen14_confirmation', 'e121/qwen14_confirmation'),
    ('Qwen3-32B', 'e131/qwen32_confirmation_function', 'e131/qwen32_confirmation_native',
     'e131/qwen32_confirmation_mechanism'),
    ('Mistral-7B', 'e123/mistral_confirmation', 'e120/mistral_confirmation', 'e121/mistral_confirmation'),
    ('Llama-3.1-8B', 'e123/llama_confirmation', 'e120/llama_confirmation', 'e121/llama_confirmation'),
    ('Llama-3.1-70B', 'e131/llama70_confirmation_function', 'e131/llama70_confirmation_native',
     'e131/llama70_confirmation_mechanism'),
]
SHORT = {'Qwen3-8B': 'Qwen3\n8B', 'Qwen3-14B': 'Qwen3\n14B', 'Qwen3-32B': 'Qwen3\n32B',
         'Mistral-7B': 'Mistral\n7B', 'Llama-3.1-8B': 'Llama\n8B', 'Llama-3.1-70B': 'Llama\n70B'}


def load(path, name='analysis.json'):
    return json.loads((RES / path / name).read_text())


def stat(d, scale=1.0):
    return {'mean': d['mean'] * scale, 'lo': d['ci95'][0] * scale, 'hi': d['ci95'][1] * scale}


numbers = {'note': 'Confirmation split, n=32 contexts per checkpoint; 95% context-bootstrap intervals.'}


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=250)
    plt.close(fig)


# ---------------------------------------------------------------- Figure 2: cross-source effect
def fig_leak():
    conds = [('shared_normal_native', 'Shared, full reading', GRAY, 'o'),
             ('shared_normal_gate', 'Shared, A-only reading', BLUE, 'o'),
             ('shared_answer_cross_off_gate', 'Shared, A-only, path blocked', GREEN, 'D'),
             ('far_normal_gate', 'Separate, A-only reading', ORANGE, 's')]
    out = {}
    fig, ax = plt.subplots(figsize=(COL_W, 2.0))
    x = np.arange(len(MODELS))
    w = .19
    for j, (key, label, color, marker) in enumerate(conds):
        for i, (m, fsrc, _, _) in enumerate(MODELS):
            s = stat(load(fsrc)['A_B_code_response'][key]['signed'])
            out.setdefault(m, {})[key] = s
            xi = x[i] + (j - 1.5) * w
            ax.bar(xi, s['mean'], w * .92, color=color, alpha=.9 if j else .55, lw=0,
                   label=label if i == 0 else None)
            ax.errorbar(xi, s['mean'], yerr=[[s['mean'] - s['lo']], [s['hi'] - s['mean']]], fmt='none',
                        ecolor='black', elinewidth=.6, capsize=1.2, capthick=.6)
        for i, (m, fsrc, _, _) in enumerate(MODELS):
            out[m]['within_class_control_gate'] = stat(
                load(fsrc)['A_B_code_response']['shared_normal_gate']['within_signed'])
    ax.axhline(0, color='black', lw=.5)
    ax.set_xticks(x, [SHORT[m[0]] for m in MODELS])
    ax.tick_params(axis='x', length=0, pad=2)
    ax.set_ylabel("Pull of B's convention\non A's margin (nats)")
    ax.set_ylim(-.25, 3.2)
    ax.legend(loc='lower left', bbox_to_anchor=(-.02, 1.0), ncol=2, frameon=False, handlelength=1,
              columnspacing=.6, handletextpad=.35, borderaxespad=.1, fontsize=6.6)
    save(fig, 'fig_leak')
    numbers['cross_source_effect_sst'] = out


# ---------------------------------------------------------------- Figure 3: reconstruction scatter
def rule_double(dest, kind='kv', r=0):
    rows = [json.loads(x) for x in (RES / dest / 'behavior.jsonl').read_text().splitlines()]
    z = lambda k: np.array([row['conditions'][k]['z'] for row in rows])
    target = (z(f'cross_label_r{r}') - z(f'cross_f0r{r}')) - (z(f'origin_label_r{r}') - z(f'origin_f0r{r}'))
    pred = (z(f'cross_edge_{kind}_r{r}') - z(f'cross_f0r{r}')) - (z(f'origin_edge_{kind}_r{r}') - z(f'origin_f0r{r}'))
    return target.ravel(), pred.ravel()


def fig_reconstruction():
    fig, axes = plt.subplots(1, 6, figsize=(FULL_W, 1.32))
    out = {}
    for ax, (m, _, _, rsrc) in zip(axes, MODELS):
        t, p = rule_double(rsrc)
        r = float(np.corrcoef(t, p)[0, 1])
        stored = load(rsrc)['reconstruction']['label_interface_B0_kv']
        assert abs(r - stored['rule_double_contrast']['correlation']) < 1e-6, (m, r)
        rd = stored['rule_double_contrast']
        out[m] = {'r': r, 'r_lo': rd['correlation_ci95'][0], 'r_hi': rd['correlation_ci95'][1],
                  'rmse': rd['rmse'], 'zero_rmse': rd['zero_rmse'], 'n_points': int(t.size),
                  'raw_r': stored['raw']['correlation']}
        lim = np.percentile(np.abs(np.r_[t, p]), 99.5) * 1.08
        ax.plot([-lim, lim], [-lim, lim], color=GRAY, lw=.6, ls='--', zorder=1)
        ax.scatter(p, t, s=3.5, color=BLUE, alpha=.45, lw=0, zorder=2)
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect('equal')
        ax.set_title(m, pad=2)
        ax.text(.04, .96, f'$r$ = {r:.2f}', transform=ax.transAxes, va='top', fontsize=7)
        ax.locator_params(nbins=3)
    axes[0].set_ylabel('Actual effect (nats)')
    fig.supxlabel('Predicted by patching B-answer messages at A-label positions (nats)', fontsize=8, y=-.06)
    fig.subplots_adjust(wspace=.45)
    save(fig, 'fig_reconstruction')
    numbers['reconstruction_sst_kv'] = out


# ---------------------------------------------------------------- Table 1: native operation
def table_operation():
    out = {}
    for m, _, osrc, _ in MODELS:
        a = load(osrc)
        R, C = a['responses'], a['contrasts']
        out[m] = {
            'effect_full_reading': stat(R['shared_native_native']['rule_signed']),
            'effect_A_only_reading': stat(R['shared_gate_native']['rule_signed']),
            'removal_A_only_reading': stat(C['shared_gate_cross_answer_removal']['rule_signed']),
            'removal_full_reading': stat(C['shared_native_cross_answer_removal']['rule_signed']),
            'within_source_removal_full_reading': stat(C['shared_native_within_answer_removal']['rule_signed']),
            'restoration_A_only_reading': stat(C['shared_gate_answer_path_restoration']['rule_signed']),
            'restoration_full_reading': stat(C['shared_native_answer_path_restoration']['rule_signed']),
        }
    numbers['native_operation_restaurant'] = out


# ---------------------------------------------------------------- Table 2 + Figure 4a: policies
def policies():
    out = {}
    for m, fsrc, _, _ in MODELS:
        full = load(fsrc, 'full_output_summary.json')
        cand = load(fsrc)
        P, C = full['policy_accuracy'], full['contrasts']
        out[m] = {
            'native': stat(P['shared_normal_native']['both'], 100),
            'native_opposite': stat(P['shared_normal_native']['opposite_convention'], 100),
            'native_same': stat(P['shared_normal_native']['same_convention'], 100),
            'selective': stat(P['shared_answer_cross_off_native']['both'], 100),
            'complete': stat(P['shared_all_cross_off_native']['both'], 100),
            'query_only': stat(P['shared_normal_gate']['both'], 100),
            'selective_plus_query': stat(P['shared_answer_cross_off_gate']['both'], 100),
            'd_selective': stat(C['shared_answer_cross_off_minus_normal_native']['both'], 100),
            'd_selective_A': stat(C['shared_answer_cross_off_minus_normal_native']['A'], 100),
            'd_selective_B': stat(C['shared_answer_cross_off_minus_normal_native']['B'], 100),
            'd_selective_opposite': stat(C['shared_answer_cross_off_minus_normal_native']['opposite_convention'], 100),
            'd_selective_same': stat(C['shared_answer_cross_off_minus_normal_native']['same_convention'], 100),
            'd_complete': stat(C['shared_all_cross_off_minus_normal_native']['both'], 100),
            'd_selective_minus_complete': stat(C['shared_answer_minus_all_native']['both'], 100),
            'd_query_only': stat(C['shared_query_isolation_normal']['both'], 100),
            'sep_native_full': stat(P['far_normal_native']['both'], 100),
            'sep_complete_full': stat(P['far_all_cross_off_native']['both'], 100),
            'sep_complete_candidate': stat(cand['policy_accuracy']['far_all_cross_off_native']['both'], 100),
            'sep_native_candidate': stat(cand['policy_accuracy']['far_normal_native']['both'], 100),
            'sep_complete_other_word': stat(P['far_all_cross_off_native']['other_source_word'], 100),
        }
    numbers['policies_sst'] = out
    return out


def fig_separate_and_schema(pol):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 1.75), gridspec_kw={'width_ratios': [1.55, 1]})
    x = np.arange(len(MODELS)); w = .26
    bars = [('sep_native_full', 'Native', GRAY),
            ('sep_complete_candidate', 'Isolated: own two words', LIGHT),
            ('sep_complete_full', 'Isolated: full vocabulary', RED)]
    for j, (key, label, color) in enumerate(bars):
        for i, (m, *_rest) in enumerate(MODELS):
            s = pol[m][key]; xi = x[i] + (j - 1) * w
            ax1.bar(xi, s['mean'], w * .92, color=color, lw=0, label=label if i == 0 else None)
            ax1.errorbar(xi, s['mean'], yerr=[[s['mean'] - s['lo']], [s['hi'] - s['mean']]], fmt='none',
                         ecolor='black', elinewidth=.6, capsize=1.2, capthick=.6)
    ax1.axhline(50, color=GRAY, lw=.5, ls=':')
    ax1.set_xticks(x, [SHORT[m[0]] for m in MODELS]); ax1.tick_params(axis='x', length=0, pad=2)
    ax1.set_ylim(0, 112); ax1.set_yticks([0, 25, 50, 75, 100]); ax1.set_ylabel('Accuracy (%)')
    ax1.set_title('(a) Separate label words', loc='left', pad=15)
    ax1.legend(loc='lower left', bbox_to_anchor=(-.01, .99), ncol=3, frameon=False, handlelength=1,
               columnspacing=.7, handletextpad=.35, borderaxespad=.1, fontsize=6.6)

    s125 = json.loads((RES / 'e125' / 'summary.json').read_text())['runs']
    names = [('qwen3', 'Qwen3-8B'), ('mistral', 'Mistral-7B'), ('llama', 'Llama-3.1-8B')]
    sch = {}
    for i, (k, m) in enumerate(names):
        c = s125[f'{k}_confirmation']['analysis']['contrasts']
        sch[m] = {'formation': stat(c['formation_true_minus_unrelated_gain']['both'], 100),
                  'reading': stat(c['reading_true_minus_unrelated_gain']['both'], 100),
                  'formation_true_minus_swapped': stat(c['formation_true_minus_swapped_gain']['both'], 100),
                  'swapped_formation_gain': stat(c['swapped_formation_only_gain']['both'], 100)}
        for j, (key, label, color) in enumerate([('formation', 'Read during formation', BLUE),
                                                  ('reading', 'Read by the query', ORANGE)]):
            s = sch[m][key]; xi = i + (j - .5) * .34
            ax2.bar(xi, s['mean'], .31, color=color, lw=0, label=label if i == 0 else None)
            ax2.errorbar(xi, s['mean'], yerr=[[s['mean'] - s['lo']], [s['hi'] - s['mean']]], fmt='none',
                         ecolor='black', elinewidth=.6, capsize=1.2, capthick=.6)
    ax2.axhline(0, color='black', lw=.5)
    ax2.set_xticks(range(3), [SHORT[m] for _, m in names]); ax2.tick_params(axis='x', length=0, pad=2)
    ax2.set_ylabel('Gain over unrelated\ntable (points)'); ax2.set_ylim(-2, 33)
    ax2.set_title('(b) Public word-set table', loc='left', pad=15)
    ax2.legend(loc='lower left', bbox_to_anchor=(-.01, .99), ncol=2, frameon=False, handlelength=1,
               columnspacing=.7, handletextpad=.35, borderaxespad=.1, fontsize=6.6)
    fig.subplots_adjust(wspace=.36)
    save(fig, 'fig_separate_schema')
    numbers['public_schema_sst'] = sch


if __name__ == '__main__':
    fig_leak()
    fig_reconstruction()
    table_operation()
    pol = policies()
    fig_separate_and_schema(pol)
    (OUT / 'numbers.json').write_text(json.dumps(numbers, indent=1) + '\n')
    print('wrote', sorted(p.name for p in OUT.iterdir()))


# ---------------------------------------------------------------- appendix tables (LaTeX)
TAB = ROOT / 'paper' / 'tables'


def cell(s, d=2):
    return f"{s['mean']:.{d}f}\\ci{{{s['lo']:.{d}f}}}{{{s['hi']:.{d}f}}}".replace('-', '$-$')


def write_table(name, rows):
    TAB.mkdir(exist_ok=True)
    (TAB / f'{name}.tex').write_text('\n'.join(rows) + '\n')


def appendix_tables():
    ce = numbers['cross_source_effect_sst']
    rows = []
    for m, *_ in MODELS:
        v = ce[m]
        rows.append(f"{m} & {cell(v['shared_normal_native'])} & {cell(v['shared_normal_gate'])} & "
                    f"{cell(v['shared_answer_cross_off_gate'])} & {cell(v['far_normal_gate'])} & "
                    f"{cell(v['within_class_control_gate'])} \\\\")
    write_table('app_leak', rows)
    anchors = {}
    for m, src in [('Qwen3-8B', 'e131/qwen3_confirmation_function'), ('Qwen3-32B', 'e131/qwen32_confirmation_function'),
                   ('Llama-3.1-8B', 'e131/llama_confirmation_function'), ('Llama-3.1-70B', 'e131/llama70_confirmation_function')]:
        a = load(src)['A_B_code_response']
        anchors[m] = {k: stat(a[k]['signed']) for k in ['shared_normal_native', 'shared_normal_gate', 'shared_answer_cross_off_gate']}
    numbers['cross_source_effect_matched_sizes'] = anchors
    write_table('app_leak_matched', [f"{m} & {cell(v['shared_normal_native'])} & {cell(v['shared_normal_gate'])} & "
                                     f"{cell(v['shared_answer_cross_off_gate'])} \\\\" for m, v in anchors.items()])

    rows = []
    for m, _, _, rsrc in MODELS:
        rec = load(rsrc)['reconstruction']
        parts = []
        for ch in ['k', 'v', 'kv']:
            rd = rec[f'label_interface_B0_{ch}']['rule_double_contrast']
            parts.append(f"{rd['correlation']:.2f}")
        rd = rec['label_interface_B0_kv']['rule_double_contrast']
        rs = rec['label_interface_B1_kv']['rule_double_contrast']
        rows.append(f"{m} & {' & '.join(parts)} & {rd['correlation_ci95'][0]:.2f}--{rd['correlation_ci95'][1]:.2f} & "
                    f"{rd['rmse']:.2f} & {rd['zero_rmse']:.2f} & {rs['correlation']:.2f} \\\\")
    write_table('app_reconstruction', rows)

    op = numbers['native_operation_restaurant']
    for m, *_ in MODELS:
        src = dict((x[0], x[2]) for x in MODELS)[m]
        C = load(src)['contrasts']
        op[m]['within_source_removal_A_only'] = stat(C['shared_gate_within_answer_removal']['rule_signed'])
    write_table('app_operation_gate', [f"{m} & {cell(v['effect_A_only_reading'])} & {cell(v['removal_A_only_reading'])} & "
                                       f"{cell(v['within_source_removal_A_only'])} & {cell(v['restoration_A_only_reading'])} \\\\"
                                       for m, v in op.items()])
    write_table('app_operation_full', [f"{m} & {cell(v['effect_full_reading'])} & {cell(v['removal_full_reading'])} & "
                                       f"{cell(v['within_source_removal_full_reading'])} & {cell(v['restoration_full_reading'])} \\\\"
                                       for m, v in op.items()])

    rows, assoc = [], {}
    for m, _, _, rsrc in MODELS:
        R = load(rsrc)['relation']
        assoc[m] = {'full': stat(R['full_native']['absolute_effect']), 'answer_abs': stat(R['answer_native']['absolute_effect']),
                    'answer_signed': stat(R['answer_native']['signed_effect']), 'label_abs': stat(R['label_native']['absolute_effect'])}
        v = assoc[m]
        rows.append(f"{m} & {cell(v['full'])} & {cell(v['label_abs'])} & {cell(v['answer_abs'])} & {cell(v['answer_signed'])} \\\\")
    numbers['association_sst'] = assoc
    write_table('app_association', rows)

    pol = numbers['policies_sst']
    for m, fsrc, *_ in MODELS:
        P = load(fsrc, 'full_output_summary.json')['policy_accuracy']
        pol[m]['complete_plus_query'] = stat(P['shared_all_cross_off_gate']['both'], 100)
        pol[m]['complete_opposite'] = stat(P['shared_all_cross_off_native']['opposite_convention'], 100)
        pol[m]['complete_same'] = stat(P['shared_all_cross_off_native']['same_convention'], 100)
        pol[m]['selective_opposite'] = stat(P['shared_answer_cross_off_native']['opposite_convention'], 100)
    write_table('app_policy_acc', [f"{m} & {cell(v['native'],1)} & {cell(v['selective'],1)} & {cell(v['complete'],1)} & "
                                   f"{cell(v['query_only'],1)} & {cell(v['selective_plus_query'],1)} & {cell(v['complete_plus_query'],1)} \\\\"
                                   for m, v in pol.items()])
    write_table('app_policy_delta', [f"{m} & {cell(v['d_selective'],1)} & {cell(v['d_selective_A'],1)} & {cell(v['d_selective_B'],1)} & "
                                     f"{cell(v['d_selective_opposite'],1)} & {cell(v['d_selective_same'],1)} \\\\" for m, v in pol.items()])
    write_table('app_policy_other', [f"{m} & {cell(v['d_complete'],1)} & {cell(v['d_query_only'],1)} & {cell(v['complete_opposite'],1)} & "
                                     f"{cell(v['complete_same'],1)} & {cell(v['selective_opposite'],1)} \\\\" for m, v in pol.items()])
    write_table('app_separate', [f"{m} & {cell(v['sep_native_candidate'],1)} & {cell(v['sep_native_full'],1)} & "
                                 f"{cell(v['sep_complete_candidate'],1)} & {cell(v['sep_complete_full'],1)} & {cell(v['sep_complete_other_word'],1)} \\\\"
                                 for m, v in pol.items()])
    sch = numbers['public_schema_sst']
    write_table('app_schema', [f"{m} & {cell(v['formation'],1)} & {cell(v['reading'],1)} & {cell(v['swapped_formation_gain'],1)} & "
                               f"{cell(v['formation_true_minus_swapped'],1)} \\\\" for m, v in sch.items()])


appendix_tables()
(OUT / 'numbers.json').write_text(json.dumps(numbers, indent=1) + '\n')


# ---------------------------------------------------------------- Figure: accuracy by convention world
def fig_worlds():
    pols = [('shared_normal_native', 'Native', GRAY, 'o'), ('shared_answer_cross_off_native', 'Selective blocking', GREEN, 'D'),
            ('shared_all_cross_off_native', 'Complete isolation', RED, 'X'), ('shared_normal_gate', 'A-only reading', BLUE, 's')]
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.75), sharey=True, gridspec_kw={'width_ratios': [1, 1]})
    out = {}
    for ax, world, title in [(axes[0], 'opposite_convention', 'Conflicting conventions'),
                             (axes[1], 'same_convention', 'Agreeing conventions')]:
        for j, (key, label, color, marker) in enumerate(pols):
            for i, (m, fsrc, *_r) in enumerate(MODELS):
                st = stat(load(fsrc, 'full_output_summary.json')['policy_accuracy'][key][world], 100)
                out.setdefault(m, {}).setdefault(world, {})[key] = st
                xi = i + (j - 1.5) * .17
                ax.errorbar(xi, st['mean'], yerr=[[st['mean'] - st['lo']], [st['hi'] - st['mean']]], fmt=marker,
                            color=color, ms=3.2, mew=0, elinewidth=.6, capsize=0, label=label if i == 0 else None)
        ax.axhline(50, color=GRAY, lw=.5, ls=':')
        ax.set_xticks(range(len(MODELS)), ['Q8', 'Q14', 'Q32', 'M7', 'L8', 'L70'], fontsize=6.5)
        ax.tick_params(axis='x', length=0, pad=1.5)
        ax.set_title(title, pad=2)
        ax.set_ylim(40, 101)
    axes[0].set_ylabel('Accuracy (%)')
    axes[0].legend(loc='lower left', bbox_to_anchor=(-.22, 1.12), ncol=4, frameon=False, handlelength=.8,
                   columnspacing=.6, handletextpad=.25, borderaxespad=0, fontsize=6.4)
    fig.subplots_adjust(wspace=.08)
    save(fig, 'fig_worlds')
    numbers['policies_by_world_sst'] = out


fig_worlds()
(OUT / 'numbers.json').write_text(json.dumps(numbers, indent=1) + '\n')
