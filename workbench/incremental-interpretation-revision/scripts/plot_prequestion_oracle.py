"""E54 static scientific figures: absolute repair/damage, never gap alone."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    a=json.loads(args.report.read_text());args.out.mkdir(exist_ok=True,parents=True)
    models=list(a['diagnostics']);short=['Qwen 8B','Gemma 12B','Llama 8B']
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42})
    for target in ('initial','final'):
        fig,axes=plt.subplots(1,2,figsize=(10,7),sharey=True)
        labels=[]
        for readout,ax in zip(('words','letters'),axes):
            labels=[]
            for i,construction in enumerate(('MVRR','NPZ','NPS','NPVP')):
                for j,model in enumerate(models):
                    y=i*4+j;labels.append((y,construction+' / '+short[j]))
                    report=a['reports'][f'{model}/{construction}/{target}/{readout}/same_goldTrue/all/correct']
                    for condition,color,offset in [('gp','#1864ab',-.13),('control','#d9480f',.13)]:
                        stat=report['contrasts']['SOURCE_ALL-CAUSAL']['gains'][condition]
                        if stat['estimate'] is None:continue
                        value=100*stat['estimate'];lo,hi=100*np.array(stat['ci95'])
                        ax.errorbar(value,y+offset,xerr=[[value-lo],[hi-value]],fmt='o',color=color,
                                    markersize=4,capsize=2,label='GP' if condition=='gp' and y==0 else 'Cue' if y==0 else None)
            ax.axvline(0,color='black',lw=.7);ax.set_title(readout.title());ax.grid(axis='x',alpha=.2)
            ax.set_xlabel('Accuracy change (percentage points, 95% cluster CI)')
        axes[0].set_yticks([v for v,label in labels],[label for v,label in labels]);axes[0].invert_yaxis()
        axes[0].legend(loc='lower left');fig.suptitle('E54: source visibility / '+target+' questions')
        fig.tight_layout();stem=args.out/('source_visibility_'+target)
        fig.savefig(stem.with_suffix('.png'),dpi=180);fig.savefig(stem.with_suffix('.pdf'));plt.close(fig)


if __name__=='__main__':main()
