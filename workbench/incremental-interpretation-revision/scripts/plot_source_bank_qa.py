"""Standalone scientific figure of all E64 construction/target QA source-bank effects."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data import sha
p=argparse.ArgumentParser();p.add_argument('--map',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=json.load(open(a.map));r=d['reports']
models=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];constructions=['MVRR','NPZ','NPS','NPVP']
contrasts=[('FULL_BANK-BASE_BANK','Full source bank','#343434'),('TARGET_BANK-BASE_BANK','Ambiguous words only','#d87828'),('CONTEXT_BANK-BASE_BANK','Other source words only','#3679ab')]
fig,axes=plt.subplots(4,3,figsize=(11,10),sharey=True)
for row,c in enumerate(constructions):
 for col,m in enumerate(models):
  ax=axes[row,col];ax.axhline(0,color='#bbbbbb',linewidth=.8)
  for x,q in enumerate(['initial','final']):
   for offset,(op,label,color) in zip([-.18,0,.18],contrasts):
    cell=r[f'{m}/{c}/gp/{q}/words/same_goldTrue/correct/{op}']
    if cell['estimate'] is None:continue
    v=100*cell['estimate'];lo,hi=[100*z for z in cell['ci95']]
    ax.errorbar(x+offset,v,yerr=[[v-lo],[hi-v]],fmt='o',color=color,capsize=3,markersize=4,label=label if row==0 and col==0 and x==0 else None)
  counts=[r[f'{m}/{c}/gp/{q}/words/same_goldTrue/correct/BASE_BANK']['n_clusters'] for q in ['initial','final']]
  ax.set_xticks([0,1],[f'Initial\nn={counts[0]}',f'Final\nn={counts[1]}']);ax.set_xlim(-.45,1.45);ax.set_ylim(-45,105)
  ax.spines[['top','right']].set_visible(False)
  if col==0:ax.set_ylabel(c+'\nAccuracy change (pp)')
  if row==0:ax.set_title(['Qwen3 8B','Gemma3 12B','Llama3.1 8B'][col])
  if not any(counts):ax.text(.5,.5,'No matched source pairs',transform=ax.transAxes,ha='center',color='#666666',fontsize=9)
fig.suptitle('Fixed source-bank effects on original garden-path questions',fontsize=14,y=.995)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.052),ncol=3,frameon=False)
fig.text(.5,.017,'GP sources; words readout; original gold agrees with G2. Lexical-cluster 95% intervals.\nNPS cue performance is weak; NPVP unavailable. Free-role effects remain pending.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.105,1,.965]);a.out.mkdir(parents=True,exist_ok=True)
for ext in ['png','pdf']:fig.savefig(a.out/('source_bank_QA_effects.'+ext),dpi=180,bbox_inches='tight')
(a.out/'provenance.json').write_text(json.dumps(dict(map_path=str(a.map),map_sha256=sha(a.map),code_sha256=sha(Path(__file__)),scope='All constructions, family panel, targets and three fixed source-bank versus BASE contrasts, GP words/samegold; roles pending.'),indent=2)+'\n')
