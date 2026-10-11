"""Show rule asymmetry and the explicit-parameter positive control."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    r=json.loads(Path('results/e77/qwen3_function/analysis.json').read_text())
    modes=['mixed','mixed_instruction','single','single_instruction','direct']
    labels=['Mixed','Mixed + source instruction','Single source','Single + source instruction','Explicit source rules']
    fig,axes=plt.subplots(2,2,figsize=(11.3,6.4),sharex=True)
    for row,(rule,color) in enumerate([('identity','#49728B'),('complement','#A87352')]):
        for col,group in enumerate(['interpolation','extrapolation']):
            ax=axes[row,col];vals=[r['conditions'][m+'.base'][group][rule+'_accuracy'] for m in modes]
            mean=np.array([v['mean'] for v in vals]);ci=np.array([v['ci95'] for v in vals]);ys=np.arange(5)
            ax.errorbar(mean,ys,xerr=[mean-ci[:,0],ci[:,1]-mean],fmt='o',color=color,ms=4,capsize=2)
            ax.set(yticks=ys,yticklabels=labels if col==0 else [],xlim=(-.03,1.03))
            ax.invert_yaxis();ax.axvline(.8,color='gray',ls='--',lw=.8,alpha=.6)
            ax.set_title(('Copy input' if rule=='identity' else '9 minus input')+' / '+group,fontsize=10)
            ax.grid(axis='x',alpha=.18);ax.spines[['top','right']].set_visible(False)
    for ax in axes[-1]:ax.set_xlabel('Candidate-number accuracy')
    fig.text(.03,.025,'E77 discovery only: 32 contexts, all queries kept; 95% context-bootstrap CIs. Each source has the same label histogram.\n'
             'Explicit rules supply parameters. Single-source copy also fails the preset gate; no unique composition-deficit claim.',fontsize=8)
    fig.tight_layout(rect=[0,.10,1,1]);out=Path('results/figs')
    fig.savefig(out/'e77_rule_inference_execution.png',dpi=180)
    fig.savefig(out/'e77_rule_inference_execution.pdf',metadata={'CreationDate':None,'ModDate':None})


if __name__=='__main__':main()
