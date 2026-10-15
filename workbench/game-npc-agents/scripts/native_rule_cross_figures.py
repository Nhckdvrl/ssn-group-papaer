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
    data={e:{m:json.loads((a.results/f'{e}_{m}_cross_summary.json').read_text()) for m in ['gemma','32b']} for e in ['E67','E68']}
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
    fig,axes=plt.subplots(2,3,figsize=(12,6.5),sharey=True,layout='constrained')
    for i,m in enumerate(['gemma','32b']):
        for j,(metric,title) in enumerate([('goal','Task executed'),('any_legal_block','Any first legal block'),('transfer','Requested transfer')]):
            ax=axes[i,j]
            for b,p in enumerate(['firm','agreeable']):
                vs=[data['E68'][m]['cells'][f'all/{p}/goal_item/{r}/{r}/block_status'][metric] for r in [G,A,B]]
                bars(ax,range(3),vs,colors[b],p,(b-.5)*.34)
            ax.set_xticks(range(3),['Priority','Asset','Do not give']);ax.set_title(models[m]+' — '+title)
            ax.set_ylabel('Episodes (%)')
    axes[0,0].legend(fontsize=9);fig.supxlabel('109 local held-out worlds; ordinary state/error feedback; graph-cluster 95% intervals')
    for ext in ['png','pdf','svg']:fig.savefig(a.out/f'E68_reserve_behavior.{ext}',dpi=180)
    plt.close(fig)


if __name__=='__main__':main()
