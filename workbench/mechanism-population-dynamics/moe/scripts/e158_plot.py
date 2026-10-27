"""Render E158 completed summary; CPU-only, no model or raw data access."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/'results'/'e158'
MODELS=('P','A','B'); PATHS=('R','S','RS'); COLORS=('#2563a8','#bd5926','#338054')


def save(fig,root,name):
    root.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'):fig.savefig(root/f'{name}.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)


def baseline_plot(data,output):
    base=data['baseline']; top1=np.asarray(base['canonical_top1_by_model_relation']);top10=np.asarray(base['canonical_top10_by_model_relation']);floor=base['floor']
    fig,axes=plt.subplots(1,2,figsize=(10.4,5.7));fig.subplots_adjust(left=.08,right=.97,top=.84,bottom=.27,wspace=.35)
    pos=np.arange(3);w=.34
    for i,ax in enumerate(axes):
        ax.bar(pos-w/2,top1[:,i],w,label='Top-1',color='#2563a8');ax.bar(pos+w/2,top10[:,i],w,label='Top-10',color='#90b4d9')
        ax.set_xticks(pos,MODELS);ax.set_ylim(0,24);ax.set_ylabel('Canonical queries correct (of 24)');ax.set_title(('Capital','Language')[i]);ax.legend(frameon=False)
    fig.suptitle('E158 native baseline: canonical answer first token',fontsize=14)
    counts=', '.join(f'{s}: {int(v)}' for s,v in zip(MODELS,floor['top1_changed_count']))
    comparison = "Full-head vs last-only readout" if data.get("execution_mode") == "full_prefix_fixed_native_causal_prefix_no_KV_cache" else "Cache vs uncached"
    fig.text(.08,.19,f"{comparison}, all 96 queries: top-1 changes {counts}; max KL {floor['cache_KL_max']:.3g};\nmax absolute selected-token log-probability difference {floor['selected_logp_max_abs_difference']:.3g}.",fontsize=9,va='top',linespacing=1.5)
    control = 'readout' if data.get('execution_mode') == 'full_prefix_fixed_native_causal_prefix_no_KV_cache' else 'cache'
    fig.text(.08,.07,f'Only the predefined canonical answer first token is evaluated; model and {control} numerical controls are reported separately.',fontsize=9,va='top')
    save(fig,output,'e158_native_baseline')


def curve(ax,point,ci):
    layers=np.arange(1,17)
    for j,path in enumerate(PATHS):
        y=point[j]; bounds=ci[j]
        ax.plot(layers,y,label=path,color=COLORS[j],lw=1.8)
        ax.fill_between(layers,bounds[:,0],bounds[:,1],color=COLORS[j],alpha=.16,linewidth=0)
    ax.axhline(0,color='0.65',lw=.7);ax.set_xlim(1,16);ax.set_xticks([1,4,8,12,16]);ax.grid(alpha=.14)


def mediation(data,output,scenario_indices,name):
    stat=data['all']['source_rank_specificity_gain']; point=np.asarray(stat['point']);ci=np.asarray(stat['ci95']);rows=len(scenario_indices)
    fig,axes=plt.subplots(rows,3,figsize=(12,3.5*rows+1.7),squeeze=False,sharex=True,sharey=True)
    fig.subplots_adjust(left=.09,right=.97,top=.86,bottom=.22 if rows==1 else .15,wspace=.23,hspace=.35)
    for row,s in enumerate(scenario_indices):
        for m,model in enumerate(MODELS):
            ax=axes[row,m];curve(ax,point[m,s],ci[m,s]);ax.set_title(f'{model} · {("Entity", "Attribute", "Paraphrase")[s]}');ax.set_xlabel('Intervened layer')
            if m==0:ax.set_ylabel('Source rank-specificity gain')
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.5,.91))
    fig.suptitle('Source-answer specificity under path interchange',fontsize=14,y=.98)
    fig.text(.09,.065,'Shading: 95% paired country bootstrap over 24 fixed countries, equal relation macro.\nCanonical answer first-token scope; R/S/RS probe input mediation, not knowledge-storage fractions.',fontsize=9,va='top',linespacing=1.5)
    save(fig,output,name)


def removal(data,output):
    m=data['matched_removal']['all'];metrics=(('target_NLL_increase','Target NLL increase (nat)'),('target_top1_drop','Target top-1 drop'))
    fig,axes=plt.subplots(2,3,figsize=(12,8.1),sharex=True);fig.subplots_adjust(left=.09,right=.97,top=.86,bottom=.16,wspace=.26,hspace=.38)
    for r,(key,label) in enumerate(metrics):
        v=np.asarray(m[key]['point']);ci=np.asarray(m[key]['ci95'])
        for i,model in enumerate(MODELS):
            ax=axes[r,i];curve(ax,v[i],ci[i]);ax.set_title(f'{model} · {label}');ax.set_xlabel('Removed layer')
            if i==0:ax.set_ylabel(label)
    h,l=axes[0,0].get_legend_handles_labels();fig.legend(h,l,loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.5,.91))
    fig.suptitle('Matched target-path removal at the last input position',fontsize=14,y=.98)
    fig.text(.09,.07,'Shading: 95% paired country bootstrap (24 countries, equal relation macro).\nNLL and top-1 loss use separate scales; the canonical answer first token is the measured target.',fontsize=9,va='top',linespacing=1.5)
    save(fig,output,'e158_matched_removal')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--summary',type=Path,default=ROOT/'summary.json');p.add_argument('--output',type=Path,default=ROOT/'figures');args=p.parse_args()
    data=json.loads(args.summary.read_text());status=data.get('status')
    if data.get('experiment')!='E158' or status not in ('complete','baseline_only'):raise ValueError('A complete or sealed baseline-only E158 summary is required')
    if tuple(data['models'])!=MODELS or tuple(data['paths'])!=PATHS:raise ValueError('Unexpected source/path order')
    baseline_plot(data,args.output)
    if status=='complete':
        mediation(data,args.output,(0,1),'e158_entity_attribute_mediation')
        mediation(data,args.output,(2,),'e158_paraphrase_control')
        removal(data,args.output)

if __name__=='__main__':main()
