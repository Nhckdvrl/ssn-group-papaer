"""E65 complete four-construction goal-by-target map, no success-panel selection."""
import json,hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
root=Path('/data1/xiangding/work/incremental-interpretation-revision/E65');path=root/'goal-by-question-map-v1.json';reports=json.loads(path.read_text())['reports']
fig,axes=plt.subplots(4,3,figsize=(14,12),constrained_layout=True)
for i,c in enumerate(['MVRR','NPZ','NPS','NPVP']):
 for j,m in enumerate(['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct']):
  ax=axes[i,j];arr=np.zeros((2,2));texts={}
  for g,goal in enumerate(['INITIAL','FINAL']):
   for t,target in enumerate(['initial','final']):
    r=reports[f'{m}/{c}/gp/{target}/words/same_goldTrue/correct/{goal}-NONE'];arr[g,t]=100*r['estimate'];texts[g,t]=f"{arr[g,t]:+.1f}\n[{100*r['ci95'][0]:+.1f}, {100*r['ci95'][1]:+.1f}]"
  im=ax.imshow(arr,cmap='RdBu',vmin=-60,vmax=60,aspect='auto')
  for (g,t),s in texts.items():ax.text(t,g,s,ha='center',va='center',fontsize=10,color='white' if abs(arr[g,t])>35 else 'black')
  ax.set_xticks([0,1],['Later initial Q','Later final Q']);ax.set_yticks([0,1],['Initial goal','Final goal']);ax.set_title(c+' / '+['Qwen3','Gemma3','Llama3.1'][j])
fig.suptitle('E65: advance question does not yield uniform cross-relation repair',fontsize=15)
fig.colorbar(im,ax=axes,shrink=.65,label='Accuracy change versus no advance question (percentage points)')
fig.supxlabel('Published GP sentences; matching source gold; words, both option mappings; 95% lexical-cluster bootstrap CI.\nAll four constructions and three families. Complete cue/letters/probability/joint panels remain in the full map.',fontsize=10)
out=root/'figures-v1';out.mkdir(exist_ok=True)
for ext in ['png','pdf']:fig.savefig(out/f'goal_by_question_map.{ext}',dpi=160)
(out/'provenance.json').write_text(json.dumps(dict(full_path=str(path),full_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
