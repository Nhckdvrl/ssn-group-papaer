"""Show discovery boundaries and independent confirmation; no selected layers."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def points(ax,values,ys,color,label):
    mean=np.array([v['mean'] for v in values]);lo=np.array([v['ci95'][0] for v in values]);hi=np.array([v['ci95'][1] for v in values])
    ax.errorbar(mean,ys,xerr=[mean-lo,hi-mean],fmt='o',ms=4,capsize=2,color=color,label=label)


def main():
    fig,axes=plt.subplots(1,3,figsize=(13.3,4.2),gridspec_kw={'width_ratios':[1,1,1.25]})
    src=[('qwen3_discovery','Qwen discovery'),('qwen3_confirmation','Qwen confirmation'),('mistral_discovery','Mistral discovery')]
    data=[json.load(open(Path('results/e67')/n/'analysis.json')) for n,_ in src];y=np.arange(3)
    points(axes[0],[a['conditions']['D0Q0']['accuracy'] for a in data],y-.08,'#355C7D','Code in metadata')
    points(axes[0],[a['conditions']['D1Q1']['accuracy'] for a in data],y+.08,'#C06C84','Code in answer prefix')
    axes[0].set(yticks=y,yticklabels=[l for _,l in src],xlabel='Final-label accuracy',xlim=(.4,.92));axes[0].invert_yaxis()
    axes[0].set_title('Same final label; encoding matters',fontsize=10);fig.legend(*axes[0].get_legend_handles_labels(),fontsize=8,loc='upper left',bbox_to_anchor=(.12,.20),frameon=False)
    a=json.load(open('results/e69/qwen3_confirmation/analysis.json'))
    keys=['D1Q1','isolated.prefix.key','blind.prefix.key'];labels=['Native prefix K','Isolated prefix K','Label-blind prefix K'];y=np.arange(3)
    points(axes[1],[a['conditions'][k]['paired_source_ranking'] for k in keys],y,'#417D7A','Source ranking')
    axes[1].set(yticks=y,yticklabels=labels,xlabel='Correct source ordering',xlim=(.6,1.02));axes[1].invert_yaxis()
    axes[1].set_title('History dependence ≠ label-rule content',fontsize=10)
    a=json.load(open('results/e70/qwen3_confirmation/analysis.json'))
    keys=['isolated','common','centered','shared_frame','blind','D1Q1'];labels=['Isolated','Own common shift','Centered changes','Frozen shared shift','Full label-blind K','Native'];y=np.arange(6)
    points(axes[2],[a['conditions'][k]['accuracy'] for k in keys],y-.08,'#355C7D','Final-label accuracy')
    points(axes[2],[a['conditions'][k]['paired_source_ranking'] for k in keys],y+.08,'#417D7A','Source ranking')
    axes[2].set(yticks=y,yticklabels=labels,xlabel='Accuracy / source ordering',xlim=(.45,1.02));axes[2].invert_yaxis()
    axes[2].set_title('Shared offset restores prediction partially',fontsize=10);fig.legend(*axes[2].get_legend_handles_labels(),fontsize=8,loc='upper left',bbox_to_anchor=(.73,.20),frameon=False)
    for ax in axes:ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.text(.06,.015,'95% context bootstrap CIs. E69/E70 keep native label evidence. E70 uses float32. Frozen shift is estimated without query/label access.',fontsize=8)
    fig.tight_layout(rect=[0,.25,1,1]);out=Path('results/figs');fig.savefig(out/'e67_e70_scaffold.png',dpi=180);fig.savefig(out/'e67_e70_scaffold.pdf')

if __name__=='__main__':main()
