"""Plot independent E85 cue responses and fixed discovery forecasts."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('confirmation')
    ap.add_argument('forecast')
    ap.add_argument('output')
    a = ap.parse_args()
    analysis = json.loads((Path(a.confirmation)/'analysis.json').read_text())
    forecast = json.loads(Path(a.forecast).read_text())
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0), sharey=True, constrained_layout=True)
    modes = ['full_base', 'name_K', 'label_KV', 'joint']
    for layout, ax in enumerate(axes):
        for cue, color, offset, label in [('field','#2864a4',-.17,'Source field'),
                                         ('code','#d47722',.17,'Code cue')]:
            rows = [analysis['conditions'][f'D{layout}.{mode}'][cue] for mode in modes]
            means = np.array([r['mean'] for r in rows])
            cis = np.array([r['ci95'] for r in rows])
            x = np.arange(4)+offset
            ax.bar(x, means, width=.32, color=color, alpha=.85, label=label)
            ax.errorbar(x, means, yerr=np.stack((means-cis[:,0],cis[:,1]-means)),
                        fmt='none', ecolor=color, capsize=3, linewidth=1.2)
            pred = forecast['predictions'][f'D{layout}.{cue}']['product']['mean']
            ax.plot(3+offset, pred, marker='D', markersize=6,
                    markerfacecolor='white', markeredgecolor='black', linestyle='none',
                    label='Frozen product forecast' if cue=='field' else None)
        ax.axhline(0, color='.35', linewidth=.8)
        ax.set_xticks(np.arange(4),['Native','Name K','Label K/V','Joint'])
        ax.set_title('Tag layout' if layout==0 else 'Answer-prefix layout')
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15)
        ax.set_axisbelow(True)
    axes[0].set_ylabel('Cue contribution to label logit difference (nats)')
    axes[0].legend(frameon=False,fontsize=8,loc='upper left')
    fig.suptitle('Identity-key and label-mapping interventions compose differently for the two cues',fontsize=11)
    out = Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    for ext in ['png','pdf']:
        fig.savefig(out.with_suffix('.'+ext),dpi=180)


if __name__ == '__main__':
    main()
