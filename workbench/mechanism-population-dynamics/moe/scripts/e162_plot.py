"""E162 complete-population figures; all four published paths remain visible."""
import json
import hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/'results/e162'
NAMES=('P','A','B','F');LABELS=('P: before anneal','A: standard','B: late EMO','F: full-course EMO')
COLORS=('#5a7e9a','#d7994e','#5b987b','#9a729e')
FOOT=('Fixed public checkpoints and inputs; no new training. Input CIs do not quantify training-seed uncertainty.\n'
      'F and B share the declared final EMO recipe; original initialization and optimizer/batch chains are unverified.')


def save(fig,name):
    output=ROOT/'figures';output.mkdir(exist_ok=True)
    for ext in ('png','pdf'):fig.savefig(output/(name+'.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)


def bars(ax,tables,labels,colors,kind):
    x=np.arange(len(tables));p=np.array([t['point'] for t in tables]);ci=np.array([t[kind] for t in tables])
    ax.bar(x,p,color=colors,width=.65);ax.vlines(x,ci[:,0],ci[:,1],color='#222',lw=1.15)
    ax.axhline(0,color='#777',lw=.8);ax.set_xticks(x,labels);ax.grid(axis='y',alpha=.17)


def main():
    path=ROOT/'summary.json';s=json.loads(path.read_text())
    if s['status']!='complete' or s['models']!=list(NAMES):raise ValueError('Complete four-model summary required')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    for metric,title in [('raw_accuracy','Raw accuracy'),('per_char_accuracy','Per-character accuracy'),
                         ('true_answer_token_NLL','True-answer token NLL'),('choice_CE','Choice CE')]:
        fig,axes=plt.subplots(1,2,figsize=(13,5.9));x=np.arange(4)
        conditions=('native','routed_zero','shared_zero','all_moe_zero')
        for j,condition in enumerate(conditions):
            values=[s['task'][metric][n]['absolute'][condition] for n in NAMES]
            p=np.array([v['point'] for v in values]);ci=np.array([v['ci95'] for v in values]);offset=(j-1.5)*.19
            axes[0].bar(x+offset,p,.18,color=COLORS[j],label=('Complete','R zero','S zero','R+S zero')[j])
            axes[0].vlines(x+offset,ci[:,0],ci[:,1],color='#222',lw=.8)
        axes[0].set_xticks(x,NAMES);axes[0].set_ylabel(title);axes[0].legend(frameon=False,fontsize=9);axes[0].grid(axis='y',alpha=.2)
        for j,condition in enumerate(('routed_zero','shared_zero')):
            values=[s['task'][metric][n]['removal_cost'][condition] for n in NAMES]
            p=np.array([v['point'] for v in values]);ci=np.array([v['ci95'] for v in values]);offset=(j-.5)*.3
            axes[1].bar(x+offset,p,.29,color=('#5587a1','#cb8d4e')[j],label=('R removal','S removal')[j]);axes[1].vlines(x+offset,ci[:,0],ci[:,1],color='#222',lw=.9)
        axes[1].axhline(0,color='#777',lw=.8);axes[1].set_xticks(x,NAMES);axes[1].set_ylabel('Accuracy drop' if metric.endswith('accuracy') else 'Loss increase')
        axes[1].legend(frameon=False,fontsize=9);axes[1].grid(axis='y',alpha=.2)
        fig.suptitle('Native task computation across mature training paths · '+title,fontweight='bold',fontsize=14)
        fig.subplots_adjust(top=.86,bottom=.24,wspace=.3);fig.text(.5,.045,FOOT+'\n128 questions, 64 per subject; paired within-subject bootstrap 95% CI. All four conditions retained.',ha='center',fontsize=9)
        save(fig,'task_'+metric)
    fig,axes=plt.subplots(1,2,figsize=(12,5.8))
    for j,c in enumerate(('native','routed_zero','shared_zero')):
        tables=[s['LM']['full'][n][c]['nll'] for n in NAMES];p=np.array([v['point'] for v in tables]);ci=np.array([v['file_ci95'] for v in tables]);x=np.arange(4)+(j-1)*.24
        axes[0].bar(x,p,.23,color=COLORS[j],label=('Complete','R zero','S zero')[j]);axes[0].vlines(x,ci[:,0],ci[:,1],color='#222',lw=.9)
    axes[0].set_xticks(range(4),NAMES);axes[0].set_ylabel('Natural-text NLL');axes[0].legend(frameon=False);axes[0].grid(axis='y',alpha=.2)
    tables=[s['F_minus_reference']['LM']['full'][n]['R_cost_minus_S_cost'] for n in NAMES[:3]]
    bars(axes[1],tables,('F − P','F − A','F − B'),COLORS[:3],'file_ci95');axes[1].set_ylabel('Difference in R cost − S cost')
    fig.suptitle('Natural text · absolute quality and allocation contrasts',fontweight='bold',fontsize=14)
    fig.subplots_adjust(top=.85,bottom=.23,wspace=.3);fig.text(.5,.04,FOOT+'\n64 windows and 20 paired input-file clusters; 95% CI. Positive allocation contrast means a shift toward R dependence relative to S.',ha='center',fontsize=9)
    save(fig,'text_quality_and_allocation')
    fig,axes=plt.subplots(1,2,figsize=(12,5.8))
    for r,rule in enumerate(('pool','full')):
        ax=axes[r];x=np.arange(3)
        for j,key in enumerate(('own_prefix_delta_NLL','random_mean_delta_NLL')):
            tables=[s['budget'][n][rule][key] for n in ('A','B','F')];p=np.array([v['point'] for v in tables]);ci=np.array([v['file_ci95'] for v in tables]);offset=(j-.5)*.3
            ax.bar(x+offset,p,.29,color=('#5c8d9c','#d7994e')[j],label=('Own input-prefix selector','Three fixed random probes')[j]);ax.vlines(x+offset,ci[:,0],ci[:,1],color='#222',lw=.9)
        ax.set_xticks(x,('A','B','F'));ax.set_title(('Pool denominator','Full 127-expert denominator')[r]);ax.set_ylabel('Suffix NLL increase from same complete model');ax.grid(axis='y',alpha=.2)
    axes[0].legend(frameon=False,fontsize=9)
    fig.suptitle('Input-based selection across both normalization rules',fontweight='bold',fontsize=14)
    fig.subplots_adjust(top=.85,bottom=.25,wspace=.3);fig.text(.5,.045,FOOT+'\n32 slots = 31 routed + shared; prefix-only selection, suffix-only scores. Both rules and all three random probes retained.\nP is absent from this common-rule figure because its full-denominator counterfactual was not measured.',ha='center',fontsize=9)
    save(fig,'prefix_and_random_budgets')
    selected=s['all_four_full_correct'];fig,ax=plt.subplots(figsize=(11,6.5));bottom=np.zeros(4)
    palette=plt.get_cmap('tab20')
    for code in range(8):
        y=np.array([selected['models'][n]['counts'][code] for n in NAMES]);ax.bar(range(4),y,bottom=bottom,color=palette(2*code),label=f'{code:03b}');bottom+=y
    ax.set_xticks(range(4),NAMES);ax.set_ylabel('Questions in fixed common-success subset')
    ax.legend(title='D / D+R / D+S',ncol=4,frameon=False,loc='upper center',bbox_to_anchor=(.5,1.29))
    fig.suptitle(f"Same successful decisions, branch dependence retained · n={selected['count']}",fontweight='bold')
    fig.subplots_adjust(top=.72,bottom=.24)
    fig.text(.5,.05,FOOT+f"\nSelected by all four native complete systems correct; subject counts {selected['per_subject_count']}. No CI or population claim.\nAll eight patterns, including nonmonotonic ones, remain visible; 000 means neither D nor either single path preserves the correct choice.",ha='center',fontsize=9)
    save(fig,'common_success_patterns')
    (ROOT/'figures/source.json').write_text(json.dumps({'summary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'raw_sha256':s['raw_sha256'],
        'plot_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'selection':'All primary inputs/models/conditions; common-success plot explicitly secondary'},indent=2)+'\n')
    print('All E162 figures complete')


if __name__=='__main__':main()
