"""Finite-panel family/model/construction macro with shared lexical resampling."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import sha


def family(model):
    for prefix,name in (('Qwen','Qwen'),('gemma','Gemma'),('Meta-Llama','Llama'),('Mistral','Mistral'),('OLMo','OLMo')):
        if model.startswith(prefix):return name
    raise ValueError('Unknown family: '+model)


def macro(cells,weights=None,clusters=None):
    model_cells=collections.defaultdict(list)
    for (model,construction),values in cells.items():
        if weights is None:model_cells[model].append(np.mean(list(values.values())))
        else:
            mask=np.array([k in values for k in clusters],dtype=float)
            value=np.array([values.get(k,0) for k in clusters])
            denominator=weights@mask;numerator=weights@value
            model_cells[model].append(np.divide(numerator,denominator,out=np.full_like(numerator,np.nan,dtype=float),where=denominator>0))
    families=collections.defaultdict(list)
    for model,values in model_cells.items():families[family(model)].append(np.mean(values,axis=0))
    return np.mean([np.mean(v,axis=0) for v in families.values()],axis=0)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--effects',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    groups=collections.defaultdict(lambda:collections.defaultdict(dict))
    for line in args.effects.read_text().splitlines():
        r=json.loads(line)
        if r['construction']=='pooled':continue
        key=r['format'],r['stratum'],r['metric'],r['statistic']
        cell=r['model'],r['construction']
        assert r['cluster_id'] not in groups[key][cell]
        groups[key][cell][r['cluster_id']]=r['value']
    output={}
    for key,cells in sorted(groups.items()):
        clusters=sorted({k for v in cells.values() for k in v})
        if not clusters:continue
        rng=np.random.default_rng(52);draws=[]
        for _ in range(100):
            weights=rng.multinomial(len(clusters),np.full(len(clusters),1/len(clusters)),size=100)
            draws.extend(macro(cells,weights,clusters))
        draws=np.asarray(draws);defined=draws[np.isfinite(draws)]
        fams=sorted({family(m) for m,c in cells});constructs=sorted({c for m,c in cells})
        output['/'.join(key)]=dict(estimate=float(macro(cells)),
            ci95=list(map(float,np.quantile(defined,[.025,.975]))) if len(clusters)>1 and len(defined) else None,
            n_clusters=len(clusters),families=fams,constructions=constructs,models=sorted({m for m,c in cells}),
            non_estimable_bootstrap_draws=int(len(draws)-len(defined)),
            cells={m+'/'+c:len(v) for (m,c),v in cells.items()},
            breadth_present=len(fams)>=3 and len(constructs)>=2)
    report=dict(effects_sha256=sha(args.effects),seed=52,bootstrap_draws=10000,statistics=output,
        interpretation='Materials uncertainty for this fixed panel: average constructs within model, models within family, then families. Same cluster multiplicities across all cells. Missing cells are not zero; undefined bootstrap draws are reported. Breadth is descriptive, never an automatic scientific decision.')
    args.out.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
