"""Plot the completed E71 map, including both readouts and all interactions."""
import argparse
import json
from pathlib import Path

from data import sha


def plot(root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    path = root / 'correct-prefix-binding-map-v1.json'
    complete = json.loads((root / 'complete-map-v1.json').read_text())
    assert complete['all_models_complete'] and complete['map_sha256'] == sha(path)
    result = json.loads(path.read_text())
    panels = result['panels']
    models = ['Qwen3-8B', 'gemma-3-12b-it', 'Meta-Llama-3.1-8B-Instruct']
    titles = ['Qwen3-8B', 'Gemma3-12B', 'Llama3.1-8B']
    assert len(panels) == complete['panels'] == 126
    index = {(p['model'], p['construction'], p['condition'], p['metric'], p['operation']): p for p in panels}
    assert len(index) == len(panels)
    fig, axes = plt.subplots(4, 3, figsize=(13.5, 11), sharex=True)
    colors = {'gp': '#c35f34', 'cue': '#2378a1', 'gp-minus-cue': '#6b559a'}
    for row, (construction, metric) in enumerate([(c, m) for c in ['MVRR', 'NPZ'] for m in ['p_correct', 'correct']]):
        for col, model in enumerate(models):
            ax = axes[row, col]
            for y, condition in enumerate(['gp', 'cue', 'gp-minus-cue']):
                operation = 'interaction' if condition == 'gp-minus-cue' else 'CUT-minus-NATIVE'
                p = index[(model, construction, condition, metric, operation)]
                label = {'gp': 'GP', 'cue': 'Cue', 'gp-minus-cue': 'GP − Cue'}[condition]
                if p['value'] is None:
                    ax.text(0, y, label + ': unavailable', va='center', ha='center', fontsize=9)
                    continue
                value = 100 * p['value']
                low, high = [100 * v for v in p['CI95']]
                ax.plot([low, high], [y, y], color=colors[condition], linewidth=2)
                ax.scatter(value, y, color=colors[condition], s=32, zorder=3)
                ax.text(.98, y, f'{value:+.1f} [{low:+.1f}, {high:+.1f}]  n={p["clusters"]}',
                        transform=ax.get_yaxis_transform(), ha='right', va='bottom', fontsize=8)
            ax.set_yticks([0, 1, 2], ['GP', 'Cue', 'GP − Cue'])
            ax.set_ylim(2.65, -.55)
            ax.axvline(0, color='#888888', linewidth=.8, linestyle='--')
            ax.grid(axis='x', alpha=.15)
            ax.spines[['top', 'right']].set_visible(False)
            if row == 0:
                ax.set_title(titles[col])
            if col == 0:
                ax.set_ylabel(construction + '\n' + ('Correct-choice probability' if metric == 'p_correct' else 'Top-choice accuracy'))
            if row == 3:
                ax.set_xlabel('CUT − Native (percentage points)')
    # Use common limits from all displayed intervals, rather than crop large losses.
    intervals = [100 * v for p in panels if p['metric'] in ['p_correct', 'correct']
                 and p['operation'] in ['CUT-minus-NATIVE', 'interaction'] and p['CI95'] is not None for v in p['CI95']]
    extent = max([10] + [abs(v) for v in intervals]) + 8
    for ax in axes.flat:
        ax.set_xlim(-extent, extent)
    fig.suptitle('E71: effect of consuming a correct first clause on later relation choice', fontsize=14)
    fig.text(.5, .015, '95% paired lexical-cluster bootstrap CI; n = clusters. Correct assistant prefill; candidate choice, not spontaneous generation.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .035, 1, .96])
    out = root / 'figures-v1'
    out.mkdir(exist_ok=True)
    for suffix in ['png', 'pdf']:
        fig.savefig(out / ('correct-prefix-binding-effects.' + suffix), dpi=180, bbox_inches='tight')
    plt.close(fig)
    (out / 'manifest.json').write_text(json.dumps(dict(map_sha256=sha(path), code_sha256=sha(Path(__file__)),
        displayed='All 3 families, 2 constructions, both primary readouts, GP/Cue paired effects and interactions',
        artifacts={p.name: sha(p) for p in sorted(out.glob('correct-prefix-binding-effects.*'))}), indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    plot(parser.parse_args().root)
