"""Key E158 whole-path readouts from audited summary and ceiling diagnostic."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/'results'/'e158'/'whole_path'


def main():
    s=json.loads((ROOT/'summary.json').read_text());d=json.loads((ROOT/'readout_diagnostic.json').read_text())
    if s['status']!='complete' or d['status']!='POST_HOC_complete' or s['raw_sha256']!=d['raw_sha256']:raise ValueError('Completed matching summary and diagnostic required')
    if tuple(s['models'])!=('P','A','B') or tuple(s['scenarios'])!=('entity','attribute','paraphrase') or tuple(s['paths'])!=('R','S','RS','A'):raise ValueError('Incorrect source axes')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,3,figsize=(14,8.5),sharey='row');colors=['#16708a','#cb6a36'];x=np.arange(4)
    for row,(key,ylabel) in enumerate((('source_hit1','Donor answer top-1 fraction'),('source_rank_specificity_gain','Donor rank specificity gain'))):
        p=np.asarray(s['all'][key]['point']);ci=np.asarray(s['all'][key]['ci95'])
        if p.shape!=(3,3,4) or ci.shape!=(3,3,4,2):raise ValueError('Summary axes differ')
        for model,ax in enumerate(axes[row]):
            for scenario,label in enumerate(('Entity change','Attribute change')):
                pos=x+(-.16 if scenario==0 else .16);v=p[model,scenario];lo=ci[model,scenario,:,0];hi=ci[model,scenario,:,1]
                ax.bar(pos,v,width=.30,color=colors[scenario],label=label,zorder=2)
                ax.vlines(pos,lo,hi,color='#222',lw=1,zorder=3);ax.hlines(lo,pos-.04,pos+.04,color='#222',lw=1,zorder=3);ax.hlines(hi,pos-.04,pos+.04,color='#222',lw=1,zorder=3)
            ax.set_xticks(x,['R','S','R+S','Attn']);ax.axhline(0,color='#555',lw=.8);ax.grid(axis='y',alpha=.17,zorder=0)
            if row==0:
                reference=sum(s['baseline']['canonical_top1_by_model_relation'][model])/48
                ax.axhline(reference,color='#555',ls='--',lw=1.1,label='Native donor-answer reference')
                ax.set_title(('P','A','B')[model],fontsize=12,fontweight='bold')
            if model==0:ax.set_ylabel(ylabel)
    axes[0,0].legend(frameon=False,fontsize=9,loc='upper left');axes[0,0].set_ylim(0,1.12)
    fig.suptitle('Whole-path interchange: donor answers and rank specificity',fontsize=16,fontweight='bold')
    fig.subplots_adjust(left=.08,right=.98,top=.89,bottom=.24,hspace=.36,wspace=.16)
    vals=[v['mean_win_fraction'] for group in d['models'].values() for v in group]
    foot=('POST-HOC readout diagnostic: native unasked-answer within-relation win fractions '
          f'{min(vals):.3f}–{max(vals):.3f}; ranking may already be near ceiling. Original metrics unchanged.\n'
          'First canonical answer token; whole terminal position across 16 layers, earlier decoder prefix fixed; nonreplaced paths endogenous.\n'
          '24 countries × 2 relations; equal-relation macro, paired country 95% CI (not seed uncertainty). Dashed line is a reference, not an upper bound.')
    fig.text(.5,.055,foot,ha='center',fontsize=9,linespacing=1.45)
    out=ROOT/'figures'/'content_control';out.parent.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'):fig.savefig(out.with_suffix('.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig);print(out)


if __name__=='__main__':main()
