"""Standalone E80 figures; all models/constructions and cue harms retained."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def plot(root):
    assert json.loads((root/'complete-map-v1.json').read_text())['all_models_complete']
    ps=json.loads((root/'grammar-trust-map-v1.json').read_text())['panels']
    idx={(p['model'],p['construction'],p['condition'],p['readout'],p['target'],p['metric'],p['operation']):p for p in ps}
    models=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct']
    constructs=['MVRR','NPZ','NPS','NPVP']; out=root/'figures-v1';out.mkdir(exist_ok=True)
    ops=[('TRUST-minus-NATIVE','#0072B2',-.13),('NOISY-minus-NATIVE','#D55E00',.13)]
    metrics=[('initial','p_correct','Initial: normalized correct-answer probability'),
             ('final','p_correct','Final: normalized correct-answer probability'),
             ('joint_all_questions','correct','All original questions correct')]
    for ro in ['words','letters']:
        fig,axes=plt.subplots(3,3,figsize=(14,9),sharex=True,sharey='col')
        for i,m in enumerate(models):
            for k,(target,metric,title) in enumerate(metrics):
                ax=axes[i,k];ax.axhline(0,color='.65',lw=.8)
                for j,ct in enumerate(constructs):
                    for op,color,offset in ops:
                        for cond,extra,face in [('gp',-.035,color),('control',.035,'white')]:
                            p=idx[m,ct,cond,ro,target,metric,op];v=p['value']*100;low,high=[x*100 for x in p['CI95']]
                            ax.errorbar(j+offset+extra,v,yerr=[[max(0,v-low)],[max(0,high-v)]],fmt='o',
                                        ms=4,color=color,mfc=face,mec=color,capsize=2,lw=.8)
                ax.set_xticks(range(4),constructs);ax.grid(axis='y',alpha=.15)
                if i==0:ax.set_title(title,fontsize=10)
                if k==0:ax.set_ylabel(m+'\nChange (percentage points)',fontsize=9)
        handles=[Line2D([],[],color=color,marker='o',lw=.8,label=op.replace('-minus-',' − ')) for op,color,_ in ops]
        handles += [Line2D([],[],color='.3',marker='o',mfc=face,lw=0,label=label)
                    for face,label in [('.3','GP'),('white','Cue control')]]
        fig.legend(handles=handles,loc='lower center',ncol=4,frameon=False)
        fig.suptitle('E80 input reliability: '+ro+' readout; original source gold; 95% lexical-cluster bootstrap CI')
        fig.tight_layout(rect=(0,.045,1,.96))
        for ext in ['png','pdf']:fig.savefig(out/f'grammar_trust_{ro}.{ext}',dpi=180)
        plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);plot(p.parse_args().root)
