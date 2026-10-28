"""Plot complete E160 producer/consumer results, retaining all nine combinations."""
import json
import hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/'results/e160/retry_1'
NAMES=('P','A','B')
FOOT=('The same suite of 16 shared experts S_P and P dense/gate parameters throughout. Each fixed-producer comparison replays the same S trajectory.\n'
      '128 fixed questions; paired question 95% CIs within two fixed subjects. Replay retains producer R history.')


def points(table):
    if isinstance(table,dict):return float(table['point'])
    return np.array([points(x) for x in table])


def intervals(table):
    if isinstance(table,dict):return np.array(table['question_ci95'])
    return np.array([intervals(x) for x in table])


def save(fig,name):
    output=ROOT/'figures';output.mkdir(exist_ok=True)
    for extension in ('png','pdf'):fig.savefig(output/(name+'.'+extension),dpi=180,bbox_inches='tight')
    plt.close(fig)


def heatmap(ax,table,title,percentage=False,signed=False):
    x=points(table)
    if x.shape!=(3,3):raise ValueError('Expected consumer × producer')
    if signed:
        bound=max(float(np.abs(x).max()),.01);im=ax.imshow(x,cmap='RdBu',vmin=-bound,vmax=bound)
    else:im=ax.imshow(x,cmap='viridis_r')
    for i in range(3):
        for j in range(3):
            text=f'{x[i,j]:.1%}' if percentage else f'{x[i,j]:+.3f}' if signed else f'{x[i,j]:.3f}'
            ax.text(j,i,text,ha='center',va='center',color='black',fontsize=10,
                    bbox={'facecolor':'white','alpha':.78,'edgecolor':'none','pad':2})
    ax.set_xticks(range(3),NAMES);ax.set_yticks(range(3),NAMES)
    ax.set_xlabel('S signal producer (R source)');ax.set_ylabel('Signal consumer (R source)');ax.set_title(title)
    return im


def main():
    path=ROOT/'summary.json';s=json.loads(path.read_text())
    if s['status']!='complete' or s['consumer_order']!=list(NAMES) or s['producer_order']!=list(NAMES):raise ValueError('Complete correct axes required')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    primary=lambda name:s['metrics'][name]['primary']
    for loss,filename,label in (('true_answer_token_NLL','signal_cross_token_NLL','True-answer token NLL'),('choice_CE','signal_cross_choice_CE','Choice CE')):
        p=primary(loss);fig,axes=plt.subplots(1,3,figsize=(13,5.5))
        heatmap(axes[0],p['conditions']['full'],'Complete prediction · '+label)
        heatmap(axes[1],p['contrasts']['shared_necessity'],'S removal cost',signed=True)
        heatmap(axes[2],p['contrasts']['direct_online_routed_necessity'],'Online R removal cost\nS trajectory retained',signed=True)
        fig.suptitle('Producing a signal and using it are separate interventions',fontweight='bold',fontsize=14)
        fig.subplots_adjust(top=.79,bottom=.25,wspace=.48);fig.text(.5,.04,FOOT,ha='center',fontsize=9);save(fig,filename)
    for metric,filename,label in (('raw_accuracy','signal_cross_raw_accuracy','Raw accuracy'),('per_char_accuracy','signal_cross_per_char_accuracy','Per-character accuracy')):
        p=primary(metric);fig,axes=plt.subplots(1,3,figsize=(13,5.5))
        heatmap(axes[0],p['conditions']['full'],'Complete prediction · '+label,percentage=True)
        heatmap(axes[1],p['contrasts']['shared_necessity'],'Accuracy drop: remove S',percentage=True,signed=True)
        heatmap(axes[2],p['contrasts']['direct_online_routed_necessity'],'Accuracy drop: remove online R\nS trajectory retained',percentage=True,signed=True)
        fig.suptitle('Actual task accuracy accompanies the loss-based effects',fontweight='bold',fontsize=14)
        fig.subplots_adjust(top=.79,bottom=.25,wspace=.48);fig.text(.5,.04,FOOT,ha='center',fontsize=9);save(fig,filename)
    fig,axes=plt.subplots(1,2,figsize=(12,5.7))
    supplemental=json.loads((ROOT/'natural_vs_fixed_partner_effects.json').read_text())
    if supplemental['raw_sha256']!=s['raw_sha256']:raise ValueError('Natural contrast provenance differs')
    for ax,metric,label in zip(axes,('true_answer_token_NLL','raw_accuracy'),('S removal: answer NLL cost','S removal: accuracy drop')):
        natural=supplemental['metrics'][metric]['natural']
        fixed=supplemental['metrics'][metric]['fixed_producer_P']
        x=np.arange(2)
        ax.bar(x-.18,points(natural),.36,label='S recomputed naturally',color='#e09d58')
        ax.bar(x+.18,points(fixed),.36,label='Identical producer-P S signal',color='#3a8596')
        ni=intervals(natural);ax.vlines(x-.18,ni[:,0],ni[:,1],color='#222',lw=1.2)
        ci=intervals(fixed)
        ax.vlines(x+.18,ci[:,0],ci[:,1],color='#222',lw=1.2)
        ax.axhline(0,color='#777',lw=.8);ax.set_xticks(x,('Consumer A − P','Consumer B − P'));ax.set_ylabel(label);ax.grid(axis='y',alpha=.2)
    axes[1].legend(frameon=False,fontsize=9)
    fig.suptitle('Partner effects with natural versus fixed shared signals',fontweight='bold',fontsize=14)
    fig.subplots_adjust(top=.85,bottom=.27,wspace=.35)
    fig.text(.5,.045,FOOT+'\nNatural and fixed-signal contrasts use the same paired bootstrap; all four metrics and their difference are preserved.',ha='center',fontsize=9)
    save(fig,'natural_vs_fixed_partner_effect')
    fig,axes=plt.subplots(2,3,figsize=(13,8))
    for row,(metric,label) in enumerate((('true_answer_token_NLL','Answer NLL recovered'),('raw_accuracy','Raw accuracy recovered'))):
        values=primary(metric)['contrasts']['recovery_under_routed_removal']
        for column,(subject,title) in enumerate(((None,'Equal-subject macro'),('high_school_biology','Biology'),('high_school_mathematics','Mathematics'))):
            ax=axes[row,column];table=values if subject is None else [v['per_subject'][subject] for v in values]
            v=points(table);ci=intervals(table)
            ax.bar(range(3),v,color=('#688fa3','#db9a55','#789d74'),width=.65)
            ax.vlines(range(3),ci[:,0],ci[:,1],color='#222',lw=1.2);ax.axhline(0,color='#777',lw=.8)
            ax.set_xticks(range(3),NAMES);ax.set_xlabel('S trajectory producer');ax.set_title(title);ax.grid(axis='y',alpha=.2)
            if column==0:ax.set_ylabel(label)
    fig.suptitle('Retaining computed S trajectories after online R removal',fontweight='bold',fontsize=14)
    fig.subplots_adjust(top=.87,bottom=.22,wspace=.35,hspace=.45)
    fig.text(.5,.035,FOOT+'\nSignals were computed with R present; fixed-signal R-zero NLL remains 7.4–7.6 versus complete NLL near 2.1.\nThis is not an R-free model or intrinsic S-only ability; the two subjects have opposite loss responses.',ha='center',fontsize=9)
    save(fig,'routed_removal_signal_recovery')
    (ROOT/'figures/source.json').write_text(json.dumps({'summary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
       'raw_sha256':s['raw_sha256'],'plot_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       'selection':'all 128 primary inputs, all 9 cells, all 4 metrics; no intervention-based cohort selection'},indent=2)+'\n')
    print('Complete E160 figures generated')


if __name__=='__main__':main()
