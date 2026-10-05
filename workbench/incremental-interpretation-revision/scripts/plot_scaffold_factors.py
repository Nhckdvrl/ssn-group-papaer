"""Scientific forest plot of all E46 cells; preregistered two-order averages."""
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot(path,cohort):
    j=json.loads(path.read_text());assert j['experiment']=='E46'
    cells=j['probability']['cells'];names=[f'I{i}R{r}E{e}' for i,r,e in itertools.product((0,1),repeat=3)]
    fig,axes=plt.subplots(1,3,figsize=(13,6),sharey=True)
    for ax,measure,title in zip(axes,('activity','neutral_entity','J'),('Patient prediction D','General mention D','Patient minus mention J')):
        for shift,readout,label,color in [(-.17,'old','Earlier event','C0'),(0,'new_same','New: same action','C1'),(.17,'new_different','New: different action','C2')]:
            values=[cells[f'{cohort}/order_average/{name}/{readout}/{measure}'] for name in names]
            y=np.arange(len(names))+shift;x=np.array([v['estimate'] for v in values]);ci=np.array([v['ci95'] for v in values])
            ax.errorbar(x,y,xerr=np.stack((x-ci[:,0],ci[:,1]-x)),fmt='o',markersize=4,capsize=2,color=color,label=label)
        ax.axvline(0,color='0.5',linewidth=.8);ax.grid(axis='x',alpha=.2);ax.set_title(title);ax.set_xlabel('Role-evidence effect (bits)')
    axes[0].set_yticks(range(8),[name.replace('I','Identity ').replace('R',' / report ').replace('E',' / event ') for name in names]);axes[0].invert_yaxis()
    axes[-1].legend(loc='lower right',fontsize=8)
    n=len(j['probability']['cohorts'][cohort]);fig.suptitle(f'E46 | Qwen3-8B frozen | {n} verb families | paired bootstrap 95% CI')
    fig.text(.5,.012,'0/1: component absent/present; report=0 uses nearby. Event=1 adds anchor and nominal restatement. Two-order averages; not world probability.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.035,1,.95))
    for ext in ('png','pdf'):fig.savefig(path.parent/f'E46-scaffold-factors-{cohort}.{ext}',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('summary',type=Path);p.add_argument('--cohort',default='all');a=p.parse_args();plot(a.summary,a.cohort)
