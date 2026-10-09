"""Show relational-code confirmation and the failed frozen-frame generalization."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_ci(ax, values, ys, color, label):
    m=np.array([v['mean'] for v in values]);lo=np.array([v['ci95'][0] for v in values]);hi=np.array([v['ci95'][1] for v in values])
    ax.errorbar(m,ys,xerr=[m-lo,hi-m],fmt='o',ms=4,capsize=3,color=color,label=label)


def main():
    d=json.load(open('results/e71/qwen3_discovery/analysis.json'));c=json.load(open('results/e71/qwen3_confirmation/analysis.json'))
    fig,axes=plt.subplots(1,3,figsize=(12.8,4.5),gridspec_kw={'width_ratios':[1,1,1.1]})
    keys=['linked.D0','linked.D1','orthogonal.D0','orthogonal.D1'];labels=['Linked: metadata','Linked: answer prefix','Orthogonal: metadata','Orthogonal: answer prefix'];y=np.arange(4)
    plot_ci(axes[0],[c['conditions'][k]['accuracy'] for k in keys],y,'#355C7D','Confirmation')
    axes[0].set(yticks=y,yticklabels=labels,xlabel='Final-label accuracy',xlim=(.45,.75));axes[0].invert_yaxis();axes[0].set_title('Same grammar; source relation matters',fontsize=10)
    y=np.arange(2)
    plot_ci(axes[1],[d['transfer']['linked.'+k]['fraction_of_blind_effect'] for k in ['common','shared_frame']],y-.07,'#C06C84','Discovery')
    plot_ci(axes[1],[c['transfer']['linked.'+k]['fraction_of_blind_effect'] for k in ['common','shared_frame']],y+.07,'#355C7D','Confirmation')
    axes[1].set(yticks=y,yticklabels=['Own common shift','Frozen old shift'],xlabel='Fraction of margin effect',xlim=(0,1));axes[1].invert_yaxis();axes[1].axvline(.5,ls='--',alpha=.4,color='gray');axes[1].set_title('Frozen transfer misses preset threshold',fontsize=10)
    vals=[a['cooperation'][r]['paired_source_ranking'] for a in [d,c] for r in ['linked','orthogonal']]
    ys=np.arange(4)
    plot_ci(axes[2],vals,ys,'#417D7A','Interaction')
    axes[2].set(yticks=ys,yticklabels=['Linked discovery','Orthogonal discovery','Linked confirmation','Orthogonal confirmation'],xlabel='Source-ranking interaction',xlim=(-.18,.20));axes[2].invert_yaxis();axes[2].axvline(0,ls='--',alpha=.4,color='gray');axes[2].set_title('Source-ranking cooperation varies',fontsize=10)
    for ax in axes:ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.legend(*axes[1].get_legend_handles_labels(),fontsize=8,loc='lower center',bbox_to_anchor=(.48,.085),ncol=2,frameon=False)
    fig.text(.04,.02,'95% context bootstrap CIs. New names/codes/lexicon/labels in confirmation. Native label evidence retained in key interventions.',fontsize=8)
    fig.tight_layout(rect=[0,.18,1,1]);out=Path('results/figs');fig.savefig(out/'e71_relation_frame.png',dpi=180);fig.savefig(out/'e71_relation_frame.pdf')

if __name__=='__main__':main()
