"""Scientific figure from immutable E30 numerical summaries, no raw stimuli."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot(summary,wording,out):
    s=json.loads(summary.read_text());w=json.loads(wording.read_text());fig,axes=plt.subplots(1,2,figsize=(10.5,4.5),layout='constrained')
    predicate=s['experiment']=='E31'
    markers=('same_began','different_began') if predicate else ('separate','second')
    colors={markers[0]:'#276c9d',markers[1]:'#bb6a20'}
    labels={markers[0]:'Same predicate',markers[1]:'Different predicate'} if predicate else {m:m for m in markers}
    def point(ax,x,v,color,label=None,marker='o',alpha=1):
        y=v['estimate'];lo,hi=v['ci95'];ax.errorbar(x,y,yerr=[[y-lo],[hi-y]],fmt=marker,color=color,capsize=3,markersize=6,label=label,alpha=alpha)
    point(axes[0],0,s['probability']['cells']['all/D/original/original_activity/named/activity'],'#202020','Original activity')
    point(axes[0],0,s['probability']['cells']['all/D/original/original_activity/named/neutral_entity'],'#aaaaaa',marker='s')
    for marker,shift in zip(markers,(-.10,.10)):
        for x,mode in ((1,'same_actor'),(2,'other_actor')):
            point(axes[0],x+shift,s['probability']['cells'][f'all/D/{marker}/{mode}/named/activity'],colors[marker],labels[marker] if x==1 else None)
            point(axes[0],x+shift,s['probability']['cells'][f'all/D/{marker}/{mode}/named/neutral_entity'],'#aaaaaa',marker='s',alpha=.7)
        for x,kind in ((0,'same_actor_new_activity'),(1,'other_actor_new_activity')):
            point(axes[1],x+shift,w['cells'][f'all/{marker}/{kind}/named'],colors[marker],labels[marker] if x==0 else None)
    axes[0].set(xticks=[0,1,2],xticklabels=['Original\nactor / activity','Same actor\nnew activity','Other actor\nnew activity'],ylabel='Role-fact effect on patient preference (bits)',title='A. Named participant prediction reverses',ylim=(-4.8,4.5))
    axes[0].text(.03,.04,'Gray squares: matched neutral entity mention',transform=axes[0].transAxes,color='#666666',fontsize=9)
    axes[1].set(xticks=[0,1],xticklabels=['Same actor\nnew activity','Other actor\nnew activity'],ylabel='Signed old-role carryover (percentage points)',title='B. Relation classifications retain old direction',ylim=(-5,90))
    axes[1].text(.03,.12,'Named facts; wording split preregistered.\nBase: all three cyclic label mappings.' if predicate else 'Named facts; wording split is post hoc.\nBase: all three cyclic label mappings.',transform=axes[1].transAxes,color='#666666',fontsize=9)
    for ax in axes:
        ax.axhline(0,color='#777777',lw=.8,ls='--');ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,fontsize=9);ax.grid(axis='y',alpha=.15)
    fig.suptitle('New-event participant effects depend on predicate matching' if predicate else 'Event boundaries change how participant facts are used',fontsize=13)
    fig.supxlabel('Frozen Qwen3-8B; source S1 removed; 24 items / 12 verb families; paired bootstrap 95% CI',fontsize=9)
    for suffix in ('.png','.pdf'):fig.savefig(out.with_suffix(suffix),dpi=180)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--summary',type=Path,required=True);p.add_argument('--wording',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();plot(a.summary,a.wording,a.out)
