"""E12 preregistered source/answer effects; different scales kept separate."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);a=p.parse_args()
    source=json.loads((a.results/'E12-E10-source-summary.json').read_text())
    answer=json.loads((a.results/'E10-summary.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    def draw(ax,x,v,color,label=None,scale=1):
        y=v['estimate']*scale;lo,hi=[t*scale for t in v['ci95']]
        ax.errorbar(x,y,yerr=[[y-lo],[hi-y]],fmt='o',capsize=4,color=color,label=label)
    for i,c in enumerate(('gp','explicit_cue')):
        k=f'pooled/all/base/option1_A/question_pre_minus_post/options_post/disambiguator_bits/{c}'
        draw(axes[0],i,source['processing_effects'][k],'#165b9d')
        for mapping,offset,color,label in [('option1_A',-.12,'#165b9d','Option1 = A'),('option1_B',.12,'#ba4a30','Option1 = B')]:
            k=f'pooled/all/base/{mapping}/q_pre_minus_post/o_post/{c}/correct'
            draw(axes[1],i+offset,answer['placement_effects'][k],color,label if i==0 else None,100)
    axes[0].set_title('Predicting the original disambiguating word')
    axes[0].set_ylabel('Early minus late question: surprisal (bits)')
    axes[1].set_title('Answering the original comprehension question')
    axes[1].set_ylabel('Early minus late question: accuracy (pp)')
    for ax in axes:
        ax.set_xticks([0,1],['GP','Explicit cue']);ax.set_xlim(-.5,1.5)
        ax.axhline(0,color='gray',lw=.7);ax.spines[['top','right']].set_visible(False)
    axes[1].legend(frameon=False,fontsize=9)
    fig.suptitle('Same sentences and prompts; options held after the sentence (base)',fontsize=12)
    fig.text(.5,.01,'24 lexical clusters; three constructions averaged within cluster; 95% paired bootstrap CIs.\n'
             'Option mapping occurs after the sentence, so both mappings share the same source prediction prefix.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.09,1,.92])
    for ext in ('png','pdf'):fig.savefig(a.results/f'E12-source-and-answer.{ext}',dpi=180)


if __name__=='__main__':main()
