"""Organize complete audited estimates into paper figures; no new tests."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

MOE = Path(__file__).resolve().parents[1]
OUT = MOE / 'paper/figures'
RECORD = {'kind': 'Post-hoc organization; no new model runs, scoring or statistical tests',
          'sources': {}, 'estimates': {}}
BLUE, RED, DARK, GRAY = '#176b9a', '#bf4548', '#30343b', '#92999f'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def source(experiment):
    path = MOE / 'results' / experiment / 'summary.json'
    data = json.loads(path.read_text())
    assert data['status'] == 'complete'
    RECORD['sources'][experiment] = {'path': str(path), 'sha256': sha(path)}
    if experiment in ('e163', 'e164', 'e165'):
        audit_path = path.parent / 'independent_audit.json'
        audit = json.loads(audit_path.read_text())
        assert audit['status'] == 'passed' and audit['summary_sha256'] == sha(path)
        RECORD['sources'][experiment]['audit_sha256'] = sha(audit_path)
    return data


def get(data, experiment, keys, name):
    value = data
    for key in keys:
        value = value[key]
    ci_key = next(k for k in ('ci95', 'file_ci95', 'question_ci95') if k in value)
    p, lo, hi = value['point'], *value[ci_key]
    assert np.isfinite([p, lo, hi]).all() and lo <= p <= hi
    row = {'point': p, 'ci95': [lo, hi], 'source': experiment,
           'json_path': keys, 'original_CI_field': ci_key}
    RECORD['estimates'][name] = row
    return row


def dot(ax, value, position, color, *, offset=0, label=None, horizontal=False):
    p = value['point']; lo, hi = value['ci95']
    if horizontal:
        ax.errorbar(p, position + offset, xerr=[[p-lo], [hi-p]], color=color,
                    fmt='o', capsize=3, ms=5, label=label)
    else:
        ax.errorbar(position + offset, p, yerr=[[p-lo], [hi-p]], color=color,
                    fmt='o', capsize=3, ms=5, label=label)


def save(fig, name, footer):
    fig.text(.5, .015, footer, ha='center', va='bottom', fontsize=9)
    fig.savefig(OUT / (name + '.png'), dpi=210, bbox_inches='tight')
    fig.savefig(OUT / (name + '.pdf'), bbox_inches='tight', metadata={'CreationDate': None, 'ModDate': None})
    plt.close(fig)


def native(s162, s163):
    fig, grid = plt.subplots(2, 2, figsize=(11.6, 7.3))
    axes=list(grid.flat)
    names = ('A', 'B', 'F')
    labels = ('Std anneal\nA', 'Late EMO\nB', 'Full EMO\nF')
    for i, name in enumerate(names):
        v = get(s163, 'e163', ['native', 'LM', 'nll', name, 'absolute', 'native'], 'intact_' + name)
        dot(axes[0], v, i, DARK)
        axes[0].annotate(f"{v['point']:.3f}", (i, v['point']), xytext=(0, 9),
                         textcoords='offset points', ha='center', fontsize=10)
        for key, color, off, lab in [('own_prefix_delta_NLL', BLUE, -.11, 'Selected pool'),
                                      ('random_mean_delta_NLL', GRAY, .11, 'Random pools (mean)')]:
            v = get(s162, 'e162', ['budget', name, 'pool', key], key + '_' + name)
            dot(axes[1], v, i, color, offset=off, label=lab if i == 0 else None)
        for key, color, off, lab in [('R_zero', BLUE, -.11, 'Remove routed suite'),
                                      ('S_zero', RED, .11, 'Remove shared suite')]:
            v = get(s163, 'e163', ['native', 'LM', 'nll', name, 'damage', key], key + '_' + name)
            dot(axes[2], v, i, color, offset=off, label=lab if i == 0 else None)
    for ax, title, ylabel in zip(axes[:3],
            ('A  Intact prediction', 'B  Selective execution: 31R + S', 'C  Predictive dependence'),
            ('Text NLL (nats)', 'Budget NLL damage (nats)', 'Removal NLL damage (nats)')):
        ax.set(title=title, ylabel=ylabel, xticks=range(3), xticklabels=labels, xlim=(-.5, 2.5))
        ax.grid(axis='y', alpha=.18)
    axes[1].set_ylim(bottom=0); axes[2].set_ylim(bottom=0)
    axes[1].legend(frameon=False, fontsize=10); axes[2].legend(frameon=False, fontsize=10)
    counts=[]
    for label in ('P','A','B','F'):
        keys=['all_four_full_correct','models',label,'joint_necessary'];row=s162
        for key in keys:row=row[key]
        denominator=int(row['count']);value=int(round(row['pooled_point']*denominator))
        assert denominator==40 and row['ci']=='not computed'
        counts.append(value)
        RECORD['estimates']['same_facts_joint_'+label]={'source':'e162','json_path':keys,
            'point':value,'denominator':denominator,'original_pooled_point':row['pooled_point'],
            'kind':'Selected common-full-success count; no confidence interval computed',
            'selection':'All four native models answer correctly; all40 retained, 34 biology and6 mathematics.'}
    axes[3].bar(range(4),counts,color=[GRAY,DARK,BLUE,RED],width=.58)
    for i,value in enumerate(counts):axes[3].text(i,value+.6,str(value)+'/40',ha='center',fontsize=11)
    axes[3].set(title='D  Same facts, different cooperation',ylabel='Both R and S necessary (count)',
                xticks=range(4),xticklabels=['Parent\nP','Std anneal\nA','Late EMO\nB','Full EMO\nF'],ylim=(0,29))
    axes[3].grid(axis='y',alpha=.18)
    fig.subplots_adjust(left=.075, right=.99, bottom=.14, top=.93, hspace=.5, wspace=.32)
    save(fig, '01_selection_and_dependence',
         'A-C: all three post-annealing paths; 64 language windows /20 file clusters, original95% input CIs.\n'
         'D: fixed40 questions correct in all four models; selected-set counts, no CI. R/S cover all16 layers.\n'
         'B/F intact text NLL2.6218 /2.6212; task raw accuracy39.06% each.')


def transport(s):
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.15), sharey=True)
    labels = ('Natural routes', 'Fixed P routes', 'Fixed B routes')
    keys = ('natural_B_minus_P', 'R_B_minus_P_at_route_P', 'R_B_minus_P_at_route_B')
    for i, key in enumerate(keys):
        for policy, color, off, lab in [('full', DARK, -.075, 'Full computation'),
                                        ('P32', BLUE, .075, 'Common P selector: 31R + S')]:
            v = get(s, 'e164', ['fresh_primary', 'true_answer_token_NLL', policy + '/' + key], policy + '_' + key)
            dot(axes[0], v, i, color, offset=off, label=lab if i == 0 else None, horizontal=True)
    for i, key in enumerate(('natural', 'fixed_route_P', 'fixed_route_B')):
        v = get(s, 'e164', ['fresh_primary', 'true_answer_token_NLL', 'S_partner_change/' + key], 'shared_' + key)
        dot(axes[1], v, i, RED, horizontal=True)
    axes[0].set(title='A  Replacing R_P with R_B', xlabel='Answer NLL change (negative = better)')
    axes[1].set(title='B  Same S_P: change in removal cost', xlabel='NLL damage difference\n(positive = stronger dependence)')
    for ax in axes:
        ax.set(yticks=range(3), yticklabels=labels, ylim=(2.45, -.45))
        ax.axvline(0, color='.6', ls='--', lw=1); ax.grid(axis='x', alpha=.18)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, fontsize=11,
               loc='upper center', bbox_to_anchor=(.5, .995), ncol=2)
    acc = get(s, 'e164', ['fresh_primary', 'raw_accuracy', 'P32/natural_B_minus_P'], 'P32_accuracy')
    ce = get(s, 'e164', ['fresh_primary', 'choice_CE', 'P32/natural_B_minus_P'], 'P32_choice_CE')
    fig.subplots_adjust(left=.15, right=.98, top=.78, bottom=.28, wspace=.24)
    save(fig, '02_property_and_partner_under_fixed_routes',
         'Common P backbone / gate parameters / S_P. Fixed routes clamp support and weights; other responses remain endogenous.\n'
         f"All 55 subjects / 440 questions; paired 95% subject-cluster intervals. Natural P32 choice CE change = {ce['point']:.3f}; "
         f"accuracy = {acc['point']*100:+.2f} pp [{acc['ci95'][0]*100:.2f}, {acc['ci95'][1]*100:.2f}].")


def message(s):
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8))
    for i, rule in enumerate(('raw', 'norm', 'gram')):
        v = get(s, 'e163', ['cross', 'true_answer_token_NLL', 'matching_cost', rule], 'message_' + rule)
        dot(axes[0], v, i, BLUE)
    axes[0].set(title='A  Message mismatch cost', ylabel='Foreign minus own NLL (nats)',
                xticks=range(3), xticklabels=('Raw', 'Norm', 'Gram'), ylim=(0, .33))
    for ax, field, title, xlabel in [(axes[1], 'true_answer_token_NLL', 'B  Gram minus raw', 'NLL cost change (negative = improvement)'),
                                      (axes[2], 'choice_CE', 'C  Decision distribution', 'Choice CE cost change')]:
        base = ['cross', field, 'rule_contrasts', 'gram_minus_raw']
        for i, subject in enumerate(('high_school_biology', 'high_school_mathematics', None)):
            path = base if subject is None else base + ['per_subject', subject]
            v = get(s, 'e163', path, field + '_gram_minus_raw_' + str(subject))
            dot(ax, v, i, BLUE, horizontal=True)
        ax.set(title=title, xlabel=xlabel, yticks=range(3), yticklabels=('Biology', 'Mathematics', 'Mean'), ylim=(2.4, -.4))
        ax.axvline(0, color='.6', ls='--', lw=1)
    for ax in axes:
        ax.grid(alpha=.16)
    fig.subplots_adjust(left=.065, right=.99, top=.88, bottom=.23, wspace=.65)
    save(fig, '03_actual_message_reuse',
         'Same S_P functions and input text; all 27 source × consumer × correction cells retained.\n'
         '128 biology / mathematics questions, original paired 95% input intervals. Norm/Gram use consumer clean scalar witnesses.')


def external_lineage(s):
    fig, axes = plt.subplots(1, 3, figsize=(12.3, 4.1))
    for i, label in enumerate(('P', 'A')):
        for policy, color, off in [('full', DARK, -.10), ('P16', BLUE, .10)]:
            key = 'absolute/D_'+label+'_G_'+label+'_E_'+label+'_'+policy
            value = get(s, 'e165', ['true_answer_token_NLL', key], 'OL_'+key)
            dot(axes[0], value, i, color, offset=off, label=policy if i == 0 else None)
    axes[0].set(title='A  Intact and restricted quality', ylabel='Answer NLL (nats)',
                xticks=[0, 1], xticklabels=('Mature parent\nP', 'Ordinary anneal\nA'), xlim=(-.5, 1.5))
    axes[0].legend(frameon=False, fontsize=10)
    keys = ('natural_A_minus_P', 'E_A_minus_P_at_route_P', 'E_A_minus_P_at_route_A')
    for i, key in enumerate(keys):
        for policy, color, off in [('full', DARK, -.075), ('P16', BLUE, .075)]:
            value = get(s, 'e165', ['true_answer_token_NLL', policy+'/actual_route/'+key], 'OL_'+policy+'_'+key)
            dot(axes[1], value, i, color, offset=off, horizontal=True)
    axes[1].set(title='B  Expert bank A minus P', xlabel='NLL change (negative = better)',
                yticks=range(3), yticklabels=('Natural routes', 'Fixed P routes', 'Fixed A routes'), ylim=(2.4, -.4))
    for i, context in enumerate(('00', '01')):
        for policy, color, off in [('full', DARK, -.075), ('P16', BLUE, .075)]:
            key = policy+'/D_A_minus_P_fixed_'+context
            value = get(s, 'e165', ['true_answer_token_NLL', key], 'OL_'+key)
            dot(axes[2], value, i, color, offset=off, horizontal=True)
    axes[2].set(title='C  Backbone A minus P', xlabel='NLL change (positive = worse)',
                yticks=[0, 1], yticklabels=('With E_P', 'With E_A'), ylim=(1.5, -.5))
    for ax in axes[1:]:
        ax.axvline(0, color='.6', ls='--', lw=1)
    for ax in axes:
        ax.grid(alpha=.16)
    for label in ('P', 'A'):
        for policy in ('full', 'P16'):
            key='absolute/D_'+label+'_G_'+label+'_E_'+label+'_'+policy
            get(s,'e165',['raw_accuracy',key],'OL_accuracy_'+label+'_'+policy)
    fig.subplots_adjust(left=.065, right=.99, top=.87, bottom=.25, wspace=.65)
    save(fig, '04_native_trends_and_transport',
         'OLMoE: fixed parent-calibrated pool16/64. Full (dark) and P16 (blue); all55 subjects /440 questions, original95% CIs.\n'
         'P16 accuracy is only22.05% /21.14%: this is a probability-quality property, not a deployable compressed model. C fixes G_P parameters, not realized routes.')


def gain_source(family):
    root=MOE/'results/e166';path=root/(family+'_summary.json')
    end=json.loads((root/'execution_complete.json').read_text())
    audit_path=root/'independent_audit.json';audit=json.loads(audit_path.read_text())
    assert end['status']=='complete' and audit['status']=='passed'
    assert audit['families'][family]['summary_sha256']==end['summary_sha256'][family]==sha(path)
    label='e166_'+family
    RECORD['sources'][label]={'path':str(path),'sha256':sha(path),'audit_sha256':sha(audit_path)}
    return json.loads(path.read_text())


def gain_transport(emo,olmoe):
    fig,axes=plt.subplots(2,2,figsize=(11.7,7.6))
    for ax,data,family,title in [(axes[0,0],emo,'emo','A  EMO: source and gain'),
                                 (axes[0,1],olmoe,'olmoe','B  OLMoE: source and gain')]:
        for p,policy in enumerate(('full','pool')):
            for name,color,off,lab in [('donor_minus_P',BLUE,-.09,'Donor minus P'),
                                       ('GainP_minus_P',RED,.09,'GainP minus P')]:
                row=get(data,'e166_'+family,['true_answer_token_NLL',policy+'/S1/'+name],family+'_'+policy+'_'+name)
                dot(ax,row,p,color,offset=off,label=lab if p==0 else None)
        ax.set(title=title,ylabel='Answer NLL change (nats)',xticks=[0,1],xticklabels=['Full','P32' if family=='emo' else 'P16'])
        ax.legend(frameon=False,fontsize=9)
    ax=axes[1,0]
    for p,policy in enumerate(('full','pool')):
        for name,color,off,lab in [('donor_minus_P',BLUE,-.09,'Donor minus P'),('GainP_minus_P',RED,.09,'GainP minus P')]:
            value=get(emo,'e166_emo',['true_answer_token_NLL',policy+'/S_role/'+name],'S_role_'+policy+'_'+name)
            dot(ax,value,p,color,offset=off,label=lab if p==0 else None)
    ax.set(title='C  EMO: change in unchanged S role',ylabel='Extra S-removal NLL cost',xticks=[0,1],xticklabels=['Full','P32'])
    ax.legend(frameon=False,fontsize=9)
    ax=axes[1,1]
    for p,policy in enumerate(('full','pool')):
        for s,color,off,lab in [('S1',BLUE,-.09,'Shared functions active'),('S0',DARK,.09,'Shared outputs zero')]:
            value=get(emo,'e166_emo',['true_answer_token_NLL',policy+'/'+s+'/donor_minus_P'],'S_contribution_'+policy+'_'+s)
            dot(ax,value,p,color,offset=off,label=lab if p==0 else None)
    ax.set(title='D  EMO: same-budget shared intervention',ylabel='Donor minus P answer NLL',xticks=[0,1],xticklabels=['Full','P32'])
    ax.legend(frameon=False,fontsize=9)
    for ax in axes.flat:ax.axhline(0,color='.6',ls='--',lw=1);ax.grid(axis='y',alpha=.16);ax.set_xlim(-.4,1.4)
    fig.subplots_adjust(left=.08,right=.99,top=.94,bottom=.12,hspace=.55,wspace=.35)
    save(fig,'05_gain_and_partner_interventions',
         'Same realized parent routes within each policy; all55 subjects /440 questions, paired95% subject-cluster CIs.\n'
         'GainP: 16 fixed layer scalars from native P calibration responses; no predictive-loss fit. Tokenizers analyzed separately.')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 12, 'axes.titlesize': 13, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42})
    s162, s163, s164, s165 = (source(e) for e in ('e162', 'e163', 'e164', 'e165'))
    native(s162, s163); transport(s164); message(s163); external_lineage(s165)
    count=4
    if (MOE/'results/e166/execution_complete.json').exists():
        gain_transport(gain_source('emo'),gain_source('olmoe'));count=5
    RECORD.update(status='complete', source_code_sha256=sha(__file__),
                  no_new_model_runs=True, no_new_statistical_tests=True,
                  scope='Conditional input intervals; no initialization population or universal modularity claim.',
                  figures={p.name: sha(p) for p in OUT.glob('*') if p.suffix in ('.pdf', '.png')})
    (OUT / 'figure_sources.json').write_text(json.dumps(RECORD, indent=2) + '\n')
    print(json.dumps({'status': 'complete', 'figures': count, 'estimates': len(RECORD['estimates']),
                      'source_sidecar': str(OUT / 'figure_sources.json')}))


if __name__ == '__main__':
    main()
