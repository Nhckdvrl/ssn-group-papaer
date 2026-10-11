"""Report all frozen operation and natural-text runs; no new scientific readouts."""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [('qwen3', 'Qwen3-8B'), ('mistral', 'Mistral-7B'),
            ('llama', 'Llama-3.1-8B'), ('qwen14', 'Qwen3-14B')]


def collect():
    runs = {}
    for experiment, nc in [('e120', 64), ('e121', 43)]:
        for dest in sorted((ROOT / 'results' / experiment).glob('*')):
            if not (dest / 'run.json').exists():
                continue
            run = json.loads((dest / 'run.json').read_text())
            analysis = json.loads((dest / 'analysis.json').read_text())
            rows = [json.loads(line) for line in (dest / 'behavior.jsonl').read_text().splitlines()]
            keys = set(rows[0]['conditions'])
            assert len(rows) == analysis['n_contexts'] == run['args']['n']
            assert len(keys) == nc and all(set(r['conditions']) == keys for r in rows)
            assert all(len(v['z']) == 8 for r in rows for v in r['conditions'].values())
            assert run['numeric_max_error'] <= .001
            if experiment == 'e120':
                assert run['graph_zero_max_error'] <= .001 and run['native_mask_cache_max_error'] <= .001
                assert all({int(k) for k in v} == set(range(run['num_layers'])) and set(v.values()) == {len(rows)}
                           for v in run['all_layer_consumption'].values())
            else:
                assert run['edge_self_max_error'] == 0 and run['sender_layer0_KV_max_error'] == 0
                assert run['pristine_source_cache_exact']
            audit = {'n_contexts': len(rows), 'conditions': nc, 'queries': 8, 'scores': len(rows) * nc * 8,
                     'script_sha256': run['script_sha256'], 'numeric_max_error': run['numeric_max_error'],
                     'all_conditions_retained': True, 'review_type': 'author completion; independent review separate'}
            (dest / 'completeness_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
            runs[str(dest.relative_to(ROOT))] = {'completion': audit, 'gpu_hours': run['gpu_hours'], 'analysis': analysis}
    out = {'runs': runs, 'total_contexts': sum(r['completion']['n_contexts'] for r in runs.values()),
           'total_scores': sum(r['completion']['scores'] for r in runs.values()),
           'total_gpu_hours': sum(r['gpu_hours'] for r in runs.values())}
    (ROOT / 'results/e120/e120_e121_summary.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


def errorbar(ax, x, value, color, marker='o', label=None):
    ax.errorbar(x, value['mean'], yerr=[[value['mean'] - value['ci95'][0]], [value['ci95'][1] - value['mean']]],
                fmt=marker, color=color, capsize=3, label=label)


def plot(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), layout='constrained')
    for i, (family, _) in enumerate(FAMILIES):
        key = f'results/e120/{family}_confirmation'
        if key not in out['runs']:
            continue
        a = out['runs'][key]['analysis']
        for j, (scope, color) in enumerate([('native', '#2166ac'), ('gate', '#b2182b')]):
            offset = (j - .5) * .23
            for ax, contrast in [(axes[0], 'cross_answer_removal'), (axes[1], 'answer_path_restoration')]:
                errorbar(ax, i + offset, a['contrasts'][f'shared_{scope}_{contrast}']['rule_signed'], color,
                         label=('Full-source query' if scope == 'native' else 'A-only query') if i == 0 else None)
        for j, (condition, color, marker) in enumerate([('single_A', '#2166ac', 'o'),
                                                       ('single_A_within_answer_off', '#b2182b', 's')]):
            errorbar(axes[2], i + (j - .5) * .23, a['accuracy'][condition]['candidate'], color, marker,
                     ('Single A' if j == 0 else 'Single A, own-answer history off') if i == 0 else None)
    for ax in axes:
        ax.set_xticks(range(4), ['Qwen 8B', 'Mistral', 'Llama', 'Qwen 14B'])
        ax.legend(fontsize=8)
    for ax in axes[:2]:
        ax.axhline(0, color='gray', lw=.8)
        ax.set_ylabel('Paired signed B-rule response difference (nats)')
    axes[0].set_title('Remove historical B-answer → A-label access')
    axes[1].set_title('Restore that path in an otherwise B→A-blocked graph')
    axes[2].set_title('Private-function controls')
    axes[2].set_ylabel('Candidate-label accuracy')
    axes[2].set_ylim(0, 1.05)
    fig.suptitle('Native formation operations: 32 new-material contexts, frozen all-layer masks', fontsize=12)
    base = ROOT / 'results/figs/fig_native_operation_necessity'
    fig.savefig(base.with_suffix('.png'), dpi=180)
    fig.savefig(base.with_suffix('.pdf'))
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3), layout='constrained')
    for i, (family, _) in enumerate(FAMILIES):
        key = f'results/e121/{family}_confirmation'
        if key not in out['runs']:
            continue
        a = out['runs'][key]['analysis']
        for j, p in enumerate(['False', 'True']):
            errorbar(axes[0], i + (j - .5) * .22, a['single_source_by_polarity'][p], ['#2166ac', '#b2182b'][j],
                     label=['Positive convention', 'Inverted convention'][j] if i == 0 else None)
        errorbar(axes[1], i, a['contrasts']['A_formation_B_shared']['absolute_rule_effect'], '#2166ac')
        for j, channel in enumerate(['k', 'kv', 'v']):
            v = a['reconstruction'][f'label_interface_B0_{channel}']['rule_double_contrast']
            axes[2].plot(i + (j - 1) * .2, v['rmse'], ['o', 's', '^'][j], color=['#2166ac', '#b2182b', '#4d9221'][j],
                         label=channel.upper() if i == 0 else None)
        axes[2].plot(i, v['zero_rmse'], 'x', color='black', label='Zero prediction' if i == 0 else None)
    for ax in axes:
        ax.set_xticks(range(4), ['Qwen 8B', 'Mistral', 'Llama', 'Qwen 14B'])
    axes[0].set_title('Private-rule ability on real held-out queries')
    axes[0].set_ylabel('Candidate-label accuracy')
    axes[0].set_ylim(0, 1.05)
    axes[0].legend(fontsize=8)
    axes[1].set_title('Native source-evidence formation')
    axes[1].set_ylabel('Paired change in B-rule magnitude (nats)')
    axes[1].axhline(0, color='gray', lw=.8)
    axes[2].set_title('Frozen label-interface namespace prediction')
    axes[2].set_ylabel('Rule double-contrast RMSE (nats)')
    axes[2].legend(fontsize=8)
    fig.suptitle('Real SST5 text: independent demo partition and official test queries, n=32', fontsize=12)
    base = ROOT / 'results/figs/fig_natural_text_formation'
    fig.savefig(base.with_suffix('.png'), dpi=180)
    fig.savefig(base.with_suffix('.pdf'))
    plt.close(fig)


if __name__ == '__main__':
    out = collect()
    if any('confirmation' in k for k in out['runs']):
        plot(out)
    print(json.dumps({k: v for k, v in out.items() if k != 'runs'}))
