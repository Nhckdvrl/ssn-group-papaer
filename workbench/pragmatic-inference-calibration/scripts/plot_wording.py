"""E59 prospective readouts; exported scientific figure, no new comparisons."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from run_followup_queue import ROOT

p=Path(__file__).resolve().parents[1]/'results/E59-wording-summary.json';d=json.loads(p.read_text())
out=ROOT/'figures';out.mkdir(exist_ok=True)
paths=[out/'E59-wording-stage.png',out/'E59-wording-stage.pdf'];assert not any(p.exists() for p in paths)
left='OLMo-2-1124-13B-SFT';right='OLMo-2-1124-13B-DPO';delta=d['paired_stage_changes'][left+' -> '+right]
x=np.arange(3);labels=['Original W0','Paraphrase W1','Paraphrase W2'];colors=['#264653','#2a9d8f','#e76f51']
fig,axes=plt.subplots(1,3,figsize=(12,4.4),layout='constrained')
for ax,key,title in zip(axes[:2],['four_way_brier','definite_probability'],['Change in distance to human ratings','Change in definite interpretation mass']):
 vals=[delta[f'W{i}/common-chat/full_logprob'][key] for i in range(3)]
 means=np.array([v['mean'] for v in vals]);ci=np.array([v['ci95'] for v in vals]).T
 for j in range(3):ax.errorbar(x[j],means[j],yerr=np.array([[means[j]-ci[0,j]],[ci[1,j]-means[j]]]),fmt='o',color=colors[j],capsize=4)
 ax.axhline(0,color='#888888',lw=.8);ax.set_xticks(x,labels,rotation=20,ha='right');ax.set_ylabel('DPO minus SFT');ax.set_title(title,fontsize=10)
ax=axes[2]
for j in range(3):
 v=[d['models'][m]['null_readout'][f'W{j}/common-chat']['full_logprob']['conditional_probs'][1] for m in [left,right]]
 ax.plot([0,1],v,'o-',color=colors[j],label=labels[j])
ax.set_xticks([0,1],['SFT','DPO']);ax.set_ylim(0,1);ax.set_ylabel('P(probably meant Yes | four candidates)');ax.set_title('No-dialogue response prior',fontsize=10);ax.legend(frameon=False,fontsize=8)
for ax in axes:
 ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
fig.suptitle('OLMo2-13B: wording stability does not identify pragmatic competence',fontsize=12)
fig.supxlabel('IQAP 150 development dialogues; common chat; full candidate + terminal likelihood.\nError bars: paired item bootstrap 95% CI; no training-seed or isolated DPO causal claim.',fontsize=9)
for p in paths:fig.savefig(p,dpi=180)
manifest=Path(__file__).resolve().parents[1]/'results/E59-figure-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'source_summary_sha256':hashlib.sha256((Path(__file__).resolve().parents[1]/'results/E59-wording-summary.json').read_bytes()).hexdigest(),
    'artifacts':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},indent=2)+'\n')
print(json.dumps([str(p) for p in paths]))
