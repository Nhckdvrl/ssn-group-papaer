"""Author completeness and plotting of all preregistered E122 conditions."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [('qwen3', 'Qwen3-8B'), ('mistral', 'Mistral-7B'),
            ('llama', 'Llama-3.1-8B'), ('qwen14', 'Qwen3-14B')]
CONDITIONS = [('normal_native', 'Native'), ('answer_cross_off_native', 'Answer formation'),
              ('all_cross_off_native', 'All cross-source formation'),
              ('normal_gate', 'Query only'), ('answer_cross_off_gate', 'Answer + query'),
              ('all_cross_off_gate', 'All formation + query')]


def collect():
    runs = {}
    records = []
    for family, label in FAMILIES:
        for phase in ['discovery', 'confirmation']:
            dest = ROOT / 'results/e122' / f'{family}_{phase}'
            if not (dest / 'analysis.json').exists():
                continue
            run = json.loads((dest / 'run.json').read_text())
            analysis = json.loads((dest / 'analysis.json').read_text())
            raw = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
            assert len(raw) == analysis['n_contexts'] == run['args']['n']
            keys = set(raw[0]['conditions'])
            assert len(keys) == 61 and all(set(r['conditions']) == keys for r in raw)
            assert all(len(v['z']) == len(v['gold']) == len(v['argmax_correct']) == 8
                       for row in raw for v in row['conditions'].values())
            for key in ['numeric_max_error', 'native_mask_cache_max_error', 'graph_zero_max_error']:
                assert run[key] <= .001
            assert all({int(k) for k in v} == set(range(run['num_layers']))
                       and set(v.values()) == {len(raw)} for v in run['all_layer_consumption'].values())
            audit = {'contexts': len(raw), 'conditions': 61, 'queries': 8,
                     'scores': len(raw) * 61 * 8, 'all_conditions_retained': True,
                     'source_sha256': run['script_sha256'],
                     'raw_sha256': hashlib.sha256((dest / 'behavior.jsonl').read_bytes()).hexdigest(),
                     'author_completion_check': True, 'independent_review': 'separate session/report'}
            (dest / 'completeness_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
            runs[f'{family}_{phase}'] = {'audit': audit, 'gpu_hours': run['gpu_hours'], 'analysis': analysis}
            for key, values in analysis['policy_accuracy'].items():
                for metric, value in values.items():
                    records.append({'model': label, 'phase': phase, 'policy_scope': key, 'metric': metric,
                        'mean': value['mean'], 'ci_low': value['ci95'][0], 'ci_high': value['ci95'][1],
                        'contexts': value['n_contexts']})
    out = {'runs': runs, 'contexts': sum(v['audit']['contexts'] for v in runs.values()),
           'scores': sum(v['audit']['scores'] for v in runs.values()),
           'gpu_hours': sum(v['gpu_hours'] for v in runs.values())}
    (ROOT / 'results/e122/wave_summary.json').write_text(json.dumps(out, indent=2) + '\n')
    if records:
        with (ROOT / 'results/e122/policy_accuracy.csv').open('w') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(records)
    return out


def plot(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), layout='constrained', sharey=True)
    colors = ['#555555', '#2166ac', '#d6604d', '#4d9221', '#67a9cf', '#f4a582']
    labels = ['Native', 'Answer\nformation', 'All cross-source\nformation', 'Query\nonly',
              'Answer\n+ query', 'All formation\n+ query']
    for ax, (family, label) in zip(axes.flat, FAMILIES):
        key = f'{family}_confirmation'
        ax.set_title(label)
        if key not in out['runs']:
            ax.text(.5, .5, 'Confirmation running', transform=ax.transAxes, ha='center')
            continue
        a = out['runs'][key]['analysis']['policy_accuracy']
        for i, (condition, _) in enumerate(CONDITIONS):
            v = a[condition]['both']
            ax.bar(i, 100 * v['mean'], color=colors[i], width=.65)
            ax.errorbar(i, 100 * v['mean'], yerr=[[100 * (v['mean'] - v['ci95'][0])],
                [100 * (v['ci95'][1] - v['mean'])]], color='black', capsize=3)
            ax.text(i, 100 * v['mean'] + 4, f"{100 * v['mean']:.1f}", ha='center', fontsize=9)
            for j, (actor, marker) in enumerate([('A', 'o'), ('B', '^')]):
                ax.plot(i + (j - .5) * .12, 100 * a[condition][actor]['mean'], marker,
                        color='black', ms=3, alpha=.8)
        ax.set_xticks(range(6), labels, fontsize=8)
        ax.set_ylim(45, 100)
        ax.set_ylabel('Mean accuracy across the two requested sources (%)')
        ax.axhline(50, color='gray', ls=':', lw=.8)
    fig.suptitle('Formation versus query isolation: fixed policies, new-material confirmation n=32', fontsize=13)
    base = ROOT / 'results/figs/fig_source_function_formation'
    fig.savefig(base.with_suffix('.png'), dpi=180)
    fig.savefig(base.with_suffix('.pdf'))
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), layout='constrained')
    for i, (family, label) in enumerate(FAMILIES):
        key = f'{family}_confirmation'
        if key not in out['runs']:
            continue
        a = out['runs'][key]['analysis']
        for j, (metric, color, marker) in enumerate([('A', '#2166ac', 'o'), ('B', '#b2182b', '^')]):
            v = a['contrasts']['answer_cross_off_minus_normal_native'][metric]
            axes[0].errorbar(i + (j - .5) * .22, 100 * v['mean'],
                yerr=[[100 * (v['mean'] - v['ci95'][0])], [100 * (v['ci95'][1] - v['mean'])]],
                fmt=marker, color=color, capsize=3, label=metric if i == 0 else None)
        for j, (metric, color, marker) in enumerate([('agree', '#4d9221', 'o'), ('disagree', '#762a83', '^')]):
            v = a['contrasts']['answer_cross_off_minus_normal_native'][metric]
            axes[1].errorbar(i + (j - .5) * .22, 100 * v['mean'],
                yerr=[[100 * (v['mean'] - v['ci95'][0])], [100 * (v['ci95'][1] - v['mean'])]],
                fmt=marker, color=color, capsize=3, label=('Golds agree' if metric == 'agree' else 'Golds disagree') if i == 0 else None)
        for j, (contrast, color, marker, title) in enumerate([
                ('answer_minus_all_native', '#2166ac', 'o', 'Answer versus all formation'),
                ('query_isolation_normal', '#4d9221', '^', 'Query only versus native')]):
            v = a['contrasts'][contrast]['both']
            axes[2].errorbar(i + (j - .5) * .22, 100 * v['mean'],
                yerr=[[100 * (v['mean'] - v['ci95'][0])], [100 * (v['ci95'][1] - v['mean'])]],
                fmt=marker, color=color, capsize=3, label=title if i == 0 else None)
    for ax in axes:
        ax.set_xticks(range(4), ['Qwen 8B', 'Mistral', 'Llama', 'Qwen 14B'])
        ax.axhline(0, color='gray', lw=.8)
        ax.set_ylabel('Paired accuracy difference (percentage points)')
        ax.legend(fontsize=8)
    axes[0].set_title('Each requested source: answer formation − native')
    axes[1].set_title('Same or conflicting correct labels')
    axes[2].set_title('Policy alternatives')
    fig.suptitle('Functional consequences of preserving source-specific answer formation', fontsize=12)
    base = ROOT / 'results/figs/fig_source_function_tradeoffs'
    fig.savefig(base.with_suffix('.png'), dpi=180)
    fig.savefig(base.with_suffix('.pdf'))
    plt.close(fig)


if __name__ == '__main__':
    result = collect()
    if result['runs']:
        plot(result)
    print(json.dumps({k: v for k, v in result.items() if k != 'runs'}))
