"""Standalone E91 figure from registered summary metrics; no new selection."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

base=Path(__file__).resolve().parents[1]
a=json.loads((base/'results/e91/qwen3_confirmation/analysis.json').read_text())
plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'ps.fonttype':42})
fig,ax=plt.subplots(1,2,figsize=(10.1,4.1),gridspec_kw={'width_ratios':[1.15,1]})
modes=['shared_native','far_native','shared_gate','far_gate']
labels=['Shared labels\nNative read','Separate labels\nNative read','Shared labels\nRead A only','Separate labels\nRead A only']
for i,k in enumerate(modes):
    x=a['rule_dependence'][k]['absolute']; m=x['mean']; lo,hi=x['ci95']
    ax[0].bar(i,m,color='#537796' if k.startswith('shared') else '#C68A42',width=.68)
    ax[0].errorbar(i,m,yerr=[[m-lo],[hi-m]],fmt='none',color='black',capsize=4)
ax[0].set_xticks(range(4),labels,fontsize=9)
ax[0].set_ylabel('Mean |source B rule effect| (nats)')
ax[0].set_title('Label separation affects indirect influence too')
ax[0].set_ylim(bottom=0)
keys=['shared_gate','key_patch','value_patch','far_gate']
labels=['Shared K/V','Far K only','Far V only','Far K/V']
for i,k in enumerate(keys):
    x=a['rule_dependence'][k]['absolute']; m=x['mean']; lo,hi=x['ci95']
    ax[1].bar(i,m,color=['#537796','#8CA394','#BCA184','#C68A42'][i],width=.68)
    ax[1].errorbar(i,m,yerr=[[m-lo],[hi-m]],fmt='none',color='black',capsize=4)
ax[1].set_xticks(range(4),labels,fontsize=9)
ax[1].set_title("Change only A's cached states; query reads A only")
ax[1].set_ylim(bottom=0)
for aa in ax:
    aa.spines[['top','right']].set_visible(False)
    aa.grid(axis='y',alpha=.18);aa.set_axisbelow(True)
fig.suptitle("B's label vocabulary changes rule influence carried by A",fontsize=13)
fig.text(.5,.015,'48 fresh contexts; paired context bootstrap 95% CI. A raw tokens and output labels stay fixed.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.045,1,.92))
out=base/'results/figs/e91_label_namespace_and_inherited_rule'
fig.savefig(out.with_suffix('.png'),dpi=180)
fig.savefig(out.with_suffix('.pdf'))
print(out)
