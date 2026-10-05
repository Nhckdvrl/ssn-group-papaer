"""E33 paired role prediction across words, paraphrases, and action changes."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot(summary,cohort,out):
    data=json.loads(summary.read_text());cells=data['cells'];n=len(data['cohorts'][cohort])
    assert n>0
    fig,axes=plt.subplots(2,2,figsize=(10.5,6.4),sharex=True,sharey='row')
    orders=('negate_then_affirm','affirm_then_negate')
    labels=('Original words','Action paraphrase','Different action')
    for col,order in enumerate(orders):
        for row,measure in enumerate(('activity','J')):
            ax=axes[row,col]
            for mode,color,label in [('same_actor','#0072B2','Same actor'),('other_actor','#D55E00','Other actor')]:
                parent=f'{cohort}/{measure}/same_action_original_words/{order}/same_began/{mode}'
                para=f'{cohort}/D/paraphrase/{order}/same_began/{mode}/activity' if measure=='activity' else f'{cohort}/J/paraphrase/{order}/same_began/{mode}'
                changed=f'{cohort}/{measure}/fixed_different_action/{order}/same_began/{mode}'
                vals=[cells[k] for k in (parent,para,changed)];y=np.array([v['estimate'] for v in vals]);ci=np.array([v['ci95'] for v in vals])
                x=np.arange(3)+(0.035 if mode=='other_actor' else -0.035)
                ax.errorbar(x,y,yerr=np.stack((y-ci[:,0],ci[:,1]-y)),fmt='o-',capsize=3,color=color,label=label,linewidth=1.7)
            ax.axhline(0,color='#888888',linewidth=.8,linestyle='--')
            ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
            ax.set_xticks(range(3),labels);ax.set_xlim(-.25,2.25)
            if col==0:ax.set_ylabel('Role effect on patient prediction, D (bits)' if row==0 else 'Activity minus neutral role effect, J (bits)')
            if row==0:ax.set_title('Fact: not X but only Y' if col==0 else 'Fact: only Y but not X')
    axes[0,0].legend(frameon=False,loc='best')
    fig.suptitle('Which action identity carries prior participant evidence?',fontsize=14)
    fig.text(.5,.016,f'Qwen3-8B frozen text prediction · {n} verb families · independently defined {cohort} cohort\nPaired family bootstrap 95% CIs; action-category matching does not imply strict synonym identity.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.075,1,.95))
    for suffix in ('.png','.pdf'):fig.savefig(out.with_suffix(suffix),dpi=200,bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--summary',type=Path,required=True);p.add_argument('--cohort',default='basic_action_clear');p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();plot(a.summary,a.cohort,a.out)
