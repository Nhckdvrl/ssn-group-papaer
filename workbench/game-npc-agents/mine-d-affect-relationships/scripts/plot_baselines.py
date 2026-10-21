#!/usr/bin/env python3
"""Research plots for completed reproduction scores, with corpus-level observations."""
import argparse,json
from pathlib import Path

def main():
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 a=argparse.ArgumentParser();a.add_argument('--phase-summary',required=True);a.add_argument('--out-prefix',required=True);args=a.parse_args();data=json.loads(Path(args.phase_summary).read_text());modes=['base','raw_profile','naive_rewrite','phase_tree'];labels=['Base','Raw profile','Rewrite','PHASE-Tree'];corpora=['Friends','TheOffice','HPD','StarTrek_TNG'];colors=['#4E79A7','#F28E2B','#59A14F','#B07AA1']
 fig,axs=plt.subplots(1,2,figsize=(10,4),sharey=True)
 for ax,metric,title in zip(axs,['character_score','semantic_score'],['Character consistency','Contextual coherence']):
  for corpus,c in zip(corpora,colors):ax.plot(range(4),[data['groups'][m]['by_corpus'][corpus][metric] for m in modes],'.-',lw=1,alpha=.7,label=corpus,color=c)
  ax.plot(range(4),[data['groups'][m]['macro'][metric] for m in modes],'o-',color='#222222',lw=2.4,label='Corpus macro',zorder=5)
  ax.set_xticks(range(4),labels);ax.set_ylim(1,5);ax.set_title(title);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
 axs[0].set_ylabel('Native rubric score (1–5)');axs[1].legend(fontsize=8,loc='lower right')
 fig.suptitle('LongEvoRoleBench: four native text conditions',fontsize=13)
 fig.text(.5,.01,'64 paired questions · Qwen2.5-7B actor · local Qwen3-32B judge · corpus-level lines',ha='center',fontsize=9)
 fig.tight_layout(rect=(0,.04,1,.94));prefix=Path(args.out_prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
 fig.savefig(str(prefix)+'.png',dpi=180);fig.savefig(str(prefix)+'.pdf')
if __name__=='__main__':main()
