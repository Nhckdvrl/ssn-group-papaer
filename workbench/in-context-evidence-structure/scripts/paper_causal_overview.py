"""Static manuscript diagram of tested interfaces, not an exhaustive circuit."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
fig, ax = plt.subplots(figsize=(12.5, 5.1), layout='constrained')
ax.set_xlim(0, 12.5)
ax.set_ylim(0, 5)
ax.axis('off')


def box(x, y, w, h, text, color, fontsize=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.08',
                              ec=color, fc='white', lw=1.7))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fontsize)


def arrow(start, end, color='#333333', linestyle='-', bend=0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=16,
        lw=1.7, color=color, linestyle=linestyle, connectionstyle=f'arc3,rad={bend}'))


box(.25, 3.5, 2.15, .9, 'A demonstrations\nFixed raw rule', '#2166ac')
box(.25, 1.9, 2.15, .9, 'B demonstrations\nCriterion × convention', '#b2182b')
box(3.2, 2.9, 2.35, 1.35, 'Prefix formation\n\nHistorical answers\n→ later labels', '#555555')
box(6.45, 2.9, 2.2, 1.35, 'Contextualized\nsource evidence\n\nA positions ≠ A-only\nrelation dependence', '#2166ac', 10)
box(9.45, 2.9, 2.65, 1.35, 'Source-conditioned query\n\nRead all source positions\nor requested source only', '#4d9221', 10)
arrow((2.48, 3.95), (3.12, 3.95), '#2166ac')
arrow((2.48, 2.35), (3.35, 2.82), '#b2182b')
arrow((5.63, 3.57), (6.37, 3.57))
arrow((8.73, 3.57), (9.37, 3.57))
box(6.45, 1.25, 2.2, .8, 'B-position caches\nAlso contextualized', '#b2182b', 10)
arrow((5.63, 3.02), (6.37, 1.95), '#b2182b', bend=.05)
arrow((8.73, 1.65), (10.1, 2.82), '#b2182b', '--', .1)
ax.text(9.65, 1.45, 'Available under\nfull-source reading',
        color='#b2182b', ha='center', fontsize=10)

ax.text(4.38, 2.48, 'Output coding changes\nformation messages', ha='center', color='#555555', fontsize=10)
ax.text(7.56, 2.48, 'Functional provenance\nmeasured by B-rule changes', ha='center', color='#2166ac', fontsize=10)
ax.text(10.8, 2.48, 'Reading access differs from\nrelation isolation', ha='center', color='#4d9221', fontsize=10)
ax.text(6.25, 4.75, 'Shared outputs couple source-specific evidence before query retrieval',
        ha='center', fontsize=15, weight='bold')
ax.text(6.25, .68, 'Test chain: frozen formation prediction → native operation removal / restricted restoration\n'
        '→ fixed-output association counterfactuals → two-source functional policies',
        ha='center', fontsize=11)
ax.text(6.25, .08, 'Arrows denote tested information access and causal interfaces; this diagram does not assert unique neural modules.',
        ha='center', fontsize=9, color='#555555')
dest = ROOT / 'results/figs/fig_source_evidence_overview'
fig.savefig(dest.with_suffix('.png'), dpi=180)
fig.savefig(dest.with_suffix('.pdf'))
plt.close(fig)
