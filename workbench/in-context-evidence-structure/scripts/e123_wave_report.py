"""Completeness, full-output reporting, and plots for the frozen E123 wave.

Does not modify scientific scores or primary candidate-space readouts.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from e118_criterion_code_feature_crossing import interval

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [('qwen3', 'Qwen3-8B'), ('mistral', 'Mistral-7B'),
            ('llama', 'Llama-3.1-8B'), ('qwen14', 'Qwen3-14B')]
POLICIES = ['normal', 'answer_cross_off', 'all_cross_off']
SCOPES = ['native', 'gate']
CONDITIONS = [('normal_native', 'Native'), ('answer_cross_off_native', 'Answer\nformation'),
              ('all_cross_off_native', 'All cross-source\nformation'), ('normal_gate', 'Query\nonly'),
              ('answer_cross_off_gate', 'Answer +\nquery'), ('all_cross_off_gate', 'All formation\n+ query')]


def output_metrics(raw, preflight):
    """Readouts on the exact same primary world/source/query weighting."""
    agg, out, differences = {}, {}, {}
    for ns in ['shared', 'far']:
        for policy in POLICIES:
            for scope in SCOPES:
                correct = np.asarray([[[r['conditions'][f'{w}_{ns}_{policy}_{scope}_{owner}']['argmax_correct']
                    for owner in [0, 1]] for w in ['origin', 'cross']] for r in raw], dtype=float)
                other_word = np.asarray([[[[int(t in preflight['word_ids']['far' if owner == 0 else 'shared'])
                    if ns == 'far' else 0 for t in r['conditions'][f'{w}_{ns}_{policy}_{scope}_{owner}']['argmax_token']]
                    for owner in [0, 1]] for w in ['origin', 'cross']] for r in raw], dtype=float)
                values = {'both': correct.mean((1, 2, 3)), 'A': correct[:, :, 0].mean((1, 2)),
                          'B': correct[:, :, 1].mean((1, 2)), 'opposite_convention': correct[:, 0].mean((1, 2)),
                          'same_convention': correct[:, 1].mean((1, 2)),
                          'other_source_word': other_word.mean((1, 2, 3)),
                          'A_other_source_word': other_word[:, :, 0].mean((1, 2)),
                          'B_other_source_word': other_word[:, :, 1].mean((1, 2))}
                agg[ns, policy, scope] = values
                out[f'{ns}_{policy}_{scope}'] = {k: interval(v) for k, v in values.items()}
        for scope in SCOPES:
            for policy in POLICIES[1:]:
                differences[f'{ns}_{policy}_minus_normal_{scope}'] = {k: interval(
                    agg[ns, policy, scope][k] - agg[ns, 'normal', scope][k]) for k in agg[ns, 'normal', scope]}
            differences[f'{ns}_answer_minus_all_{scope}'] = {k: interval(
                agg[ns, 'answer_cross_off', scope][k] - agg[ns, 'all_cross_off', scope][k])
                for k in agg[ns, 'normal', scope]}
        for policy in POLICIES:
            differences[f'{ns}_query_isolation_{policy}'] = {k: interval(
                agg[ns, policy, 'gate'][k] - agg[ns, policy, 'native'][k]) for k in agg[ns, policy, 'native']}
    return {'policy_accuracy': out, 'contrasts': differences,
            'scope': 'Secondary full-vocabulary and other-source-word readouts; original primary unchanged.'}


def collect():
    runs, records = {}, []
    for family, label in FAMILIES:
        for phase in ['discovery', 'confirmation']:
            dest = ROOT / 'results/e123' / f'{family}_{phase}'
            if not (dest / 'run.json').exists() or not (dest / 'analysis.json').exists():
                continue
            run, analysis, preflight = [json.loads((dest / f'{s}.json').read_text())
                                       for s in ['run', 'analysis', 'preflight']]
            raw = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
            assert len(raw) == analysis['n_contexts'] == run['args']['n']
            keys = set(raw[0]['conditions'])
            assert len(keys) == 85 and all(set(r['conditions']) == keys for r in raw)
            assert all(len(v['z']) == len(v['gold']) == len(v['argmax_correct']) == 8
                       for r in raw for v in r['conditions'].values())
            assert run['script_sha256'] == '95a574892e7609a25146f730f7843d176fe27487353f2ad7c9fa7fd01971e9a5'
            assert all(run[k] <= .001 for k in ['numeric_max_error', 'native_mask_cache_max_error', 'graph_zero_max_error'])
            assert all({int(k) for k in v} == set(range(run['num_layers'])) and set(v.values()) == {len(raw)}
                       for v in run['all_layer_consumption'].values())
            audit = {'contexts': len(raw), 'conditions': 85, 'queries': 8, 'scores': len(raw) * 680,
                     'all_conditions_retained': True, 'source_sha256': run['script_sha256'],
                     'raw_sha256': hashlib.sha256((dest / 'behavior.jsonl').read_bytes()).hexdigest(),
                     'author_completion_check': True, 'independent_review': 'separate session/report'}
            full = output_metrics(raw, preflight)
            (dest / 'completeness_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
            (dest / 'full_output_summary.json').write_text(json.dumps(full, indent=2) + '\n')
            runs[f'{family}_{phase}'] = {'audit': audit, 'gpu_hours': run['gpu_hours'],
                'analysis': analysis, 'full_output': full}
            for kind, source in [('candidate', analysis), ('full_vocabulary', full)]:
                for key, values in source['policy_accuracy'].items():
                    for metric, value in values.items():
                        records.append({'model': label, 'phase': phase, 'readout': kind, 'policy_scope': key,
                            'metric': metric, 'mean': value['mean'], 'ci_low': value['ci95'][0],
                            'ci_high': value['ci95'][1], 'contexts': value['n_contexts']})
    result = {'runs': runs, 'contexts': sum(r['audit']['contexts'] for r in runs.values()),
              'scores': sum(r['audit']['scores'] for r in runs.values()),
              'gpu_hours': sum(r['gpu_hours'] for r in runs.values())}
    (ROOT / 'results/e123/wave_summary.json').write_text(json.dumps(result, indent=2) + '\n')
    if records:
        with (ROOT / 'results/e123/policy_accuracy.csv').open('w') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(records)
    return result


def plot(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 4, figsize=(15.5, 8), sharey=True, layout='constrained')
    colors = ['#555555', '#2166ac', '#d6604d', '#4d9221', '#67a9cf', '#f4a582']
    for col, (family, label) in enumerate(FAMILIES):
        key = f'{family}_confirmation'
        for row, ns in enumerate(['shared', 'far']):
            ax = axes[row, col]
            ax.set_title(label + (' — shared words' if ns == 'shared' else ' — separate words'), fontsize=10)
            if key not in out['runs']:
                ax.text(.5, .5, 'Confirmation running', transform=ax.transAxes, ha='center')
                continue
            run = out['runs'][key]
            for i, (condition, _) in enumerate(CONDITIONS):
                v = run['analysis']['policy_accuracy'][f'{ns}_{condition}']['both']
                ax.errorbar(i-.09, 100*v['mean'], yerr=[[100*(v['mean']-v['ci95'][0])],
                    [100*(v['ci95'][1]-v['mean'])]], fmt='o', color=colors[i], capsize=2, ms=5,
                    label='Own-word candidates' if i == 0 else None)
                f = run['full_output']['policy_accuracy'][f'{ns}_{condition}']['both']
                ax.errorbar(i+.09, 100*f['mean'], yerr=[[100*(f['mean']-f['ci95'][0])],
                    [100*(f['ci95'][1]-f['mean'])]], fmt='x', color='black', capsize=2, ms=5,
                    label='Full-vocabulary argmax' if i == 0 else None)
            ax.set_xticks(range(6), [x[1] for x in CONDITIONS], fontsize=7, rotation=45, ha='right')
            ax.set_ylim(45, 102)
            ax.axhline(50, color='gray', lw=.6, ls=':')
            ax.legend(loc='lower right', fontsize=7)
            if col == 0:
                ax.set_ylabel('Mean accuracy across requested sources (%)')
    fig.suptitle('Real-text private rules: formation and reading policies, independent n=32 confirmation', fontsize=13)
    base = ROOT / 'results/figs/fig_natural_source_function_policies'
    fig.savefig(base.with_suffix('.png'), dpi=180)
    fig.savefig(base.with_suffix('.pdf'))
    plt.close(fig)

    fig, axes = plt.subplots(1, 4, figsize=(14, 4.4), layout='constrained', sharey=True)
    for ax, (family, label) in zip(axes, FAMILIES):
        ax.set_title(label, fontsize=11)
        key = f'{family}_confirmation'
        if key not in out['runs']:
            continue
        a = out['runs'][key]['analysis']['A_B_code_response']
        for ns, color, offset, marker in [('shared', '#2166ac', -.09, 'o'), ('far', '#b2182b', .09, '^')]:
            for i, (condition, _) in enumerate(CONDITIONS):
                v = a[f'{ns}_{condition}']['absolute']
                ax.errorbar(i+offset, v['mean'], yerr=[[v['mean']-v['ci95'][0]],
                    [v['ci95'][1]-v['mean']]], fmt=marker, color=color, capsize=2, ms=4,
                    label=ns if i == 0 else None)
        ax.set_xticks(range(6), [x[1] for x in CONDITIONS], rotation=45, ha='right', fontsize=7)
        ax.set_ylim(bottom=0)
        ax.legend(fontsize=8)
    axes[0].set_ylabel('A response magnitude to B convention (nats)')
    fig.suptitle('Functional provenance under fixed A output words: preregistered response observer', fontsize=12)
    base = ROOT / 'results/figs/fig_natural_source_provenance'
    fig.savefig(base.with_suffix('.png'), dpi=180)
    fig.savefig(base.with_suffix('.pdf'))
    plt.close(fig)


if __name__ == '__main__':
    result = collect()
    plot(result)
    print(json.dumps({k: v for k, v in result.items() if k != 'runs'}))
