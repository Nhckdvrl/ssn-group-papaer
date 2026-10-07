"""Complete E65/E66 joint-source panels; every construction, family, and goal."""
import json,hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
cache=Path('/data1/xiangding/work/incremental-interpretation-revision');native=cache/'E65/goal-by-question-map-v1.json';routed=cache/'E66/goal-by-question-source-only-v1.json';n=json.loads(native.read_text())['reports'];r=json.loads(routed.read_text())['reports']
fig,axes=plt.subplots(4,3,figsize=(13,12),sharey=True,constrained_layout=False)
for i,c in enumerate(['MVRR','NPZ','NPS','NPVP']):
 for j,m in enumerate(['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct']):
  ax=axes[i,j];p=f'{m}/{c}/gp/words/joint_all_questions_correct/'
  for k,(label,table,col) in enumerate([('Native: both paths',n,'#1b729a'),('Goal through source only',r,'#c55530')]):
   records=[table[p+g+'-NONE'] for g in ['INITIAL','FINAL']];y=np.array([x['estimate'] for x in records])*100;bounds=np.array([x['ci95'] for x in records])*100;xx=np.arange(2)+(k-.5)*.16
   ax.errorbar(xx,y,yerr=np.maximum(0,np.array([y-bounds[:,0],bounds[:,1]-y])),fmt='o',capsize=4,color=col,label=label)
  ax.axhline(0,color='gray',lw=.8);ax.set_xticks([0,1],['INITIAL goal','FINAL goal']);ax.set_title(c+' / '+['Qwen3','Gemma3','Llama3.1'][j]);ax.set_ylim(-70,75)
  if j==0:ax.set_ylabel('Change in all-Q joint accuracy (pp)')
fig.subplots_adjust(left=.075,right=.995,bottom=.10,top=.90,hspace=.42,wspace=.20)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.966),ncol=2)
fig.suptitle('Advance-question benefits require more than goal-conditioned source states',fontsize=15,y=.995)
fig.supxlabel('All four constructions, three families and both original goal types; published GP sources; words, both option mappings.\n95% lexical-cluster bootstrap CI; no filtering by goal truth. INITIAL/FINAL mark question target, not revision operation.\nE66 changes downstream access while native source states remain unchanged; this does not identify a unique latent parse.',fontsize=9,y=.01)
out=cache/'E66/figures-v1';out.mkdir(exist_ok=True)
for ext in ['png','pdf']:fig.savefig(out/f'goal_paths_joint.{ext}',dpi=160,bbox_inches='tight')
(out/'provenance.json').write_text(json.dumps(dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),source_only_sha256=hashlib.sha256(routed.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
