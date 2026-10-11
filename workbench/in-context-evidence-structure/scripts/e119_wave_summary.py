"""Collect every E119 run and plot the prospectively frozen functional observer.

This is a reporting script, not a new scientific readout or a fitted predictor.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def collect():
    runs = {}
    for block, conditions in [('native', 43), ('criterion', 33)]:
        for phase in ['discovery', 'confirmation']:
            dest = ROOT / 'results/e119' / f'{block}_{phase}'
            run = json.loads((dest / 'run.json').read_text())
            analysis = json.loads((dest / 'analysis.json').read_text())
            rows = [json.loads(line) for line in (dest / 'behavior.jsonl').read_text().splitlines()]
            keys = set(rows[0]['conditions'])
            assert len(rows) == run['args']['n'] == analysis['n_contexts']
            assert len(keys) == conditions and all(set(row['conditions']) == keys for row in rows)
            assert all(len(v['z']) == 8 for row in rows for v in row['conditions'].values())
            assert run['numeric_max_error'] <= .001 and run['edge_self_max_error'] == 0
            assert run['pristine_source_cache_exact'] and run['sender_layer0_KV_max_error'] == 0
            audit = {
                'n_contexts': len(rows), 'conditions': conditions, 'queries_per_condition': 8,
                'scores': len(rows) * conditions * 8, 'all_conditions_retained': True,
                'numeric_max_error': run['numeric_max_error'], 'self_max_error': run['edge_self_max_error'],
                'script_sha256': run['script_sha256'], 'model_revision': run['model_revision'],
                'review_type': 'author completion check; independent raw review separate',
            }
            (dest / 'completeness_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
            record = {'completion': audit, 'gpu_hours': run['gpu_hours'], 'analysis': analysis}
            if block == 'criterion':
                record['response_rotation'] = json.loads((dest / 'response_rotation.json').read_text())
            runs[dest.name] = record
    out = {
        'runs': runs, 'total_scores': sum(r['completion']['scores'] for r in runs.values()),
        'total_contexts': sum(r['completion']['n_contexts'] for r in runs.values()),
        'total_gpu_hours': sum(r['gpu_hours'] for r in runs.values()),
        'scope': 'four completed frozen runs; no context/channel selection; all discovery results retained',
    }
    (ROOT / 'results/e119/wave_summary.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


def plot(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    rotation = out['runs']['criterion_confirmation']['response_rotation']['modes']
    modes = ['native', 'gate', 'label', 'label_gate', 'edge', 'edge_gate', 'far_label']
    labels = ['Full native', 'Full A cache, A-only query', 'A-label interchange',
              'A-label interchange, A-only', 'Historical answer KV',
              'Historical answer KV, A-only', 'Separate-output label donor']
    fig = plt.figure(figsize=(13, 7), layout='constrained')
    grid = fig.add_gridspec(2, 4, height_ratios=[1, 1.25])
    selected = ['native', 'gate', 'label', 'label_gate']
    maxv = max(abs(np.asarray(rotation[k]['matrix_mean'])).max() for k in selected)
    for j, mode in enumerate(selected):
        ax = fig.add_subplot(grid[0, j])
        matrix = np.asarray(rotation[mode]['matrix_mean'])
        im = ax.imshow(matrix, cmap='RdBu_r', vmin=-maxv, vmax=maxv)
        for i in range(2):
            for k in range(2):
                ax.text(k, i, f'{matrix[i, k]:.3f}', ha='center', va='center',
                        color='white' if abs(matrix[i, k]) > .6 * maxv else 'black')
        ax.set_xticks([0, 1], ['Food', 'Service'], fontsize=9)
        ax.set_xlabel('Input-feature response', fontsize=8)
        ax.set_yticks([0, 1], ['B food rule', 'B service rule'], fontsize=8)
        ax.set_title(labels[modes.index(mode)].replace(', ', '\n'), fontsize=10)
    fig.colorbar(im, ax=fig.axes, shrink=.7, label='B convention reversal / 2 (nats)')
    for span, metric, xlabel in [
        (slice(0, 2), 'determinant_nats_squared', 'Mean signed determinant (nats²)'),
        (slice(2, 4), 'normalized_rotation', 'Mean signed normalized determinant'),
    ]:
        ax = fig.add_subplot(grid[1, span])
        for i, mode in enumerate(modes):
            v = rotation[mode][metric]
            ax.errorbar(v['mean'], i, xerr=[[v['mean'] - v['ci95'][0]], [v['ci95'][1] - v['mean']]],
                        fmt='o', color='#2166ac', capsize=3)
        ax.axvline(0, color='gray', lw=.8)
        ax.set_yticks(range(len(modes)), labels, fontsize=8)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel)
        ax.grid(axis='x', alpha=.15)
    fig.suptitle('Qwen3-14B: functional criterion responses, 32 new-material contexts\n'
                 'Matrices: mean responses. Determinants: computed within each context before averaging.', fontsize=12)
    base = ROOT / 'results/figs/fig_stronger_model_functional_responses'
    fig.savefig(base.with_suffix('.png'), dpi=180)
    fig.savefig(base.with_suffix('.pdf'))
    plt.close(fig)


if __name__ == '__main__':
    summary = collect()
    plot(summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'runs'}))
