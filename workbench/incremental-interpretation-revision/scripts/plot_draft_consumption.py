"""E77 fixed all-family/construction paired source-consumption figures."""
import argparse,json
from pathlib import Path
from data import sha

def plot(root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    p=root/'retire-original-map-v1.json';c=json.loads((root/'complete-map-v1.json').read_text());assert c['all_models_complete'] and c['map_sha256']==sha(p)
    r=json.loads(p.read_text());ix={(x['model'],x['construction'],x['condition'],x['readout'],x['draft'],x['target'],x['metric'],x['operation']):x for x in r['panels']};models=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];cts=['MVRR','NPZ','NPS','NPVP'];out=root/'figures-v1';out.mkdir(exist_ok=True)
    for ro in ['words','letters']:
        fig,axes=plt.subplots(3,3,figsize=(13,10),sharey=True)
        for j,model in enumerate(models):
            for i,(target,metric) in enumerate([('initial','p_correct'),('final','p_correct'),('joint_all_questions','correct')]):
                ax=axes[i,j];ax.axhline(0,color='.5',lw=.7)
                for k,(draft,cond,color,marker) in enumerate([('FREE','gp','#2864a0','o'),('EVENT_FIRST','gp','#c06817','s'),('FREE','control','#2864a0','o'),('EVENT_FIRST','control','#c06817','s')]):
                    for n,ct in enumerate(cts):
                        x=ix[model,ct,cond,ro,draft,target,metric,'CUT-minus-NATIVE'];v=100*x['value'];lo,hi=[100*y for y in x['CI95']];z=n+(k-1.5)*.15
                        ax.plot([z,z],[lo,hi],color=color,lw=.9);ax.plot(z,v,marker,color=color,mfc=color if cond=='gp' else 'white',ms=4,label=(draft+' / '+cond) if n==0 and i==0 and j==0 else None)
                ax.set_xticks(range(4),cts);ax.set_ylim(-100,100);ax.grid(axis='y',alpha=.15)
                if i==0:ax.set_title(model)
                if j==0:ax.set_ylabel(target+'\nCUT − native (pp)')
        hs,ls=axes[0,0].get_legend_handles_labels();fig.legend(hs,ls,loc='upper center',bbox_to_anchor=(.5,.96),ncol=4,frameon=False);fig.suptitle('E77: stop original-source consumption after relational draft — '+ro,y=.995);fig.tight_layout(rect=(0,0,1,.925))
        for suffix in ['png','pdf']:fig.savefig(out/('source_consumption_'+ro+'.'+suffix),dpi=180)
        plt.close(fig)
    (out/'manifest.json').write_text(json.dumps(dict(map_sha256=sha(p),code_sha256=sha(Path(__file__)),scope='All families/constructs/both source conditions and readouts, two draft types, three primary relational targets.'),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);plot(p.parse_args().root)
