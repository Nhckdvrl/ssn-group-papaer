"""Static manuscript diagram of tested interfaces, not an exhaustive circuit."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
fig, ax = plt.subplots(figsize=(6.3, 2.45), layout='constrained')
ax.set_xlim(0, 12.5)
ax.set_ylim(0, 5)
ax.axis('off')


def box(x, y, w, h, text, color, fontsize=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.08',
                              ec=color, fc='white', lw=1.7))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fontsize)


def arrow(start, end, color='#333333', linestyle='-', bend=0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=10,
        lw=1.7, color=color, linestyle=linestyle, connectionstyle=f'arc3,rad={bend}'))


box(.25, 3.5, 2.15, .9, 'A demonstrations\nFixed raw rule', '#2166ac')
box(.25, 1.9, 2.15, .9, 'B demonstrations\nCriterion ×\nconvention', '#b2182b')
box(3.2, 2.9, 2.35, 1.35, 'Prefix formation\n\nHistorical answers\n→ later labels', '#555555')
box(6.45, 2.9, 2.2, 1.35, 'A-position evidence\n\nCan depend on\nB’s relations', '#2166ac', 8)
box(9.45, 2.9, 2.65, 1.35, 'Source-conditioned\nquery\n\nAll-source / A-only', '#4d9221', 8)
arrow((2.48, 3.95), (3.12, 3.95), '#2166ac')
arrow((2.48, 2.35), (3.35, 2.82), '#b2182b')
arrow((5.63, 3.57), (6.37, 3.57))
arrow((8.73, 3.57), (9.37, 3.57))
box(6.45, 1.25, 2.2, .8, 'B-position caches\nContextualized', '#b2182b', 8)
arrow((5.63, 3.02), (6.37, 1.95), '#b2182b', bend=.05)
arrow((8.73, 1.65), (10.1, 2.82), '#b2182b', '--', .1)
ax.text(6.25, 4.75, 'Shared outputs shape source evidence during formation',
        ha='center', fontsize=10, weight='bold')
ax.text(6.25, .5, 'Formation: which relations enter the evidence?     Reading: which positions does the query access?',
        ha='center', fontsize=7.5)
dest = ROOT / 'results/figs/fig_source_evidence_overview'
fig.savefig(dest.with_suffix('.png'), dpi=180)
fig.savefig(dest.with_suffix('.pdf'))
plt.close(fig)
