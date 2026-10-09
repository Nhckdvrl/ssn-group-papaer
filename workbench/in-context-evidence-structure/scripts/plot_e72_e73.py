"""Show censoring and parsing limits without treating them as incapacity."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def points(ax, vals, y, color, label):
    m = np.array([v['mean'] for v in vals])
    ci = np.array([v['ci95'] for v in vals])
    ax.errorbar(m, y, xerr=[m-ci[:, 0], ci[:, 1]-m], fmt='o', ms=4,
                capsize=2, color=color, label=label)


def main():
    a = json.loads(Path('results/e73/qwen3_discovery/analysis.json').read_text())
    f = json.loads(Path('results/e73/qwen3_discovery/format_audit.json').read_text())
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.9))
    schemas = ['source_only', 'orthogonal_prefix', 'entity_binding', 'single_source']
    ys = np.arange(4)
    for delta, mode, color, label in [(-.16, 'chat', '#646C79', 'Default chat'),
                                     (0, 'chat_instruction', '#BB7662', '+ Source instruction'),
                                     (.16, 'thinking_instruction', '#367879', '+ Thinking')]:
        points(axes[0], [a['conditions'][s+'.'+mode+'.4096']['accuracy'] for s in schemas], ys+delta, color, label)
    axes[0].set(yticks=ys, yticklabels=['Source-conditioned', 'Orthogonal prefix', 'Literal binding', 'Single source'],
                xlabel='Accuracy at 4096 tokens (strict parser)', xlim=(-.04, 1.04))
    axes[0].invert_yaxis()
    axes[0].set_title('Completed replies still need task controls', fontsize=10)
    for delta, key, color, label in [(-.1, 'strict_accuracy', '#646C79', 'Registered strict parser'),
                                   (.1, 'accuracy', '#A09A4B', 'Decoration audit (POST-HOC)')]:
        points(axes[1], [f['conditions'][s+'.chat.4096'][key] for s in schemas], ys+delta, color, label)
    axes[1].set(yticks=ys, yticklabels=['Source-conditioned', 'Orthogonal prefix', 'Literal binding', 'Single source'],
                xlabel='Default chat accuracy at 4096 tokens', xlim=(-.04, 1.04))
    axes[1].invert_yaxis()
    axes[1].set_title('Markdown decoration caused false failures', fontsize=10)
    for ax in axes:
        ax.grid(axis='x', alpha=.2)
        ax.spines[['top', 'right']].set_visible(False)
        leg = ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(0, -.19), frameon=False)
        leg.set_in_layout(False)
    fig.text(.04, .02, 'E73 discovery only: 4 contexts, all cases included; 95% context-bootstrap CIs. No independent capability confirmation.\n'
             '48 actual short/long generation-prefix audits agree. Nonthinking replies may contain prose reasoning.', fontsize=8)
    fig.tight_layout(rect=[0, .30, 1, 1])
    out = Path('results/figs')
    fig.savefig(out/'e72_e73_interface_audit.png', dpi=180)
    fig.savefig(out/'e72_e73_interface_audit.pdf', metadata={'CreationDate': None, 'ModDate': None})


if __name__ == '__main__':
    main()
