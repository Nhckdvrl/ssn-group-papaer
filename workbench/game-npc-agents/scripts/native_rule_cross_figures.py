#!/usr/bin/env python3
"""Standalone research figures for completed E67/E68 graph-cluster estimates."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from native_rule_cross_report import G,A,B


def bars(ax, x, values, color, label, offset=0, width=.32):
    means=np.array([v['mean'] for v in values])*100
    lo=np.array([v['graph_bootstrap_95'][0] for v in values])*100
    hi=np.array([v['graph_bootstrap_95'][1] for v in values])*100
    ax.bar(np.asarray(x)+offset,means,width=width,color=color,label=label,
           yerr=np.array([means-lo,hi-means]),capsize=2,error_kw={'linewidth':.8})
    ax.set_ylim(0,108);ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'svg.fonttype':'none'})
    data={'E67':{m:json.loads((a.results/f'E67_{m}_cross_summary.json').read_text()) for m in ['gemma','32b']}}
    colors=['#4477AA','#EE9944'];models={'gemma':'Gemma 3 12B','32b':'Qwen3 32B'}
    fig,axes=plt.subplots(2,2,figsize=(11,7),sharey=True,layout='constrained')
    combinations=[(A,A),(A,G),(G,A),(G,G)]
    for i,m in enumerate(['gemma','32b']):
        for j,p in enumerate(['firm','agreeable']):
            ax=axes[i,j]
            for b,fb in enumerate(['legacy','block_status']):
                vs=[data['E67'][m]['cells'][f'all/{p}/goal_item/{up}/{ex}/{fb}']['goal'] for up,ex in combinations]
                bars(ax,range(4),vs,colors[b],['Original feedback','State + native error feedback'][b],(b-.5)*.34)
            ax.set_xticks(range(4),['Asset / Asset','Asset / Priority','Priority / Asset','Priority / Priority'],rotation=12)
            ax.set_title(models[m]+' — '+p);ax.set_ylabel('Native task executed (%)')
    axes[0,0].legend(fontsize=8,loc='upper left');fig.supxlabel('Upstream rule / Execution rule; 79 worlds, 3 seeds per persona')
    for ext in ['png','pdf','svg']:fig.savefig(a.out/f'E67_cross_execution.{ext}',dpi=180)
    plt.close(fig)
    if not all((a.results/f'E68_{m}_cross_summary.json').exists() for m in ['gemma','32b']):return
    data['E68']={m:json.loads((a.results/f'E68_{m}_cross_summary.json').read_text()) for m in ['gemma','32b']}
    for scope,n,suffix in [('all',109,'behavior'),('wear_wield',41,'equip_behavior')]:
        fig,axes=plt.subplots(2,3,figsize=(12,6.5),sharey=True,layout='constrained')
        for i,m in enumerate(['gemma','32b']):
            for j,(metric,title) in enumerate([('goal','Task executed'),('any_legal_block','Any legal block'),('transfer','Requested transfer')]):
                ax=axes[i,j]
                for b,p in enumerate(['firm','agreeable']):
                    vs=[data['E68'][m]['cells'][f'{scope}/{p}/goal_item/{r}/{r}/block_status'][metric] for r in [G,A,B]]
                    bars(ax,range(3),vs,colors[b],p,(b-.5)*.34)
                ax.set_xticks(range(3),['Priority','Asset','Do not give']);ax.set_title(models[m]+' — '+title)
                ax.set_ylabel('Episodes (%)')
        axes[0,0].legend(fontsize=9);fig.supxlabel(f'{n} local held-out worlds; ordinary state/error feedback; graph-cluster 95% intervals')
        for ext in ['png','pdf','svg']:fig.savefig(a.out/f'E68_reserve_{suffix}.{ext}',dpi=180)
        plt.close(fig)
    # Paired effects have intervals computed on graph differences, not subtraction of marginal intervals.
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for i,m in enumerate(['gemma','32b']):
        report=data['E68'][m]
        for ax in axes:
            ax.axvline(0,color='#777777',linewidth=.8);ax.spines[['top','right']].set_visible(False)
            ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
        specs=[(p,up) for p in ['firm','agreeable'] for up in [A,G]]
        values=[report['contrasts'][f'wear_wield/{p}/block_status/exec_G_minus_A_given_{up}']['goal'] for p,up in specs]
        other=[report['contrasts']['all/other_item/A_minus_F_generic'][k] for k in ['transfer','both','goal']]
        for ax,vs in zip(axes,[values,other]):
            means=np.array([v['mean'] for v in vs])*100
            lo=np.array([v['graph_bootstrap_95'][0] for v in vs])*100
            hi=np.array([v['graph_bootstrap_95'][1] for v in vs])*100
            ax.errorbar(means,np.arange(len(vs))+(i-.5)*.18,xerr=[means-lo,hi-means],
                        fmt='o',capsize=3,color=colors[i],label=models[m])
            ax.set_xlabel('Paired difference (percentage points)')
    axes[0].set_yticks(range(4),['Firm, upstream Asset','Firm, upstream Priority','Agreeable, upstream Asset','Agreeable, upstream Priority'])
    axes[0].set_title('Goal: execution Priority − Asset\n41 held-out equip worlds')
    axes[1].set_yticks(range(3),['Requested transfer','Both events completed','Original task'])
    axes[1].set_title('Agreeable − Firm under Priority\n60 held-out other-item worlds')
    axes[1].legend(loc='best')
    for ext in ['png','pdf','svg']:fig.savefig(a.out/f'E68_reserve_paired_effects.{ext}',dpi=180)
    plt.close(fig)


if __name__=='__main__':main()
