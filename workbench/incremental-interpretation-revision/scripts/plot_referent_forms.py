"""Scientific E48 forest figure of preregistered order-averaged cells."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]/'results'
j=json.loads((root/'E48-summary.json').read_text())
cells=j['probability']['cells'];fig,axes=plt.subplots(1,2,figsize=(10,4.8),sharey=True)
forms=[('name','name'),('name','description'),('description','name'),('description','description')]
for ax,inv in zip(axes,('I0','I1')):
    for readout,offset,color,label in [('old',.2,'#2463a6','Same old activity'),('new_same',0,'#c24732','New actor, same action'),('new_different',-.2,'#36866c','New actor, different action')]:
        for y,(fact,target) in enumerate(forms):
            s=cells[f'all/order_average/{fact}/{target}/{inv}/{readout}/activity'];mu=s['estimate'];lo,hi=s['ci95']
            ax.errorbar(mu,y+offset,xerr=[[mu-lo],[hi-mu]],fmt='o',color=color,capsize=3,label=label if y==0 else None)
    ax.axvline(0,color='gray',lw=1);ax.set_title('No inventory' if inv=='I0' else 'Additional names inventory')
    ax.set_xlabel('Role-world difference D (bits)');ax.set_yticks(range(4),[f'{f.title()} → {t.title()}' for f,t in forms]);ax.grid(axis='x',alpha=.15)
axes[0].set_ylabel('Old fact form → readout form');handles,labels=axes[1].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=9)
fig.subplots_adjust(bottom=.18)
fig.suptitle('E48: fixed alias mappings; all 12 families; paired 95% bootstrap CI')
fig.tight_layout(rect=(0,.07,1,1))
for ext in ('png','pdf'):fig.savefig(root/f'E48-referent-form-crossover.{ext}',dpi=180,bbox_inches='tight')
