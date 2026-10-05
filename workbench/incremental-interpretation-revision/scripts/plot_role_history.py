"""Scientific summary of registered E17/E19/E20, with identical seven source sets."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

p=Path(__file__).resolve().parents[1]/'results'
e17=json.loads((p/'E17-summary.json').read_text());e19=json.loads((p/'E19-summary.json').read_text());e20=json.loads((p/'E20-summary.json').read_text())
left=[e17['contrasts']['episodic_reference/optionboth/D_relation/same'],e17['contrasts']['episodic_reference/optionboth/D_neutral/same']]
right=[e19['contrasts']['all/optionboth/R/D/none/same'],e19['contrasts']['all/optionboth/R/D/reference_only/same'],e20['contrasts']['faithful_order/optionboth/R/D/negate_then_affirm/reference_only']]
assert all(x['pair_ids']==left[0]['pair_ids'] and x['n_sets']==7 for x in left+right)
fig,axes=plt.subplots(1,2,figsize=(9,3.8),constrained_layout=True)
for ax,values,labels,title in [(axes[0],left,['Original activity\npredicate','Neutral entity\nperception'],'Patient preference depends on continuation'),(axes[1],right,['No exclusive\nrole statement','Only reference,\nnot original NP','Not original NP,\nonly reference'],'Explicit role evidence reduces history effect')]:
    means=np.array([x['estimate'] for x in values]);ci=np.array([x['ci95'] for x in values]);xx=np.arange(len(values))
    ax.bar(xx,means,color=['#355f8d','#6d9b79','#b79a61'][:len(values)],width=.58)
    ax.errorbar(xx,means,yerr=np.vstack((means-ci[:,0],ci[:,1]-means)),fmt='none',ecolor='black',capsize=4,lw=1)
    ax.axhline(0,color='gray',lw=.8);ax.set_xticks(xx,labels,fontsize=9);ax.set_title(title,fontsize=10)
    ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('GP minus comma in own-over-other NP preference (bits)',fontsize=9)
axes[1].set_ylabel('GP minus comma in reference-over-own NP preference (bits)',fontsize=9)
fig.suptitle('Frozen Qwen3-8B; same-activity continuation; 7 paired source clusters',fontsize=11)
fig.savefig(p/'E17-E20-role-history.png',dpi=180)
fig.savefig(p/'E17-E20-role-history.pdf')
