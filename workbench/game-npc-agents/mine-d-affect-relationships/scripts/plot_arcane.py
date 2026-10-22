#!/usr/bin/env python3
"""Plot completed per-metric ArcANE means without pooling different cohorts."""
import argparse,json
from pathlib import Path

def main():
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 a=argparse.ArgumentParser();a.add_argument('--summary',required=True);a.add_argument('--out-prefix',required=True);args=a.parse_args();d=json.loads(Path(args.summary).read_text());groups=d['groups'];modes=[m for m in ['vanilla','arc','summary','state_summary','state_summary_step','prefix_memory'] if any(g.endswith('|'+m) for g in groups)];models=[('Qwen/Qwen3-8B','Qwen3-8B','#4E79A7'),('arcane-8B-dpo','ArcANE-8B-DPO','#59A14F'),('Qwen/Qwen3-32B','Qwen3-32B','#E15759')];fig,axs=plt.subplots(1,2,figsize=(14 if len(modes)>3 else 10,4.5),sharey=True)
 for ax,metric,title in zip(axs,['apf','ptf'],['Action phase fidelity','Complete trajectory fidelity']):
  for model,label,color in models:
   if model+'|'+modes[0] not in groups:continue
   available=[m for m in modes if model+'|'+m in groups];rs=[groups[model+'|'+m] for m in available];ys=[r['metrics'][metric] for r in rs];cis=[r['metric_descriptive_novel_bootstrap95'][metric] for r in rs];x=[modes.index(m) for m in available];ax.errorbar(x,ys,yerr=[[max(0,y-c[0]) for y,c in zip(ys,cis)],[max(0,c[1]-y) for y,c in zip(ys,cis)]],fmt='o-',color=color,lw=2,capsize=3,label=label)
   books=sorted(set.intersection(*(set(r['by_novel']) for r in rs)))
   for book in books:ax.plot(x,[r['by_novel'][book][metric] for r in rs],'-',color=color,lw=.7,alpha=.16)
  ax.set_xticks(range(len(modes)),[{'vanilla':'Identity +\nsource unit','arc':'Official\nArc','summary':'Recent plot\nsummary','state_summary':'Character state\nQwen32 teacher','state_summary_step':'Character state\nStep5 teacher','prefix_memory':'Full source prefix\nordinary memory'}[m] for m in modes]);ax.set_ylim(0,100);ax.set_title(title);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
 axs[0].set_ylabel('Native rubric points');axs[1].legend(fontsize=8,loc='lower right')
 cohort='64 complete probes / 205 phase trials' if d['experiment']=='D-E01' else '25 matched complete probes / 81 phase trials'
 if d['experiment']=='D-E09':cohort='6 characters / 15 complete probes / 47 phase trials'
 qualifier=' [legacy Monte source mismatch]' if d['experiment']=='D-E03' else ''
 fig.suptitle(d['experiment']+' · '+cohort+qualifier,fontsize=13);fig.text(.5,.01,'Six-book macro · descriptive book bootstrap intervals · local Qwen3-32B judge · rubric points, not accuracy',ha='center',fontsize=9);fig.tight_layout(rect=(0,.05,1,.94));p=Path(args.out_prefix);p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(str(p)+'.png',dpi=180);fig.savefig(str(p)+'.pdf')
if __name__=='__main__':main()
