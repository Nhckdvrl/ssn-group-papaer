"""E69 complete three-family 2x2 measurements, with both original/source regimes."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data import sha

p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=json.loads(a.map.read_text())['reports']
models=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];cells=[('prob','gp'),('improb','gp'),('prob','control'),('improb','control')]
fig,axes=plt.subplots(2,3,figsize=(13,7),sharey=True);fig.subplots_adjust(left=.07,right=.985,bottom=.15,top=.86,hspace=.48,wspace=.17)
for col,m in enumerate(models):
    for row,t in enumerate(['initial','final']):
        ax=axes[row,col]
        for s,offset,color,marker in [('O2',-.09,'#767676','o'),('G2',.09,'#186eae','s')]:
            vals=[d[f'{m}/{s}/{sub}/{cond}/{t}/words/correct'] for sub,cond in cells];y=np.array([v['estimate']*100 for v in vals]);lo=np.array([v['ci95'][0]*100 for v in vals]);hi=np.array([v['ci95'][1]*100 for v in vals])
            ax.errorbar(np.arange(4)+offset,y,yerr=np.vstack([y-lo,hi-y]),fmt=marker,color=color,capsize=3,ms=5,label=s)
        ax.set_title(m if row==0 else '');ax.set_xticks(range(4),['GP\nplausible','GP\nimplausible','cue\nplausible','cue\nimplausible']);ax.set_ylim(-3,103);ax.grid(axis='y',alpha=.18);ax.spines[['top','right']].set_visible(False)
        if col==0:ax.set_ylabel(('Initial relation (No)' if t=='initial' else 'Final relation (Yes)')+'\nAccuracy (%)')
fig.suptitle('Event plausibility still changes source-grounded judgments',y=.99,fontsize=15)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,['Original task (O2)','Explicit source support (G2)'],loc='upper center',bbox_to_anchor=(.5,.965),ncol=2,frameon=False)
fig.text(.5,.025,'45 original published lexical sets; words, both option mappings; 95% cluster bootstrap CI.\nImplausible variants also change entities; effects are not isolated latent-role interventions.',ha='center',fontsize=9)
a.out.mkdir(parents=True,exist_ok=True)
for ext in ['png','pdf']:fig.savefig(a.out/f'plausibility_structure.{ext}',dpi=170)
(a.out/'provenance.json').write_text(json.dumps(dict(map_path=str(a.map),map_sha256=sha(a.map),code_sha256=sha(Path(__file__)),panels='All three registered families and both question targets; original/source regimes; words only, letters/probabilities in full map.'),indent=2)+'\n')
