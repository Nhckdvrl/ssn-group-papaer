"""Print-readable rendering of all E125 confirmation phase cells; no new inference."""
import csv, hashlib, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/e125/summary.json'
def main():
 summary=json.loads(SOURCE.read_text());rows=[]
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(1,3,figsize=(6.3,2.5),sharey=True)
 families=[('qwen3','Qwen3-8B'),('mistral','Mistral-7B'),('llama','Llama-3.1-8B')]
 rosters=[('true','#1768ac'),('unrelated','#b86b26'),('swapped','#aa3453')]
 for ax,(family,label) in zip(axes,families):
  item=summary['runs'][family+'_confirmation'];assert item['analysis']['n_contexts']==32
  a=item['analysis']['phase_accuracy']
  for j,(roster,color) in enumerate(rosters):
   x=np.arange(4)+(j-1)*.07
   for metric,marker,linestyle in [('both','o','-'),('candidate','x','--')]:
    vals=[a[f'{roster}_f{f}r{r}'][metric] for f,r in [(0,0),(1,0),(0,1),(1,1)]]
    y=np.array([v['mean'] for v in vals])*100
    if metric=='both':
     err=np.array([[v['mean']-v['ci95'][0] for v in vals],[v['ci95'][1]-v['mean'] for v in vals]])*100
     ax.errorbar(x,y,yerr=err,marker=marker,color=color,lw=.85,ms=3,capsize=1.6)
    else:ax.plot(x,y,marker=marker,ls=linestyle,color=color,lw=.75,ms=3,alpha=.65)
    for (f,r),v in zip([(0,0),(1,0),(0,1),(1,1)],vals):
     rows.append({'model':label,'roster':roster,'formation':f,'reading':r,'readout':metric,'mean':v['mean']*100,'ci_low':v['ci95'][0]*100,'ci_high':v['ci95'][1]*100})
  ax.set_xticks(range(4),['00','10','01','11']);ax.set_xlabel('Formation / reading access')
  ax.set_title(label,fontsize=8.5);ax.set_ylim(0,102);ax.set_yticks([0,50,100]);ax.grid(axis='y',alpha=.2,lw=.6)
 axes[0].set_ylabel('Mean accuracy (%)')
 handles=[Line2D([0],[0],color=c,lw=1,label=n.capitalize()) for n,c in rosters]
 handles += [Line2D([0],[0],color='#333333',marker='o',ms=3,lw=.8,label='Full vocabulary'),Line2D([0],[0],color='#333333',marker='x',ms=3,lw=.8,ls='--',label='Own-word candidates')]
 fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.51,.015),ncol=5,frameon=False,fontsize=7,handlelength=1,columnspacing=1)
 fig.subplots_adjust(left=.09,right=.985,top=.88,bottom=.31,wspace=.22)
 base=ROOT/'results/figs/fig_public_source_schema_summary'
 for ext in ['png','pdf']:fig.savefig(base.with_suffix('.'+ext),dpi=220,bbox_inches='tight')
 p=ROOT/'results/e125/main_figure_values.csv'
 with p.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
 (ROOT/'results/e125/main_figure_manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'csv_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'points':len(rows),'scope':'All E125 confirmation phase cells, three models/rosters, four F/R access conditions, candidate and full output; full-output error bars show existing 95% context-bootstrap intervals; candidate curves retain existing means. Original wide rendering remains in results/figs; all phase cells shown here are also tabulated in Appendix H.','new_scientific_inference':False},indent=2)+'\n')
if __name__=='__main__':main()
