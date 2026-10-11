"""Collect completed frozen runs; never select contexts, channels, or coefficients."""
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def collect():
    runs = {}
    for experiment in ['e115', 'e116', 'e117']:
        for dest in sorted((ROOT / 'results' / experiment).glob('*')):
            if not (dest / 'analysis.json').exists() or not (dest / 'run.json').exists():
                continue
            run = json.loads((dest / 'run.json').read_text())
            analysis = json.loads((dest / 'analysis.json').read_text())
            rows = [json.loads(line) for line in (dest / 'behavior.jsonl').read_text().splitlines()]
            n = run['args']['n']
            nc = {'e115': 43, 'e116': 33, 'e117': 52}[experiment]
            assert len(rows) == n == analysis['n_contexts']
            keys = set(rows[0]['conditions'])
            assert len(keys) == nc
            assert all(set(r['conditions']) == keys for r in rows)
            assert all(len(v['z']) == 8 for r in rows for v in r['conditions'].values())
            assert run['numeric_max_error'] <= .001
            assert run['edge_self_max_error'] <= .001
            assert run['pristine_source_cache_exact']
            record = {
                'n_contexts': n, 'conditions': nc, 'scores': n * nc * 8,
                'gpu_hours': run['gpu_hours'], 'model_revision': run['model_revision'],
                'script_sha256': run['script_sha256'], 'numeric_max_error': run['numeric_max_error'],
                'self_max_error': run['edge_self_max_error'],
                'single_A_by_polarity': analysis['single_source_by_polarity'],
                'contrasts': analysis['contrasts'], 'relation': analysis['relation'],
                'reconstruction': analysis['reconstruction'],
            }
            if experiment == 'e117':
                record.update(single_B_by_polarity=analysis['single_B_by_polarity'],
                              feature_contrasts=analysis['feature_contrasts'],
                              feature_responses=analysis['feature_responses'])
                profile = dest / 'complete_feature_profile.json'
                if profile.exists():
                    record['complete_feature_profile'] = json.loads(profile.read_text())
            # Keep all condition accuracies, including direct and instruction controls.
            record['accuracy'] = {k: v['accuracy'] for k, v in analysis['metrics'].items()}
            runs[str(dest.relative_to(ROOT))] = record
            audit = {k: record[k] for k in ['n_contexts', 'conditions', 'scores', 'script_sha256',
                                         'numeric_max_error', 'self_max_error']}
            audit['condition_set_complete'] = True
            audit['queries_per_condition'] = 8
            audit['pristine_source_cache_exact'] = True
            audit['review_type'] = 'author completion check; independent review is separate'
            (dest / 'completeness_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    out = {'runs': runs, 'total_scores': sum(r['scores'] for r in runs.values()),
           'total_gpu_hours': sum(r['gpu_hours'] for r in runs.values())}
    (ROOT / 'results/e117/wave_summary.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


def plot(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    runs = out['runs']
    families = [('qwen3', 'Qwen3-8B'), ('mistral', 'Mistral-7B-v0.3'), ('llama', 'Llama-3.1-8B')]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout='constrained')
    conditions = ['single_A', 'origin_f0r0', 'origin_gate_shared', 'direct_A']
    for i, (family, label) in enumerate(families):
        key = f'results/e117/{family}_confirmation'
        if key not in runs:
            continue
        r = runs[key]
        means = [r['accuracy'][c]['mean'] for c in conditions]
        axes[0].plot(range(4), means, 'o-', label=label)
        for ax, pairing, title in [
            (axes[1], 'relation_label_cross_native_minus_relation_label_within_native', 'A-label cache interchange'),
            (axes[2], 'relation_answer_cross_kv_native_minus_relation_answer_within_kv_native', 'Historical B-answer KV at formation')]:
            for j, feature in enumerate(['food', 'service']):
                x = i + (j - .5) * .25
                v = r['feature_contrasts'][pairing][feature]
                ax.errorbar(x, v['mean'], yerr=np.array([[v['mean'] - v['ci95'][0]], [v['ci95'][1] - v['mean']]]),
                            fmt='o', color=['#2166ac', '#b2182b'][j], capsize=3,
                            label=feature if i == 0 else None)
            ax.set_title(title)
    axes[0].set_xticks(range(4), ['Single A', 'Native', 'A only', 'Direct rule'])
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel('Candidate-label accuracy')
    axes[0].set_title('Functional controls on novel inputs')
    axes[0].legend(fontsize=8)
    for ax in axes[1:]:
        ax.axhline(0, color='gray', lw=.8)
        ax.set_xticks(range(3), ['Qwen', 'Mistral', 'Llama'])
        ax.set_ylabel('Cross minus within: feature contrast (nats)')
        ax.legend(fontsize=8)
    fig.suptitle('Criterion-sensitive evidence: independent new-material confirmation', fontsize=12)
    dest = ROOT / 'results/figs/fig_criterion_feature_formation'
    fig.savefig(dest.with_suffix('.png'), dpi=180)
    fig.savefig(dest.with_suffix('.pdf'))
    plt.close(fig)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--plot', action='store_true')
    args = ap.parse_args()
    result = collect()
    if args.plot:
        plot(result)
    print(json.dumps({k: v for k, v in result.items() if k != 'runs'}))
