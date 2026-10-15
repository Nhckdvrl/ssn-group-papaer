#!/usr/bin/env python3
"""E69 paired contrasts, static scientific export; no automatic verdict."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'svg.fonttype':'none'})
    fig,axes=plt.subplots(2,3,figsize=(12,6.5),layout='constrained',sharey=True)
    for i,(model,name) in enumerate([('gemma','Gemma 3 12B'),('32b','Qwen3 32B')]):
        r=json.loads((a.results/f'E69_{model}_matched.json').read_text())
        for j,(metric,title) in enumerate([('goal','Task event, eight steps'),('first_step_goal','Task event, first step'),('any_target_give','Any target-item Give, eight steps')]):
            ax=axes[i,j]
            vs=[r['contrasts'][key][metric] for key in ['all/A_minus_F/equip','all/A_minus_F/duty_give','all/persona_x_task']]
            means=np.array([v['mean'] for v in vs])*100
            lo=np.array([v['graph_bootstrap_95'][0] for v in vs])*100
            hi=np.array([v['graph_bootstrap_95'][1] for v in vs])*100
            ax.errorbar(means,[2,1,0],xerr=[means-lo,hi-means],fmt='o',capsize=4,color=['#4477AA','#AA3377'][i])
            ax.axvline(0,color='#777777',linewidth=.8);ax.spines[['top','right']].set_visible(False)
            ax.set_yticks([2,1,0],['A−F, Equip task','A−F, Duty-Give task','Difference of effects'])
            ax.grid(axis='x',alpha=.2);ax.set_title(name+'\n'+title)
            ax.set_xlabel('Paired difference (percentage points)')
    fig.supxlabel('112 same-world task pairs; three seeds per persona; pointwise graph-cluster 95% intervals')
    for ext in ['png','pdf','svg']:
        path=a.out/f'E69_matched_task_effects.{ext}';fig.savefig(path,dpi=180)
        if ext=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)


if __name__=='__main__':main()
