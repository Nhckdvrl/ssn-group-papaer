"""Plot completed E158 whole-terminal-path summaries, without reading raw data."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/'results'/'e158'/'whole_path'
MODELS=('P','A','B'); SCENARIOS=('entity','attribute','paraphrase'); PATHS=('R','S','RS','A')
LABELS=('R','S','R+S','Attn'); COLORS=('#16708a','#cb6a36','#805aaa','#618a55')
FOOT='Whole terminal position across 16 layers; earlier native decoder states fixed; nonreplaced paths endogenous.\n24 countries × 2 relations; equal-relation macro and paired country 95% CI describe these inputs, not model-seed variation.'


def save(fig,output,name):
    output.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'): fig.savefig(output/(name+'.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)


def validate(summary):
    if summary.get('status') not in ('complete','baseline_only'): raise ValueError('Summary is not complete')
    if tuple(summary.get('models',()))!=MODELS or tuple(summary.get('scenarios',()))!=SCENARIOS or tuple(summary.get('paths',()))!=PATHS: raise ValueError('Unexpected axes')
    if summary.get('execution_mode')!='whole_terminal_path_fixed_native_prefix_no_KV_cache': raise ValueError('Unexpected execution mode')
    floor=summary['baseline']['floor']
    if floor.get('KV_cache_used') is not False or floor.get('legacy_cache_field_names') is not True: raise ValueError('Missing readout floor metadata')


def bars(ax,point,ci):
    point=np.asarray(point,dtype=float);ci=np.asarray(ci,dtype=float)
    if point.shape!=(4,) or ci.shape!=(4,2) or not np.isfinite(point).all() or not np.isfinite(ci).all():raise ValueError('Bad plot data')
    ax.bar(np.arange(4),point,color=COLORS,width=.65,zorder=2)
    x=np.arange(4);ax.vlines(x,ci[:,0],ci[:,1],color='#282828',lw=1.1,zorder=3)
    ax.hlines(ci[:,0],x-.06,x+.06,color='#282828',lw=1.1,zorder=3);ax.hlines(ci[:,1],x-.06,x+.06,color='#282828',lw=1.1,zorder=3)
    ax.set_xticks(range(4),LABELS);ax.axhline(0,color='#555',lw=.8);ax.grid(axis='y',alpha=.18,zorder=0)


def baseline(summary,out):
    b=summary['baseline']; top1=np.asarray(b['canonical_top1_by_model_relation']); top10=np.asarray(b['canonical_top10_by_model_relation'])
    if top1.shape!=(3,2) or top10.shape!=(3,2): raise ValueError('Baseline shape mismatch')
    fig,axes=plt.subplots(1,2,figsize=(11,5.6),sharey=True)
    for j,ax in enumerate(axes):
        x=np.arange(3);ax.bar(x-.19,top1[:,j],.38,label='Top 1',color='#16708a');ax.bar(x+.19,top10[:,j],.38,label='Top 10',color='#cb6a36')
        ax.set_title(('Relation 1','Relation 2')[j]);ax.set_xticks(x,MODELS);ax.set_ylim(0,25);ax.grid(axis='y',alpha=.18)
    axes[0].set_ylabel('Correct canonical questions / 24');axes[1].legend(frameon=False)
    f=b['floor']; changes=', '.join(f'{m}: {n}' for m,n in zip(MODELS,f['top1_changed_count']))
    fig.suptitle('Native baseline · canonical factual queries',fontsize=15,fontweight='bold')
    fig.subplots_adjust(bottom=.25,top=.83,wspace=.22)
    fig.text(.5,.07,f"Inherited full-head vs last-only readout, no KV cache: max KL {f['cache_KL_max']:.3g}; top-1 changes {changes} / 96.",ha='center',fontsize=9)
    save(fig,out,'native_baseline')


def metric_panels(summary,out,metric,title,filename):
    stat=summary['all'][metric];p=np.asarray(stat['point']);ci=np.asarray(stat['ci95'])
    if p.shape!=(3,3,4) or ci.shape!=(3,3,4,2): raise ValueError('Feature metric shape mismatch')
    fig,axes=plt.subplots(2,3,figsize=(13,8),sharey=True)
    for row,scenario in enumerate(('Entity','Attribute')):
        for model in range(3):
            ax=axes[row,model];bars(ax,p[model,row],ci[model,row]);ax.set_title(f'{scenario} · {MODELS[model]}');
            if model==0:ax.set_ylabel('Rank specificity gain' if metric=='source_rank_specificity_gain' else 'Source top-1 fraction')
    fig.suptitle(title,fontsize=15,fontweight='bold');fig.subplots_adjust(top=.90,bottom=.15,hspace=.42,wspace=.22);fig.text(.5,.035,FOOT,ha='center',fontsize=9,linespacing=1.45)
    save(fig,out,filename)


def sham(summary,out):
    stat=summary['all']['source_rank_specificity_gain'];p=np.asarray(stat['point']);ci=np.asarray(stat['ci95'])
    fig,axes=plt.subplots(1,3,figsize=(13,5.4),sharey=True)
    for i,ax in enumerate(axes):bars(ax,p[i,2],ci[i,2]);ax.set_title(MODELS[i])
    axes[0].set_ylabel('Rank specificity gain');fig.suptitle('Paraphrase control · source rank specificity',fontsize=15,fontweight='bold')
    fig.subplots_adjust(top=.85,bottom=.25,wspace=.22);fig.text(.5,.045,FOOT,ha='center',fontsize=9,linespacing=1.45);save(fig,out,'paraphrase_control')


def removals(summary,out):
    fig,axes=plt.subplots(2,3,figsize=(13,8))
    for row,(key,label) in enumerate((('target_NLL_increase','Target NLL increase'),('target_top1_drop','Target top-1 accuracy drop'))):
        stat=summary['matched_removal']['all'][key];p=np.asarray(stat['point']);ci=np.asarray(stat['ci95'])
        if p.shape!=(3,4) or ci.shape!=(3,4,2):raise ValueError('Removal shape mismatch')
        for i,ax in enumerate(axes[row]):
            bars(ax,p[i],ci[i]);ax.set_title(f'{label} · {MODELS[i]}')
            if i==0:ax.set_ylabel(label)
    fig.suptitle('Whole-path removal · matched target questions',fontsize=15,fontweight='bold');fig.subplots_adjust(top=.9,bottom=.15,hspace=.43,wspace=.32)
    fig.text(.5,.035,FOOT+'\nRemoval effects are not knowledge fractions.',ha='center',fontsize=9,linespacing=1.45);save(fig,out,'matched_removal')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--summary',type=Path,default=ROOT/'summary.json');p.add_argument('--output',type=Path,default=ROOT/'figures');args=p.parse_args()
    summary=json.loads(args.summary.read_text());validate(summary)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    baseline(summary,args.output)
    if summary['status']=='complete':
        metric_panels(summary,args.output,'source_rank_specificity_gain','Whole-path interchange · source rank specificity','source_rank_specificity')
        sham(summary,args.output);removals(summary,args.output)
    print(f"Figures written to {args.output}")


if __name__=='__main__':main()
