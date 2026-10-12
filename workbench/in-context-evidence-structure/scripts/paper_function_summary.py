"""Readable main-paper view of E123; full six-policy plots stay in Appendix F.

Uses existing confirmed bootstrap estimates without new fitting or selection.
"""
import csv, hashlib, json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/e123/wave_summary.json'
FAMILIES=[('qwen3','Qwen3-8B'),('mistral','Mistral-7B'),('llama','Llama-3.1-8B'),('qwen14','Qwen3-14B')]
POLICIES=[('normal','Native','#555555'),('answer_cross_off','Selective answer restriction','#2166ac'),('all_cross_off','All cross-source restriction','#d6604d')]
def main():
 summary=json.loads(SOURCE.read_text()); rows=[]
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(1,2,figsize=(6.3,2.85),sharey=True,gridspec_kw={'width_ratios':[1.25,1]})
 for i,(family,label) in enumerate(FAMILIES):
  item=summary['runs'][family+'_confirmation']; assert item['audit']['contexts']==32
  y=3-i
  for j,(policy,name,color) in enumerate(POLICIES):
   stat=item['full_output']['policy_accuracy'][f'shared_{policy}_native']['both']
   value=100*stat['mean'];lo,hi=np.array(stat['ci95'])*100
   axes[0].errorbar(value,y+(1-j)*.17,xerr=[[value-lo],[hi-value]],fmt='o',color=color,ms=3.5,capsize=2,lw=.9,label=name if i==0 else None)
   rows.append({'model':label,'namespace':'shared','policy':policy,'query_scope':'full-source','readout':'full_vocabulary','mean':value,'ci_low':lo,'ci_high':hi})
  for source,kind,marker,color,offset in [('analysis','candidate','o','#2166ac',.1),('full_output','full_vocabulary','x','#222222',-.1)]:
   stat=item[source]['policy_accuracy']['far_all_cross_off_native']['both']
   value=100*stat['mean'];lo,hi=np.array(stat['ci95'])*100
   axes[1].errorbar(value,y+offset,xerr=[[value-lo],[hi-value]],fmt=marker,color=color,ms=4,capsize=2,lw=.9,label='Own-word candidates' if source=='analysis' and i==0 else 'Full vocabulary' if i==0 else None)
   rows.append({'model':label,'namespace':'separate','policy':'all_cross_off','query_scope':'full-source','readout':kind,'mean':value,'ci_low':lo,'ci_high':hi})
 for ax in axes:
  ax.set_ylim(-.42,3.48);ax.grid(axis='y',color='#eeeeee',lw=.6);ax.set_axisbelow(True)
  ax.set_xlabel('Mean rule-use accuracy (%)');ax.set_xticks([50,75,100]);ax.set_xlim(47,102)
  ax.axvline(50,color='#bbbbbb',ls=':',lw=.7)
 axes[0].set_yticks(range(4),[label for _,label in reversed(FAMILIES)])
 axes[0].set_title('(a) Shared words',fontsize=9)
 axes[1].set_title('(b) Separate words\nAll cross-source restriction',fontsize=9)
 fig.legend(*axes[0].get_legend_handles_labels(),loc='lower left',bbox_to_anchor=(.02,.015),frameon=False,fontsize=7.2,handlelength=1)
 fig.legend(*axes[1].get_legend_handles_labels(),loc='lower left',bbox_to_anchor=(.62,.055),frameon=False,fontsize=7.2,handlelength=1)
 fig.subplots_adjust(left=.155,right=.985,top=.84,bottom=.35,wspace=.17)
 base=ROOT/'results/figs/fig_natural_source_function_summary'
 for ext in ['pdf','png']:fig.savefig(base.with_suffix('.'+ext),dpi=220,bbox_inches='tight')
 csvpath=ROOT/'results/e123/main_figure_values.csv'
 with csvpath.open('w',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
 (ROOT/'results/e123/main_figure_manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'csv_sha256':hashlib.sha256(csvpath.read_bytes()).hexdigest(),'points':len(rows),'scope':'Presentation of existing E123 confirmed estimates, n32; full-source reading, both-source context averages. Panel a: three shared-word formation policies. Panel b: all-cross restriction with separate words, candidate vs full output. All six policies and both namespaces retained in Appendix F.','new_scientific_inference':False},indent=2)+'\n')
if __name__=='__main__':main()
