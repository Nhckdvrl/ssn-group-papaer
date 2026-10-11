"""Summarize all completed E118 cases and visualize full functional responses."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
runs={}
for dest in sorted((ROOT/'results/e118').glob('*')):
    if not (dest/'run.json').exists():continue
    r=json.loads((dest/'run.json').read_text());a=json.loads((dest/'analysis.json').read_text())
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    assert len(rows)==r['args']['n'] and all(len(x['conditions'])==33 for x in rows)
    assert all(len(v['z'])==8 for x in rows for v in x['conditions'].values())
    assert r['numeric_max_error']<=.001 and r['edge_self_max_error']<=.001 and r['pristine_source_cache_exact']
    audit={'n_contexts':len(rows),'conditions':33,'queries_per_condition':8,'scores':len(rows)*264,
           'numeric_max_error':r['numeric_max_error'],'edge_self_max_error':r['edge_self_max_error'],
           'script_sha256':r['script_sha256'],'all_conditions_retained':True,
           'review_type':'author completion check; independent audit separate'}
    (dest/'completeness_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    runs[dest.name]={'completion':audit,'gpu_hours':r['gpu_hours'],'analysis':a}
out={'runs':runs,'total_scores':sum(r['completion']['scores'] for r in runs.values()),
     'total_gpu_hours':sum(r['gpu_hours'] for r in runs.values()),'failed_runs':'execution_failures.json; zero science scores excluded'}
(ROOT/'results/e118/wave_summary.json').write_text(json.dumps(out,indent=2)+'\n')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
families=[('qwen3','Qwen3-8B'),('mistral','Mistral-7B-v0.3'),('llama','Llama-3.1-8B')]
modes=['native','label','label_gate']
fig,axes=plt.subplots(3,3,figsize=(10,8),layout='constrained')
maxv=max(abs(v['mean']) for family,_ in families if family+'_confirmation' in runs
         for mode in modes for task in ['food','service'] for f,v in runs[family+'_confirmation']['analysis']['code_effects'][mode][task].items() if f in ['food','service'])
for i,(family,label) in enumerate(families):
    if family+'_confirmation' not in runs:continue
    a=runs[family+'_confirmation']['analysis']
    for j,mode in enumerate(modes):
        ax=axes[i,j]
        data=np.array([[a['code_effects'][mode][task][f]['mean'] for f in ['food','service']] for task in ['food','service']])
        im=ax.imshow(data,cmap='RdBu_r',vmin=-maxv,vmax=maxv)
        for y in range(2):
            for x in range(2):ax.text(x,y,f'{data[y,x]:.3f}',ha='center',va='center',color='white' if abs(data[y,x])>.6*maxv else 'black')
        ax.set_xticks([0,1],['Food response','Service response'],fontsize=8)
        ax.set_yticks([0,1],['B food rule','B service rule'],fontsize=8)
        ax.set_title((label+'\n' if j==0 else '')+{'native':'Native all-source query','label':'A-label cache interchange','label_gate':'Same A-label interchange, A-only query'}[mode],fontsize=9)
fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.8,label='Same-minus-opposite B convention / 2 (nats)')
fig.suptitle('Functional information: entire criterion × feature matrix, new-material confirmation',fontsize=12)
base=ROOT/'results/figs/fig_criterion_code_responses'
fig.savefig(base.with_suffix('.png'),dpi=180);fig.savefig(base.with_suffix('.pdf'));plt.close(fig)
print(json.dumps({k:v for k,v in out.items() if k!='runs'}))
