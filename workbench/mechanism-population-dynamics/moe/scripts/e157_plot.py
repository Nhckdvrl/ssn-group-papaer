"""Plot completed E157 task-subbank results alongside sealed E156 references."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

BASE=Path(__file__).resolve().parents[1]/'results'
NEW=BASE/'e157'; OLD=BASE/'e156'; FIGURES=NEW/'figures'
DONORS=('A','B'); SHARED=('P','A','B'); SUBJECTS=('high_school_biology','high_school_mathematics')


def save(fig, stem, directory):
    directory.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'): fig.savefig(directory/f'{stem}.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)


def grid_figure(summary,directory):
    views=summary['scopes']['all_questions']['views']
    specs=(('minus_PP_full','true_answer_token_NLL','Full NLL − PP (nat/token)',1),
           ('minus_PP_full','raw_accuracy','Full accuracy − PP (pp)',100),
           ('minus_whole_bank_full','true_answer_token_NLL','Partial − whole-bank NLL',1))
    labels=[(g,r,s) for g in ('Bio','Math') for r in DONORS for s in SHARED]
    fig,axs=plt.subplots(1,3,figsize=(11.6,9.2))
    fig.subplots_adjust(left=.20,right=.97,top=.88,bottom=.15,wspace=.36)
    for column,(ax,(reference,metric,title,scale)) in enumerate(zip(axs,specs)):
        grid=np.array([[views[g]['cells'][r+s][reference][metric]['per_subject'][subject]['point']*scale for subject in SUBJECTS] for g,r,s in labels])
        extent=max(float(np.max(np.abs(grid))),1e-12)
        im=ax.imshow(grid,cmap='coolwarm',norm=TwoSlopeNorm(vmin=-extent,vcenter=0,vmax=extent),aspect='auto')
        for i in range(len(labels)):
            for j in range(2): ax.text(j,i,f'{grid[i,j]:+.2f}' if scale==100 else f'{grid[i,j]:+.3f}',ha='center',va='center',fontsize=8)
        ax.set_xticks([0,1],['Biology','Math']);ax.set_yticks(range(len(labels)),[f'{g} | R{r}, S{s}' for g,r,s in labels] if column==0 else ['']*len(labels)); ax.set_title(title,fontsize=10)
        ax.axhline(5.5,color='black',lw=.8);fig.colorbar(im,ax=ax,fraction=.05,pad=.03)
    fig.suptitle('E157: fixed partial grafts evaluated on both subjects',fontsize=14)
    fig.text(.20,.095,'Each row is one fixed graft: group-selected donor R, S source, and the remaining P receiver.\nBoth subject columns score that same model; all 12 source combinations are shown. PP and whole-bank references are E156 full models.',ha='left',va='top',fontsize=9,linespacing=1.5)
    save(fig,'e157_fixed_grafts_by_subject',directory)


def tradeoff_figure(summary,old,directory):
    cells=summary['scopes']['all_questions']['views']['on_domain']['cells']
    refs=old['scopes']['all_questions']; oldcross=refs['cross']
    pp_mask=oldcross['PP']['receiverP32']['true_answer_token_NLL']['point']
    colors={'A':'#2563a8','B':'#b15424'}; markers={'P':'o','A':'s','B':'^'}
    fig,ax=plt.subplots(figsize=(9.5,8.3));fig.subplots_adjust(left=.13,right=.96,top=.87,bottom=.31)
    for donor in DONORS:
        for shared in SHARED:
            key=donor+shared; cell=cells[key]
            xrec=cell['minus_PP_full']['true_answer_token_NLL']; x=xrec['point']; lo,hi=xrec['question_ci95']
            y=cell['inherited_E156_receiverP32']['true_answer_token_NLL']['point']-pp_mask
            before=refs['relative_to_PP'][key]['full']['true_answer_token_NLL']['point']
            # The shared y is the inherited E156 masked readout, an operator identity, not a new E157 measurement.
            ax.annotate('',xy=(x,y),xytext=(before,y),arrowprops={'arrowstyle':'->','color':colors[donor],'lw':1.3,'alpha':.75})
            ax.scatter([before],[y],marker=markers[shared],facecolors='none',edgecolors=colors[donor],s=72,zorder=3)
            ax.errorbar(x,y,xerr=np.array([[max(0.,x-lo)],[max(0.,hi-x)]]),fmt=markers[shared],color=colors[donor],capsize=3,markersize=7,zorder=4)
            ax.annotate('R'+donor+'/S'+shared,(x,y),xytext=(5,5),textcoords='offset points',fontsize=8)
    pp_full=oldcross['PP']['full']['true_answer_token_NLL']['point']
    for label,reference in refs['native'].items():
        x=reference['full']['true_answer_token_NLL']['point']-pp_full
        y=reference['receiverP32']['true_answer_token_NLL']['point']-pp_mask
        ax.scatter(x,y,color='0.45',marker='D',s=30,zorder=3)
        ax.annotate('Native '+label,(x,y),xytext=(5,4),textcoords='offset points',fontsize=8,color='0.35')
    ax.axhline(0,color='0.7',lw=.8);ax.axvline(0,color='0.7',lw=.8)
    ax.set_xlabel('Full answer-token NLL − PP full (nat/token)')
    ax.set_ylabel('Inherited masked answer-token NLL − PP masked (nat/token)')
    ax.set_title('On-domain paired transfer: whole bank to partial graft')
    ax.grid(alpha=.15)
    fig.text(.13,.205,'Open: E156 whole bank; filled: E157 partial graft; arrows connect matching R/S sources.\nHorizontal bars: paired 95% question CI for partial full − PP. Gray native references use their own D/G.',fontsize=9,va='top',linespacing=1.5)
    fig.text(.13,.095,'On-domain combines two fixed grafts by known subject (Bio/Math). Masked coordinates are inherited\nfrom E156; unchanged y is an operator identity, not a new finding. Off-domain masked values were not measured.',fontsize=9,va='top',linespacing=1.5)
    save(fig,'e157_on_domain_transfer',directory)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary',type=Path,default=NEW/'summary.json');parser.add_argument('--e156-summary',type=Path,default=OLD/'summary.json');parser.add_argument('--output',type=Path,default=FIGURES)
    args=parser.parse_args(); current=json.loads(args.summary.read_text());previous=json.loads(args.e156_summary.read_text())
    if current.get('experiment')!='E157' or current.get('status')!='complete' or previous.get('experiment')!='E156' or previous.get('status')!='complete': raise ValueError('Complete E157 and E156 summaries required')
    if current.get('previous_raw_sha256')!=previous.get('raw_sha256'): raise ValueError('E156 reference raw hashes differ')
    grid_figure(current,args.output);tradeoff_figure(current,previous,args.output)


if __name__=='__main__': main()
