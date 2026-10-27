"""Plot completed E159 summaries without accessing experiment raw data."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]/'results'/'e159'
SOURCES=('P','A','B','zero')
FOOT='Expert function suites span 16 layers; dense backbone and router parameters are P.\nHidden states and routing remain endogenous; input-question CIs do not measure model-seed uncertainty.'


def save(fig,out,name):
    out.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'):fig.savefig(out/(name+'.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)


def heatmaps(data,out):
    fig,axes=plt.subplots(1,2,figsize=(13,6))
    for ax,(metric,title) in zip(axes,(('true_answer_token_NLL','True-answer NLL / token'),('raw_accuracy','Raw accuracy'))):
        table=data['metrics'][metric]['full_and_border_table']
        x=np.array([[table[r+s]['point'] for s in SOURCES] for r in SOURCES],dtype=float)
        if x.shape!=(4,4) or not np.isfinite(x).all():raise ValueError('Invalid table')
        im=ax.imshow(x,cmap='Blues',aspect='equal');fig.colorbar(im,ax=ax,shrink=.78)
        threshold=(x.min()+x.max())/2
        for i in range(4):
            for j in range(4):ax.text(j,i,f'{x[i,j]:.3f}',ha='center',va='center',color='white' if x[i,j]>threshold else '#1d2630',fontsize=11)
        ax.set_xticks(range(4),SOURCES);ax.set_yticks(range(4),SOURCES);ax.set_xlabel('Shared suite source');ax.set_ylabel('Routed suite source');ax.set_title(title,fontweight='bold')
    fig.suptitle('Full and ablated conditions: P backbone and router',fontsize=15,fontweight='bold');fig.subplots_adjust(top=.84,bottom=.23,wspace=.28)
    fig.text(.5,.065,'Full 3×3 table reuses E156; PP and seven branch-removal conditions measured here.\nThree replay E155 P; four were previously unknown.\n'+FOOT,ha='center',fontsize=9,linespacing=1.45)
    save(fig,out,'full_border_tables')


def interval(ax,y,stat,color,offset=0):
    point=float(stat['point']);lo,hi=map(float,stat['question_ci95'])
    if not np.isfinite([point,lo,hi]).all():raise ValueError('Nonfinite interval')
    ax.hlines(y+offset,lo,hi,color=color,lw=1.8);ax.plot(point,y+offset,'o',color=color,markersize=6)


def effects(data,out):
    metric=data['metrics']['true_answer_token_NLL']; pair=metric['unchanged_partner']
    fig,axes=plt.subplots(1,3,figsize=(15,6),gridspec_kw={'width_ratios':[1,1,1.05]})
    for ax,key,title,labels in ((axes[0],'shared_necessity_fixed_S','Shared necessity · change routed partner',['Fixed S$_P$','Fixed S$_A$','Fixed S$_B$']),
                                (axes[1],'routed_necessity_fixed_R','Routed necessity · change shared partner',['Fixed R$_P$','Fixed R$_A$','Fixed R$_B$'])):
        for i,source in enumerate(SOURCES[:3]):
            interval(ax,i,pair[key]['A-P'][source],'#16708a',-.13);interval(ax,i,pair[key]['B-P'][source],'#cb6a36',.13)
        ax.set_yticks(range(3),labels);ax.invert_yaxis();ax.set_title(title,fontweight='bold');ax.axvline(0,color='#555',lw=.8);ax.grid(axis='x',alpha=.16)
        ax.plot([],[],'o',color='#16708a',label='A − P');ax.plot([],[],'o',color='#cb6a36',label='B − P');ax.legend(frameon=False,loc='best',fontsize=9)
        ax.set_xlabel('Necessity change · NLL / token')
    ax=axes[2];native=metric['native_context']['necessity_differences']['native_B_minus_BB']
    for i,key in enumerate(('shared','routed','balance')):interval(ax,i,native[key],'#6554a4')
    ax.set_yticks(range(3),['Shared','Routed','S − R']);ax.invert_yaxis();ax.axvline(0,color='#555',lw=.8);ax.grid(axis='x',alpha=.16)
    ax.set_title('B experts: native vs P D/G',fontweight='bold');ax.set_xlabel('Necessity difference · NLL / token')
    fig.suptitle('Necessity changes at fixed expert suite',fontsize=15,fontweight='bold');fig.subplots_adjust(left=.10,right=.97,top=.82,bottom=.25,wspace=.58)
    fig.text(.5,.055,'All 128 questions: 64 biology + 64 mathematics; equal-subject macro, 1,000 paired question bootstrap draws, seed 159001.\nS − R cancels the full-performance term and is not a responsibility fraction.\nLeft/middle: D/G parameters fixed to P. Right: same B expert functions, native B versus P D/G.\nExpert function suites span 16 layers; hidden states and routing remain endogenous.',ha='center',fontsize=9,linespacing=1.4)
    save(fig,out,'unchanged_partner_effects')


def patterns(data,out):
    cells=data['all_nine_full_success']['patterns']['cells']; colors=['#9c5d5a','#16708a','#cb6a36','#805aaa','#6d9671']
    labels=['Neither alone; D fails (000)','R alone (010)','S alone (001)','Either alone (011)','D works (1xx)']
    values=[]
    for r in SOURCES[:3]:
      for s in SOURCES[:3]:
        a=np.asarray(cells[r+s]['counts'],dtype=int)
        if a.shape!=(8,) or a.sum()!=33:raise ValueError('Invalid pattern counts')
        values.append([a[0],a[2],a[1],a[3],a[4:].sum()])
    fig,ax=plt.subplots(figsize=(11,7));y=np.arange(9);left=np.zeros(9)
    for i,(label,color) in enumerate(zip(labels,colors)):
        v=np.array(values)[:,i];ax.barh(y,v,left=left,label=label,color=color,height=.72)
        for row,(start,n) in enumerate(zip(left,v)):
            if n:ax.text(start+n/2,row,str(n),ha='center',va='center',fontsize=9,color='white',fontweight='bold')
        left+=v
    ax.set_yticks(y,[r+' / '+s for r in SOURCES[:3] for s in SOURCES[:3]]);ax.invert_yaxis();ax.set_xlabel('Questions / 33');ax.set_ylabel('Routed / shared source');ax.set_xlim(0,33)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.13),ncol=3,frameon=False,fontsize=9)
    fig.suptitle('Branch removal on 33 cases correct in all nine full conditions',fontsize=15,fontweight='bold');fig.subplots_adjust(left=.15,right=.96,top=.88,bottom=.30)
    fig.text(.5,.045,'Pooled 33 cases: 30 biology, 3 mathematics; no CI. Raw eight patterns remain in the summary.\nD = both expert branches removed; R/S alone = respective single branch retained.\n'+FOOT,ha='center',fontsize=9,linespacing=1.4)
    save(fig,out,'selected_cohort_patterns')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--summary',type=Path,default=ROOT/'summary.json');p.add_argument('--output',type=Path,default=ROOT/'figures');args=p.parse_args()
    data=json.loads(args.summary.read_text())
    if data.get('status')!='complete' or tuple(data.get('source_order',()))!=SOURCES:raise ValueError('Completed E159 summary with expected sources required')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    heatmaps(data,args.output);effects(data,args.output);patterns(data,args.output)
    print(f'Figures written to {args.output}')


if __name__=='__main__':main()
