"""Scientific figure; all discovery/confirmation runs shown, ratios nonadditive."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    names = [('qwen3_synthetic_discovery','Qwen synthetic D'), ('qwen3_synthetic_confirmation','Qwen synthetic C'),
             ('qwen3_real_discovery','Qwen real D'), ('qwen3_real_confirmation','Qwen real C'),
             ('mistral_synthetic_discovery','Mistral synthetic D')]
    data = [json.loads((Path('results/e65') / n / 'analysis.json').read_text()) for n,_ in names]
    fig, axes = plt.subplots(1, 2, figsize=(11,4.4), gridspec_kw={'width_ratios':[1.35,1]})
    colors = ['#276FBF','#ED9B40','#58A37A','#7D5BA6']
    groups = [('freeze_p_label','Demo label → answer'),('freeze_q_source','Query source → answer'),
              ('freeze_q_marker','Query Label marker → answer'),('freeze_q_relay','All query relay → answer')]
    y = np.arange(len(names))
    for i, (key, name) in enumerate(groups):
        vals = [d['conditions'][key]['remaining_fraction'] for d in data]
        m=np.array([v['mean'] for v in vals]); lo=np.array([v['ci95'][0] for v in vals]); hi=np.array([v['ci95'][1] for v in vals])
        axes[0].errorbar(m,y+(i-1.5)*.17,xerr=np.array([m-lo,hi-m]),fmt='o',ms=4,capsize=2,color=colors[i],label=name)
    axes[0].set(yticks=y,yticklabels=[l for _,l in names],xlabel='Source-K effect remaining after message freeze',xlim=(-.08,1.1))
    axes[0].invert_yaxis(); axes[0].axvline(0,color='.65',lw=.6); axes[0].axvline(1,color='.65',lw=.6)
    axes[0].legend(fontsize=8,loc='lower right'); axes[0].set_title('Sender dependence varies across models',fontsize=11)
    for i,(key,label) in enumerate([('drop_direct','Delete direct demo labels'),('drop_relay','Delete query relay')]):
        v=[d['native_contrasts'][key]['accuracy_minus_base'] for d in data]
        m=np.array([e['mean'] for e in v]); lo=np.array([e['ci95'][0] for e in v]); hi=np.array([e['ci95'][1] for e in v])
        axes[1].errorbar(m,y+(i-.5)*.15,xerr=[m-lo,hi-m],fmt='o',capsize=2,ms=4,color=colors[i],label=label)
    axes[1].set(yticks=y,yticklabels=[],xlabel='Native accuracy change',xlim=(-.4,.12)); axes[1].invert_yaxis()
    axes[1].axvline(0,color='.5',lw=.8); axes[1].set_title('Deleting direct reads is not a stable repair',fontsize=11)
    axes[1].legend(fontsize=8,loc='lower left')
    fig.text(.1,.015,'95% context bootstrap CIs. D/C: discovery/confirmation. Real texts use controlled source rules. Effect fractions are not additive.',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]); out=Path('results/figs'); out.mkdir(exist_ok=True)
    fig.savefig(out/'e65_relay.png',dpi=180); fig.savefig(out/'e65_relay.pdf')

if __name__ == '__main__': main()
