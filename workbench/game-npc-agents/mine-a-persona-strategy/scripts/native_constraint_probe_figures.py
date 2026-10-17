#!/usr/bin/env python3
"""Standalone scientific figures for completed E65 and E66 probes."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def point(ax, result, y, color, marker='o', scale=100, label=None):
    mean = scale*result['mean']
    lo,hi = np.asarray(result['graph_bootstrap_95'])*scale
    ax.errorbar(mean,y,xerr=[[mean-lo],[hi-mean]],color=color,fmt=marker,
                capsize=2,markersize=4,label=label,lw=1.2)


def save(fig, target):
    for suffix in ['png','pdf','svg']:
        fig.savefig(target.with_suffix('.'+suffix),dpi=180,bbox_inches='tight')
    plt.close(fig)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True)
    a=ap.parse_args()
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    e65=json.loads((a.results/'E65_gemma_scope.json').read_text())
    assert e65['status']=='COMPLETE'
    rules=['none','generic_priority','asset_protection','temporal_permission','negative_only',
           'retention_only','negative_with_use','asset_with_use']
    names=['No added rule (E63)','Task priority (E63)','Asset package (E63)',
           'A: use, then help','B: do not give quest items','C: retain quest items',
           'D: B + use permission','E: asset + use permission']
    fig,axes=plt.subplots(1,3,figsize=(14,5.5),sharey=True)
    metrics=[('goal_executed','Native goal executed (%)'),('neither_event','Neither goal nor transfer (%)'),
             ('plan_feasible_no_actual_goal','Feasible listed plan, goal not executed (%)')]
    for ax,(metric,title) in zip(axes,metrics):
        for i,rule in enumerate(rules):
            for p,dy,color in [('firm',-.13,'#245f9c'),('agreeable',.13,'#d16a35')]:
                point(ax,e65['cells'][f'all/{p}/{rule}'][metric],i+dy,color,label=p.capitalize() if i==0 else None)
        ax.axhline(2.5,c='.6',lw=.7,ls='--')
        ax.set_xlim(-2,102);ax.set_title(title,fontsize=10);ax.grid(axis='x',alpha=.2)
    axes[0].set_yticks(range(len(rules)),names);axes[0].invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(.98,.94), ncol=2, frameon=False)
    fig.suptitle('E65: limits on giving versus permission to use — Gemma 3 12B',fontsize=13)
    fig.text(.02,.015,'79 native worlds (44 wear, 35 wield); 3 seeds averaged per world; 95% world-bootstrap intervals.\n'
             'All five new rules apply at every stage. Historical reference rows are separated; no world rules changed.',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,.94));save(fig,a.results/'E65_constraint_scope')
    fig,axes=plt.subplots(2,3,figsize=(14,7.5),sharex='col')
    conditions=[('natural','none'),('natural','generic_priority'),('natural','asset_protection'),
                ('fixed_asset_context','none'),('fixed_asset_context','generic_priority'),
                ('fixed_asset_context','asset_with_use')]
    names=['Natural: no rule','Natural: task priority','Natural: asset package',
           'Same asset context: remove rule','Same asset context: priority','Same asset context: add use permission']
    metrics=[('goal_probability','Goal-command probability (%)',100),
             ('emote_family_start_probability','Emote-family start probability (%)',100),
             ('legal_start_entropy_nats','Legal-start entropy (nats)',1)]
    for row,(model,title) in enumerate([('gemma','Gemma 3 12B'),('32b','Qwen3 32B')]):
        result=json.loads((a.results/f'E66_{model}_competition.json').read_text())
        assert result['status']=='COMPLETE'
        for ax,(field,label,scale) in zip(axes[row],metrics):
            for i,(context,rule) in enumerate(conditions):
                value=result['cells'][f'pooled/{context}/{rule}'][field]
                if value is not None:
                    point(ax,value,i,'#537a99' if context=='natural' else '#b75f46',scale=scale)
            ax.axhline(2.5,c='.6',lw=.7,ls='--');ax.grid(axis='x',alpha=.2)
            ax.set_xlabel(label,fontsize=10)
            if scale==100:ax.set_xlim(-2,102)
            ax.invert_yaxis()
            ax.set_yticks(range(6),names if ax is axes[row,0] else ['']*6)
        axes[row,0].set_title(title,loc='left',fontweight='bold')
    fig.suptitle('E66: action competition at the first execution decision',fontsize=13)
    fig.text(.02,.015,'79 worlds; fixed seed 6301; personas averaged within world; 95% world-bootstrap intervals.\n'
             'Canonical native-menu trie readout, not exact original JSON-sampler probabilities. Start entropy is not full command entropy.',fontsize=9)
    fig.tight_layout(rect=(0,.08,1,.95));save(fig,a.results/'E66_action_competition')


if __name__=='__main__':main()
