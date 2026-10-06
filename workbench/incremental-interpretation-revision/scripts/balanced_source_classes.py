"""E59 W3 class-balanced description; missing semantic classes remain missing."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np

from balanced_map import macro
from data import sha


def summarize(effects,out):
    groups=collections.defaultdict(lambda:collections.defaultdict(dict))
    for line in effects.read_text().splitlines():
        r=json.loads(line)
        if r['same_gold_only'] or r['literal_label']=='ALL' or not r['statistic'].startswith('cell/W3/'):
            continue
        key=r['model'],r['construction'],r['target'],r['readout'],r['metric'],r['statistic']
        cell=r['model'],r['literal_label']
        assert r['cluster_id'] not in groups[key][cell]
        groups[key][cell][r['cluster_id']]=r['value']
    reports={}
    for key,cells in sorted(groups.items()):
        clusters=sorted({k for v in cells.values() for k in v})
        rng=np.random.default_rng(52);draws=[]
        for _ in range(100):
            weights=rng.multinomial(len(clusters),np.full(len(clusters),1/len(clusters)),size=100)
            draws.extend(macro(cells,weights,clusters))
        defined=np.asarray(draws);defined=defined[np.isfinite(defined)]
        labels=sorted(label for model,label in cells)
        reports['/'.join(key)]=dict(estimate=float(macro(cells)),
            ci95=np.quantile(defined,[.025,.975]).tolist() if len(clusters)>1 and len(defined) else None,
            n_clusters=len(clusters),classes_present=labels,
            classes_missing=sorted({'ENTAILED','CONTRADICTED','NEITHER'}-set(labels)),
            cluster_counts_by_class={label:len(v) for (model,label),v in cells.items()},
            undefined_bootstrap_draws=10000-len(defined))
    out.write_text(json.dumps(dict(effects_sha256=sha(effects),statistics=reports,
        interpretation='Equal mean of observed literal-class cells with shared lexical-cluster resampling. Not a full three-class estimate when a class is absent; missing is not zero. W3 is never directly compared with two-choice O2/G2 absolute accuracy or probability.'),indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--effects',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    summarize(args.effects,args.out)
