"""Illustrative E60 NPZ panel; all prespecified windows and both targets/sides."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
r=json.loads(args.report.read_text());names=('Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct')
ops=('CUT_EARLY_QUARTER','CUT_LATE_QUARTER','CUT_EARLY_HALF','CUT_LATE_HALF');x=np.arange(4)
fig,axes=plt.subplots(2,3,figsize=(12,6),sharey=True,sharex=True)
for col,model in enumerate(names):
 for row,condition in enumerate(('gp','control')):
  ax=axes[row,col];ax.axhline(0,color='.6',lw=.8)
  for target,color,offset in [('initial','#2469a6',-.07),('final','#c14c39',.07)]:
   rep=r['reports'][f'{model}/NPZ/{target}/words/same_goldTrue/correct']
   values=[rep['contrasts'][op+'-BASE']['gains'][condition] for op in ops]
   y=np.array([v['estimate'] for v in values])*100
   bounds=np.array([v['ci95'] for v in values])*100
   ax.errorbar(x+offset,y,yerr=np.stack([y-bounds[:,0],bounds[:,1]-y]),color=color,marker='o',capsize=3,lw=1.5,label=f'{target} (n={values[0]["n_clusters"]} clusters)')
  ax.set_ylim(-110,110);ax.set_xticks(x,('early 1/4','late 1/4','early 1/2','late 1/2'));ax.grid(axis='y',alpha=.15)
  ax.spines[['top','right']].set_visible(False)
  if row==0:ax.set_title(model.replace('Meta-Llama-3.1-8B-Instruct','Llama-3.1-8B').replace('gemma-3-12b-it','Gemma-3-12B'))
  if col==0:ax.set_ylabel(('GP' if condition=='gp' else 'Clear cue')+' accuracy gain (pp)')
  if row==1:ax.set_xlabel('Source access removed in these blocks')
  if col==0:ax.legend(fontsize=8,loc='lower left' if row==0 else 'upper left')
fig.suptitle('Initial-question gains accompany loss of final-question accuracy',fontsize=12)
fig.text(.5,.005,'NPZ illustrative panel; all four registered cuts. Words, matching source gold, 95% paired cluster-bootstrap CI.\nSource hidden states unchanged. Complete constructions/readouts/strata remain in the full E60 map.',ha='center',fontsize=8)
fig.tight_layout(rect=(0,.06,1,.96));args.out.mkdir(parents=True,exist_ok=True)
for ext in ('png','pdf'):fig.savefig(args.out/f'source_access_repair_and_damage.{ext}',dpi=180,bbox_inches='tight')
