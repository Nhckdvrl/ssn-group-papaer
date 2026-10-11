"""Show prespecified E86 rule/alias responses and frozen extrapolations."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('directory')
    ap.add_argument('output')
    a=ap.parse_args()
    data=json.loads((Path(a.directory)/'analysis.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.0),constrained_layout=True)
    keys=[f'{s}.D{d}.native' for d in (0,1) for s in ['balanced','segregated']]
    x=np.arange(4)
    for name,color,offset,label in [('rule','#2864a4',-.18,'Input-rule response'),
                                     ('alias','#d47722',.18,'Alias response')]:
        rows=[data['conditions'][k]['unseen'][name] for k in keys]
        means=np.array([r['mean'] for r in rows])
        cis=np.array([r['ci95'] for r in rows])
        axes[0].bar(x+offset,means,.34,color=color,alpha=.85,label=label)
        axes[0].errorbar(x+offset,means,yerr=np.stack((means-cis[:,0],cis[:,1]-means)),
                         fmt='none',ecolor=color,capsize=3)
    axes[0].set_xticks(x,['Tag\nbalanced','Tag\nsegregated','Prefix\nbalanced','Prefix\nsegregated'])
    axes[0].set_ylabel('Contribution to class logit difference (nats)')
    axes[0].legend(frameon=False,fontsize=8)
    axes[0].set_title('Same source, two interchangeable codes')
    rows=[data['frozen_comparison'][f'D{d}'] for d in (0,1)]
    means=np.array([r['actual_delta_gap']['mean'] for r in rows])
    cis=np.array([r['actual_delta_gap']['ci95'] for r in rows])
    axes[1].bar(np.arange(2),means,.45,color=['#7da4cf','#4275a9'],label='Measured effect')
    axes[1].errorbar(np.arange(2),means,yerr=np.stack((means-cis[:,0],cis[:,1]-means)),
                     fmt='none',ecolor='black',capsize=3)
    pred=np.array([r['frozen_cue_gap']['mean'] for r in rows])
    axes[1].plot(np.arange(2),pred,'D',markerfacecolor='white',markeredgecolor='#a65a14',
                  markersize=7,label='Frozen E85 cue forecast')
    axes[1].axhline(0,color='.35',linestyle='--',label='Scope forecast')
    axes[1].set_xticks(np.arange(2),['Tag','Prefix'])
    axes[1].set_ylabel('Increase in matched−crossed margin gap (nats)')
    axes[1].set_title('Segregated support minus balanced support')
    axes[1].legend(frameon=False,fontsize=8)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15)
        ax.set_axisbelow(True)
    fig.suptitle('Unseen inputs; 95% context-bootstrap intervals',fontsize=11)
    out=Path(a.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    for ext in ['png','pdf']:
        fig.savefig(out.with_suffix('.'+ext),dpi=180)


if __name__=='__main__':
    main()
