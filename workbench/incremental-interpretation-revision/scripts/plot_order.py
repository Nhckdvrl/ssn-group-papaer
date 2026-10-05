"""Standalone scientific figure from E03 FP32 registered paired estimates."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root=Path(__file__).resolve().parents[1]/'results'
s=json.loads((root/'E03-fp32-summary.json').read_text())
keys=[(d,i,a) for d in ('reg','rev') for i in ('raw','chat') for a in ('none','assertion')]
fig,ax=plt.subplots(figsize=(8.5,5.2),layout='constrained')
for query,color,offset,label in [('reg','#2166ac',-.12,'Sentence before question'),('rev','#b2182b',.12,'Question before sentence')]:
    stats=[s['effects'][f'correct/{demo}/{query}/{interface}/{instr}/lingering'] for demo,interface,instr in keys]
    values=np.array([v['estimate']*100 for v in stats])
    ci=np.array([v['ci95'] for v in stats])*100
    ax.errorbar(values,np.arange(len(keys))+offset,xerr=np.stack([values-ci[:,0],ci[:,1]-values]),
                fmt='o',color=color,label=label,capsize=3,markersize=5)
ax.axvline(0,color='0.3',lw=1)
ax.set_yticks(np.arange(len(keys)),[f'Demo {d} / {i} / {a}' for d,i,a in keys])
ax.invert_yaxis();ax.set_xlabel('GP-question accuracy: nonGP − GP (percentage points)')
ax.set_title('Qwen3-8B: query order reverses the condition effect\nFixed demo bundle; full FP32; 69 paired lexical sets; 95% cluster bootstrap CI',fontsize=11)
ax.legend(loc='lower center',bbox_to_anchor=(.5,-.27),ncol=2,fontsize=9);ax.spines[['right','top']].set_visible(False)
fig.savefig(root/'E03-order-effects.png',dpi=200)
fig.savefig(root/'E03-order-effects.pdf')
