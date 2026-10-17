#!/usr/bin/env python3
"""E70–E73 static scientific exports from complete graph-cluster reports."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def save(fig, folder, name):
    for ext in ['png', 'pdf', 'svg']:
        p = folder/(name+'.'+ext)
        metadata = {'Date': None} if ext == 'svg' else {'CreationDate': None} if ext == 'pdf' else None
        fig.savefig(p, dpi=180, metadata=metadata)
        if ext == 'svg':
            p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(exist_ok=True)
    reports = {model: json.loads((args.results/f'E70_{model}_complete.json').read_text())
               for model in ['gemma', '32b']}
    plt.rcParams.update({'font.size': 10, 'pdf.fonttype': 42, 'svg.fonttype': 'none', 'svg.hashsalt': 'game-npc-E70-E72'})
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout='constrained', sharey=True)
    outcomes = [('to_goal', 'Authored recipient', '#4477AA'),
                ('to_competitor', 'Other peer', '#CC6677'),
                ('to_other', 'Other recipient', '#999999'),
                ('no_transfer', 'No selected-item Give', '#DDCC77')]
    for i, (model, name) in enumerate([('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
        for j, state in enumerate(['ready', 'equipped']):
            ax = axes[i, j]; bottom = np.zeros(4)
            keys = [p+'/'+state+'_'+d for d in ['aligned', 'divert'] for p in ['firm', 'agreeable']]
            for metric, label, color in outcomes:
                means = np.array([reports[model]['cells'][k][metric]['mean'] for k in keys])*100
                ax.bar(np.arange(4), means, bottom=bottom, label=label, color=color, width=.7)
                bottom += means
            ax.set_xticks(np.arange(4), ['Firm\naligned', 'Agreeable\naligned', 'Firm\ndivert', 'Agreeable\ndivert'])
            ax.set_title(name+' / '+('item ready' if state == 'ready' else 'item equipped'))
            ax.set_ylim(0, 100); ax.set_ylabel('First selected-item disposition (%)')
            ax.spines[['top', 'right']].set_visible(False)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside upper center', ncol=4, frameon=False)
    fig.supxlabel('117 source worlds, three seeds; up to eight actions, stopping at first selected-item Give.\nAligned = speaker is authored recipient. Source goal, personas and native rules retained.', fontsize=10)
    save(fig, args.out, 'E70_first_disposition')
    selections = [
        ('mechanics_minus_baseline/aligned', 'to_goal', 'Mechanics / aligned: to authored recipient'),
        ('mechanics_minus_baseline/divert', 'to_goal', 'Mechanics / divert: to authored recipient'),
        ('mechanics_minus_baseline/divert', 'to_competitor', 'Mechanics / divert: to requesting peer'),
        ('priority_minus_baseline/divert', 'to_goal', 'Priority / divert: to authored recipient'),
        ('staged_minus_baseline/aligned', 'to_goal', 'Staged / aligned: to authored recipient'),
        ('staged_minus_baseline/divert', 'to_goal', 'Staged / divert: to authored recipient')]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), layout='constrained', sharey=True)
    for ax, (model, name) in zip(axes, [('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
        for persona, color, offset in [('firm', '#4477AA', .10), ('agreeable', '#AA3377', -.10)]:
            vals = [reports[model]['contrasts'][persona+'/'+term][metric] for term, metric, _ in selections]
            means = np.array([v['mean'] for v in vals])*100
            lower = np.array([v['graph_bootstrap_95'][0] for v in vals])*100
            upper = np.array([v['graph_bootstrap_95'][1] for v in vals])*100
            ax.errorbar(means, np.arange(len(vals))+offset, xerr=[means-lower, upper-means], fmt='o', capsize=3,
                        label=persona.capitalize(), color=color)
        ax.axvline(0, color='#777777', linewidth=.8); ax.grid(axis='x', alpha=.2)
        ax.set_yticks(np.arange(len(selections)), [r[2] for r in selections]); ax.set_ylim(len(selections)-.5, -.5)
        ax.spines[['top', 'right']].set_visible(False); ax.set_title(name)
        ax.set_xlabel('Paired difference (percentage points)'); ax.legend(frameon=False)
    fig.supxlabel('All controls hold equipped physical state fixed. Pointwise graph-cluster 95% intervals.\nStaged and direct interfaces share the exact same conversation; interface packages differ.', fontsize=10)
    save(fig, args.out, 'E70_paired_controls')
    joined_paths = {m: args.results/f'E70_E71_{m}_joined.json' for m in ['gemma', '32b']}
    if all(p.exists() for p in joined_paths.values()):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained', sharey=True)
        for ax, (model, name) in zip(axes, [('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
            data = json.loads(joined_paths[model].read_text())
            for state, color, offset in [('ready', '#4477AA', .10), ('equipped', '#CC6677', -.10)]:
                vals = []
                for context in ['unsolicited', 'aligned', 'divert']:
                    f = data['cells']['firm/'+state+'_'+context]['to_goal']['mean']
                    a = data['cells']['agreeable/'+state+'_'+context]['to_goal']['mean']
                    if context == 'unsolicited':
                        entry = data['contrasts']['A_minus_F/'+state+'_unsolicited']['to_goal']
                    else:
                        entry = reports[model]['contrasts']['A_minus_F/'+state+'_'+context]['to_goal']
                    assert abs(entry['mean']-(a-f)) < 1e-10
                    vals.append(entry)
                means = np.array([v['mean'] for v in vals])*100
                lower = np.array([v['graph_bootstrap_95'][0] for v in vals])*100
                upper = np.array([v['graph_bootstrap_95'][1] for v in vals])*100
                ax.errorbar(means, np.arange(3)+offset, xerr=[means-lower, upper-means],
                            fmt='o', capsize=3, color=color, label=state.capitalize())
            ax.set_yticks(np.arange(3), ['No solicitation', 'Aligned request', 'Diverting request'])
            ax.set_ylim(2.5, -.5); ax.axvline(0, color='#777777', linewidth=.8)
            ax.grid(axis='x', alpha=.2); ax.spines[['top', 'right']].set_visible(False)
            ax.set_title(name); ax.set_xlabel('Agreeable - Firm: authored-recipient Give (pp)')
            ax.legend(frameon=False)
        fig.supxlabel('Same 117 authored Give tasks, source items and three seeds. Pointwise graph-cluster 95% intervals.\nNo solicitation removes request and generated dialogue together; it is a context-package baseline.', fontsize=10)
        save(fig, args.out, 'E70_E71_persona_by_context')
    e72_paths = {m: args.results/f'E72_{m}_complete.json' for m in ['gemma','32b']}
    if all(p.exists() for p in e72_paths.values()):
        selections = [('aligned','to_goal','Aligned: authored-recipient Give'),
                      ('divert','to_goal','Divert: authored-recipient Give'),
                      ('divert','to_competitor','Divert: requesting-peer Give'),
                      ('divert','no_transfer','Divert: no selected-item Give')]
        fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained',sharey=True)
        for ax,(model,name) in zip(axes,[('gemma','Gemma 3 12B'),('32b','Qwen3 32B')]):
            r=json.loads(e72_paths[model].read_text())
            for p,color,offset in [('firm','#4477AA',.10),('agreeable','#AA3377',-.10)]:
                vv=[r['contrasts'][p+'/goal_minus_valid/'+d][f] for d,f,_ in selections]
                means=np.array([v['mean'] for v in vv])*100
                lo=np.array([v['graph_bootstrap_95'][0] for v in vv])*100
                hi=np.array([v['graph_bootstrap_95'][1] for v in vv])*100
                ax.errorbar(means,np.arange(4)+offset,xerr=[means-lo,hi-means],fmt='o',capsize=3,label=p.capitalize(),color=color)
            ax.set_yticks(np.arange(4),[s[2] for s in selections]);ax.set_ylim(3.5,-.5)
            ax.axvline(0,color='#777777',linewidth=.8);ax.grid(axis='x',alpha=.2)
            ax.set_title(name);ax.set_xlabel('Expanded - native-menu candidates (pp)')
            ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False)
        fig.supxlabel('117 equipped source worlds; identical dialogue/persona/state and eight-action budget.\nOnly candidate list/enum differs; failed attempts consume steps. Pointwise graph-cluster 95% intervals.',fontsize=10)
        save(fig,args.out,'E72_candidate_effects')
    e73_paths = {m: args.results/f'E73_{m}_complete.json' for m in ['gemma', '32b']}
    if all(p.exists() for p in e73_paths.values()):
        arms = ['valid_candidates', 'goal_candidates', 'initial_feedback']
        fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout='constrained', sharey=True)
        for i, (model, name) in enumerate([('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
            r = json.loads(e73_paths[model].read_text())
            for j, direction in enumerate(['aligned', 'divert']):
                ax = axes[i, j]
                for p, color, offset in [('firm', '#4477AA', -.10), ('agreeable', '#AA3377', .10)]:
                    vv = [r['cells'][p+'/'+direction+'_'+arm]['to_goal'] for arm in arms]
                    means = np.array([v['mean'] for v in vv])*100
                    lo = np.array([v['graph_bootstrap_95'][0] for v in vv])*100
                    hi = np.array([v['graph_bootstrap_95'][1] for v in vv])*100
                    ax.errorbar(np.arange(3)+offset, means, yerr=[means-lo, hi-means],
                                fmt='o', capsize=3, color=color, label=p.capitalize())
                ax.set_xticks(np.arange(3), ['Native menu', 'Expanded\ncandidates', 'Native menu +\ninitial feedback'])
                ax.set_ylim(0, 104); ax.set_ylabel('Give to authored recipient (%)')
                ax.set_title(name+' / '+direction+' request')
                ax.grid(axis='y', alpha=.2); ax.spines[['top', 'right']].set_visible(False)
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='outside upper center', ncol=2, frameon=False)
        fig.supxlabel('Same 117 equipped worlds, exact dialogue and eight-action budget; three seeds, graph-cluster 95% intervals.\nExpanded candidates allow costly failed attempts; initial feedback exposes a true engine check before the first action.', fontsize=10)
        save(fig, args.out, 'E73_initial_information')


if __name__ == '__main__':
    main()
