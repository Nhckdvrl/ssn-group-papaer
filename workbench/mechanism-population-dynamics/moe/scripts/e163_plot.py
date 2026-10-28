"""Compact E163 scientific figures from the sealed, audited summary only."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT=Path(__file__).resolve().parents[1]/'results/e163'
NAMES=('P','A','B','F')
TARGETS=('R','S','RS')
MODES=('zero','norm_mean','gram_mean','gram_random0','gram_random1')
LABELS=('Remove','Norm / mean','Gram / mean','Gram / random 0','Gram / random 1')
RULES=('raw','norm','gram')


def save(fig,name):
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    fig.savefig(out/(name+'.png'),dpi=190,bbox_inches='tight')
    fig.savefig(out/(name+'.pdf'),bbox_inches='tight')
    plt.close(fig)


def native_heatmap(summary,domain,field,name,title):
    values=[]
    for target in TARGETS:
        values.append(np.array([[summary['native'][domain][field][n]['damage'][target+'_'+m]['point'] for m in MODES] for n in NAMES]))
    extent=max(1e-6,max(abs(v).max() for v in values))
    fig,axes=plt.subplots(1,3,figsize=(13,3.9),constrained_layout=True)
    for ax,target,array in zip(axes,TARGETS,values):
        im=ax.imshow(array,cmap='RdBu_r',norm=TwoSlopeNorm(0,-extent,extent),aspect='auto')
        ax.set(yticks=range(4),yticklabels=NAMES,xticks=range(5),xticklabels=LABELS,title=target if target!='RS' else 'Entire MoE increment R+S')
        plt.setp(ax.get_xticklabels(),rotation=36,ha='right',fontsize=8)
        for i,j in np.ndindex(array.shape):
            value=array[i,j]
            ax.text(j,i,f'{value:.2f}',ha='center',va='center',fontsize=9,
                    color='white' if abs(value)>.58*extent else 'black')
    fig.colorbar(im,ax=axes,shrink=.7,label='Damage relative to native (nats)')
    fig.suptitle(title+'\nAll fixed models and directions; all 16 layers. Positive = worse.',fontsize=12)
    save(fig,name)


def task_accuracy(summary):
    fig,axes=plt.subplots(1,3,figsize=(13,3.8),constrained_layout=True)
    for ax,target in zip(axes,TARGETS):
        native=np.array([summary['native']['task']['raw_accuracy'][n]['absolute']['native']['point'] for n in NAMES])*100
        ax.plot(range(4),native,'k--',label='Native',alpha=.7)
        for mode,label in zip(MODES,LABELS):
            y=np.array([summary['native']['task']['raw_accuracy'][n]['absolute'][target+'_'+mode]['point'] for n in NAMES])*100
            ax.plot(range(4),y,marker='o',ms=3,label=label)
        ax.set(xticks=range(4),xticklabels=NAMES,title=target if target!='RS' else 'R+S',ylabel='Raw accuracy (%)')
        ax.set_ylim(bottom=0)
        ax.grid(alpha=.2)
    axes[-1].legend(fontsize=7,loc='upper right',ncol=1)
    fig.suptitle('Fixed biology + mathematics, all 128 questions\nAccuracy is shown separately from likelihood damage.',fontsize=12)
    save(fig,'native_task_accuracy')


def cross(summary):
    x=summary['cross']['true_answer_token_NLL']
    grids=[]
    for rule in RULES:
        table=x['absolute'][rule]
        grids.append(np.array([[table[c+'_'+p]['point']-table[c+'_'+c]['point'] for p in NAMES[:3]] for c in NAMES[:3]]))
    extent=max(1e-6,max(abs(g).max() for g in grids))
    fig,axes=plt.subplots(1,4,figsize=(13,3.7),constrained_layout=True,gridspec_kw={'width_ratios':[1,1,1,1.2]})
    for ax,rule,grid in zip(axes,RULES,grids):
        im=ax.imshow(grid,cmap='RdBu_r',norm=TwoSlopeNorm(0,-extent,extent))
        ax.set(xticks=range(3),xticklabels=NAMES[:3],yticks=range(3),yticklabels=NAMES[:3],xlabel='Message producer',ylabel='R consumer',title=rule.capitalize())
        for i,j in np.ndindex(grid.shape):
            ax.text(j,i,f'{grid[i,j]:+.3f}',ha='center',va='center',fontsize=9,
                    color='white' if abs(grid[i,j])>.58*extent else 'black')
    ax=axes[3]
    for i,rule in enumerate(RULES):
        record=x['matching_cost'][rule];point=record['point'];low,high=record['ci95']
        ax.errorbar(point,i,xerr=[[point-low],[high-point]],fmt='o',capsize=4,label=rule)
    ax.axvline(0,color='grey',ls='--',lw=1)
    ax.set(yticks=range(3),yticklabels=('Raw','Norm corrected','Gram corrected'),xlabel='Foreign minus own (nats)',title='Six foreign / three own')
    ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
    fig.colorbar(im,ax=axes[:3],shrink=.55,label='Consumer-relative answer NLL cost')
    fig.suptitle('Same S_P function, same input; actual R-context messages\nNorm/Gram use the consumer clean scalar witnesses; all 128 questions, paired 95% CI.',fontsize=12)
    save(fig,'actual_message_reuse')


def main():
    summary=json.loads((ROOT/'summary.json').read_text());audit=json.loads((ROOT/'independent_audit.json').read_text())
    if summary['status']!='complete' or audit['status']!='passed':
        raise ValueError('Sealed complete and independently checked result required')
    native_heatmap(summary,'LM','nll','native_LM_geometry','Native language prediction: preserving message geometry')
    native_heatmap(summary,'task','true_answer_token_NLL','native_task_geometry','True-answer token NLL: preserving message geometry')
    task_accuracy(summary);cross(summary)
    print(json.dumps({'status':'complete','figures':4,'path':str(ROOT/'figures')}))


if __name__=='__main__':main()
