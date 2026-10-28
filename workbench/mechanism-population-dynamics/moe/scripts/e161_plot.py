"""Plot complete predeclared E161 outcomes without reclassifying any output."""
import json
import hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]/'results/e161'
NAMES = ('P', 'A', 'B')
PATHS = ('R', 'S', 'R+S', 'Attn')
OUTCOMES = ('original', 'entity_hybrid', 'relation_hybrid', 'full_donor', 'other')
LABELS = ('Original', 'Entity hybrid', 'Relation hybrid', 'Full donor', 'Other')
COLORS = ('#5479a6', '#d29832', '#b85c61', '#42918a', '#d1d4d8')
FOOT = ('Whole terminal paths across 16 layers; earlier native positions fixed. 24 countries × 2 relations.\n'
        'All inputs and all four paths retained; first-token readout. Country CIs describe inputs, not training seeds.')


def save(fig, name):
    output = ROOT/'figures'
    output.mkdir(exist_ok=True)
    for ext in ('png', 'pdf'):
        fig.savefig(output/(name+'.'+ext), dpi=180, bbox_inches='tight')
    plt.close(fig)


def main():
    summary_path = ROOT/'summary.json'
    s = json.loads(summary_path.read_text())
    if s['status'] != 'complete' or s['models'] != list(NAMES) or s['paths'] != ['R','S','RS','A']:
        raise ValueError('Only the complete frozen E161 population is supported')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                         'axes.spines.top':False,'axes.spines.right':False})
    rates = np.array([s['all']['top1_'+o]['point'] for o in OUTCOMES])
    if rates.shape != (5,3,4) or not np.allclose(rates.sum(0), 1):
        raise ValueError('Invalid outcome partition')
    fig, axes = plt.subplots(2,3,figsize=(12,8),gridspec_kw={'height_ratios':[1.2,1]})
    pref = s['preferences']['relation_hybrid_minus_full_donor_all_paths']
    point = np.asarray(pref['point']); ci = np.asarray(pref['ci95'])
    for i, name in enumerate(NAMES):
        ax = axes[0,i]; bottom = np.zeros(4)
        for k, (label, color) in enumerate(zip(LABELS, COLORS)):
            ax.bar(np.arange(4), rates[k,i], .7, bottom=bottom, color=color,
                   edgecolor='white', linewidth=.5, label=label)
            for x, value, offset in zip(range(4), rates[k,i], bottom):
                if value >= .07:
                    ax.text(x, offset+value/2, f'{value:.0%}',ha='center',va='center',fontsize=9)
            bottom += rates[k,i]
        ax.set_title(name, fontweight='bold');ax.set_xticks(range(4),PATHS);ax.set_ylim(0,1.02)
        if i == 0:ax.set_ylabel('Fraction of full-vocabulary top-1 outcomes')
        ax = axes[1,i]
        for k in range(4):
            ax.plot(point[i,k], k, 'o', color='#346d86')
            ax.hlines(k,ci[i,k,0],ci[i,k,1],color='#346d86',lw=1.5)
        ax.axvline(0, color='#777',lw=.9);ax.set_xlim(-1.05,.2)
        ax.set_yticks(range(4),PATHS);ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
        ax.set_xlabel('Relation hybrid − full donor\nPaired country 95% CI')
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.94),ncol=5,frameon=False)
    fig.suptitle('Changing both country and relation tests compositional transfer',fontsize=14,fontweight='bold')
    fig.subplots_adjust(top=.83,bottom=.15,wspace=.3,hspace=.45)
    fig.text(.5,.025,FOOT,ha='center',fontsize=9)
    save(fig,'crossed_outcomes')

    gains = np.array([s['all']['logprob_gain_'+o]['point'] for o in OUTCOMES[:4]])
    fig, axes = plt.subplots(1,3,figsize=(13,5.4),sharey=True)
    for i,ax in enumerate(axes):
        values = gains[:,i].T
        im = ax.imshow(values,cmap='RdBu',vmin=-16,vmax=16,aspect='auto')
        ax.set_title(NAMES[i]);ax.set_yticks(range(4),PATHS)
        ax.set_xticks(range(4),('Original','Entity\nhybrid','Relation\nhybrid','Full\ndonor'))
        for r in range(4):
            for c in range(4):
                ax.text(c,r,f'{values[r,c]:+.2f}',ha='center',va='center',
                        color='white' if abs(values[r,c])>10 else '#202020',fontsize=10)
    fig.colorbar(im,ax=axes,location='right',fraction=.023,pad=.03,label='Log-probability gain (nats)')
    fig.suptitle('Donor probability can increase without a successful first-token answer',fontsize=14,fontweight='bold')
    fig.subplots_adjust(top=.83,bottom=.25,right=.87)
    fig.text(.5,.045,FOOT+'\nPoint estimates shown; all paired intervals and relation-specific values remain in summary.json.',ha='center',fontsize=9)
    save(fig,'all_label_logprob_gains')
    (ROOT/'figures/source.json').write_text(json.dumps({
        'summary_sha256':hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        'raw_sha256':s['raw_sha256'],'plot_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'selection':'none; all three models, four paths, five predeclared outcomes',
        'uncertainty':'paired country bootstrap as frozen in E161; no CI on selected subset'
    },indent=2)+'\n')
    print('E161 full-population figures complete')


if __name__ == '__main__':
    main()
