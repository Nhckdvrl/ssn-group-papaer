"""E76 fixed full panel plot, only after complete-map SHA closure."""
import argparse
import json
from pathlib import Path
from data import sha


def plot(root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    path=root/'event-first-draft-map-v1.json';complete=json.loads((root/'complete-map-v1.json').read_text())
    assert complete['all_models_complete'] and complete['map_sha256']==sha(path)
    report=json.loads(path.read_text());index={(x['model'],x['construction'],x['condition'],x['readout'],x['target'],x['metric'],x['operation']):x for x in report['panels']}
    models=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];constructs=['MVRR','NPZ','NPS','NPVP'];directory=root/'figures-v1';directory.mkdir(exist_ok=True)
    for readout in ['words','letters']:
        for metric in ['correct','p_correct']:
            targets=['initial','final','joint_all_questions'] if metric=='correct' else ['initial','final']
            fig,axes=plt.subplots(len(targets),3,figsize=(13,3.2*len(targets)),squeeze=False,sharey=True)
            for column,model in enumerate(models):
                for row,target in enumerate(targets):
                    ax=axes[row,column];ax.axhline(0,color='.5',lw=.7)
                    for k,(op,cond,color,marker) in enumerate([('FREE-minus-DIRECT','gp','#2864a0','o'),('EVENT_FIRST-minus-DIRECT','gp','#c06817','s'),('FREE-minus-DIRECT','control','#2864a0','o'),('EVENT_FIRST-minus-DIRECT','control','#c06817','s')]):
                        for i,construct in enumerate(constructs):
                            p=index[model,construct,cond,readout,target,metric,op]
                            if p['value'] is None:continue
                            v=100*p['value'];lo,hi=[100*x for x in p['CI95']];label=('Free / ' if op.startswith('FREE') else 'Event first / ')+('GP' if cond=='gp' else 'cue') if i==0 and row==0 and column==0 else None
                            ax.errorbar(i+(k-1.5)*.15,v,yerr=[[v-lo],[hi-v]],color=color,fmt=marker,mfc=color if cond=='gp' else 'white',capsize=2,ms=4,lw=.8,label=label)
                    ax.set_xticks(range(4),constructs);ax.set_ylim(-100,100);ax.grid(axis='y',alpha=.15)
                    if row==0:ax.set_title(model)
                    if column==0:ax.set_ylabel(target+'\nChange versus direct QA (pp)')
            handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=4,frameon=False,bbox_to_anchor=(.5,.965))
            fig.suptitle('Original-source QA after model-generated relational drafts — '+readout+' / '+metric,y=.995)
            fig.tight_layout(rect=(0,0,1,.925));stem=directory/('draft_to_QA_'+readout+'_'+metric)
            fig.savefig(stem.with_suffix('.png'),dpi=180);fig.savefig(stem.with_suffix('.pdf'));plt.close(fig)
    (directory/'provenance.json').write_text(json.dumps(dict(map_sha256=sha(path),plot_code_sha256=sha(Path(__file__)),policy='All families, constructions, two readouts and both source conditions; no effect-based selection.'),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);plot(p.parse_args().root)
