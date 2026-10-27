"""Four-panel mature-source research map from sealed E155–E157 results."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]/'results'

def load(path):
    with (ROOT/path).open() as f:return json.load(f)
def digest(path):
    with (ROOT/path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def point_ci(row):return float(row['point']),np.array(row['question_ci95'],dtype=float)
def bar_ci(ax,y,row,color,marker,label=None):
    p,ci=point_ci(row);ax.errorbar(p,y,xerr=[[max(0,p-ci[0])],[max(0,ci[1]-p)]],marker=marker,color=color,capsize=3,markersize=6,linestyle='none',label=label)

def main():
    p155=load('e155/dependency_patterns_posthoc.json'); e155=load('e155/summary.json'); e156=load('e156/transfer_contrasts.json');e157=load('e157/summary.json')
    if e155['status']!='complete' or e156['status']!='complete' or e157['status']!='complete' or e156['raw_sha256']!=e157['previous_raw_sha256']:raise ValueError('Expected completed compatible source results')
    fig,axes=plt.subplots(2,2,figsize=(16,11.8));fig.subplots_adjust(left=.08,right=.96,top=.91,bottom=.16,wspace=.35,hspace=.51)
    a,b,c,d=axes.ravel()
    for xy,text,color in [((.13,.55),'P · pre-anneal\n1T tokens','#e9edf2'),((.69,.77),'A · standard\n+50B tokens','#dceaf8'),((.69,.30),'B · constrained\n+50B tokens','#f8e1d3')]:
        a.text(*xy,text,ha='center',va='center',fontsize=11,bbox=dict(boxstyle='round,pad=.6',facecolor=color,edgecolor='#8795a1'))
    for end in ((.48,.75),(.48,.32)):a.add_patch(FancyArrowPatch((.28,.55),end,arrowstyle='->',mutation_scale=14,lw=1.4,color='#526372'))
    acc=[e155['sources'][s]['native']['raw_accuracy']['point']*100 for s in 'PAB']
    a.text(.5,.07,'Fixed 128-question RC accuracy (P / A / B): '+' / '.join(f'{x:.2f}%' for x in acc)+'\nDeclared public lineage; original batch/optimizer byte chain not verified.',ha='center',va='bottom',fontsize=9,transform=a.transAxes)
    a.set(xlim=(0,1),ylim=(0,1));a.axis('off');a.set_title('A  One declared mature lineage',loc='left',fontweight='bold')
    labels=['D fails; either branch removal fails','Only D+R succeeds','Only D+S succeeds','D fails; D+R and D+S succeed','D-only succeeds']
    colors=['#9c4d46','#5181b0','#d49058','#80a981','#b2b8c0'];x=np.arange(3); bottom=np.zeros(3)
    raw=[p155['sources'][s]['pooled_pattern_counts'] for s in 'PAB']
    values=np.array([[v[0],v[2],v[1],v[3],sum(v[4:8])] for v in raw]);assert values.sum(axis=1).tolist()==[44]*3
    for i,(label,color) in enumerate(zip(labels,colors)):
        y=values[:,i];b.bar(x,y,bottom=bottom,color=color,label=label,width=.65)
        for j,num in enumerate(y):
            if num:b.text(j,bottom[j]+num/2,str(num),ha='center',va='center',fontsize=9,color='white' if i in (0,1) else 'black')
        bottom+=y
    b.set_xticks(x,['P','A','B']);b.set_ylim(0,48);b.set_ylabel('Questions (pooled count)');b.set_title('B  Native-common-success patterns',loc='left',fontweight='bold')
    b.legend(loc='upper center',bbox_to_anchor=(.5,-.14),ncol=2,fontsize=8,frameon=False)
    b.text(.02,.95,'POST-HOC · 44 questions; eight patterns retained in source',transform=b.transAxes,fontsize=8,va='top')
    rows=e156['scopes']['all_questions'];keys=['RA_SP_minus_PP','RB_SP_minus_PP','RP_SB_minus_PP','RB_SB_minus_PP']; names=['R A / S P','R B / S P','R P / S B','R B / S B']
    for i,k in enumerate(keys):
        r=rows[k]['policies'];bar_ci(c,i+.10,r['full']['true_answer_token_NLL'],'#2563a8','o','Full' if i==0 else None)
        bar_ci(c,i-.10,r['receiverP32']['true_answer_token_NLL'],'#bd5926','s','P-mask' if i==0 else None)
    c.axvline(0,color='.6',lw=.8);c.set_yticks(range(4),names);c.invert_yaxis();c.set_xlabel('Answer-token NLL − PP (nat/token)');c.set_title('C  E156: fixed full and P-mask transfer',loc='left',fontweight='bold');c.legend(frameon=False,loc='upper left',fontsize=9);c.grid(axis='x',alpha=.15)
    cells=e157['scopes']['all_questions']['views']['on_domain']['cells'];whole=rows['RB_SP_minus_PP']['policies']['full']['true_answer_token_NLL']
    drows=[whole,cells['BP']['minus_PP_full']['true_answer_token_NLL'],cells['BB']['minus_PP_full']['true_answer_token_NLL']]
    for i,(r,color) in enumerate(zip(drows,['#78838e','#2563a8','#bd5926'])):bar_ci(d,i,r,color,'o')
    d.axvline(0,color='.6',lw=.8);d.set_yticks([0,1,2],['Whole R B / S P','Partial R B / S P','Partial R B / S B']);d.invert_yaxis();d.set_xlabel('Full answer-token NLL − PP (nat/token)');d.set_title('D  E157: on-domain partial vs whole',loc='left',fontweight='bold');d.grid(axis='x',alpha=.15)
    p,ci=point_ci(cells['BP']['minus_whole_bank_full']['true_answer_token_NLL'])
    d.text(.02,.16,f'Partial − whole R B / S P: {p:+.6f} [{ci[0]:+.6f}, {ci[1]:+.6f}]\nPaired difference; not an equivalence claim.',transform=d.transAxes,fontsize=9,va='bottom')
    fig.suptitle('Mature MoE: computational dependence and functional reuse',fontsize=16)
    sources=['e155/dependency_patterns_posthoc.json','e155/summary.json','e156/transfer_contrasts.json','e157/summary.json']
    references='  |  '.join(f'{s}  {digest(s)[:12]}' for s in sources)
    fig.text(.08,.105,'One lineage, two fixed subjects. Error bars: paired question bootstrap; fixed inputs, not training-seed variation.\nRaw accuracy did not improve in the reported E157 reuse comparison. Active top-k remains 7 routed + 1 shared; 32 is an eligibility budget.\nE156 masked results are inherited references, not new E157 measurements. Panels compare shared successes, function donors and receiver context.',fontsize=9,va='top',linespacing=1.5)
    fig.text(.08,.025,'Sources (results/ relative path · SHA256 prefix): '+references,fontsize=7,va='bottom')
    out=ROOT/'e157/figures';out.mkdir(exist_ok=True,parents=True)
    for ext in ('png','pdf'):fig.savefig(out/f'mature_role_and_reuse_chain.{ext}',dpi=220,bbox_inches='tight')
    plt.close(fig)

if __name__=='__main__':main()
