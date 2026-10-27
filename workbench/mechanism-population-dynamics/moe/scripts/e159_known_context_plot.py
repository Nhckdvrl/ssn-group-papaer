"""Render audited inherited E159 context comparisons; no model or raw data."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results'/'e159'
TASK=ROOT/'known_border_posthoc.json'; LM=ROOT/'known_lm_border_posthoc.json'
OUT=ROOT/'figures'/'e159_known_context'


def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    task=json.loads(TASK.read_text()); lm=json.loads(LM.read_text())
    if any(x.get('status')!='complete_POST_HOC_inherited_only' or x.get('new_model_forwards')!=0 for x in (task,lm)): raise ValueError('Expected completed inherited-only evidence')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','savefig.facecolor':'white'})
    fig,axs=plt.subplots(2,2,figsize=(14,10.5),gridspec_kw={'hspace':.52,'wspace':.34})
    fig.subplots_adjust(left=.12, right=.97, top=.86, bottom=.28)
    fig.suptitle('Computational dependence changes around unchanged expert functions',fontsize=18,fontweight='bold',y=.97)
    fig.text(.5,.925,'Expert function suites span all 16 layers; weights are fixed across the compared contexts.',ha='center',fontsize=11.5)
    colors={'A':'#126a87','B':'#cf6a35'}
    for ax,branch,letter,title in [(axs[0,0],'shared','A','Language modeling · shared suite'),(axs[0,1],'routed','B','Language modeling · routed suite')]:
        for i,function in enumerate(('A','B')):
            vals=[lm['branches'][branch][f'background_{bg}_function_{function}']['removal_delta_NLL'] for bg in ('A','B')]
            y=np.array([v['point'] for v in vals]); ci=np.array([v['input_file_ci95'] for v in vals]); xpos=np.array([0.,1.])+(i-.5)*.045
            ax.errorbar(xpos,y,yerr=np.array([y-ci[:,0],ci[:,1]-y]),color=colors[function],marker='o',lw=2.3,capsize=4,label=f'Fixed {"S" if branch=="shared" else "R"}$_{{{function}}}$')
        ax.set_title(f'{letter}  {title}',loc='left',pad=10);ax.set_xticks([0,1],['Background A','Background B']);ax.set_ylabel('Removal Δ NLL per token');ax.legend(frameon=False,loc='best');ax.grid(axis='y',alpha=.17)
        ax.text(.02,.02,'95% CI: 20 input files',transform=ax.transAxes,fontsize=9,color='#555555',va='bottom')
    ax=axs[1,0]; c=task['same_correct_decision_counts']['B']; counts=[c['native_without_S']['total'],c['same_S_graft_without_S_inherited_P']['total']];total=task['cohort']['total']
    y=np.arange(2);ax.barh(y,counts,color=['#126a87','#cf6a35'],height=.48);ax.set_yticks(y,['Native B','P background + S$_B$']);ax.invert_yaxis();ax.set_xlim(0,37);ax.set_xticks([0,11,22,33]);ax.set_xlabel('Questions still correct after shared-suite removal')
    for i,n in enumerate(counts):ax.text(n+.5,i,f'{n} / {total}',va='center',fontweight='bold')
    ax.set_title('C  Fixed RC tasks · same S$_B$; 33 full-correct cases',loc='left',pad=10)
    ax.text(0,-.25,'33 questions: 30 biology, 3 mathematics; no CI.\nFull true-answer token NLL: native B 2.0078, P + S$_B$ 2.1739.\nSame correct decisions do not imply equal distributions.',transform=ax.transAxes,fontsize=9.5,va='top',linespacing=1.45)
    ax=axs[1,1]; names=['S$_A$','R$_A$','S$_B$','R$_B$']; entries=[]
    for model,branch in [('A','S'),('A','R'),('B','S'),('B','R')]:entries.append(task['metrics']['true_answer_token_NLL'][model][f'native_minus_same_{branch}_receiver_necessity'])
    for i,(name,v) in enumerate(zip(names,entries)):
        point=v['point']; lo,hi=v['question_ci95'];ax.errorbar(point,i,xerr=[[point-lo],[hi-point]],fmt='o',color=colors['A' if i<2 else 'B'],capsize=4,markersize=7)
        ax.annotate(f'{point:+.2f}',(point,i),xytext=(6,7),textcoords='offset points',fontsize=10)
    ax.axvline(0,color='#555555',lw=1);ax.set_yticks(range(4),names);ax.invert_yaxis();ax.set_xlabel('Native − P-background removal Δ NLL per answer token');ax.set_title('D  Fixed RC tasks · 128 fixed questions',loc='left',pad=10);ax.grid(axis='x',alpha=.17)
    ax.text(.02,-.25,'95% CI: paired question bootstrap, 64 per subject;\nequal biology / mathematics macro.',transform=ax.transAxes,fontsize=9.5,va='top',linespacing=1.4)
    footer=('POST-HOC: E150/E151/E155/E156 reuse; inherited zero-endpoint identity; 0 new forwards; one public lineage.\n'
            'Context changes dense backbone, router and other expert branch jointly; no isolated partner effect.\n'
            f'JSON SHA-256: MMLU {sha(TASK)[:12]}  |  LM {sha(LM)[:12]}')
    fig.text(.5,.025,footer,ha='center',va='bottom',fontsize=9,color='#444444',linespacing=1.5)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'):fig.savefig(OUT.with_suffix('.'+ext),dpi=200,bbox_inches='tight')
    plt.close(fig)
    print(str(OUT.with_suffix('.png')));print(str(OUT.with_suffix('.pdf')))


if __name__=='__main__':main()
