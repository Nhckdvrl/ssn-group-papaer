#!/usr/bin/env python3
"""Within-consumer paired state effects; never rank models by absolute NLL."""
import argparse,json
from pathlib import Path

def main():
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 a=argparse.ArgumentParser();a.add_argument('--summaries',nargs='+',required=True);a.add_argument('--out-prefix',required=True);args=a.parse_args();rows=[json.loads(Path(p).read_text()) for p in args.summaries];assert all(r['status']=='COMPLETE' for r in rows)
 fig,axs=plt.subplots(1,2,figsize=(11,4),sharey=True);labels={'qwen3_8b':'Qwen3-8B','arcane_8b_dpo':'ArcANE-8B-DPO','qwen3_32b':'Qwen3-32B'};colors=['#4E79A7','#59A14F','#E15759']
 for ax,key,title in zip(axs,['recursive_native minus teacher_forced','recursive_summary minus recursive_native'],['Recursive native prompt − released-prior updates','Ordinary recursive summary − recursive native prompt']):
  ax.axhline(0,color='#777777',lw=1)
  for r,color in zip(rows,colors):
   metric=r['paired_differences'][key]['mean_target_nll'];points=[metric['by_checkpoint'][str(i)] for i in [1,4,8]];ys=[p['book_macro'] for p in points];ci=[p['descriptive_book_bootstrap95'] for p in points]
   ax.errorbar([1,4,8],ys,yerr=[[max(0,y-c[0]) for y,c in zip(ys,ci)],[max(0,c[1]-y) for y,c in zip(ys,ci)]],fmt='o-',capsize=3,color=color,label=labels[r['consumer']])
  ax.set_xticks([1,4,8]);ax.set_xlabel('Completed character appearances');ax.set_title(title,fontsize=10);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
 axs[0].set_ylabel('Paired source-turn NLL difference (nats/token)');axs[1].legend(fontsize=8);fig.suptitle('D-E06 · 29 character trajectories / 8 books · 87 matched next-role turns');fig.text(.5,.015,'Within-model contrasts · descriptive book intervals · negative means better source prediction, not unique role-play correctness',ha='center',fontsize=8);fig.tight_layout(rect=(0,.05,1,.94));p=Path(args.out_prefix);p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(str(p)+'.png',dpi=180);fig.savefig(str(p)+'.pdf')
if __name__=='__main__':main()
