"""E78 all-family absolute accuracies/probabilities, only from a closed whole map."""
import argparse,json
from pathlib import Path
from data import sha
from stronger_draft_pipeline import MODELS

def plot(root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    p=root/'stronger-draft-map-v1.json';c=json.loads((root/'complete-map-v1.json').read_text());assert c['all_models_complete'] and c['map_sha256']==sha(p)
    r=json.loads(p.read_text());ix={(x['model'],x['construction'],x['condition'],x['readout'],x['target'],x['metric'],x['operation']):x for x in r['panels']};cts=['MVRR','NPZ','NPS','NPVP'];out=root/'figures-v1';out.mkdir(exist_ok=True)
    for ro in ['words','letters']:
        fig,axes=plt.subplots(3,3,figsize=(14,10),sharey=True)
        for j,model in enumerate(MODELS):
            for i,(target,metric) in enumerate([('initial','p_correct'),('final','p_correct'),('joint_all_questions','correct')]):
                ax=axes[i,j]
                for k,(op,color,marker) in enumerate([('DIRECT','#2864a0','o'),('SOURCE_AND_DRAFT','#c06817','s'),('DRAFT_ONLY','#318450','^')]):
                    for z,cond in enumerate(['gp','control']):
                        for n,ct in enumerate(cts):
                            x=ix[model,ct,cond,ro,target,metric,op];v=100*x['value'];lo,hi=[100*y for y in x['CI95']];pos=n+(2*k+z-2.5)*.12
                            ax.plot([pos,pos],[lo,hi],color=color,lw=.9);ax.plot(pos,v,marker,color=color,mfc=color if cond=='gp' else 'white',ms=4,label=(op+' / '+cond) if n==0 and i==0 and j==0 else None)
                ax.set_xticks(range(4),cts);ax.set_ylim(-3,103);ax.grid(axis='y',alpha=.15)
                if i==0:ax.set_title(model)
                if j==0:ax.set_ylabel(target+'\nOriginal-source gold performance (%)')
        hs,ls=axes[0,0].get_legend_handles_labels();fig.legend(hs,ls,loc='upper center',bbox_to_anchor=(.5,.96),ncol=3,frameon=False);fig.suptitle('E78: strong-model original-source versus draft consumption — '+ro,y=.995);fig.tight_layout(rect=(0,0,1,.91))
        for suffix in ['png','pdf']:fig.savefig(out/('stronger_draft_'+ro+'.'+suffix),dpi=180)
        plt.close(fig)
    (out/'manifest.json').write_text(json.dumps(dict(map_sha256=sha(p),code_sha256=sha(Path(__file__)),scope='All strong families/constructions/source conditions/readouts and all three original-gold pipelines; no effect-based selection.'),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);plot(p.parse_args().root)
