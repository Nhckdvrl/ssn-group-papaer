"""Source-owned operator contrast, before mechanistic provenance claims."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval as bootstrap


def ci(x):return bootstrap(x,seed=760,nboot=4000)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();d=Path(a.directory)
    run=json.loads((d/'run.json').read_text());assert run['sanity_max_error']<=.1
    rows=[json.loads(l) for l in (d/'behavior.jsonl').read_text().splitlines()];n=len(rows);assert n==run['args']['n']
    out={'run':run,'conditions':{},'signed_responses':{},'specificity':{},'limitations':['Familiar +/-1 operator selected from context, not arbitrary function learning.',
        'Conditional next-token behavior; no word-copy mechanism has been identified.','Owner compensation can interact nonlinearly.']}
    phi={};ld={};metrics={};idx=np.arange(n);pair=np.array([r['pair'] for r in rows])
    for k in rows[0]['scores']:
        v=np.array([r['scores'][k] for r in rows]);assert v.shape==(n,12,4) and np.isfinite(v).all()
        gold=np.array([r['gold'][k] for r in rows]);g=v[idx[:,None],np.arange(12)[None],gold]
        other=v.copy();other[idx[:,None],np.arange(12)[None],gold]=-np.inf;margin=g-other.max(-1)
        metrics[k]={name:{'accuracy':(margin[:,qs]>0).mean(-1),'margin':margin[:,qs].mean(-1)} for name,qs in [('owned_novel',[1,4]),('foreign_novel',[7,10]),('seen',[0,2,3,5,6,8,9,11])]}
        out['conditions'][k]={name:{stat:ci(x) for stat,x in values.items()} for name,values in metrics[k].items()}
        la=v[idx,1,pair[:,0]]-v[idx,1,pair[:,1]];lb=v[idx,4,pair[:,0]]-v[idx,4,pair[:,1]];ld[k]=(la,lb);phi[k]=la-lb
        out['conditions'][k]['source_contrast']=ci(phi[k])
    for ins in [0,1]:
        root=str(ins)+'.';base=root+'base'
        out['signed_responses'][root+'sync']=ci(phi[base]-phi[root+'scope_swap'])
        for owner,comp,s in [('owned_a','comp_a',0),('owned_b','comp_b',1)]:
            out['signed_responses'][root+owner+'_minus_comp']=ci(phi[root+comp]-phi[root+owner])
            out['specificity'][root+owner]={'edited_ld':ci((1 if s==0 else -1)*(ld[base][s]-ld[root+owner][s])),
                'untouched_ld_change':ci(ld[root+owner][1-s]-ld[base][1-s])}
        for change in ['foreign_swap','comp_a','comp_b']:
            k=root+change
            out['specificity'][k]={'source_contrast_minus_base':ci(phi[k]-phi[base]),
                'accuracy_minus_base':ci(metrics[k]['owned_novel']['accuracy']-metrics[base]['owned_novel']['accuracy']),
                'margin_minus_base':ci(metrics[k]['owned_novel']['margin']-metrics[base]['owned_novel']['margin'])}
    (d/'analysis.json').write_text(json.dumps(out,indent=2));print(out['conditions']['0.base'],out['conditions']['1.base']);print(out['signed_responses']);print(out['specificity'])


if __name__=='__main__':main()
